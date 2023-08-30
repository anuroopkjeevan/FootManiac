
from django.urls import path
from . import views

urlpatterns = [
path('', views.interface, name="interface"),
path('home/', views.home, name="home"),
path('home_2/', views.home_2, name='home_2'),
path('signin/', views.signin, name="signin"),
path('signup/', views.signup, name="signup"),
path('check_email/', views.check_email_view, name='check_email'),
path('product_detail/<int:product_id>/', views.product_detail, name='product_detail'),
path('Direct/<int:category_id>/', views.Direct, name='Direct'),
path('activate/<str:uidb64>/<str:token>/', views.activate, name='activate'),
path('women/', views.women, name='women'),
path('men/', views.men, name='men'),
path('children/', views.children, name='children'),
path('password_reset/', views.password_reset_request, name='password_reset_request'),
path('verify_otp/', views.verify_otp, name='verify_otp'),
path('reset_password/', views.reset_password, name='reset_password'),
]
