# Compras y ventas

El modulo `Commerce` queda activo como base v0.9 de Celestial ERP.

## Alcance Cerrado

- `v0.9.1`: compras con documentos y lineas asociadas a productos.
- `v0.9.2`: proveedores.
- `v0.9.3`: ventas con documentos y lineas asociadas a productos.
- `v0.9.4`: clientes.

## Rutas

| Ruta | Uso |
| --- | --- |
| `/comercio/` | Dashboard comercial. |
| `/comercio/proveedores/` | Catalogo de proveedores. |
| `/comercio/clientes/` | Catalogo de clientes. |
| `/comercio/compras/` | Documentos de compra. |
| `/comercio/ventas/` | Documentos de venta. |
| `/comercio/reportes/` | Reportes comerciales iniciales. |

## Modelos

| Modelo | Uso |
| --- | --- |
| `Supplier` | Proveedor. |
| `Customer` | Cliente. |
| `PurchaseOrder` | Documento/cabecera de compra. |
| `PurchaseOrderLine` | Linea de compra asociada a producto. |
| `SalesOrder` | Documento/cabecera de venta. |
| `SalesOrderLine` | Linea de venta asociada a producto. |

## Permisos

| Permiso | Uso |
| --- | --- |
| `Commerce.access_commerce_module` | Acceso al modulo comercial. |
| `Commerce.manage_commerce_partners` | Administrar proveedores y clientes. |
| `Commerce.manage_purchases` | Administrar compras. |
| `Commerce.manage_sales` | Administrar ventas. |
| `Commerce.view_commerce_reports` | Ver reportes comerciales. |

## Nota Operativa

Esta version no descuenta ni ingresa stock automaticamente. Esa integracion debe hacerse con una regla clara de confirmacion/recepcion/despacho para no alterar Inventario por documentos en borrador.
