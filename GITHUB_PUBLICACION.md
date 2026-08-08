# Publicacion segura en GitHub

## Regla principal

El repositorio contiene solamente codigo, plantillas, archivos estaticos y documentacion tecnica. Nunca se publican datos reales, bases de datos, respaldos, planillas, CSV, archivos subidos ni secretos.

## Protecciones incorporadas

- `.gitignore` bloquea bases SQLite, dumps PostgreSQL, SQL, CSV y formatos Excel/Calc.
- `backups/`, `uploads/`, `reports/`, entornos virtuales y logs quedan fuera de Git.
- `.env`, `.pgpass`, claves, el secreto local de Django y `.postgres_password` quedan fuera de Git.
- `.githooks/pre-commit` rechaza un commit si intenta incluir una extension de datos privada.
- La version se mantiene en `Celestial_ERP/Applet/version.py` y se muestra automaticamente en portal, API y Django Admin.

## Flujo obligatorio para cada mejora

1. Modificar el codigo y sus pruebas.
2. Incrementar `ERP_VERSION` en `Celestial_ERP/Applet/version.py`.
3. Actualizar `version_log.md` y, cuando corresponda, `ROADMAP.md`.
4. Ejecutar `python manage.py check` y las pruebas relacionadas.
5. Revisar `git status --short` antes de preparar el commit.
6. Confirmar con `git diff --cached --name-only` que no existen datos privados.

## Conexion con GitHub

Despues de crear un repositorio vacio y privado en GitHub:

```bash
git remote add origin git@github.com:USUARIO/REPOSITORIO.git
git push -u origin main
```

Se recomienda mantener el repositorio privado hasta completar una revision de secretos, licencias, documentos e imagenes.

## Si un archivo privado entra por error

No basta con borrarlo en un commit posterior: permanece en el historial. Se debe detener la publicacion, rotar cualquier credencial expuesta y limpiar el historial antes de subirlo a GitHub.
