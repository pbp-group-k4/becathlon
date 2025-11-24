from django.urls import path
from . import views

app_name = 'auth'

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    # JSON API endpoints for Flutter
    path('json/login/', views.login_json, name='login_json'),
    path('json/signup/', views.signup_json, name='signup_json'),
    path('json/logout/', views.logout_json, name='logout_json'),
]
