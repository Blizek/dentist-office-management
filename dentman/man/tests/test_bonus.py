import pytest
from decimal import Decimal
from datetime import date, datetime
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from dentman.man.models import Worker, ManagementStaff, Bonus

User = get_user_model()


@pytest.fixture
def worker(db):
    """Fixture to create a worker."""
    user = User.objects.create_user(username='bonusworker', password='password123')
    return Worker.objects.create(user=user)


@pytest.fixture
def hr_staff(db):
    """Fixture to create HR management staff."""
    user = User.objects.create_user(username='hrmanager', password='password123')
    worker = Worker.objects.create(user=user)
    return ManagementStaff.objects.create(worker=worker, is_hr=True)


@pytest.mark.django_db
def test_bonus_creation(worker, hr_staff):
    """Test bonus creation"""
    bonus = Bonus(
        worker=worker,
        management_staff=hr_staff,
        bonus_amount=Decimal('1000.00'),
        bonus_date=date(2025, 1, 15),
        bonus_reason="Excellent performance in Q4"
    )
    bonus.save()
    
    assert bonus.worker == worker
    assert bonus.management_staff == hr_staff
    assert bonus.bonus_amount == Decimal('1000.00')
    assert bonus.bonus_date == date(2025, 1, 15)
    assert bonus.bonus_reason == "Excellent performance in Q4"


@pytest.mark.django_db
def test_bonus_negative_amount_validation(worker, hr_staff):
    """Test validation for negative amount"""
    bonus = Bonus(
        worker=worker,
        management_staff=hr_staff,
        bonus_amount=Decimal('-100.00'),  # Negative amount
        bonus_date=date(2025, 1, 15),
        bonus_reason="Should not work with negative amount"
    )
    
    with pytest.raises(ValidationError):
        bonus.full_clean()


@pytest.mark.django_db
def test_bonus_zero_amount(worker, hr_staff):
    """Test bonus with zero amount"""
    bonus = Bonus(
        worker=worker,
        management_staff=hr_staff,
        bonus_amount=Decimal('0.00'),
        bonus_date=date(2025, 1, 15),
        bonus_reason="Zero bonus test"
    )
    bonus.save()
    
    assert bonus.bonus_amount == Decimal('0.00')


@pytest.mark.django_db
def test_bonus_date_validation(worker, hr_staff):
    """Test bonus date relationships"""
    # Test when received date is before granted date (should be allowed)
    bonus = Bonus(
        worker=worker,
        management_staff=hr_staff,
        bonus_amount=Decimal('750.00'),
        bonus_date=date(2025, 2, 15),
        bonus_reason="Date validation test"
    )
    bonus.save()
    
    assert bonus.bonus_date == date(2025, 2, 15)


@pytest.mark.django_db
def test_bonus_long_reason(worker, hr_staff):
    """Test bonus with long reason text"""
    long_reason = "This is a very long reason for the bonus that contains many words and explains in detail why this bonus was granted to the employee for their outstanding work and dedication to the company."
    
    bonus = Bonus(
        worker=worker,
        management_staff=hr_staff,
        bonus_amount=Decimal('1200.00'),
        bonus_date=date(2025, 1, 25),
        bonus_reason=long_reason
    )
    bonus.save()
    
    assert bonus.bonus_reason == long_reason


@pytest.mark.django_db
def test_bonus_cascade_delete_worker(worker, hr_staff):
    """Test cascade deletion when worker (beneficent) is deleted"""
    bonus = Bonus.objects.create(
        worker=worker,
        management_staff=hr_staff,
        bonus_amount=Decimal('800.00'),
        bonus_date=date(2025, 1, 10),
        bonus_reason="Cascade test bonus"
    )
    
    bonus_id = bonus.id
    worker_id = worker.id
    
    # Delete the worker
    worker.delete()
    
    # The bonus should be deleted due to CASCADE
    assert not Bonus.objects.filter(id=bonus_id).exists()
    assert not Worker.objects.filter(id=worker_id).exists()


@pytest.mark.django_db
def test_bonus_cascade_delete_manager(worker, hr_staff):
    """Test cascade deletion when manager is deleted"""
    bonus = Bonus.objects.create(
        worker=worker,
        management_staff=hr_staff,
        bonus_amount=Decimal('600.00'),
        bonus_date=date(2025, 1, 12),
        bonus_reason="Manager cascade test"
    )
    
    bonus_id = bonus.id
    manager_id = hr_staff.id
    
    # Delete the manager
    hr_staff.delete()
    
    # The bonus should be deleted due to CASCADE
    assert not Bonus.objects.filter(id=bonus_id).exists()
    assert not ManagementStaff.objects.filter(id=manager_id).exists()


@pytest.mark.django_db
def test_bonus_decimal_precision(worker, hr_staff):
    """Test decimal precision for amount field"""
    # Test with many decimal places - should be rounded to 2 decimal places
    precise_amount = Decimal('123.456789')
    
    bonus = Bonus(
        worker=worker,
        management_staff=hr_staff,
        bonus_amount=precise_amount,
        bonus_date=date(2025, 1, 16),
        bonus_reason="Precision test"
    )
    
    with pytest.raises(ValidationError):
        bonus.full_clean()