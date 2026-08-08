# Ideas para evolucion de modulos

Fecha de referencia: 2026-07-13

Este documento junta ideas para evolucionar Celestial ERP despues de la base `1.0.3`. Contabilidad, Inventario, Compras/Ventas y Asistencia ya existen como modulos iniciales; lo pendiente es cerrar reglas, integraciones, aprobaciones y despliegue.

## Estado Actual

| Linea | Estado |
| --- | --- |
| `v0.7` Contabilidad | Base activa. |
| `v0.8` Inventario | Base activa. |
| `v0.9.1` Compras | Base activa. |
| `v0.9.2` Proveedores | Base activa. |
| `v0.9.3` Ventas | Base activa. |
| `v0.9.4` Clientes | Base activa. |
| `v0.9.6C` Asistencia | Base activa. |
| `v0.9.7` Operacion SQLite reforzada | Base activa. |
| `v0.9.8` Auditoria granular | Base activa. |
| `v0.9.9` Integracion asistencia-remuneraciones | Base activa. |

## Contabilidad Avanzada

Base ya disponible:

- Plan de cuentas.
- Centros de costo.
- Mapeo item-cuenta.
- Asientos desde remuneraciones.
- Reportes iniciales.

Ideas futuras:

- Validar plan con contador o sistema externo.
- Cierres/aprobaciones por periodo.
- Exportacion a formato contable externo.
- Reportes por centro de costo y periodo.
- Integracion comercial para compras/ventas confirmadas.

## Inventario Avanzado

Base ya disponible:

- Productos.
- Bodegas.
- Stock.
- Movimientos.
- Valorizacion.

Ideas futuras:

- Kardex formal.
- Documentos de recepcion/despacho.
- Cierres de inventario.
- Ajustes con flujo de aprobacion.
- Integracion controlada con compras y ventas.

## Compras Avanzadas

Base ya disponible:

- Proveedores.
- Documentos de compra.
- Lineas de compra por producto.
- Reportes iniciales.

Ideas futuras:

- Solicitudes de compra.
- Aprobaciones por monto o rol.
- Recepcion parcial o total.
- Registro de documentos tributarios.
- Movimiento de inventario solo al confirmar recepcion.
- Integracion contable solo al confirmar documento.

## Ventas Avanzadas

Base ya disponible:

- Clientes.
- Documentos de venta.
- Lineas de venta por producto.
- Reportes iniciales.

Ideas futuras:

- Cotizaciones.
- Conversion de cotizacion a venta.
- Reserva de stock.
- Despacho/entrega.
- Facturacion electronica si se requiere.
- Integracion contable solo con documento confirmado.

## Asistencia Avanzada

Base ya disponible:

- Registros diarios por trabajador.
- Historico individual.
- Reporte mensual.
- Exportacion CSV.
- Impresion/PDF desde navegador.

Ideas futuras:

- Importacion masiva desde reloj control.
- Turnos y horarios esperados por trabajador.
- Alertas de atrasos o ausencias repetidas.
- Integracion con liquidaciones para dias trabajados, ausencias y horas extras.

## Configuracion

Ideas futuras:

- Parametros editables por administrador.
- Datos de empresa/RUT/representantes.
- Configuracion de retencion de backups.
- Configuracion por modulo.
- Bitacora de cambios de parametros.

## Integraciones

Estado actual:

- `ERP_api` entrega endpoints JSON basicos protegidos por login/permisos.

Ideas futuras:

- Versionado formal de API.
- Tokens para integraciones internas.
- Endpoints paginados.
- Filtros por periodo/trabajador/item.
- Webhooks internos.
- Conectores hacia BI o sistemas externos.

## Orden Recomendado

1. `v1.0.4`: backups reales con restauracion validada.
2. `v1.0.5`: auditoria validada por usuario/rol.
3. `v1.0.7`: IA local cuantizada como servicio LAN separado.
4. `v1.0.8` a `v1.0.10`: PostgreSQL al final, solo con servidor autorizado.

## Preguntas Abiertas

- Contabilidad: existe plan de cuentas oficial?
- Contabilidad: los asientos deben exportarse a otro sistema?
- Inventario: cuantas bodegas reales existen?
- Inventario: quien aprueba ajustes?
- Compras: quien aprueba y con que limites?
- Ventas: habra facturacion electronica o solo seguimiento interno?
- Integraciones: la API sera solo interna o habra clientes externos?
- Configuracion: que parametros debe poder cambiar un administrador sin tocar codigo?
