# Version y estado del sistema

Fecha de referencia: 2026-07-13

Version actual: `1.0.8`

## Donde vive la version

La version central del sistema vive en:

```text
Celestial_ERP/Applet/services.py
```

Constante:

```python
ERP_VERSION = "1.0.8"
```

## Donde se muestra

| Lugar | Detalle |
| --- | --- |
| Navbar web | `Celestial_ERP/Applet/templates/shared/topbar.html` muestra `v1.0.8`. |
| Django Admin | `Applet/admin.py` configura `site_header`, `site_title` e `index_title` con `v1.0.8`. |
| API | `ERP_api/views.py` expone la version en `/api/`, `/api/health/` y `/api/system-status/`. |
| Documentacion | `ROADMAP.md`, `version_log.md` y documentos en `docs/` mencionan `1.0.8`. |

## Estado funcional cerrado en v0.6.8

- Separacion de configuracion desarrollo/produccion.
- Preparacion de variables sensibles y operacion sin claves temporales conocidas.
- Bootstrap local/offline sin CDN.
- Logs persistentes rotativos.
- Procesamiento background simple para cargas largas.
- Backup SQLite con verificacion y retencion simple.
- Diagnostico de seguridad operativa.
- Exportaciones CSV por trabajador, periodo y liquidacion.

## Estado funcional cerrado en v0.7.5a

- Plan de cuentas.
- Centros de costo.
- Mapeos item remuneracion a cuenta contable.
- Asientos contables desde remuneraciones por periodo.
- Reportes contables iniciales.
- Reportes de remuneraciones con graficos laterales y listas con scroll vertical.

## Estado funcional cerrado en v0.8.4

- Catalogo de productos.
- Bodegas y saldos de stock.
- Movimientos de entrada, salida y ajuste.
- Valorizacion por costo promedio.
- Navbar, API, permisos, admin y pruebas automaticas de Inventario.

## Estado funcional cerrado en v0.9.6C

- Compras y ventas base cerradas en `v0.9.4`.
- Asistencia historica por trabajador y fecha.
- Registros con entrada, salida, descanso, estado, fuente y notas.
- Reporte mensual por trabajador.
- Exportacion CSV e impresion/PDF desde navegador.
- Navbar, API, permisos, admin y pruebas automaticas de Asistencia.

## Estado funcional cerrado en v0.9.7

- Operacion local reforzada sobre SQLite.
- Comando `check_sqlite_operational_health`.
- Diagnostico de integridad, WAL, backups, uploads y conteos base.
- PostgreSQL movido al final del roadmap.

## Estado funcional cerrado en v0.9.8-v1.0.8

- Auditoria granular con objeto, id, representacion y cambios JSON.
- Filtros de auditoria por modulo, accion, objeto, id y texto.
- Sincronizacion asistencia-remuneraciones por periodo.
- Testing amplio con 41 pruebas automaticas.
- Documentacion operativa cerrada.
- Deploy local/red interna documentado.

## Roadmap vigente

| Linea | Estado |
| --- | --- |
| `v0.6.x` | Cerrada como base operativa robusta sin PostgreSQL. |
| `v0.7.x` | Cerrada como base contable inicial. |
| `v0.8.x` | Cerrada como base inicial de inventario. |
| `v0.9.x` | Compras/ventas, asistencia, SQLite reforzado, auditoria e integracion asistencia-remuneraciones cerradas. |
| `v1.0.x` | Testing, documentacion operativa, deploy LAN, backups restaurables y auditoria por rol cerrados hasta `v1.0.8`; PostgreSQL queda al final. |
| `v1.0.x` | Version estable, despliegue LAN, proyeccion IA local cuantizada y preparacion PostgreSQL documentada. |

## Decision sobre PostgreSQL

La preparacion final de PostgreSQL fue movida al final de `v1.0.x` porque el equipo actual tiene limitaciones de permisos y recursos. Mientras tanto, SQLite queda permitido para operacion local/controlada, con backups frecuentes y sin multiusuario intensivo.

## Decision sobre IA local

La IA local cuantizada queda planificada desde `v1.0.7` como servicio separado en servidor LAN. No se mezcla con la base operativa actual para evitar sobrecargar este equipo.

