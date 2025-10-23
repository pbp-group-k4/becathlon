from django.urls import path
from . import views

urlpatterns = [
    path("", views.detail, name="detail"),
    path("edit/", views.edit, name="edit"),
    path("ajax/toggle-newsletter/", views.toggle_newsletter_ajax, name="toggle_newsletter_ajax"),
]
