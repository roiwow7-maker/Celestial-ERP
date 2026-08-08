# Celestial ERP Roadmap

Fecha de referencia: 2026-08-07

Version actual del sistema: `1.1.1`.

Hitos previos integrados:

- `0.4.13`: validacion funcional con usuarios nominales de cada rol completada.
- `0.4.14`: politica formal de retencion/restauracion de backups completada.
- `0.7.5a`: modulo contable base completado y pulido visual de reportes/metricas numericas grandes.
- `0.8.4`: inventario base completado con productos, bodegas/stock, movimientos y valorizacion.
- `0.9.4`: compras y ventas base completadas con proveedores, clientes y documentos comerciales.
- `0.9.6C`: asistencia historica completada con registros diarios, reporte mensual, exportacion CSV e impresion/PDF desde navegador.
- `0.9.7`: operacion local reforzada sobre SQLite con diagnostico de salud, backups y limites documentados.
- `0.9.8`: auditoria granular avanzada con filtros por objeto y trazabilidad estructurada.
- `0.9.9`: integracion asistencia-remuneraciones para dias, ausencias, permisos y horas no trabajadas.
- `1.0.3`: testing ampliado, documentacion operativa cerrada y deploy LAN documentado.
- `1.0.8`: backups reales validados, auditoria por usuario/rol, plan de migracion de datos, proyeccion IA LAN y preparacion PostgreSQL documentada.
- `1.0.9`: ensayo SQLite a PostgreSQL completado con migraciones y carga integral de datos.
- `1.0.10`: PostgreSQL activado como base principal y contenido historico validado.
- `1.1.1`: backup PostgreSQL verificado, pantalla administrativa adaptada y preparacion segura para GitHub.

## v0.3 - Plataforma base
- [x] DATA_scope remuneraciones
- [x] ETL historico
- [x] Dashboard
- [x] Reportes
- [x] Carga ETL web
- [x] Applet portal
- [x] Auditoria inicial
- [x] Backups iniciales
- [x] Estado del sistema
- [x] API inicial
- [x] Django Admin personalizado

## v0.4.14 - Control de acceso y operacion segura
- [x] Login obligatorio
- [x] Superusuario local de desarrollo
- [x] Roles reales: Administrador, RRHH, Contabilidad, Solo lectura
- [x] Permisos finos por modulo y accion
- [x] Restricciones por modulo en vistas HTML
- [x] API protegida por login/permisos
- [x] Navegacion superior por permisos
- [x] Navegacion de remuneraciones mas especifica
- [x] Estados de empleados
- [x] Ficha individual de trabajador con cambio de estado controlado
- [x] Carga ETL controlada por permisos
- [x] Opcion de carga individual por codigo de ficha
- [x] v0.4.13 - Validacion funcional con usuarios nominales de cada rol
- [x] v0.4.14 - Politica formal de retencion/restauracion de backups

## v0.5.8 / v0.5.8c - Operacion RRHH controlada y pulido UI
- [x] v0.5.1 - Alta y edicion individual de trabajador desde formulario propio
- [x] v0.5.2 - Carga individual de liquidacion sin archivo masivo
- [x] v0.5.3 - Edicion controlada de movimientos de remuneracion
- [x] v0.5.4 - Vistas dedicadas de periodos, liquidaciones e items
- [x] v0.5.5 - Validaciones por fila y columna en cargas ETL
- [x] v0.5.6 - Reporte de calidad de carga con advertencias, duplicados y rechazos
- [x] v0.5.7 - Auditoria granular de cambios manuales
- [x] v0.5.8 - Pruebas automaticas de permisos por rol
- [x] v0.5.8c - Pulido UI Bootstrap, paleta claro/oscuro y Django Admin sin cambios funcionales de alcance

## v0.6 - Base operativa robusta
- [x] v0.6.1 - Separacion de configuracion desarrollo/produccion
- [x] v0.6.2 - Preparacion de variables sensibles, credenciales nominales y operacion sin claves temporales
- [x] v0.6.3 - Bootstrap local/offline para operacion en red interna sin CDN
- [x] v0.6.4 - Logs persistentes de aplicacion
- [x] v0.6.5 - Procesamiento asincronico simple para cargas largas
- [x] v0.6.6 - Estrategia de backup con retencion y restauracion probada
- [x] v0.6.7 - Seguridad operativa verificable con comando de diagnostico
- [x] v0.6.8 - Exportaciones adicionales por trabajador, periodo y liquidacion

## v0.7 - Contabilidad
- [x] v0.7.1 - Plan de cuentas
- [x] v0.7.2 - Centros de costo
- [x] v0.7.3 - Mapeo item remuneracion a cuenta contable
- [x] v0.7.4 - Asientos contables desde liquidaciones
- [x] v0.7.5 - Reportes contables iniciales y dashboard
- [x] v0.7.5a - Ajuste responsive de reportes: graficos con desplazamiento lateral y listas con scroll vertical

## v0.8 - Inventario
- [x] v0.8.1 - Productos
- [x] v0.8.2 - Stock
- [x] v0.8.3 - Movimientos
- [x] v0.8.4 - Valorizacion

## v0.9 - Compras, ventas y asistencia
- [x] v0.9.1 - Compras
- [x] v0.9.2 - Proveedores
- [x] v0.9.3 - Ventas
- [x] v0.9.4 - Clientes
- [x] v0.9.6C - Asistencia historica por trabajador, dia, mes, entrada/salida, exportacion CSV e impresion/PDF
- [x] v0.9.7 - Operacion local reforzada sobre SQLite sin instalar PostgreSQL
- [x] v0.9.8 - Auditoria granular avanzada con filtros por objeto y trazabilidad de cambios manuales
- [x] v0.9.9 - Integracion asistencia-remuneraciones para dias, ausencias y horas

## v1.0 - Primera version estable
- [x] v1.0.1 - Testing amplio
- [x] v1.0.2 - Documentacion operativa cerrada
- [x] v1.0.3 - Deploy local/red interna documentado
- [x] v1.0.4 - Backups reales con restauracion validada
- [x] v1.0.5 - Auditoria validada por usuario/rol
- [x] v1.0.6 - Plan de migracion de datos documentado
- [x] v1.0.7 - Proyeccion de servidor LAN con IA local cuantizada como servicio separado
- [x] v1.0.8 - Preparacion final de migracion a PostgreSQL en servidor autorizado
- [x] v1.0.9 - Ensayo de migracion SQLite a PostgreSQL
- [x] v1.0.10 - Migracion real a PostgreSQL con infraestructura y permisos autorizados

### Evidencia de cierre v1.0.9-v1.0.10

- Backend Django cambiado a `django.db.backends.postgresql`.
- Base activa `celestial_erp` con usuario PostgreSQL `admin_cerp`.
- Dependencia `psycopg` incorporada e instalada.
- Todas las migraciones Django aplicadas correctamente en PostgreSQL.
- `297.084` objetos transferidos desde SQLite.
- Conteos principales validados: `517` empleados, `276.253` movimientos de remuneraciones, `19.719` resumenes y `161` eventos de auditoria.
- Superusuario Django `admin` conservado, activo y con permisos de staff/superusuario.
- Archivo SQLite original conservado como respaldo de reversa.
- `manage.py check` ejecutado sin observaciones.

## v1.1 - Operacion segura sobre PostgreSQL

### Prioridad critica

- [x] v1.1.1 - Implementar backups PostgreSQL con `pg_dump`, retencion y registro de auditoria
- [ ] v1.1.2 - Implementar y probar restauracion PostgreSQL con `pg_restore` en una base aislada
- [x] v1.1.3 - Adaptar la pantalla, estado del sistema y permisos de backups para PostgreSQL
- [ ] v1.1.4 - Mover credenciales PostgreSQL a variables de entorno obligatorias y retirar valores sensibles del codigo

### Prioridad alta

- [ ] v1.1.5 - Ejecutar y adaptar toda la suite automatizada usando PostgreSQL
- [ ] v1.1.6 - Comparar automaticamente conteos, sumas y reglas de negocio entre SQLite y PostgreSQL
- [ ] v1.1.7 - Crear usuarios nominales, rotar credenciales administrativas y validar los cuatro roles
- [ ] v1.1.8 - Preparar ejecucion productiva con WSGI/ASGI, servicio persistente, HTTPS y `DEBUG=false`
- [ ] v1.1.9 - Definir monitoreo de conexion, espacio, rendimiento, logs y fallos de backup

### Prioridad media

- [ ] v1.1.10 - Programar limpieza y retencion de archivos sensibles en `uploads/`
- [ ] v1.1.11 - Ampliar pruebas de integracion ETL con archivos reales pequenos y errores por fila/columna
- [ ] v1.1.12 - Validar reglas oficiales de remuneraciones y clasificacion de items con el area de negocio
- [ ] v1.1.13 - Evaluar cola de trabajos dedicada si las cargas simultaneas superan el proceso background actual

### Evolucion funcional posterior

- [ ] Contabilidad: cierres, aprobaciones y exportacion formal de asientos
- [ ] Inventario: kardex, cierres y documentos de recepcion/despacho
- [ ] Compras y ventas: integracion con stock y contabilidad segun reglas aprobadas
- [ ] Reportes: PDF server-side solo para documentos que requieran formato fijo
- [ ] IA local: mantener como servicio LAN separado y avanzar solo con un caso de uso aprobado

## Proximo paso recomendado

Continuar con `v1.1.2` y `v1.1.4`: probar una restauracion PostgreSQL completa en una base aislada y retirar las credenciales de la configuracion versionada. El backup manual PostgreSQL ya esta operativo y verificado; la automatizacion debe ejecutarse mediante un planificador del sistema, no durante una peticion web. El frontend real queda planificado en `docs/21_PLAN_FRONTEND_REAL.md`.
