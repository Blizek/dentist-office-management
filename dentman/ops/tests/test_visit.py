import pytest
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils import timezone

from dentman.ops.models import Visit, Service, Category, VisitStatus, Discount

User = get_user_model()


@pytest.mark.django_db
def test_visit_creation():
    """Test visit creation"""
    patient = User.objects.create_user(
        username='patient',
        password='test123',
        is_patient=True
    )
    dentist = User.objects.create_user(
        username='dentist',
        password='test123',
        is_dentist=True
    )
    category = Category.objects.create(name="Dental Care")
    service = Service.objects.create(name="Checkup", category=category)
    visit_status = VisitStatus.objects.create(name="Booked", is_booked=True)
    
    scheduled_from = timezone.now() + timedelta(hours=1)
    scheduled_to = scheduled_from + timedelta(hours=1)
    
    visit = Visit.objects.create(
        patient=patient,
        service=service,
        scheduled_from=scheduled_from,
        scheduled_to=scheduled_to,
        visit_status=visit_status,
        price=Decimal('100.00')
    )
    visit.dentists.add(dentist)
    
    assert visit.patient == patient
    assert visit.service == service
    assert visit.scheduled_from == scheduled_from
    assert visit.scheduled_to == scheduled_to
    assert visit.visit_status == visit_status
    assert visit.price == Decimal('100.00')
    assert visit.final_price == Decimal('0.0')
    assert isinstance(visit.eid, uuid.UUID)
    assert dentist in visit.dentists.all()


@pytest.mark.django_db
def test_visit_str_representation():
    """Test string representation of visit"""
    patient = User.objects.create_user(
        username='patient',
        first_name='John',
        last_name='Patient',
        password='test123',
        is_patient=True
    )
    category = Category.objects.create(name="General Visit")
    service = Service.objects.create(name="Checkup", category=category)
    visit_status = VisitStatus.objects.create(name="Booked")
    
    scheduled_from = timezone.now() + timedelta(hours=1)
    scheduled_to = scheduled_from + timedelta(hours=1)
    
    visit = Visit.objects.create(
        patient=patient,
        service=service,
        scheduled_from=scheduled_from,
        scheduled_to=scheduled_to,
        visit_status=visit_status,
        price=Decimal('100.00')
    )

    str_repr = str(visit)
    assert "John Patient's visit for Checkup scheduled for" in str_repr


@pytest.mark.django_db
def test_visit_calculate_final_price():
    """Test final price calculation with discounts"""
    patient = User.objects.create_user(
        username='patient',
        password='test123',
        is_patient=True
    )
    category = Category.objects.create(name="General Visit")
    service = Service.objects.create(name="Checkup", category=category)
    visit_status = VisitStatus.objects.create(name="Booked")
    
    # Create discounts
    discount1 = Discount.objects.create(
        name="10% Off",
        percent=10,
        discount_type='first_visit'
    )
    discount2 = Discount.objects.create(
        name="5% Off",
        percent=5,
        discount_type='promo_code',
        promotion_code='SAVE5'
    )
    
    scheduled_from = timezone.now() + timedelta(hours=1)
    scheduled_to = scheduled_from + timedelta(hours=1)
    
    visit = Visit.objects.create(
        patient=patient,
        service=service,
        scheduled_from=scheduled_from,
        scheduled_to=scheduled_to,
        visit_status=visit_status,
        price=Decimal('100.00')
    )
    visit.discounts.add(discount1, discount2)

    visit.calculate_final_price()
    
    assert visit.final_price == Decimal('85.50')


@pytest.mark.django_db
def test_visit_scheduled_time_validation():
    """Test validation that scheduled_to must be after scheduled_from"""
    patient = User.objects.create_user(
        username='patient',
        password='test123',
        is_patient=True
    )
    category = Category.objects.create(name="General Visit")
    service = Service.objects.create(name="Checkup", category=category)
    visit_status = VisitStatus.objects.create(name="Booked")
    
    scheduled_from = timezone.now() + timedelta(hours=2)
    scheduled_to = timezone.now() + timedelta(hours=1)
    
    visit = Visit(
        patient=patient,
        service=service,
        scheduled_from=scheduled_from,
        scheduled_to=scheduled_to,
        visit_status=visit_status,
        price=Decimal('100.00')
    )
    
    with pytest.raises(ValidationError):
        visit.full_clean()


@pytest.mark.django_db
def test_visit_ending_time_validation():
    """Test validation that ending_time must be after starting_time"""
    patient = User.objects.create_user(
        username='patient',
        password='test123',
        is_patient=True
    )
    category = Category.objects.create(name="General Visit")
    service = Service.objects.create(name="Checkup", category=category)
    visit_status = VisitStatus.objects.create(name="Booked")
    
    scheduled_from = timezone.now() + timedelta(hours=1)
    scheduled_to = scheduled_from + timedelta(hours=1)
    starting_time = timezone.now() + timedelta(hours=2)
    ending_time = timezone.now() + timedelta(hours=1)
    
    visit = Visit(
        patient=patient,
        service=service,
        scheduled_from=scheduled_from,
        scheduled_to=scheduled_to,
        starting_time=starting_time,
        ending_time=ending_time,
        visit_status=visit_status,
        price=Decimal('100.00')
    )
    
    with pytest.raises(ValidationError):
        visit.full_clean()


@pytest.mark.django_db
def test_visit_meta_attributes():
    """Test model meta attributes"""
    assert Visit._meta.verbose_name == "visit"
    assert Visit._meta.verbose_name_plural == "visits"


@pytest.mark.django_db
def test_visit_patient_limit_choices():
    """Test that patient field limits choices to users with is_patient=True"""
    field = Visit._meta.get_field('patient')
    assert field._limit_choices_to == {'is_patient': True}


@pytest.mark.django_db
def test_visit_dentists_limit_choices():
    """Test that dentists field limits choices to users with is_dentist=True"""
    field = Visit._meta.get_field('dentists')
    assert field._limit_choices_to == {'is_dentist': True}
