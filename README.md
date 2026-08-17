# Celestial ERP

ERP web modular para remuneraciones, asistencia, contabilidad, inventario, compras y ventas. Incluye un pipeline ETL para transformar liquidaciones historicas, control de acceso por roles, auditoria, API interna y respaldos PostgreSQL verificados.

> Version actual: **1.2.1** · Backend Django con PostgreSQL · Frontend Next.js/Electron · Operacion local/LAN controlada

![Arquitectura general de Celestial ERP](docs/assets/arquitectura_general.svg)

## Estado del proyecto

Celestial ERP comenzo como un proceso ETL para liquidaciones historicas y evoluciono a una aplicacion Django multiusuario. La migracion desde SQLite a PostgreSQL ya fue completada y validada con `297.084` objetos historicos. SQLite se conserva solamente como respaldo de reversa y fuente historica.

Actualmente estan operativos:

- frontend nativo responsive en Next.js/TypeScript, accesible desde navegador y smartphone en LAN;
- aplicacion de escritorio Electron empaquetable como AppImage;
- portal web, login, navegacion por permisos y Django Admin personalizado;
- remuneraciones, trabajadores, periodos, items, movimientos y liquidaciones;
- carga ETL web y por consola, con seguimiento de corridas y validaciones;
- asistencia diaria, reportes mensuales e integracion con remuneraciones;
- contabilidad base, inventario, compras y ventas;
- reportes nativos con indicadores, graficos, filtros e impresion/PDF desde navegador;
- carga masiva conectada al ETL, con historial y seguimiento de ejecucion;
- administracion de usuarios y roles desde el frontend para perfiles autorizados;
- auditoria estructurada por usuario, rol, objeto y cambios;
- API Django v1 protegida para sesion, recursos CRUD, reportes, ETL y usuarios;
- backups PostgreSQL manuales y automaticos mediante `pg_dump`, verificados con `pg_restore`;
- restauracion PostgreSQL probada en un cluster temporal aislado;
- configuracion de desarrollo, operacion LAN y despliegue productivo con Gunicorn, Next.js, systemd y nginx.

La version `1.2.1` cerro la validacion automatizada con 51 pruebas sobre PostgreSQL temporal. Los siguientes incrementos cubren validacion del AppImage en un equipo limpio, prueba fisica desde smartphone, HTTPS/firewall y evolucion funcional de contabilidad, inventario y comercio.

## Modulos

| Modulo | Aplicacion Django | Alcance actual |
| --- | --- | --- |
| Portal y control | `Applet` | Inicio, modulos, seguridad, auditoria, backups y estado del sistema |
| Remuneraciones | `DATA_scope` | Trabajadores, periodos, items, movimientos, liquidaciones, reportes y ETL |
| Asistencia | `Attendance` | Registros diarios, historico, reporte mensual y sincronizacion con remuneraciones |
| Contabilidad | `Accounting` | Plan de cuentas, centros de costo, mapeos, asientos y reportes iniciales |
| Inventario | `Inventory` | Productos, bodegas, stock, movimientos y valorizacion |
| Compras y ventas | `Commerce` | Proveedores, clientes, ordenes de compra y venta |
| API interna | `ERP_api` | Sesion, catalogos, CRUD, reportes, cargas ETL y usuarios protegidos |
| Frontend | `frontend` | Next.js responsive, proxy seguro a Django y empaquetado Electron |

## Arquitectura

```text
Navegador / smartphone / Electron
                |
                v
        Next.js (puerto 3000)
                |
                v
 Django API (puerto 8000, privado)
                |
                v
           PostgreSQL
```

En produccion, nginx publica HTTPS y envia el trafico a Next.js. Django mantiene permisos, reglas de negocio, auditoria y ETL. Ni el navegador ni Electron se conectan directamente a PostgreSQL.

## Tecnologias

- Python 3.12+
- Django 6.0
- PostgreSQL y `psycopg` 3
- Node.js 24 LTS y npm 11
- Next.js 16, React 19 y TypeScript
- Electron y electron-builder para escritorio
- pandas y openpyxl para ETL
- Bootstrap 5.3.3 servido localmente
- HTML y CSS responsive sin dependencia operativa de CDN
- `pg_dump` y `pg_restore` para respaldos PostgreSQL

Las versiones declaradas se encuentran en [`requirements.txt`](requirements.txt).

## Requisitos

- Python compatible con Django 6.0.
- PostgreSQL en ejecucion.
- Base y usuario PostgreSQL creados.
- Herramientas cliente `pg_dump` y `pg_restore` para respaldos.
- Node.js `>=20.9` para Next.js; se recomienda la version indicada en `Celestial_ERP/frontend/.nvmrc`.
- Acceso local o LAN controlado; no se recomienda exponer `runserver` a internet.

## Instalacion rapida

### 1. Clonar y crear el entorno

```bash
git clone https://github.com/roiwow7-maker/Celestial-ERP.git
cd Celestial-ERP
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

En PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Crear PostgreSQL

Ejemplo desde `psql` usando nombres propios para el ambiente:

```sql
CREATE USER celestial_app WITH PASSWORD 'CAMBIAR_ESTA_CLAVE';
CREATE DATABASE celestial_erp OWNER celestial_app;
```

No escribas credenciales reales en archivos versionados.

### 3. Configurar variables

Variables principales:

```text
POSTGRES_DB=celestial_erp
POSTGRES_USER=celestial_app
POSTGRES_PASSWORD=una-clave-segura
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432
DJANGO_SECRET_KEY=una-clave-larga-y-unica
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
ERP_SETTINGS_ENV=dev
```

Consulta [`.env.example`](.env.example) para ver todas las opciones. Django toma estas variables del entorno; el archivo `.env` no se publica ni se carga automaticamente sin una herramienta externa.

Para desarrollo local tambien se admite `Celestial_ERP/.postgres_password`, que esta ignorado por Git. En produccion deben utilizarse secretos del sistema o variables protegidas.

### 4. Preparar Django

```bash
cd Celestial_ERP
python manage.py migrate
python manage.py createsuperuser
python manage.py check
python manage.py runserver 127.0.0.1:8000
```

Abrir:

- Portal: <http://127.0.0.1:8000/>
- Django Admin: <http://127.0.0.1:8000/admin/>
- API interna: <http://127.0.0.1:8000/api/>

En Windows tambien puede utilizarse [`start_erp_web.ps1`](start_erp_web.ps1).

### 5. Preparar el frontend real

En otra terminal:

```bash
cd Celestial_ERP/frontend
npm ci
npm run dev
```

Abrir <http://127.0.0.1:3000>. Next.js escucha en `0.0.0.0:3000` para permitir pruebas LAN, mientras Django permanece privado en `127.0.0.1:8000`.

Comprobaciones y empaquetado de escritorio:

```bash
npm run lint
npm run typecheck
npm run build
npm run build:desktop
```

El AppImage se genera en `Celestial_ERP/frontend/dist-electron/` y esta excluido del repositorio por ser un artefacto local.

## Roles y seguridad

El acceso requiere login. Los roles funcionales son:

| Rol | Alcance general |
| --- | --- |
| Administrador | Configuracion, seguridad, auditoria, backups y operacion completa |
| RRHH | Trabajadores, remuneraciones, cargas y asistencia |
| Contabilidad | Lectura de remuneraciones y operacion contable/comercial autorizada |
| Solo lectura | Consulta de modulos permitidos sin operaciones sensibles |

Inicializacion de grupos y permisos:

```bash
python manage.py setup_access_control
```

Para ambientes compartidos:

- usar usuarios nominales y rotar credenciales temporales;
- definir `ERP_SETTINGS_ENV=prod` y `DJANGO_DEBUG=false`;
- configurar `DJANGO_SECRET_KEY`, hosts, cookies seguras y HTTPS;
- no publicar PostgreSQL directamente en internet;
- revisar auditoria y logs periodicamente.

Consulta [Administracion y multiusuario](docs/05_ADMIN_MULTIUSUARIO.md) y [Seguridad, roles y permisos](docs/assets/08_seguridad_roles_permisos.md).

## Pipeline ETL

El pipeline acepta fuentes XLS, XLSX y CSV, normaliza liquidaciones historicas, clasifica items, genera salidas de revision e importa datos a Django.

Flujo general:

```text
Fuente historica
  -> transformacion y normalizacion
  -> clasificacion de items
  -> CSV/Excel de revision
  -> validaciones
  -> importacion transaccional a Django/PostgreSQL
  -> reportes y auditoria
```

Ejecucion principal:

```bash
python run_etl.py --help
```

Importacion directa desde Django:

```bash
python Celestial_ERP/manage.py import_payroll_data --help
```

Los archivos de entrada y salida contienen informacion privada y estan excluidos globalmente del repositorio.

Documentacion: [Pipeline ETL](docs/03_ETL_PIPELINE.md) y [Reglas de remuneraciones](REGLAS_NEGOCIO_REMUNERACIONES.md).

## Backups PostgreSQL

Crear un respaldo apropiado para la base activa:

```bash
cd Celestial_ERP
python manage.py backup_database
```

Con PostgreSQL, el comando:

1. ejecuta `pg_dump` en formato custom comprimido;
2. omite propietarios y privilegios especificos del servidor;
3. verifica el archivo mediante `pg_restore --list`;
4. aplica retencion de 30 dias conservando al menos siete copias;
5. registra la operacion cuando se ejecuta desde la pantalla administrativa.

Los respaldos se guardan en `backups/`, carpeta excluida de Git. Deben copiarse cifrados a una ubicacion independiente.

La restauracion PostgreSQL fue validada en un cluster temporal aislado. `deploy/` incluye servicios y timers de ejemplo para backup, retencion, limpieza y monitoreo; deben instalarse solamente en un servidor autorizado y con credenciales protegidas.

## Comandos utiles

Desde `Celestial_ERP/`:

```bash
python manage.py check
python manage.py showmigrations
python manage.py migrate
python manage.py setup_access_control
python manage.py validate_business_rules
python manage.py sync_attendance_payroll
python manage.py cleanup_uploads --days 30
python manage.py backup_database
```

Ayuda detallada:

```bash
python manage.py help <comando>
```

## Pruebas

Comprobacion base:

```bash
cd Celestial_ERP
python manage.py check
python manage.py makemigrations --check --dry-run
```

Suite por aplicaciones:

```bash
python manage.py test Applet DATA_scope ERP_api Accounting Inventory Commerce Attendance
```

Suite completa en PostgreSQL temporal aislado:

```bash
cd ..
./venv/bin/python tools/run_postgresql_tests.py
```

La validacion de `1.2.1` ejecuto 51 pruebas correctamente. El script crea un cluster temporal, ejecuta la suite y lo elimina al finalizar sin tocar la base productiva.

## Estructura del repositorio

```text
Celestial-ERP/
├── Celestial_ERP/             # Proyecto Django y aplicaciones
│   ├── Accounting/
│   ├── Applet/
│   ├── Attendance/
│   ├── Celestial_ERP/         # Settings, URLs, ASGI y WSGI
│   ├── Commerce/
│   ├── DATA_scope/
│   ├── ERP_api/
│   ├── frontend/              # Next.js, React, TypeScript y Electron
│   ├── Inventory/
│   └── manage.py
├── deploy/                    # systemd, nginx, timers y entorno de ejemplo
├── docs/                      # Manuales, arquitectura y operacion
├── tools/                     # Herramientas auxiliares ETL/Excel
├── run_etl.py                 # Orquestador ETL
├── requirements.txt
├── ROADMAP.md
└── version_log.md
```

No forman parte del repositorio: bases de datos, dumps, backups, CSV, Excel, uploads, reportes operativos, logs, entornos virtuales y secretos.

## Documentacion

Lectura recomendada:

1. [Documentacion general](docs/00_DOCUMENTACION_GENERAL.md)
2. [Manual completo](docs/MANUAL_COMPLETO_CELESTIAL_ERP.md)
3. [Indice maestro](docs/INDICE_DOCUMENTACION.md)
4. [Roadmap](ROADMAP.md)
5. [Registro de versiones](version_log.md)

Por tema:

- [Portal y orquestador](docs/01_APPLET_PORTAL.md)
- [Remuneraciones](docs/02_DATA_SCOPE_REMUNERACIONES.md)
- [API interna](docs/04_API.md)
- [Operacion y backups](docs/06_OPERACION_LOCAL_BACKUPS.md)
- [Contabilidad](docs/11_CONTABILIDAD.md)
- [Inventario](docs/12_INVENTARIO.md)
- [Compras y ventas](docs/13_COMPRAS_VENTAS.md)
- [Asistencia](docs/14_ASISTENCIA.md)
- [Deploy LAN](docs/18_DEPLOY_LAN.md)
- [PostgreSQL, Nginx y Next.js](docs/20_POSTGRESQL_NGINX_NEXTJS.md)
- [Plan del frontend real](docs/21_PLAN_FRONTEND_REAL.md)
- [Operacion PostgreSQL y produccion](docs/22_OPERACION_POSTGRESQL_PRODUCCION.md)
- [Validacion frontend 1.2.x](docs/23_VALIDACION_FRONTEND_1_2.md)
- [Revision de evolucion funcional](docs/24_REVISION_EVOLUCION_FUNCIONAL.md)
- [Publicacion segura en GitHub](GITHUB_PUBLICACION.md)

Algunos documentos describen etapas historicas sobre SQLite. Para decisiones actuales prevalecen este README, [`ROADMAP.md`](ROADMAP.md), [`version_log.md`](version_log.md) y los documentos `20`/`21`.

## Privacidad del repositorio

Este repositorio no contiene los datos utilizados por el ERP. `.gitignore` y el hook `.githooks/pre-commit` bloquean:

- SQLite, dumps PostgreSQL y archivos SQL;
- CSV, XLS, XLSX, XLSM y ODS;
- backups, uploads y reportes;
- `.env`, contraseñas locales, secretos y claves;
- logs, archivos temporales y entornos virtuales.

Antes de cada publicacion se debe revisar:

```bash
git status --short
git diff --cached --name-only
```

Si un secreto o dato privado entra al historial, eliminarlo en un commit posterior no es suficiente: debe rotarse la credencial y limpiarse el historial antes de publicar.

## Roadmap

Prioridades inmediatas:

1. validar el AppImage en un equipo Linux limpio (`1.2.2`);
2. completar la prueba fisica desde smartphone en LAN (`1.2.3`);
3. aplicar HTTPS, servicios persistentes y firewall en servidor autorizado (`1.2.4`);
4. implementar aprobaciones, anulaciones y cierres contables (`1.2.5`);
5. implementar kardex y documentos de inventario (`1.2.6`);
6. integrar compras y ventas con stock y contabilidad (`1.2.7`).

El detalle se mantiene en [`ROADMAP.md`](ROADMAP.md) y [Plan del frontend real](docs/21_PLAN_FRONTEND_REAL.md).

## Versionado y mantenimiento

La fuente unica de version es:

```text
Celestial_ERP/Applet/version.py
```

Cada mejora debe:

1. actualizar `ERP_VERSION`;
2. registrar el cambio en `version_log.md`;
3. actualizar el roadmap cuando cierre o agregue un hito;
4. ejecutar las comprobaciones relacionadas;
5. verificar que no se incluyan datos privados.

## Licencia

Celestial ERP se publica como **software propietario visible para fines de portafolio**. No es software libre ni de codigo abierto. La visualizacion del repositorio no concede autorizacion para operarlo, modificarlo, redistribuirlo o explotarlo comercialmente.

Consulta la [Licencia Propietaria de Celestial ERP para Portafolio](LICENSE.md), preparada con referencia a la Ley chilena N.º 17.336. Los componentes de terceros conservan sus propias licencias.

Antes de comercializar el sistema o aceptar contribuciones externas, la licencia y la titularidad deben ser revisadas por un abogado habilitado en Chile.
