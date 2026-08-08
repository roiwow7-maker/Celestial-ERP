# UI Bootstrap

Fecha de referencia: 2026-07-10

## Objetivo

La interfaz web de Celestial ERP fue normalizada sobre Bootstrap 5 para mejorar consistencia visual, responsividad y mantenibilidad sin abandonar la identidad previa del sistema.

La paleta fue suavizada hacia tonos pastel neutrales y un poco mas oscuros: azules grisaceos, verdes suaves, arena clara y rosados apagados solo para estados de alerta.

La UI soporta modo claro y oscuro. El tema activo se guarda en `localStorage` con la clave:

```text
celestial-erp-theme
```

El atributo aplicado al documento es:

```html
<html data-erp-theme="light">
<html data-erp-theme="dark">
```

Tambien se sincroniza `data-bs-theme` para que Bootstrap respete el modo activo.

Se conserva la paleta base:

- Azul principal pastel oscuro: `#5f8794`.
- Azul fuerte neutral: `#476f7c`.
- Verde suave oscuro: `#668f78`.
- Arena claro: `#eee4d4`.
- Fondo claro operativo: `#f4f1ec`.
- Texto principal: `#24303f`.
- Texto secundario: `#5d6878`.

Modo oscuro:

- Fondo: `#1f2933`.
- Superficie: `#293541`.
- Azul pastel: `#8db7c1`.
- Verde pastel: `#98bda5`.
- Texto principal: `#eef2f4`.
- Texto secundario: `#b8c3ca`.

## Archivos principales

| Archivo | Funcion |
| --- | --- |
| `Celestial_ERP/Applet/templates/Applet/base.html` | Layout base, carga Bootstrap, CSS propio y JS propio. |
| `Celestial_ERP/Applet/templates/shared/topbar.html` | Navbar Bootstrap flotante con permisos por modulo. |
| `Celestial_ERP/Applet/static/Applet/css/app.css` | Tema visual de Celestial ERP y clases de compatibilidad. |
| `Celestial_ERP/Applet/static/Applet/js/app.js` | Interacciones comunes: paneles colapsables y cambio de tema. |
| `Celestial_ERP/Applet/templates/admin/base_site.html` | Layout personalizado del Django Admin con Bootstrap. |
| `Celestial_ERP/Applet/static/Applet/css/admin.css` | Tema pastel/flotante especifico para Django Admin. |

## Bootstrap

La version integrada es Bootstrap `5.3.3` local/offline:

```text
Celestial_ERP/Applet/static/vendor/bootstrap/css/bootstrap.min.css
Celestial_ERP/Applet/static/vendor/bootstrap/js/bootstrap.bundle.min.js
```

La UI ya no depende de CDN para Bootstrap. Si se actualiza Bootstrap, reemplazar esos archivos y probar:

```powershell
python manage.py check
python manage.py test Applet DATA_scope ERP_api
```

## Criterio visual

La navbar se comporta como una capa flotante superior:

- `position: sticky`.
- Separacion superior.
- Bordes redondeados.
- Fondo blanco translucido.
- Sombra mas marcada que el resto de los elementos.

Los paneles, tablas, metricas y tarjetas tambien flotan sobre el fondo, pero con menor intensidad visual:

- Sombra mas suave.
- Borde claro.
- Radio de 10px.
- Fondo blanco casi opaco.

Esto genera una jerarquia clara:

1. Navbar: elemento mas cercano.
2. Paneles y tarjetas: superficie de trabajo.
3. Fondo: plano visual secundario.

## Patrones de templates

Las paginas nuevas deben extender:

```django
{% extends "Applet/base.html" %}
```

Estructura recomendada:

```django
{% block title %}Titulo | Celestial ERP{% endblock %}

{% block content %}
<section class="page-head">
    <div>
        <h1>Titulo</h1>
        <p class="lead">Descripcion breve.</p>
    </div>
</section>

<section class="panel">
    ...
</section>
{% endblock %}
```

Clases preferidas:

- Acciones principales: `button`.
- Acciones secundarias: `button secondary`.
- Contenedores: `panel`.
- KPIs: `metric` dentro de `metrics`.
- Grillas: `grid` o `grid two`.
- Tablas anchas: envolver en `table-scroll`.
- Formularios: `form-control`, `form-select`, `form-check-input`.

## Paginas migradas

- Portal Applet.
- Navbar compartida.
- Login.
- Dashboard de remuneraciones.
- Trabajadores, periodos, items, liquidaciones, movimientos.
- Formularios manuales.
- Reportes.
- Cargas ETL.
- Kanban operativo.
- Prueba de rutas.
- Django Admin: portada, navbar flotante, listados, filtros, formularios y botones.

## Notas de mantenimiento

- Evitar CSS embebido extenso en templates nuevos.
- Usar `extra_head` solo para estilos especificos de una pantalla compleja.
- Mantener la logica de permisos en templates al modificar la navbar.
- No reemplazar clases propias como `panel`, `metric` o `button` sin revisar todas las vistas, porque actuan como compatibilidad entre Bootstrap y el estilo historico del ERP.
