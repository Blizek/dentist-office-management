import os

from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver

from dentman.app.models import User, Attachment
from dentman.utils import get_upload_path

@receiver(post_save, sender=User)
def move_profile_photo(sender, instance, created, **kwargs):
    if instance.profile_photo and 'temp' in instance.profile_photo.name:
        old_name = instance.profile_photo.name
        filename = os.path.basename(old_name)
        new_name = get_upload_path(instance, filename)
        if old_name != new_name:
            file = instance.profile_photo.storage.open(old_name)
            instance.profile_photo.storage.save(new_name, file)
            instance.profile_photo.storage.delete(old_name)
            instance.profile_photo.name = new_name
            instance.save(update_fields=['profile_photo'])

@receiver(pre_delete, sender=User)
def delete_profile_photo(sender, instance, **kwargs):
    instance.delete_profile_photo()
    
@receiver(post_save, sender=Attachment)
def move_file(sender, instance, created, **kwargs):
    if instance.file and 'temp' in instance.file.name:
        old_name = instance.file.name
        filename = os.path.basename(old_name)
        new_name = get_upload_path(instance, filename)
        if old_name != new_name:
            file = instance.file.storage.open(old_name)
            instance.file.storage.save(new_name, file)
            instance.file.storage.delete(old_name)
            instance.file.name = new_name
            instance.save(update_fields=['file'])

@receiver(pre_delete, sender=Attachment)
def delete_file(sender, instance, **kwargs):
    instance.delete_file()