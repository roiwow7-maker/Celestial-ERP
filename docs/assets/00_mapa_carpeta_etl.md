# Mapa de la carpeta ETL

Fecha de referencia: 2026-07-13

Version documentada: `1.0.8`

## Raiz del workspace

La carpeta `C:\Users\RoyGabrielZaioLopez\Desktop\ETL` contiene el sistema completo: scripts ETL historicos, proyecto Django, datos transformados, respaldos, reportes y documentacion.

## Carpetas principales

| Carpeta | Uso |
| --- | --- |
| `Celestial_ERP/` | Proyecto Django operativo. Contiene `manage.py`, apps, settings y base SQLite. |
| `csv_por_categoria/` | Salidas generadas desde `tabcreated.py`, un CSV por categoria de item. |
| `csv_equivalentes_liquidaciones/` | CSV equivalentes a hojas de la plantilla de liquidaciones. |
| `csv_equivalentes_liquidaciones_review/` | Copia/revision de CSV equivalentes. |
| `descripciones_codigo_item/` | Diccionarios CSV de codigo item a descripcion. |
| `docs/` | Documentacion general del sistema. |
| `docs/assets/` | Diagramas SVG y documentacion tecnica ampliada. |
| `backups/` | Respaldos SQLite generados por `backup_sqlite`. |
| `logs/` | Logs persistentes de Django, ERP y ETL. |
| `reports/` | Reportes de validacion generados por comandos. |
| `uploads/` | Corridas de carga web, archivos subidos, estados y salidas descargables. |
| `venv/` | Entorno virtual local de Python. No es parte funcional del codigo. |

## Archivos raiz importantes

| Archivo | Uso |
| --- | --- |
| `run_etl.py` | Orquesta el flujo ETL completo. |
| `dataload.py` | Transforma Excel historico a `transformed.csv`. |
| `tabcreated.py` | Separa `transformed.csv` por categoria. |
| `build_liquidaciones_csvs.py` | Genera CSV equivalentes a plantilla de liquidaciones. |
| `transfer_liquidaciones_to_excel.py` | Carga CSV equivalentes en la plantilla Excel final. |
| `requirements.txt` | Dependencias Python principales. |
| `start_erp_web.ps1` | Arranque local del servidor Django. |
| `backup_erp.ps1` | Script PowerShell para backup. |
| `ROADMAP.md` | Roadmap vigente del sistema. |
| `version_log.md` | Historial de versiones desde `0.0.1` hasta `1.0.8`. |
| `DOCUMENTACION_GENERAL_APLICACION.md` | Documento ejecutivo general. |
| `REGLAS_NEGOCIO_REMUNERACIONES.md` | Reglas funcionales de remuneraciones. |
| `ARQUITECTURA_ERP_REVISION.md` | Revision arquitectonica historica. |
| `EVALUACION_SISTEMA.md` | Evaluacion funcional del sistema. |

## Archivos de datos raiz

| Archivo | Uso |
| --- | --- |
| `ITEMS_ACUMULADOS_Historico Payroll.xlsx` | Fuente historica principal para ETL. |
| `Copia de Liquidaciones Historicas (37).xlsx` | Plantilla base de liquidaciones. |
| `transformed.csv` | CSV largo transformado desde historico. |
| `Liquidaciones_Historicas_Cargadas.xlsx` | Excel final generado desde CSV equivalentes. |
| `resumen_items_historico.csv` | Resumen exploratorio de items. |
| `validacion_excel_vs_csv.csv` | Validacion historica Excel contra CSV. |

## Proyecto Django

| Ruta | Uso |
| --- | --- |
| `Celestial_ERP/manage.py` | Entrada de comandos Django. |
| `Celestial_ERP/Celestial_ERP/` | Proyecto Django: urls, asgi, wsgi, settings. |
| `Celestial_ERP/Applet/` | Portal, seguridad, auditoria, backups, UI base. |
| `Celestial_ERP/DATA_scope/` | Remuneraciones, ETL web, modelos payroll, reportes. |
| `Celestial_ERP/Accounting/` | Contabilidad: cuentas, centros, mapeos, asientos y reportes. |
| `Celestial_ERP/Inventory/` | Inventario: productos, bodegas, stock, movimientos y valorizacion. |
| `Celestial_ERP/Commerce/` | Compras y ventas: proveedores, clientes y documentos comerciales. |
| `Celestial_ERP/Attendance/` | Asistencia: registros historicos por trabajador, dia, mes, entrada y salida. |
| `Celestial_ERP/ERP_api/` | API JSON interna. |
| `Celestial_ERP/db.sqlite3` | Base de datos SQLite local. |

## Carpetas sensibles

Estas carpetas pueden contener datos personales, liquidaciones o informacion operativa sensible:

- `uploads/`
- `backups/`
- `logs/`
- `reports/`
- `Celestial_ERP/db.sqlite3`
- CSV y Excel de remuneraciones en la raiz

No deben subirse a repositorios publicos ni compartirse sin control.

