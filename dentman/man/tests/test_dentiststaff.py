import pytest
from django.contrib.auth import get_user_model

from dentman.man.models import Worker, DentistStaff

User = get_user_model()


@pytest.mark.django_db
def test_dentist_staff_creation_dentist():
    """Test dentist staff creation as a dentist"""
    user = User.objects.create_user(
        username='dentistuser',
        password='test123',
        is_worker=True,
        is_dentist=True
    )
    worker = Worker.objects.create(user=user)
    
    dentist_staff = DentistStaff.objects.create(
        worker=worker,
        is_dentist=True
    )
    
    assert dentist_staff.worker == worker
    assert dentist_staff.is_dentist is True


@pytest.mark.django_db
def test_dentist_staff_creation_assistant():
    """Test dentist staff creation as an assistant"""
    user = User.objects.create_user(
        username='assistantuser',
        password='test123',
        is_worker=True
    )
    worker = Worker.objects.create(user=user)
    
    dentist_staff = DentistStaff.objects.create(
        worker=worker,
        is_dentist=False
    )
    
    assert dentist_staff.worker == worker
    assert dentist_staff.is_dentist is False


@pytest.mark.django_db
def test_dentist_staff_default_values():
    """Test default values"""
    user = User.objects.create_user(
        username='defaultuser',
        password='test123',
        is_worker=True
    )
    worker = Worker.objects.create(user=user)
    
    dentist_staff = DentistStaff.objects.create(worker=worker)
    
    assert dentist_staff.is_dentist is False  # default value


@pytest.mark.django_db
def test_dentist_staff_one_to_one_constraint():
    """Test that each worker can have only one dentist staff instance"""
    user = User.objects.create_user(
        username='uniquedentist',
        password='test123',
        is_worker=True
    )
    worker = Worker.objects.create(user=user)
    
    # Create first dentist staff instance
    dentist_staff1 = DentistStaff.objects.create(worker=worker)
    
    # Try to create second dentist staff instance for same worker
    with pytest.raises(Exception):  # Should raise IntegrityError
        DentistStaff.objects.create(worker=worker)


@pytest.mark.django_db
def test_dentist_staff_cascade_delete():
    """Test that dentist staff is deleted when worker is deleted"""
    user = User.objects.create_user(
        username='deletedentist',
        password='test123',
        is_worker=True
    )
    worker = Worker.objects.create(user=user)
    
    dentist_staff = DentistStaff.objects.create(worker=worker)
    dentist_staff_id = dentist_staff.id
    
    # Delete worker
    worker.delete()
    
    # Dentist staff should be deleted due to CASCADE
    assert not DentistStaff.objects.filter(id=dentist_staff_id).exists()
