# Plan de frontend real para Celestial ERP

Fecha de referencia: 2026-08-07

## Objetivo

Construir una interfaz moderna para usuarios de RRHH, Contabilidad, Inventario y Ventas sin reescribir las reglas de negocio que ya funcionan en Django. Django continuara siendo la autoridad para autenticacion, permisos, auditoria, ETL y acceso a PostgreSQL.

## Arquitectura elegida

```text
Navegador -> Nginx/HTTPS -> Frontend Next.js
                        -> API Django -> PostgreSQL
```

- Next.js con TypeScript para la experiencia de usuario.
- Django como API y panel administrativo de respaldo.
- PostgreSQL accesible solamente desde Django.
- Nginx como unico punto de entrada y mismo dominio para frontend/API.
- Autenticacion inicial con sesion Django, cookie segura `HttpOnly` y CSRF. No guardar tokens en `localStorage`.
- Bootstrap actual se conserva hasta reemplazar cada pantalla; no se hara un cambio total en un solo despliegue.

## Principios

1. No duplicar calculos, permisos ni reglas de negocio en el frontend.
2. Versionar la API bajo `/api/v1/`.
3. Migrar modulo por modulo con reversa inmediata a la vista Django existente.
4. Mantener Django Admin para tareas tecnicas y recuperacion operativa.
5. Diseñar primero los flujos diarios; la apariencia visual se define sobre casos reales.
6. Cumplir accesibilidad basica: teclado, foco visible, contraste, etiquetas y estados de error.

## Fases

### Fase 0 - Seguridad y contrato tecnico

- [ ] Retirar credenciales PostgreSQL del codigo y cargarlas desde el ambiente.
- [ ] Definir dominio, HTTPS, CORS/CSRF y politica de sesiones.
- [ ] Inventariar endpoints existentes y definir respuestas/error estables.
- [ ] Agregar OpenAPI y pruebas de contrato.
- [ ] Definir estados comunes: carga, vacio, error, sin permiso y sesion vencida.

### Fase 1 - Base del frontend

- [ ] Crear aplicacion Next.js con TypeScript, lint, pruebas y variables por ambiente.
- [ ] Crear sistema visual: colores, tipografia, espaciado, tablas, formularios y dialogos.
- [ ] Implementar login, cierre de sesion y recuperacion ante sesion expirada.
- [ ] Implementar layout responsive, navegacion por permisos y pagina 403/404.
- [ ] Crear cliente API centralizado con CSRF, timeouts y manejo uniforme de errores.

### Fase 2 - Primer flujo vertical

El primer modulo sera Remuneraciones porque ya tiene datos, permisos, reportes y uso operativo demostrable.

- [ ] Dashboard de remuneraciones.
- [ ] Listado y ficha de trabajadores.
- [ ] Periodos, liquidaciones e items con filtros y paginacion server-side.
- [ ] Carga ETL con progreso, resultado y descarga de errores.
- [ ] Reportes y exportacion manteniendo los mismos conteos que Django.
- [ ] Pruebas con los roles Administrador, RRHH, Contabilidad y Solo lectura.

### Fase 3 - Modulos ERP

- [ ] Asistencia.
- [ ] Contabilidad.
- [ ] Inventario.
- [ ] Compras y ventas.
- [ ] Auditoria, usuarios, estado del sistema y backups.

Cada modulo se considera migrado solo cuando tiene paridad funcional, permisos verificados, pruebas de navegador y una ruta de reversa documentada.

### Fase 4 - Produccion

- [ ] Build reproducible y despliegue independiente de frontend/backend.
- [ ] Nginx con HTTPS, compresion, limites de carga y cabeceras seguras.
- [ ] Logs y monitoreo de errores frontend/backend.
- [ ] Pruebas end-to-end de los flujos criticos.
- [ ] Prueba LAN con usuarios nominales y dispositivos reales.
- [ ] Procedimiento de despliegue y rollback.

## Entregable inicial recomendado

Un prototipo navegable del login, layout y dashboard de remuneraciones conectado a `/api/v1/`, seguido por trabajadores y carga ETL. Este alcance valida arquitectura, autenticacion, permisos, tablas grandes y cargas largas antes de migrar el resto.

## Criterios de exito

- Ningun navegador accede directamente a PostgreSQL.
- Los cuatro roles obtienen exactamente los permisos definidos en Django.
- Conteos y resultados coinciden con las vistas actuales.
- Las tablas grandes usan filtros y paginacion en servidor.
- La carga ETL no bloquea la interfaz y presenta progreso/error recuperable.
- El frontend puede desplegarse o revertirse sin alterar los datos.

## Decisiones pendientes antes de programar

- Confirmar si el frontend se usara solo en LAN o tambien remotamente mediante VPN.
- Identificar los tres flujos mas frecuentes de cada rol.
- Definir identidad visual y dispositivos objetivo.
- Decidir si Next.js se alojara junto a Django o en un servicio separado.

