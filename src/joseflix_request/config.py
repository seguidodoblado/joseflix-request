"""Rutas y ajustes del usuario: datos en ~/.local/share/joseflix-request y copias de seguridad de la base."""
import json
import os
import shutil
from datetime import datetime
from pathlib import Path

LANGUAGES = ("es", "en")   # idiomas que se pueden elegir en Ajustes (None: el del sistema)
BACKUPS_KEPT = 10

APP_DIR = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local/share") / "joseflix-request"
DB = APP_DIR / "joseflix.sqlite3"
CONFIG = APP_DIR / "config.json"
BACKUPS_DIR = APP_DIR / "backups"
POSTERS_DIR = APP_DIR / "posters"


def ensure_dirs() -> None:
    BACKUPS_DIR.mkdir(parents=True, exist_ok=True)


def read_config(path: Path | None = None) -> dict:
    try:
        data = json.loads((path or CONFIG).read_text())
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def set_option(key: str, value, path: Path | None = None) -> None:
    """Guarda una opción sin tocar las demás."""
    path = path or CONFIG
    config = read_config(path)
    config[key] = value
    path.parent.mkdir(parents=True, exist_ok=True)
    # El token de TMDB se guarda en claro: el archivo queda legible solo por el usuario.
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(descriptor, "w") as handle:
        handle.write(json.dumps(config))
    path.chmod(0o600)


def get_token(path: Path | None = None) -> str:
    try:
        return json.loads((path or CONFIG).read_text()).get("tmdb_token", "")
    except (FileNotFoundError, json.JSONDecodeError):
        return os.environ.get("TMDB_API_KEY", "")


def set_token(value: str, path: Path | None = None) -> None:
    set_option("tmdb_token", value, path)


def language(path: Path | None = None) -> str | None:
    """El idioma elegido, o None para seguir el del sistema (un valor desconocido se ignora)."""
    value = read_config(path).get("language")
    return value if value in LANGUAGES else None


def dark_mode(path: Path | None = None) -> bool | None:
    """El tema elegido (True oscuro, False claro), o None para seguir el del sistema."""
    value = read_config(path).get("dark_theme")
    return value if isinstance(value, bool) else None


def poster_size(path: Path | None = None) -> int:
    value = read_config(path).get("poster_size", 96)
    return value if isinstance(value, int) and not isinstance(value, bool) and value > 0 else 96


def sort_desc(path: Path | None = None) -> bool:
    return read_config(path).get("sort_desc") is True


def make_backup(db: Path | None = None, backups_dir: Path | None = None, keep: int = BACKUPS_KEPT):
    """Copia la base de datos a la carpeta de copias y conserva solo las `keep` últimas."""
    db, backups_dir = db or DB, backups_dir or BACKUPS_DIR
    if not db.exists():
        return None
    backups_dir.mkdir(parents=True, exist_ok=True)
    dest = backups_dir / f'joseflix-{datetime.now().astimezone().strftime("%Y%m%d-%H%M%S-%f")}.sqlite3'
    shutil.copy2(db, dest)
    for old in sorted(backups_dir.glob("joseflix-*.sqlite3"))[:-keep]:
        old.unlink()
    return dest


def list_backups(backups_dir: Path | None = None) -> list[Path]:
    return sorted((backups_dir or BACKUPS_DIR).glob("joseflix-*.sqlite3"), reverse=True)


def restore_backup(source: Path, db: Path | None = None, backups_dir: Path | None = None) -> None:
    """Sustituye la base de datos por una copia, guardando antes una copia del estado actual."""
    db = db or DB
    make_backup(db, backups_dir)
    shutil.copy2(source, db)
