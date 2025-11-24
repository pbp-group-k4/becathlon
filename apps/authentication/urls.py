from django.urls import path
from . import views

app_name = 'auth'

urlpatterns = [
    # Web views
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Flutter mobile API endpoints
    path('flutter/login/', views.flutter_login, name='flutter_login'),
    path('flutter/register/', views.flutter_register, name='flutter_register'),
    path('flutter/logout/', views.flutter_logout, name='flutter_logout'),
]
