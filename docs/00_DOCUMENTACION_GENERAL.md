# Celestial ERP - Documentacion general

Fecha de referencia: 2026-07-13

## Resumen ejecutivo

Celestial ERP es una plataforma local/red interna construida en Django para operar datos historicos de remuneraciones. El sistema nacio como un ETL de payroll y hoy incluye portal web, dashboard, reportes, carga controlada, auditoria, backups, API inicial y control de acceso por roles.

La version funcional actual es `1.0.8`. El foco de v0.5 fue operacion RRHH controlada, la linea `0.6.x` cerro la base operativa robusta sin PostgreSQL, `0.7.x` activo la base contable, `0.8.x` activo inventario, `0.9.x` activo compras/ventas, asistencia, SQLite reforzado, auditoria granular e integracion asistencia-remuneraciones, y `1.0.8` deja cerrados testing, documentacion, deploy LAN, backups restaurables, auditoria por rol, plan de migracion, IA local separada y preparacion PostgreSQL documentada.

## Estado actual de datos

| Area | Cantidad |
| --- | ---: |
| Usuarios | 1 |
| Grupos/Roles | 7 |
| Trabajadores | 517 |
| Periodos | 114 |
| Items de remuneracion | 131 |
| Movimientos | 276253 |
| Liquidaciones | 19719 |
| Importaciones ETL auditadas | 4 |
| Eventos de auditoria Applet | 41 |

## Modulos activos

| Modulo | Estado | Proposito |
| --- | --- | --- |
| Applet | Activo | Portal principal, navbar, launcher de modulos, seguridad, auditoria, backups, estado del sistema y Kanban ERP. |
| DATA_scope | Activo | Remuneraciones, trabajadores, dashboard, reportes, cargas ETL, Kanban operativo y modelos de payroll. |
| Accounting | Activo | Plan de cuentas, centros de costo, mapeos, asientos contables y reportes iniciales. |
| Inventory | Activo | Productos, bodegas, stock, movimientos y valorizacion. |
| Commerce | Activo | Proveedores, clientes, compras, ventas y reportes comerciales iniciales. |
| Attendance | Activo | Asistencia diaria, historico por trabajador, reporte mensual, exportacion CSV e impresion/PDF. |
| ERP_api | Activo inicial | Endpoints JSON de salud, estado, modulos, resumen payroll y periodos. |
| Django Admin | Activo | Administracion interna de usuarios, grupos, datos y auditoria. |

## Acceso y usuarios

El login es obligatorio para las vistas del portal, remuneraciones, herramientas y API interna.

Rutas:

| Ruta | Descripcion |
| --- | --- |
| `/login/` | Ingreso al sistema |
| `/logout/` | Salida de sesion via POST |
| `/admin/` | Django Admin |
| `/applet/` | Portal principal |

Usuario local de desarrollo creado:

| Usuario | Clave | Uso |
| --- | --- | --- |
| `root` | `root` | Superusuario local de desarrollo |

Esta clave es solo para ambiente local. Debe cambiarse antes de cualquier uso compartido.

## Roles y permisos

Roles funcionales:

| Rol | Alcance esperado |
| --- | --- |
| Administrador | Acceso total operativo, seguridad, backups, administracion y datos. |
| RRHH | Operacion de remuneraciones, cargas, importacion y estados de trabajadores. |
| Contabilidad | Lectura de remuneraciones y descarga de salidas autorizadas. |
| Solo lectura | Consulta de remuneraciones sin acciones sensibles. |

Permisos custom principales:

| Permiso | Proposito |
| --- | --- |
| `Applet.access_admin_module` | Acceso al modulo de administracion. |
| `Applet.access_security_module` | Acceso a seguridad y auditoria. |
| `Applet.run_backups` | Ejecutar backups manuales. |
| `DATA_scope.access_payroll_module` | Acceso al modulo de remuneraciones. |
| `DATA_scope.manage_employee_status` | Cambiar estados de trabajadores. |
| `DATA_scope.upload_payroll_data` | Subir archivos de remuneraciones. |
| `DATA_scope.import_payroll_data` | Importar datos al ERP. |
| `DATA_scope.clear_payroll_data` | Limpiar datos antes de importar. |
| `DATA_scope.download_upload_output` | Descargar salidas de cargas ETL. |

Comando para crear/actualizar roles:

```powershell
python manage.py setup_access_control
```

## Navegacion web

La navegacion principal esta en una navbar superior y se adapta a permisos del usuario.

Rutas principales:

| Ruta | Descripcion |
| --- | --- |
| `/applet/` | Inicio Applet |
| `/applet/modules/` | Launcher de modulos |
| `/applet/security/` | Roles y usuarios |
| `/applet/audit/` | Eventos auditados |
| `/applet/backups/` | Backups manuales y automaticos |
| `/applet/system-status/` | Estado del sistema |
| `/applet/kanban/` | Kanban general ERP |
| `/remuneraciones/` | Dashboard de remuneraciones |
| `/remuneraciones/trabajadores/` | Listado y estados de trabajadores |
| `/reportes/` | Reportes con filtros, graficos y exportacion |
| `/cargas/` | Carga ETL controlada |
| `/contabilidad/` | Dashboard contable |
| `/inventario/` | Dashboard de inventario |
| `/comercio/` | Dashboard de compras y ventas |
| `/asistencia/` | Dashboard de asistencia |
| `/kanban/` | Kanban operativo de remuneraciones |
| `/api/` | API JSON interna |

## Datos y modelos principales

| Modelo | Uso |
| --- | --- |
| `Employee` | Trabajadores, datos laborales y estado. |
| `PayrollPeriod` | Periodos de remuneracion. |
| `PayrollItem` | Codigos/items de remuneracion y categoria. |
| `PayrollEntry` | Movimiento por trabajador, periodo e item. |
| `PayrollSummary` | Resumen de liquidacion por trabajador y periodo. |
| `ImportRun` | Auditoria de corridas ETL. |
| `AttendanceRecord` | Asistencia por trabajador y fecha con entrada, salida, estado y horas. |
| `AuditLog` | Eventos operativos de Applet/DATA_scope. |

Estados de trabajador:

| Estado tecnico | Etiqueta |
| --- | --- |
| `active` | Activo |
| `inactive` | Inactivo |
| `terminated` | Finiquitado |
| `pending_review` | Pendiente revision |

## Flujo ETL

El ETL puede ejecutarse por consola o desde `/cargas/`.

Flujo base:

1. Entrada Excel historico o CSV transformado.
2. Transformacion a formato largo (`transformed.csv`).
3. Separacion por categorias.
4. Generacion de CSV equivalentes a liquidaciones.
5. Generacion opcional de Excel final.
6. Importacion opcional a modelos Django.
7. Registro de `ImportRun` y eventos de auditoria.

Scripts principales:

| Archivo | Proposito |
| --- | --- |
| `run_etl.py` | Orquestador principal. |
| `dataload.py` | Transformacion de Excel historico. |
| `tabcreated.py` | Separacion por categorias. |
| `build_liquidaciones_csvs.py` | CSV equivalentes a liquidaciones. |
| `transfer_liquidaciones_to_excel.py` | Salida Excel final. |
| `import_payroll_data.py` | Importacion a Django. |

Categorias de items:

- `haberes_normales_imponibles`
- `haberes_exentos_no_imponibles`
- `asignaciones_familiares`
- `contribucion_empleador`
- `descuentos_legales_previsionales`
- `otros_descuentos`
- `provisiones`
- `totales`

## Carga web

Ruta:

```text
/cargas/
```

Formatos aceptados:

- `.xlsx`
- `.xls`
- `.csv`

Controles actuales:

- Carga masiva controlada.
- Carga individual por codigo de ficha como alcance declarado.
- Importar al ERP solo si el usuario tiene permiso.
- Limpiar datos solo si el usuario tiene permiso.
- Descargar salidas solo si el usuario tiene permiso.
- Guardado de archivos por corrida en `uploads/<timestamp>/`.
- Procesamiento en segundo plano opcional con pagina de estado por corrida.

Pendiente importante: la carga individual aun reutiliza el pipeline de archivo. Falta formulario manual real para trabajador/liquidacion.

## Reportes

Ruta:

```text
/reportes/
```

Funciones:

- Filtro por trabajador, RUT, codigo, documento, division, periodo, categoria y sueldo liquido.
- KPIs de liquidaciones, trabajadores, haberes, descuentos, sueldo liquido y costo empresa.
- Grafico por categoria.
- Grafico por periodo.
- Tabla por departamento.
- Tabla por trabajador.
- Tabla por periodo.
- Exportacion CSV controlada por permiso.
- Impresion/PDF desde navegador.

## API interna

Ruta base:

```text
/api/
```

Endpoints:

| Ruta | Descripcion |
| --- | --- |
| `/api/` | Indice de endpoints |
| `/api/health/` | Salud del servicio |
| `/api/system-status/` | Estado operativo |
| `/api/modules/` | Modulos |
| `/api/payroll/summary/` | Resumen payroll |
| `/api/payroll/periods/` | Periodos recientes |

La API ya requiere login y permisos cuando expone informacion de remuneraciones.

## Backups y operacion local

Backups:

- Comando: `python manage.py backup_sqlite`
- Script: `backup_erp.ps1`
- Carpeta: `backups/`
- Backup automatico: activo cada 90 minutos mediante middleware.

Estado:

- Politica formal de retencion/restauracion documentada.
- Backup SQLite con verificacion `integrity_check`.
- Retencion simple por dias y minimo de copias.
- Separar backups de ambiente productivo/local sigue recomendado antes de operar en red.

## Pruebas y verificacion

Comandos usados:

```powershell
python manage.py check
python manage.py test Applet DATA_scope ERP_api Accounting Inventory Commerce Attendance
```

Estado actual:

- `check`: sin errores.
- tests existentes: 37 OK.

## Faltantes principales

| Prioridad | Falta | Motivo |
| --- | --- | --- |
| Alta | Recalculo automatico de liquidaciones | Los movimientos se editan de forma controlada, pero los totales no se recalculan automaticamente. |
| Media | PostgreSQL | Recomendado antes de multiusuario sostenido; movido al final de v1.0.x por limitaciones actuales de permisos/infraestructura. |
| Baja | Cola real de trabajos | El background simple ya existe; una cola dedicada solo seria necesaria si el volumen crece. |
| Cerrado v0.6.4 | Logs persistentes | Existen logs rotativos de aplicacion y ETL. |
| Cerrado v0.9.8 | Auditoria granular avanzada | Existen campos estructurados, cambios JSON y filtros por objeto. |
| Cerrado v0.6.8 | Exportaciones adicionales | Existen exportaciones por trabajador, periodo y liquidacion. |
| Baja | Compras/ventas avanzado | La base existe; falta integracion con stock, contabilidad, aprobaciones y documentos formales. |

## Version actual

Version funcional: `1.0.8`.

Hitos cerrados:

- `0.4.13`: validacion funcional con usuarios nominales de cada rol.
- `0.4.14`: politica formal de retencion/restauracion de backups.
- `0.5.8`: operacion RRHH controlada.
- `0.5.8c`: pulido UI Bootstrap, Django Admin y modo claro/oscuro.
- `0.6.8`: base operativa robusta sin PostgreSQL.
- `0.7.5a`: base contable inicial y reportes pulidos.
- `0.8.4`: base inicial de inventario.
- `0.9.4`: base inicial de compras y ventas.
- `0.9.6C`: asistencia historica diaria, mensual y por trabajador.
- `0.9.7`: operacion local reforzada sobre SQLite.
- `0.9.8`: auditoria granular avanzada.
- `0.9.9`: integracion asistencia-remuneraciones.
- `1.0.3`: testing amplio, documentacion operativa y deploy LAN documentado.
- `1.0.8`: backups restaurables, auditoria por usuario/rol, plan de migracion, IA local separada y preparacion PostgreSQL documentada.

Foco siguiente recomendado: `v1.0.9 - Ensayo de migracion SQLite a PostgreSQL` solo en servidor autorizado, dejando `v1.0.10` para migracion real con infraestructura y permisos.
