from django.urls import path
from . import views

urlpatterns = [
    path("", views.detail, name="detail"),
    path("edit/", views.edit, name="edit"),
    path("ajax/toggle-newsletter/", views.toggle_newsletter_ajax, name="toggle_newsletter_ajax"),
    path("ajax/switch-account-type/", views.switch_account_type_ajax, name="switch_account_type_ajax"),
    path("api/", views.api_profile_detail, name="api_profile_detail"),
    path("api/update/", views.api_profile_update, name="api_profile_update"),

]
