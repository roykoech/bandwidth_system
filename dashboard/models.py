from django.db import models
class Device(models.Model):
    device_name = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField(unique=True)
    mac_address = models.CharField(max_length=17, unique=True)
    department = models.CharField(max_length=100)
    is_connected = models.BooleanField(default=False)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.device_name

class BandwidthUsage(models.Model):
    device = models.ForeignKey(
    Device,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name="bandwidth_records"
)

    download_mb = models.FloatField(default=0)
    upload_mb = models.FloatField(default=0)
    recorded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
     if self.device:
        return f"{self.device.device_name} - {self.recorded_at}"
     return f"Deleted device - {self.recorded_at}"

