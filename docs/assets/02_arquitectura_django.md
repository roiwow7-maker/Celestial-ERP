# Arquitectura Django

Fecha de referencia: 2026-07-13

Version documentada: `1.2.1`

> Django sigue siendo la autoridad de negocio, pero desde `1.2.0` se complementa con Next.js/Electron y la API v1. Consultar `../25_ESTADO_ACTUAL_1_2_1.md`.

## Proyecto

El proyecto Django vive en:

```text
Celestial_ERP/
```

Entrada principal:

```text
Celestial_ERP/manage.py
```

Modulo de proyecto:

```text
Celestial_ERP/Celestial_ERP/
```

## Apps instaladas

| App | Proposito |
| --- | --- |
| `Applet` | Portal principal, UI base, roles, auditoria, backups, estado del sistema y admin custom. |
| `DATA_scope` | Remuneraciones, trabajadores, periodos, items, movimientos, liquidaciones, reportes y cargas ETL. |
| `Accounting` | Plan de cuentas, centros de costo, mapeos, asientos y reportes contables. |
| `Inventory` | Productos, bodegas, stock, movimientos y valorizacion. |
| `Commerce` | Proveedores, clientes, compras, ventas y reportes comerciales. |
| `Attendance` | Asistencia historica diaria, mensual y por trabajador. |
| `ERP_api` | API v1 para sesion, recursos CRUD, reportes, ETL y usuarios. |

## Settings

La configuracion fue separada en paquete:

```text
Celestial_ERP/Celestial_ERP/settings/
```

| Archivo | Uso |
| --- | --- |
| `__init__.py` | Selecciona settings segun `ERP_SETTINGS_ENV`. |
| `base.py` | Configuracion comun: apps, middleware, DB, static, logging, backups. |
| `dev.py` | Desarrollo local. |
| `prod.py` | Produccion/red interna controlada. |

Variable de seleccion:

```text
ERP_SETTINGS_ENV=dev
ERP_SETTINGS_ENV=prod
```

## Base de datos

Base actual:

```text
Celestial_ERP/db.sqlite3
```

Motor:

```text
django.db.backends.sqlite3
```

Opciones SQLite relevantes:

- `timeout` configurable por `SQLITE_TIMEOUT_SECONDS`.
- `journal_mode=WAL`.
- `synchronous=NORMAL`.
- `foreign_keys=ON`.

## Middleware

Middleware propio:

```text
Applet.middleware.AutoBackupMiddleware
```

Uso:

- Revisa si corresponde backup automatico.
- Ejecuta backup si el ultimo respaldo supera el intervalo configurado.
- Intervalo por defecto: 90 minutos.

## Templates

| Ruta | Uso |
| --- | --- |
| `Applet/templates/Applet/base.html` | Layout base Bootstrap. |
| `Applet/templates/shared/topbar.html` | Navbar flotante compartida. |
| `Applet/templates/registration/login.html` | Login custom. |
| `Applet/templates/admin/base_site.html` | Tema Django Admin custom. |
| `Applet/templates/admin/index.html` | Portada del Django Admin. |
| `DATA_scope/templates/DATA_scope/` | Pantallas de remuneraciones, reportes, cargas y formularios. |
| `Inventory/templates/Inventory/` | Pantallas de inventario. |
| `Commerce/templates/Commerce/` | Pantallas de compras y ventas. |
| `Attendance/templates/Attendance/` | Pantallas de asistencia. |

## Static

| Ruta | Uso |
| --- | --- |
| `Applet/static/Applet/css/app.css` | Tema general Celestial ERP. |
| `Applet/static/Applet/css/admin.css` | Tema Django Admin. |
| `Applet/static/Applet/js/app.js` | Interacciones UI y cambio de tema. |
| `Applet/static/vendor/bootstrap/` | Bootstrap 5.3.3 local/offline. |

## Logging

Carpeta:

```text
logs/
```

Archivos esperados:

- `celestial_erp.log`
- `etl.log`

Los handlers son rotativos y se configuran desde `settings/base.py`.

