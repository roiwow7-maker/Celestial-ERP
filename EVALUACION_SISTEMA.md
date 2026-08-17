# Evaluacion del sistema

Fecha de referencia: 2026-07-13

> Revision historica. Desde esta evaluacion se completaron PostgreSQL, settings separados, usuarios nominales, backups/restauracion, 51 pruebas y frontend Next.js/Electron. Estado vigente: `docs/25_ESTADO_ACTUAL_1_2_1.md`.

## 1. Criterio de evaluacion

Clasificacion usada:

- Fuerte: funciona bien, aporta valor y puede mantenerse con ajustes menores.
- Medio: funciona o esta encaminado, pero requiere mejoras antes de escalar.
- Debil: tiene riesgo operativo, tecnico o de mantenimiento relevante.
- Catastrofico: puede bloquear el uso real del sistema, producir errores graves, perdida de datos o exposicion de informacion sensible.

## 2. Resumen general

El sistema evoluciono desde una base ETL y admin Django hacia un ERP Django/PostgreSQL con frontend Next.js/Electron. La version vigente es `1.2.1`. HTTPS productivo y reglas oficiales de negocio siguen dependiendo de infraestructura y aprobacion externa.

## 3. Evaluacion por item

| Item | Estado | Evaluacion | Riesgo principal | Accion recomendada |
| --- | --- | --- | --- | --- |
| Modelo de datos ERP | Fuerte | Los modelos cubren trabajadores, periodos, items, movimientos y resumenes. Hay indices y restricciones unicas importantes. | Puede faltar normalizacion futura para empresas, contratos, centros de costo o multiempresa. | Mantener estructura actual y extender solo cuando exista caso de uso real. |
| Carga historica a Django | Fuerte | El comando `import_payroll_data` usa bulk inserts y transacciones. Buena base para cargas grandes. | Si cambia el formato CSV, puede fallar por nombres de columnas. | Agregar validacion previa de columnas y reporte de errores. |
| Validacion de montos y filas | Fuerte | Los archivos de validacion muestran consistencia entre Excel y CSV. | Las validaciones actuales no cubren todas las reglas de negocio. | Expandir validaciones por trabajador, periodo, categoria y totales esperados. |
| Clasificacion de items | Medio | Existe una clasificacion amplia por categorias y una marca `requiere_confirmacion`. | Algunos codigos podrian estar mal clasificados si no hay catalogo oficial. | Crear maestro oficial de conceptos con versionado y aprobacion. |
| Pipeline ETL | Fuerte | `run_etl.py` ejecuta transformacion, separacion, generacion de CSV, Excel e importacion; tambien acepta entrada XLS/XLSX/CSV y rutas de salida configurables. | Falta enriquecer reportes de calidad en la orquestacion. | Agregar reporte final consolidado con tiempos, archivos y validaciones por fila. |
| Dashboard web | Fuerte | Existe una portada web funcional con metricas, accesos a reportes, cargas, admin y modulos ERP base. | Aun requiere reglas de aprobacion/cierre para operacion formal. | Mantenerlo como entrada operativa y sumar alertas de calidad. |
| Reportes web | Fuerte | Hay reportes con KPIs, filtros por periodo, graficas con scroll interno, tabla, CSV e impresion/PDF por navegador. | Las graficas son HTML/CSS sin libreria estadistica avanzada. | Agregar reportes por trabajador, division, item y comparativos. |
| Carga web de archivos | Fuerte | Permite subir CSV, XLSX y XLS, ejecutar ETL y descargar salidas por corrida. Tiene procesamiento background simple con estado por corrida. | Una cola real puede ser necesaria si escala el volumen. | Mantener modo background y evaluar cola dedicada solo si crece el uso. |
| Prueba de rutas | Fuerte | Existe `/cargas/probar-rutas/` para verificar rutas principales del sistema. | Solo comprueba disponibilidad de enlaces, no reglas funcionales. | Agregar prueba de salud con conteos y checks de archivos requeridos. |
| Django Admin | Medio | Permite operar datos rapidamente sin crear pantallas propias. | No es una interfaz final para usuarios administrativos no tecnicos. | Usarlo como respaldo interno y construir vistas ERP dedicadas. |
| Base SQLite | Medio | Correcta para prototipo local y pruebas. | Puede quedar corta para concurrencia, red local, respaldos y multiusuario. | Migrar a PostgreSQL cuando se pase a uso real. |
| Instalacion sin permisos admin | Medio | El sistema puede correr con Python local; no requiere Node para el ERP web actual. | PostgreSQL, servicios de Windows o despliegue permanente pueden requerir permisos. | Usar ejecucion local, PostgreSQL portable/remoto o solicitar permisos para servicio formal. |
| Configuracion Django | Medio | Acepta variables para hosts, debug, secret key y cookies seguras. Tambien genera clave local fuera del codigo. | Faltan settings separados para desarrollo/produccion. | Crear `settings/base.py`, `settings/dev.py`, `settings/prod.py`. |
| Seguridad | Medio | `DEBUG` queda apagado por defecto, la clave fija fue reemplazada por env/local secret y cookies seguras se activan fuera de debug. | HTTPS y HSTS dependen de infraestructura externa. | Activar SSL/HSTS cuando exista reverse proxy o servidor autorizado. |
| Usuario administrador | Medio | Existen roles base (`ERP Lectura`, `ERP Operador ETL`, `ERP Administrador Datos`) y el admin local fue asociado al rol administrador. | La clave temporal debe rotarse y deben crearse usuarios nominales. | Usar `setup_access_control --admin-password` y crear usuarios individuales. |
| Encoding de textos | Fuerte | Se escanearon archivos `.py`, `.md` y `.csv` sin marcadores mojibake conocidos; los headers actuales se leen en UTF-8. | Nuevos archivos fuente podrian venir con encoding defectuoso. | Mantener validacion al ingresar nuevas fuentes. |
| Dependencias | Fuerte | `requirements.txt` declara Django, pandas y openpyxl con versiones exactas usadas por el entorno actual. | Cambios futuros de version deben probarse antes de actualizar. | Mantener upgrades controlados con pruebas. |
| Pruebas automatizadas | Fuerte | La suite `1.2.1` ejecuta 51 pruebas sobre PostgreSQL temporal e incluye integracion ETL representativa y API v1. | Faltan pruebas end-to-end en navegador y dispositivos externos. | Agregar E2E después de estabilizar los flujos `1.2.5-1.2.7`. |
| Manejo de errores ETL | Medio | El importador valida columnas antes de cargar; la carga web muestra salida y errores del proceso ETL. | Falta reporte estructurado por fila/columna en transformaciones previas. | Generar reporte de errores detallado en `run_etl.py`. |
| Auditoria | Fuerte | Existe modelo `ImportRun` con estado, hashes SHA-256, rutas, conteos y errores. | Aun no asocia cada fila importada a una corrida especifica. | Evaluar relacionar datos con corrida si se requiere trazabilidad completa. |
| Backups | Fuerte | Existe comando `backup_sqlite`, script `backup_erp.ps1`, backup automatico y politica documentada de retencion/restauracion. | Falta validar restauracion periodica en ambiente real. | Probar restauracion con calendario operativo. |
| Rendimiento futuro | Medio | Bulk create y relaciones indexadas ayudan bastante. | Consultas agregadas grandes pueden volverse lentas con mas historico. | Agregar indices, vistas materializadas o tablas resumen si crece el volumen. |
| Integridad de negocio | Medio | Hay documento de reglas y comando `validate_business_rules`; la ultima revision compara `Sueldo Liquido*` contra `A000`, descrito como Sueldo Liquido. Hay 19359 liquidaciones con A000 y 360 sin A000 en 0. | Falta aprobacion funcional/legal para liquidaciones sin A000 y formulas finales. | Validar reglas con negocio y marcar version aprobada. |
| Produccion web | Medio | Se redujeron riesgos de configuracion local, pero `runserver` sigue siendo solo desarrollo. | Produccion real requiere infraestructura fuera del alcance sin permisos. | Usar WSGI/ASGI productivo, reverse proxy, HTTPS y logs cuando exista ambiente autorizado. |
| Datos sensibles | Medio | Se mejoro configuracion base, se ignoran secretos/backups y se mantiene admin autenticado. | Falta control de roles de negocio y cifrado de transporte en red. | Crear perfiles de usuario y activar HTTPS en ambiente final. |
| Archivos subidos | Medio | Los archivos se guardan por corrida en `uploads/`, quedan fuera de git y existe `cleanup_uploads` para retencion. | Falta programar limpieza automatica y definir dias oficiales de retencion. | Agendar `cleanup_uploads --days N`. |
| Ausencia de permisos/infra formal | Catastrofico | Sin permisos, podria no ser posible instalar servicio, PostgreSQL o abrir puertos. | El ERP puede quedar solo como demo local. | Definir ambiente objetivo: local, red interna, servidor autorizado o nube. |

## 4. Puntos fuertes

- La transformacion historica ya esta avanzada.
- Los datos cargados tienen volumen real y estructura util.
- El modelo Django esta bien orientado al dominio de remuneraciones.
- Hay validaciones de filas y montos ya generadas.
- La carga a base usa transacciones y operaciones masivas.
- Ya existe servicio web local y admin operativo.
- Existen reportes web con graficas, CSV e impresion/PDF.
- Existe carga web de archivos integrada al ETL.
- Existe prueba de rutas principales.

## 5. Puntos medios

- El sistema funciona para prototipo local, pero no esta listo para produccion.
- El dashboard sirve como punto de entrada operativo a los modulos principales.
- Las cargas web funcionan con modo background simple.
- SQLite es suficiente para desarrollo, pero no para operacion multiusuario seria.
- Las reglas de clasificacion existen, pero requieren aprobacion funcional.
- La instalacion sin permisos es viable para desarrollo, pero limitada para despliegue.

## 6. Puntos debiles

No quedan items de la tabla principal en estado `Debil` que sean corregibles dentro del workspace sin permisos externos.

Riesgos residuales a vigilar:

- Falta probar restauracion periodica de backups en ambiente real.
- Falta reporte de errores ETL por fila y columna.
- Falta programar limpieza automatica de `uploads/`.
- Falta aprobar reglas oficiales con negocio.
- Falta crear usuarios nominales y rotar la clave temporal del admin local.

## 7. Puntos catastroficos

No quedan puntos catastroficos totalmente corregibles dentro del workspace sin permisos externos. Permanecen como bloqueos de infraestructura para produccion real:

1. No exponer `runserver` como produccion.
2. No abrir el sistema a internet sin HTTPS/reverse proxy.
3. No operar datos personales y salariales sin roles de negocio.
4. No depender de SQLite para operacion multiusuario real.

## 8. Priorizacion recomendada

### Prioridad 1: estabilidad y seguridad minima

- Cambiar credenciales temporales.
- Configurar `DJANGO_SECRET_KEY` en ambiente compartido.
- Mantener `DEBUG=false` para cualquier uso compartido.
- Definir `ALLOWED_HOSTS`.
- Programar backup automatico de `db.sqlite3`.
- Usar roles `ERP Lectura`, `ERP Operador ETL` y `ERP Administrador Datos`.

### Prioridad 2: confiabilidad del ETL

- Normalizar encoding.
- Mantener `run_etl.py` como entrada unica de ejecucion ETL.
- Ampliar validaciones previas y posteriores.
- Crear reporte de errores.
- Revisar cada corrida en `ImportRun`.
- Definir limpieza y retencion de `uploads/`.
- Ejecutar `validate_business_rules` despues de cargas relevantes.

### Prioridad 3: funcionalidad ERP

- Integracion compras/ventas con recepcion/despacho de inventario.
- Cierres o aprobaciones comerciales/contables.
- Exportacion adicional a Excel/PDF estructurado si se requiere.
- Integracion futura de asistencia con liquidaciones para dias trabajados, ausencias y horas.
- Filtros por periodo, trabajador, categoria e item.
- Procesamiento asincronico para cargas grandes.

### Prioridad 4: infraestructura

- Decidir ambiente objetivo.
- Evaluar PostgreSQL.
- Definir despliegue como servicio.
- Configurar logs.
- Preparar estrategia de respaldo y recuperacion.

## 9. Conclusion

El sistema es una buena base para un ERP local de remuneraciones con modulos operativos iniciales. Ya resolvio una parte dificil: transformar historicos complejos, cargarlos a una estructura relacional y abrir superficies web para operar. El siguiente salto no es agregar mas pantallas por agregar, sino cerrar confiabilidad: restauracion probada, reglas de aprobacion, PostgreSQL autorizado, despliegue LAN formal y pruebas de integracion con datos reales pequenos.
