import os
from pathlib import Path

from joseflix_request import config


def test_the_tests_never_use_the_real_data_folder():
    real = Path.home() / ".local/share/joseflix-request"
    assert config.APP_DIR != real and real not in config.APP_DIR.parents
    assert str(config.APP_DIR).startswith(os.environ["XDG_DATA_HOME"])


def test_set_option_keeps_the_rest_of_the_settings(tmp_path: Path):
    path = tmp_path / "config.json"
    config.set_option("poster_size", 120, path)
    config.set_option("sort_desc", True, path)
    assert config.read_config(path) == {"poster_size": 120, "sort_desc": True}


def test_the_settings_file_is_only_readable_by_its_owner(tmp_path: Path):
    path = tmp_path / "config.json"
    path.write_text("{}")
    path.chmod(0o644)                                           # un archivo creado por una versión anterior
    config.set_token("secreto", path)
    assert path.stat().st_mode & 0o777 == 0o600


def test_a_missing_or_broken_file_reads_as_empty(tmp_path: Path):
    path = tmp_path / "config.json"
    assert config.read_config(path) == {}
    path.write_text("no es json")
    assert config.read_config(path) == {}
    path.write_text("[1, 2]")
    assert config.read_config(path) == {}


def test_the_token_comes_from_the_settings_and_falls_back_to_the_environment(tmp_path: Path, monkeypatch):
    path = tmp_path / "config.json"
    monkeypatch.setenv("TMDB_API_KEY", "del-entorno")
    assert config.get_token(path) == "del-entorno"          # sin fichero
    config.set_token("guardado", path)
    assert config.get_token(path) == "guardado"
    path.write_text('{"otra": 1}')
    assert config.get_token(path) == ""                      # fichero válido sin token: no se mira el entorno


def test_language_and_theme_ignore_unknown_values(tmp_path: Path):
    path = tmp_path / "config.json"
    assert config.language(path) is None and config.dark_mode(path) is None
    path.write_text('{"language": "en", "dark_theme": true}')
    assert config.language(path) == "en" and config.dark_mode(path) is True
    path.write_text('{"language": "klingon", "dark_theme": "si"}')
    assert config.language(path) is None and config.dark_mode(path) is None
    config.set_option("dark_theme", None, path)                  # volver a «Sistema»
    assert config.dark_mode(path) is None


def test_poster_size_and_sort_order_have_defaults(tmp_path: Path):
    path = tmp_path / "config.json"
    assert config.poster_size(path) == 96 and config.sort_desc(path) is False
    path.write_text('{"poster_size": 160, "sort_desc": true}')
    assert config.poster_size(path) == 160 and config.sort_desc(path) is True
    path.write_text('{"poster_size": "grande", "sort_desc": 1}')
    assert config.poster_size(path) == 96 and config.sort_desc(path) is False


def test_without_a_database_there_is_nothing_to_back_up(tmp_path: Path):
    assert config.make_backup(tmp_path / "no.sqlite3", tmp_path / "backups") is None


def test_only_the_last_ten_backups_are_kept(tmp_path: Path):
    db = tmp_path / "joseflix.sqlite3"
    db.write_bytes(b"datos")
    backups = tmp_path / "backups"
    for _ in range(13):
        config.make_backup(db, backups)
    kept = config.list_backups(backups)
    assert len(kept) == config.BACKUPS_KEPT
    assert kept == sorted(kept, reverse=True)                   # las más recientes primero


def test_restoring_replaces_the_database_after_saving_the_current_state(tmp_path: Path):
    db = tmp_path / "joseflix.sqlite3"
    backups = tmp_path / "backups"
    db.write_bytes(b"antes")
    old = config.make_backup(db, backups)
    db.write_bytes(b"despues")
    config.restore_backup(old, db, backups)
    assert db.read_bytes() == b"antes"
    assert any(b.read_bytes() == b"despues" for b in config.list_backups(backups))   # copia de seguridad previa
