# Generated by Django 5.2.4 on 2025-07-20 21:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ops', '0007_alter_visitstatus_is_booked'),
    ]

    operations = [
        migrations.AddField(
            model_name='discount',
            name='additional_info',
            field=models.TextField(blank=True, verbose_name='Additional information'),
        ),
        migrations.AddField(
            model_name='visitstatus',
            name='additional_info',
            field=models.TextField(blank=True, verbose_name='Additional information'),
        ),
    ]
