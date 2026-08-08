# UI Bootstrap y Django Admin

Fecha de referencia: 2026-07-13

Version documentada: `1.0.8`

## Bootstrap local

Bootstrap integrado:

```text
Celestial_ERP/Applet/static/vendor/bootstrap/css/bootstrap.min.css
Celestial_ERP/Applet/static/vendor/bootstrap/js/bootstrap.bundle.min.js
```

Version:

```text
5.3.3
```

La webapp no depende de CDN para Bootstrap.

## Tema visual

Archivos:

```text
Celestial_ERP/Applet/static/Applet/css/app.css
Celestial_ERP/Applet/static/Applet/js/app.js
```

Caracteristicas:

- Paleta pastel oscura y neutral.
- Modo claro y oscuro.
- Persistencia de tema en `localStorage`.
- Navbar flotante.
- Paneles y filas con menor profundidad visual que la navbar.

Clave de tema:

```text
celestial-erp-theme
```

Atributos sincronizados:

```html
data-erp-theme="light|dark"
data-bs-theme="light|dark"
```

## Jerarquia visual

1. Navbar flotante: capa mas cercana.
2. Paneles, rows, tablas y metricas: superficie de trabajo.
3. Fondo: plano secundario.

## Templates UI principales

| Template | Uso |
| --- | --- |
| `Applet/base.html` | Layout global. |
| `shared/topbar.html` | Navbar flotante y version visible. |
| `registration/login.html` | Login. |
| `DATA_scope/dashboard.html` | Dashboard remuneraciones. |
| `DATA_scope/reports.html` | Reportes. |
| `DATA_scope/upload.html` | Cargas ETL. |
| `DATA_scope/model_form.html` | Formularios genericos. |
| `Inventory/templates/Inventory/` | Pantallas de inventario. |
| `Commerce/templates/Commerce/` | Pantallas de compras y ventas. |

## Django Admin

Archivos:

```text
Celestial_ERP/Applet/templates/admin/base_site.html
Celestial_ERP/Applet/templates/admin/index.html
Celestial_ERP/Applet/static/Applet/css/admin.css
```

Version visible:

- `Applet/admin.py` define `admin.site.site_header` usando `ERP_VERSION`.
- `base_site.html` renderiza `{{ site_header }}`.

El admin mantiene:

- navbar flotante interna
- accesos rapidos al portal
- tema claro/oscuro
- Bootstrap local
- estilo pastel oscuro/neutral

## Regla de UI

Al crear una pagina nueva:

```django
{% extends "Applet/base.html" %}
```

Usar:

- `panel` para contenedores.
- `metric` para KPIs.
- `table-scroll` para tablas anchas.
- `form-control`, `form-select`, `form-check-input` para formularios.
- `button` y `button secondary` para acciones compatibles con el tema.

