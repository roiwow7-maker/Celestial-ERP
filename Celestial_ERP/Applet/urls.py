from django.urls import path

from . import views


app_name = "applet"

urlpatterns = [
    path("", views.home, name="home"),
    path("modules/", views.modules, name="modules"),
    path("kanban/", views.kanban, name="kanban"),
    path("admin-panel/", views.admin_panel, name="admin_panel"),
    path("security/", views.security, name="security"),
    path("audit/", views.audit, name="audit"),
    path("backups/", views.backups, name="backups"),
    path("system-status/", views.system_status, name="system_status"),
]
