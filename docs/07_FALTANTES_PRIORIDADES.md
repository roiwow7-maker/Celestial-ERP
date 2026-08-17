# Faltantes y prioridades

Fecha de referencia: 2026-08-16

Este documento conserva la evaluacion posterior a `1.0.8`. Para prioridades vigentes `1.2.x`, consultar `ROADMAP.md`, `23_VALIDACION_FRONTEND_1_2.md` y `24_REVISION_EVOLUCION_FUNCIONAL.md`.

## Versionado inmediato

- Version actual: `1.2.1`.
- `0.4.13`: validacion funcional con usuarios nominales de cada rol completada.
- `0.4.14`: politica formal de retencion/restauracion de backups completada.

## Alta prioridad

| Falta | Estado | Siguiente accion |
| --- | --- | --- |
| Validacion AppImage | Pendiente `1.2.2` | Ejecutar en un Linux limpio y validar reemplazo/reinstalacion. |
| Validacion smartphone | Pendiente `1.2.3` | Probar menu, formularios, tablas, filtros y graficos en dispositivo real. |
| HTTPS y firewall | Preparado `1.2.4` | Aplicar con dominio, certificado y acceso administrativo reales. |

## Media prioridad

| Falta | Estado | Siguiente accion |
| --- | --- | --- |
| Suite PostgreSQL | Completado | 51 pruebas correctas en cluster temporal aislado. |
| PostgreSQL | Completado | Base principal desde `1.0.10`; mantener backups y monitoreo. |
| Cargas asincronicas | Completado base | Existe proceso background simple con estado por corrida; queda pendiente cola real si escala. |
| Bootstrap local/offline | Completado | Bootstrap 5.3.3 queda servido desde `static/vendor/bootstrap/`. |
| IA local | Exploratorio futuro | Postergar a v1.0.x como servicio LAN separado con modelo cuantizado via API local. |

## Baja prioridad

| Falta | Estado | Siguiente accion |
| --- | --- | --- |
| Contabilidad avanzada | Base completada | Validar plan con contador, exportar asientos si se requiere y agregar cierres/aprobaciones. |
| Inventario avanzado | Base completada | Agregar kardex/cierres/documentos solo si la operacion lo exige. |
| Compras y ventas avanzado | Base completada | Integrar stock/contabilidad solo cuando existan reglas de despacho, recepcion y facturacion. |
| PDF nativo | No iniciado | Hoy se usa impresion del navegador; evaluar PDF server-side si se necesita formato fijo. |

## Riesgos

- HTTPS/firewall aun requieren aplicacion en el servidor definitivo.
- Las reglas oficiales de remuneraciones requieren aprobacion formal del area de negocio.
- Las cargas ETL largas ya tienen modo background simple; queda pendiente una cola real si el volumen crece.
- Los archivos en `uploads/` pueden contener datos sensibles.
- La carga individual aun no es formulario manual real; solo declara alcance por ficha dentro del flujo de archivo.

## Recomendacion de proxima version

La secuencia vigente es `1.2.2-1.2.4` para validaciones externas y `1.2.5-1.2.9` para contabilidad avanzada, inventario documental, integracion comercial, PDF fijo e IA local aprobada.
