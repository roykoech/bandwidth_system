from .forms import DeviceForm
import csv
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Sum
from .models import Device, BandwidthUsage

def home(request):

    device_form = DeviceForm()

    if request.method == "POST":
        if not request.user.is_authenticated:
         from django.contrib.auth.views import redirect_to_login
        return redirect_to_login(request.get_full_path())
        device_form = DeviceForm(request.POST)

        if device_form.is_valid():
            device_form.save()
            messages.success(
                request,
                "Device registered successfully!"
            )
            from django.shortcuts import redirect
            return redirect("home")
    
    start_date = request.GET.get("start_date", "")
    end_date = request.GET.get("end_date", "")

    devices = Device.objects.all()

    department = request.GET.get("department", "")
    status = request.GET.get("status", "")

    if department:
        devices = devices.filter(department=department)

    if status == "connected":
        devices = devices.filter(is_connected=True)
    elif status == "disconnected":
        devices = devices.filter(is_connected=False)

    departments = (
        Device.objects.order_by("department")
        .values_list("department", flat=True)
        .distinct()
    )

    usage_totals = BandwidthUsage.objects.aggregate(
        total_download=Sum("download_mb"),
        total_upload=Sum("upload_mb"),
    )

    total_download = usage_totals["total_download"] or 0
    total_upload = usage_totals["total_upload"] or 0

    device_usage = BandwidthUsage.objects.select_related("device").all()

    if start_date:
        device_usage = device_usage.filter(recorded_at__date__gte=start_date)

    if end_date:
        device_usage = device_usage.filter(recorded_at__date__lte=end_date)

    report_totals = device_usage.aggregate(
        total_download=Sum("download_mb"),
        total_upload=Sum("upload_mb"),
    )

    report_download = report_totals["total_download"] or 0
    report_upload = report_totals["total_upload"] or 0

    context = {
        "devices": devices,
        "device_form": device_form,
        "departments": departments,
        "selected_department": department,
        "selected_status": status,
        "total_devices": Device.objects.count(),
        "connected_devices": Device.objects.filter(is_connected=True).count(),
        "disconnected_devices": Device.objects.filter(is_connected=False).count(),
        "total_download": total_download,
        "total_upload": total_upload,
        "total_usage": total_download + total_upload,
        "device_usage": device_usage,
        "start_date": start_date,
        "end_date": end_date,
        "report_download": report_download,
        "report_upload": report_upload,
        "report_total": report_download + report_upload,
    }

    return render(request, "dashboard/home.html", context)

def export_bandwidth_report(request):
    start_date = request.GET.get("start_date", "")
    end_date = request.GET.get("end_date", "")

    records = BandwidthUsage.objects.select_related("device").all()

    if start_date:
        records = records.filter(recorded_at__date__gte=start_date)

    if end_date:
        records = records.filter(recorded_at__date__lte=end_date)

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = (
        'attachment; filename="bandwidth_report.csv"'
    )

    writer = csv.writer(response)

    writer.writerow([
        "Device Name",
        "IP Address",
        "Department",
        "Download (MB)",
        "Upload (MB)",
        "Total Usage (MB)",
        "Recorded At",
    ])

    for record in records:
        writer.writerow([
            record.device.device_name,
            record.device.ip_address,
            record.device.department,
            record.download_mb,
            record.upload_mb,
            record.download_mb + record.upload_mb,
            record.recorded_at.strftime("%Y-%m-%d %H:%M:%S"),
        ])

    return response
@login_required
def edit_device(request, device_id):
    device = get_object_or_404(Device, id=device_id)
    device_form = DeviceForm(instance=device)

    if request.method == "POST":
        device_form = DeviceForm(request.POST, instance=device)

        if device_form.is_valid():
            device_form.save()
            messages.success(
                request,
                "Device updated successfully!"
            )
            from django.shortcuts import redirect
            return redirect("home")

    return render(
        request,
        "dashboard/edit_device.html",
        {
            "device_form": device_form,
            "device": device,
        },
    )

