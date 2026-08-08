# v1.0.4-v1.0.8 - Base estable previa a PostgreSQL

Fecha de referencia: 2026-07-14

Version operativa: `1.0.8`

## Alcance

Este documento cierra los hitos `v1.0.4` a `v1.0.8` sin instalar PostgreSQL en el equipo actual. La prioridad es operar de forma controlada con SQLite, backups restaurables, auditoria verificable y planes listos para mover el sistema a servidor autorizado.

## v1.0.4 - Backups reales con restauracion validada

Comando operativo:

```powershell
python Celestial_ERP\manage.py validate_backup_restore
```

Uso con backup especifico:

```powershell
python Celestial_ERP\manage.py validate_backup_restore --backup-path backups\db_AAAAMMDD_HHMMSS.sqlite3
```

El comando:

- usa el ultimo backup si no se entrega ruta;
- copia el backup a una ubicacion temporal;
- abre la copia restaurada sin tocar la base activa;
- ejecuta `pragma integrity_check`;
- verifica tablas criticas de remuneraciones y auditoria;
- reporta conteos por tabla.

Para inspeccion manual:

```powershell
python Celestial_ERP\manage.py validate_backup_restore --keep-restored-copy
```

## v1.0.5 - Auditoria validada por usuario/rol

La auditoria queda validada con usuarios nominales:

- cada evento conserva `user`;
- el usuario conserva sus grupos funcionales;
- las acciones manuales guardan objeto, ID, representacion y cambios JSON cuando aplica;
- la vista de auditoria permite filtrar por modulo, accion, objeto, ID y texto.

Prueba automatica cubierta:

```powershell
python Celestial_ERP\manage.py test Applet
```

## v1.0.6 - Plan de migracion de datos

Fases recomendadas:

1. Congelar ventana de cambios.
2. Ejecutar backup SQLite.
3. Validar restauracion con `validate_backup_restore`.
4. Ejecutar `check_sqlite_operational_health`.
5. Exportar inventario de tablas y conteos.
6. Ensayar migracion en copia, nunca directo sobre produccion.
7. Comparar conteos origen/destino.
8. Probar login, reportes, cargas, auditoria y modulos criticos.
9. Documentar responsable, fecha, backup usado y resultado.

Criterio de corte: no migrar si falla integridad, restauracion, conteos base o permisos.

## v1.0.7 - IA local cuantizada como servicio separado

La IA local no debe correr dentro del proceso Django.

Arquitectura recomendada:

- servidor LAN separado;
- endpoint HTTP interno;
- modelo cuantizado cargado en servicio propio;
- acceso desde Celestial ERP solo por API;
- sin acceso directo a la base productiva;
- logs separados;
- timeouts y limites de memoria;
- apagado seguro si el servidor IA no responde.

El equipo dual Xeon puede servir como nodo LAN si se valida consumo electrico, temperatura, estabilidad y compatibilidad de GPU.

## v1.0.8 - Preparacion PostgreSQL en servidor autorizado

PostgreSQL queda preparado documentalmente, no instalado en el equipo limitado.

Checklist previo:

- servidor autorizado disponible;
- usuario de sistema nominal;
- credenciales fuera del repo;
- backup SQLite validado;
- restauracion probada;
- plan de reversa;
- ventana de mantenimiento;
- pruebas automaticas verdes;
- acceso LAN controlado;
- `ALLOWED_HOSTS` y variables de produccion definidas.

Pendiente real:

- `v1.0.9`: ensayo SQLite a PostgreSQL en servidor autorizado.
- `v1.0.10`: migracion real solo con infraestructura y permisos.
