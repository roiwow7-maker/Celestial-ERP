from django.urls import path

from . import v1, views


app_name = "erp_api"

urlpatterns = [
    path("v1/session/", v1.session_view, name="v1_session"),
    path("v1/login/", v1.login_view, name="v1_login"),
    path("v1/logout/", v1.logout_view, name="v1_logout"),
    path("v1/catalog/", v1.catalog, name="v1_catalog"),
    path("v1/reports/", v1.reports, name="v1_reports"),
    path("v1/uploads/", v1.uploads, name="v1_uploads"),
    path("v1/uploads/<str:run_id>/", v1.upload_status, name="v1_upload_status"),
    path("v1/users/", v1.users, name="v1_users"),
    path("v1/users/<int:user_id>/", v1.user_detail, name="v1_user_detail"),
    path("v1/resources/<slug:resource>/", v1.resource_collection, name="v1_resource_collection"),
    path("v1/resources/<slug:resource>/<int:object_id>/", v1.resource_detail, name="v1_resource_detail"),
    path("", views.index, name="index"),
    path("health/", views.health, name="health"),
    path("system-status/", views.system_status, name="system_status"),
    path("modules/", views.modules, name="modules"),
    path("payroll/summary/", views.payroll_summary, name="payroll_summary"),
    path("payroll/periods/", views.payroll_periods, name="payroll_periods"),
]
