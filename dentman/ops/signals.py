import os

from django.db.models.signals import post_save, pre_delete, m2m_changed
from django.dispatch import receiver

from dentman.ops.models import Post, Visit
from dentman.utils import get_upload_path

@receiver(post_save, sender=Post)
def move_main_photo(sender, instance, created, **kwargs):
    """Move the main photo of post's into dedicated directory"""
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
    """Delete main photo of post if post is going to be deleted"""
    instance.delete_main_photo()

@receiver(m2m_changed, sender=Visit.discounts.through)
def calculate_final_price(sender, instance, action, **kwargs):
    """Signal's function to calculate final price after every update of visit's discounts list"""
    if action in ["post_add", "post_remove", "post_clear"]:
        instance.calculate_final_price()
        instance.save(update_fields=['final_price'])