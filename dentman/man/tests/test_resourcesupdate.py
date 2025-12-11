import pytest
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.utils import timezone
from dentman.man.models import Resource, ResourcesUpdate
from dentman.app.models import Metrics

# --- FIXTURES ---

@pytest.fixture
def metric(db):
    """Creates a Metric instance (e.g., Liters)."""
    return Metrics.objects.create(
        measurement_name="Liters",
        measurement_name_shortcut="l",
        measurement_type=1
    )

@pytest.fixture
def resource(db, metric):
    """Creates a Resource instance with an initial amount of 100.0."""
    return Resource.objects.create(
        resource_name="Water",
        default_metric=metric,
        actual_amount=Decimal("100.0000000")
    )

# --- TESTS ---

@pytest.mark.django_db
def test_resources_update_delivery_increases_amount(resource, metric):
    """
    Test if creating a ResourcesUpdate with is_newly_delivered=True
    correctly increases the actual_amount of the related Resource.
    """
    initial_amount = resource.actual_amount
    amount_to_add = Decimal("50.0000000")

    # Create the update record (Delivery)
    update = ResourcesUpdate(
        resource=resource,
        amount_change=amount_to_add,
        metric=metric,
        is_newly_delivered=True,
        update_datetime=timezone.now()
    )
    update.save()

    # Refresh resource from DB to get updated values
    resource.refresh_from_db()

    # Assertions
    assert resource.actual_amount == initial_amount + amount_to_add
    assert resource.actual_amount == Decimal("150.0000000")


@pytest.mark.django_db
def test_resources_update_usage_decreases_amount(resource, metric):
    """
    Test if creating a ResourcesUpdate with is_newly_delivered=False
    correctly decreases the actual_amount of the related Resource.
    """
    initial_amount = resource.actual_amount  # 100.0
    amount_to_remove = Decimal("30.0000000")

    # Create the update record (Usage)
    update = ResourcesUpdate(
        resource=resource,
        amount_change=amount_to_remove,
        metric=metric,
        is_newly_delivered=False,
        update_datetime=timezone.now()
    )
    update.save()

    resource.refresh_from_db()

    # Assertions
    assert resource.actual_amount == initial_amount - amount_to_remove
    assert resource.actual_amount == Decimal("70.0000000")


@pytest.mark.django_db
def test_resources_update_validation_insufficient_funds(resource, metric):
    """
    Test validation logic: trying to use more resources than available
    should raise a ValidationError in the clean() method.
    """
    # Resource has 100.0, we try to remove 150.0
    amount_too_big = Decimal("150.0000000")

    update = ResourcesUpdate(
        resource=resource,
        amount_change=amount_too_big,
        metric=metric,
        is_newly_delivered=False  # usage
    )

    # We expect ValidationError when running full_clean()
    with pytest.raises(ValidationError) as excinfo:
        update.full_clean()

    # Check if the error is assigned to the correct field
    assert "amount_change" in excinfo.value.message_dict
    assert excinfo.value.message_dict["amount_change"] == ["You can't use more resource than you have"]


@pytest.mark.django_db
def test_resources_update_str_representation_added(resource, metric):
    """
    Test the string representation when resources are ADDED.
    Format: "{resource_name}'s update: {amount}{metric_shortcut} ADDED"
    """
    update = ResourcesUpdate(
        resource=resource,
        amount_change=Decimal("10.5"),
        metric=metric,
        is_newly_delivered=True
    )
    
    # Expected: Water's update: 10.5l ADDED
    expected_str = "Water's update: 10.5l ADDED"
    assert str(update) == expected_str


@pytest.mark.django_db
def test_resources_update_str_representation_removed(resource, metric):
    """
    Test the string representation when resources are REMOVED.
    Format: "{resource_name}'s update: {amount}{metric_shortcut} REMOVED"
    """
    update = ResourcesUpdate(
        resource=resource,
        amount_change=Decimal("5.0"),
        metric=metric,
        is_newly_delivered=False
    )
    
    # Expected: Water's update: 5.0l REMOVED
    expected_str = "Water's update: 5.0l REMOVED"
    assert str(update) == expected_str


@pytest.mark.django_db
def test_resources_update_default_datetime(resource, metric):
    """Test if update_datetime is automatically set to now if not provided."""
    update = ResourcesUpdate.objects.create(
        resource=resource,
        amount_change=Decimal("1.0"),
        metric=metric,
        is_newly_delivered=True
    )
    
    assert update.update_datetime is not None
    # Check if the date is close to now (sanity check)
    assert (timezone.now() - update.update_datetime).total_seconds() < 10