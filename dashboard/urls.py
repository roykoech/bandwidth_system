from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", views.home, name="home"),
    path(
        "export-report/",
        views.export_bandwidth_report,
        name="export_bandwidth_report",
    ),
    path(
        "edit-device/<int:device_id>/",
        views.edit_device,
        name="edit_device",
    ),
    path(
    "login/",
    auth_views.LoginView.as_view(
        template_name="dashboard/login.html"
    ),
    name="login",
),
]

