from django.contrib import admin
from . import views
from django.urls import path
from django.shortcuts import render


urlpatterns = [
       path('add_to_cart/<int:variant_id>/', views.add_to_cart, name='add_to_cart'),
       path('cart/',views.cart,name="cart"),
       path('Remove/<int:variant_id>/', views.remove_item, name="remove_item"),
       path('checkout/', views.checkout, name='checkout'),
       path('update_cart_item/<int:item_id>/<int:quantity>/', views.update_cart_item, name='update_cart_item'),       path('page_empty/', views.page_empty, name='page_empty'),
       path('create_coupon/', views.create_coupon, name='create_coupon'),
       path('coupon_list/', views.coupon_list, name='coupon_list'),
       path('add_coupon/', views.add_coupon, name='add_coupon'),
 

         
      #  path('update_item/<int:item_id>/', views.update_item, name='update_item'),
      #  path('remove_item/<int:item_id>/', views.remove_item, name='remove_item'),
]

 
