from __future__ import annotations

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .access import all_permissions_required, module_permission_required
from .audit import log_event
from .models import AuditLog
from .services import (
    auto_backup_enabled,
    auto_backup_interval_minutes,
    ensure_role_groups,
    latest_backup_file,
    run_backup,
    system_status_items,
)


def root(request):
    return redirect("applet:home")


@login_required
def home(request):
    return render(request, "Applet/home.html")


@login_required
def modules(request):
    return render(request, "Applet/modules.html")


@login_required
def kanban(request):
    columns = [
        {
            "title": "Pendiente",
            "cards": [
                "v1.1.1 - Backups y restauracion PostgreSQL",
                "v1.1.4 - Credenciales PostgreSQL solo por variables de entorno",
                "v1.2 - Frontend web desacoplado y orientado a usuarios",
            ],
        },
        {
            "title": "En desarrollo",
            "cards": [
                "Depuracion puntual de SEGCEI en planilla externa",
                "Validacion automatica de backups PostgreSQL",
            ],
        },
        {
            "title": "En prueba",
            "cards": [
                "Revision funcional post v1.0.8",
                "Prueba de deploy LAN desde otro equipo",
                "Ensayo de restauracion periodico con backup real reciente",
            ],
        },
        {
            "title": "Terminado",
            "cards": [
                "Applet portal base v0.3",
                "Flujo ETL base v0.3",
                "DATA_scope remuneraciones base",
                "Dashboard y reportes",
                "Carga ETL web",
                "API inicial",
                "Django Admin personalizado",
                "Navbar superior v0.4",
                "Superusuario local root creado",
                "Control de acceso v0.4.14",
                "Operacion RRHH controlada v0.5.8c",
                "Base operativa robusta v0.6.8",
                "Contabilidad base v0.7.5a",
                "Inventario base v0.8.4",
                "Compras y ventas base v0.9.4",
                "Asistencia historica v0.9.6C",
                "Operacion SQLite reforzada v0.9.7",
                "Auditoria granular avanzada v0.9.8",
                "Integracion asistencia-remuneraciones v0.9.9",
                "Testing amplio v1.0.1",
                "Documentacion operativa cerrada v1.0.2",
                "Deploy local/red interna documentado v1.0.3",
                "Backups reales con restauracion validada v1.0.4",
                "Auditoria validada por usuario/rol v1.0.5",
                "Plan de migracion de datos documentado v1.0.6",
                "IA local cuantizada como servicio separado v1.0.7",
                "Preparacion PostgreSQL documentada v1.0.8",
                "Roadmap y version_log actualizados a v1.0.8",
                "Ensayo de migracion PostgreSQL v1.0.9",
                "Migracion real a PostgreSQL v1.0.10",
            ],
        },
    ]
    return render(request, "Applet/kanban.html", {"columns": columns})


@module_permission_required("Applet.access_admin_module")
def admin_panel(request):
    sections = [
        {"name": "Usuarios y roles", "url": "applet:security"},
        {"name": "Auditoria y logs", "url": "applet:audit"},
        {"name": "Backups", "url": "applet:backups"},
        {"name": "Estado del sistema", "url": "applet:system_status"},
        {"name": "Parametros generales", "url": None},
    ]
    return render(request, "Applet/admin_panel.html", {"sections": sections})


@module_permission_required("Applet.access_security_module")
def security(request):
    groups = ensure_role_groups()
    User = get_user_model()
    users = User.objects.order_by("username")[:50]
    return render(
        request,
        "Applet/security.html",
        {
            "groups": groups,
            "users": users,
            "user_count": User.objects.count(),
        },
    )


@module_permission_required("Applet.access_security_module")
def audit(request):
    module = request.GET.get("module", "").strip()
    action = request.GET.get("action", "").strip()
    object_type = request.GET.get("object_type", "").strip()
    object_id = request.GET.get("object_id", "").strip()
    search = request.GET.get("q", "").strip()
    logs = AuditLog.objects.select_related("user").order_by("-created_at")
    if module:
        logs = logs.filter(module__icontains=module)
    if action:
        logs = logs.filter(action__icontains=action)
    if object_type:
        logs = logs.filter(object_type__icontains=object_type)
    if object_id:
        logs = logs.filter(object_id__icontains=object_id)
    if search:
        logs = logs.filter(description__icontains=search)
    return render(
        request,
        "Applet/audit.html",
        {
            "logs": logs[:200],
            "module": module,
            "action": action,
            "object_type": object_type,
            "object_id": object_id,
            "search": search,
        },
    )


@all_permissions_required("Applet.access_admin_module", "Applet.run_backups")
def backups(request):
    backup_error = ""
    if request.method == "POST":
        try:
            run_backup(request=request, action="backup_created")
            messages.success(request, "Backup ejecutado correctamente.")
        except Exception as exc:
            backup_error = str(exc)
            messages.error(request, f"No se pudo ejecutar el backup: {backup_error}")
            log_event(request, "backup_error", "Applet", backup_error)

    latest_backup = latest_backup_file()
    return render(
        request,
        "Applet/backups.html",
        {
            "latest_backup": latest_backup,
            "backup_error": backup_error,
            "backup_dir": settings.PROJECT_ROOT / "backups",
            "auto_backup_enabled": auto_backup_enabled(),
            "auto_backup_interval": auto_backup_interval_minutes(),
        },
    )


@login_required
def system_status(request):
    return render(request, "Applet/system_status.html", {"status_items": system_status_items()})
