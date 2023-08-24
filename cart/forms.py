# checkout/forms.py
from django import forms
from .models import Address, Coupon
# from .models import Coupon
class ShippingAddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['House_No', 'street', 'city', 'state', 'postal_code']



class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['code', 'discount_type', 'value', 'valid_from', 'valid_to', 'max_usage_limit']
