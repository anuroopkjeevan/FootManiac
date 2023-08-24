from django import forms
from order.models import Order


class OrderStatusUpdateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['payment_status']
