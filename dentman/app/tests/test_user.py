import pytest

from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model


User = get_user_model()


@pytest.mark.django_db
def test_valid_phone_number_saves_successfully():
    valid_numbers = [
        '1234567890',
        '+1234567890',
        '123-456-7890',
        '123 456 789',
    ]

    for i, number in enumerate(valid_numbers):
        user = User(username=f'test_user_{i}', phone_number=number, password='test')

        user.save()

        assert User.objects.filter(phone_number=number).exists()


@pytest.mark.django_db
def test_invalid_phone_number_save_raises_error():
    invalid_numbers = [
        '123',
        'abc-456-7890',
        '12345678901234567',
    ]

    for number in invalid_numbers:
        user = User(username=f'test_user_{number}', phone_number=number)

        with pytest.raises(ValidationError):
            user.save()

        assert not User.objects.filter(phone_number=number).exists()