# Documentacion general de la aplicacion

Fecha de referencia: 2026-07-13

Celestial ERP es una aplicacion local/red interna para gestionar datos historicos de remuneraciones y operacion ERP inicial. Combina un pipeline ETL en Python con una webapp Django. La version funcional actual es `1.0.3`.

## Que hace hoy

- Transforma archivos historicos de payroll desde Excel/CSV.
- Clasifica items de remuneracion por categoria.
- Genera CSV por categoria y CSV equivalentes a liquidaciones.
- Puede generar un Excel final de liquidaciones.
- Importa trabajadores, periodos, items, movimientos y liquidaciones a Django.
- Muestra dashboard, reportes, trabajadores, cargas y tableros Kanban.
- Exige login obligatorio.
- Aplica roles y permisos por modulo.
- Registra eventos de auditoria.
- Ejecuta backups SQLite manuales y automaticos con verificacion y retencion.
- Procesa cargas largas en segundo plano con estado por corrida.
- Exporta CSV por trabajador, periodo y liquidacion.
- Opera una base contable inicial con plan de cuentas, centros de costo, mapeos, asientos y reportes.
- Opera inventario inicial con productos, bodegas, stock, movimientos y valorizacion.
- Opera comercio inicial con proveedores, clientes, compras, ventas y reportes comerciales.
- Opera asistencia historica con registros diarios, reporte mensual, exportacion CSV e impresion/PDF.
- Mantiene logs persistentes de aplicacion y ETL.
- Expone una API JSON interna protegida.

## Acceso

Rutas principales:

- `/login/`: login.
- `/applet/`: portal principal.
- `/remuneraciones/`: dashboard de remuneraciones.
- `/remuneraciones/trabajadores/`: trabajadores y estados.
- `/reportes/`: reportes.
- `/cargas/`: carga ETL.
- `/applet/security/`: roles y usuarios.
- `/applet/audit/`: auditoria.
- `/applet/backups/`: backups.
- `/contabilidad/`: dashboard contable.
- `/inventario/`: dashboard de inventario.
- `/comercio/`: dashboard de compras y ventas.
- `/asistencia/`: dashboard de asistencia.
- `/admin/`: Django Admin.
- `/api/`: API interna.

Usuario local de desarrollo:

- Usuario: `root`
- Clave: `root`

Debe cambiarse antes de uso compartido.

## Roles

Roles funcionales:

- Administrador.
- RRHH.
- Contabilidad.
- Solo lectura.

Permisos principales:

- Acceso a administracion.
- Acceso a seguridad/auditoria.
- Ejecutar backups.
- Acceso a remuneraciones.
- Cambiar estados de trabajadores.
- Subir archivos ETL.
- Importar datos al ERP.
- Limpiar datos antes de importar.
- Descargar salidas de cargas.
- Acceso y gestion de contabilidad.
- Acceso y gestion de inventario.
- Acceso y gestion de compras/ventas.
- Acceso y gestion de asistencia.

Comando de preparacion:

```powershell
python manage.py setup_access_control
```

## Datos actuales

- Usuarios: 1.
- Trabajadores: 517.
- Periodos: 114.
- Items: 131.
- Movimientos: 276253.
- Liquidaciones: 19719.
- Importaciones auditadas: 4.
- Eventos de auditoria: 41.

## Modelos principales

- `Employee`: trabajadores y estado.
- `PayrollPeriod`: periodos.
- `PayrollItem`: items/codigos de remuneracion.
- `PayrollEntry`: movimientos.
- `PayrollSummary`: liquidaciones.
- `ImportRun`: corridas ETL.
- `AuditLog`: eventos auditados.
- `ChartAccount`, `CostCenter`, `JournalEntry`: base contable.
- `Product`, `Warehouse`, `StockBalance`, `StockMovement`: inventario.
- `Supplier`, `Customer`, `PurchaseOrder`, `SalesOrder`: compras y ventas.
- `AttendanceRecord`: asistencia por trabajador y fecha.

Estados de trabajador:

- Activo.
- Inactivo.
- Finiquitado.
- Pendiente revision.

## ETL

Archivos principales:

- `run_etl.py`: orquestador.
- `dataload.py`: transformacion base.
- `tabcreated.py`: CSV por categoria.
- `build_liquidaciones_csvs.py`: CSV equivalentes.
- `transfer_liquidaciones_to_excel.py`: Excel final.
- `DATA_scope/management/commands/import_payroll_data.py`: importacion a Django.

Entradas aceptadas:

- `.xlsx`
- `.xls`
- `.csv`

Salidas:

- `transformed.csv`
- `csv_por_categoria/`
- `csv_equivalentes_liquidaciones/`
- `Liquidaciones_Historicas_Cargadas.xlsx`
- `uploads/<timestamp>/` para cargas web.

## Faltantes importantes

- Recalculo automatico de liquidaciones al editar movimientos.
- Auditoria granular avanzada con filtros por objeto.
- Integracion avanzada entre compras/ventas, inventario y contabilidad.
- Preparacion final de PostgreSQL al final de v1.0.x, cuando exista un servidor autorizado.
- Proyeccion de IA local cuantizada en v1.0.x como servicio separado.

## Comandos utiles

```powershell
python manage.py check
python manage.py test Applet DATA_scope ERP_api Accounting Inventory Commerce Attendance
python manage.py setup_access_control
python manage.py check_sqlite_operational_health
python manage.py backup_sqlite
python manage.py cleanup_uploads --dry-run
python manage.py validate_business_rules
```

## Estado recomendado

La base v1.0.3 deja activos Remuneraciones, Contabilidad, Inventario, Compras/Ventas, Asistencia, operacion SQLite reforzada, auditoria granular, sincronizacion asistencia-remuneraciones, testing ampliado y deploy LAN documentado. PostgreSQL se mantiene al final de v1.0.x para respetar las limitaciones actuales de permisos y hardware; la IA local cuantizada queda proyectada para v1.0.x como servicio separado en servidor LAN.
