# Generated by Django 4.2.3 on 2023-08-01 07:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0003_address_email_address_first_name_address_last_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='is_delivery_address',
            field=models.BooleanField(default=False),
        ),
    ]