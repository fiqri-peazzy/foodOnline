# Generated by Django 4.1.2 on 2023-01-30 12:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0002_vendor_vendor_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vendor',
            name='vendor_slug',
            field=models.SlugField(blank=True, max_length=100, unique=True),
        ),
    ]
