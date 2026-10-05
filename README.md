<p align="right"><a href="README.en.md">🇺🇸 English</a></p>

<p align="center">
  <img src="joseflix-request.svg" alt="Logotipo de Joseflix Request" width="128">
</p>

<h1 align="center">Joseflix Request</h1>

<p align="center">
  <a href="https://github.com/seguidodoblado/joseflix-request/releases"><img src="https://img.shields.io/github/v/release/seguidodoblado/joseflix-request" alt="release"></a>
  <a href="https://github.com/seguidodoblado/joseflix-request/actions/workflows/ci.yml"><img src="https://github.com/seguidodoblado/joseflix-request/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://github.com/seguidodoblado/joseflix-request/actions/workflows/cd.yml"><img src="https://github.com/seguidodoblado/joseflix-request/actions/workflows/cd.yml/badge.svg" alt="CD"></a>
  <a href="https://github.com/seguidodoblado/joseflix-request/blob/main/COPYING"><img src="https://img.shields.io/github/license/seguidodoblado/joseflix-request" alt="license"></a>
  <a href="https://github.com/seguidodoblado/joseflix-request/commits/main/"><img src="https://img.shields.io/github/last-commit/seguidodoblado/joseflix-request" alt="last commit"></a>
  <a href="https://github.com/seguidodoblado/joseflix-request/commits/main/"><img src="https://img.shields.io/github/commit-activity/t/seguidodoblado/joseflix-request" alt="total commits"></a>
  <a href="https://github.com/seguidodoblado/joseflix-request/releases"><img src="https://img.shields.io/github/downloads/seguidodoblado/joseflix-request/total" alt="downloads"></a>
  <a href="https://github.com/seguidodoblado/joseflix-request/stargazers"><img src="https://img.shields.io/github/stars/seguidodoblado/joseflix-request?style=flat" alt="stars"></a>
  <a href="https://github.com/seguidodoblado/joseflix-request/issues"><img src="https://img.shields.io/github/issues/seguidodoblado/joseflix-request" alt="issues"></a>
  <a href="https://github.com/seguidodoblado/joseflix-request"><img src="https://img.shields.io/github/languages/top/seguidodoblado/joseflix-request" alt="language"></a>
  <a href="https://codetime.dev"><img alt="CodeTime Badge" src="https://shields.jannchie.com/endpoint?style=flat&color=0284c7&url=https%3A%2F%2Fcodetime.dev%2Fv3%2Fusers%2Fshield%3Fuid%3D36830"></a>
  <a href="https://wakatime.com/badge/github/seguidodoblado/joseflix-request"><img src="https://wakatime.com/badge/github/seguidodoblado/joseflix-request.svg" alt="wakatime"></a>
</p>

<p align="center">
  Gestiona las peticiones de películas y series del servidor Plex Joseflix.
</p>

Aplicación de escritorio (GTK 4 + PyGObject), de uso personal: sin servidor ni cuenta, todo ocurre en tu equipo.

- **Consulta por URL de TMDB** y descarga del póster: título, año, tipo y sinopsis.
- **Peticionarios** gestionables, con estados (📨 Solicitado, 🔎 Buscando, 📥 Descargado, 📤 Subido, ✅ Notificado y
  🔧 Corregir), métodos de descarga (⬇️ JDownloader, 🧲 Transmission y 🐴 aMule), prioridad y fecha de solicitud con
  calendario.
- **Filtros** por título, estado, tipo, peticionario, prioridad y fecha, con la lista ordenada por fecha de
  solicitud (en cualquier sentido).
- **Fichas editables**, eliminación de registros y limpieza de las peticiones notificadas.
- **Copias de seguridad automáticas** al abrir la aplicación (se conservan las 10 últimas) y restauración desde
  **Ajustes**.
- **Interfaz en español e inglés** (gettext), con selector de idioma en **Ajustes → Idioma…**; **tema Sistema, Claro
  u Oscuro** y tamaño de póster ajustable.

## Documentación

Toda la documentación —instalación, guía de uso, especificaciones técnicas, solución de problemas y más— está en
la **[wiki del proyecto](https://github.com/seguidodoblado/joseflix-request/wiki)** (español e inglés).

## Privacidad

Joseflix Request no tiene servidor ni cuenta propios y no recoge datos; solo consulta TMDB cuando se lo pides. Qué se guarda, dónde y con quién se comunica está en la **[política de privacidad](PRIVACY.md)**.

## Licencia

Este proyecto se distribuye bajo la GNU General Public License, versión 3 o posterior (ver `COPYING`).
