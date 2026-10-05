<p align="right"><a href="README.md">🇪🇸 Español</a></p>

<p align="center">
  <img src="joseflix-request.svg" alt="Joseflix Request logo" width="128">
</p>

<h1 align="center">Joseflix Request</h1>

<p align="center">
  <a href="https://github.com/seguidodoblado/joseflix-request/releases"><img src="https://img.shields.io/github/v/release/seguidodoblado/joseflix-request" alt="release"></a>
  <a href="https://github.com/seguidodoblado/joseflix-request/actions/workflows/ci.yml"><img src="https://github.com/seguidodoblado/joseflix-request/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://github.com/seguidodoblado/joseflix-request/actions/workflows/cd.yml"><img src="https://github.com/seguidodoblado/joseflix-request/actions/workflows/cd.yml/badge.svg" alt="CD"></a>
  <a href="https://github.com/seguidodoblado/joseflix-request/blob/main/LICENSE"><img src="https://img.shields.io/github/license/seguidodoblado/joseflix-request" alt="license"></a>
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
  Manage the movie and series requests of the Plex server Joseflix.
</p>

Desktop application (GTK 4 + PyGObject), for personal use: no server, no account, everything happens on your own machine.

- **Look up by TMDB URL** and download the poster: title, year, type and synopsis.
- **Manageable requesters**, with statuses (📨 Requested, 🔎 Searching, 📥 Downloaded, 📤 Uploaded, ✅ Notified and
  🔧 Fix), download methods (⬇️ JDownloader, 🧲 Transmission and 🐴 aMule), priority and request date with a
  calendar.
- **Filters** by title, status, type, requester, priority and date, with the list sorted by request date (in
  either direction).
- **Editable records**, record deletion and clearing of notified requests.
- **Automatic backups** when the application starts (the last 10 are kept) and restore from **Settings**.
- **Interface in Spanish and English** (gettext), with a language selector in **Settings → Language…**; **System,
  Light or Dark theme** and adjustable poster size.

## Documentation

All documentation—installation, usage guide, technical specifications, troubleshooting and more—is on the
**[project wiki](https://github.com/seguidodoblado/joseflix-request/wiki)** (Spanish and English).

## Privacy

Joseflix Request has no server or account of its own and does not collect data; it only queries TMDB when you ask it to. What is stored, where, and who it talks to is in the **[privacy policy](PRIVACY.en.md)**.

## License

This project is distributed under the GNU General Public License, version 3 (see `LICENSE`).
