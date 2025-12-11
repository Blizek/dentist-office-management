import os
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def user(db):
    """Fixture to create a user."""
    return User.objects.create_user(username="testuser", password="password123")


def test_create_user(user):
    """Test creating a user and check default values."""
    assert user.username == "testuser"
    assert user.is_patient is True
    assert user.is_worker is False
    assert user.is_dentist is False
    assert user.is_dev is False
    assert str(user) == "testuser"
    assert user.check_password("password123")


@pytest.mark.django_db
def test_user_str_representation(user):
    """Test the string representation of the User model."""
    assert str(user) == "testuser"


@pytest.mark.django_db
def test_valid_phone_number_saves_successfully():
    valid_numbers = [
        "1234567890",
        "+1234567890",
        "123-456-7890",
        "123 456 789",
    ]
    for i, number in enumerate(valid_numbers):
        user = User(username=f"test_user_{i}", phone_number=number, password="test")
        user.save()
        assert User.objects.filter(phone_number=number).exists()


@pytest.mark.django_db
def test_invalid_phone_number_save_raises_error():
    invalid_numbers = [
        "123",
        "abc-456-7890",
        "12345678901234567",
    ]
    for number in invalid_numbers:
        user = User(username=f"test_user_{number}", phone_number=number)
        with pytest.raises(ValidationError):
            user.save()
        assert not User.objects.filter(phone_number=number).exists()
