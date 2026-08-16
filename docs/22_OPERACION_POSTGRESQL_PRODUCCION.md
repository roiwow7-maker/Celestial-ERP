# Operacion PostgreSQL y produccion

Fecha: 2026-08-07

## Controles implementados

- `backup_database`: dump PostgreSQL verificado y con retencion.
- `validate_postgresql_restore`: restauracion real en cluster temporal aislado.
- `compare_sqlite_postgresql`: conteos y sumas de control entre origen y destino.
- `check_postgresql_operational_health`: conexion, version, tamano, actividad, disco, logs y edad del backup.
- `tools/run_postgresql_tests.py`: suite completa sobre PostgreSQL temporal independiente.
- `sync_nominal_users`: alta/validacion de identidades desde manifiesto privado.
- `cleanup_uploads`: retencion de archivos sensibles.

## Servicios

`deploy/` contiene unidades de ejemplo para:

- Gunicorn persistente;
- backup diario;
- limpieza diaria de uploads;
- diagnostico horario;
- frontend Next.js persistente en `127.0.0.1:3000`;
- Nginx con redireccion HTTPS y proxy al frontend Next.js, que mantiene Gunicorn privado en `127.0.0.1:8000`.

Los archivos deben revisarse, copiarse a las rutas del servidor y adaptarse al usuario, dominio y certificados reales. Los ejemplos no contienen secretos.

## Credenciales

La aplicacion carga `.env` local mediante `python-dotenv`, pero en produccion systemd debe inyectar `/etc/celestial-erp/erp.env` con permisos `600`. No existe contraseña PostgreSQL por defecto en el codigo.

## Usuarios nominales

Crear un manifiesto privado basado en `config/users.example.json` y ejecutar:

```bash
python manage.py sync_nominal_users /ruta/usuarios.json --credentials-output /ruta/credenciales-temporales.json
python manage.py sync_nominal_users /ruta/usuarios.json --validate-only
```

Las claves temporales se guardan con modo `600` y deben entregarse por canal seguro. El usuario debe cambiarlas al primer acceso mediante el procedimiento definido por la organizacion.

## Cola de trabajos

Decision actual: mantener el proceso background existente mientras exista una sola instancia Django y baja simultaneidad. Adoptar una cola dedicada (Celery/RQ y broker) cuando ocurra cualquiera de estos criterios:

- dos o mas cargas ETL simultaneas;
- multiples instancias de Gunicorn/servidores que deban compartir estado de trabajos;
- necesidad de reintentos automaticos, prioridades o cancelacion;
- tiempos superiores a 30 minutos recurrentes;
- perdida de trabajos ante reinicios.

Esta decision evita infraestructura innecesaria ahora y deja criterios objetivos para escalar.

## Reglas de negocio

La validacion automatica detecta diferencias tecnicas, pero la aprobacion legal/funcional debe registrar nombre, cargo, fecha, version de reglas y observaciones de RRHH/Contabilidad. No puede reemplazarse por una prueba de software.
