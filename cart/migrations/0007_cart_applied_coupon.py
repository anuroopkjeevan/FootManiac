# Generated by Django 4.2.3 on 2023-08-03 11:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0006_rename_discountcoupon_coupon'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='applied_coupon',
            field=models.ManyToManyField(blank=True, to='cart.coupon'),
        ),
    ]