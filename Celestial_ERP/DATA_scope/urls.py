from django.urls import path

from . import views

app_name = "data_scope"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("remuneraciones/", views.dashboard, name="payroll_dashboard"),
    path("remuneraciones/trabajadores/", views.employees, name="employees"),
    path("remuneraciones/trabajadores/nuevo/", views.employee_create, name="employee_create"),
    path("remuneraciones/trabajadores/<int:employee_id>/", views.employee_detail, name="employee_detail"),
    path("remuneraciones/trabajadores/<int:employee_id>/editar/", views.employee_update, name="employee_update"),
    path("remuneraciones/periodos/", views.periods, name="periods"),
    path("remuneraciones/periodos/nuevo/", views.period_create, name="period_create"),
    path("remuneraciones/periodos/<int:period_id>/editar/", views.period_update, name="period_update"),
    path("remuneraciones/items/", views.items, name="items"),
    path("remuneraciones/items/nuevo/", views.item_create, name="item_create"),
    path("remuneraciones/items/<int:item_id>/editar/", views.item_update, name="item_update"),
    path("remuneraciones/liquidaciones/", views.summaries, name="summaries"),
    path("remuneraciones/liquidaciones/nueva/", views.summary_create, name="summary_create"),
    path("remuneraciones/liquidaciones/<int:summary_id>/", views.summary_detail, name="summary_detail"),
    path("remuneraciones/liquidaciones/<int:summary_id>/editar/", views.summary_update, name="summary_update"),
    path("remuneraciones/movimientos/", views.entries, name="entries"),
    path("remuneraciones/movimientos/nuevo/", views.entry_create, name="entry_create"),
    path("remuneraciones/movimientos/<int:entry_id>/editar/", views.entry_update, name="entry_update"),
    path("kanban/", views.kanban, name="kanban"),
    path("reportes/", views.reports, name="reports"),
    path("reportes/exportar-csv/", views.export_reports_csv, name="export_reports_csv"),
    path("remuneraciones/trabajadores/<int:employee_id>/exportar-csv/", views.export_employee_csv, name="export_employee_csv"),
    path("remuneraciones/periodos/<int:period_id>/exportar-csv/", views.export_period_csv, name="export_period_csv"),
    path("remuneraciones/liquidaciones/<int:summary_id>/exportar-csv/", views.export_summary_csv, name="export_summary_csv"),
    path("cargas/", views.upload_data, name="upload_data"),
    path("cargas/estado/<str:run_id>/", views.upload_status, name="upload_status"),
    path("cargas/probar-rutas/", views.route_probe, name="route_probe"),
    path("cargas/descargar/<str:run_id>/<path:relative_path>", views.download_upload_output, name="download_upload_output"),
]
