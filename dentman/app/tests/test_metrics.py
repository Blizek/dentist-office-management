import pytest
from django.core.exceptions import ValidationError

from dentman.app.models import Metrics


@pytest.mark.django_db
def test_metrics_creation():
    """Test metrics creation with all measurement types"""
    metrics_data = [
        (1, "Meter", "m"),  # Length
        (2, "Kilogram", "kg"),  # Weight
        (3, "Piece", "pcs"),  # Amount
    ]
    
    for measurement_type, name, shortcut in metrics_data:
        metric = Metrics.objects.create(
            measurement_type=measurement_type,
            measurement_name=name,
            measurement_name_shortcut=shortcut
        )
        
        assert metric.measurement_type == measurement_type
        assert metric.measurement_name == name
        assert metric.measurement_name_shortcut == shortcut


@pytest.mark.django_db
def test_metrics_str_representation():
    """Test string representation of metrics"""
    metric = Metrics.objects.create(
        measurement_type=1,  # Length
        measurement_name="Centimeter",
        measurement_name_shortcut="cm"
    )
    
    expected_str = "Metric for Length - Centimeter (cm)"
    assert str(metric) == expected_str


@pytest.mark.django_db
def test_metrics_measurement_type_choices():
    """Test measurement type choices"""
    # Test each choice
    length_metric = Metrics.objects.create(
        measurement_type=1,
        measurement_name="Meter",
        measurement_name_shortcut="m"
    )
    assert length_metric.get_measurement_type_display() == "Length"
    
    weight_metric = Metrics.objects.create(
        measurement_type=2,
        measurement_name="Gram",
        measurement_name_shortcut="g"
    )
    assert weight_metric.get_measurement_type_display() == "Weight"
    
    amount_metric = Metrics.objects.create(
        measurement_type=3,
        measurement_name="Unit",
        measurement_name_shortcut="u"
    )
    assert amount_metric.get_measurement_type_display() == "Amount"


@pytest.mark.django_db
def test_metrics_field_validation():
    """Test field validation for required fields"""
    # Test missing required fields
    metric = Metrics()
    
    with pytest.raises(ValidationError):
        metric.full_clean()


@pytest.mark.django_db
def test_metrics_max_lengths():
    """Test field max length validation"""
    # Test measurement_name max length (100)
    long_name = "a" * 101
    metric = Metrics(
        measurement_type=1,
        measurement_name=long_name,
        measurement_name_shortcut="test"
    )
    
    with pytest.raises(ValidationError):
        metric.full_clean()
    
    # Test measurement_name_shortcut max length (10)
    long_shortcut = "a" * 11
    metric = Metrics(
        measurement_type=1,
        measurement_name="Test",
        measurement_name_shortcut=long_shortcut
    )
    
    with pytest.raises(ValidationError):
        metric.full_clean()


@pytest.mark.django_db
def test_metrics_valid_max_lengths():
    """Test valid max length values"""
    # Test valid measurement_name length (100)
    valid_name = "a" * 100
    metric = Metrics(
        measurement_type=1,
        measurement_name=valid_name,
        measurement_name_shortcut="test"
    )
    metric.full_clean()  # Should not raise ValidationError
    
    # Test valid measurement_name_shortcut length (10)
    valid_shortcut = "a" * 10
    metric = Metrics(
        measurement_type=1,
        measurement_name="Test",
        measurement_name_shortcut=valid_shortcut
    )
    metric.full_clean()  # Should not raise ValidationError


@pytest.mark.django_db
def test_metrics_measurement_types_tuple():
    """Test that all measurement types from MEASUREMENT_TYPES are valid"""
    measurement_types = Metrics.MEASUREMENT_TYPES
    
    assert len(measurement_types) == 3
    assert (1, "Length") in measurement_types
    assert (2, "Weight") in measurement_types
    assert (3, "Amount") in measurement_types


@pytest.mark.django_db
def test_metrics_meta_attributes():
    """Test model meta attributes"""
    assert Metrics._meta.verbose_name == "Metric"
    assert Metrics._meta.verbose_name_plural == "Metrics"


@pytest.mark.django_db
def test_metrics_invalid_measurement_type():
    """Test creation with invalid measurement type"""
    metric = Metrics(
        measurement_type=999,  # Invalid choice
        measurement_name="Test",
        measurement_name_shortcut="t"
    )
    
    with pytest.raises(ValidationError):
        metric.full_clean()


@pytest.mark.django_db
def test_metrics_edge_cases():
    """Test edge cases for metrics"""
    # Test with minimum valid values
    metric = Metrics.objects.create(
        measurement_type=1,
        measurement_name="A",  # Single character
        measurement_name_shortcut="a"  # Single character
    )
    
    assert metric.measurement_name == "A"
    assert metric.measurement_name_shortcut == "a"
