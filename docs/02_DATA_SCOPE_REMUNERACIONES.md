# DATA_scope - Remuneraciones

Fecha de referencia: 2026-07-13

## Proposito

DATA_scope concentra el modulo real de datos de remuneraciones. Incluye modelos de payroll, dashboard, trabajadores, reportes, cargas ETL, importacion a base y Kanban operativo.

## Modelos principales

| Modelo | Descripcion |
| --- | --- |
| `Employee` | Trabajadores, datos laborales y estado |
| `PayrollPeriod` | Periodos de remuneracion |
| `PayrollItem` | Codigos/conceptos de remuneracion |
| `PayrollEntry` | Movimientos por trabajador, periodo e item |
| `PayrollSummary` | Resumen de liquidacion |
| `ImportRun` | Auditoria de importaciones ETL |

## Rutas

| Ruta | Descripcion |
| --- | --- |
| `/remuneraciones/` | Dashboard de remuneraciones |
| `/remuneraciones/trabajadores/` | Listado de trabajadores y filtros por estado |
| `/remuneraciones/trabajadores/nuevo/` | Alta manual de trabajador |
| `/remuneraciones/trabajadores/<id>/` | Ficha individual y cambio de estado controlado |
| `/remuneraciones/trabajadores/<id>/editar/` | Edicion manual de trabajador |
| `/remuneraciones/periodos/` | Vista dedicada de periodos |
| `/remuneraciones/items/` | Vista dedicada de items |
| `/remuneraciones/liquidaciones/` | Vista dedicada de liquidaciones |
| `/remuneraciones/movimientos/` | Vista dedicada de movimientos |
| `/reportes/` | Reportes con filtros y exportacion |
| `/reportes/exportar-csv/` | Exportacion CSV protegida por permiso |
| `/cargas/` | Carga web de archivos |
| `/cargas/probar-rutas/` | Prueba de rutas |
| `/kanban/` | Kanban operativo de remuneraciones |

## Datos actuales

| Dato | Cantidad |
| --- | ---: |
| Trabajadores | 517 |
| Periodos | 114 |
| Items | 131 |
| Movimientos | 276253 |
| Liquidaciones | 19719 |

## Funcionalidades actuales

- Dashboard de KPIs.
- Estados de trabajadores.
- Ficha individual de trabajador.
- Alta y edicion manual de trabajador.
- Cambio de estado controlado por permiso.
- Vistas dedicadas de periodos, liquidaciones, movimientos e items.
- Carga individual de liquidacion desde formulario.
- Edicion controlada de movimientos.
- Reportes por periodo, departamento y trabajador.
- Filtros por periodo, division, categoria y sueldo liquido.
- Exportacion CSV protegida.
- Impresion/PDF desde navegador.
- Carga web de Excel historico o CSV transformado.
- Alcance de carga masiva o individual por codigo de ficha.
- Importacion al ERP controlada por permiso.
- Limpieza previa controlada por permiso.
- Descarga de salidas controlada por permiso.
- Auditoria de importaciones.
- Auditoria granular de cambios manuales.
- Reporte de calidad de carga con fila, campo, severidad y mensaje.

## Estados de empleados

Campo implementado: `Employee.estado`.

Estados:

- Activo.
- Inactivo.
- Finiquitado.
- Pendiente revision.

Pendiente funcional futuro:

- Definir reglas automaticas basadas en `fecha_retiro`.
- Revisar estados con RRHH.
- Agregar filtros avanzados sobre auditoria granular.

## Permisos relevantes

| Permiso | Uso |
| --- | --- |
| `access_payroll_module` | Ver remuneraciones |
| `manage_employee_status` | Cambiar estado de trabajador |
| `upload_payroll_data` | Subir archivos |
| `import_payroll_data` | Importar al ERP |
| `clear_payroll_data` | Limpiar datos previos |
| `download_upload_output` | Descargar salidas |

## Faltantes

- Recalculo automatico de liquidaciones cuando cambian movimientos.
- Filtros avanzados de auditoria por objeto.
- Pruebas con archivos reales de carga.
- Procesamiento asincronico simple para cargas largas con estado por corrida: completado como base.
- Recalculo automatico completo de resumenes al editar movimientos: pendiente.
