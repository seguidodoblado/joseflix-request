import sqlite3
from pathlib import Path

import pytest

from joseflix_request.store import Store


@pytest.fixture
def store(tmp_path: Path) -> Store:
    return Store(tmp_path / "joseflix.sqlite3")


def request(title, status="Solicitado", requester="", date="2026-10-01", media="Película", priority="Normal"):
    return {"tmdb_id": 1, "media_type": media, "title": title, "year": "2020", "overview": "", "poster_path": "",
            "tmdb_url": "", "requester": requester, "status": status, "download_method": "Sin método",
            "download_url": "", "notes": "", "priority": priority, "request_date": date}


def test_saves_and_lists_requests(store: Store):
    store.save(request("Alien"))
    store.save(request("Blade Runner"))
    assert [r["title"] for r in store.rows()] == ["Alien", "Blade Runner"]


def test_editing_updates_the_row_instead_of_adding_one(store: Store):
    store.save(request("Alien"))
    ident = store.rows()[0]["id"]
    store.save({"title": "Aliens", "status": "Buscando"}, ident)
    (row,) = store.rows()
    assert row["title"] == "Aliens" and row["status"] == "Buscando"


def test_filters_are_combined_and_none_means_no_filter(store: Store):
    store.save(request("Alien", status="Buscando", requester="Ana", media="Película", priority="Alta"))
    store.save(request("Alien 2", status="Subido", requester="Ana", media="Película", priority="Baja"))
    store.save(request("Dark", status="Buscando", requester="Luis", media="Serie", priority="Alta"))
    titles = lambda **kw: [r["title"] for r in store.rows(**kw)]
    assert titles() == ["Alien", "Alien 2", "Dark"]
    assert titles(status="Buscando") == ["Alien", "Dark"]
    assert titles(status="Buscando", media_type="Serie") == ["Dark"]
    assert titles(requester="Ana", priority="Alta") == ["Alien"]
    assert titles(text="alien") == ["Alien", "Alien 2"]            # LIKE no distingue mayúsculas


def test_the_date_filter_matches_part_of_the_date(store: Store):
    store.save(request("Octubre", date="2026-10-05"))
    store.save(request("Septiembre", date="2026-09-20"))
    assert [r["title"] for r in store.rows(date="2026-10")] == ["Octubre"]


def test_requests_without_a_date_go_last_in_both_orders(store: Store):
    store.save(request("Sin fecha", date=None))
    store.save(request("Vieja", date="2026-01-01"))
    store.save(request("Nueva", date="2026-10-01"))
    assert [r["title"] for r in store.rows()] == ["Vieja", "Nueva", "Sin fecha"]
    assert [r["title"] for r in store.rows(desc=True)] == ["Nueva", "Vieja", "Sin fecha"]


def test_requesters_are_listed_alphabetically_and_renaming_updates_the_requests(store: Store):
    for name in ("Luis", "Ana"):
        store.add_requester(name)
    store.add_requester("Ana")                                      # repetido: se ignora
    assert store.requesters() == ["Ana", "Luis"]
    store.save(request("Alien", requester="Ana"))
    store.rename_requester("Ana", "Anita")
    assert store.requesters() == ["Anita", "Luis"]
    assert store.rows()[0]["requester"] == "Anita"


def test_deleting_a_requester_keeps_their_requests_without_a_requester(store: Store):
    store.add_requester("Ana")
    store.save(request("Alien", requester="Ana"))
    store.delete_requester("Ana")
    assert store.requesters() == [] and store.rows()[0]["requester"] == ""


def test_clearing_notified_deletes_only_those(store: Store):
    store.save(request("Hecha", status="Notificado"))
    store.save(request("Pendiente", status="Buscando"))
    assert store.notified_count() == 1
    store.clear_notified()
    assert [r["title"] for r in store.rows()] == ["Pendiente"] and store.notified_count() == 0


def test_delete_removes_one_request(store: Store):
    store.save(request("Alien"))
    store.delete(store.rows()[0]["id"])
    assert store.rows() == []


def test_requesters_of_existing_requests_are_registered_when_opening(tmp_path: Path):
    path = tmp_path / "joseflix.sqlite3"
    first = Store(path)
    first.save(request("Alien", requester="Ana"))
    first.db.execute("DELETE FROM requesters")
    first.db.commit()
    first.db.close()
    assert Store(path).requesters() == ["Ana"]


def test_a_database_from_an_older_version_gets_the_new_columns(tmp_path: Path):
    path = tmp_path / "joseflix.sqlite3"
    old = sqlite3.connect(path)
    old.execute("CREATE TABLE requests (id INTEGER PRIMARY KEY,tmdb_id INTEGER,media_type TEXT,title TEXT,year TEXT,"
                "overview TEXT,poster_path TEXT,tmdb_url TEXT,requester TEXT,status TEXT,download_method TEXT,"
                "download_url TEXT,notes TEXT)")
    old.execute("INSERT INTO requests (title, requester, status) VALUES ('Vieja', 'Ana', 'Subido')")
    old.commit()
    old.close()
    row = Store(path).rows()[0]
    assert row["title"] == "Vieja" and row["priority"] is None and row["request_date"] is None


def test_opening_makes_a_backup_of_the_existing_database(tmp_path: Path):
    path = tmp_path / "joseflix.sqlite3"
    Store(path).db.close()
    Store(path).db.close()
    assert len(list((tmp_path / "backups").glob("joseflix-*.sqlite3"))) == 1   # la primera vez no había base
