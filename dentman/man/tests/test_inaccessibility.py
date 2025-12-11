import pytest
from datetime import date, time
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from dentman.man.models import Worker, Inaccessibility

User = get_user_model()


@pytest.fixture
def worker(db):
    """Fixture to create a worker."""
    user = User.objects.create_user(username='testworker', password='password123')
    return Worker.objects.create(user=user)


@pytest.mark.django_db
def test_inaccessibility_whole_day_creation(worker):
    """Test inaccessibility creation for whole day"""
    inaccessibility_date = date(2025, 6, 15)
    inaccessibility = Inaccessibility(
        worker=worker,
        date=inaccessibility_date,
        is_whole_day=True
    )
    inaccessibility.save()
    
    assert inaccessibility.worker == worker
    assert inaccessibility.date == inaccessibility_date
    assert inaccessibility.is_whole_day is True
    assert inaccessibility.since is None
    assert inaccessibility.until is None


@pytest.mark.django_db
def test_inaccessibility_partial_day_creation(worker):
    """Test inaccessibility creation for partial day"""
    inaccessibility_date = date(2025, 7, 20)
    inaccessibility = Inaccessibility(
        worker=worker,
        date=inaccessibility_date,
        is_whole_day=False,
        since=time(10, 0),
        until=time(15, 0)
    )
    inaccessibility.save()
    
    assert inaccessibility.worker == worker
    assert inaccessibility.date == inaccessibility_date
    assert inaccessibility.is_whole_day is False
    assert inaccessibility.since == time(10, 0)
    assert inaccessibility.until == time(15, 0)


@pytest.mark.django_db
def test_inaccessibility_str_representation_whole_day(worker):
    """Test string representation for whole day inaccessibility"""
    inaccessibility = Inaccessibility(
        worker=worker,
        date=date(2025, 8, 10),
        is_whole_day=True
    )
    inaccessibility.save()
    
    str_repr = str(inaccessibility)
    assert "2025-08-10" in str_repr
    assert "inaccessible" in str_repr
    # Should not contain time information for whole day
    assert "since" not in str_repr.lower() or "to" not in str_repr.lower()


@pytest.mark.django_db
def test_inaccessibility_str_representation_partial_day(worker):
    """Test string representation for partial day inaccessibility"""
    inaccessibility = Inaccessibility(
        worker=worker,
        date=date(2025, 9, 5),
        is_whole_day=False,
        since=time(14, 0),
        until=time(16, 30)
    )
    inaccessibility.save()
    
    str_repr = str(inaccessibility)
    assert "2025-09-05" in str_repr
    assert "14:00" in str_repr
    assert "16:30" in str_repr


@pytest.mark.django_db
def test_inaccessibility_validation_partial_without_times(worker):
    """Test validation error when partial day but no times provided"""
    inaccessibility = Inaccessibility(
        worker=worker,
        date=date(2025, 10, 1),
        is_whole_day=False
        # No since/until times provided
    )
    
    with pytest.raises(ValidationError):
        inaccessibility.save()


@pytest.mark.django_db
def test_inaccessibility_validation_partial_missing_since(worker):
    """Test validation error when partial day but since time missing"""
    inaccessibility = Inaccessibility(
        worker=worker,
        date=date(2025, 10, 2),
        is_whole_day=False,
        until=time(17, 0)
        # No since time provided
    )
    
    with pytest.raises(ValidationError):
        inaccessibility.save()


@pytest.mark.django_db
def test_inaccessibility_validation_partial_missing_until(worker):
    """Test validation error when partial day but until time missing"""
    inaccessibility = Inaccessibility(
        worker=worker,
        date=date(2025, 10, 3),
        is_whole_day=False,
        since=time(9, 0)
        # No until time provided
    )
    
    with pytest.raises(ValidationError):
        inaccessibility.save()


@pytest.mark.django_db
def test_inaccessibility_validation_invalid_time_range(worker):
    """Test validation error when until is before since"""
    inaccessibility = Inaccessibility(
        worker=worker,
        date=date(2025, 10, 4),
        is_whole_day=False,
        since=time(16, 0),
        until=time(10, 0)  # Earlier than since
    )
    
    with pytest.raises(ValidationError):
        inaccessibility.save()


@pytest.mark.django_db
def test_inaccessibility_valid_partial_day(worker):
    """Test valid partial day inaccessibility"""
    inaccessibility = Inaccessibility(
        worker=worker,
        date=date(2025, 11, 15),
        is_whole_day=False,
        since=time(13, 0),
        until=time(15, 0)
    )
    inaccessibility.save()
    
    # Should not raise ValidationError
    assert inaccessibility.since < inaccessibility.until


@pytest.mark.django_db
def test_inaccessibility_meta_attributes():
    """Test model meta attributes"""
    assert Inaccessibility._meta.verbose_name == "inaccessibility"
    assert Inaccessibility._meta.verbose_name_plural == "unavailability"


@pytest.mark.django_db
def test_inaccessibility_cascade_delete(worker):
    """Test cascade deletion when worker is deleted"""
    inaccessibility = Inaccessibility.objects.create(
        worker=worker,
        date=date(2025, 12, 1),
        is_whole_day=True
    )
    
    inaccessibility_id = inaccessibility.id
    worker_id = worker.id
    
    # Delete the worker
    worker.delete()
    
    # The inaccessibility should be deleted due to CASCADE
    assert not Inaccessibility.objects.filter(id=inaccessibility_id).exists()
    assert not Worker.objects.filter(id=worker_id).exists()