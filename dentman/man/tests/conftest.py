import pytest
from django.apps import apps
from .utils import InMemoryStorage

@pytest.fixture(autouse=True)
def force_in_memory_storage(monkeypatch):
    """
    Automatic fixture: every FileField in the project will use InMemoryStorage.
    Does not require patching settings or imports in models.
    """

    memory = InMemoryStorage()

    for model in apps.get_models():
        for field in model._meta.fields:
            if hasattr(field, "storage"): 
                monkeypatch.setattr(field, "storage", memory)

    yield
