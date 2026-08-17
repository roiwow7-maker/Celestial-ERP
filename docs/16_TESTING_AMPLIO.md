# Testing amplio

Fecha de referencia: 2026-08-16

Hito cerrado desde `v1.0.1`.

## Objetivo

Mantener una suite amplia sobre PostgreSQL aislado y comprobaciones de frontend para impedir regresiones sin tocar datos productivos.

## Validacion vigente 1.2.1

```bash
./venv/bin/python tools/run_postgresql_tests.py
cd Celestial_ERP/frontend
npm run lint
npm run typecheck
npm run build
```

Resultado registrado: 51 pruebas Django correctas sobre un cluster PostgreSQL temporal, más ESLint, TypeScript y build Next.js correctos.

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
