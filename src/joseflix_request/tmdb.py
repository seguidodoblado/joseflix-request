"""Consulta de una película o serie en The Movie Database (TMDB) a partir de su URL."""
import json
import re
import urllib.parse
import urllib.request
from collections.abc import Callable
from pathlib import Path

from . import config
from .i18n import _


def parse_url(url: str) -> tuple[str, str]:
    """('movie' o 'tv', identificador) de una URL de TMDB; ValueError si no lo es."""
    parts = urllib.parse.urlparse(url).path.strip("/").split("/")
    found = re.match(r"(\d+)", parts[1]) if len(parts) > 1 else None
    if len(parts) < 2 or parts[0] not in ("movie", "tv") or not found:
        raise ValueError(_("URL TMDB no válida"))
    return parts[0], found.group(1)


def lookup(url: str, token: str | None = None, opener: Callable = urllib.request.urlopen,
           posters_dir: Path | None = None) -> dict:
    """Los datos de la ficha y, si la hay, el póster descargado. `opener` y `posters_dir` se inyectan en las pruebas."""
    token = config.get_token() if token is None else token
    if not token:
        raise ValueError(_("Configura el token de TMDB desde Ajustes"))
    kind, ident = parse_url(url)
    request = urllib.request.Request(f"https://api.themoviedb.org/3/{kind}/{ident}?language=es-ES",
                                     headers={"Authorization": "Bearer " + token})
    with opener(request, timeout=15) as handle:
        data = json.load(handle)
    poster, local = data.get("poster_path") or "", ""
    if poster:
        folder = posters_dir or config.POSTERS_DIR
        folder.mkdir(parents=True, exist_ok=True)
        local = str(folder / f"{ident}.jpg")
        if not Path(local).exists():
            with opener("https://image.tmdb.org/t/p/w342" + poster, timeout=15) as handle:
                Path(local).write_bytes(handle.read())
    return {"tmdb_id": int(ident), "media_type": "Película" if kind == "movie" else "Serie",
            "title": data.get("title") or data.get("name", ""),
            "year": (data.get("release_date") or data.get("first_air_date", ""))[:4],
            "overview": data.get("overview", ""), "poster_path": local, "tmdb_url": url}
