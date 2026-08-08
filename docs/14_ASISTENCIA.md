# Asistencia

Fecha de referencia: 2026-07-13

Modulo activo desde `v0.9.6C`.

## Proposito

El modulo `Attendance` registra la asistencia historica de cada trabajador y permite consultar el estado diario, mensual y por trabajador. Cubre hora de entrada, hora de salida, minutos de descanso, horas trabajadas, estado del dia, fuente del dato y observaciones.

## Rutas

| Ruta | Uso |
| --- | --- |
| `/asistencia/` | Dashboard mensual de asistencia. |
| `/asistencia/registros/` | Registros diarios con filtros. |
| `/asistencia/registros/nuevo/` | Nuevo registro manual. |
| `/asistencia/registros/<id>/editar/` | Edicion de registro. |
| `/asistencia/trabajador/<id>/` | Historico por trabajador. |
| `/asistencia/reporte-mensual/` | Reporte mensual por trabajador. |
| `/asistencia/exportar-csv/` | Exportacion CSV filtrable. |

## Modelo Principal

`AttendanceRecord` queda vinculado a `DATA_scope.Employee` y mantiene una fila unica por trabajador y fecha.

Campos principales:

- trabajador
- fecha
- entrada
- salida
- descanso en minutos
- estado
- fuente
- observaciones
- usuario creador

Estados disponibles:

- Presente
- Ausente
- Atraso
- Permiso/Licencia
- Feriado
- Remoto

Fuentes disponibles:

- Manual
- Importacion
- Reloj control

## Reportes y Exportacion

El dashboard muestra registros del mes, trabajadores involucrados, horas, atrasos y ausencias. La vista mensual agrupa por trabajador y resume dias registrados, presentes, atrasos, ausencias, permisos y horas trabajadas.

La exportacion CSV respeta filtros por trabajador, estado y rango de fechas. El PDF se obtiene desde la impresion del navegador usando el boton `Imprimir / PDF`.

## Integracion con Remuneraciones

Desde `v0.9.9` existe sincronizacion hacia liquidaciones:

```powershell
python manage.py sync_attendance_payroll AAAAMM --dry-run
python manage.py sync_attendance_payroll AAAAMM
```

La sincronizacion actualiza dias trabajados, ausencias, permisos y horas no trabajadas. No modifica montos ni recalcula haberes/descuentos.

## Permisos

| Permiso | Uso |
| --- | --- |
| `Attendance.access_attendance_module` | Acceso al modulo. |
| `Attendance.manage_attendance_records` | Crear y editar registros. |
| `Attendance.view_attendance_reports` | Ver reportes mensuales. |
| `Attendance.export_attendance_reports` | Exportar CSV e imprimir reportes autorizados. |

Roles:

- Administrador y RRHH: acceso completo.
- Contabilidad: acceso, reportes y exportacion.
- Solo lectura: acceso y reportes.

## Validacion

Los estados con jornada trabajada requieren hora de entrada y salida. El calculo de horas descuenta minutos de descanso y soporta turnos que terminan al dia siguiente.

Pruebas ejecutadas:

```powershell
python Celestial_ERP\manage.py test Attendance
python Celestial_ERP\manage.py test Applet DATA_scope ERP_api Accounting Inventory Commerce Attendance
```

Resultado: 9 pruebas de asistencia OK y 41 pruebas totales OK.
