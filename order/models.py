from decimal import Decimal
from django.db import models
from datetime import timedelta, timezone
from django.db import models
from admin_pa.models import ProductVariant
from userprofile.models import *
from django.utils import timezone

class Order(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('PENDING','pending'),
        ('PAID','paid'),
        ('CANCELLED','cancelled'),
        ('DELIVERED','Delivered'),
        ('SHIPPED','Shipped'),
        ('RETURNED','Returned'),
        ('ORDERED','Ordered'),
        ('COMPLETED','Completed')
    ]
    PAYMENT_METHOD_CHOICES = [
        ('RAZORPAY', 'razorpay'),
        ('CASH_ON_DELIVERY', 'Cash on Delivery'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    total_price = models.FloatField(null=False)
    payment_status = models.CharField(max_length=25, choices=PAYMENT_STATUS_CHOICES, default='ordered')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    message = models.TextField(null=True)
    tracking_no = models.CharField(max_length=150, null=True)
    order_date = models.DateTimeField(default=timezone.now)
    delivery_date = models.DateTimeField(blank=True, null=True)
    razor_pay_order_id = models.CharField(max_length=150, null=True, blank=True)
    razor_pay_payment_id = models.CharField(max_length=150, null=True, blank=True)
    razor_pay_payment_signature = models.CharField(max_length=150, null=True, blank=True)
    discounted_total_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    def __str__(self):
        return f"Order {self.id}"

    def second_str(self):
        return f"{self.id} {self.tracking_no}"

    def save(self, *args, **kwargs):
        if not self.order_date:
            self.order_date = timezone.now()
        if not self.delivery_date:
            self.delivery_date = self.order_date + timedelta(hours=24)
        super().save(*args, **kwargs)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    price = models.FloatField(null=False)
    quantity = models.IntegerField(null=False)

    def __str__(self):
        return f"Order Item {self.id} - Order: {self.order.id}, Tracking No: {self.order.tracking_no}"
