from django.contrib import admin
from . import views
from django.urls import path
from django.shortcuts import render


urlpatterns = [
    path( 'wishlist/', views.wishlist,name='wishlist'),
    path('add_to_wishlist/<int:variant_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wremove/<int:item_id>/', views.wremove, name='wremove'),
       path('wishlist_to_cart/<int:variant_id>/', views.wishlist_to_cart, name='wishlist_to_cart'),
 
]