# Analisis de descripciones codigo_item

Fecha de revision: 2026-07-13

Nota: analisis historico de descripciones de items de remuneracion. Sigue siendo referencia de calidad de datos para la version operativa `0.9.4`.

## Estado general

Los archivos por categoria tienen todas sus descripciones completas:

| Archivo | Filas | Descripciones faltantes |
| --- | ---: | ---: |
| `asignaciones_familiares_descripciones.csv` | 3 | 0 |
| `contribucion_empleador_descripciones.csv` | 18 | 0 |
| `descuentos_legales_previsionales_descripciones.csv` | 18 | 0 |
| `haberes_exentos_no_imponibles_descripciones.csv` | 19 | 0 |
| `haberes_normales_imponibles_descripciones.csv` | 26 | 0 |
| `otros_descuentos_descripciones.csv` | 41 | 0 |
| `provisiones_descripciones.csv` | 5 | 0 |
| `totales_descripciones.csv` | 1 | 0 |

El archivo consolidado `todos_los_codigo_item_descripciones.csv` tiene 131 filas, pero su columna `descripcion` esta vacia en todas las filas.

## Diferencias entre consolidado y archivos por categoria

Hay dos codigos escritos distinto:

| En archivos por categoria | En consolidado |
| --- | --- |
| `DIASTR` | `DIASTR1` |
| `ISAPRE` | `ISAPRE1` |

Esto calza con el historico original, donde existen variantes como `DIASTR1` e `ISAPRE1`. Conviene decidir si el consolidado debe conservar el codigo real del archivo historico o el codigo normalizado que escribiste en la descripcion.

## Posibles errores de tipeo a revisar

Estas no son correcciones aplicadas, solo sugerencias para revisar:

| Codigo | Texto actual | Posible correccion |
| --- | --- | --- |
| `ASIFAM` | `Asifnaciones familiares Simples` | `Asignaciones familiares simples` |
| `LSAREL` | `Ley Sanna Relquidada` | `Ley Sanna Reliquidada` |
| `LSARLQ` | `Ley Sanna Relquidada` | `Ley Sanna Reliquidada` |
| `MUTREL` | `Mutual Relquidada` | `Mutual Reliquidada` |
| `SEGCEE` | `Aporte Empreza Fondo Seguro` | `Aporte Empresa Fondo Seguro` |
| `SISAFP` | `Seguri Sobrev. e Invalidez` | `Seguro Sobrev. e Invalidez` |
| `APVEXE` | `AOV Reg.Trib A` | Revisar si debe ser `APV Reg. Trib. A` |
| `ANTCIA` | `Anticipo Aginaldo Compañia` | `Anticipo Aguinaldo Compañia` |
| `DESAJU` | `Ajuste Chilena Consoidada` | `Ajuste Chilena Consolidada` |
| `PROVAC` | `Provicion Vacaciones` | `Provision Vacaciones` |

## Recomendacion

1. Corregir los textos sugeridos si estan efectivamente mal escritos.
2. Sincronizar `todos_los_codigo_item_descripciones.csv` desde los archivos por categoria.
3. Definir si el codigo final debe ser `DIASTR` o `DIASTR1`, y `ISAPRE` o `ISAPRE1`.
