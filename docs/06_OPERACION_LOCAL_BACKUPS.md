# Operacion local y backups

Fecha de referencia: 2026-08-16

> Vigencia: la politica SQLite de este documento se conserva como procedimiento historico y de reversa. Desde `1.0.10` la base principal es PostgreSQL; para operacion vigente consultar `22_OPERACION_POSTGRESQL_PRODUCCION.md`.

## Criterio

Celestial ERP se opera en ambiente local o red interna controlada. PostgreSQL es la base actual y sus respaldos se generan con `pg_dump`, se verifican con `pg_restore --list` y cuentan con retencion/automatizacion preparada. SQLite solo aplica al respaldo historico conservado.

## Politica formal de retencion

Carpeta oficial:

```text
backups/
```

Retencion recomendada para operacion local:

| Tipo | Frecuencia | Retencion |
| --- | --- | --- |
| Automatico | Cada 90 minutos mientras el sistema recibe trafico | 48 horas |
| Diario | Ultimo backup valido del dia | 30 dias |
| Semanal | Ultimo backup valido de la semana | 12 semanas |
| Mensual | Ultimo backup valido del mes | 12 meses |

La depuracion puede hacerse manualmente hasta implementar un comando especifico de rotacion por tiers. Antes de borrar respaldos se debe conservar al menos:

- Un backup del dia actual.
- Un backup del dia anterior.
- Un backup semanal reciente.
- Un backup mensual reciente.

## Backup automatico

El sistema ejecuta backup automatico si esta habilitado y el ultimo respaldo tiene mas antiguedad que el intervalo configurado.

El comando usa la API `backup` de SQLite, por lo que es mas consistente que copiar el archivo directamente cuando existe WAL activo.

Variables:

```text
ERP_AUTO_BACKUP_ENABLED=true
ERP_AUTO_BACKUP_INTERVAL_MINUTES=90
```

El backup automatico reutiliza:

```powershell
python manage.py backup_sqlite
```

Opciones utiles:

```powershell
python manage.py backup_sqlite --retention-days 30 --keep-last 5
python manage.py backup_sqlite --no-verify
python manage.py validate_backup_restore
```

## Backup manual

Ruta:

```text
/applet/backups/
```

Permite:

- Ver ultimo backup.
- Ver carpeta destino.
- Ejecutar backup manual.
- Registrar evento en auditoria.

Comando:

```powershell
python manage.py backup_sqlite
```

Salida esperada:

```text
backups/db_AAAAMMDD_HHMMSS.sqlite3
```

## Prueba de respaldo recuperable

Por defecto, `backup_sqlite` valida que la copia responda:

```sql
pragma integrity_check;
```

Desde `v1.0.4`, la restauracion tambien puede validarse sin tocar la base activa:

```powershell
python manage.py validate_backup_restore
python manage.py validate_backup_restore --backup-path backups\db_AAAAMMDD_HHMMSS.sqlite3
python manage.py validate_backup_restore --keep-restored-copy
```

Este comando copia el backup a una ubicacion temporal, ejecuta `integrity_check`, verifica tablas criticas y reporta conteos base.

Resultado esperado:

```text
ok
```

Comando de prueba:

```powershell
python manage.py test DATA_scope
```

## Procedimiento de restauracion SQLite

Usar solo con el servidor detenido.

1. Detener Django/runserver.
2. Crear una copia de seguridad del estado actual:

```powershell
python manage.py backup_sqlite --output-dir backups\pre_restore
```

3. Elegir el backup validado desde `backups/`.
4. Reemplazar `Celestial_ERP/db.sqlite3` por el archivo elegido.
5. Ejecutar verificaciones:

```powershell
python manage.py check
python manage.py migrate --plan
python manage.py test Applet DATA_scope ERP_api Accounting Inventory Commerce
```

6. Levantar el servidor.
7. Entrar con usuario administrador.
8. Revisar `/applet/system-status/`, `/remuneraciones/` y `/reportes/`.
9. Registrar en auditoria/manual operativo la fecha, archivo restaurado y responsable.

## Copia externa

Para operacion real, al menos una copia diaria debe salir del equipo local hacia un medio controlado:

- Disco externo cifrado.
- Carpeta de red con permisos restringidos.
- Repositorio de backups interno, no git.

No subir respaldos de base de datos a repositorios de codigo.

## Responsabilidades

| Rol | Responsabilidad |
| --- | --- |
| Administrador | Ejecutar backups manuales, validar restauracion y custodiar copias externas. |
| RRHH | Avisar si una carga o correccion requiere punto de restauracion previo. |
| Contabilidad | Solicitar respaldo antes de cierres o exportaciones sensibles. |
| Solo lectura | Sin responsabilidad operativa de backup. |

## Pendientes posteriores

- Rotacion por tiers diario/semanal/mensual.
- Alerta visible si falla el backup automatico.
- Migracion a PostgreSQL para multiusuario real.
- Procedimiento equivalente para PostgreSQL cuando se migre.
