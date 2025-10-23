from django.conf import settings
from django.db import models

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    first_name = models.CharField(max_length=100, blank=True)
    last_name  = models.CharField(max_length=100, blank=True)
    phone      = models.CharField(max_length=20, blank=True)
    email = models.EmailField(max_length=254, help_text='Required. Enter a valid email address.')
    preferred_sports = models.CharField(max_length=200, blank=True)
    newsletter_opt_in = models.BooleanField(default=False)

    
    def __str__(self):
        return f"Profile({self.user.username})"
