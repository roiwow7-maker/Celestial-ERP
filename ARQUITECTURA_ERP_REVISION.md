# Revision arquitectura Celestial ERP

Fecha: 2026-07-13

## Criterio de despliegue

El sistema no esta pensado para internet. El objetivo es uso local o red interna controlada.

Esto cambia las prioridades:

- No se prioriza exposicion publica.
- Si se prioriza uso multiusuario real.
- Si se prioriza respaldo automatico.
- Si se prioriza control de permisos.
- Si se prioriza trazabilidad de acciones.

## Estado actual

Arquitectura activa:

- `Applet`: portal, navegacion, seguridad inicial, auditoria, backups y estado.
- `DATA_scope`: remuneraciones, ETL, dashboard, reportes y cargas.
- `Accounting`: plan de cuentas, centros de costo, mapeos, asientos y reportes.
- `Inventory`: productos, bodegas, stock, movimientos y valorizacion.
- `Commerce`: proveedores, clientes, compras, ventas y reportes comerciales.
- `Attendance`: asistencia historica diaria, mensual y por trabajador.
- `ERP_api`: endpoints JSON iniciales.
- SQLite local: valido para prototipo y operacion local controlada.

## Backup automatico

Se deja activo un backup automatico cada 90 minutos.

Configuracion:

- `ERP_AUTO_BACKUP_ENABLED`: default `true`.
- `ERP_AUTO_BACKUP_INTERVAL_MINUTES`: default `90`.

El backup automatico reutiliza el comando existente:

```powershell
python manage.py backup_sqlite
```

## Multiusuario real

Para multiusuario real en red interna, SQLite puede funcionar en pruebas controladas, pero no es la base recomendada para operacion sostenida con varios usuarios editando/cargando datos.

Recomendacion por etapas:

1. Mantener SQLite mientras se termina funcionalidad.
2. Aplicar login obligatorio y permisos por rol.
3. Medir uso real de cargas/reportes.
4. Postergar PostgreSQL hasta el final de v1.0.x si no existe servidor autorizado.

## Navegacion de remuneraciones

Ruta principal:

- `/remuneraciones/`

Pantallas recomendadas proximas:

- Trabajadores.
- Detalle de trabajador.
- Periodos.
- Detalle de liquidacion.
- Items de remuneracion.
- Validaciones de liquidacion.

## Estados de empleados

Se recomienda agregar un estado operativo al trabajador.

Estados sugeridos:

- Activo.
- Inactivo.
- Finiquitado.
- Pendiente de revision.

Regla inicial posible:

- Si `fecha_retiro` tiene valor: `Finiquitado`.
- Si no tiene `fecha_retiro`: `Activo`.
- Si faltan datos clave: `Pendiente de revision`.

No se implementa aun para evitar tocar modelo de remuneraciones sin una regla aprobada.

## Carga de datos

Ya existe carga masiva por ETL:

- Excel historico.
- CSV transformado.
- Importacion a ERP.

Falta carga individual:

- Crear trabajador individual.
- Editar datos de trabajador.
- Crear o corregir una liquidacion puntual.
- Agregar item/movimiento puntual con auditoria.

Recomendacion:

1. Mantener carga masiva en `DATA_scope`.
2. Crear carga individual como pantallas especificas de remuneraciones.
3. Auditar cada cambio individual en `AuditLog`.
4. Restringir carga individual a roles autorizados.

## Proxima prioridad

La prioridad posterior a v1.0.3 debe enfocarse en:

- Backups reales con restauracion validada `v1.0.4`.
- Auditoria validada por usuario/rol `v1.0.5`.
- Reglas avanzadas de integracion entre compras/ventas, inventario y contabilidad.
- IA local cuantizada como servicio LAN separado.
- PostgreSQL al final de v1.0.x, solo cuando existan permisos e infraestructura.
