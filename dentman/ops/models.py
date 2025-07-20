import uuid
import os

from django.db import models
from django.contrib.auth import get_user_model

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
    is_booked = models.BooleanField("Is visit booked", default=True)
    is_accepted_by_patient = models.BooleanField("Is accepted by patient", default=False)
    is_postponed = models.BooleanField("Is visit postponed", default=False)
    is_in_progress = models.BooleanField("Is visit in progress", default=False)
    is_finished = models.BooleanField("Is visit finished", default=False)
    is_resigned_by_patient = models.BooleanField("Is visit resigned by patient", default=False)
    is_resigned_by_dentist = models.BooleanField("Is visit resigned by dentist", default=False)
    is_resigned_by_office = models.BooleanField("Is visit resigned by office", default=False)

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
    percent = models.FloatField("Discount percent", default=0.0)
    discount_type = models.CharField("Discount type", max_length=50, choices=DISCOUNT_TYPES)
    valid_since = models.DateField("Discount valid date", null=True, blank=True)
    valid_to = models.DateField("Discount valid to", null=True, blank=True)
    is_limited = models.BooleanField("Is discount limited", default=False)
    limit_value = models.IntegerField("Discount limit value", default=0, null=True, blank=True)
    used_counter = models.IntegerField("Discount used counter", default=0)

    class Meta:
        verbose_name = "discount"
        verbose_name_plural = "discounts"

    def __str__(self):
        return f"Discount {self.name} -{self.percent}%"

class Visit(CreatedUpdatedMixin):
    eid = models.UUIDField("EID", default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(User, verbose_name="Patient", on_delete=models.SET_NULL, null=True, limit_choices_to={'is_patient': True})
    dentists = models.ManyToManyField(User, verbose_name="Dentists", limit_choices_to={'is_dentist': True}, related_name="dentists")
    scheduled_from = models.DateTimeField("Scheduled from")
    scheduled_to = models.DateTimeField("Scheduled to")
    starting_time = models.DateTimeField("Visit starting time")
    ending_time = models.DateTimeField("Visit ending time")
    visit_description = models.TextField("Visit description")
    visit_status = models.ForeignKey(VisitStatus, verbose_name="Visit's status", on_delete=models.SET_NULL, null=True)
    additional_info = models.TextField("Additional information")
    price = models.DecimalField("Price", max_digits=10, decimal_places=2)
    discounts = models.ManyToManyField(Discount, verbose_name="Discounts", related_name="discounts")

    class Meta:
        verbose_name = "visit"
        verbose_name_plural = "visits"

    def __str__(self):
        return f"Visit {self.patient.get_full_name()} at {self.scheduled_from}"

class Post(CreatedUpdatedMixin):
    title = models.CharField("Title", max_length=500, unique=True)
    slug = models.SlugField("Slug", max_length=500, unique=True)
    main_photo = models.ImageField("Main photo", help_text="Main photo that will show up on the lists of posts and the main photo at the post",
                                   upload_to=get_upload_path, storage=storage, null=True)
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


