# Celestial ERP Version Log

Fecha de referencia: 2026-08-07

Este registro resume la evolucion funcional del proyecto desde una base inicial hasta la version actual `1.1.1`. Las versiones tempranas agrupan hitos historicos reconstruidos desde el estado del repositorio y la documentacion disponible.

## 0.0.x - Exploracion y base de datos inicial

- `0.0.1`: Creacion del workspace ETL y primeras pruebas de lectura de planillas historicas.
- `0.0.2`: Identificacion inicial de items de remuneracion y codigos relevantes.
- `0.0.3`: Primeros mapeos documentados para carga de liquidaciones.
- `0.0.4`: Generacion de resumenes CSV iniciales para analizar items historicos.
- `0.0.5`: Primeras pruebas de transformacion con archivos Excel de payroll.

## 0.1.x - Pipeline ETL base

- `0.1.0`: Implementacion de transformacion base en Python.
- `0.1.1`: Lectura de historicos Excel y salida `transformed.csv`.
- `0.1.2`: Separacion de datos por categorias de remuneracion.
- `0.1.3`: Generacion de CSV auxiliares para revision funcional.
- `0.1.4`: Validaciones iniciales Excel versus CSV.
- `0.1.5`: Consolidacion de reglas preliminares de clasificacion.

## 0.2.x - Liquidaciones y salidas compatibles

- `0.2.0`: Generacion de CSV equivalentes a liquidaciones.
- `0.2.1`: Construccion de archivos por categoria.
- `0.2.2`: Incorporacion de descripciones por codigo de item.
- `0.2.3`: Generacion de Excel final de liquidaciones cargadas.
- `0.2.4`: Validacion de resultados de liquidaciones.
- `0.2.5`: Documentacion de reglas de negocio de remuneraciones.

## 0.3.x - Plataforma Django y ERP base

- `0.3.0`: Creacion de proyecto Django `Celestial_ERP`.
- `0.3.1`: Creacion de app `DATA_scope` para remuneraciones.
- `0.3.2`: Modelos de trabajadores, periodos, items, movimientos y liquidaciones.
- `0.3.3`: Comando de importacion `import_payroll_data`.
- `0.3.4`: Dashboard web inicial de remuneraciones.
- `0.3.5`: Reportes web con KPIs y filtros.
- `0.3.6`: Carga ETL desde vista web.
- `0.3.7`: Portal `Applet` como entrada general.
- `0.3.8`: Auditoria inicial y modelo `ImportRun`.
- `0.3.9`: API JSON inicial protegida por login.

## 0.4.x - Seguridad y operacion controlada

- `0.4.0`: Login obligatorio.
- `0.4.1`: Roles funcionales: Administrador, RRHH, Contabilidad y Solo lectura.
- `0.4.2`: Permisos finos por modulo y accion.
- `0.4.3`: Restricciones por permisos en vistas HTML.
- `0.4.4`: API protegida por permisos.
- `0.4.5`: Navegacion superior segun permisos.
- `0.4.6`: Estados laborales de trabajadores.
- `0.4.7`: Ficha individual con cambio de estado controlado.
- `0.4.8`: Carga ETL controlada por permisos.
- `0.4.9`: Opcion de carga individual por codigo de ficha.
- `0.4.10`: Backups iniciales desde comando y pantalla web.
- `0.4.11`: Estado del sistema y prueba de rutas.
- `0.4.12`: Django Admin personalizado.
- `0.4.13`: Validacion funcional con usuarios nominales por rol.
- `0.4.14`: Politica formal de retencion/restauracion de backups.

## 0.5.x - Operacion RRHH controlada

- `0.5.1`: Alta y edicion individual de trabajador desde formulario propio.
- `0.5.2`: Carga individual de liquidacion sin archivo masivo.
- `0.5.3`: Edicion controlada de movimientos de remuneracion.
- `0.5.4`: Vistas dedicadas de periodos, liquidaciones e items.
- `0.5.5`: Validaciones por fila y columna en cargas ETL.
- `0.5.6`: Reporte de calidad de carga con advertencias, duplicados y rechazos.
- `0.5.7`: Auditoria granular de cambios manuales.
- `0.5.8`: Pruebas automaticas de permisos por rol.
- `0.5.8c`: Pulido UI Bootstrap, paleta claro/oscuro, Django Admin estilizado y version pulida sin cambios funcionales de alcance.

## 0.6.x - Base operativa robusta

- `0.6.1`: Separacion de configuracion desarrollo/produccion.
- `0.6.2`: Preparacion de variables sensibles, credenciales nominales y comando `check_operational_security`.
- `0.6.3`: Bootstrap 5.3.3 local/offline, sin dependencia de CDN.
- `0.6.4`: Logs persistentes rotativos de aplicacion y ETL.
- `0.6.5`: Procesamiento asincronico simple para cargas largas mediante comando background y estado por corrida.
- `0.6.6`: Backup SQLite con API `backup`, verificacion `integrity_check`, retencion simple y restauracion documentada.
- `0.6.7`: Seguridad operativa verificable y diagnostico estricto opcional.
- `0.6.8`: Exportaciones adicionales por trabajador, periodo y liquidacion.

## 0.7.x - Contabilidad

- `0.7.1`: Plan de cuentas con cuentas contables administrables desde web y Django Admin.
- `0.7.2`: Centros de costo administrables para imputacion contable inicial.
- `0.7.3`: Mapeo item de remuneracion a cuenta contable, con comando de catalogo base.
- `0.7.4`: Asientos contables desde movimientos/liquidaciones de remuneraciones por periodo.
- `0.7.5`: Reportes contables iniciales, dashboard, saldos por cuenta y pruebas automaticas.
- `0.7.5a`: Pulido visual de reportes y metricas: graficos de barra con desplazamiento lateral, listas con altura fija/scroll vertical y tarjetas metricas sin desbordes.

## 0.8.x - Inventario

- `0.8.1`: Catalogo de productos con SKU, categoria, unidad, stock minimo, costo estandar, formularios web y Django Admin.
- `0.8.2`: Bodegas y saldos de stock por producto/bodega con control de stock bajo.
- `0.8.3`: Movimientos de entrada, salida y ajuste, aplicados desde servicio transaccional con validacion de stock disponible.
- `0.8.4`: Valorizacion por costo promedio, dashboard de inventario, reportes por categoria, navbar/API/roles actualizados y pruebas automaticas.

## 0.9.x - Compras, ventas y asistencia

- `0.9.1`: Compras base con documentos, lineas por producto, totales y administracion web/Admin.
- `0.9.2`: Proveedores base con catalogo, busqueda, formularios y permisos.
- `0.9.3`: Ventas base con documentos, lineas por producto, totales y reportes iniciales.
- `0.9.4`: Clientes base con catalogo, busqueda, formularios, navbar/API/roles actualizados y pruebas automaticas.
- `0.9.6C`: Modulo `Attendance` con asistencia historica diaria, mensual y por trabajador; horas de entrada/salida, estados, fuente del registro, exportacion CSV, impresion/PDF desde navegador, permisos por rol, navbar/API/portal y pruebas automaticas.
- `0.9.7`: Operacion local reforzada sobre SQLite con comando `check_sqlite_operational_health`, diagnostico de integridad, WAL, backups, uploads, volumen base y documentacion de limites sin instalar PostgreSQL.
- `0.9.8`: Auditoria granular avanzada con campos estructurados de objeto, id, representacion y cambios JSON, mas filtros en vista web y admin.
- `0.9.9`: Integracion asistencia-remuneraciones mediante comando `sync_attendance_payroll` para actualizar dias trabajados, ausencias, permisos y horas no trabajadas.

## 1.0.x - Primera version estable local/LAN

- `1.0.1`: Testing amplio con cobertura de auditoria granular, sincronizacion asistencia-remuneraciones, diagnostico SQLite y suite completa.
- `1.0.2`: Documentacion operativa cerrada con guias de SQLite sin PostgreSQL, testing, auditoria, asistencia y comandos.
- `1.0.3`: Deploy local/red interna documentado para operacion LAN controlada sin exponer a internet.
- `1.0.4`: Backups reales con restauracion validada mediante comando `validate_backup_restore`, prueba de copia temporal, `integrity_check` y verificacion de tablas criticas.
- `1.0.5`: Auditoria validada por usuario/rol con prueba automatica de trazabilidad a usuario nominal y grupo funcional.
- `1.0.6`: Plan de migracion de datos documentado con fases, inventario de datos, prevalidaciones y criterios de corte.
- `1.0.7`: Proyeccion de servidor LAN con IA local cuantizada como servicio separado del proceso Django.
- `1.0.8`: Preparacion final de migracion a PostgreSQL documentada para servidor autorizado, sin ejecutar migracion real en el equipo limitado.
- `1.0.9`: Ensayo de migracion SQLite a PostgreSQL completado con migraciones, exportacion e importacion integral.
- `1.0.10`: PostgreSQL activado como base principal; 297.084 objetos validados y superusuario conservado.

## 1.1.x - Operacion PostgreSQL

- `1.1.1`: respaldo PostgreSQL en formato custom mediante `pg_dump`, verificacion con `pg_restore --list`, retencion y ejecucion desde la pantalla administrativa. Version centralizada y repositorio preparado para GitHub sin bases, respaldos, CSV, Excel ni secretos.
- Frontend real planificado por fases en `docs/21_PLAN_FRONTEND_REAL.md` con Next.js/TypeScript, API Django y despliegue progresivo.

### Actualizacion documental post `0.9.4`

- Documentacion Markdown propia del proyecto revisada y alineada a la version operativa `0.9.4`.
- Nuevo indice maestro en `docs/INDICE_DOCUMENTACION.md`.
- Documentos historicos de raiz actualizados con notas de vigencia.
- Mapeo de liquidaciones limpiado de mojibake visible y normalizado a ASCII.
- Documentacion tecnica de `docs/assets/` actualizada con `Commerce`, rutas, modelos, permisos y comandos de prueba.

### Actualizacion documental post `0.9.6C`

- Roadmap reordenado para dejar Asistencia como hito cerrado `0.9.6C`.
- PostgreSQL queda movido al final de `v1.0.x` por limitaciones de permisos/infraestructura.
- Documentacion de `docs/` y `docs/assets/` alineada con el modulo `Attendance`.
- Suite completa validada: 37 pruebas automaticas OK.

### Actualizacion documental post `0.9.7`

- PostgreSQL queda al final del roadmap como `v1.0.8`, `v1.0.9` y `v1.0.10`.
- Se agrega diagnostico operativo SQLite para trabajar de forma controlada mientras no existan permisos de instalacion.
- Se documenta una ruta concreta para seguir avanzando con SQLite, backups, limpieza de uploads y pruebas.
- Suite completa ampliada y validada: 41 pruebas automaticas OK.

## Proximas lineas

- `1.1.2`: Restauracion PostgreSQL probada en una base aislada.
- `1.1.3`: Automatizacion programada y monitoreo de backups.
- `1.1.4`: Credenciales PostgreSQL obligatorias mediante variables de entorno.
- `1.2.0`: Primer flujo vertical del frontend real.
