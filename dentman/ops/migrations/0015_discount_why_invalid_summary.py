# Generated by Django 5.2.4 on 2025-07-20 22:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ops', '0014_discount_is_actually_valid'),
    ]

    operations = [
        migrations.AddField(
            model_name='discount',
            name='why_invalid_summary',
            field=models.TextField(blank=True, help_text='There is reason why this discount is not valid', verbose_name='Why invalid summary'),
        ),
    ]
