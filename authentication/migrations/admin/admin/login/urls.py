from django.urls import path, include
from login import views
urlpatterns = [
    path('', views.signin,name='signin'),
    path('signup', views.signup , name='signup'),
    path('home', views.home , name='home'),
    path('admin_panel',views.admin_panel , name='admin_panel'),
    path('signout', views.signout, name='signout'),
    # path('edit_user/<int:id>/', views.edit_user , name='edit_user'),
    path('update_user/<int:user_id>/', views.update_user , name='update_user'),
    path('delete_user/<int:user_id>/', views.delete_user , name='delete_user'),
    path('create_user' , views.create_user , name='create_user')
]
