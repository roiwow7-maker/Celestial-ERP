# Seguridad, roles y permisos

Fecha de referencia: 2026-07-13

Version documentada: `1.0.8`

## Acceso

El sistema exige login para:

- portal
- remuneraciones
- reportes
- cargas
- herramientas administrativas
- API interna

Rutas de autenticacion:

```text
/login/
/logout/
```

## Roles funcionales

| Rol | Alcance |
| --- | --- |
| Administrador | Operacion total, seguridad, backups, admin y datos. |
| RRHH | Remuneraciones, trabajadores, cargas, importacion y estados. |
| Contabilidad | Lectura y descargas autorizadas. |
| Solo lectura | Consulta sin acciones sensibles. |

Los roles se crean/actualizan con:

```powershell
python manage.py setup_access_control
```

## Permisos Applet

| Permiso | Uso |
| --- | --- |
| `Applet.access_admin_module` | Acceso a modulo administrativo. |
| `Applet.access_security_module` | Acceso a seguridad y auditoria. |
| `Applet.run_backups` | Ejecutar backups manuales. |

## Permisos DATA_scope

| Permiso | Uso |
| --- | --- |
| `DATA_scope.access_payroll_module` | Acceso a remuneraciones. |
| `DATA_scope.manage_employee_status` | Cambiar estado de trabajador. |
| `DATA_scope.upload_payroll_data` | Subir archivos de remuneraciones. |
| `DATA_scope.import_payroll_data` | Importar datos al ERP. |
| `DATA_scope.clear_payroll_data` | Limpiar datos antes de importar. |
| `DATA_scope.download_upload_output` | Descargar salidas ETL y exportaciones. |

## Permisos Accounting

| Permiso | Uso |
| --- | --- |
| `Accounting.access_accounting_module` | Acceso al modulo contable. |
| `Accounting.manage_accounting_config` | Administrar plan de cuentas, centros y mapeos. |
| `Accounting.generate_journal_entries` | Generar asientos contables. |
| `Accounting.view_accounting_reports` | Ver reportes contables. |

## Permisos Inventory

| Permiso | Uso |
| --- | --- |
| `Inventory.access_inventory_module` | Acceso al modulo de inventario. |
| `Inventory.manage_inventory_config` | Administrar productos y bodegas. |
| `Inventory.manage_inventory_stock` | Registrar movimientos de inventario. |
| `Inventory.view_inventory_reports` | Ver stock y valorizacion. |

## Permisos Commerce

| Permiso | Uso |
| --- | --- |
| `Commerce.access_commerce_module` | Acceso al modulo comercial. |
| `Commerce.manage_commerce_partners` | Administrar proveedores y clientes. |
| `Commerce.manage_purchases` | Administrar compras. |
| `Commerce.manage_sales` | Administrar ventas. |
| `Commerce.view_commerce_reports` | Ver reportes comerciales. |

## Permisos Attendance

| Permiso | Uso |
| --- | --- |
| `Attendance.access_attendance_module` | Acceso al modulo de asistencia. |
| `Attendance.manage_attendance_records` | Crear y editar registros de asistencia. |
| `Attendance.view_attendance_reports` | Ver reportes mensuales e historicos. |
| `Attendance.export_attendance_reports` | Exportar CSV e imprimir reportes autorizados. |

## Decoradores

Archivo:

```text
Celestial_ERP/Applet/access.py
```

Funciones:

- `module_permission_required(permission)`
- `all_permissions_required(*permissions)`

## Auditoria

Eventos auditados:

- ingreso a modulos clave
- cargas ETL
- importaciones
- errores de carga
- cambios manuales
- cambios de estado de trabajador
- backups
- descargas/exportaciones relevantes

Archivos:

```text
Celestial_ERP/Applet/audit.py
Celestial_ERP/DATA_scope/audit.py
```

Modelo:

```text
Applet.AuditLog
```

## Comando de seguridad

```powershell
python manage.py check_operational_security
```

Con modo estricto:

```powershell
python manage.py check_operational_security --fail-on-warning
```

## Credenciales

El usuario `root/root` fue valido solo como desarrollo local historico. Para uso compartido:

- crear usuarios nominales
- asignar grupos reales
- cambiar claves temporales
- no compartir superusuario
- configurar `DJANGO_SECRET_KEY`
- revisar `ALLOWED_HOSTS`

## Riesgos actuales

- SQLite no es ideal para muchos usuarios escribiendo al mismo tiempo.
- `uploads/`, `backups/` y CSV pueden contener datos personales.
- Operacion en red interna requiere claves reales y hosts definidos.
- PostgreSQL queda planificado para final de v1.0.x.

