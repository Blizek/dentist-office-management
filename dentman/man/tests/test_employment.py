import pytest
import os
import tempfile
import shutil
from datetime import date
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model

from dentman.man.models import Worker, ManagementStaff, Employment

User = get_user_model()


@pytest.fixture
def worker(db):
    """Fixture to create a worker."""
    user = User.objects.create_user(username='testworker', password='password123')
    return Worker.objects.create(user=user)


@pytest.fixture
def management_staff(db):
    """Fixture to create management staff."""
    user = User.objects.create_user(username='manager', password='password123')
    worker = Worker.objects.create(user=user)
    return ManagementStaff.objects.create(worker=worker, is_hr=True)


@pytest.mark.django_db
def test_employment_creation(worker, management_staff):
    """Test employment creation"""
    contract_file = SimpleUploadedFile(
        "contract.pdf",
        b"contract_content",
        content_type="application/pdf"
    )
    
    employment = Employment(
        new_employee=worker,
        representative=management_staff,
        type_of_employment='full_time',
        is_for_limited_time=False,
        since_when=date(2025, 1, 1),
        agreement_date=date(2024, 12, 15),
        salary=Decimal('5000.00'),
        contract_scan=contract_file
    )
    employment.save()
    
    assert employment.new_employee == worker
    assert employment.representative == management_staff
    assert employment.type_of_employment == 'full_time'
    assert employment.is_for_limited_time is False
    assert employment.since_when == date(2025, 1, 1)
    assert employment.until_when is None
    assert employment.agreement_date == date(2024, 12, 15)
    assert employment.salary == Decimal('5000.00')
    assert employment.is_active is True


@pytest.mark.django_db
def test_employment_limited_time(worker, management_staff):
    """Test employment with limited time"""
    contract_file = SimpleUploadedFile(
        "temp_contract.pdf",
        b"temp_contract_content",
        content_type="application/pdf"
    )
    
    employment = Employment(
        new_employee=worker,
        representative=management_staff,
        type_of_employment='fixed_term',
        is_for_limited_time=True,
        since_when=date(2025, 1, 1),
        until_when=date(2025, 6, 30),
        agreement_date=date(2024, 12, 20),
        salary=Decimal('3000.00'),
        contract_scan=contract_file
    )
    employment.save()
    
    assert employment.is_for_limited_time is True
    assert employment.until_when == date(2025, 6, 30)


@pytest.mark.django_db
def test_employment_validation_not_limited_with_until_date(worker, management_staff):
    """Test validation error when not limited time but until_when is set"""
    contract_file = SimpleUploadedFile(
        "invalid_contract.pdf",
        b"contract_content",
        content_type="application/pdf"
    )
    
    employment = Employment(
        new_employee=worker,
        representative=management_staff,
        type_of_employment='full_time',
        is_for_limited_time=False,
        since_when=date(2025, 1, 1),
        until_when=date(2025, 12, 31),  # Should not be set when not limited
        agreement_date=date(2024, 12, 15),
        contract_scan=contract_file
    )
    
    with pytest.raises(ValidationError):
        employment.save()


@pytest.mark.django_db
def test_employment_types():
    """Test employment type choices"""
    choices = dict(Employment.EMPLOYMENT_TYPES)
    assert 'full_time' in choices
    assert 'part_time' in choices
    assert 'contract' in choices
    assert 'fixed_term' in choices
    assert 'temporary' in choices
    assert 'internship' in choices
    assert 'traineeship' in choices
    assert 'volunteer' in choices


@pytest.mark.django_db
def test_employment_meta_attributes():
    """Test model meta attributes"""
    assert Employment._meta.verbose_name == "employment"
    assert Employment._meta.verbose_name_plural == "employments"


@pytest.mark.django_db
def test_employment_cascade_delete_worker(worker, management_staff):
    """Test cascade deletion when worker is deleted"""
    contract_file = SimpleUploadedFile(
        "cascade_contract.pdf",
        b"contract_content",
        content_type="application/pdf"
    )
    
    employment = Employment.objects.create(
        new_employee=worker,
        representative=management_staff,
        type_of_employment='full_time',
        since_when=date(2025, 1, 1),
        agreement_date=date(2024, 12, 15),
        contract_scan=contract_file
    )
    
    employment_id = employment.id
    worker_id = worker.id
    
    # Delete the worker
    worker.delete()
    
    # The employment should be deleted due to CASCADE
    assert not Employment.objects.filter(id=employment_id).exists()
    assert not Worker.objects.filter(id=worker_id).exists()