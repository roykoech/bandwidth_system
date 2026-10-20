from django import forms
from .models import Device

class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = [
            "device_name",
            "ip_address",
            "mac_address",
            "department",
            "is_connected",
        ]

        widgets = {
            "device_name": forms.TextInput(attrs={
                "placeholder": "e.g. Office-PC-02"
            }),
            "ip_address": forms.TextInput(attrs={
                "placeholder": "e.g. 192.168.10.11"
            }),
            "mac_address": forms.TextInput(attrs={
                "placeholder": "e.g. 02:00:00:00:00:02"
            }),
            "department": forms.TextInput(attrs={
                "placeholder": "e.g. Finance"
            }),
        }
