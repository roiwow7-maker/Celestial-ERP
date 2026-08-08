# Mantenimiento y roadmap

Fecha de referencia: 2026-07-13

Version documentada: `1.0.8`

## Checklist despues de cambios

Ejecutar:

```powershell
cd Celestial_ERP
python manage.py check
python manage.py test Applet DATA_scope ERP_api Accounting Inventory Commerce Attendance
```

Si se toca ETL:

```powershell
cd ..
python run_etl.py --skip-import
```

Si se toca importacion:

```powershell
cd Celestial_ERP
python manage.py import_payroll_data
python manage.py validate_business_rules
```

## Versionado

Actualizar en este orden:

1. `Celestial_ERP/Applet/services.py`
2. templates visibles si tienen texto hardcodeado
3. `ROADMAP.md`
4. `version_log.md`
5. `docs/`
6. `docs/assets/`

La version actual es `1.0.8`.

## Pendientes reales

| Prioridad | Pendiente | Nota |
| --- | --- | --- |
| Alta | Recalculo automatico de liquidaciones | Al editar movimientos, los resumenes no se recalculan automaticamente. |
| Cerrado | Auditoria granular avanzada | Existe filtro por objeto/campo estructurado y cambios JSON. |
| Media | Cola real de trabajos | El background simple existe; cola dedicada solo si crece el volumen. |
| Media | Rotacion por tiers de backups | Hoy hay retencion simple por dias y minimo de copias. |
| Media | PostgreSQL | Movido al final de v1.0.x por permisos/infraestructura. |
| Baja | PDF server-side | Hoy se puede imprimir/exportar desde navegador. |

## Roadmap resumido

### v0.7 - Contabilidad

Cerrada como base contable inicial.

### v0.8 - Inventario

Cerrada como base inicial de inventario.

### v0.9 - Compras, ventas y asistencia

Cerrada como base inicial comercial, de asistencia, operacion SQLite reforzada, auditoria granular e integracion asistencia-remuneraciones. PostgreSQL queda al final de `v1.0.x`.

### v0.9 - Pendientes tecnicos

- compras
- proveedores
- ventas
- clientes
- asistencia historica
- operacion SQLite reforzada sin PostgreSQL
- auditoria granular avanzada cerrada
- integracion asistencia-remuneraciones cerrada

### v1.0 - Primera estable

- testing amplio
- documentacion operativa cerrada
- despliegue LAN documentado
- backups reales con restauracion validada
- auditoria validada por usuario/rol
- plan de migracion de datos
- IA local cuantizada como servicio LAN separado

## Recomendacion operativa con hardware limitado

Mantener SQLite mientras:

- el uso sea local o de pocos usuarios
- no haya escrituras concurrentes pesadas
- existan backups frecuentes
- se limpie `uploads/`
- se validen cargas antes de importarlas

Postergar PostgreSQL hasta el final de `v1.0.x`, despues de testing, documentacion, LAN, backups, auditoria validada e IA local separada.

## IA local

La IA local cuantizada no debe correr dentro del proceso Django. Cuando llegue v1.0.x, tratarla como servicio separado:

- endpoint HTTP interno
- modelo cuantizado
- limites de memoria
- logs separados
- cola o timeout
- sin acceso directo a DB productiva salvo API controlada

