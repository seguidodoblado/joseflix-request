import io
import json
from pathlib import Path

import pytest

from joseflix_request import tmdb


class Response(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def opener_for(payload: dict, poster: bytes = b"JPEG", calls: list | None = None):
    def opener(target, timeout=0):
        url = target if isinstance(target, str) else target.full_url
        if calls is not None:
            calls.append(url)
        return Response(poster if url.startswith("https://image.tmdb.org") else json.dumps(payload).encode())
    return opener


def test_parse_url_accepts_movie_and_tv_urls():
    assert tmdb.parse_url("https://www.themoviedb.org/movie/603-the-matrix") == ("movie", "603")
    assert tmdb.parse_url("https://www.themoviedb.org/tv/1396") == ("tv", "1396")


@pytest.mark.parametrize("url", ["", "https://www.themoviedb.org/", "https://www.themoviedb.org/person/287",
                                 "https://www.themoviedb.org/movie/", "https://www.themoviedb.org/movie/abc"])
def test_parse_url_rejects_anything_else(url):
    with pytest.raises(ValueError, match="URL TMDB no válida"):
        tmdb.parse_url(url)


def test_lookup_needs_a_token_before_anything_else(tmp_path: Path):
    with pytest.raises(ValueError, match="token de TMDB"):
        tmdb.lookup("https://www.themoviedb.org/movie/603", token="", posters_dir=tmp_path)


def test_lookup_of_a_movie_downloads_the_poster_once(tmp_path: Path):
    calls: list[str] = []
    payload = {"title": "Matrix", "release_date": "1999-03-31", "overview": "Neo.", "poster_path": "/m.jpg"}
    opener = opener_for(payload, calls=calls)
    url = "https://www.themoviedb.org/movie/603-the-matrix"
    first = tmdb.lookup(url, token="t", opener=opener, posters_dir=tmp_path)
    assert first == {"tmdb_id": 603, "media_type": "Película", "title": "Matrix", "year": "1999",
                     "overview": "Neo.", "poster_path": str(tmp_path / "603.jpg"), "tmdb_url": url}
    assert (tmp_path / "603.jpg").read_bytes() == b"JPEG"
    assert "language=es-ES" in calls[0] and calls[1].endswith("/w342/m.jpg")
    tmdb.lookup(url, token="t", opener=opener, posters_dir=tmp_path)
    assert sum(c.startswith("https://image.tmdb.org") for c in calls) == 1     # el póster ya estaba


def test_lookup_of_a_series_uses_name_and_first_air_date(tmp_path: Path):
    payload = {"name": "Dark", "first_air_date": "2017-12-01", "overview": "", "poster_path": None}
    data = tmdb.lookup("https://www.themoviedb.org/tv/70523", token="t", opener=opener_for(payload),
                       posters_dir=tmp_path)
    assert data["media_type"] == "Serie" and data["title"] == "Dark" and data["year"] == "2017"
    assert data["poster_path"] == ""
