# Reglas de negocio de remuneraciones

Fecha de referencia: 2026-07-13

Este documento describe las reglas actualmente implementadas por el ETL y el ERP. No reemplaza una validacion legal/contable formal, pero deja las formulas explicitas para revision funcional.

Version operativa actual del sistema: `1.0.3`.

## 1. Identificacion de liquidacion

La liquidacion se identifica por:

- `periodo`
- `codigo`

El numero de documento se genera como:

```text
periodo-codigo
```

## 2. Categorias usadas

Los movimientos se clasifican por `categoria_item`:

- `haberes_normales_imponibles`
- `haberes_exentos_no_imponibles`
- `asignaciones_familiares`
- `descuentos_legales_previsionales`
- `otros_descuentos`
- `contribucion_empleador`
- `provisiones`
- `totales`

## 3. Totales principales

### Total Haberes Imponibles

Suma de movimientos cuya categoria es:

- `haberes_normales_imponibles`

### Total Haberes No Imponibles

Suma de movimientos cuyas categorias son:

- `haberes_exentos_no_imponibles`
- `asignaciones_familiares`

### Total Descuentos Legales

Suma de movimientos cuya categoria es:

- `descuentos_legales_previsionales`

### Total Otros Descuentos

Suma de movimientos cuya categoria es:

- `otros_descuentos`

### Sueldo Liquido

El sueldo liquido no se calcula desde haberes y descuentos. Se toma directamente del codigo fuente:

```text
codigo_item = A000
```

El codigo `A000` esta descrito como `Sueldo Liquido` en los archivos de descripciones. Si una liquidacion no trae `A000`, el sueldo liquido queda en `0` hasta que negocio confirme otro codigo equivalente.

El campo `Saldo Sobregiro*` queda en `0` mientras no exista un codigo fuente confirmado para sobregiro.

### Costo Empresa

Formula actual:

```text
haberes_imponibles
+ haberes_no_imponibles
+ contribucion_empleador
+ provisiones
```

## 4. Validacion automatica

El comando:

```powershell
python manage.py validate_business_rules
```

genera:

```text
reports/business_rules_validation.csv
```

El reporte compara los totales guardados en `PayrollSummary` contra los movimientos reales de `PayrollEntry` por trabajador y periodo, incluyendo que `Sueldo Liquido*` calce con el codigo `A000`.

## 5. Pendientes funcionales

- Confirmar maestro oficial de codigos.
- Confirmar codigos que requieren aprobacion.
- Confirmar tratamiento de finiquitos.
- Confirmar tratamiento de provisiones.
- Confirmar si el sueldo liquido debe calcularse o recibirse como valor oficial desde sistema fuente.
