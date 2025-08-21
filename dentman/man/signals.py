import os

from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver

from dentman.man.models import Employment, Inaccessibility
from dentman.utils import get_upload_path, delete_old_file

@receiver(post_save, sender=Employment)
def move_contract_scan(sender, instance, created, **kwargs):
    """Signal's function for employment's contract scan to move from temporary folder into dedicated directory"""
    if instance.contract_scan and 'temp' in instance.contract_scan.name:
        old_name = instance.contract_scan.name
        filename = os.path.basename(old_name)
        new_name = get_upload_path(instance, filename)
        if old_name != new_name:
            file = instance.contract_scan.storage.open(old_name)
            instance.contract_scan.storage.save(new_name, file)
            instance.contract_scan.storage.delete(old_name)
            instance.contract_scan.name = new_name
            instance.save(update_fields=['contract_scan'])

@receiver(pre_delete, sender=Employment)
def delete_contract_scan(sender, instance, **kwargs):
    """Signal's function to delete employment's contract scan when user is going to be deleted"""
    delete_old_file(instance.contract_scan)

@receiver(post_save, sender=Inaccessibility)
def set_none_when_is_for_whole_day(sender, instance, created, **kwargs):
    """
    Signal's function to set both `since` and `until` to `None` when inaccessibility is for whole day (`is_whole_day` flag equals `True`).
    """
    if instance.is_whole_day and (instance.since is not None or instance.until is not None):
        instance.since = None
        instance.until = None
        instance.save(update_fields=['since', 'until'])