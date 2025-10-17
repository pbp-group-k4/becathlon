from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('api/products/', views.get_products_ajax, name='get_products_ajax'),
    path('api/products/add/', views.add_product_ajax, name='add_product_ajax'),
    path('api/products/<int:product_id>/delete/', views.delete_product_ajax, name='delete_product_ajax'),
]
