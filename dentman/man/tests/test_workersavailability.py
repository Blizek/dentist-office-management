import pytest
from datetime import time
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from dentman.man.models import Worker, WorkersAvailability

User = get_user_model()


@pytest.fixture
def worker(db):
    """Fixture to create a worker."""
    user = User.objects.create_user(username='testworker', password='password123')
    return Worker.objects.create(user=user)


@pytest.mark.django_db
def test_workers_availability_creation(worker):
    """Test workers availability creation"""
    availability = WorkersAvailability(
        worker=worker,
        weekday=1,  # Monday
        since=time(9, 0),
        until=time(17, 0)
    )
    availability.save()
    
    assert availability.worker == worker
    assert availability.weekday == 1
    assert availability.since == time(9, 0)
    assert availability.until == time(17, 0)


@pytest.mark.django_db
def test_workers_availability_str_representation(worker):
    """Test string representation of workers availability"""
    availability = WorkersAvailability(
        worker=worker,
        weekday=2,  # Tuesday
        since=time(8, 30),
        until=time(16, 30)
    )
    availability.save()
    
    str_repr = str(availability)
    assert "Tuesday" in str_repr
    assert "08:30" in str_repr
    assert "16:30" in str_repr


@pytest.mark.django_db
def test_workers_availability_weekday_choices(worker):
    """Test weekday choices validation"""
    # Valid weekday (1-7)
    availability = WorkersAvailability(
        worker=worker,
        weekday=7,  # Sunday
        since=time(10, 0),
        until=time(18, 0)
    )
    availability.save()
    assert availability.weekday == 7


@pytest.mark.django_db
def test_workers_availability_time_validation(worker):
    """Test time validation - until must be after since"""
    availability = WorkersAvailability(
        worker=worker,
        weekday=3,  # Wednesday
        since=time(17, 0),
        until=time(9, 0)  # Earlier than since
    )
    
    with pytest.raises(ValidationError):
        availability.save()


@pytest.mark.django_db
def test_workers_availability_valid_time_range(worker):
    """Test valid time range"""
    availability = WorkersAvailability(
        worker=worker,
        weekday=4,  # Thursday
        since=time(9, 0),
        until=time(17, 0)
    )
    availability.save()
    
    # Should not raise ValidationError
    assert availability.since < availability.until


@pytest.mark.django_db
def test_workers_availability_meta_attributes():
    """Test model meta attributes"""
    assert WorkersAvailability._meta.verbose_name == "worker's availability"
    assert WorkersAvailability._meta.verbose_name_plural == "workers' availabilities"


@pytest.mark.django_db
def test_workers_availability_weekday_display(worker):
    """Test weekday display method"""
    availability = WorkersAvailability(
        worker=worker,
        weekday=5,  # Friday
        since=time(9, 0),
        until=time(17, 0)
    )
    availability.save()
    
    assert availability.get_weekday_display() == "Friday"


@pytest.mark.django_db
def test_workers_availability_multiple_for_same_worker(worker):
    """Test creating multiple availabilities for same worker"""
    # Monday availability
    monday_availability = WorkersAvailability.objects.create(
        worker=worker,
        weekday=1,
        since=time(9, 0),
        until=time(17, 0)
    )
    
    # Friday availability
    friday_availability = WorkersAvailability.objects.create(
        worker=worker,
        weekday=5,
        since=time(8, 0),
        until=time(16, 0)
    )
    
    assert WorkersAvailability.objects.filter(worker=worker).count() == 2
    assert monday_availability.weekday == 1
    assert friday_availability.weekday == 5