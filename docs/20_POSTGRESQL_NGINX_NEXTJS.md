# PostgreSQL, Nginx y frontend Next.js

> Estado `1.2.1`: PostgreSQL y Next.js ya estan implementados. La configuracion productiva vigente usa nginx hacia Next.js en `127.0.0.1:3000`; Next.js proxy hacia Django en `127.0.0.1:8000`. Las fases de migracion desde SQLite se conservan como historial.

## 1. Objetivo y arquitectura

Este documento define el procedimiento para evolucionar Celestial ERP desde SQLite y vistas Django hacia PostgreSQL, Django como backend/API, Next.js como frontend y Nginx como unico punto de entrada.

```text
Usuarios LAN
    |
    v
Nginx :80/:443 (servidor de aplicacion)
    |
    +-- /, /_next/* ----------> Next.js :3000
    +-- /api/*, /admin/* -----> Django/Gunicorn :8001
    +-- /static/* ------------> archivos estaticos Django
                                  |
                                  v
                          PostgreSQL :5432
                          (servidor separado)
```

Principios:

- Nginx es el unico servicio web visible para los navegadores.
- Django conserva reglas de negocio, autenticacion, permisos, auditoria, ETL y acceso a datos.
- Next.js implementa la interfaz y consume la API de Django.
- Solo Django puede conectarse a PostgreSQL.
- PostgreSQL no se publica en internet ni se conecta directamente con el navegador.
- La migracion se ensaya antes de reemplazar SQLite.
- SQLite se conserva intacto hasta validar PostgreSQL y el plan de reversa.

## 2. Decision de infraestructura

La opcion recomendada es instalar PostgreSQL en una segunda maquina fisica con IP fija dentro de la LAN. Si no existe, se puede usar una VM para el ensayo. Una VM ubicada en el mismo equipo del ERP aisla servicios, pero no protege contra una falla fisica del anfitrion.

| Componente | Ubicacion recomendada |
| --- | --- |
| PostgreSQL | Segunda maquina con IP fija |
| Django + Gunicorn | Servidor actual del ERP |
| Next.js | Servidor actual, como servicio separado |
| Nginx | Servidor actual, delante de Django y Next.js |
| Backups | Servidor PostgreSQL y otra ubicacion independiente |

Se utilizara una version estable y soportada. A agosto de 2026, PostgreSQL 18 es estable y PostgreSQL 19 sigue en desarrollo; no se usara una beta con datos reales.

## 3. Estado actual y cambios necesarios

`Celestial_ERP/Celestial_ERP/settings/base.py` utiliza actualmente `django.db.backends.sqlite3`. Antes del cambio se debe:

- incorporar `psycopg` y un servidor WSGI como Gunicorn;
- crear configuracion PostgreSQL mediante variables de entorno;
- adaptar los comandos de salud y backup exclusivos de SQLite;
- ampliar y estabilizar la API para Next.js;
- probar migraciones, permisos, ETL y reglas de negocio con PostgreSQL;
- dejar de usar `runserver` como servidor productivo.

## 4. Servidor PostgreSQL

### 4.1 Requisitos

- Linux estable y actualizado.
- IP fija o reserva DHCP y hora sincronizada.
- SSD, idealmente 4 a 8 GB de RAM y al menos 2 nucleos.
- Firewall activo y acceso administrativo nominal por SSH.
- UPS si almacenara datos operativos.

Registrar antes de instalar:

```text
IP_SERVIDOR_APP=<IP de Django/Nginx>
IP_SERVIDOR_DB=<IP de PostgreSQL>
NOMBRE_DB=celestial_erp
USUARIO_DB=celestial_app
PUERTO_DB=5432
```

Las contraseñas reales no se escriben en documentos, scripts ni archivos versionados.

### 4.2 Instalacion

En Ubuntu Server, Debian o Linux Mint, instalar una version estable desde un repositorio confiable:

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl enable --now postgresql
sudo systemctl status postgresql
sudo -u postgres psql -c "SELECT version();"
```

No continuar si el servicio no esta activo o `dpkg` informa una instalacion interrumpida.

### 4.3 Base y rol

Generar la contraseña con un gestor de contraseñas y abrir `psql`:

```bash
sudo -u postgres psql
```

```sql
CREATE ROLE celestial_app
    WITH LOGIN
    NOSUPERUSER
    NOCREATEDB
    NOCREATEROLE
    NOREPLICATION
    PASSWORD '<CONTRASEÑA_SEGURA>';

CREATE DATABASE celestial_erp
    OWNER celestial_app
    ENCODING 'UTF8'
    TEMPLATE template0;

\q
```

Django nunca debe conectarse con el usuario `postgres`.

### 4.4 Red, autenticacion y firewall

En `postgresql.conf`, escuchar solo en la IP privada necesaria:

```conf
listen_addresses = '<IP_SERVIDOR_DB>'
password_encryption = 'scram-sha-256'
```

En `pg_hba.conf`, permitir solo al servidor de aplicacion:

```conf
host    celestial_erp    celestial_app    <IP_SERVIDOR_APP>/32    scram-sha-256
```

```bash
sudo systemctl reload postgresql
sudo ufw allow from <IP_SERVIDOR_APP> to any port 5432 proto tcp
sudo ufw status verbose
```

No usar `0.0.0.0/0`, autenticacion `trust` ni redireccionar 5432 desde el router.

### 4.5 TLS

El objetivo productivo es cifrar Django-PostgreSQL con TLS:

- configurar certificado y CA en PostgreSQL;
- cambiar la regla a `hostssl`;
- usar `sslmode=verify-full` en Django;
- instalar la CA confiable en el servidor de aplicacion;
- no dejar `sslmode=disable` como solucion permanente.

## 5. Preparacion de Django

### 5.1 Dependencias

Agregar al entorno virtual, con versiones fijadas después del ensayo:

```text
psycopg[binary]
gunicorn
```

`psycopg[binary]` simplifica el laboratorio. Antes de produccion se evaluara la variante recomendada para el sistema operativo definitivo.

### 5.2 Variables protegidas

```bash
ERP_SETTINGS_ENV=prod
DJANGO_DB_ENGINE=postgresql
DJANGO_DB_NAME=celestial_erp
DJANGO_DB_USER=celestial_app
DJANGO_DB_PASSWORD=<CONTRASEÑA_SEGURA>
DJANGO_DB_HOST=<IP_SERVIDOR_DB>
DJANGO_DB_PORT=5432
DJANGO_DB_SSLMODE=prefer
DJANGO_SECRET_KEY=<SECRETO_LARGO_Y_UNICO>
DJANGO_ALLOWED_HOSTS=erp.empresa.local
DJANGO_CSRF_TRUSTED_ORIGINS=https://erp.empresa.local
```

Cuando TLS este validado, cambiar a `DJANGO_DB_SSLMODE=verify-full`. El archivo que contenga secretos debe permanecer fuera del repositorio y con permisos `600`.

### 5.3 Configuracion objetivo

Django seleccionara SQLite o PostgreSQL explícitamente por ambiente. La configuracion PostgreSQL tendra esta forma:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ["DJANGO_DB_NAME"],
        "USER": os.environ["DJANGO_DB_USER"],
        "PASSWORD": os.environ["DJANGO_DB_PASSWORD"],
        "HOST": os.environ["DJANGO_DB_HOST"],
        "PORT": os.environ.get("DJANGO_DB_PORT", "5432"),
        "CONN_MAX_AGE": 60,
        "OPTIONS": {
            "sslmode": os.environ.get("DJANGO_DB_SSLMODE", "prefer"),
        },
    }
}
```

No se reemplazara directamente SQLite antes del ensayo.

## 6. Migracion de ensayo desde SQLite

### 6.1 Condiciones previas

- pruebas Django en verde;
- `manage.py check` sin errores;
- backup SQLite validado y copiado fuera del servidor;
- PostgreSQL de ensayo vacio;
- credenciales y ambiente separados de produccion;
- plan de reversa y ventana de mantenimiento.

### 6.2 Exportar

Detener escrituras y ejecutar:

```bash
python Celestial_ERP/manage.py backup_sqlite
python Celestial_ERP/manage.py validate_backup_restore

python Celestial_ERP/manage.py dumpdata \
  --natural-foreign \
  --natural-primary \
  --exclude contenttypes \
  --exclude auth.permission \
  --exclude admin.logentry \
  --exclude sessions \
  --indent 2 \
  --output /ruta/segura/celestial_sqlite_export.json
```

La exportacion contiene datos personales y remuneraciones: debe permanecer cifrada o en una ubicacion restringida y nunca entrar al repositorio.

### 6.3 Crear esquema y cargar

Activar la configuracion PostgreSQL de ensayo:

```bash
python Celestial_ERP/manage.py check
python Celestial_ERP/manage.py migrate
python Celestial_ERP/manage.py showmigrations
python Celestial_ERP/manage.py loaddata /ruta/segura/celestial_sqlite_export.json
python Celestial_ERP/manage.py setup_access_control
```

No usar `--fake` sin un analisis especifico. Si la carga falla, registrar el error, corregir el procedimiento, recrear la base de ensayo y repetir; no improvisar sobre produccion.

### 6.4 Validar

```bash
python Celestial_ERP/manage.py check
python Celestial_ERP/manage.py makemigrations --check --dry-run
python Celestial_ERP/manage.py test Applet DATA_scope ERP_api Accounting Inventory Commerce Attendance
python Celestial_ERP/manage.py validate_business_rules
python Celestial_ERP/manage.py check_operational_security
```

Comparar SQLite y PostgreSQL:

- empleados, periodos, liquidaciones, items y resumenes;
- usuarios, grupos y permisos;
- asistencia;
- cuentas, asientos y lineas contables;
- productos, bodegas, movimientos y saldos;
- clientes, proveedores, compras y ventas;
- totales monetarios por periodo y categoria;
- acceso a API y pantallas según cada rol;
- una carga ETL pequeña y reversible.

La migracion no se aprueba solo porque Django inicie: conteos y totales deben coincidir.

## 7. Corte definitivo y reversa

### Corte

1. Comunicar la ventana de mantenimiento.
2. Detener Next.js, Gunicorn y procesos ETL con escritura.
3. Crear y validar el ultimo backup SQLite.
4. Registrar conteos y totales de control.
5. Exportar nuevamente desde SQLite.
6. Preparar PostgreSQL limpio, ejecutar migraciones y cargar datos.
7. Repetir todas las validaciones.
8. Iniciar Gunicorn y Next.js y probarlos localmente.
9. Activar Nginx y probar mediante la URL final.
10. Conservar SQLite como respaldo sin permitir nuevas escrituras.

### Reversa

Si falla una validacion critica:

1. bloquear temporalmente el acceso en Nginx;
2. detener Django y los ETL;
3. restaurar las variables de entorno SQLite;
4. verificar que SQLite no recibio escrituras durante el intento;
5. iniciar la version anterior y ejecutar controles de salud;
6. documentar el incidente.

No operar SQLite y PostgreSQL en paralelo aceptando escrituras ni intentar conciliarlas manualmente.

## 8. Django como API

Next.js no duplicara reglas ni consultara PostgreSQL. Django ofrecera endpoints versionados, por ejemplo:

```text
/api/v1/auth/
/api/v1/employees/
/api/v1/payroll-periods/
/api/v1/payroll/
/api/v1/attendance/
/api/v1/accounting/
/api/v1/inventory/
/api/v1/commerce/
```

Antes de las pantallas se definira:

- formato uniforme de respuestas y errores;
- paginacion, filtros y ordenamiento;
- autenticacion, sesion y CSRF;
- permisos por endpoint y accion;
- validacion y auditoria en Django;
- limites de archivos y exportaciones;
- contrato OpenAPI o equivalente;
- pruebas de integracion.

Servir Next.js y Django bajo el mismo origen (`https://erp.empresa.local`) simplifica cookies, CSRF y evita habilitar CORS ampliamente.

## 9. Frontend Next.js

Crear un proyecto separado, por ejemplo `frontend/`, con TypeScript y App Router. Next.js se ocupara de interfaz, navegacion, estados y consumo de API.

Next.js no debe:

- contener credenciales PostgreSQL;
- conectarse directamente a la base;
- confiar permisos solamente al navegador;
- colocar secretos en variables `NEXT_PUBLIC_*`;
- convertirse en la fuente de verdad de calculos sensibles.

Variables conceptuales:

```bash
# Solo disponible para el proceso servidor de Next.js.
DJANGO_INTERNAL_URL=http://127.0.0.1:8001

# Visible para el navegador; nunca contiene secretos.
NEXT_PUBLIC_APP_URL=https://erp.empresa.local
```

Inicialmente se usara una sola instancia persistente de `next start`, administrada por `systemd`. Varias instancias requeririan coordinacion del cache de Next.js.

## 10. Nginx

Configuracion conceptual inicial:

```nginx
upstream celestial_next {
    server 127.0.0.1:3000;
    keepalive 32;
}

upstream celestial_django {
    server 127.0.0.1:8001;
    keepalive 16;
}

server {
    listen 80;
    server_name erp.empresa.local;
    client_max_body_size 25m;

    location /static/ {
        alias /ruta/absoluta/ETL/staticfiles/;
        access_log off;
        expires 7d;
    }

    location /api/ {
        proxy_pass http://celestial_django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_read_timeout 120s;
    }

    location /admin/ {
        proxy_pass http://celestial_django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        proxy_pass http://celestial_next;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_buffering off;
    }
}
```

Antes de recargar:

```bash
sudo nginx -t
sudo systemctl reload nginx  # solo si la prueba fue correcta
```

La version final agregara HTTPS, encabezados de seguridad, limites de tasa, logs rotados y una politica explícita para archivos privados. Los archivos de remuneraciones no deben quedar bajo una ruta publica.

## 11. Servicios

```text
postgresql.service          # segunda maquina
celestial-django.service    # Gunicorn
celestial-next.service      # next start
nginx.service
```

Cada servicio tendra usuario sin privilegios, directorio explicito, secretos protegidos, reinicio controlado, logs en `journalctl`, limites de recursos e inicio después de la red.

## 12. Backups PostgreSQL

`backup_sqlite` no cubre PostgreSQL. Antes del corte se implementara un procedimiento nuevo.

Backup logico diario:

```bash
pg_dump \
  --format=custom \
  --no-owner \
  --file=/ruta/segura/celestial_erp_$(date +%Y%m%d_%H%M%S).dump \
  celestial_erp
```

Prueba periodica en una base temporal:

```bash
createdb celestial_restore_test
pg_restore --exit-on-error --no-owner \
  --dbname=celestial_restore_test <archivo.dump>
```

Validar luego conteos y consultas. La base temporal solo se elimina después de verificar exactamente su nombre y confirmar el resultado.

Politica minima:

- backup diario automatizado;
- retencion diaria, semanal y mensual;
- copia cifrada fuera del servidor PostgreSQL;
- alerta por fallos o poco espacio;
- restauracion de prueba mensual;
- backup adicional antes de migraciones o despliegues importantes.

## 13. Fases

### A. Laboratorio PostgreSQL

- preparar segunda maquina o VM;
- hacer seleccionable la base en Django;
- instalar Psycopg;
- migrar una copia y automatizar comparaciones.

### B. API

- inventariar acciones actuales;
- diseñar `/api/v1/`;
- implementar autenticacion, permisos, CSRF y auditoria;
- agregar pruebas de contrato.

### C. Frontend

- crear `frontend/` con Next.js y TypeScript;
- construir diseño, login y navegacion;
- migrar un modulo a la vez sin retirar prematuramente Django;
- comprobar permisos y accesibilidad.

### D. Nginx y servicios

- crear servicios Gunicorn y Next.js;
- configurar Nginx en LAN y luego HTTPS;
- probar archivos, timeouts, reinicios y carga.

### E. Corte

- congelar escrituras;
- exportar, migrar y validar;
- habilitar PostgreSQL;
- observar intensivamente los primeros dias;
- conservar la reversa hasta aprobar el cierre.

## 14. Criterios de finalizacion

- PostgreSQL solo acepta equipos autorizados.
- Django es el unico componente con credenciales de base.
- tests, reglas de negocio, conteos y totales coinciden.
- Nginx publica Next.js y Django bajo una URL unica.
- HTTPS y cookies seguras estan activos.
- roles y auditoria funcionan correctamente.
- existe backup automatizado y restauracion probada.
- SQLite queda archivado sin escrituras.

## 15. Referencias oficiales

- PostgreSQL, versiones: <https://www.postgresql.org/support/versioning/>
- PostgreSQL, autenticacion: <https://www.postgresql.org/docs/current/client-authentication.html>
- PostgreSQL, `pg_hba.conf`: <https://www.postgresql.org/docs/current/auth-pg-hba-conf.html>
- PostgreSQL, TLS: <https://www.postgresql.org/docs/current/ssl-tcp.html>
- PostgreSQL, backup y restauracion: <https://www.postgresql.org/docs/current/backup.html>
- Django 6.0 y PostgreSQL: <https://docs.djangoproject.com/en/6.0/topics/install/>
- Django, despliegue: <https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/>
- Next.js, self-hosting: <https://nextjs.org/docs/app/guides/self-hosting>
- Next.js, Backend for Frontend: <https://nextjs.org/docs/app/guides/backend-for-frontend>
- Nginx, proxy HTTP: <https://nginx.org/en/docs/http/ngx_http_proxy_module.html>
