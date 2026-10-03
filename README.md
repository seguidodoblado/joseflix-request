# Joseflix Request

![release](https://img.shields.io/github/v/release/seguidodoblado/joseflix-request) ![license](https://img.shields.io/github/license/seguidodoblado/joseflix-request) ![last commit](https://img.shields.io/github/last-commit/seguidodoblado/joseflix-request) ![downloads](https://img.shields.io/github/downloads/seguidodoblado/joseflix-request/total) ![stars](https://img.shields.io/github/stars/seguidodoblado/joseflix-request?style=flat) ![issues](https://img.shields.io/github/issues/seguidodoblado/joseflix-request) ![language](https://img.shields.io/github/languages/top/seguidodoblado/joseflix-request)

Aplicación de escritorio para gestionar las peticiones de películas y series del servidor Plex Joseflix.

Última release: [v1.0.3-1](https://github.com/seguidodoblado/joseflix-request/releases/tag/v1.0.3-1)

## Características

- Consulta mediante URL de TMDB y descarga del póster.
- Título, año, tipo y sinopsis.
- Peticionarios gestionables.
- Estados: 📨 Solicitado, 🔎 Buscando, 📥 Descargado, 📤 Subido, ✅ Notificado y 🔧 Corregir.
- Métodos de descarga: ❓ Sin método, ⬇️ JDownloader, 🧲 Transmission y 🐴 aMule.
- Prioridad (🔴 Alta, 🟡 Normal y 🟢 Baja) y fecha de solicitud con calendario.
- Filtros por título, estado, tipo, peticionario, prioridad y fecha, con la lista ordenada por fecha de solicitud (en cualquier sentido).
- Fichas editables y eliminación de registros, y limpieza de las peticiones notificadas.
- Copias de seguridad automáticas al abrir la aplicación (se conservan las 10 últimas) y restauración desde **Ajustes**.
- Modos claro y oscuro, y tamaño de póster ajustable.

## Desarrollo

```bash
sudo apt install python3 python3-gi gir1.2-gtk-4.0
python3 joseflix_request.py
```

Los datos se guardan en `~/.local/share/joseflix-request/`.

Configura el token de TMDB desde **Ajustes → Configurar TMDB…**. Debe utilizarse el token de acceso de lectura de la API, normalmente el token largo que comienza por `eyJ`.

## Paquete Debian

El paquete utiliza GTK 4 y PyGObject del sistema, y utiliza estas rutas:

```text
/usr/bin/joseflix-request
/opt/joseflix-request/
/usr/share/applications/joseflix-request.desktop
/usr/share/icons/hicolor/scalable/apps/joseflix-request.svg
```

Para construirlo:

```bash
./build-deb.sh
```

El resultado se genera en la carpeta superior del proyecto. Para instalarlo:

```bash
sudo apt install ../joseflix-request_x.x.x-x_all.deb
```
