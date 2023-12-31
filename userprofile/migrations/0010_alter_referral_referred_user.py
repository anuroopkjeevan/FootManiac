# Generated by Django 4.2.3 on 2023-08-12 05:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('userprofile', '0009_alter_referral_timestamp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='referral',
            name='referred_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='referred_by', to=settings.AUTH_USER_MODEL),
        ),
    ]
