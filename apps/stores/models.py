from django.db import models
from django.utils import timezone

class Store(models.Model):
    name = models.CharField(max_length=150)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=120, blank=True, default="")
    country = models.CharField(max_length=100, default="Indonesia")
    longitude = models.FloatField()
    latitude = models.FloatField()
    store_hours = models.TextField(blank=True, help_text="Store opening hours (formatted text or JSON)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["city"]),
            models.Index(fields=["country"]),
            models.Index(fields=["is_active"]),
        ]
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} — {self.city}, {self.country}"
