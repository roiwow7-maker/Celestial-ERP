# Documentacion tecnica ampliada - Celestial ERP

Fecha de referencia: 2026-07-13

Version documentada: `1.0.8`

Esta carpeta contiene documentacion detallada de todo lo que vive en la carpeta `ETL`. Se deja aqui por solicitud operativa, junto a los assets existentes de diagramas.

## Indice

- `00_mapa_carpeta_etl.md`: inventario de carpetas y archivos principales del workspace.
- `01_version_y_estado.md`: version actual, hitos cerrados y estado funcional.
- `02_arquitectura_django.md`: estructura Django, settings, apps, middleware y templates base.
- `03_modulos_rutas_y_api.md`: rutas HTML y endpoints JSON.
- `04_modelos_datos_y_formularios.md`: modelos, relaciones, formularios y admins.
- `05_pipeline_etl.md`: scripts ETL de raiz, entradas, salidas y flujo completo.
- `06_operacion_comandos.md`: comandos `manage.py`, scripts PowerShell, backups, logs y validaciones.
- `07_ui_bootstrap_admin.md`: Bootstrap local, tema claro/oscuro, navbar flotante y Django Admin.
- `08_seguridad_roles_permisos.md`: login, roles, permisos, auditoria y credenciales.
- `09_datos_generados_y_archivos.md`: CSV, Excel, uploads, backups, reports, logs y datos sensibles.
- `10_mantenimiento_roadmap.md`: mantenimiento, riesgos, pendientes y roadmap reordenado.
- `../14_ASISTENCIA.md`: detalle funcional del modulo de asistencia.

## Diagramas

- `arquitectura_general.svg`
- `flujo_etl.svg`

## Regla de mantenimiento

Cuando cambie una ruta, modelo, comando o version visible del sistema, actualizar primero el codigo y despues estos documentos. La version central vive en `Celestial_ERP/Applet/services.py` como `ERP_VERSION`.

