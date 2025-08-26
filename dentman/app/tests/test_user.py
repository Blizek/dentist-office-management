import uuid

from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

import pytest


User = get_user_model()


@pytest.mark.django_db
class TestUser:
    def test_user_creation(self):
        user = User.objects.create(username="test_user", first_name="test", last_name="test", email="test@example.com",
                                   phone_number="+48 123 456 789", is_patient=True, is_worker=True, is_dev=False, password="test")

        assert user.get_username() == "test_user"
        assert user.first_name == "test"
        assert user.last_name == "test"
        assert user.email == "test@example.com"
        assert isinstance(user.eid, uuid.UUID)
        assert user.phone_number == "+48 123 456 789"
        assert user.is_patient is True
        assert user.is_worker is True
        assert user.is_dev is False


    def test_valid_phone_number_saves_successfully(self):
        valid_numbers = [
            '1234567890',
            '+1234567890',
            '123-456-7890',
            '123 456 789',
            '+48 123 456 789',
        ]

        for i, number in enumerate(valid_numbers):
            user = User(username=f'test_user_{i}', phone_number=number, password='test')

            user.save()

            assert User.objects.filter(phone_number=number).exists()

    def test_invalid_phone_number_save_raises_error(self):
        invalid_numbers = [
            '123',
            'abc-456-7890',
            '12345678901234567',
        ]

        for i, number in enumerate(invalid_numbers):
            user = User(username=f'test_user_{i}', phone_number=number, password='test')

            with pytest.raises(ValidationError):
                user.save()

            assert not User.objects.filter(phone_number=number).exists()