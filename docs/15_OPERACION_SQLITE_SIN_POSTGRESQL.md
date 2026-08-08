# Operacion SQLite sin PostgreSQL

Fecha de referencia: 2026-07-13

Modulo operativo documentado desde `v0.9.7`.

## Objetivo

Mientras no se pueda instalar PostgreSQL, Celestial ERP queda orientado a operacion local o red interna liviana con SQLite. Esto permite seguir avanzando sin bloquear desarrollo, siempre que se respeten limites de concurrencia, backups y limpieza de archivos sensibles.

## Diagnostico Operativo

Comando principal:

```powershell
python manage.py check_sqlite_operational_health
```

Modo estricto:

```powershell
python manage.py check_sqlite_operational_health --fail-on-warning
```

El diagnostico revisa:

- motor SQLite activo
- existencia y tamano de `db.sqlite3`
- `pragma integrity_check`
- `journal_mode`
- `foreign_keys`
- ultimo backup registrado
- cantidad de carpetas en `uploads/`
- conteos base de trabajadores, periodos, items, movimientos, liquidaciones, cargas y asistencia

## Reglas de Uso

- Evitar varios usuarios escribiendo al mismo tiempo.
- Ejecutar backups antes de cargas grandes o correcciones manuales masivas.
- Limpiar `uploads/` periodicamente.
- No exponer `runserver` a internet.
- Mantener usuarios nominales y no compartir superusuario.
- Usar PostgreSQL solo cuando exista servidor/permisos reales.

## Rutina Recomendada

Antes de operar:

```powershell
python manage.py check
python manage.py check_operational_security
python manage.py check_sqlite_operational_health
python manage.py backup_sqlite
```

Despues de cargas o cambios importantes:

```powershell
python manage.py validate_business_rules
python manage.py check_sqlite_operational_health
```

Antes de sincronizar asistencia:

```powershell
python manage.py backup_sqlite
python manage.py sync_attendance_payroll AAAAMM --dry-run
python manage.py sync_attendance_payroll AAAAMM
```

Limpieza:

```powershell
python manage.py cleanup_uploads --dry-run
python manage.py cleanup_uploads --days 30
```

## Decision sobre PostgreSQL

PostgreSQL ya no queda como siguiente paso inmediato. Se mueve al final de `v1.0.x`, despues de testing, documentacion operativa, despliegue LAN, backups reales, auditoria validada, plan de migracion e IA local como servicio separado.
