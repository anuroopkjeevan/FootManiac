# Generated by Django 4.2.3 on 2023-07-22 15:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('admin_pa', '0015_alter_variant_variant_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='variant',
            name='variant_image',
        ),
    ]
