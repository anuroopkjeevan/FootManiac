from django.contrib import admin
from . import views
from django.urls import path
from django.shortcuts import render

urlpatterns = [
    # Other URL patterns for other views in your project
    path('update_profile/', views.update_profile, name='update_profile'),
    path('profile/', views.profile, name='profile'),
    path('address_list/', views.address_list, name='address_list'),
    path('addresses/add/', views.address_add, name='address_add'),
    path('addresses/edit/<int:address_id>/', views.address_add, name='edit_address'),
    path('change_password/', views.change_password, name='change_password'),
    path('logout/', views.logout_view, name='logout'),
    # path('addresses/', views.address_list, name='address_list'),
    # path('address/add/', views.address_form, name='address_add'),
    path('address/<int:address_id>/edit/', views.address_add, name='address_edit'),
    path('order_list/', views.order_list, name='order_list'),
    path('orders/<int:order_id>/', views.order_details, name='order_details'),
    path('adorder_details/<int:order_id>/', views.adorder_details, name='adorder_details'),
    path('cancel_order/<int:order_id>/', views.cancel_order, name='cancel_order'),
    # path('update_order_status/<int:order_id>/<str:new_status>/', views.update_order_status, name='update_order_status'),
    path('show_wallet/', views.show_wallet, name='show_wallet'),
]