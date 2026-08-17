# Celestial ERP Frontend

Frontend real de Celestial ERP construido con Next.js 16, React 19, TypeScript y Electron. Django conserva autenticacion, permisos, reglas de negocio, auditoria, ETL y acceso exclusivo a PostgreSQL.

## Requisitos

- Node.js 24 recomendado mediante `.nvmrc` (Next.js requiere Node `>=20.9`).
- Backend Django disponible en `http://127.0.0.1:8000`.

## Desarrollo

```bash
nvm use
npm ci
npm run dev
```

Abrir `http://127.0.0.1:3000`. El servidor escucha en `0.0.0.0` para pruebas LAN; `/backend/` se envía a Django mediante el proxy interno.

Para iniciar backend, frontend y Electron en desarrollo:

```bash
npm run dev:desktop
```

## Validacion

```bash
npm run lint
npm run typecheck
npm run build
```

## Escritorio

```bash
npm run build:desktop
```

El AppImage se genera en `dist-electron/`. `dist-electron/`, `release-electron/`, builds, variables privadas y dependencias instaladas estan excluidos de Git.

## Configuracion

Copiar `.env.example` solo como referencia. `DJANGO_BACKEND_URL` debe apuntar a Django por una direccion privada. No incluir credenciales en variables `NEXT_PUBLIC_*` ni conectar el frontend directamente a PostgreSQL.

## Estado 1.2.1

- Sesion Django y CSRF integrados.
- CRUD por modulo mediante API v1.
- Reportes con filtros, graficos e impresion/PDF.
- Carga masiva ETL con historial y estado.
- Administracion autorizada de usuarios y roles.
- Diseño responsive para smartphone.
- Build standalone incorporado al AppImage.
