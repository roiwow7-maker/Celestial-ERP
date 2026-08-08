from django.urls import path

from . import views


app_name = "attendance"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("registros/", views.records, name="records"),
    path("registros/nuevo/", views.record_create, name="record_create"),
    path("registros/<int:record_id>/editar/", views.record_update, name="record_update"),
    path("trabajador/<int:employee_id>/", views.employee_attendance, name="employee_attendance"),
    path("mensual/", views.monthly_report, name="monthly_report"),
    path("exportar-csv/", views.export_csv, name="export_csv"),
]
