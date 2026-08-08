# v0.6 con recursos limitados y proyeccion IA local

Fecha de referencia: 2026-07-10

## Objetivo

Avanzar la base operativa robusta de Celestial ERP sin depender todavia de PostgreSQL ni de permisos de instalacion en este equipo.

La estrategia es preparar el proyecto para moverse despues a un servidor LAN, manteniendo el equipo actual como ambiente de desarrollo/operacion limitada. La IA local queda documentada como proyeccion posterior, no como requisito de v0.6.

## Avances aplicados

### Settings separados

La configuracion Django quedo separada en:

```text
Celestial_ERP/Celestial_ERP/settings/
```

Archivos:

- `base.py`: configuracion comun.
- `dev.py`: configuracion local de desarrollo.
- `prod.py`: configuracion para operacion compartida/servidor.
- `__init__.py`: selecciona entorno por `ERP_SETTINGS_ENV`.

Variable de entorno:

```powershell
ERP_SETTINGS_ENV=dev
ERP_SETTINGS_ENV=prod
```

Por compatibilidad, `DJANGO_SETTINGS_MODULE=Celestial_ERP.settings` sigue funcionando.

### Logs persistentes

Se agregaron logs rotativos en:

```text
logs/celestial_erp.log
logs/etl.log
```

Variables:

```powershell
DJANGO_LOG_LEVEL=INFO
ERP_LOG_LEVEL=INFO
ERP_LOG_MAX_BYTES=5242880
ERP_LOG_BACKUP_COUNT=5
```

### SQLite endurecido temporalmente

Mientras PostgreSQL no este disponible, SQLite queda configurado con:

- Timeout configurable.
- WAL.
- `synchronous=NORMAL`.
- `temp_store=MEMORY`.
- Foreign keys activas.

Variable:

```powershell
SQLITE_TIMEOUT_SECONDS=20
```

Esto no reemplaza PostgreSQL para multiusuario real, pero reduce friccion en operacion local/controlada.

### Seguridad operativa basica

Se agrego el comando:

```powershell
python manage.py check_operational_security
```

Revisa:

- Entorno activo.
- `DEBUG`.
- `DJANGO_SECRET_KEY`.
- `ALLOWED_HOSTS`.
- Cookies seguras fuera de debug.
- Usuarios activos.
- Claves temporales conocidas.
- Usuarios staff sin grupo/rol.

Para usarlo como check estricto:

```powershell
python manage.py check_operational_security --fail-on-warning
```

### Bootstrap local/offline

Bootstrap 5.3.3 quedo copiado en:

```text
Celestial_ERP/Applet/static/vendor/bootstrap/
```

Las plantillas principales ya cargan Bootstrap desde `{% static %}` y no desde CDN.

### Backups con verificacion y retencion simple

`backup_sqlite` usa la API `backup` de SQLite y ejecuta `pragma integrity_check` por defecto.

Opciones:

```powershell
python manage.py backup_sqlite --retention-days 30 --keep-last 5
python manage.py backup_sqlite --no-verify
```

### Cargas largas en segundo plano

La carga web puede ejecutar ETL en segundo plano. Cada corrida crea:

```text
uploads/<run_id>/job_config.json
uploads/<run_id>/job_status.json
uploads/<run_id>/stdout.log
uploads/<run_id>/stderr.log
```

El comando interno usado por la vista es:

```powershell
python manage.py run_upload_job uploads\<run_id>\job_config.json
```

La pantalla `/cargas/` muestra un enlace de estado para revisar si la corrida esta en cola, ejecutandose, finalizada o fallida.

### Exportaciones adicionales

Se agregaron CSV operativos para:

- Trabajador.
- Periodo.
- Liquidacion.

Estas exportaciones requieren permiso `DATA_scope.download_upload_output`.

## Pendientes por permisos o infraestructura

- PostgreSQL, movido hacia final de v1.0.x.
- Servicio permanente del ERP.
- Reverse proxy/HTTPS.
- Cola real de trabajos para cargas largas.
- Servidor LAN estable.

## Servidor LAN propuesto para etapa posterior

Hardware disponible estimado:

- Dual Xeon Harpertown X5490.
- 32 GB RAM DDR2.
- 3 GPU de 12 GB VRAM cada una.
- 4 TB SSD en SATA 2.
- Fuente 1100 W.

Uso recomendado futuro:

- Servidor LAN para Celestial ERP.
- PostgreSQL cuando se puedan instalar servicios.
- API de IA local cuando la base ERP ya este estabilizada.
- Backups locales y copia externa.

Limitaciones:

- CPU antigua, usar como host y no como motor principal de inferencia.
- Alto consumo electrico/calor.
- SATA 2 limita carga inicial desde disco, no necesariamente inferencia una vez cargado el modelo.
- Priorizar inferencia por GPU.

## IA local recomendada para v1.0.x

Con 3 GPU de 12 GB:

- 8B cuantizado: muy comodo.
- 12B/14B cuantizado: recomendado para primera integracion.
- 30B/32B cuantizado: viable con reparto multi-GPU.
- 70B: posible solo con compromisos fuertes, no recomendado como primera meta.

Stack inicial recomendado cuando corresponda:

1. Linux en servidor.
2. Drivers NVIDIA.
3. `llama.cpp server` u Ollama.
4. API local en LAN.
5. Integracion posterior desde Celestial ERP, ya fuera del alcance de v0.6.

Casos de uso para el ERP:

- Resumen de liquidaciones.
- Explicacion de diferencias por periodo.
- Deteccion asistida de anomalias ETL.
- Ayuda para clasificar items.
- Consultas sobre documentacion interna.
- Reportes narrativos para RRHH/contabilidad.

## Orden recomendado de v0.6

1. Cerrar settings dev/prod.
2. Cerrar credenciales nominales y variables sensibles.
3. Pasar Bootstrap a local/offline.
4. Fortalecer logs y backups.
5. Preparar despliegue LAN.
6. Preparar PostgreSQL en v1.0.x final cuando exista servidor/permisos.
7. Dejar la IA local como proyeccion v1.0.x, sin bloquear la base operativa.
