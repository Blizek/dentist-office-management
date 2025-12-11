import pytest
from django.core.exceptions import ValidationError

from dentman.ops.models import Category


@pytest.mark.django_db
def test_category_creation():
    """Test category creation"""
    category = Category.objects.create(name="Root Category")
    
    assert category.name == "Root Category"
    assert category.parent is None


@pytest.mark.django_db
def test_category_with_parent():
    """Test category creation with parent"""
    parent_category = Category.objects.create(name="Parent Category")
    child_category = Category.objects.create(
        name="Child Category",
        parent=parent_category
    )
    
    assert child_category.name == "Child Category"
    assert child_category.parent == parent_category


@pytest.mark.django_db
def test_category_str_representation_without_parent():
    """Test string representation for root category"""
    category = Category.objects.create(name="Root Category")
    
    assert str(category) == "Root Category"


@pytest.mark.django_db
def test_category_str_representation_with_parent():
    """Test string representation for child category"""
    parent_category = Category.objects.create(name="Parent Category")
    child_category = Category.objects.create(
        name="Child Category",
        parent=parent_category
    )
    
    expected_str = "Parent Category -> Child Category"
    assert str(child_category) == expected_str


@pytest.mark.django_db
def test_category_unique_name():
    """Test that category names must be unique"""
    Category.objects.create(name="Unique Category")
    
    with pytest.raises(Exception):
        Category.objects.create(name="Unique Category")


@pytest.mark.django_db
def test_category_meta_attributes():
    """Test model meta attributes"""
    assert Category._meta.verbose_name == "Category"
    assert Category._meta.verbose_name_plural == "Categories"


@pytest.mark.django_db
def test_category_max_length():
    """Test category name max length"""
    long_name = "a" * 255
    category = Category(name=long_name)
    category.full_clean()
    
    too_long_name = "a" * 256
    category = Category(name=too_long_name)
    
    with pytest.raises(ValidationError):
        category.save()


@pytest.mark.django_db
def test_category_cascade_delete_parent():
    """Test that deleting parent sets children's parent to None"""
    parent_category = Category.objects.create(name="Parent Category")
    child_category = Category.objects.create(
        name="Child Category",
        parent=parent_category
    )
    
    parent_category.delete()
    
    child_category.refresh_from_db()
    assert child_category.parent is None
