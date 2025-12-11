import pytest
from datetime import date, timedelta
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from dentman.ops.models import Discount

# --- FIXTURES ---

@pytest.fixture
def base_discount():
    """
    Fixture returning a basic, valid discount instance.
    Used as a starting point for other tests to avoid repetition.
    """
    return Discount(
        name="Standard Discount",
        percent=10,
        discount_type="other",
        is_active=True,
        # is_currently_valid will be calculated on save
    )

# --- VALIDATION & INTEGRITY TESTS ---

@pytest.mark.django_db
def test_discount_name_uniqueness(base_discount):
    """
    Test that the 'name' field must be unique.
    Since FullCleanMixin is used, it raises ValidationError BEFORE database IntegrityError.
    """
    base_discount.save()

    duplicate_discount = Discount(
        name="Standard Discount",  # Same name as base_discount
        percent=20,
        discount_type="other"
    )

    with pytest.raises(ValidationError) as excinfo:
        duplicate_discount.save()
    
    assert "name" in excinfo.value.message_dict
    assert "already exists" in str(excinfo.value.message_dict["name"])

@pytest.mark.django_db
def test_discount_percent_boundaries():
    """
    Test boundary values for the 'percent' field (0-100).
    """
    # Test 0% (Allowed)
    d0 = Discount(name="Zero Percent", percent=0, discount_type="other")
    d0.full_clean()  # Should not raise error
    d0.save()
    
    # Test 100% (Allowed)
    d100 = Discount(name="Free Service", percent=100, discount_type="other")
    d100.full_clean()  # Should not raise error
    d100.save()
    
    # Test 101% (Forbidden)
    d_over = Discount(name="Over limit", percent=101, discount_type="other")
    with pytest.raises(ValidationError) as excinfo:
        d_over.full_clean()
    assert "percent" in excinfo.value.message_dict

    # Test -1% (Forbidden)
    d_under = Discount(name="Under limit", percent=-1, discount_type="other")
    with pytest.raises(ValidationError) as excinfo:
        d_under.full_clean()
    assert "percent" in excinfo.value.message_dict

@pytest.mark.django_db
def test_promo_code_requirement_logic():
    """
    Test the clean() method logic:
    If discount_type is 'promo_code', promotion_code field cannot be empty.
    """
    # Case 1: Type is 'promo_code' but code is missing -> Error
    discount = Discount(
        name="No Code", 
        percent=5, 
        discount_type="promo_code", 
        promotion_code=""
    )
    with pytest.raises(ValidationError) as excinfo:
        discount.full_clean()
    assert "promotion_code" in excinfo.value.message_dict
    
    # Case 2: Type is 'promo_code' and code is present -> OK
    discount.promotion_code = "VALID"
    discount.full_clean() # Should pass

# --- BUSINESS LOGIC: SAVE METHOD & STATUS FLAGS ---

@pytest.mark.django_db
def test_promotion_code_whitespace_strip(base_discount):
    """
    Test that save() method removes leading/trailing whitespace from promotion_code.
    """
    base_discount.discount_type = "promo_code"
    base_discount.promotion_code = "  SUMMER 2025  "
    base_discount.save()
    
    # Expect trimmed string
    assert base_discount.promotion_code == "SUMMER 2025"

@pytest.mark.django_db
def test_multiple_invalid_reasons_aggregation(base_discount):
    """
    Test if 'why_invalid_summary' correctly aggregates multiple reasons.
    Scenario: Discount is inactive AND expired AND limit reached.
    """
    base_discount.is_active = False
    base_discount.valid_to = date.today() - timedelta(days=1) # Expired
    base_discount.is_limited = True
    base_discount.limit_value = 5
    base_discount.used_counter = 5 # Limit reached
    
    base_discount.save()
    
    summary = base_discount.why_invalid_summary
    
    # 1. Check valid flag
    assert base_discount.is_currently_valid is False
    
    # 2. Check if all reasons are present in the summary
    assert "Discount is currently inactive" in summary
    assert "Discount has expired" in summary
    assert "Discount's limit has been reached" in summary
    
    # 3. Check formatting (items should be separated by newlines)
    assert len(summary.split('\n')) >= 3

# --- DATE LOGIC TESTS ---

@pytest.mark.django_db
@pytest.mark.parametrize("days_offset, expected_valid, reason_part", [
    (-5, False, "Discount has expired"),          # valid_to was 5 days ago
    (5, True, None),                              # valid_to is in 5 days
])
def test_valid_to_logic(base_discount, days_offset, expected_valid, reason_part):
    """Test validation based on 'valid_to' date."""
    base_discount.valid_to = date.today() + timedelta(days=days_offset)
    base_discount.save()
    
    assert base_discount.is_currently_valid is expected_valid
    if reason_part:
        assert reason_part in base_discount.why_invalid_summary

@pytest.mark.django_db 
@pytest.mark.parametrize("days_offset, expected_valid, reason_part", [
    (5, False, "It's too early"),                 # valid_since is in 5 days
    (-5, True, None),                             # valid_since was 5 days ago
])
def test_valid_since_logic(base_discount, days_offset, expected_valid, reason_part):
    """Test validation based on 'valid_since' date."""
    base_discount.valid_since = date.today() + timedelta(days=days_offset)
    base_discount.save()
    
    assert base_discount.is_currently_valid is expected_valid
    if reason_part:
        assert reason_part in base_discount.why_invalid_summary

# --- LIMIT LOGIC TESTS ---

@pytest.mark.django_db
def test_limit_value_is_none_bug_check(base_discount):
    """
    CRITICAL TEST: This checks if the model handles limit_value=None correctly.
    If 'check_limits' compares None <= int, this will raise a TypeError.
    """
    base_discount.is_limited = True
    base_discount.limit_value = None  # Simulate empty field from form
    base_discount.used_counter = 0
    
    # This ensures the code treats None as 0 (or infinite) and doesn't crash
    try:
        base_discount.save()
    except TypeError:
        pytest.fail("Model crashed because limit_value was None. Fix check_limits method.")
        
    # Assuming logic treats None as 0 limit:
    assert base_discount.is_currently_valid is False 
    assert "limit has been reached" in base_discount.why_invalid_summary

@pytest.mark.django_db
@pytest.mark.parametrize("limit, used, expected_valid", [
    (10, 9, True),   # 1 remaining -> Valid
    (10, 10, False), # 0 remaining -> Invalid
    (10, 11, False), # Over limit -> Invalid
])
def test_limit_counters_logic(base_discount, limit, used, expected_valid):
    """Test standard limit counting logic."""
    base_discount.is_limited = True
    base_discount.limit_value = limit
    base_discount.used_counter = used
    base_discount.save()
    
    assert base_discount.is_currently_valid is expected_valid

@pytest.mark.django_db
def test_limit_logic_when_is_limited_false(base_discount):
    """
    Test that limit values are ignored if is_limited is False.
    Even if used_counter > limit_value, it should remain valid.
    """
    base_discount.is_limited = False
    base_discount.limit_value = 5
    base_discount.used_counter = 100 # Way over limit
    
    base_discount.save()
    
    assert base_discount.is_currently_valid is True
    assert "limit has been reached" not in base_discount.why_invalid_summary