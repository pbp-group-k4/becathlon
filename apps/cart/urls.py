from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_view, name='cart_view'),
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('clear/', views.clear_cart, name='clear_cart'),
    path('checkout/', views.checkout_view, name='checkout_view'),
    path('api/summary/', views.api_cart_summary, name='api_cart_summary'),
    path('api/count/', views.api_cart_count, name='api_cart_count'),

    # flutter web routes
    path('flutter/', views.flutter_cart_view, name='flutter_cart_view'),
    path('flutter/add/<int:product_id>/', views.flutter_add_to_cart, name='flutter_add_to_cart'),
    path('flutter/update/<int:item_id>/', views.flutter_update_cart_item, name='flutter_update_cart_item'),
    path('flutter/remove/<int:item_id>/', views.flutter_remove_from_cart, name='flutter_remove_from_cart'),
    path('flutter/clear/', views.flutter_clear_cart, name='flutter_clear_cart'),
    path('flutter/count/', views.flutter_cart_count, name='flutter_cart_count'),
    path('flutter/checkout/', views.flutter_checkout_view, name='flutter_checkout_view'),
]