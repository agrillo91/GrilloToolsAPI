from django.db import models
from django.utils import timezone

class LicenseManager(models.Model):
    email = models.EmailField(unique=True)
    key = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)
    max_devices = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.email} ({'Active' if self.is_active else 'Inactive'})"
    
    def can_activate(self):
        """Comprueba si la licencia aún puede activarse en otro equipo"""
        if not self.is_active:
            return False
        return self.activations.count() < self.max_devices

class DeviceActivation(models.Model):
    license = models.ForeignKey(
        LicenseManager,
        on_delete=models.CASCADE,
        related_name="activations"
    )
    machine_id = models.CharField(max_length=64)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    activated_at = models.DateTimeField(default=timezone.now)
    last_checkin = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('license', 'machine_id')  # una máquina no puede activar dos veces la misma licencia
        # pass

    def __str__(self):
        # return f"{self.machine_id} ({self.license.key})"
        return f"{self.license.key} ({self.ip_address})"