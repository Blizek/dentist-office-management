# Generated by Django 5.2.4 on 2025-07-20 21:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ops', '0013_alter_discount_limit_value'),
    ]

    operations = [
        migrations.AddField(
            model_name='discount',
            name='is_actually_valid',
            field=models.BooleanField(default=False, verbose_name='Is actually valid'),
        ),
    ]
