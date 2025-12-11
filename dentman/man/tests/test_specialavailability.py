import pytest
from datetime import date, time
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from dentman.man.models import Worker, SpecialAvailability

User = get_user_model()


@pytest.fixture
def worker(db):
    """Fixture to create a worker."""
    user = User.objects.create_user(username='testworker', password='password123')
    return Worker.objects.create(user=user)


@pytest.mark.django_db
def test_special_availability_creation(worker):
    """Test special availability creation"""
    special_date = date(2025, 12, 25)  # Christmas
    special_availability = SpecialAvailability(
        worker=worker,
        date=special_date,
        since=time(10, 0),
        until=time(14, 0),
        reason="Holiday schedule"
    )
    special_availability.save()
    
    assert special_availability.worker == worker
    assert special_availability.date == special_date
    assert special_availability.since == time(10, 0)
    assert special_availability.until == time(14, 0)
    assert special_availability.reason == "Holiday schedule"


@pytest.mark.django_db
def test_special_availability_str_representation(worker):
    """Test string representation of special availability"""
    special_date = date(2025, 6, 15)
    special_availability = SpecialAvailability(
        worker=worker,
        date=special_date,
        since=time(9, 30),
        until=time(15, 30),
        reason="Doctor appointment"
    )
    special_availability.save()
    
    str_repr = str(special_availability)
    assert "2025-06-15" in str_repr
    assert "09:30" in str_repr
    assert "15:30" in str_repr


@pytest.mark.django_db
def test_special_availability_time_validation(worker):
    """Test time validation - until must be after since"""
    special_availability = SpecialAvailability(
        worker=worker,
        date=date(2025, 7, 4),
        since=time(16, 0),
        until=time(8, 0),  # Earlier than since
        reason="Invalid time range"
    )
    
    with pytest.raises(ValidationError):
        special_availability.save()


@pytest.mark.django_db
def test_special_availability_valid_time_range(worker):
    """Test valid time range"""
    special_availability = SpecialAvailability(
        worker=worker,
        date=date(2025, 8, 15),
        since=time(11, 0),
        until=time(15, 0),
        reason="Reduced hours"
    )
    special_availability.save()
    
    # Should not raise ValidationError
    assert special_availability.since < special_availability.until


@pytest.mark.django_db
def test_special_availability_without_reason(worker):
    """Test special availability without reason"""
    special_availability = SpecialAvailability(
        worker=worker,
        date=date(2025, 9, 1),
        since=time(8, 0),
        until=time(12, 0)
        # No reason provided
    )
    special_availability.save()
    
    assert special_availability.reason == ""


@pytest.mark.django_db
def test_special_availability_meta_attributes():
    """Test model meta attributes"""
    assert SpecialAvailability._meta.verbose_name == "special availability"
    assert SpecialAvailability._meta.verbose_name_plural == "special availabilities"


@pytest.mark.django_db
def test_special_availability_multiple_dates(worker):
    """Test creating special availabilities for multiple dates"""
    # First special availability
    first_availability = SpecialAvailability.objects.create(
        worker=worker,
        date=date(2025, 12, 24),
        since=time(9, 0),
        until=time(13, 0),
        reason="Christmas Eve"
    )
    
    # Second special availability
    second_availability = SpecialAvailability.objects.create(
        worker=worker,
        date=date(2025, 12, 31),
        since=time(10, 0),
        until=time(14, 0),
        reason="New Year's Eve"
    )
    
    assert SpecialAvailability.objects.filter(worker=worker).count() == 2
    assert first_availability.date == date(2025, 12, 24)
    assert second_availability.date == date(2025, 12, 31)


@pytest.mark.django_db
def test_special_availability_cascade_delete(worker):
    """Test cascade deletion when worker is deleted"""
    special_availability = SpecialAvailability.objects.create(
        worker=worker,
        date=date(2025, 10, 31),
        since=time(9, 0),
        until=time(17, 0),
        reason="Halloween"
    )
    
    availability_id = special_availability.id
    worker_id = worker.id
    
    # Delete the worker
    worker.delete()
    
    # The special availability should be deleted due to CASCADE
    assert not SpecialAvailability.objects.filter(id=availability_id).exists()
    assert not Worker.objects.filter(id=worker_id).exists()