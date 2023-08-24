from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path, include
from .import views
urlpatterns = [
    path('place_order/<int:selected_address_id>/', views.place_order, name='place_order'),
    path('Add_address/', views.Add_address, name='Add_address'),
    path('choose_delivery_address/<int:address_id>/', views.choose_delivery_address, name='choose_delivery_address'),
    path('initiate_payment/', views.initiate_payment, name='initiate_payment'),
    path('online_payment_order/<int:add_id>',views.online_payment_order,name='online_payment_order'),
    path('add_select/', views.add_select, name='add_select'),
    path('order_confirmation/', views.order_confirmation, name='order_confirmation'),
    path('place-order-with-wallet/<int:selected_address_id>/', views.place_order_with_wallet, name='place_order_with_wallet'),
    


]

 