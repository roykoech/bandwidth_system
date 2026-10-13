from django.contrib import admin
from .models import Device, BandwidthUsage

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = (
        "device_name",
        "ip_address",
        "department",
        "is_connected",
    )
    list_filter = ("department", "is_connected")
    search_fields = ("device_name", "ip_address", "mac_address")

@admin.register(BandwidthUsage)
class BandwidthUsageAdmin(admin.ModelAdmin):
    list_display = (
        "device",
        "download_mb",
        "upload_mb",
        "recorded_at",
    )
    list_filter = ("recorded_at",)
