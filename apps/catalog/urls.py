from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.catalog_home, name='home'),
    path('category/<int:category_id>/', views.category_products, name='category'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('api/filter/', views.api_filter_products, name='api_filter'),
    path('api/product/<int:product_id>/quick-view/', views.api_product_quick_view, name='api_quick_view'),
]
