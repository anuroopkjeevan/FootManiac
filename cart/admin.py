from django.contrib import admin
from .models import Cart
from .models import CartItems,Coupon

admin.site.register(Cart)
admin.site.register(CartItems)
admin.site.register(Coupon)
