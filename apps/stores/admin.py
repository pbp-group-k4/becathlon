from django.contrib import admin
from .models import Store

@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "is_active")
    list_filter = ("is_active", "city")
    search_fields = ("name", "address", "city")
