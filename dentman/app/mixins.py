from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class CreatedUpdatedMixin(models.Model):
    created_by = models.ForeignKey(User, verbose_name="Created by", on_delete=models.SET_NULL, default=None, null=True,
                                   blank=True, editable=False, related_name='created_by_set')
    updated_by = models.ForeignKey(User, verbose_name="Updated by", on_delete=models.SET_NULL, default=None, null=True,
                                   blank=True, editable=True, related_name='updated_by_set')
    created_at = models.DateTimeField("Created at", auto_now_add=True)
    updated_at = models.DateTimeField("Updated at", auto_now=True)

    class Meta:
        abstract = True