# Modelos, datos y formularios

Fecha de referencia: 2026-07-13

Version documentada: `1.0.8`

## Modelos Applet

### `AuditLog`

Uso: auditoria operativa del sistema.

Campos principales:

- `user`
- `action`
- `module`
- `description`
- `object_type`
- `object_id`
- `object_repr`
- `changes`
- `created_at`

Se registra desde:

- `Applet/audit.py`
- cambios manuales de `DATA_scope/audit.py`
- backups
- cargas ETL
- acciones administrativas relevantes

Desde `v0.9.8`, los cambios manuales guardan trazabilidad estructurada por objeto y cambios JSON para permitir filtros mas precisos.

## Modelos DATA_scope

### `Employee`

Trabajador.

Campos principales:

- `codigo_ficha`
- `rut`
- `nombre`
- `estado`
- `division`
- `afp`
- `isapre`
- fechas de ingreso/retiro
- jornada y horario

Estados:

- `active`
- `inactive`
- `terminated`
- `pending_review`

Permisos:

- `access_payroll_module`
- `manage_employee_status`

### `PayrollPeriod`

Periodo de remuneracion.

Campos:

- `periodo`
- `year`
- `month`

Formato esperado de `periodo`: `AAAAMM`.

### `PayrollItem`

Item/codigo de remuneracion.

Campos:

- `codigo`
- `categoria`
- `descripcion`
- `requiere_confirmacion`

Categorias:

- `asignaciones_familiares`
- `contribucion_empleador`
- `descuentos_legales_previsionales`
- `haberes_exentos_no_imponibles`
- `haberes_normales_imponibles`
- `otros_descuentos`
- `provisiones`
- `totales`

### `PayrollEntry`

Movimiento de remuneracion por trabajador, periodo e item.

Relaciones:

- `employee`
- `period`
- `item`

Campo monetario:

- `monto`

Restriccion:

- unico por `employee + period + item`.

### `PayrollSummary`

Liquidacion/resumen por trabajador y periodo.

Relaciones:

- `employee`
- `period`

Campos clave:

- `document_number`
- `rut_empresa`
- `sueldo_base`
- dias y horas
- costo empresa
- haberes
- descuentos
- sueldo liquido
- impuestos
- aportes previsionales y patronales

Restriccion:

- unica por `employee + period`.

### `ImportRun`

Auditoria de corrida ETL.

Estados:

- `started`
- `success`
- `failed`

Guarda:

- rutas de archivos
- hash SHA256 de entradas
- si hubo limpieza previa
- conteos importados
- error en caso de fallo

Permisos:

- `upload_payroll_data`
- `import_payroll_data`
- `clear_payroll_data`
- `download_upload_output`

## Modelos Accounting

| Modelo | Uso |
| --- | --- |
| `ChartAccount` | Cuenta del plan de cuentas. |
| `CostCenter` | Centro de costo. |
| `PayrollItemAccountMapping` | Mapeo entre item de remuneracion y cuenta contable. |
| `JournalEntry` | Cabecera de asiento contable. |
| `JournalEntryLine` | Linea contable con Debe/Haber. |

## Modelos Inventory

| Modelo | Uso |
| --- | --- |
| `Product` | Producto/SKU con categoria, unidad, minimo y costo estandar. |
| `Warehouse` | Bodega o ubicacion. |
| `StockBalance` | Saldo actual por producto/bodega con costo promedio. |
| `StockMovement` | Entrada, salida o ajuste aplicado al saldo. |

## Modelos Commerce

| Modelo | Uso |
| --- | --- |
| `Supplier` | Proveedor. |
| `Customer` | Cliente. |
| `PurchaseOrder` | Documento de compra. |
| `PurchaseOrderLine` | Linea de compra asociada a producto. |
| `SalesOrder` | Documento de venta. |
| `SalesOrderLine` | Linea de venta asociada a producto. |

## Modelos Attendance

| Modelo | Uso |
| --- | --- |
| `AttendanceRecord` | Registro unico por trabajador y fecha con entrada, salida, descanso, estado, fuente y notas. |

El modelo calcula `worked_minutes` y `worked_hours`, descuenta descanso y soporta turnos nocturnos que terminan al dia siguiente.

## Formularios

Archivo:

```text
Celestial_ERP/DATA_scope/forms.py
```

| Formulario | Modelo | Uso |
| --- | --- | --- |
| `EmployeeForm` | `Employee` | Alta/edicion de trabajador. |
| `PayrollPeriodForm` | `PayrollPeriod` | Alta/edicion de periodo con validacion `AAAAMM`. |
| `PayrollItemForm` | `PayrollItem` | Alta/edicion de item. |
| `PayrollSummaryForm` | `PayrollSummary` | Alta/edicion de liquidacion. |
| `PayrollEntryForm` | `PayrollEntry` | Alta/edicion de movimiento. |
| `ProductForm` | `Product` | Alta/edicion de producto. |
| `WarehouseForm` | `Warehouse` | Alta/edicion de bodega. |
| `StockMovementForm` | `StockMovement` | Registro de movimiento de stock. |
| `SupplierForm` | `Supplier` | Alta/edicion de proveedor. |
| `CustomerForm` | `Customer` | Alta/edicion de cliente. |
| `PurchaseOrderForm` | `PurchaseOrder` | Alta de compra. |
| `SalesOrderForm` | `SalesOrder` | Alta de venta. |
| `AttendanceRecordForm` | `AttendanceRecord` | Alta/edicion de asistencia diaria. |

Todos heredan estilos Bootstrap desde `BaseStyledModelForm`.

## Admins

| Archivo | Modelos registrados |
| --- | --- |
| `Applet/admin.py` | `AuditLog` y version visible del admin. |
| `DATA_scope/admin.py` | `Employee`, `PayrollPeriod`, `PayrollItem`, `PayrollEntry`, `PayrollSummary`, `ImportRun`. |
| `Accounting/admin.py` | `ChartAccount`, `CostCenter`, `PayrollItemAccountMapping`, `JournalEntry`, `JournalEntryLine`. |
| `Inventory/admin.py` | `Product`, `Warehouse`, `StockBalance`, `StockMovement`. |
| `Commerce/admin.py` | `Supplier`, `Customer`, `PurchaseOrder`, `PurchaseOrderLine`, `SalesOrder`, `SalesOrderLine`. |
| `Attendance/admin.py` | `AttendanceRecord`. |

El admin es una herramienta interna. Para operacion diaria conviene usar las vistas propias del ERP porque aplican flujos y permisos mas especificos.

