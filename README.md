# Portal de Artistas (versión inicial)

Primera versión del portal. La versión mantenida y más completa es `dbartista`
(CSP, rate limiting, transacciones con limpieza de archivos, paginación con total, etc.).

## Seguridad
- Perfil, avatar y publicaciones requieren token y solo permiten modificar lo propio.
- Las imágenes se validan por contenido (PNG/JPG/WEBP, máx. 5 MB) y se guardan con nombre generado.
- El correo de los artistas no se expone en las rutas públicas.
- Limitaciones conocidas: el token se guarda en `localStorage`, no hay límite de intentos de login ni
  borrado de publicaciones.

## Puesta en marcha
1. Crea la base de datos: `CREATE DATABASE db_artista CHARACTER SET utf8mb4;`
2. Copia `.env.example` a `.env` y completa los datos.
3. `pip install -r requirements.txt` y luego `uvicorn backend.app.main:app --reload`
4. Abre http://localhost:8000
