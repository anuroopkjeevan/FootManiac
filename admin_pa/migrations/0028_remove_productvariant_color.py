# Generated by Django 4.2.3 on 2023-08-22 03:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('admin_pa', '0027_offer'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productvariant',
            name='color',
        ),
    ]
