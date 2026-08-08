# Faltantes y prioridades

Fecha de referencia: 2026-07-13

Este documento resume lo que falta despues de cerrar la base v1.0.8.

## Versionado inmediato

- Version actual: `1.0.8`.
- `0.4.13`: validacion funcional con usuarios nominales de cada rol completada.
- `0.4.14`: politica formal de retencion/restauracion de backups completada.

## Alta prioridad

| Falta | Estado | Siguiente accion |
| --- | --- | --- |
| Backups reales con restauracion validada | Pendiente | Probar restauracion calendarizada en copia local/LAN. |

## Media prioridad

| Falta | Estado | Siguiente accion |
| --- | --- | --- |
| Ampliar tests de permisos | Parcial | Agregar pruebas de mas flujos POST y cargas con archivos reales. |
| PostgreSQL | Postergado al final de v1.0.x | Preparar migracion cuando exista servidor/permisos. |
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

- SQLite no es ideal para concurrencia sostenida.
- La clave `root/root` es solo local y debe cambiarse.
- Las cargas ETL largas ya tienen modo background simple; queda pendiente una cola real si el volumen crece.
- Los archivos en `uploads/` pueden contener datos sensibles.
- La carga individual aun no es formulario manual real; solo declara alcance por ficha dentro del flujo de archivo.

## Recomendacion de proxima version

La siguiente version deberia avanzar con los pendientes que aun requieren servidor autorizado o validacion periodica:

1. Ensayo de migracion SQLite a PostgreSQL en servidor autorizado.
2. Migracion real a PostgreSQL solo con infraestructura, permisos y ventana de mantenimiento.
3. Cola real de trabajos si las cargas crecen.
4. Validacion LAN recurrente con usuarios nominales reales.
5. Pruebas periodicas de restauracion con backup reciente.
