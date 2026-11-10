# Política de privacidad / Privacy Policy

## 🇪🇸 Español

Última actualización: 5 de octubre de 2026.

Joseflix Request es una aplicación de escritorio de uso personal. No tiene servidor ni cuenta propios y su autor
no recibe ningún dato de quien la usa.

## Qué datos trata

- **Tus peticiones:** el título, el año, la sinopsis, el tipo, el estado, el método de descarga, la prioridad, la
  fecha de solicitud, el enlace de descarga y las notas que escribes, y el nombre de quien hace cada petición
  (el peticionario).
- **Los datos de TMDB** de cada título: la ficha y el póster.
- **Tus ajustes:** el token de acceso de TMDB, el idioma, el tema, el tamaño de los pósters y el orden de la lista.

## Dónde se guardan

Todo queda en tu equipo, en `~/.local/share/joseflix-request/` (o en `$XDG_DATA_HOME`):

- `joseflix.sqlite3`: las peticiones y los peticionarios.
- `config.json`: los ajustes y el token de TMDB. El token se guarda en claro, con permisos 600 (solo lo lee tu
  usuario).
- `backups/`: las últimas diez copias de la base de datos, que se hacen al abrir la aplicación o a petición tuya.
- `posters/`: los pósters descargados.

## Con quién se comunica

La red solo se usa cuando consultas un título, y solo con **The Movie Database (TMDB)**:

- `api.themoviedb.org`: recibe el identificador del título que has pegado y tu token de acceso.
- `image.tmdb.org`: recibe la petición del póster.

La aplicación no envía a TMDB los peticionarios, las notas ni el resto de tus datos, y no incluye analítica,
telemetría, publicidad ni otros servicios de terceros. El enlace de descarga y el botón «Abrir enlace» solo
abren la dirección que tú has escrito, con el programa de tu sistema.

## Cómo borrar tus datos

Elimina la carpeta `~/.local/share/joseflix-request/`. Desinstalar la aplicación no la borra por sí solo. Para
retirar el acceso de la aplicación a TMDB, revoca el token en tu cuenta de TMDB.

## Cambios en esta política

Si cambia, se actualizará este documento y la fecha de arriba; el historial está en el repositorio.

## Contacto

Jose Antonio Seguido Doblado · jose.antonio.seguido@gmail.com

---

## 🇺🇸 English

Last updated: October 5, 2026.

Joseflix Request is a desktop application for personal use. It has no server or account of its own, and its
author does not receive any data from the people who use it.

## What data it handles

- **Your requests:** the title, year, synopsis, type, status, download method, priority, request date, download
  link and the notes you write, and the name of whoever makes each request (the requester).
- **The TMDB data** of each title: the record and the poster.
- **Your settings:** the TMDB access token, the language, the theme, the poster size and the list order.

## Where it is stored

Everything stays on your computer, in `~/.local/share/joseflix-request/` (or in `$XDG_DATA_HOME`):

- `joseflix.sqlite3`: the requests and the requesters.
- `config.json`: the settings and the TMDB token. The token is stored in clear text, with 600 permissions (only
  your user can read it).
- `backups/`: the last ten copies of the database, made when the application starts or when you ask for one.
- `posters/`: the downloaded posters.

## Who it communicates with

The network is only used when you look a title up, and only with **The Movie Database (TMDB)**:

- `api.themoviedb.org`: receives the identifier of the title you pasted and your access token.
- `image.tmdb.org`: receives the request for the poster.

The application does not send TMDB the requesters, the notes or the rest of your data, and it includes no
analytics, telemetry, advertising or other third-party services. The download link and the "Open link" button
only open the address you wrote, with your system's program.

## How to delete your data

Remove the `~/.local/share/joseflix-request/` folder. Uninstalling the application does not delete it by itself.
To withdraw the application's access to TMDB, revoke the token in your TMDB account.

## Changes to this policy

If it changes, this document and the date above will be updated; the history is in the repository.

## Contact

Jose Antonio Seguido Doblado · jose.antonio.seguido@gmail.com
