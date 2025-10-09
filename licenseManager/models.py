from django.db import models

class LicenseManager(models.Model):
    email = models.EmailField(unique=True)
    key = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email} ({'Active' if self.is_active else 'Inactive'})"
