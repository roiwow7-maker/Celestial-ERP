# Deploy local/red interna

Fecha de referencia: 2026-07-13

Hito cerrado desde `v1.0.3`.

> Actualizacion `1.2.1`: para uso movil se publica Next.js en `0.0.0.0:3000`; Django permanece en `127.0.0.1:8000` y se consume por proxy. Para produccion usar `deploy/celestial-frontend.service` y `deploy/nginx-celestial-erp.conf`, no `runserver` expuesto.

## Alcance

Este deploy es para red interna controlada, no internet publico. PostgreSQL es la base principal y solo el frontend debe quedar accesible desde clientes LAN.

## Variables Minimas

```powershell
$env:ERP_SETTINGS_ENV="prod"
$env:DJANGO_DEBUG="false"
$env:DJANGO_ALLOWED_HOSTS="127.0.0.1,localhost,IP_DEL_EQUIPO"
$env:DJANGO_SERVE_STATIC_LOCALLY="true"
$env:ERP_AUTO_BACKUP_ENABLED="true"
$env:ERP_AUTO_BACKUP_INTERVAL_MINUTES="90"
```

Definir tambien `DJANGO_SECRET_KEY` con una clave propia antes de uso compartido.

## Arranque LAN Controlado

Desde `Celestial_ERP/`:

```powershell
python manage.py check
python manage.py check_operational_security
python manage.py check_sqlite_operational_health
python manage.py runserver 0.0.0.0:8000
```

Acceso desde otro equipo:

```text
http://IP_DEL_EQUIPO:8000/
```

## Reglas

- No exponer a internet.
- No operar con `root/root`.
- No permitir cargas simultaneas pesadas.
- Ejecutar backup antes de cargas ETL o sincronizaciones.
- Mantener firewall limitado a red interna.
- Migrar a servidor formal antes de uso concurrente serio.
