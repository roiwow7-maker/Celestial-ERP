# Documentacion operativa cerrada

Fecha de referencia: 2026-07-13

Hito cerrado desde `v1.0.2`.

## Documentos Base

- `ROADMAP.md`
- `version_log.md`
- `docs/00_DOCUMENTACION_GENERAL.md`
- `docs/06_OPERACION_LOCAL_BACKUPS.md`
- `docs/15_OPERACION_SQLITE_SIN_POSTGRESQL.md`
- `docs/16_TESTING_AMPLIO.md`
- `docs/18_DEPLOY_LAN.md`

## Rutina Operativa

1. Iniciar servidor solo en red confiable.
2. Verificar salud con `check`, `check_operational_security` y `check_sqlite_operational_health`.
3. Ejecutar backup antes de cargas o sincronizaciones.
4. Usar usuarios nominales y permisos por rol.
5. Registrar cambios manuales mediante vistas del ERP, no editando la base directamente.
6. Validar suite de pruebas antes de cerrar version.

## Comandos Criticos

```powershell
python manage.py setup_access_control
python manage.py check_operational_security
python manage.py check_sqlite_operational_health
python manage.py backup_sqlite
python manage.py cleanup_uploads --dry-run
python manage.py sync_attendance_payroll 202607 --dry-run
```

PostgreSQL queda fuera de la operacion inmediata y al final del roadmap.
