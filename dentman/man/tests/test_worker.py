import pytest
from datetime import date, timedelta
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from dentman.man.models import Worker

User = get_user_model()


@pytest.mark.django_db
def test_worker_creation_with_defaults():
    """Test worker creation with default values"""
    user = User.objects.create_user(
        username='workeruser',
        password='test123',
        is_worker=True,
        is_dentist_staff=True,
        is_dentist=True
    )
    
    worker = Worker.objects.create(user=user)
    
    assert worker.user == user
    assert worker.since_when == date.today()
    assert worker.to_when is None
    assert worker.is_active is True


@pytest.mark.django_db
def test_worker_creation_with_custom_values():
    """Test worker creation with custom values"""
    user = User.objects.create_user(
        username='customworker',
        password='test123',
        is_worker=True,
        is_dentist_staff=True,
        is_dentist=True
    )
    
    since_date = date.today() - timedelta(days=30)
    to_date = date.today() + timedelta(days=30)
    
    worker = Worker.objects.create(
        user=user,
        since_when=since_date,
        to_when=to_date
    )
    
    assert worker.user == user
    assert worker.since_when == since_date
    assert worker.to_when == to_date
    assert worker.is_active is False


@pytest.mark.django_db
def test_worker_str_representation():
    """Test string representation of worker"""
    user = User.objects.create_user(
        username='testworker',
        first_name='John',
        last_name='Doe',
        password='test123',
        is_worker=True,
        is_dentist_staff=True,
        is_dentist=True
    )
    
    worker = Worker.objects.create(user=user)
    
    expected_str = f"Worker {user.get_full_name()}"
    assert str(worker) == expected_str


@pytest.mark.django_db
def test_worker_save_method_sets_inactive_when_to_when_set():
    """Test that save method sets is_active to False when to_when is set"""
    user = User.objects.create_user(
        username='inactiveworker',
        password='test123',
        is_worker=True,
        is_dentist_staff=True,
        is_dentist=True
    )
    
    worker = Worker.objects.create(user=user)
    assert worker.is_active is True

    worker.to_when = date.today() + timedelta(days=1)
    worker.save()
    
    assert worker.is_active is False


@pytest.mark.django_db
def test_worker_one_to_one_constraint():
    """Test that each user can have only one worker instance"""
    user = User.objects.create_user(
        username='uniqueworker',
        password='test123',
        is_worker=True,
        is_dentist_staff=True,
        is_dentist=True
    )
    
    worker1 = Worker.objects.create(user=user)
    
    with pytest.raises(Exception):
        Worker.objects.create(user=user)


@pytest.mark.django_db
def test_worker_cascade_delete():
    """Test that worker is deleted when user is deleted"""
    user = User.objects.create_user(
        username='deleteworker',
        password='test123',
        is_worker=True,
        is_dentist_staff=True,
        is_dentist=True
    )
    
    worker = Worker.objects.create(user=user)
    worker_id = worker.id
    
    user.delete()
    
    assert not Worker.objects.filter(id=worker_id).exists()


@pytest.mark.django_db
def test_worker_meta_attributes():
    """Test model meta attributes"""
    assert Worker._meta.verbose_name == "worker"
    assert Worker._meta.verbose_name_plural == "workers"


@pytest.mark.django_db
def test_worker_default_since_when():
    """Test that since_when defaults to today"""
    user = User.objects.create_user(
        username='todayworker',
        password='test123',
        is_worker=True,
        is_dentist_staff=True,
        is_dentist=True
    )
    
    worker = Worker.objects.create(user=user)
    assert worker.since_when == date.today()


@pytest.mark.django_db
def test_worker_is_active_field_not_editable():
    """Test that is_active field is not editable"""
    field = Worker._meta.get_field('is_active')
    assert field.editable is False
