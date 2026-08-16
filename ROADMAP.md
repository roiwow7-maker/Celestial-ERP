# Celestial ERP Roadmap

Fecha de referencia: 2026-08-16

Version actual del sistema: `1.2.1`.

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
- `1.1.1a`: README principal consolidado, instalacion segura, operacion PostgreSQL y navegacion documental.
- `1.1.1b`: licencia propietaria chilena para exposicion del codigo como portafolio.
- `1.1.11`: operacion PostgreSQL reforzada con restauracion aislada, pruebas, comparacion, monitoreo, deploy y ETL de integracion.
- `1.1.11a`: backup PostgreSQL automatico diario con bloqueo concurrente, verificacion, retencion y log operativo.
- `1.1.11b`: usuarios nominales creados, credenciales administrativas rotadas y matriz de los cuatro roles validada.
- `1.2.0` (en preparacion): frontend nativo Next.js, API Django v1, escritorio Electron, reportes, ETL, administracion y experiencia movil implementados.
- `1.2.1`: suite Django completa validada con 51 pruebas sobre PostgreSQL temporal aislado.

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
- [x] v1.1.2 - Implementar y probar restauracion PostgreSQL con `pg_restore` en una base aislada
- [x] v1.1.3 - Adaptar la pantalla, estado del sistema y permisos de backups para PostgreSQL
- [x] v1.1.4 - Mover credenciales PostgreSQL a variables de entorno obligatorias y retirar valores sensibles del codigo

### Prioridad alta

- [x] v1.1.5 - Ejecutar y adaptar toda la suite automatizada usando PostgreSQL
- [x] v1.1.6 - Comparar automaticamente conteos, sumas y reglas de negocio entre SQLite y PostgreSQL
- [x] v1.1.7 - Crear usuarios nominales, rotar credenciales administrativas y validar los cuatro roles
- [x] v1.1.8 - Preparar ejecucion productiva con WSGI, servicio persistente, HTTPS y `DEBUG=false`
- [x] v1.1.9 - Definir monitoreo de conexion, espacio, rendimiento, logs y fallos de backup

### Prioridad media

- [x] v1.1.10 - Programar limpieza y retencion de archivos sensibles en `uploads/`
- [x] v1.1.11 - Ampliar pruebas de integracion ETL con archivos pequenos representativos y errores por fila/columna
- [ ] v1.1.12 - Validar reglas oficiales de remuneraciones y clasificacion de items con el area de negocio
- [x] v1.1.13 - Evaluar cola de trabajos dedicada si las cargas simultaneas superan el proceso background actual

### Evolucion funcional posterior

- [ ] v1.2.5 - Contabilidad: aprobacion/contabilizacion/anulacion auditada, cierres y exportacion formal de asientos
- [ ] v1.2.6 - Inventario: documentos de recepcion/despacho/ajuste, kardex valorizado, reversas y cierres
- [ ] v1.2.7 - Compras y ventas: integracion idempotente con stock y contabilidad segun reglas aprobadas
- [ ] v1.2.8 - Reportes: PDF server-side para documentos de formato fijo, versionados y auditados
- [ ] v1.2.9 - IA local: servicio LAN separado para un unico caso de uso aprobado y de solo lectura

La revision tecnica, dependencias, decisiones de negocio y criterios de cierre se detallan en `docs/24_REVISION_EVOLUCION_FUNCIONAL.md`.

## v1.2 - Frontend real multiplataforma (en preparacion)

### Experiencia web y escritorio

- [x] Frontend nativo en Next.js y TypeScript, sin incrustar las vistas HTML de Django
- [x] Inicio de sesion, sesion autenticada y cierre de sesion conectados al backend
- [x] Navegacion y operaciones CRUD para remuneraciones, asistencia, contabilidad, inventario, compras y ventas
- [x] API Django v1 para sesion, catalogos, recursos, reportes, cargas ETL y administracion de usuarios
- [x] Empaquetado Electron con servidor Next.js standalone y dependencias incluidas
- [x] Diseno responsive con menu movil, tablas en tarjetas y formularios adaptados a smartphone

### Reportes, ETL y administracion

- [x] Reportes nativos de remuneraciones, asistencia, contabilidad, inventario y comercio
- [x] Graficos y filtros por modulo
- [x] Estilos de impresion para guardar o imprimir los reportes como PDF desde el navegador
- [x] Carga masiva conectada al proceso ETL existente, con historial, estado y descargas
- [x] Administracion de usuarios, roles y estados restringida al modulo de seguridad
- [x] Acceso LAN del frontend mediante `0.0.0.0`, manteniendo Django detrás del proxy de Next.js

### Validacion pendiente antes de publicar v1.2.0

- [x] `manage.py check`
- [x] ESLint, comprobacion TypeScript y build de produccion del frontend
- [x] Verificacion funcional de endpoints de reportes, usuarios, cargas y filtros
- [x] v1.2.1 - Ejecutar la suite Django completa en una base PostgreSQL temporal aislada: 51 pruebas OK
- [ ] v1.2.2 - Probar el AppImage generado en un equipo limpio y validar actualizacion/reinstalacion
- [ ] v1.2.3 - Validar navegacion completa desde al menos un smartphone real en la red local
- [ ] v1.2.4 - Aplicar y validar HTTPS y reglas de firewall del servidor antes de cualquier exposicion fuera de la LAN

## Proximo paso recomendado

Completar `v1.2.2` con la prueba del AppImage en un equipo limpio y continuar con la validacion fisica en smartphone para `v1.2.3`. La configuracion de despliegue HTTPS queda preparada, pero `v1.2.4` solo puede cerrarse al aplicarla con dominio, certificado y acceso administrativo reales. En paralelo, cerrar `v1.1.12` con la aprobacion formal del area de remuneraciones.
