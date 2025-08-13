import os

from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver

from dentman.man.models import Employment
from dentman.utils import get_upload_path

@receiver(post_save, sender=Employment)
def move_contract_scan(sender, instance, created, **kwargs):
    """Signal's function for employment's contract scan to move from temporary folder into dedicated directory"""
    print("hmm?")
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
    instance.delete_contract_scan()