from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'email', 'newsletter_opt_in')
    search_fields = ('user__username', 'email', 'first_name', 'last_name')
    list_filter = ('newsletter_opt_in', 'user__date_joined')
    readonly_fields = ('user',)
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Preferences', {
            'fields': ('preferred_sports', 'newsletter_opt_in')
        }),
    )

