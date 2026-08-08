# Datos generados y archivos

Fecha de referencia: 2026-07-13

Version documentada: `1.0.8`

## Entradas historicas

| Archivo | Uso |
| --- | --- |
| `ITEMS_ACUMULADOS_Historico Payroll.xlsx` | Fuente historica principal. |
| `Copia de Liquidaciones Historicas (37).xlsx` | Plantilla usada para equivalentes y Excel final. |
| `Planilla_Basica_Implementacion.xlsx` | Material de implementacion/base historica. |

## Salidas ETL

| Ruta | Uso |
| --- | --- |
| `transformed.csv` | Formato largo con trabajador, periodo, item, categoria y monto. |
| `csv_por_categoria/*.csv` | Un CSV por categoria de item. |
| `csv_equivalentes_liquidaciones/*.csv` | CSV compatibles con hojas de liquidaciones. |
| `Liquidaciones_Historicas_Cargadas.xlsx` | Excel final generado. |

## Diccionarios

Carpeta:

```text
descripciones_codigo_item/
```

Uso:

- Mapear `codigo_item` a descripcion legible.
- Alimentar `PayrollItem.descripcion`.
- Mejorar nombres en CSV equivalentes.

## Uploads web

Carpeta:

```text
uploads/
```

Cada corrida puede contener:

- archivo original subido
- `transformed.csv`
- `csv_por_categoria/`
- `csv_equivalentes_liquidaciones/`
- `Liquidaciones_Historicas_Cargadas.xlsx`
- `job_config.json`
- `job_status.json`
- `stdout.log`
- `stderr.log`
- `reporte_calidad_carga.csv`

Limpieza:

```powershell
cd Celestial_ERP
python manage.py cleanup_uploads --dry-run
python manage.py cleanup_uploads --days 30
```

## Backups

Carpeta:

```text
backups/
```

Formato:

```text
db_AAAAMMDD_HHMMSS.sqlite3
```

Comando:

```powershell
python manage.py backup_sqlite --retention-days 30 --keep-last 5
```

## Reports

Carpeta:

```text
reports/
```

Uso:

- Validaciones de reglas de negocio.
- Reportes CSV generados por comandos.

## Logs

Carpeta:

```text
logs/
```

Uso:

- seguimiento de errores
- diagnostico ETL
- auditoria tecnica no funcional

## Datos sensibles

Se consideran sensibles:

- nombres de trabajadores
- RUT
- liquidaciones
- montos
- respaldos DB
- logs que incluyan rutas o errores de carga
- archivos subidos

Reglas:

- No subir a repositorios publicos.
- No enviar por canales inseguros.
- Limpiar `uploads/` periodicamente.
- Mantener backups fuera de git.
- Validar permisos de carpetas antes de operar en LAN.

