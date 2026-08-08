# Applet - Portal y orquestador

Fecha de referencia: 2026-07-20

## Estado del modulo

Estado actual: **base operativa v1.0.8**.

Applet actua como portal/orquestador del ERP. Centraliza navegacion, login, roles, auditoria, backups, estado del sistema, Kanban general y accesos a modulos existentes.

No contiene la logica profunda de remuneraciones. Esa logica vive en DATA_scope.

## Rutas

| Ruta | Vista | Descripcion |
| --- | --- | --- |
| `/applet/` | `home` | Inicio general del ERP |
| `/applet/modules/` | `modules` | Launcher de modulos |
| `/applet/kanban/` | `kanban` | Tablero general ERP |
| `/applet/admin-panel/` | `admin_panel` | Panel administrativo general |
| `/applet/security/` | `security` | Usuarios, roles y permisos |
| `/applet/audit/` | `audit` | Eventos del sistema |
| `/applet/backups/` | `backups` | Estado y ejecucion manual de backups |
| `/applet/system-status/` | `system_status` | Estado operativo del sistema |

## Checklist funcional

- [x] Home general del ERP.
- [x] Launcher de modulos.
- [x] Kanban general actualizado.
- [x] Panel administrativo general.
- [x] Login obligatorio.
- [x] Roles funcionales.
- [x] Permisos por modulo.
- [x] Restricciones de vistas administrativas.
- [x] Auditoria con `AuditLog`.
- [x] Vista de backups protegida por permiso.
- [x] Backup automatico cada 90 minutos.
- [x] Estado del sistema.
- [x] Navbar superior compartida.
- [x] Integracion con DATA_scope.
- [x] Integracion con Django Admin.
- [x] Integracion con ERP_api.

## Componentes importantes

| Archivo | Funcion |
| --- | --- |
| `Applet/views.py` | Vistas HTML basadas en funciones |
| `Applet/access.py` | Decoradores de login/permisos |
| `Applet/services.py` | Roles, permisos, backups y estado del sistema |
| `Applet/audit.py` | Registro seguro de eventos |
| `Applet/middleware.py` | Backup automatico cada 90 minutos |
| `Applet/models.py` | Modelo `AuditLog` y permisos custom |
| `Applet/templates/shared/topbar.html` | Navbar superior compartida |

## Navegacion

La interfaz usa una navbar superior con secciones desplegables:

- General.
- Remuneraciones.
- Inventario.
- Control.
- Herramientas.

La navbar se adapta a permisos. Un usuario sin permiso de remuneraciones no ve accesos operativos de DATA_scope; un usuario sin permiso administrativo no ve seguridad/backups.

## Seguridad

Roles funcionales:

- Administrador.
- RRHH.
- Contabilidad.
- Solo lectura.

Permisos de Applet:

- `access_admin_module`.
- `access_security_module`.
- `run_backups`.

El comando `setup_access_control` crea/actualiza los grupos y asigna permisos.

## Auditoria

Modelo: `AuditLog`.

Campos:

- `user`
- `action`
- `module`
- `description`
- `created_at`

Eventos actuales:

- Acceso a dashboard.
- Visualizacion de reportes.
- Exportacion CSV.
- Inicio/exito/error de cargas ETL.
- Cambio de estado de trabajador.
- Backups manuales y automaticos.

## Backups

El backup manual se ejecuta desde:

```text
/applet/backups/
```

El backup automatico se revisa por middleware y se ejecuta si el ultimo respaldo tiene mas de 90 minutos.

Variables:

```text
ERP_AUTO_BACKUP_ENABLED=true
ERP_AUTO_BACKUP_INTERVAL_MINUTES=90
```

## Pendientes

- Filtros avanzados en auditoria.
- Rotacion de claves y politica de usuarios.
