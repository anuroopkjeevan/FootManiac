from django.contrib import admin
from .models import Category,Product, ProductVariant,size,ProductImage,Color,Offer

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(size)
admin.site.register(ProductVariant)
admin.site.register(ProductImage)
admin.site.register(Color)
admin.site.register(Offer)



