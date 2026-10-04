# Multiempresa y seguridad — 1.3.1

## Arquitectura implementada

Un frontend Next.js ofrece un login independiente. Cada empresa tiene un backend Django local,
una base PostgreSQL, un usuario PostgreSQL, una clave Django y un directorio privado.
Los usuarios, grupos, sesiones y eventos de auditoría viven en la base de su empresa.
No hay SSO: tener una cuenta en una empresa no concede acceso a otra.

```text
Opera → Next.js :3000
          ├─ /backend/company/default/… → Django :8000 → celestial_erp
          └─ /backend/company/rgamer-store/… → Django :8001 → erp_rgamer_store
```

El login en `/login` detecta la empresa por el dominio del correo institucional y el
portal conserva su identificador en `/portal?company=rgamer-store`. Los usuarios
locales sin correo acceden mediante un enlace acotado a su empresa. La selección no
depende de una variable global compartida ni de una cabecera que el cliente pueda
usar para elegir conexiones arbitrarias. El proxy consulta un registro permitido y
comprueba `X-ERP-Company` antes de entregar la respuesta. Los nombres de cookies
llevan el identificador de la empresa. Cambiar de empresa carga un documento nuevo
para descartar estado y peticiones anteriores. La sesión histórica de la empresa
actual solo puede migrar hacia `default`.

Los procesos separados conservan la semántica de los comandos existentes: cada
importación, descarga, respaldo y tarea hereda una única configuración. No se usa
un router que pueda volver accidentalmente a la base `default` fuera de una petición.

## Estado local

- Empresa actual: se conservan base, datos, cuentas y puerto 8000.
- Nueva empresa: **rgamer-store**, base `erp_rgamer_store`, puerto 8001.
- Perfil privado: `config/companies/rgamer-store/company.env`.
- Cuenta inicial nominal: `roy.admin`, rol Administrador, sin superusuario Django.
- Credencial generada aleatoriamente: `config/companies/rgamer-store/initial-access.json`, modo 0600. No publicar ni adjuntar a incidencias. Tras guardarla en un gestor de contraseñas, eliminar ese archivo.
- Registro de backends: `config/companies.json`; se descubre automáticamente en desarrollo. En despliegues, definir `ERP_COMPANIES_FILE` con ruta absoluta.
- Datos operativos nuevos: `tenant-data/rgamer-store/{uploads,backups,logs,reports}`.

Estos archivos privados están excluidos de Git. Ninguna base se copia para crear
una empresa: se ejecutan las migraciones y se crean sus propios usuarios.

## Uso y arranque

Abrir `http://127.0.0.1:3000/login` e ingresar con correo institucional o usuario.
El backend nuevo permanece activo
mientras se conserve el proceso local; todavía no se instaló un servicio del sistema.
Después de reiniciar el PC:

```bash
./venv/bin/python tools/start_companies.py
```

Este lanzador reutiliza los backends que ya responden con la identidad correcta e
inicia los faltantes. Mantenerlo abierto. En otra terminal:

```bash
cd Celestial_ERP/frontend
npm run dev
```

Comandos exclusivos de rgamer-store, desde la raíz:

```bash
./venv/bin/python tools/company_manage.py --profile config/companies/rgamer-store/company.env check
./venv/bin/python tools/company_manage.py --profile config/companies/rgamer-store/company.env backup_database
./venv/bin/python tools/company_manage.py --profile config/companies/rgamer-store/company.env check_operational_security
```

No ejecutar un comando sin perfil suponiendo que la elección del navegador cambia
la terminal: sin perfil se opera sobre la empresa actual.

## Alta de otra empresa

```bash
./venv/bin/python tools/prepare_company.py --id nueva-empresa --name "Nueva empresa" --port 8002
```

El preparador genera un perfil, SQL privado y una entrada del registro. No ejecuta
SQL ni sobrescribe perfiles existentes. Revisar el SQL y ejecutarlo como administrador
PostgreSQL (la contraseña del sistema se introduce únicamente en la terminal):

```bash
sudo -u postgres psql -v ON_ERROR_STOP=1 < config/companies/nueva-empresa/provision.sql
./venv/bin/python tools/company_manage.py --profile config/companies/nueva-empresa/company.env migrate --noinput
./venv/bin/python tools/company_manage.py --profile config/companies/nueva-empresa/company.env bootstrap_company_admin --username administrador --credential-file config/companies/nueva-empresa/initial-access.json
./venv/bin/python tools/company_manage.py --profile config/companies/nueva-empresa/company.env runserver 127.0.0.1:8002 --noreload
```

Con el backend activo, desde otra terminal:

```bash
./venv/bin/python tools/register_company.py --entry config/companies/nueva-empresa/frontend-entry.json
```

El registro verifica la identidad del servicio antes de publicarlo. Un error en el
SQL detiene la ejecución; no repetirlo a ciegas ni borrar bases para reintentar.
Revisar qué recursos quedaron creados y completar el alta con el administrador.

## Controles implementados

- Base y credencial PostgreSQL por empresa, sin `SUPERUSER`, `CREATEDB` ni `CREATEROLE` para la cuenta nueva.
- En bases nuevas, acceso `PUBLIC` revocado; solo el propietario y administradores PostgreSQL pueden conectar.
- Rutas separadas para archivos ETL, logs, reportes y backups. Nuevos respaldos con modo 0600 y verificación con `pg_restore --list`.
- Cookies de sesión `HttpOnly`, `SameSite=Lax`, nombres independientes por empresa y respuestas privadas sin caché.
- CSRF Django conservado; proxy valida una lista explícita de orígenes antes de traducir cabeceras. Por defecto solo localhost/127.0.0.1:3000. Configurar `ERP_PUBLIC_ORIGIN` para LAN/HTTPS.
- Proxy conserva cabeceras de protección del backend y elimina cabeceras de reenvío recibidas del cliente. Errores de conexión no exponen rutas internas ni secretos.
- Intentos de login contados en PostgreSQL (compartidos entre workers): bloqueo temporal por cuenta y por dirección del backend; ventana 15 minutos, cinco fallos por cuenta. Detrás del proxy las conexiones comparten IP, por lo que el contador de dirección es global por empresa. En producción añadir limitación por IP real en nginx.
- Sesión limitada a ocho horas y cierre tras 30 minutos sin peticiones autenticadas. El polling también cuenta como actividad; no equivale a detectar presencia física del usuario.
- Contraseñas nuevas validadas (mínimo 12 caracteres y validadores Django). No se cambian contraseñas existentes automáticamente.
- Permisos separados para consultar el módulo de seguridad y crear/modificar cuentas. Administradores normales no pueden modificar superusuarios. Se protege la propia cuenta y el último administrador de rol.
- Eventos de acceso, cierre, expiración, cambios de usuarios y escrituras CRUD de la API; nunca se registra la contraseña. Los fallos de auditoría se notifican al log, pero el almacén no es inmutable ni externo.
- La API rechaza editar movimientos de inventario y devuelve un error de validación al intentar una salida sin stock.
- Límite de carga API de 25 MiB y de cuerpo del proxy de 27 MiB. El límite de servidor web sigue siendo necesario en producción.
- La revisión operativa ya no imprime contraseñas al detectar claves temporales.

## Permiso pendiente en la base histórica

La base `celestial_erp` conserva su ACL original. Quitar CONNECT/TEMPORARY de PUBLIC
requiere aprobación explícita y quedó pendiente tras el bloqueo de la revisión
automática. Esto no afecta el rechazo de sesiones cruzadas en la aplicación, pero
no debe confundirse con prohibir conexiones SQL a esa base. Verificar el propietario
y conexiones utilizadas antes de cambiar su ACL.

## Validación reproducible

```bash
./venv/bin/python tools/run_postgresql_tests.py
./venv/bin/python tools/test_company_isolation.py
cd Celestial_ERP/frontend
npm run test:security
npm run typecheck
npm run lint
npm run build
```

La prueba de aislamiento crea un cluster PostgreSQL desechable con dos roles/bases;
prueba usuarios con el mismo nombre e ID, rechazo de cookies cruzadas, datos
separados, conexiones SQL cruzadas denegadas y respaldos privados independientes.
No usa ni borra datos de las empresas locales.

Las pruebas del proxy verifican filtrado de cookies, CSRF/orígenes, identidad del
backend, empresas desconocidas, redirecciones y compatibilidad de la sesión histórica.

## Hallazgos que continúan pendientes

1. Paginación y filtros por relaciones: el listado de recursos continúa limitado a 100 filas por defecto.
2. Reportes: indicadores globales y detalle filtrado deben alinearse; los límites de 24 períodos/300 saldos deben ser visibles o reemplazarse por paginación/exportación.
3. Rendimiento: evitar consultas por fila al serializar relaciones y no enviar catálogos completos de formularios en cada listado.
4. Separar `erp-shell.tsx` y `ERP_api/v1.py` por responsabilidad y añadir cancelación de consultas al cambiar módulos.
5. Auditar también escrituras fuera de la API, endurecer el admin y modelar reversas/aprobaciones/cierres como operaciones de negocio.

## Antes de alojar empresas externas

Esta entrega habilita operación local multiempresa; no es una certificación de
seguridad ni una auditoría completa de todos los caminos del ERP.

- Instalar HTTPS, firewall, nginx con límite de cuerpos e intentos, `DEBUG=false`, cookies Secure y origen público explícito. PostgreSQL y los backends deben permanecer privados.
- Usar un usuario del sistema o contenedor por empresa y proteger sus perfiles. En este PC los procesos pertenecen a la misma cuenta local: una ejecución de código arbitrario bajo esa cuenta podría leer otros perfiles.
- Añadir MFA y recuperación segura de cuentas antes de abrir acceso externo.
- Separar rol de migraciones del rol de ejecución para eliminar DDL del usuario operativo.
- Cifrar discos y respaldos con claves gestionadas fuera del servidor; los dumps actuales no están cifrados. Programar copias externas y ensayar restauración por empresa.
- Centralizar alertas y auditoría con retención e integridad independientes; definir responsables, recuperación y respuesta a incidentes.
- Validar concurrencia, carga, límites de archivos y cálculos contables con casos reales controlados.

Referencias utilizadas: [seguridad en Django 6.0](https://docs.djangoproject.com/en/6.0/topics/security/),
[validadores de contraseñas](https://docs.djangoproject.com/en/6.0/topics/auth/passwords/) y
[creación de bases PostgreSQL](https://www.postgresql.org/docs/current/sql-createdatabase.html).

## Accesos locales adicionales — 2026-10-04

Por solicitud del propietario se crearon `local.admin` (Administrador) y
`local.consulta` (Solo lectura) en ambas empresas, con claves sencillas entregadas
al propietario. No se alteraron las cuentas existentes ni los validadores generales
de contraseñas. Se verificaron los cuatro logins y la denegación de administración
de usuarios para consulta. El frontend local se inició escuchando en 127.0.0.1.
