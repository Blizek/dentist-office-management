import uuid
import os
import datetime
from decimal import Decimal

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.timezone import localtime

from dentman.app.mixins import CreatedUpdatedMixin
from dentman.storage import CustomFileSystemStorage
from dentman.utils import get_upload_path

from tinymce.models import HTMLField

User = get_user_model()
storage = CustomFileSystemStorage()


class Category(CreatedUpdatedMixin):
    """Database model for the tree of categories to build nicely divided services into subcategories"""
    name = models.CharField("Category name", max_length=255, unique=True)
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL
    ) # parent is a category for which this category is a subcategory

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        if not self.parent:
            return f"{self.name}"
        return f"{self.parent} -> {self.name}"


class Service(CreatedUpdatedMixin):
    """Services are all possible services that patient can get in dentist's office"""
    name = models.CharField("Service name", max_length=255, unique=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True) # every service has to be a part of some category


    class Meta:
        verbose_name = "Service"
        verbose_name_plural = "Services"

    def __str__(self):
        if not self.category:
            return f"{self.name}"
        return f"{self.name} in category {self.category}"


class VisitStatus(CreatedUpdatedMixin):
    """Visit's statuses with BooleanFields to specify which situation each status describes"""
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
    """Discounts that are or were available in the service for customers"""
    # Types of discounts
    # 1) first_visit - promotion for patients that used this dentist for the first time
    # 2) promo_code - promotion code that can be typed, and it gives you special discount
    # 3) min_purchase - promotion for regular patients
    # 4) others - other types of possible discounts
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
    valid_since = models.DateField("Discount valid date", null=True, blank=True) # since when discount is valid (null=since forever)
    valid_to = models.DateField("Discount valid to", null=True, blank=True) # to when discount is valid (null=to forever)
    is_currently_valid = models.BooleanField(
        "Is currently valid", default=False
    ) # flag not to calculate every time if discount is valid; flag is updated after every use
    why_invalid_summary = models.TextField("Why invalid summary", blank=True,
                                            help_text="There is reason why this discount is not valid"
    ) # short summary why discount is invalid (or info that is currently valid)
    is_limited = models.BooleanField("Is discount limited", default=False) # if discount is limited by usage
    limit_value = models.IntegerField("Discount limit value", default=0, null=True, blank=True,
                                      validators=[MinValueValidator(0, "Value cannot be less than 0")]
    ) # if is limited how many times discount can be used
    is_active = models.BooleanField("Is discount active", default=True)
    used_counter = models.IntegerField("Discount used counter", default=0) # how much times discount was used
    additional_info = models.TextField("Additional information", blank=True)

    class Meta:
        verbose_name = "discount"
        verbose_name_plural = "discounts"

    def __str__(self):
        return f"Discount {self.name} -{self.percent}%"

    def save(self, *args, **kwargs):
        # check if discount is still valid, update a flag and summary why is valid/invalid
        is_valid_date, invalid_date_reason = self.check_validation_date()
        is_valid_limit, invalid_limit_reason = self.check_limits()
        is_active, inactive_info = self.check_if_active()

        why_invalid = f"{inactive_info}\n{invalid_date_reason}\n{invalid_limit_reason}"
        if is_valid_date and is_valid_limit and is_active:
            self.is_currently_valid = True
            why_invalid = f"Discount is currently valid"
        else:
            self.is_currently_valid = False
        self.why_invalid_summary = why_invalid.strip("\n")

        super().save(*args, **kwargs)

    def check_validation_date(self):
        """Check if discount is still up-to-date"""
        today = datetime.date.today()

        if self.valid_since is not None and today < self.valid_since:
            return False, "It's too early to use this promotion"
        elif self.valid_to is not None and today > self.valid_to:
            return False, "Discount has expired"
        return True, ""

    def check_limits(self):
        """Check if discount hasn't reached its limit of usage"""
        if self.is_limited and self.limit_value <= self.used_counter:
            return False, "Discount's limit has been reached"
        return True, ""

    def check_if_active(self):
        """Check if discount is currently active"""
        if not self.is_active:
            return False, "Discount is currently inactive"
        return True, ""


class Visit(CreatedUpdatedMixin):
    """Model describing patient's visits in dentist's office"""
    eid = models.UUIDField("EID", default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(User, verbose_name="Patient", on_delete=models.SET_NULL, null=True, limit_choices_to={'is_patient': True})
    service = models.ForeignKey(Service, verbose_name="Service", on_delete=models.SET_NULL, null=True)
    dentists = models.ManyToManyField(User, verbose_name="Dentists", limit_choices_to={'is_dentist': True}, related_name="dentists")
    scheduled_from = models.DateTimeField("Scheduled from")
    scheduled_to = models.DateTimeField("Scheduled to")
    starting_time = models.DateTimeField("Visit starting time", blank=True, null=True)
    ending_time = models.DateTimeField("Visit ending time", blank=True, null=True)
    visit_description = models.TextField("Visit description", blank=True, null=True)
    visit_status = models.ForeignKey(VisitStatus, verbose_name="Visit's status", on_delete=models.SET_NULL, null=True)
    additional_info = models.TextField("Additional information", blank=True, null=True)
    price = models.DecimalField("Price", max_digits=10, decimal_places=2)
    discounts = models.ManyToManyField(Discount, verbose_name="Discounts", related_name="discounts", blank=True)
    final_price = models.DecimalField("Final price", max_digits=10, decimal_places=2, default=0.0,
                                      help_text="Final price of service including discounts")

    class Meta:
        verbose_name = "visit"
        verbose_name_plural = "visits"

    def __str__(self):
        scheduled_from_localtime = localtime(self.scheduled_from)
        return f"{self.patient.get_full_name()}'s visit for {self.service.name} scheduled for {scheduled_from_localtime.strftime('%d.%m.%Y %H:%M')}"

    def calculate_final_price(self):
        """Method to calculate final price of the service including discounts"""
        current_final_price = self.price

        for discount in self.discounts.all():
            decimal_discount_percent = Decimal(discount.percent)
            multiplier = Decimal(1) - decimal_discount_percent / Decimal(100)
            current_final_price *= multiplier

        self.final_price = current_final_price


class Post(CreatedUpdatedMixin):
    """Model for posts that office stuff can add and patients can read"""
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
            if self.main_photo != actual_photo: # if new photo has been uploaded delete old one and upload a new one
                self.delete_old_file(actual_photo)
        super().save(*args, **kwargs)

    def delete_main_photo(self):
        if self.main_photo:
            self.main_photo.delete()

    def delete_old_file(self, old_file):
        if old_file.name != "":
            os.remove(str(storage.base_location) + f"/{old_file.name}")


