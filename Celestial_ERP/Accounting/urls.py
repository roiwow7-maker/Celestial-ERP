from django.urls import path

from . import views


app_name = "accounting"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("plan-cuentas/", views.chart_accounts, name="chart_accounts"),
    path("plan-cuentas/nueva/", views.chart_account_create, name="chart_account_create"),
    path("plan-cuentas/<int:account_id>/editar/", views.chart_account_update, name="chart_account_update"),
    path("centros-costo/", views.cost_centers, name="cost_centers"),
    path("centros-costo/nuevo/", views.cost_center_create, name="cost_center_create"),
    path("centros-costo/<int:center_id>/editar/", views.cost_center_update, name="cost_center_update"),
    path("mapeos/", views.mappings, name="mappings"),
    path("mapeos/nuevo/", views.mapping_create, name="mapping_create"),
    path("mapeos/<int:mapping_id>/editar/", views.mapping_update, name="mapping_update"),
    path("asientos/", views.journal_entries, name="journal_entries"),
    path("asientos/generar-remuneraciones/", views.generate_payroll_journal, name="generate_payroll_journal"),
    path("asientos/<int:journal_id>/", views.journal_detail, name="journal_detail"),
    path("reportes/", views.reports, name="reports"),
]
