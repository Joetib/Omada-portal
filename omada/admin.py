from django.contrib import admin

from omada.models import OmadaClient, OmadaDevice, PortalSession

# Register your models here.


@admin.register(PortalSession)
class PortalSessionAdmin(admin.ModelAdmin):
    list_display = ("client_mac", "site_name", "created_at")
    search_fields = (
        "client_mac",
        "site_name",
    )
    list_filter = ("created_at",)
    readonly_fields = ("created_at",)


@admin.register(OmadaClient)
class OmadaClientAdmin(admin.ModelAdmin):
    list_display = (
        "client_id",
        "mac_address",
        "ip_address",
        "hostname",
        "device",
        "connected_since",
        "last_seen",
    )
    search_fields = ("client_id", "mac_address", "ip_address", "hostname")
    list_filter = ("device", "connected_since", "last_seen")
    readonly_fields = ("created_at", "updated_at")


@admin.register(OmadaDevice)
class OmadaDeviceAdmin(admin.ModelAdmin):
    list_display = (
        "device_id",
        "name",
        "mac_address",
        "ip_address",
        "model",
        "firmware_version",
        "status",
        "last_seen",
    )
    search_fields = ("device_id", "name", "mac_address", "ip_address", "model")
    list_filter = ("status", "last_seen")
    readonly_fields = ("created_at", "updated_at")
