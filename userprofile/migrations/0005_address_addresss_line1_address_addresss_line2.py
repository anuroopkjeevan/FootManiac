# Generated by Django 4.2.3 on 2023-08-02 06:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0004_address_is_delivery_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='addresss_line1',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AddField(
            model_name='address',
            name='addresss_line2',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
    ]
