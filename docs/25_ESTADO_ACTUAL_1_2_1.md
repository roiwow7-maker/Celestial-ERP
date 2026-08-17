# Estado actual de Celestial ERP 1.2.1

Fecha de referencia: 2026-08-16

Este documento es la referencia corta del estado vigente. Cuando un documento historico describa SQLite, una API inicial o Next.js como trabajo futuro, prevalecen este archivo, `README.md`, `ROADMAP.md` y `version_log.md`.

## Plataforma activa

- Backend Django 6 con PostgreSQL como base principal.
- Frontend nativo Next.js 16, React 19 y TypeScript.
- Aplicacion de escritorio Electron empaquetable como AppImage.
- Proxy de Next.js hacia Django; PostgreSQL no es accesible desde clientes.
- Operacion local/LAN responsive para escritorio y smartphone.
- Preparacion productiva con Gunicorn, Next.js standalone, systemd y nginx/HTTPS.

## Funciones disponibles

- Autenticacion por sesion Django, CSRF, roles y permisos por modulo.
- Remuneraciones, asistencia, contabilidad base, inventario y comercio.
- CRUD nativo conectado a la API Django v1.
- Reportes por modulo con indicadores, graficos, filtros e impresion/PDF desde navegador.
- Carga masiva conectada al ETL, procesamiento asincronico, historial y descargas.
- Administracion de usuarios y roles para administradores autorizados.
- Auditoria estructurada y diagnosticos operativos.
- Backups PostgreSQL manuales/automaticos, retencion y restauracion aislada validada.

## Validacion

- `python manage.py check`: sin observaciones.
- Suite Django: 51 pruebas correctas sobre PostgreSQL temporal aislado.
- Frontend: ESLint, TypeScript y build de produccion correctos.
- AppImage `1.2.1`: generado y servidor standalone interno validado localmente.

## Pendientes versionados

- `1.2.2`: validar AppImage en un equipo Linux limpio.
- `1.2.3`: completar prueba fisica en smartphone real dentro de la LAN.
- `1.2.4`: aplicar y validar dominio, TLS, servicios y firewall productivos.
- `1.2.5`: aprobaciones, anulaciones, cierres y exportacion contable formal.
- `1.2.6`: kardex y documentos/cierres de inventario.
- `1.2.7`: integracion idempotente de comercio con stock y contabilidad.
- `1.2.8`: PDF server-side para documentos de formato fijo.
- `1.2.9`: primer caso aprobado de IA local, separado y de solo lectura.

## Privacidad

No se versionan bases, dumps, backups, CSV, Excel, uploads, reportes operativos, AppImages, `.env`, contraseñas, tokens ni claves. Los ejemplos contienen solamente marcadores o fixtures ficticios.
