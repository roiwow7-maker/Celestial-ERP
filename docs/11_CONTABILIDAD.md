# Contabilidad

Fecha de referencia: 2026-07-13

Version documentada del modulo: `0.7.5a`

Version operativa del sistema: `1.0.8`

## Estado

El modulo `Accounting` queda activo como base contable inicial de Celestial ERP.

## Alcance cerrado

- `v0.7.1`: plan de cuentas.
- `v0.7.2`: centros de costo.
- `v0.7.3`: mapeo item remuneracion a cuenta contable.
- `v0.7.4`: asientos contables desde remuneraciones por periodo.
- `v0.7.5`: reportes contables iniciales.
- `v0.7.5a`: pulido visual de reportes y metricas.

## Rutas

| Ruta | Uso |
| --- | --- |
| `/contabilidad/` | Dashboard contable. |
| `/contabilidad/plan-cuentas/` | Plan de cuentas. |
| `/contabilidad/centros-costo/` | Centros de costo. |
| `/contabilidad/mapeos/` | Mapeos item-cuenta. |
| `/contabilidad/asientos/` | Asientos contables. |
| `/contabilidad/asientos/generar-remuneraciones/` | Generacion de asiento desde periodo de remuneraciones. |
| `/contabilidad/reportes/` | Reportes iniciales. |

## Modelos

| Modelo | Uso |
| --- | --- |
| `ChartAccount` | Cuenta contable del plan de cuentas. |
| `CostCenter` | Centro de costo. |
| `PayrollItemAccountMapping` | Relacion entre `PayrollItem` y cuenta contable. |
| `JournalEntry` | Cabecera de asiento contable. |
| `JournalEntryLine` | Linea de asiento con Debe/Haber. |

## Comandos

Preparar catalogo inicial:

```powershell
python manage.py seed_accounting_catalog
```

Generar asiento por periodo:

```powershell
python manage.py generate_payroll_journal_entries 202606
python manage.py generate_payroll_journal_entries 202606 --replace-existing
```

## Catalogo base

El comando `seed_accounting_catalog` crea cuentas de remuneraciones, pasivos, descuentos y centros `GEN`/`RRHH`. Luego mapea los items existentes segun categoria de remuneracion.

## Asientos

La generacion de asientos usa `PayrollEntry` por periodo y agrupa por:

- cuenta contable
- centro de costo
- tipo de movimiento: Debe o Haber

Si queda diferencia, agrega contrapartida automatica a `2101 - Remuneraciones por pagar`.

## Validacion actual

Se genero el asiento operativo:

```text
REM-202606
Debe: 574960609
Haber: 574960609
Cuadrado: si
```

## Pendientes contables futuros

- Validar plan de cuentas contra un contador o sistema externo real.
- Definir reglas por empresa, division o centro de costo real.
- Exportar asientos a formato externo si se requiere.
- Agregar cierre/aprobacion de asientos.
- Agregar reportes por centro de costo y periodo.
