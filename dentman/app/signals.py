import os

from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver

from dentman.app.models import User, Attachment, get_profile_photo_upload_path
from dentman.utils import get_upload_path, delete_old_file

@receiver(post_save, sender=User)
def move_profile_photo(sender, instance, created, **kwargs):
    """Signal's function for user's profile photo to move from temporary folder into dedicated directory"""
    if instance.profile_photo and 'temp' in instance.profile_photo.name:
        old_name = instance.profile_photo.name
        filename = os.path.basename(old_name)
        new_name = get_profile_photo_upload_path(instance, filename)
        if old_name != new_name:
            file = instance.profile_photo.storage.open(old_name)
            instance.profile_photo.storage.save(new_name, file)
            instance.profile_photo.storage.delete(old_name)
            instance.profile_photo.name = new_name
            instance.save(update_fields=['profile_photo'])

@receiver(pre_delete, sender=User)
def delete_profile_photo(sender, instance, **kwargs):
    """Signal's function to delete user's profile photo when user is going to be deleted"""
    delete_old_file(instance.profile_photo)

@receiver(post_save, sender=Attachment)
def move_file(sender, instance, created, **kwargs):
    """Signal's function to move attachment file from temporary folder into dedicated directory"""
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
    """Signal's function to delete attachment file when attachment is going to be deleted"""
    delete_old_file(instance.file)