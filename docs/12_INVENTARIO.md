# Inventario

El modulo `Inventory` queda activo como base v0.8 de Celestial ERP.

## Alcance Cerrado

- `v0.8.1`: productos con SKU, categoria, unidad, stock minimo, costo estandar y estado activo.
- `v0.8.2`: bodegas y saldos de stock por producto/bodega.
- `v0.8.3`: movimientos de entrada, salida y ajuste con actualizacion transaccional del saldo.
- `v0.8.4`: valorizacion por costo promedio, dashboard, reportes por categoria y pruebas automaticas.

## Rutas

| Ruta | Uso |
| --- | --- |
| `/inventario/` | Dashboard de inventario. |
| `/inventario/productos/` | Catalogo de productos. |
| `/inventario/bodegas/` | Bodegas. |
| `/inventario/stock/` | Saldos actuales. |
| `/inventario/movimientos/` | Historial de movimientos. |
| `/inventario/movimientos/nuevo/` | Registro de entrada, salida o ajuste. |
| `/inventario/valorizacion/` | Reporte valorizado. |

## Modelos

| Modelo | Uso |
| --- | --- |
| `Product` | Producto/SKU con unidad, categoria y parametros de stock. |
| `Warehouse` | Bodega o ubicacion de stock. |
| `StockBalance` | Saldo actual por producto y bodega. |
| `StockMovement` | Entrada, salida o ajuste aplicado al saldo. |

## Permisos

| Permiso | Uso |
| --- | --- |
| `Inventory.access_inventory_module` | Acceso al modulo. |
| `Inventory.manage_inventory_config` | Alta/edicion de productos y bodegas. |
| `Inventory.manage_inventory_stock` | Registro de movimientos. |
| `Inventory.view_inventory_reports` | Reportes y valorizacion. |

## Nota Operativa

La valorizacion usa costo promedio guardado en `StockBalance`. Para la operacion actual con SQLite esto mantiene el modulo liviano y suficiente para inventario inicial. Si mas adelante se necesita cierre mensual, trazabilidad contable o kardex formal, conviene agregar documentos de inventario y periodos cerrados antes de migrar a PostgreSQL.
