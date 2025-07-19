import os

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import FileExtensionValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.apps import apps

from dentman.storage import CustomFileSystemStorage
from dentman.utils import get_upload_path

storage = CustomFileSystemStorage()
file_extension_validator = FileExtensionValidator(['pdf', 'jpg', 'png', 'mp4'])


class User(AbstractUser):
    """User model class"""
    phone_number = models.CharField("Phone number", max_length=20, blank=True, null=True)
    profile_photo = models.ImageField("Profile photo", upload_to=get_upload_path, storage=storage, blank=True, null=True)
    is_patient = models.BooleanField("Is patient", default=True)
    is_worker = models.BooleanField("Is worker", default=False)
    is_dentist = models.BooleanField("Is dentist", default=False)
    is_dev = models.BooleanField("Is developer", default=False)
    additional_info = models.TextField("Additional information", blank=True, null=True)

    def delete_profile_photo(self):
        if self.profile_photo:
            self.profile_photo.delete()

class Attachment(models.Model):
    """Attachment model class"""
    file = models.FileField("File", upload_to=get_upload_path, storage=storage, blank=False, null=False, validators=[file_extension_validator])
    is_active = models.BooleanField("Is active", default=True)
    additional_info = models.TextField("Additional information", blank=True, null=True)

    class Meta:
        verbose_name = "Attachment"
        verbose_name_plural = "Attachments"

    def __str__(self):
        return f"Attachment {os.path.basename(self.file.name)}"

    def delete_file(self):
        if self.file:
            self.file.delete()

class AttachmentEntity(models.Model):
    """ManyToMany model between attachments and another models"""
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

class Metrics(models.Model):
    """Model to describe all possible types of metrics"""
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
