from django.urls import path

from . import views


app_name = "erp_api"

urlpatterns = [
    path("", views.index, name="index"),
    path("health/", views.health, name="health"),
    path("system-status/", views.system_status, name="system_status"),
    path("modules/", views.modules, name="modules"),
    path("payroll/summary/", views.payroll_summary, name="payroll_summary"),
    path("payroll/periods/", views.payroll_periods, name="payroll_periods"),
]
