from __future__ import annotations

import io
import threading
import time
from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management import call_command
from django.db import connection

from DATA_scope.models import Employee, ImportRun, PayrollEntry, PayrollItem, PayrollPeriod, PayrollSummary
from Attendance.models import AttendanceRecord
from Accounting.models import ChartAccount, CostCenter, JournalEntry, JournalEntryLine, PayrollItemAccountMapping
from Inventory.models import Product, StockBalance, StockMovement, Warehouse
from Commerce.models import Customer, PurchaseOrder, PurchaseOrderLine, SalesOrder, SalesOrderLine, Supplier

from .audit import log_event
from .version import ERP_VERSION


ROLE_NAMES = ["Administrador", "RRHH", "Contabilidad", "Solo lectura"]
_backup_lock = threading.Lock()


STANDARD_DATA_MODELS = [
    Employee,
    PayrollPeriod,
    PayrollItem,
    PayrollEntry,
    PayrollSummary,
    ImportRun,
    AttendanceRecord,
    ChartAccount,
    CostCenter,
    PayrollItemAccountMapping,
    JournalEntry,
    JournalEntryLine,
    Product,
    Warehouse,
    StockBalance,
    StockMovement,
    Supplier,
    Customer,
    PurchaseOrder,
    PurchaseOrderLine,
    SalesOrder,
    SalesOrderLine,
]
CUSTOM_PERMISSIONS = {
    "Administrador": [
        "Applet.access_admin_module",
        "Applet.access_security_module",
        "Applet.run_backups",
        "Accounting.access_accounting_module",
        "Accounting.manage_accounting_config",
        "Accounting.generate_journal_entries",
        "Accounting.view_accounting_reports",
        "Inventory.access_inventory_module",
        "Inventory.manage_inventory_config",
        "Inventory.manage_inventory_stock",
        "Inventory.view_inventory_reports",
        "Commerce.access_commerce_module",
        "Commerce.manage_commerce_partners",
        "Commerce.manage_purchases",
        "Commerce.manage_sales",
        "Commerce.view_commerce_reports",
        "DATA_scope.access_payroll_module",
        "DATA_scope.manage_employee_status",
        "DATA_scope.upload_payroll_data",
        "DATA_scope.import_payroll_data",
        "DATA_scope.clear_payroll_data",
        "DATA_scope.download_upload_output",
        "Attendance.access_attendance_module",
        "Attendance.manage_attendance_records",
        "Attendance.view_attendance_reports",
        "Attendance.export_attendance_reports",
    ],
    "RRHH": [
        "DATA_scope.access_payroll_module",
        "DATA_scope.manage_employee_status",
        "DATA_scope.upload_payroll_data",
        "DATA_scope.import_payroll_data",
        "DATA_scope.download_upload_output",
        "Attendance.access_attendance_module",
        "Attendance.manage_attendance_records",
        "Attendance.view_attendance_reports",
        "Attendance.export_attendance_reports",
    ],
    "Contabilidad": [
        "DATA_scope.access_payroll_module",
        "DATA_scope.download_upload_output",
        "Accounting.access_accounting_module",
        "Accounting.manage_accounting_config",
        "Accounting.generate_journal_entries",
        "Accounting.view_accounting_reports",
        "Inventory.access_inventory_module",
        "Inventory.view_inventory_reports",
        "Commerce.access_commerce_module",
        "Commerce.manage_commerce_partners",
        "Commerce.manage_purchases",
        "Commerce.manage_sales",
        "Commerce.view_commerce_reports",
        "Attendance.access_attendance_module",
        "Attendance.view_attendance_reports",
        "Attendance.export_attendance_reports",
    ],
    "Solo lectura": [
        "DATA_scope.access_payroll_module",
        "Attendance.access_attendance_module",
        "Attendance.view_attendance_reports",
        "Accounting.access_accounting_module",
        "Accounting.view_accounting_reports",
        "Inventory.access_inventory_module",
        "Inventory.view_inventory_reports",
        "Commerce.access_commerce_module",
        "Commerce.view_commerce_reports",
    ],
}


def ensure_role_groups():
    groups = []
    for name in ROLE_NAMES:
        group, _ = Group.objects.get_or_create(name=name)
        permissions = list(role_permissions(name))
        if permissions:
            group.permissions.set(permissions)
        groups.append(group)
    return groups


def role_permissions(role_name: str):
    permissions = []
    actions = ["view", "add", "change", "delete"] if role_name == "Administrador" else ["view"]
    if role_name == "RRHH":
        actions = ["view", "add", "change"]

    for model in STANDARD_DATA_MODELS:
        content_type = ContentType.objects.get_for_model(model)
        for action in actions:
            permission = Permission.objects.filter(
                content_type=content_type,
                codename=f"{action}_{model._meta.model_name}",
            ).first()
            if permission:
                permissions.append(permission)

    for dotted in CUSTOM_PERMISSIONS.get(role_name, []):
        app_label, codename = dotted.split(".", 1)
        permission = Permission.objects.filter(content_type__app_label=app_label, codename=codename).first()
        if permission:
            permissions.append(permission)
    return permissions


def latest_backup_file():
    backup_dir = settings.PROJECT_ROOT / "backups"
    if not backup_dir.exists():
        return None

    files = sorted(
        [
            path
            for pattern in ("postgres_*.dump", "*.sqlite3")
            for path in backup_dir.glob(pattern)
            if path.is_file()
        ],
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    if not files:
        return None

    path = files[0]
    stat = path.stat()
    return {
        "name": path.name,
        "path": str(path),
        "size_mb": round(stat.st_size / (1024 * 1024), 2),
        "modified_at": stat.st_mtime,
        "engine": "PostgreSQL" if path.suffix == ".dump" else "SQLite",
    }


def auto_backup_interval_minutes():
    return int(getattr(settings, "AUTO_BACKUP_INTERVAL_MINUTES", 90))


def auto_backup_enabled():
    return bool(getattr(settings, "AUTO_BACKUP_ENABLED", True))


def backup_is_due():
    if not auto_backup_enabled():
        return False
    latest_backup = latest_backup_file()
    if latest_backup is None:
        return True
    age_seconds = time.time() - latest_backup["modified_at"]
    return age_seconds >= auto_backup_interval_minutes() * 60


def run_backup(request=None, action: str = "backup_created"):
    output = io.StringIO()
    call_command("backup_database", stdout=output)
    message = output.getvalue().strip()
    log_event(request, action, "Applet", message)
    return message


def run_auto_backup_if_due(request=None):
    if not backup_is_due():
        return False
    if not _backup_lock.acquire(blocking=False):
        return False
    try:
        if not backup_is_due():
            return False
        run_backup(request=request, action="auto_backup_created")
        return True
    except Exception as exc:
        log_event(request, "auto_backup_error", "Applet", str(exc))
        return False
    finally:
        _backup_lock.release()


def database_status():
    try:
        with connection.cursor() as cursor:
            cursor.execute("select 1")
            cursor.fetchone()
    except Exception:
        return "Error"
    return "Conectada"


def system_status_items():
    latest_import = ImportRun.objects.order_by("-created_at").first()
    latest_backup = latest_backup_file()
    return [
        ("Estado Django", "Operativo"),
        ("Base de datos", database_status()),
        ("Modulo DATA_scope", "Activo"),
        ("Modulo Attendance", "Activo"),
        ("Modulo Applet", "Activo"),
        ("Modulo Inventory", "Activo"),
        ("Modulo Commerce", "Activo"),
        ("Ultima carga", latest_import.created_at.strftime("%Y-%m-%d %H:%M") if latest_import else "Sin cargas registradas"),
        ("Ultimo backup", latest_backup["name"] if latest_backup else "Sin backups registrados"),
        ("Backup automatico", f"Activo cada {auto_backup_interval_minutes()} minutos" if auto_backup_enabled() else "Desactivado"),
        ("Version Celestial ERP", ERP_VERSION),
    ]
