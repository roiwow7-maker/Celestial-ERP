# Validacion frontend 1.2.x

Fecha: 2026-08-16

Este documento registra las comprobaciones que requieren infraestructura externa. No deben marcarse como terminadas solo con una simulacion local.

## v1.2.2 - AppImage en equipo limpio

Artefacto candidato: `Celestial ERP-1.2.1.AppImage`.

1. Copiar el AppImage a un Linux x86_64 que no tenga el repositorio, Node.js ni dependencias del proyecto instaladas.
2. Comparar el SHA-256 con el publicado por el equipo que genero el artefacto.
3. Ejecutar `chmod +x "Celestial ERP-1.2.1.AppImage"`.
4. Mantener el backend Django accesible y ejecutar el AppImage.
5. Validar inicio/cierre de sesion, navegacion, un reporte, una consulta CRUD y una carga ETL pequena.
6. Cerrar y volver a abrir la aplicacion; reemplazarla por una nueva copia y repetir el arranque para validar reinstalacion/actualizacion manual.

Registrar equipo, distribucion, version, SHA-256, fecha, resultado y errores. Solo entonces promover a `1.2.2`.

## v1.2.3 - Smartphone real en LAN

1. Conectar el telefono a la misma red Wi-Fi que el servidor.
2. Abrir `http://192.168.50.11:3000` mientras el frontend de desarrollo este activo.
3. Validar orientacion vertical y horizontal, menu movil, login, formularios, tablas/tarjetas, filtros, graficos y cierre de sesion.
4. Confirmar que no exista desplazamiento horizontal involuntario y que los controles tactiles sean utilizables.
5. Repetir al menos en un ancho pequeno y registrar modelo, navegador, fecha, capturas y resultado.

Si el telefono no conecta, el administrador debe permitir TCP/3000 solo desde la subred LAN. En Ubuntu con UFW:

```bash
sudo ufw allow from 192.168.50.0/24 to any port 3000 proto tcp comment 'Celestial ERP LAN'
sudo ufw status numbered
```

No abrir el puerto 8000: Django debe permanecer privado. Solo promover a `1.2.3` después de la prueba física.

## v1.2.4 - HTTPS y firewall productivo

Requiere dominio real, certificado TLS y acceso administrativo al servidor. La plantilla `deploy/nginx-celestial-erp.conf` expone solamente 80/443 y envía el tráfico al frontend Next.js privado en `127.0.0.1:3000`; Next.js envía `/backend/` a Django privado en `127.0.0.1:8000`.

Reglas UFW recomendadas para el servidor productivo:

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw delete allow 3000/tcp
sudo ufw status verbose
```

Antes de promover a `1.2.4`, ejecutar `nginx -t`, comprobar redireccion HTTP a HTTPS, certificado, cookies seguras, login, carga ETL y confirmar desde otro equipo que 3000, 8000 y 5432 no sean accesibles directamente.
