from django.contrib import admin
from .models import LicenseManager
# Register your models here.

@admin.register(LicenseManager)
class LicenseManagerAdmin(admin.ModelAdmin):
    list_display = ('email', 'key', 'is_active', 'created_at')
    search_fields = ('email', 'key')
    list_filter = ('is_active', 'created_at')
    ordering = ('-created_at',)