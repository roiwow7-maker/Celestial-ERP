# Operacion y comandos

Fecha de referencia: 2026-07-13

Version documentada: `1.0.8`

## Arranque local

Desde la raiz:

```powershell
.\start_erp_web.ps1
```

O manual:

```powershell
cd Celestial_ERP
python manage.py runserver
```

## Checks principales

```powershell
cd Celestial_ERP
python manage.py check
python manage.py test Applet DATA_scope ERP_api Accounting Inventory Commerce Attendance
```

Estado validado en esta version:

- `manage.py check`: OK.
- `41 tests`: OK.

## Contabilidad

```powershell
python manage.py seed_accounting_catalog
python manage.py generate_payroll_journal_entries 202606
```

## Roles y usuarios

```powershell
python manage.py setup_access_control
```

Uso:

- Crea/actualiza grupos base.
- Asigna permisos por rol.
- Puede asociar un usuario admin existente al grupo Administrador.

Opciones:

```powershell
python manage.py setup_access_control --admin-user admin --admin-password "clave-segura"
```

## Seguridad operativa

```powershell
python manage.py check_operational_security
python manage.py check_operational_security --fail-on-warning
```

Revisa:

- entorno activo
- `DEBUG`
- `SECRET_KEY`
- `ALLOWED_HOSTS`
- cookies seguras fuera de DEBUG
- usuarios activos
- claves temporales conocidas
- staff sin grupo nominal

## Salud operativa SQLite

```powershell
python manage.py check_sqlite_operational_health
python manage.py check_sqlite_operational_health --fail-on-warning
```

Revisa:

- motor SQLite activo
- archivo `db.sqlite3`, tamano e integridad
- `journal_mode`, `foreign_keys`
- ultimo backup
- volumen de `uploads`
- conteos base de datos operativos

## Backups SQLite

```powershell
python manage.py backup_sqlite
```

Opciones:

```powershell
python manage.py backup_sqlite --output-dir ..\backups
python manage.py backup_sqlite --retention-days 30 --keep-last 5
python manage.py backup_sqlite --no-verify
python manage.py validate_backup_restore
python manage.py validate_backup_restore --backup-path backups\db_AAAAMMDD_HHMMSS.sqlite3
```

Caracteristicas:

- Usa API `sqlite3.backup`.
- Verifica con `pragma integrity_check`.
- Puede aplicar retencion simple.
- Desde `v1.0.4`, `validate_backup_restore` valida una restauracion en copia temporal sin tocar la base activa.

## Limpieza de uploads

```powershell
python manage.py cleanup_uploads --dry-run
python manage.py cleanup_uploads --days 30
```

Uso:

- Reduce exposicion de datos sensibles.
- Elimina carpetas antiguas de `uploads/`.

## Validacion de reglas de negocio

```powershell
python manage.py validate_business_rules
python manage.py validate_business_rules --fail-on-mismatch
```

Salida default:

```text
reports/business_rules_validation.csv
```

Compara:

- totales de liquidacion
- movimientos agrupados por categoria
- sueldo liquido por codigo fuente `A000`

## Sincronizacion asistencia-remuneraciones

```powershell
python manage.py sync_attendance_payroll 202607 --dry-run
python manage.py sync_attendance_payroll 202607
```

Uso:

- toma asistencia del mes del periodo
- actualiza dias trabajados
- actualiza dias de ausencia
- actualiza dias de permiso
- calcula horas no trabajadas por ausencia
- no modifica montos de remuneracion

## Job background de carga web

```powershell
python manage.py run_upload_job uploads\<run_id>\job_config.json
```

Normalmente lo invoca la vista `/cargas/`; no es necesario ejecutarlo a mano salvo diagnostico.

Genera:

- `job_status.json`
- `stdout.log`
- `stderr.log`
- `reporte_calidad_carga.csv`
- descargas detectadas

## Logs

Carpeta:

```text
logs/
```

Archivos:

- `celestial_erp.log`
- `etl.log`

Variables:

```text
ERP_LOG_LEVEL
DJANGO_LOG_LEVEL
ERP_LOG_MAX_BYTES
ERP_LOG_BACKUP_COUNT
```

## Variables importantes

| Variable | Uso |
| --- | --- |
| `ERP_SETTINGS_ENV` | `dev` o `prod`. |
| `DJANGO_SECRET_KEY` | Clave secreta real. |
| `DJANGO_DEBUG` | Debug del entorno. |
| `DJANGO_ALLOWED_HOSTS` | Hosts permitidos. |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Origenes CSRF confiables. |
| `DJANGO_SERVE_STATIC_LOCALLY` | Sirve static desde Django en LAN/local. |
| `ERP_AUTO_BACKUP_ENABLED` | Activa backup automatico. |
| `ERP_AUTO_BACKUP_INTERVAL_MINUTES` | Intervalo de backup automatico. |

