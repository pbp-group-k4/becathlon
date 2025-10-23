from django.urls import path
from . import views

app_name = "stores"

urlpatterns = [
    path("", views.store_locator, name="locator"),
    path("api/", views.api_stores, name="api"),
    path("<int:store_id>/", views.store_detail, name="detail"),
]
