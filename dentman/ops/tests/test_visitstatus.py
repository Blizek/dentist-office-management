import pytest
from django.core.exceptions import ValidationError
from dentman.ops.models import VisitStatus

# --- FIXTURES ---

@pytest.fixture
def booked_status(db):
    """Fixture for a standard 'Booked' status."""
    return VisitStatus.objects.create(
        name="Booked",
        is_booked=True
    )

# --- TESTS ---

@pytest.mark.django_db
def test_visit_status_creation_defaults():
    """
    Test that a new status has all boolean flags set to False by default.
    """
    status = VisitStatus.objects.create(name="New Status")
    
    assert status.name == "New Status"
    assert status.is_booked is False
    assert status.is_postponed is False
    assert status.is_in_progress is False
    assert status.is_finished is False
    assert status.is_resigned_by_patient is False
    assert status.is_resigned_by_dentist is False
    assert status.is_resigned_by_office is False
    assert status.additional_info == ""


@pytest.mark.django_db
def test_visit_status_str_representation(booked_status):
    """
    Test the __str__ method.
    Expected format: "Visit's status {name}"
    """
    assert str(booked_status) == "Visit's status Booked"


@pytest.mark.django_db
def test_visit_status_name_uniqueness(booked_status):
    """
    Test that creating a status with a duplicate name raises a ValidationError.
    Note: FullCleanMixin catches this before the DB IntegrityError.
    """
    duplicate_status = VisitStatus(
        name="Booked",  # Same name as the fixture
        is_finished=True
    )

    with pytest.raises(ValidationError) as excinfo:
        duplicate_status.save()
    
    assert "name" in excinfo.value.message_dict
    assert "already exists" in str(excinfo.value.message_dict["name"])


@pytest.mark.django_db
def test_visit_status_custom_flags():
    """
    Test creating a status with specific flags set to True.
    """
    status = VisitStatus.objects.create(
        name="Patient Cancelled",
        is_resigned_by_patient=True,
        additional_info="Patient didn't show up."
    )
    
    assert status.is_resigned_by_patient is True
    assert status.is_booked is False  # Should stay default
    assert status.additional_info == "Patient didn't show up."


@pytest.mark.django_db
def test_visit_status_update(booked_status):
    """
    Test updating an existing status.
    """
    booked_status.name = "Confirmed Booking"
    booked_status.additional_info = "Confirmed via phone"
    booked_status.save()
    
    booked_status.refresh_from_db()
    assert booked_status.name == "Confirmed Booking"
    assert booked_status.additional_info == "Confirmed via phone"