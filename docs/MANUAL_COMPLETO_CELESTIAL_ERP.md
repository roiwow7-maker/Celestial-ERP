# Manual completo Celestial ERP

Fecha de referencia: 2026-07-20

Version documentada: `1.0.8`

## Proposito del documento

Este manual consolida la documentacion operativa de Celestial ERP en un solo documento: manual de uso, implementacion, gestion interna, ETL, seguridad, backups, administracion y roadmap. Esta pensado para operacion local o red interna controlada.

## 1. Vision General

Celestial ERP es una plataforma Django para gestionar datos historicos y operativos de remuneraciones. El sistema nacio como un ETL para liquidaciones historicas y evoluciono a una webapp con modulos de remuneraciones, contabilidad, inventario, compras/ventas, asistencia, auditoria, backups, API interna y administracion multiusuario.

La version actual es `1.0.8`. PostgreSQL esta preparado documentalmente, pero la operacion actual sigue sobre SQLite por limitaciones de permisos e infraestructura. La migracion real queda para `v1.0.9` y `v1.0.10`.

## 2. Alcance Funcional

Modulos principales:

- Applet: portal, navegacion, estado del sistema, auditoria, backups, seguridad y kanban.
- DATA_scope: remuneraciones, trabajadores, periodos, items, movimientos, liquidaciones, reportes y cargas ETL.
- ERP_api: API interna protegida por login/permisos.
- Accounting: plan de cuentas, centros de costo, mapeos, asientos y reportes contables.
- Inventory: productos, bodegas, stock, movimientos y valorizacion.
- Commerce: proveedores, clientes, compras, ventas y reportes comerciales.
- Attendance: asistencia historica diaria, mensual y por trabajador.

## 3. Manual de Uso

### 3.1 Ingreso al sistema

1. Abrir la URL local o LAN del sistema.
2. Iniciar sesion con usuario nominal.
3. Usar la barra superior para entrar a modulos visibles segun permisos.
4. No compartir claves ni operar con usuarios genericos salvo emergencia controlada.

### 3.2 Navegacion

La navbar muestra opciones segun rol:

- General: portal, modulos y estado del sistema.
- Remuneraciones: dashboard, trabajadores, periodos, items, movimientos, liquidaciones, reportes y cargas.
- Contabilidad: dashboard, plan de cuentas, centros de costo, mapeos, asientos y reportes.
- Inventario: productos, bodegas, stock, movimientos y valorizacion.
- Comercio: proveedores, clientes, compras, ventas y reportes.
- Control: administracion, seguridad, auditoria y backups.
- Herramientas: kanban y API interna.

### 3.3 Remuneraciones

Uso recomendado:

1. Revisar dashboard general.
2. Buscar trabajador por nombre, RUT o codigo de ficha.
3. Revisar periodos y liquidaciones.
4. Crear o editar datos manuales solo con permiso adecuado.
5. Usar reportes para filtros por departamento, periodo, categoria y rango liquido.
6. Exportar CSV cuando se requiera analisis externo.

### 3.4 Cargas ETL

La carga web permite subir Excel historico o CSV transformado. La carga genera estado por corrida y permite revisar salidas. Para cargas grandes se recomienda ejecutar desde consola con `run_etl.py`.

### 3.5 Contabilidad

Flujo base:

1. Revisar plan de cuentas.
2. Revisar centros de costo.
3. Mantener mapeos item remuneracion a cuenta contable.
4. Generar asientos desde liquidaciones.
5. Revisar reportes contables iniciales.

### 3.6 Inventario

Flujo base:

1. Mantener productos y bodegas.
2. Revisar saldos de stock.
3. Registrar movimientos de entrada, salida o ajuste.
4. Revisar valorizacion por costo promedio.

### 3.7 Compras y ventas

Flujo base:

1. Mantener proveedores y clientes.
2. Registrar compras y ventas.
3. Revisar documentos y lineas.
4. Consultar reportes comerciales.

### 3.8 Asistencia

Flujo base:

1. Crear registros diarios por trabajador.
2. Mantener hora de entrada, salida, estado y fuente.
3. Revisar historico por trabajador.
4. Revisar reporte mensual.
5. Exportar CSV o imprimir/guardar como PDF desde navegador.

## 4. Manual de Implementacion

### 4.1 Requisitos

- Windows con Python disponible.
- Dependencias en `requirements.txt`.
- Acceso al workspace `C:\Users\RoyGabrielZaioLopez\Desktop\ETL`.
- SQLite para operacion actual.
- PostgreSQL solo cuando exista servidor autorizado.

### 4.2 Instalacion local

Pasos generales:

```powershell
cd C:\Users\RoyGabrielZaioLopez\Desktop\ETL
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python Celestial_ERP\manage.py migrate
python Celestial_ERP\manage.py check
```

### 4.3 Ejecucion local

```powershell
python Celestial_ERP\manage.py runserver
```

Para red interna, usar configuracion LAN documentada en `docs/18_DEPLOY_LAN.md`, ajustar `ALLOWED_HOSTS` y firewall local.

### 4.4 Variables y configuracion

La configuracion sensible no debe guardarse en git. Usar `.env` o variables de entorno segun el entorno. Revisar `.env.example`.

Variables importantes:

- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG`
- `DJANGO_ALLOWED_HOSTS`
- `DJANGO_SETTINGS_MODULE`
- `ERP_AUTO_BACKUP_ENABLED`
- `ERP_AUTO_BACKUP_INTERVAL_MINUTES`

## 5. Manual de Gestion Interna

### 5.1 Roles

Roles funcionales:

- Administrador: acceso total, seguridad, backups, admin y datos.
- RRHH: operacion de remuneraciones y asistencia segun permisos.
- Contabilidad: lectura/exportacion y modulo contable.
- Solo lectura: consulta controlada sin escritura sensible.

### 5.2 Usuarios

Buenas practicas:

- Usar usuarios nominales.
- Evitar usuarios compartidos.
- Desactivar usuarios que ya no operan.
- Revisar permisos antes de entregar acceso.
- Registrar cambios relevantes mediante auditoria.

### 5.3 Auditoria

La auditoria registra usuario, modulo, accion, descripcion, objeto, ID, representacion y cambios JSON cuando aplica. La vista permite filtrar por modulo, accion, objeto, ID y texto.

### 5.4 Django Admin

El Django Admin queda reservado para administracion interna. Debe usarse con cuidado porque permite cambios directos en datos y configuracion. La UI del admin esta personalizada con colores del sistema y tema claro/oscuro.

## 6. Manual ETL

### 6.1 Flujo general

1. Entrada: Excel historico o CSV transformado.
2. `dataload.py`: transforma Excel a `transformed.csv`.
3. `tabcreated.py`: separa CSV por categoria.
4. `build_liquidaciones_csvs.py`: genera CSV equivalentes a liquidaciones.
5. `transfer_liquidaciones_to_excel.py`: crea Excel final.
6. Importacion Django con `import_payroll_data`.

### 6.2 Ejecucion completa

```powershell
python run_etl.py --input "ITEMS_ACUMULADOS_Historico Payroll.xlsx"
```

Opciones utiles:

- `--skip-excel`
- `--skip-import`
- `--clear`
- `--rut-empresa`
- `--source-format historic_excel`
- `--source-format transformed_csv`

### 6.3 Cargas SEGCEI y COSESO

Herramienta reusable:

```powershell
python tools\load_item_to_liquidaciones_workbook.py --source "csv_por_categoria\contribucion_empleador.csv" --workbook "Liquidaciones_Historicas_Cargadas_SEGCEI_COSESO_workcopy.xlsx" --item-code SEGCEI --output "Liquidaciones_Historicas_Cargadas_SEGCEI_COSESO_FINAL.xlsx"
python tools\load_item_to_liquidaciones_workbook.py --source "ITEMS_ACUMULADOS_Historico Payroll.xlsx" --workbook "Liquidaciones_Historicas_Cargadas_SEGCEI_workcopy.xlsx" --item-code COSESO --output "Liquidaciones_Historicas_Cargadas_SEGCEI_COSESO_workcopy.xlsx"
```

Mapeos:

- `SEGCEI` hacia `Seguro Cesantia Empleador (Ley proteccion empleo)`.
- `COSESO` hacia `Cotizacion Expectativa de Vida`.

El generador `build_liquidaciones_csvs.py` tambien calcula `COSESO` para la columna `Cotizacion Expectativa de Vida`.

## 7. Operacion y Backups

### 7.1 Backup manual

```powershell
python Celestial_ERP\manage.py backup_sqlite
```

Opciones:

```powershell
python Celestial_ERP\manage.py backup_sqlite --retention-days 30 --keep-last 5
python Celestial_ERP\manage.py backup_sqlite --no-verify
```

### 7.2 Restauracion validada

Desde `v1.0.4`:

```powershell
python Celestial_ERP\manage.py validate_backup_restore
python Celestial_ERP\manage.py validate_backup_restore --backup-path backups\db_AAAAMMDD_HHMMSS.sqlite3
```

El comando valida una restauracion en copia temporal sin tocar la base activa.

### 7.3 Salud SQLite

```powershell
python Celestial_ERP\manage.py check_sqlite_operational_health
```

Valida integridad, WAL, claves foraneas, ultimo backup, uploads y conteos base.

## 8. Seguridad Operativa

Principios:

- Login obligatorio.
- Permisos por modulo y accion.
- Usuarios nominales.
- Backups frecuentes.
- Datos sensibles fuera de git.
- Red interna controlada.
- PostgreSQL antes de multiusuario sostenido.

Comando recomendado:

```powershell
python Celestial_ERP\manage.py check_operational_security
```

## 9. API Interna

Ruta principal:

```text
/api/
```

La API requiere sesion. Los endpoints de remuneraciones requieren permisos de payroll. El explorador visual muestra endpoints en acordeon y permite consultar el indice JSON con:

```text
/api/?format=json
```

## 10. Testing y Validacion

Comandos:

```powershell
python Celestial_ERP\manage.py check
python Celestial_ERP\manage.py makemigrations --check --dry-run
python Celestial_ERP\manage.py test Applet DATA_scope ERP_api Accounting Inventory Commerce Attendance
```

Estado validado al 2026-07-20:

- `check`: OK.
- migraciones pendientes: ninguna.
- suite completa: 48 tests OK.
- SQLite: `integrity_check` OK.

## 11. Deploy LAN

Uso recomendado:

1. Definir IP del equipo servidor.
2. Ajustar `ALLOWED_HOSTS`.
3. Ejecutar migraciones.
4. Crear usuarios nominales.
5. Probar acceso desde otro equipo.
6. Validar firewall.
7. Ejecutar backup inicial.
8. Probar restauracion del backup.

No exponer a internet sin hardening adicional.

## 12. IA Local

La IA local cuantizada queda planificada como servicio LAN separado. No debe ejecutarse dentro del proceso Django. Debe tener endpoint interno, logs propios, limites de memoria, timeouts y acceso controlado sin conectar directo a la base productiva.

## 13. PostgreSQL

Estado actual:

- Preparacion documentada en `v1.0.8`.
- Ensayo pendiente en `v1.0.9`.
- Migracion real pendiente en `v1.0.10`.

No migrar sin:

- servidor autorizado;
- backup validado;
- plan de reversa;
- ventana de mantenimiento;
- pruebas verdes;
- credenciales fuera del repo.

## 14. Mantenimiento Recurrente

Rutina recomendada:

- Diario: revisar acceso, errores visibles y ultimo backup.
- Semanal: ejecutar `check_sqlite_operational_health`.
- Mensual: validar restauracion de un backup.
- Antes de cambios grandes: backup manual y pruebas.
- Despues de cargas ETL: revisar conteos, reportes y auditoria.

## 15. Archivos Clave

- `Celestial_ERP/Applet/services.py`: version y servicios centrales.
- `run_etl.py`: orquestador ETL.
- `dataload.py`: transformacion historica.
- `build_liquidaciones_csvs.py`: CSV equivalentes.
- `tools/load_item_to_liquidaciones_workbook.py`: carga SEGCEI/COSESO a Excel.
- `ROADMAP.md`: roadmap vigente.
- `version_log.md`: bitacora de versiones.
- `docs/INDICE_DOCUMENTACION.md`: indice maestro.

## 16. Riesgos y Pendientes

Riesgos actuales:

- SQLite no es ideal para multiusuario sostenido.
- Excel puede bloquear archivos si estan abiertos.
- Backups deben copiarse fuera del equipo periodicamente.
- Artefactos temporales pueden quedar bloqueados por Windows.

Pendientes:

- `v1.0.9`: ensayo SQLite a PostgreSQL.
- `v1.0.10`: migracion real a PostgreSQL.
- Validacion LAN recurrente.
- Politica externa de respaldo fuera del equipo.

## 17. Anexos

Documentos relacionados:

- `docs/00_DOCUMENTACION_GENERAL.md`
- `docs/01_APPLET_PORTAL.md`
- `docs/03_ETL_PIPELINE.md`
- `docs/05_ADMIN_MULTIUSUARIO.md`
- `docs/06_OPERACION_LOCAL_BACKUPS.md`
- `docs/18_DEPLOY_LAN.md`
- `docs/19_V10_PRE_POSTGRESQL_IA_BACKUPS.md`
- `ROADMAP.md`
- `version_log.md`
