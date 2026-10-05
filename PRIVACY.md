<p align="right"><a href="PRIVACY.en.md">🇺🇸 English</a></p>

# Política de privacidad

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
