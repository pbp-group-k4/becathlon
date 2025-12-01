from django.urls import path
from . import views

app_name = 'order'

urlpatterns = [
    path('', views.order_list, name='order_list'),
    path('<int:order_id>/', views.order_detail, name='order_detail'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('checkout/success/<int:order_id>/', views.checkout_success, name='checkout_success'),
    # AJAX endpoints
    path('<int:order_id>/status/', views.check_delivery_status, name='check_delivery_status'),
    path('<int:order_id>/rate/', views.submit_rating, name='submit_rating'),
    
    # Flutter API endpoints
    path('flutter/checkout/', views.flutter_checkout, name='flutter_checkout'),
    path('flutter/list/', views.flutter_order_list, name='flutter_order_list'),
    path('flutter/<int:order_id>/', views.flutter_order_detail, name='flutter_order_detail'),
    path('flutter/<int:order_id>/status/', views.flutter_check_delivery_status, name='flutter_check_delivery_status'),
    path('flutter/<int:order_id>/rate/', views.flutter_submit_rating, name='flutter_submit_rating'),
]
