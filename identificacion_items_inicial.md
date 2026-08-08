# Identificacion inicial de items payroll

Fecha de referencia: 2026-07-13

Fuente: `ITEMS_ACUMULADOS_Historico Payroll.xlsx`

Nota: documento historico de clasificacion inicial. Sigue vigente como referencia ETL, pero el sistema actual esta en version `0.9.4`.

- Hoja: `Sheet1`
- Filas: 19719
- Columnas: 150
- Periodos: 201701 a 202606
- Items con monto distinto de cero: 130
- Resumen cuantitativo: `resumen_items_historico.csv`

## Columnas de persona/liquidacion

`codigo`, `nombre`, `Codigo A.F.P.`, `Isapre`, `diastr`, `Division`,
`Fecha de Ingreso`, `Fecha de Retiro`, `Horario de trabajo`, `Jornada: V / S`,
`Jornada de contrato`, `Rut`, `periodo`

## Haberes normales imponibles

Primera identificacion por codigos de sueldo, bonos, horas extra, gratificacion,
vacaciones remuneradas y diferencias/remuneraciones.

`000011`, `A000`, `AGUCIA`, `AGUINA`, `BOASIG`, `BODESE`, `BOESPE`, `BONCIA`,
`BONCOM`, `BONCON`, `BONDEF`, `BONESC`, `BONESP`, `BONOCE`, `BONQUI`, `BONRET`,
`BONVAC`, `DIFSUE`, `HEX050`, `HEX100`, `HRSEXT`, `MESDEA`, `OTSBON`,
`RIMALM`, `TRAREM`, `VACCIA`, `VACPRO`

## Haberes exentos / no imponibles

Primera identificacion por codigos de colacion, movilizacion, viaticos,
otros bonos no imponibles y traslados.

`AS1COL`, `ASICOL`, `ASIMOV`, `ANTVIA`, `FOTROS`, `OTSBNI`, `TRAGEN`, `TRESPD`,
`TRESPH`, `VIATIC`

## Asignaciones familiares

Items separados de los haberes no imponibles por corresponder a asignacion familiar.

`ASIFAM`, `ASIFAP`, `ASIFAR`

## Provisiones

Items claramente marcados como provision o acumulacion asociada.

`PROACU`, `PROCON`, `PROGAN`, `PROIAS`, `PROVAC`

## Contribucion del empleador

Items asociados a mutual, SIS, seguro de cesantia empleador, ley SANNA y
reliquidaciones/aportes patronales relacionados.

`COCAPI`, `COSESO`, `LSANNA`, `LSAREL`, `LSARLQ`, `MUTREL`, `MUTUAL`, `SCEREL`,
`SCERLQ`, `SEGCA1`, `SEGCEE`, `SEGMUT`, `SISAFP`, `SISREL`, `SISRLQ`

## Descuentos legales / previsionales

Items asociados a AFP, salud, impuesto, APV/ahorro previsional, seguro cesantia
trabajador, diferencias/reliquidaciones legales y trabajo pesado trabajador.

`AFPAHO`, `AFPCOT`, `AFPREL`, `AFPRLQ`, `APVEXE`, `DIFCOT`, `IMPREL`, `IMPRLQ`,
`IMPUES`, `ISAPRE1`, `ISAREL`, `ISARLQ`, `SCIREL`, `SCIRLQ`, `SEGCEI`

## Otros descuentos

Items asociados a anticipos, prestamos, descuentos internos, retenciones,
caja/creditos, sobregiros y ajustes.

`AHCAJA`, `AHOPER`, `AHOPRE`, `AHOVOL`, `ANTAGI`, `ANTBEN`, `ANTBES`, `ANTBON`,
`ANTCIA`, `ANTDIF`, `ANTFIN`, `ANTICA`, `ANTICI`, `ANTQUI`, `ANTVAC`, `ATRASO`,
`CAJACO`, `DESAJU`, `DESCCO`, `DESCHI`, `DESCHU`, `DESFAL`, `DESFAR`,
`DESGIM`, `DESOPT`, `DESQUI`, `DESSEC`, `DEUFIN`, `OTDESC`, `OTRANT`, `PRCAJ2`,
`PRECA3`, `PRECA4`, `PRECAJ`, `PRECIA`, `PREEMP`, `PRESS3`, `PRHERO`, `REDONA`,
`RETJUD`, `SBGIRA`, `SBGIRO`, `SUMCAJ`, `SUMSEG`

## Finiquito / indemnizaciones

Conviene cargar estos items en la hoja de lineas de finiquito o revisarlos como
haberes no imponibles/exentos segun la regla de negocio.

`DIAPEN`, `INDLEA`, `INDLEG`, `INDVOL`, `PERDID`

## Bases, totales o controles

No conviene migrarlos como items de detalle si se recalculan o se cargan en
campos resumen de la liquidacion.

`DIASLI`, `DIASTR1`, `SEGCET`, `SCTREL`, `SCTRLQ`, `SUBASE`, `Totales`

## Columnas de item sin movimiento

Existen como columnas en el Excel, pero no tienen montos distintos de cero en
el historico revisado.

`DESCOL`, `DESUES`, `DIFBVA`, `HONREM`, `PEPEME`, `TRAHON`

## Requieren confirmacion

Estos codigos fueron clasificados por patron de nombre, pero conviene validarlos
con una nomina de conceptos oficial antes de migrar historicos.

`000011`, `AGUCIA`, `ANTAGI`, `ANTBEN`, `ANTBES`, `ANTBON`, `ANTCIA`, `ANTDIF`,
`ANTFIN`, `ANTICA`, `ANTVIA`, `BOASIG`, `FOTROS`, `MESDEA`, `RIMALM`, `SEGCA1`,
`SUMSEG`, `TRAGEN`, `TRESPD`, `TRESPH`, `VACPRO`
