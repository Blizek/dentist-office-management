# Generated by Django 5.2.4 on 2025-07-13 12:09

import dentman.app.models
import dentman.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='additional_info',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='is_dev',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='is_patient',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='user',
            name='is_worker',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='phone_number',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Phone number'),
        ),
        migrations.AddField(
            model_name='user',
            name='profile_photo',
            field=models.FileField(blank=True, null=True, storage=dentman.storage.CustomFileSystemStorage(), upload_to=dentman.app.models.get_upload_path, verbose_name='Profile photo'),
        ),
    ]
