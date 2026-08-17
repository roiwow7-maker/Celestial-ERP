# Documentacion Celestial ERP

Esta carpeta contiene documentacion especifica por modulo y una guia general del sistema.

> Estado vigente: `1.2.1`. Comenzar por `25_ESTADO_ACTUAL_1_2_1.md`. Los documentos de SQLite y versiones `0.x`/`1.0.x` se conservan como historial y no describen la base productiva actual.

## Archivos principales

- `INDICE_DOCUMENTACION.md`: indice maestro ordenado de toda la documentacion propia del proyecto.
- `00_DOCUMENTACION_GENERAL.md`: vision completa de la plataforma.
- `01_APPLET_PORTAL.md`: portal principal, navegacion, seguridad, auditoria y backups.
- `02_DATA_SCOPE_REMUNERACIONES.md`: modulo de remuneraciones, reportes y cargas.
- `03_ETL_PIPELINE.md`: flujo ETL historico y archivos generados.
- `04_API.md`: endpoints JSON disponibles.
- `05_ADMIN_MULTIUSUARIO.md`: administracion, roles y uso multiusuario interno.
- `06_OPERACION_LOCAL_BACKUPS.md`: operacion local/red interna y politica formal de retencion/restauracion de backups.
- `07_FALTANTES_PRIORIDADES.md`: faltantes reales y prioridades recomendadas despues de v0.4.
- `08_IDEAS_MODULOS_FUTUROS.md`: ideas y alcance posible para contabilidad, inventario, compras, ventas, configuracion e integraciones.
- `09_UI_BOOTSTRAP.md`: integracion Bootstrap, navbar flotante, tema visual y patrones de templates.
- `10_V06_OPERACION_LIMITADA_IA_LOCAL.md`: avance v0.6 sin PostgreSQL, settings separados, logs, SQLite temporal y proyeccion posterior de servidor LAN con IA local.
- `11_CONTABILIDAD.md`: modulo contable v0.7 con plan de cuentas, centros de costo, mapeos, asientos y reportes.
- `12_INVENTARIO.md`: modulo de inventario v0.8 con productos, bodegas, stock, movimientos y valorizacion.
- `13_COMPRAS_VENTAS.md`: modulo comercial v0.9 con proveedores, clientes, compras y ventas.
- `14_ASISTENCIA.md`: modulo de asistencia v0.9.6C con registros diarios, historico por trabajador, reporte mensual y exportacion.
- `15_OPERACION_SQLITE_SIN_POSTGRESQL.md`: operacion reforzada sobre SQLite mientras PostgreSQL queda postergado al final del roadmap.
- `16_TESTING_AMPLIO.md`: suite de validacion para cerrar versiones.
- `17_DOCUMENTACION_OPERATIVA_CERRADA.md`: documentos y rutina operativa base.
- `18_DEPLOY_LAN.md`: despliegue local/red interna controlada.
- `19_V10_PRE_POSTGRESQL_IA_BACKUPS.md`: cierre v1.0.4-v1.0.8 con backups restaurables, auditoria por rol, plan de migracion, IA local separada y PostgreSQL preparado.
- `20_POSTGRESQL_NGINX_NEXTJS.md`: arquitectura PostgreSQL, Django, Next.js y nginx; incluye decisiones historicas y actuales.
- `21_PLAN_FRONTEND_REAL.md`: plan del frontend y estado de cumplimiento.
- `22_OPERACION_POSTGRESQL_PRODUCCION.md`: operacion y despliegue productivo preparado.
- `23_VALIDACION_FRONTEND_1_2.md`: pruebas externas pendientes para AppImage, smartphone y HTTPS.
- `24_REVISION_EVOLUCION_FUNCIONAL.md`: analisis de los siguientes modulos avanzados.
- `25_ESTADO_ACTUAL_1_2_1.md`: resumen canonico vigente.
- `MANUAL_COMPLETO_CELESTIAL_ERP.md`: manual consolidado de uso, implementacion, gestion interna, ETL, operacion y seguridad.
- `Celestial_ERP_Manual_Completo.pdf`: version PDF del manual consolidado.
- `Celestial_ERP_Manual_Completo.html`: version imprimible desde navegador.
- `../version_log.md`: bitacora historica de versiones desde `0.0.1` hasta el estado actual.
- `Celestial_ERP_Documentacion.ipynb`: notebook de lectura ejecutiva.
- `Celestial_ERP_Documentacion_General.pdf`: version PDF general, si fue generada.

## Documentacion ampliada en assets

Por solicitud operativa, `assets/` contiene tambien una documentacion tecnica ampliada de toda la carpeta `ETL`:

- `assets/README.md`: indice de la documentacion ampliada.
- `assets/00_mapa_carpeta_etl.md`: mapa del workspace.
- `assets/01_version_y_estado.md`: version y estado actual `1.2.1`.
- `assets/02_arquitectura_django.md`: arquitectura Django.
- `assets/03_modulos_rutas_y_api.md`: rutas y API.
- `assets/04_modelos_datos_y_formularios.md`: modelos, formularios y admin.
- `assets/05_pipeline_etl.md`: pipeline ETL.
- `assets/06_operacion_comandos.md`: comandos operativos.
- `assets/07_ui_bootstrap_admin.md`: UI Bootstrap y Django Admin.
- `assets/08_seguridad_roles_permisos.md`: seguridad, roles y permisos.
- `assets/09_datos_generados_y_archivos.md`: datos generados y archivos sensibles.
- `assets/10_mantenimiento_roadmap.md`: mantenimiento y roadmap.

## Documentos historicos fuera de docs

Algunos documentos historicos siguen en la raiz de `ETL` por compatibilidad con el flujo de trabajo:

- `ROADMAP.md`
- `version_log.md`
- `DOCUMENTACION_GENERAL_APLICACION.md`
- `EVALUACION_SISTEMA.md`
- `ARQUITECTURA_ERP_REVISION.md`
- `REGLAS_NEGOCIO_REMUNERACIONES.md`
- `identificacion_items_inicial.md`
- `mapeo_carga_liquidaciones.md`

Todos quedan enlazados desde `INDICE_DOCUMENTACION.md`.

## Diagramas

Los diagramas estan en `assets/` como SVG para poder abrirlos desde navegador, Markdown o editores.
