import pytest
from django.core.exceptions import ValidationError

from dentman.ops.models import Category, Service


@pytest.mark.django_db
def test_service_creation():
    """Test service creation"""
    category = Category.objects.create(name="Dental Category")
    
    service = Service.objects.create(
        name="Teeth Cleaning",
        category=category
    )
    
    assert service.name == "Teeth Cleaning"
    assert service.category == category


@pytest.mark.django_db
def test_service_creation_with_null_category():
    """Test service creation with null category is not allowed"""
    with pytest.raises(ValidationError):
        service = Service(name="Emergency Service", category=None)
        service.save()


@pytest.mark.django_db
def test_service_str_representation_with_category():
    """Test string representation with category"""
    category = Category.objects.create(name="Dental Category")
    service = Service.objects.create(
        name="Teeth Cleaning",
        category=category
    )
    
    expected_str = "Teeth Cleaning in category Dental Category"
    assert str(service) == expected_str


@pytest.mark.django_db
def test_service_str_representation_without_category():
    """Test string representation without category"""
    category = Category.objects.create(name="General")
    service = Service.objects.create(name="Emergency Service", category=category)
    
    assert str(service) == "Emergency Service in category General"


@pytest.mark.django_db
def test_service_unique_name():
    """Test that service names must be unique"""
    category = Category.objects.create(name="General")
    Service.objects.create(name="Unique Service", category=category)
    
    with pytest.raises(Exception):
        Service.objects.create(name="Unique Service", category=category)


@pytest.mark.django_db
def test_service_meta_attributes():
    """Test model meta attributes"""
    assert Service._meta.verbose_name == "Service"
    assert Service._meta.verbose_name_plural == "Services"


@pytest.mark.django_db
def test_service_max_length():
    """Test service name max length"""
    category = Category.objects.create(name="General")
    long_name = "a" * 255
    service = Service(name=long_name, category=category)
    service.save()
    
    too_long_name = "a" * 256
    service = Service(name=too_long_name, category=category)
    
    with pytest.raises(ValidationError):
        service.save()


@pytest.mark.django_db
def test_service_category_set_null():
    """Test that deleting category sets service's category to None"""
    category = Category.objects.create(name="Test Category")
    service = Service.objects.create(
        name="Test Service",
        category=category
    )
    
    category.delete()
    
    service.refresh_from_db()
    assert service.category is None
