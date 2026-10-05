"""Base de datos SQLite de peticiones y peticionarios."""
import sqlite3
from pathlib import Path

from . import config


class Store:
    def __init__(self, db_path: Path | None = None):
        self.path = db_path or config.DB
        self.path.parent.mkdir(parents=True, exist_ok=True)
        config.make_backup(self.path, self.path.parent / "backups")   # copia de seguridad al abrir
        self.db = sqlite3.connect(self.path)
        self.db.row_factory = sqlite3.Row
        self.db.execute(
            "CREATE TABLE IF NOT EXISTS requests (id INTEGER PRIMARY KEY,tmdb_id INTEGER,media_type TEXT,title TEXT,"
            "year TEXT,overview TEXT,poster_path TEXT,tmdb_url TEXT,requester TEXT,status TEXT,download_method TEXT,"
            "download_url TEXT,notes TEXT,priority TEXT,request_date TEXT)")
        for column in ("priority TEXT", "request_date TEXT"):   # bases creadas por versiones anteriores
            try:
                self.db.execute(f"ALTER TABLE requests ADD COLUMN {column}")
            except sqlite3.OperationalError:
                pass
        self.db.execute("CREATE TABLE IF NOT EXISTS requesters (name TEXT PRIMARY KEY)")
        self.db.execute('INSERT OR IGNORE INTO requesters SELECT DISTINCT requester FROM requests WHERE requester!=""')
        self.db.commit()

    def rows(self, text="", status=None, media_type=None, requester=None, priority=None, date="", desc=False):
        """Las peticiones filtradas, por fecha de solicitud. Los filtros de `None` no se aplican; son claves."""
        query = "SELECT * FROM requests WHERE title LIKE ?"
        args = [f"%{text}%"]
        for value, column in ((status, "status"), (media_type, "media_type"), (requester, "requester"),
                              (priority, "priority")):
            if value is not None:
                query += f" AND {column}=?"
                args.append(value)
        if date:
            query += " AND request_date LIKE ?"
            args.append(f"%{date}%")
        order = "DESC" if desc else "ASC"
        return self.db.execute(
            query + f" ORDER BY (request_date IS NULL), request_date {order}, id {order}", args).fetchall()

    def requesters(self) -> list[str]:
        return [row[0] for row in self.db.execute("SELECT name FROM requesters ORDER BY name")]

    def save(self, data: dict, ident=None) -> None:
        if ident:
            self.db.execute("UPDATE requests SET " + ",".join(f"{k}=?" for k in data) + " WHERE id=?",
                            [*data.values(), ident])
        else:
            self.db.execute("INSERT INTO requests (" + ",".join(data) + ") VALUES ("
                            + ",".join("?" for _field in data) + ")", list(data.values()))
        self.db.commit()

    def delete(self, ident) -> None:
        self.db.execute("DELETE FROM requests WHERE id=?", (ident,))
        self.db.commit()

    def notified_count(self) -> int:
        return self.db.execute("SELECT COUNT(*) FROM requests WHERE status='Notificado'").fetchone()[0]

    def clear_notified(self) -> None:
        for ident in [row["id"] for row in self.db.execute("SELECT id FROM requests WHERE status='Notificado'")]:
            self.delete(ident)

    def add_requester(self, name: str) -> None:
        self.db.execute("INSERT OR IGNORE INTO requesters(name) VALUES (?)", (name,))
        self.db.commit()

    def rename_requester(self, old: str, new: str) -> None:
        self.db.execute("UPDATE requesters SET name=? WHERE name=?", (new, old))
        self.db.execute("UPDATE requests SET requester=? WHERE requester=?", (new, old))
        self.db.commit()

    def delete_requester(self, name: str) -> None:
        self.db.execute("DELETE FROM requesters WHERE name=?", (name,))
        self.db.execute('UPDATE requests SET requester="" WHERE requester=?', (name,))
        self.db.commit()
