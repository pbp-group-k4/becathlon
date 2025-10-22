from django.urls import path
from . import views

app_name = 'recommendation'

urlpatterns = [
    path('product/<int:product_id>/', views.recommendations_for_product, name='by_product'),
    path('for-you/', views.recommendations_for_user, name='for_user'),
]
