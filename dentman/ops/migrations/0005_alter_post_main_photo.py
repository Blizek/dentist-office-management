# Generated by Django 5.2.4 on 2025-07-20 14:26

import dentman.storage
import dentman.utils
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ops', '0004_alter_post_text_html'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='main_photo',
            field=models.ImageField(help_text='Main photo that will show up on the lists of posts and the main photo at the post', null=True, storage=dentman.storage.CustomFileSystemStorage(), upload_to=dentman.utils.get_upload_path, verbose_name='Main photo'),
        ),
    ]
