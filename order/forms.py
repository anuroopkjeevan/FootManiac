from django import forms
from .models import Order
from django import forms
from .models import Address
class OrderForm(forms.ModelForm):
    PAYMENT_METHOD_CHOICES = [
        ('RAZORPAY', 'Razorpay'),
        ('CASH_ON_DELIVERY', 'Cash on Delivery'),
        # Add other payment methods as needed
    ]

    payment_method = forms.ChoiceField(choices=PAYMENT_METHOD_CHOICES, widget=forms.RadioSelect)

    class Meta:
        model = Order
        fields = ['address', 'total_price', 'message']



class AddressForm(forms.ModelForm):
    class Meta:
      class AddressForm(forms.ModelForm):
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'House_No', 'street', 'city', 'state', 'postal_code']