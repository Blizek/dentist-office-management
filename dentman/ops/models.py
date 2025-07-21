import uuid
import os
import datetime
from decimal import Decimal

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

from dentman.app.mixins import CreatedUpdatedMixin
from dentman.storage import CustomFileSystemStorage
from dentman.utils import get_upload_path

from tinymce.models import HTMLField

User = get_user_model()
storage = CustomFileSystemStorage()

class Category(CreatedUpdatedMixin):
    name = models.CharField("Category name", max_length=255, unique=True)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        if not self.parent:
            return f"{self.name}"
        return f"{self.parent} -> {self.name}"

class Service(CreatedUpdatedMixin):
    name = models.CharField("Service name", max_length=255, unique=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = "Service"
        verbose_name_plural = "Services"

    def __str__(self):
        if not self.category:
            return f"{self.name}"
        return f"{self.name} in category {self.category}"

class VisitStatus(CreatedUpdatedMixin):
    name = models.CharField("Visit status", max_length=255, unique=True)
    is_booked = models.BooleanField("Is visit booked", default=False)
    is_postponed = models.BooleanField("Is visit postponed", default=False)
    is_in_progress = models.BooleanField("Is visit in progress", default=False)
    is_finished = models.BooleanField("Is visit finished", default=False)
    is_resigned_by_patient = models.BooleanField("Is visit resigned by patient", default=False)
    is_resigned_by_dentist = models.BooleanField("Is visit resigned by dentist", default=False)
    is_resigned_by_office = models.BooleanField("Is visit resigned by office", default=False)
    additional_info = models.TextField("Additional information", blank=True)

    class Meta:
        verbose_name = "visit's status"
        verbose_name_plural = "visit's statuses"

    def __str__(self):
        return f"Visit's status {self.name}"

class Discount(CreatedUpdatedMixin):
    DISCOUNT_TYPES = (
        ('first_visit', 'First visit'),
        ('promo_code', 'Promotion code'),
        ('min_purchase', 'Minimal visit amount'),
        ('other', 'Other')
    )

    name = models.CharField("Discount name", max_length=255, unique=True)
    description = models.TextField("Discount description", blank=True)
    percent = models.IntegerField("Discount percent", default=0,
                                  validators=[
                                      MinValueValidator(0, "Value cannot be less than 0"),
                                      MaxValueValidator(100, "Value cannot be greater than 100")
                                  ])
    discount_type = models.CharField("Discount type", max_length=50, choices=DISCOUNT_TYPES)
    promotion_code = models.CharField("Promotion code", max_length=30, blank=True)
    valid_since = models.DateField("Discount valid date", null=True, blank=True)
    valid_to = models.DateField("Discount valid to", null=True, blank=True)
    is_currently_valid = models.BooleanField("Is currently valid", default=False)
    why_invalid_summary = models.TextField("Why invalid summary", blank=True,
                                            help_text="There is reason why this discount is not valid")
    is_limited = models.BooleanField("Is discount limited", default=False)
    limit_value = models.IntegerField("Discount limit value", default=0, null=True, blank=True,
                                      validators=[MinValueValidator(0, "Value cannot be less than 0")])
    used_counter = models.IntegerField("Discount used counter", default=0)
    additional_info = models.TextField("Additional information", blank=True)

    class Meta:
        verbose_name = "discount"
        verbose_name_plural = "discounts"

    def __str__(self):
        return f"Discount {self.name} -{self.percent}%"

    def save(self, *args, **kwargs):
        is_valid_date, invalid_date_reason = self.check_validation_date()
        is_valid_limit, invalid_limit_reason = self.check_limits()

        why_invalid = f"{invalid_date_reason}\n{invalid_limit_reason}"
        if is_valid_date and is_valid_limit:
            self.is_currently_valid = True
            why_invalid = f"Discount is currently valid"
        else:
            self.is_currently_valid = False
        self.why_invalid_summary = why_invalid.strip("\n")

        super().save(*args, **kwargs)

    def check_validation_date(self):
        today = datetime.date.today()

        if self.valid_since is not None and today < self.valid_since:
            return False, "It's too early to use this promotion"
        elif self.valid_to is not None and today > self.valid_to:
            return False, "Discount has expired"
        return True, ""

    def check_limits(self):
        if self.is_limited and self.limit_value <= self.used_counter:
            return False, "Discount's limit has been reached"
        return True, ""

class Visit(CreatedUpdatedMixin):
    eid = models.UUIDField("EID", default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(User, verbose_name="Patient", on_delete=models.SET_NULL, null=True, limit_choices_to={'is_patient': True})
    dentists = models.ManyToManyField(User, verbose_name="Dentists", limit_choices_to={'is_dentist': True}, related_name="dentists")
    scheduled_from = models.DateTimeField("Scheduled from")
    scheduled_to = models.DateTimeField("Scheduled to")
    starting_time = models.DateTimeField("Visit starting time", blank=True, null=True)
    ending_time = models.DateTimeField("Visit ending time", blank=True, null=True)
    visit_description = models.TextField("Visit description", blank=True, null=True)
    visit_status = models.ForeignKey(VisitStatus, verbose_name="Visit's status", on_delete=models.SET_NULL, null=True)
    additional_info = models.TextField("Additional information", blank=True, null=True)
    price = models.DecimalField("Price", max_digits=10, decimal_places=2)
    discounts = models.ManyToManyField(Discount, verbose_name="Discounts", related_name="discounts")
    final_price = models.DecimalField("Final price", max_digits=10, decimal_places=2, default=0.0,
                                      help_text="Final price of service including discounts")

    class Meta:
        verbose_name = "visit"
        verbose_name_plural = "visits"

    def __str__(self):
        return f"Visit {self.patient.get_full_name()} at {self.scheduled_from}"

    def calculate_final_price(self):
        current_final_price = self.price

        for discount in self.discounts.all():
            decimal_discount_percent = Decimal(discount.percent)
            multiplier = Decimal(1) - decimal_discount_percent / Decimal(100)
            current_final_price *= multiplier

        self.final_price = current_final_price

class Post(CreatedUpdatedMixin):
    title = models.CharField("Title", max_length=500, unique=True)
    slug = models.SlugField("Slug", max_length=500, unique=True)
    main_photo = models.ImageField("Main photo", upload_to=get_upload_path, storage=storage, null=True,
                                   help_text="Main photo that will show up on the lists of posts and the main photo at the post")
    text_html = HTMLField("Text html", help_text="Blog's text written in HTML format")
    visit_counter = models.IntegerField("Visit counter", default=0)

    class Meta:
        verbose_name = "post"
        verbose_name_plural = "posts"

    def __str__(self):
        return f"Post {self.title}"

    def save(self, *args, **kwargs):
        if self.pk:
            actual_photo = Post.objects.get(pk=self.pk).main_photo
            if self.main_photo != actual_photo:
                self.delete_old_file(actual_photo)
        super().save(*args, **kwargs)

    def delete_main_photo(self):
        if self.main_photo:
            self.main_photo.delete()

    def delete_old_file(self, old_file):
        if old_file.name != "":
            os.remove(str(storage.base_location) + f"/{old_file.name}")


