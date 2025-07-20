import os

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from dentman.ops.models import Post
from dentman.utils import get_upload_path

@receiver(post_save, sender=Post)
def move_main_photo(sender, instance, created, **kwargs):
    if instance.main_photo and 'temp' in instance.main_photo.name:
        old_name = instance.main_photo.name
        filename = os.path.basename(old_name)
        new_name = get_upload_path(instance, filename)
        if old_name != new_name:
            file = instance.main_photo.storage.open(old_name)
            instance.main_photo.storage.save(new_name, file)
            instance.main_photo.storage.delete(old_name)
            instance.main_photo.name = new_name
            instance.save(update_fields=['main_photo'])

@receiver(pre_delete, sender=Post)
def delete_main_photo(sender, instance, **kwargs):
    instance.delete_main_photo()