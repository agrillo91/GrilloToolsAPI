from django.contrib import admin
from .models import LicenseManager, DeviceActivation


# 🔹 Muestra las activaciones directamente dentro de cada licencia
class DeviceActivationInline(admin.TabularInline):
    model = DeviceActivation
    extra = 0
    readonly_fields = ('machine_id', 'ip_address', 'activated_at', 'last_checkin')
    can_delete = True


@admin.register(LicenseManager)
class LicenseManagerAdmin(admin.ModelAdmin):
    list_display = ('email', 'key', 'is_active', 'max_devices', 'activation_count', 'created_at')
    search_fields = ('email', 'key')
    list_filter = ('is_active', 'created_at')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    inlines = [DeviceActivationInline]

    def activation_count(self, obj):
        """Cuenta las activaciones registradas de esta licencia."""
        return obj.activations.count()
    activation_count.short_description = 'Activaciones'


# 🔹 Registro independiente para ver las activaciones desde el panel principal
@admin.register(DeviceActivation)
class DeviceActivationAdmin(admin.ModelAdmin):
    list_display = ('license', 'machine_id', 'ip_address', 'activated_at', 'last_checkin')
    search_fields = ('license__email', 'machine_id')
    readonly_fields = ('activated_at', 'last_checkin')
    list_filter = ('activated_at',)
