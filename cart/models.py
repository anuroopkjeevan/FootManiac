from django.db import models
from django.contrib.auth.models import User
from admin_pa.models import ProductVariant
from userprofile.models import *
from django.db.models import Sum
from decimal import Decimal
from django.utils import timezone

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    applied_coupon = models.OneToOneField('Coupon', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"Cart #{self.pk} for {self.user.username}"

    def get_total_price(self):
        return self.cartitems_set.aggregate(total_price=Sum('price'))['total_price']
    
    def apply_coupon(self, discount_percentage):
        total = self.calculate_total()  # Implement calculate_total() method based on your cart items

        # Handle the case where total is None (e.g., no cart items)
        if total is None:
            return None

        discount = (total * Decimal(discount_percentage)) / Decimal('100')
        return total - discount
    
    
    
class CartItems(models.Model):
    cart = models.ForeignKey("Cart", on_delete=models.CASCADE)
    product = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    quantity = models.PositiveBigIntegerField(default=1)
    price = models.DecimalField( max_digits=8, decimal_places=2)


    def get_item_price(self):
        return Decimal(self.price) * Decimal(self.quantity)



class Coupon(models.Model):
    code = models.CharField(max_length=20, unique=True)
    discount_type = models.CharField(max_length=10, choices=[('percentage', 'Percentage'), ('fixed', 'Fixed Amount')])
    value = models.DecimalField(max_digits=10, decimal_places=2)
    valid_from = models.DateTimeField(default=timezone.now)
    valid_to = models.DateTimeField()
    max_usage_limit = models.PositiveIntegerField(default=1)
    used_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.code

    