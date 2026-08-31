# Joseflix Request

Aplicación de escritorio para gestionar las peticiones de películas y series del servidor Plex Joseflix.

## Características

- Consulta mediante URL de TMDB y descarga del póster.
- Título, año, tipo y sinopsis.
- Peticionarios gestionables.
- Estados: 📨 Solicitado, 🔎 Buscando, 📥 Descargado, 📤 Subido y ✅ Notificado.
- Métodos de descarga: DD, Torrent y ED2K.
- Filtros por título, estado, tipo y peticionario.
- Fichas editables y eliminación de registros.
- Modos claro y oscuro.

## Desarrollo

```bash
python3 -m venv .venv
.venv/bin/pip install PySide6
.venv/bin/python joseflix_request.py
```

Los datos se guardan en `~/.local/share/joseflix-request/`.

Configura el token de TMDB desde **Ajustes → Configurar TMDB…**. Debe utilizarse el token de acceso de lectura de la API, normalmente el token largo que comienza por `eyJ`.

## Paquete Debian

El paquete incluye el entorno virtual de PySide6 y utiliza estas rutas:

```text
/usr/bin/joseflix-request
/usr/share/joseflix-request/
/opt/venvs/joseflix-request/
```

Para construirlo:

```bash
./build-deb.sh
```

El resultado se genera en la carpeta superior del proyecto. Para instalarlo:

```bash
sudo apt install ../joseflix-request_0.1.0-1_all.deb
```

## Desarrollador

seguidodoblado — jose.antonio.seguido@gmail.com
