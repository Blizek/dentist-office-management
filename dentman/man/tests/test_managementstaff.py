import pytest
from django.contrib.auth import get_user_model

from dentman.man.models import Worker, ManagementStaff

User = get_user_model()


@pytest.mark.django_db
def test_management_staff_creation():
    """Test management staff creation"""
    user = User.objects.create_user(
        username='manageruser',
        password='test123',
        is_worker=True
    )
    worker = Worker.objects.create(user=user)
    
    management_staff = ManagementStaff.objects.create(
        worker=worker,
        is_hr=True,
        is_financial=True
    )
    
    assert management_staff.worker == worker
    assert management_staff.is_hr is True
    assert management_staff.is_financial is True


@pytest.mark.django_db
def test_management_staff_str_representation_both_roles():
    """Test string representation with both HR and financial roles"""
    user = User.objects.create_user(
        username='manageruser',
        first_name='John',
        last_name='Manager',
        password='test123',
        is_worker=True
    )
    worker = Worker.objects.create(user=user)
    
    management_staff = ManagementStaff.objects.create(
        worker=worker,
        is_hr=True,
        is_financial=True
    )
    
    expected_str = f"{user.get_full_name()} with HR, Financial permissions"
    assert str(management_staff) == expected_str


@pytest.mark.django_db
def test_management_staff_str_representation_hr_only():
    """Test string representation with HR role only"""
    user = User.objects.create_user(
        username='hruser',
        first_name='Jane',
        last_name='HR',
        password='test123',
        is_worker=True
    )
    worker = Worker.objects.create(user=user)
    
    management_staff = ManagementStaff.objects.create(
        worker=worker,
        is_hr=True,
        is_financial=False
    )
    
    expected_str = f"{user.get_full_name()} with HR permissions"
    assert str(management_staff) == expected_str


@pytest.mark.django_db
def test_management_staff_str_representation_financial_only():
    """Test string representation with financial role only"""
    user = User.objects.create_user(
        username='financeuser',
        first_name='Bob',
        last_name='Finance',
        password='test123',
        is_worker=True
    )
    worker = Worker.objects.create(user=user)
    
    management_staff = ManagementStaff.objects.create(
        worker=worker,
        is_hr=False,
        is_financial=True
    )
    
    expected_str = f"{user.get_full_name()} with Financial permissions"
    assert str(management_staff) == expected_str


@pytest.mark.django_db
def test_management_staff_default_values():
    """Test default values"""
    user = User.objects.create_user(
        username='defaultmanager',
        password='test123',
        is_worker=True
    )
    worker = Worker.objects.create(user=user)
    
    management_staff = ManagementStaff.objects.create(worker=worker)
    
    assert management_staff.is_hr is False
    assert management_staff.is_financial is False


@pytest.mark.django_db
def test_management_staff_one_to_one_constraint():
    """Test that each worker can have only one management staff instance"""
    user = User.objects.create_user(
        username='uniquemanager',
        password='test123',
        is_worker=True
    )
    worker = Worker.objects.create(user=user)
    
    management_staff1 = ManagementStaff.objects.create(worker=worker)
    
    with pytest.raises(Exception):
        ManagementStaff.objects.create(worker=worker)


@pytest.mark.django_db
def test_management_staff_meta_attributes():
    """Test model meta attributes"""
    assert ManagementStaff._meta.verbose_name == "management staff"
    assert ManagementStaff._meta.verbose_name_plural == "management staffs"
