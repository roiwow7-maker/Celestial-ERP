# Modulos, rutas y API

Fecha de referencia: 2026-07-13

Version documentada: `1.0.8`

## Rutas globales

| Ruta | Modulo | Uso |
| --- | --- | --- |
| `/login/` | Django auth | Inicio de sesion. |
| `/logout/` | Django auth | Cierre de sesion via POST. |
| `/` | Applet | Redireccion/entrada raiz. |
| `/applet/` | Applet | Portal principal. |
| `/api/` | ERP_api | Explorador visual de API interna. |
| `/inventario/` | Inventory | Inventario, stock y valorizacion. |
| `/comercio/` | Commerce | Compras, ventas, proveedores y clientes. |
| `/asistencia/` | Attendance | Asistencia historica diaria, mensual y por trabajador. |
| `/admin/` | Django Admin | Administracion interna. |
| `/static/` | Static local | Servido local cuando `DJANGO_SERVE_STATIC_LOCALLY=true`. |

## Applet

| Ruta | Vista | Uso |
| --- | --- | --- |
| `/applet/` | `home` | Inicio general del ERP. |
| `/applet/modules/` | `modules` | Launcher de modulos. |
| `/applet/kanban/` | `kanban` | Roadmap visual general. |
| `/applet/admin-panel/` | `admin_panel` | Panel administrativo general. |
| `/applet/security/` | `security` | Usuarios, roles y permisos. |
| `/applet/audit/` | `audit` | Eventos auditados. |
| `/applet/backups/` | `backups` | Backups manuales y estado. |
| `/applet/system-status/` | `system_status` | Estado operativo. |

## DATA_scope

| Ruta | Vista | Uso |
| --- | --- | --- |
| `/remuneraciones/` | `dashboard` | Dashboard payroll. |
| `/remuneraciones/trabajadores/` | `employees` | Lista y filtros de trabajadores. |
| `/remuneraciones/trabajadores/nuevo/` | `employee_create` | Crear trabajador. |
| `/remuneraciones/trabajadores/<id>/` | `employee_detail` | Ficha individual. |
| `/remuneraciones/trabajadores/<id>/editar/` | `employee_update` | Editar trabajador. |
| `/remuneraciones/periodos/` | `periods` | Periodos. |
| `/remuneraciones/periodos/nuevo/` | `period_create` | Crear periodo. |
| `/remuneraciones/periodos/<id>/editar/` | `period_update` | Editar periodo. |
| `/remuneraciones/items/` | `items` | Items de remuneracion. |
| `/remuneraciones/items/nuevo/` | `item_create` | Crear item. |
| `/remuneraciones/items/<id>/editar/` | `item_update` | Editar item. |
| `/remuneraciones/liquidaciones/` | `summaries` | Lista de liquidaciones. |
| `/remuneraciones/liquidaciones/nueva/` | `summary_create` | Crear liquidacion. |
| `/remuneraciones/liquidaciones/<id>/` | `summary_detail` | Detalle de liquidacion. |
| `/remuneraciones/liquidaciones/<id>/editar/` | `summary_update` | Editar liquidacion. |
| `/remuneraciones/movimientos/` | `entries` | Movimientos. |
| `/remuneraciones/movimientos/nuevo/` | `entry_create` | Crear movimiento. |
| `/remuneraciones/movimientos/<id>/editar/` | `entry_update` | Editar movimiento. |
| `/reportes/` | `reports` | Reportes y filtros. |
| `/reportes/exportar-csv/` | `export_reports_csv` | Export general de reportes. |
| `/remuneraciones/trabajadores/<id>/exportar-csv/` | `export_employee_csv` | Export por trabajador. |
| `/remuneraciones/periodos/<id>/exportar-csv/` | `export_period_csv` | Export por periodo. |
| `/remuneraciones/liquidaciones/<id>/exportar-csv/` | `export_summary_csv` | Export por liquidacion. |
| `/cargas/` | `upload_data` | Carga ETL web. |
| `/cargas/estado/<run_id>/` | `upload_status` | Estado de carga background. |
| `/cargas/probar-rutas/` | `route_probe` | Prueba de rutas ETL. |
| `/cargas/descargar/<run_id>/<path>/` | `download_upload_output` | Descarga salidas de carga. |
| `/kanban/` | `kanban` | Kanban operativo DATA_scope. |

## Accounting

| Ruta | Vista | Uso |
| --- | --- | --- |
| `/contabilidad/` | `dashboard` | Dashboard contable. |
| `/contabilidad/plan-cuentas/` | `chart_accounts` | Plan de cuentas. |
| `/contabilidad/centros-costo/` | `cost_centers` | Centros de costo. |
| `/contabilidad/mapeos/` | `mappings` | Mapeos item-cuenta. |
| `/contabilidad/asientos/` | `journal_entries` | Asientos contables. |
| `/contabilidad/asientos/generar-remuneraciones/` | `generate_payroll_journal` | Generacion de asiento de remuneraciones. |
| `/contabilidad/reportes/` | `reports` | Reportes contables iniciales. |

## Inventory

| Ruta | Vista | Uso |
| --- | --- | --- |
| `/inventario/` | `dashboard` | Dashboard de inventario. |
| `/inventario/productos/` | `products` | Productos/SKU. |
| `/inventario/productos/nuevo/` | `product_create` | Crear producto. |
| `/inventario/bodegas/` | `warehouses` | Bodegas. |
| `/inventario/stock/` | `stock` | Saldos actuales. |
| `/inventario/movimientos/` | `movements` | Movimientos de stock. |
| `/inventario/movimientos/nuevo/` | `movement_create` | Registrar entrada, salida o ajuste. |
| `/inventario/valorizacion/` | `valuation` | Valorizacion por costo promedio. |

## Commerce

| Ruta | Vista | Uso |
| --- | --- | --- |
| `/comercio/` | `dashboard` | Dashboard de compras y ventas. |
| `/comercio/proveedores/` | `suppliers` | Proveedores. |
| `/comercio/clientes/` | `customers` | Clientes. |
| `/comercio/compras/` | `purchase_orders` | Compras. |
| `/comercio/ventas/` | `sales_orders` | Ventas. |
| `/comercio/reportes/` | `reports` | Reportes comerciales. |

## Attendance

| Ruta | Vista | Uso |
| --- | --- | --- |
| `/asistencia/` | `dashboard` | Dashboard de asistencia del mes. |
| `/asistencia/registros/` | `records` | Registros diarios con filtros. |
| `/asistencia/registros/nuevo/` | `record_create` | Crear registro. |
| `/asistencia/registros/<id>/editar/` | `record_update` | Editar registro. |
| `/asistencia/trabajador/<id>/` | `employee_attendance` | Historico por trabajador. |
| `/asistencia/reporte-mensual/` | `monthly_report` | Reporte mensual. |
| `/asistencia/exportar-csv/` | `export_csv` | Exportacion CSV filtrable. |

## API interna

| Endpoint | Permiso | Uso |
| --- | --- | --- |
| `/api/` | Login | Explorador visual Bootstrap con endpoints en cascada, permisos y ejemplos. |
| `/api/?format=json` | Login | Indice JSON de endpoints y version. |
| `/api/health/` | Login | Salud basica del servicio. |
| `/api/system-status/` | Login | Estado Django, DB, backup, ultima carga y version. |
| `/api/modules/` | `DATA_scope.access_payroll_module` | Modulos activos y futuros. |
| `/api/payroll/summary/` | `DATA_scope.access_payroll_module` | Conteos payroll. |
| `/api/payroll/periods/` | `DATA_scope.access_payroll_module` | Ultimos periodos. |

El explorador de `/api/` usa acordeon Bootstrap para ver una API a la vez. Las respuestas restringidas no muestran datos sensibles si el usuario no tiene el permiso requerido.

## Exportaciones v0.6.8

Las exportaciones nuevas usan permiso:

```text
DATA_scope.download_upload_output
```

Salidas:

- CSV por trabajador.
- CSV por periodo.
- CSV por liquidacion.

Estas salidas deben tratarse como informacion sensible.

