# Testing amplio

Fecha de referencia: 2026-07-13

Hito cerrado desde `v1.0.1`.

## Objetivo

Mantener una suite minima pero amplia para validar que los modulos base siguen funcionando mientras el sistema opera con SQLite.

## Comando Principal

```powershell
python manage.py test Applet DATA_scope ERP_api Accounting Inventory Commerce Attendance
```

Cobertura actual:

- portal, roles y permisos
- remuneraciones y validaciones base
- backups SQLite
- diagnostico operativo SQLite
- contabilidad
- inventario
- compras y ventas
- asistencia
- auditoria granular
- sincronizacion asistencia-remuneraciones

## Criterio de Cierre

Antes de cerrar una version:

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test Applet DATA_scope ERP_api Accounting Inventory Commerce Attendance
python manage.py check_sqlite_operational_health
```

Si alguno falla, no se considera version cerrada.
