from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    # Web views
    path('', views.catalog_home, name='home'),
    path('category/<int:category_id>/', views.category_products, name='category'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('api/filter/', views.api_filter_products, name='api_filter'),
    path('api/product/<int:product_id>/quick-view/', views.api_product_quick_view, name='api_quick_view'),
    
    # Mobile API endpoints
    path('mobile/products/', views.mobile_products_list, name='mobile_products_list'),
    path('mobile/products/<int:product_id>/', views.mobile_product_detail, name='mobile_product_detail'),
    path('mobile/categories/', views.mobile_categories_list, name='mobile_categories_list'),
]
