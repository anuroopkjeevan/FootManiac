from django.contrib import admin
from django.urls import path
from .import views
from authentication.views import product_detail


urlpatterns = [
        path('download_order_pdf_sales/',views.download_order_pdf_sales,name='download_order_pdf_sales'),
        path('sales/' ,views.sales,name='sales'),
        path('allsales/' ,views.allsales,name='allsales'),
        path('download-report/', views.download_report, name='download_report'),
        path('dashboard/',views.dashboard,name='dashboard'),
        path('admin_panel/', views.admin_panel, name='admin_panel'),
        path('add_category/', views.add_category, name='add_category'),
        path('category/<int:pk>/edit/', views.edit_category, name='edit_category'),
        path('category/', views.category, name='category'),
        path('product/', views.product, name='product'),
        path('add_image/', views.add_image, name='add_image'),
        path('add_product/', views.add_product, name='add_product'),
        path('edit_category/<int:category_id>',views.edit_category,name="edit_category"),
        path('block_users/<int:user_id>/',views.block_user,name='block_user'),
        path('unblock_users/<int:user_id>/',views.unblock_user,name='unblock_user'),
        path('disable/<int:product_id>/', views.disable, name='disable'),
        path('enable/<int:product_id>/', views.enable, name='enable'),
        path('product_variant/<int:product_id>/', views.product_variant, name='product_variant'),
        path('search/', views.search_view, name='search_view'), 
        path('search/', views.search_view, name='search_view'),
        path('search/<int:product_id>/', views.search_view, name='search_view'),
        path('add_variant/<int:product_id>/', views.add_variant, name='add_variant'),
]
