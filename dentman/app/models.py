import os
import uuid
import re

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import FileExtensionValidator, ValidationError
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.apps import apps
from django.conf import settings

from dentman.storage import CustomFileSystemStorage
from dentman.utils import get_upload_path, delete_old_file
from dentman.app.mixins import CreatedUpdatedMixin, FullCleanMixin

storage_user = CustomFileSystemStorage(location=settings.STORAGE_ROOT / 'users-prof-photo', base_url=f"/app/profile-photos")
storage = CustomFileSystemStorage()
file_extension_validator = FileExtensionValidator(['pdf', 'jpg', 'png', 'mp4'])
phone_number_regex = r"^\+?[1-9]\d{0,2}[\d\s\-()]{4,14}$"

def get_profile_photo_upload_path(instance: models.Model, filename: str) -> str:
    """
    Function to return path where users' profile photos are stored.

    If it's new user then photo is stored in 'users-prof-photo/temp' directory
    Otherwise photo is stored in 'users-prof-photo/{eid}' directory
    """
    instance_id = instance.id or 'temp'
    if isinstance(instance_id, int):
        d = f"{instance.eid}"
    else:
        d = 'temp'
    return f"{d}/{filename}"


class User(AbstractUser, CreatedUpdatedMixin, FullCleanMixin):
    """
    User model class. It overrides AbstractUser and has additional fields:
    1) eid - additional unique id for field (isn't primary key)
    2) phone_number - CharField for user's phone number
    3) profile_photo - user profile's image
    4) is_patient - Boolean for patient status
    5) is_worker - Boolean for worker status
    6) is_dentist - Boolean for dentist status
    7) is_dev - Boolean for dev status
    8) additional_info - TextField with additional information about user
    """
    eid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    phone_number = models.CharField("Phone number", max_length=16, blank=True, null=True)
    profile_photo = models.ImageField("Profile photo", upload_to=get_profile_photo_upload_path, storage=storage_user, blank=True, null=True)
    is_patient = models.BooleanField("Is patient", default=True)
    is_worker = models.BooleanField("Is worker", default=False)
    is_dentist = models.BooleanField("Is dentist", default=False)
    is_dev = models.BooleanField("Is developer", default=False)
    additional_info = models.TextField("Additional information", blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.pk:
            actual_photo = User.objects.get(pk=self.pk).profile_photo
            if self.profile_photo != actual_photo: # if new profile photo has been uploaded delete old one and upload a new one
                delete_old_file(actual_photo)
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()

        if self.phone_number:
            if not re.match(phone_number_regex, self.phone_number):
                raise ValidationError({
                    "phone_number": "Invalid phone number format"
                })


class Attachment(CreatedUpdatedMixin, FullCleanMixin):
    """
    Attachment model class. Contains fields:
    1) file - FileField with attachment file
    2) is_active - Boolean for active status
    3) additional_info - TextField with additional information about attachment
    """
    file = models.FileField("File", upload_to=get_upload_path, storage=storage, blank=False, null=False, validators=[file_extension_validator])
    is_active = models.BooleanField("Is active", default=True)
    additional_info = models.TextField("Additional information", blank=True, null=True)

    class Meta:
        verbose_name = "Attachment"
        verbose_name_plural = "Attachments"

    def __str__(self):
        return f"Attachment {os.path.basename(self.file.name)}"


class AttachmentEntity(CreatedUpdatedMixin, FullCleanMixin):
    """
    ManyToMany model between attachments and another models. Fields are:
    1) attachment - Attachment model foreign key
    2) content_type - ContentType model foreign key
    3) object_id - PositiveIntegerField with id of object that this attachment belongs to
    4) content_object - GenericForeignKey with object that this attachment belongs to
    """
    attachment = models.ForeignKey(Attachment, on_delete=models.CASCADE, verbose_name="Attachment", null=False, blank=False)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, verbose_name="Content type", null=False, blank=False)
    object_id = models.PositiveIntegerField(verbose_name="Object ID", null=False, blank=False)
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        verbose_name = "Attachment's entity"
        verbose_name_plural = "Attachments' entities"

    def __str__(self):
        attachment_filename = os.path.basename(self.attachment.file.name)
        attachment_id = self.attachment.pk
        attachment_info = f"Attachment {attachment_filename} (ID: {attachment_id})"

        if self.object_id:
            model_class = apps.get_model(self.content_type.app_label, self.content_type.model)
            model_verbose_name = model_class._meta.verbose_name

            object_representation = f"{model_verbose_name}: {self.content_object} (ID: {self.object_id})"

            return f"{attachment_info} for {object_representation}"
        else:
            return attachment_info


class Metrics(CreatedUpdatedMixin, FullCleanMixin):
    """
    Model to describe all possible types of metrics. Fields:
    1) measurement_type - one of three measurement types: Length, Weight, Amount. Field is PositiveSmallIntegerField.
    2) measurement_name - name of measurement
    3) measurement_name_shortcut - short name of measurement
    """
    MEASUREMENT_TYPES = (
        (1, "Length"),
        (2, "Weight"),
        (3, "Amount"),
    )

    measurement_type = models.PositiveSmallIntegerField("Measurement type", choices=MEASUREMENT_TYPES, null=False, blank=False)
    measurement_name = models.CharField("Measurement name", max_length=100, null=False, blank=False)
    measurement_name_shortcut = models.CharField("Measurement name shortcut", max_length=10, null=False, blank=False)

    class Meta:
        verbose_name = "Metric"
        verbose_name_plural = "Metrics"

    def __str__(self):
        return f"Metric for {self.get_measurement_type_display()} - {self.measurement_name} ({self.measurement_name_shortcut})"
