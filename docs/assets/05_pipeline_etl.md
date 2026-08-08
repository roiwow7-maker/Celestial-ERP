# Pipeline ETL

Fecha de referencia: 2026-07-13

Version documentada: `1.0.8`

## Flujo completo

```text
Excel historico o CSV transformado
    -> dataload.py
    -> transformed.csv
    -> tabcreated.py
    -> csv_por_categoria/
    -> build_liquidaciones_csvs.py
    -> csv_equivalentes_liquidaciones/
    -> transfer_liquidaciones_to_excel.py
    -> Liquidaciones_Historicas_Cargadas.xlsx
    -> import_payroll_data
    -> db.sqlite3
```

El orquestador principal es:

```powershell
python run_etl.py
```

## `run_etl.py`

Orquesta:

1. Transformacion de historico.
2. Separacion por categoria.
3. Generacion de CSV equivalentes.
4. Generacion opcional de Excel final.
5. Importacion opcional a Django.

Opciones relevantes:

```powershell
python run_etl.py --input archivo.xlsx
python run_etl.py --source-format transformed_csv --input transformed.csv
python run_etl.py --skip-excel
python run_etl.py --skip-import
python run_etl.py --clear
```

## `dataload.py`

Entrada default:

```text
ITEMS_ACUMULADOS_Historico Payroll.xlsx
```

Salida default:

```text
transformed.csv
```

Funcion:

- Lee hoja `Sheet1`.
- Conserva columnas de identidad del trabajador/periodo.
- Convierte columnas de items a formato largo.
- Elimina montos cero.
- Clasifica `codigo_item` en `categoria_item`.
- Marca items que requieren confirmacion.

## `tabcreated.py`

Entrada:

```text
transformed.csv
```

Salida:

```text
csv_por_categoria/
```

Funcion:

- Agrupa por `categoria_item`.
- Genera un CSV por categoria.
- Limpia archivos CSV anteriores de la carpeta de salida.

## `build_liquidaciones_csvs.py`

Entrada:

```text
transformed.csv
Copia de Liquidaciones Historicas (37).xlsx
descripciones_codigo_item/
```

Salida:

```text
csv_equivalentes_liquidaciones/
```

Genera:

- `Liquidaciones.csv`
- `Haberes_Imponibles.csv`
- `Haberes_No_Imponibles.csv`
- `Descuentos.csv`
- `Lineas_de_Finiquito.csv`
- `resumen_generacion.csv`

Funcion:

- Lee encabezados desde la plantilla Excel.
- Calcula totales de liquidacion.
- Usa descripciones de items si existen.
- Mantiene compatibilidad con la plantilla historica.

## `transfer_liquidaciones_to_excel.py`

Entrada:

```text
csv_equivalentes_liquidaciones/
Copia de Liquidaciones Historicas (37).xlsx
```

Salida:

```text
Liquidaciones_Historicas_Cargadas.xlsx
```

Funcion:

- Valida que los encabezados CSV coincidan con cada hoja.
- Limpia filas antiguas de la plantilla.
- Inserta datos nuevos.
- Guarda Excel final.

## Importacion a Django

Comando:

```powershell
cd Celestial_ERP
python manage.py import_payroll_data
```

Entradas default:

- `../transformed.csv`
- `../csv_equivalentes_liquidaciones/Liquidaciones.csv`
- `../descripciones_codigo_item`

Opciones:

```powershell
python manage.py import_payroll_data --clear
python manage.py import_payroll_data --transformed ruta.csv --summaries Liquidaciones.csv
```

Importa:

- trabajadores
- periodos
- items
- movimientos
- liquidaciones
- corrida `ImportRun`

## Carga web

Ruta:

```text
/cargas/
```

Modo v0.6.5:

- Puede ejecutar ETL en segundo plano.
- Guarda `job_config.json`.
- Actualiza `job_status.json`.
- Captura `stdout.log` y `stderr.log`.
- Genera reporte de calidad si existe `transformed.csv`.

Estado:

```text
/cargas/estado/<run_id>/
```

## Validacion de calidad

Archivo:

```text
Celestial_ERP/DATA_scope/quality.py
```

Uso:

- Revisa columnas requeridas.
- Detecta problemas basicos en `transformed.csv`.
- Escribe `reporte_calidad_carga.csv`.

