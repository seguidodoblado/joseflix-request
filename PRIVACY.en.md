<p align="right"><a href="PRIVACY.md">🇪🇸 Español</a></p>

# Privacy Policy

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
