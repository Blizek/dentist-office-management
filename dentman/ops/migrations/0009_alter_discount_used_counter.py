# Generated by Django 5.2.4 on 2025-07-20 21:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ops', '0008_discount_additional_info_visitstatus_additional_info'),
    ]

    operations = [
        migrations.AlterField(
            model_name='discount',
            name='used_counter',
            field=models.IntegerField(default=0, editable=False, verbose_name='Discount used counter'),
        ),
    ]
