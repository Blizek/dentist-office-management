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


@pytest.mark.django_db
def test_worker_must_have_staff_type():
    user = User(username="worker_no_staff", is_worker=True)
    with pytest.raises(ValidationError) as excinfo:
        user.save()
    assert "is_dentist_staff" in excinfo.value.message_dict


@pytest.mark.django_db
def test_staff_type_must_be_worker():
    user = User(username="staff_not_worker", is_dentist_staff=True, is_worker=False)
    with pytest.raises(ValidationError) as excinfo:
        user.save()
    assert "is_worker" in excinfo.value.message_dict


@pytest.mark.django_db
def test_dentist_staff_must_have_role():
    user = User(
        username="dentist_staff_no_role",
        is_worker=True,
        is_dentist_staff=True
    )
    with pytest.raises(ValidationError) as excinfo:
        user.save()
    assert "is_dentist" in excinfo.value.message_dict


@pytest.mark.django_db
def test_dentist_role_requires_dentist_staff_flag():
    user = User(
        username="dentist_no_staff_flag",
        is_worker=True,
        is_dentist=True,
        is_dentist_staff=False
    )
    with pytest.raises(ValidationError) as excinfo:
        user.save()
    assert "is_dentist_staff" in excinfo.value.message_dict


@pytest.mark.django_db
def test_management_staff_must_have_role():
    user = User(
        username="mgmt_no_role",
        is_worker=True,
        is_management_staff=True
    )
    with pytest.raises(ValidationError) as excinfo:
        user.save()
    assert "is_hr" in excinfo.value.message_dict


@pytest.mark.django_db
def test_hr_role_requires_management_staff_flag():
    user = User(
        username="hr_no_staff_flag",
        is_worker=True,
        is_hr=True,
        is_management_staff=False
    )
    with pytest.raises(ValidationError) as excinfo:
        user.save()
    assert "is_management_staff" in excinfo.value.message_dict


@pytest.mark.django_db
def test_valid_dentist_setup():
    user = User(
        username="valid_dentist",
        password="password",
        is_worker=True,
        is_dentist_staff=True,
        is_dentist=True
    )

    user.save()
    assert user.pk is not None


@pytest.mark.django_db
def test_valid_management_setup():
    user = User(
        username="valid_financial",
        password="password",
        is_worker=True,
        is_management_staff=True,
        is_financial=True
    )

    user.save()
    assert user.pk is not None