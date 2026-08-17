# Administracion y multiusuario

Fecha de referencia: 2026-08-16

## Proposito

El sistema esta pensado para uso local o red interna controlada. La version `1.2.1` mantiene Django Admin como respaldo técnico y agrega administracion nativa de usuarios/roles en Next.js, restringida por `Applet.access_security_module`.

## Admin Django

Ruta:

```text
/admin/
```

El admin permite gestionar:

- Usuarios.
- Grupos y permisos.
- Trabajadores.
- Periodos.
- Items de remuneracion.
- Movimientos.
- Liquidaciones.
- Corridas ETL.
- Auditoria.
- Contabilidad.
- Inventario.
- Compras y ventas.

## Login obligatorio

Rutas operativas como `/applet/`, `/remuneraciones/`, `/reportes/`, `/cargas/`, `/contabilidad/`, `/inventario/`, `/comercio/`, `/kanban/` y `/api/` requieren sesion.

Ruta de ingreso:

```text
/login/
```

## Roles funcionales

Roles preparados:

- Administrador.
- RRHH.
- Contabilidad.
- Solo lectura.

Comando para crear o actualizar roles:

```powershell
python manage.py setup_access_control
```

## Permisos sensibles

Acciones restringidas:

- Acceder a administracion.
- Acceder a seguridad y auditoria.
- Ejecutar backups.
- Ver modulo de remuneraciones.
- Cambiar estados de trabajadores.
- Subir archivos ETL.
- Importar al ERP.
- Limpiar datos antes de importar.
- Descargar salidas de cargas.
- Consultar endpoints API de remuneraciones.
- Gestionar contabilidad.
- Gestionar inventario.
- Gestionar proveedores, clientes, compras y ventas.

## Usuario local de desarrollo

Existe un superusuario local:

- Usuario: `root`
- Clave: `root`

Debe cambiarse antes de uso compartido.

## Multiusuario

SQLite es suficiente para desarrollo y prototipo local. Para operacion multiusuario sostenida se recomienda PostgreSQL.

Orden recomendado:

1. Mantener usuarios nominales por rol.
2. Ejecutar pruebas automaticas antes de cambios.
3. Validar reglas de negocio por modulo.
4. Probar restauracion de backups periodicamente.
5. Migrar a PostgreSQL antes de uso concurrente serio.

## Pendientes

- Rotacion de claves y politica de usuarios.
- Politica de bloqueo/desactivacion de usuarios.
- Auditoria granular de cambios manuales.
- PostgreSQL en servidor autorizado.
