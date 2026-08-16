# Revision de evolucion funcional 1.2.x

Fecha: 2026-08-16

## Resultado general

Los cinco frentes revisados tienen bases reutilizables, pero ninguno cumple todavia un flujo operativo completo. La implementacion debe respetar el orden contabilidad, inventario, comercio, documentos PDF e IA, porque cada etapa consume reglas o documentos de la anterior.

## v1.2.5 - Contabilidad controlada

### Base existente

- Plan de cuentas, centros de costo y mapeo de items de remuneraciones.
- Generacion transaccional de asientos de remuneraciones.
- Estados de asiento `draft`, `posted` y `void`.
- Validacion de asiento balanceado y reportes de saldos.

### Faltantes

- No existen acciones controladas para contabilizar o anular asientos.
- No hay aprobador, fechas de aprobacion/contabilizacion/anulacion ni motivo de anulacion.
- Un asiento existente puede reemplazarse; esto debe prohibirse cuando este contabilizado.
- Falta cierre por periodo que impida modificaciones posteriores.
- Falta exportacion formal con formato y columnas acordados con Contabilidad.
- Faltan permisos separados, auditoria y pruebas de transiciones de estado.

### Criterio de cierre

Un usuario autorizado puede aprobar, contabilizar y anular con trazabilidad; un periodo cerrado bloquea cambios; los asientos contabilizados son balanceados e inmutables; la exportacion acordada reproduce exactamente sus lineas.

## v1.2.6 - Inventario documental y kardex

### Base existente

- Productos, bodegas, saldos, movimientos, costo promedio y valorizacion.
- Aplicacion atomica de entradas, salidas y ajustes.
- Bloqueo de salidas sin stock y registro del usuario creador.

### Faltantes

- El movimiento no conserva saldo y costo anterior/posterior, necesarios para un kardex verificable.
- No hay documentos de recepcion, despacho o ajuste con cabecera, lineas, numeracion y estados.
- No existe reversa controlada; un movimiento aplicado queda marcado, pero no tiene movimiento compensatorio formal.
- No hay cierre de inventario por periodo ni bloqueo retroactivo.
- Faltan permisos de aprobacion, auditoria del documento y pruebas de concurrencia/idempotencia.

### Criterio de cierre

Cada variacion de stock nace de un documento confirmado o una reversa trazable; el kardex reconstruye cantidades y valores; los cierres bloquean movimientos retroactivos y los saldos coinciden con la suma del kardex.

## v1.2.7 - Integracion comercio, stock y contabilidad

### Base existente

- Proveedores, clientes, ordenes y lineas de compra/venta vinculadas a productos.
- Estados `draft`, `confirmed` y `cancelled` y totales comerciales.

### Faltantes

- Cambiar el estado a confirmado no genera recepcion ni despacho.
- No existe bodega por documento ni cantidades recibidas/despachadas parciales.
- No existen cuentas contables configurables para compras, ventas, impuestos, inventario, costo de venta o cuentas por pagar/cobrar.
- No hay idempotencia para impedir movimientos o asientos duplicados.
- La anulacion no genera reversas de stock y contabilidad.

### Decisiones de negocio obligatorias

- Definir si una orden confirmada mueve stock o si lo hace un documento separado de recepcion/despacho.
- Definir recepciones/despachos parciales, impuestos, descuentos, monedas y politica de costo de venta.
- Definir momento contable: orden, recepcion/despacho, factura o pago.

### Criterio de cierre

Confirmar el evento de negocio aprobado genera una sola vez los documentos de inventario y asientos correspondientes; anulaciones generan reversas; las referencias permiten navegar desde la orden hasta todos sus efectos.

## v1.2.8 - PDF formal server-side

### Base existente

- Reportes nativos con filtros, graficos y estilos de impresion/guardado como PDF desde el navegador.

### Alcance recomendado

El PDF server-side no debe reemplazar todos los reportes interactivos. Debe reservarse para documentos de formato fijo: asientos contabilizados, libro o comprobante de cierre, recepcion, despacho y documentos comerciales aprobados.

### Faltantes y criterio de cierre

- Definir plantilla, tamaño de pagina, numeracion, zona horaria, moneda y datos legales.
- Generar el PDF desde datos persistidos y una version de plantilla identificable.
- Aplicar permisos, auditoria, pruebas de contenido y respuesta de descarga segura.
- El mismo documento y version deben producir contenido funcionalmente reproducible.

## v1.2.9 - IA local con caso de uso aprobado

### Base existente

- Solo existe arquitectura documental: servicio LAN separado de Django y sin acceso directo a PostgreSQL.

### Primer caso recomendado para aprobacion

Asistente de consulta explicativa de reportes, limitado a datos agregados que la API entregue segun los permisos del usuario. No debe escribir datos, aprobar operaciones, calcular remuneraciones ni ejecutar SQL libre.

### Criterio de cierre

El caso de uso tiene responsable y datos autorizados; el servicio exige autenticacion interna, aplica timeout y limites; no tiene acceso directo a la base; registra solicitudes sin secretos ni datos sensibles completos; y una caida de IA no afecta la operacion del ERP.

## Dependencias

```text
v1.2.5 Contabilidad ─┐
                    ├─> v1.2.7 Comercio integrado ─> v1.2.8 PDF formal
v1.2.6 Inventario ──┘

v1.2.9 IA local: independiente, pero posterior a estabilizar permisos y reportes
```
