# ERP_api - API interna y explorador visual

Fecha de referencia: 2026-08-16

## Proposito

ERP_api conserva los endpoints iniciales y agrega una API v1 consumida por Next.js para sesion, catalogos, recursos CRUD, reportes, cargas ETL y usuarios.

Es una API inicial para integracion local o herramientas internas, no una API publica de internet.

## Seguridad

La API requiere sesion. Los endpoints que exponen informacion de remuneraciones requieren permiso de acceso al modulo de remuneraciones.

El explorador visual respeta los permisos del usuario: las rutas restringidas se muestran bloqueadas si el usuario no tiene `DATA_scope.access_payroll_module`.

## Endpoints

| Ruta | Descripcion |
| --- | --- |
| `/api/` | Explorador visual en cascada con rutas, permisos y ejemplo de respuesta |
| `/api/?format=json` | Indice JSON de endpoints |
| `/api/health/` | Salud del servicio |
| `/api/system-status/` | Estado operativo |
| `/api/modules/` | Modulos activos y proximos |
| `/api/payroll/summary/` | Conteos principales de remuneraciones |
| `/api/payroll/periods/` | Ultimos periodos |
| `/api/v1/session/` | Estado de sesion, usuario y permisos efectivos |
| `/api/v1/login/` | Inicio de sesion JSON con CSRF |
| `/api/v1/logout/` | Cierre de sesion |
| `/api/v1/catalog/` | Catalogo de recursos visibles |
| `/api/v1/resources/<recurso>/` | Listado, alta y consulta CRUD autorizada |
| `/api/v1/reports/` | Reportes, filtros y series para graficos |
| `/api/v1/uploads/` | Carga masiva ETL e historial |
| `/api/v1/users/` | Administracion protegida de usuarios y roles |

## Explorador visual

La ruta `/api/` renderiza una pantalla Bootstrap con acordeon:

- Cada endpoint aparece como una fila plegable.
- Solo una fila queda abierta a la vez.
- Se muestran metodo, ruta, URL completa, permiso requerido y ejemplo de respuesta.
- El primer endpoint queda abierto por defecto para orientar al usuario.
- Para integraciones que necesiten JSON, usar `/api/?format=json`.

## Ejemplo de estado

```json
{
  "django": "operativo",
  "database": "connected",
  "data_scope": "activo",
  "external_etl": "disponible",
  "auto_backup": {
    "enabled": true,
    "interval_minutes": 90
  },
  "version": "1.0.8"
}
```

## Estado actual

La API esta activa, protegida por login/permisos y con explorador visual interno, pero aun no tiene:

- Paginacion formal.
- Filtros avanzados.
- Endpoints de detalle por trabajador.
- Endpoints de detalle por liquidacion.
- Versionado formal de API.
- Tokens o autenticacion no interactiva.

## Recomendacion

Antes de uso multiusuario real:

1. Agregar tests de permisos por endpoint.
2. Agregar paginacion.
3. Agregar filtros.
4. Definir versionado.
5. Definir si se necesitara autenticacion por token para integraciones internas.
