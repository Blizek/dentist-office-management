import pytest
from decimal import Decimal
from django.core.exceptions import ValidationError
from dentman.app.models import Metrics
from dentman.man.models import Resource


@pytest.fixture
def metric(db):
    """Create sample Metrics instance for testing."""
    return Metrics.objects.create(
        measurement_name="Liters",
        measurement_name_shortcut="l",
        measurement_type=3
    )

@pytest.mark.django_db
def test_resource_creation_happy_path(metric):
    """Test correct creation of Resource with all data provided."""
    resource = Resource.objects.create(
        resource_name="Water",
        default_metric=metric,
        actual_amount=Decimal("123.4567890")
    )
    
    assert resource.resource_name == "Water"
    assert resource.default_metric == metric
    assert resource.actual_amount == Decimal("123.4567890")
    assert hasattr(resource, 'created_at') 


@pytest.mark.django_db
def test_resource_default_values(metric):
    """Test domyślnych wartości (actual_amount powinno być 0.0)."""
    resource = Resource.objects.create(
        resource_name="Paper",
        default_metric=metric
    )
    
    assert resource.actual_amount == Decimal("0.0")


@pytest.mark.django_db
def test_resource_validation_no_name(metric):
    """Test validation: missing resource name should raise an error."""
    resource = Resource(
        resource_name="",  # Puste pole
        default_metric=metric
    )
    
    with pytest.raises(ValidationError) as excinfo:
        resource.full_clean()
    
    assert "resource_name" in excinfo.value.message_dict


@pytest.mark.django_db
def test_resource_on_delete_set_null(metric):
    """
    Test behavior of on_delete=SET_NULL.
    When the Metric is deleted, the default_metric field in Resource should become None.
    """
    resource = Resource.objects.create(
        resource_name="Gas",
        default_metric=metric,
        actual_amount=Decimal("10.0")
    )
    
    metric.delete()
    
    resource.refresh_from_db()
    
    assert resource.default_metric is None
    assert Resource.objects.filter(id=resource.id).exists()