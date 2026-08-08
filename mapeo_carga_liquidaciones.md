# Mapeo para cargar Copia de Liquidaciones Historicas (37).xlsx

Fecha de referencia: 2026-07-13

Nota: documento historico de mapeo ETL. Sigue vigente como referencia para salidas Excel en la version operativa `0.9.4`.

El archivo `Copia de Liquidaciones Historicas (37).xlsx` es una plantilla con estas hojas:

- `Liquidaciones`
- `Haberes Imponibles`
- `Haberes No Imponibles`
- `Descuentos`
- `Lineas de Finiquito`

Los CSV de `csv_por_categoria/` deben cargarse asi.

## 1. Haberes Imponibles

CSV origen:

- `csv_por_categoria/haberes_normales_imponibles.csv`

Hoja destino:

- `Haberes Imponibles`

| Columna Excel | Dato desde CSV |
| --- | --- |
| `Numero de Documento*` | `periodo` + `codigo` |
| `Codigo de Ficha` | `codigo` |
| `Rut empresa` | Valor fijo a definir |
| `Nombre` | `codigo_item` |
| `Monto` | `monto` |

## 2. Haberes No Imponibles

CSV origen:

- `csv_por_categoria/haberes_exentos_no_imponibles.csv`
- `csv_por_categoria/asignaciones_familiares.csv`

Hoja destino:

- `Haberes No Imponibles`

| Columna Excel | Dato desde CSV |
| --- | --- |
| `Numero de Documento*` | `periodo` + `codigo` |
| `Codigo de Ficha` | `codigo` |
| `Rut empresa` | Valor fijo a definir |
| `Nombre` | `codigo_item` |
| `Monto` | `monto` |
| `Tributable` | `No` |

## 3. Descuentos

CSV origen:

- `csv_por_categoria/descuentos_legales_previsionales.csv`
- `csv_por_categoria/otros_descuentos.csv`

Hoja destino:

- `Descuentos`

| Columna Excel | Dato desde CSV |
| --- | --- |
| `Numero de Documento*` | `periodo` + `codigo` |
| `Codigo de Ficha` | `codigo` |
| `Rut empresa` | Valor fijo a definir |
| `Nombre` | `codigo_item` |
| `Monto` | `monto` |

## 4. Liquidaciones

CSV origen principal:

- `transformed.csv`

Tambien se usan como control:

- `csv_por_categoria/haberes_normales_imponibles.csv`
- `csv_por_categoria/haberes_exentos_no_imponibles.csv`
- `csv_por_categoria/asignaciones_familiares.csv`
- `csv_por_categoria/descuentos_legales_previsionales.csv`
- `csv_por_categoria/otros_descuentos.csv`
- `csv_por_categoria/contribucion_empleador.csv`
- `csv_por_categoria/provisiones.csv`
- `csv_por_categoria/totales.csv`

Hoja destino:

- `Liquidaciones`

Debe existir una fila por liquidacion, es decir, por combinacion:

- `periodo`
- `codigo`

| Columna Excel | Dato desde CSV |
| --- | --- |
| `Numero de Documento*` | `periodo` + `codigo` |
| `Codigo de Ficha` | `codigo` |
| `RUT Empresa*` | Valor fijo a definir |
| `Dias Trabajados*` | `diastr` |
| `Total Haberes Imponibles*` | Suma de `haberes_normales_imponibles` por `periodo` + `codigo` |
| `Total Haberes No Imponibles No Tributables*` | Suma de `haberes_exentos_no_imponibles` + `asignaciones_familiares` |
| `Total Descuentos Legales*` | Suma de `descuentos_legales_previsionales` |
| `Total Otros Descuentos*` | Suma de `otros_descuentos` |
| `Seguro Cesantia (Empleador)` | Suma de codigos de cesantia empleador si se separan desde `contribucion_empleador` |
| `Mutual Empleador` | Suma de `MUTUAL` / `MUTREL` si aplica |
| `Pago SIS (Empleador)` | Suma de `SISAFP` / `SISREL` / `SISRLQ` si aplica |
| `Otros Aportes Patronales` | Resto de `contribucion_empleador` no asignado a campos especificos |

Columnas que requieren regla de negocio antes de cargar:

- `Sueldo Base*`
- `Dias Laborales*`
- `Dias Licencias*`
- `Dias Permisos*`
- `Dias Ausencias*`
- `Dias Suspendidos*`
- `Numero Horas No Trabajadas*`
- `Sobretiempo horas extras*`
- `Costo Empresa*`
- `Sueldo Liquido*`
- `Base Tributable*`
- `Rebaja Zona Extrema*`
- `Impuesto*`
- `Pago Prevision*`
- `Pago Salud Obligatoria*`
- `Pago Salud Voluntaria*`
- `Pago Prevision Voluntaria*`
- `Seguro Cesantia (Trabajador)*`
- `Trabajo Pesado (Trabajador)*`
- `Saldo Sobregiro*`

## 5. Lineas de Finiquito

Actualmente no hay un CSV separado de finiquitos.

Si se decide que algun codigo corresponde a finiquito, se debe crear un CSV nuevo y cargarlo en:

- `Lineas de Finiquito`

| Columna Excel | Dato desde CSV |
| --- | --- |
| `Numero de Documento*` | `periodo` + `codigo` |
| `Codigo de Ficha` | `codigo` |
| `Rut empresa` | Valor fijo a definir |
| `Nombre` | `codigo_item` |
| `Monto` | `monto` |
| `Codigo item` | `codigo_item` |

## 6. CSV que no se cargan como lineas normales

### `totales.csv`

No se debe cargar como haber o descuento. El codigo `Totales` es un total de control.

Usos recomendados:

- Validar que la suma final por liquidacion calce.
- Comparar contra `Sueldo Liquido*` o contra el total esperado, segun la regla del sistema.

### `provisiones.csv`

No tiene una hoja directa en la plantilla.

Usos posibles:

- Incluirlo en `Costo Empresa*`.
- Mantenerlo solo como control contable.
- Cargarlo en otra plantilla si el sistema tiene una seccion de provisiones.

## 7. Datos que faltan definir

Antes de generar el Excel final hay que confirmar:

1. `RUT Empresa*` / `Rut empresa`.
2. Formato exacto de `Numero de Documento*`.
3. Si `Codigo de Ficha` debe ser `codigo` o `Rut`.
4. Regla exacta para calcular `Sueldo Liquido*`.
5. Si `provisiones.csv` se carga en `Costo Empresa*` o queda solo como control.
6. Si la hoja `Lineas de Finiquito` se usara o queda vacia.
