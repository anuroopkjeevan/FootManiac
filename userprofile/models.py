from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid
from django.dispatch import receiver
import random
import string
from django.db.models.signals import post_save
from django.dispatch import receiver
import random
import string

from django.shortcuts import render
# from django.contrib.auth.models import User


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    addresss_line1 = models.CharField(max_length=150, null=True, blank=True)
    addresss_line2= models.CharField(max_length=150, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    House_No = models.IntegerField(default=None)
    street = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=10)

    # New field to indicate if this address is the delivery address for the user
    is_delivery_address = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s Address"




class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user.username}'s Wallet"







def generate_referral_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

class Referral(models.Model):
    referring_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referrals_made')
    referred_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referred_by')
    referral_code = models.CharField(max_length=6, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, unique=True)

    def __str__(self):
        return f"{self.referring_user.username} referred {self.referred_user.username}"
@receiver(post_save, sender=User)
def create_user_referral(sender, instance, created, **kwargs):
    if created:
        referral_code = generate_referral_code()
        Referral.objects.create(referring_user=instance, referred_user=instance, referral_code=referral_code)


# You can remove the save_user_referral signal as it's not necessary

    # Your user model fields and methods here



