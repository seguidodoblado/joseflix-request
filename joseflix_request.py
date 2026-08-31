#!/usr/bin/env python3
import json, os, sqlite3, urllib.parse, urllib.request
from pathlib import Path

from gi.repository import Gtk, Gio, GdkPixbuf

APP_DIR = Path(os.environ.get("XDG_DATA_HOME", Path.home()/".local/share")) / "joseflix-request"
DB_PATH = APP_DIR / "joseflix.sqlite3"
STATUSES = ["Solicitado", "Buscando", "Descargado", "Subido", "Notificado"]
METHODS = ["DD", "Torrent", "ED2K"]

class Store:
    def __init__(self):
        APP_DIR.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(DB_PATH)
        self.db.row_factory = sqlite3.Row
        self.db.execute("""CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY, tmdb_id INTEGER, media_type TEXT NOT NULL,
            title TEXT NOT NULL, year TEXT, overview TEXT, poster_path TEXT,
            tmdb_url TEXT NOT NULL, requester TEXT NOT NULL, status TEXT NOT NULL,
            download_method TEXT, download_url TEXT, notes TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
        self.db.commit()
    def all(self, text="", status="Todos", requester="Todos", media="Todos"):
        q = "SELECT * FROM requests WHERE (title LIKE ? OR requester LIKE ?)"
        args = [f"%{text}%", f"%{text}%"]
        if status != "Todos": q += " AND status=?"; args.append(status)
        if requester != "Todos": q += " AND requester=?"; args.append(requester)
        if media != "Todos": q += " AND media_type=?"; args.append(media)
        return self.db.execute(q + " ORDER BY updated_at DESC, id DESC", args).fetchall()
    def requesters(self):
        return [r[0] for r in self.db.execute("SELECT DISTINCT requester FROM requests ORDER BY requester")]
    def save(self, data, ident=None):
        if ident:
            fields = ", ".join(f"{k}=?" for k in data)
            self.db.execute(f"UPDATE requests SET {fields}, updated_at=CURRENT_TIMESTAMP WHERE id=?", [*data.values(), ident])
        else:
            keys = ",".join(data); marks = ",".join("?" for _ in data)
            self.db.execute(f"INSERT INTO requests ({keys}) VALUES ({marks})", list(data.values()))
        self.db.commit()

def tmdb_id_from_url(url):
    parts = urllib.parse.urlparse(url).path.strip("/").split("/")
    if len(parts) >= 2 and parts[1].isdigit() and parts[0] in ("movie", "tv"):
        return parts[0], int(parts[1])
    raise ValueError("La URL debe ser una URL de TMDB de película o serie")

def tmdb_fetch(url):
    key = os.environ.get("TMDB_API_KEY")
    if not key: raise ValueError("Configura TMDB_API_KEY antes de consultar TMDB")
    kind, ident = tmdb_id_from_url(url)
    endpoint = f"https://api.themoviedb.org/3/{kind}/{ident}?api_key={urllib.parse.quote(key)}&language=es-ES&append_to_response=images"
    with urllib.request.urlopen(endpoint, timeout=15) as response: data = json.load(response)
    title = data.get("title") or data.get("name") or "Sin título"
    date = data.get("release_date") or data.get("first_air_date") or ""
    posters = [data.get("poster_path")] + [x.get("file_path") for x in data.get("images", {}).get("posters", [])]
    return {"tmdb_id": ident, "media_type": "Película" if kind == "movie" else "Serie", "title": title,
            "year": date[:4], "overview": data.get("overview", ""), "poster_path": next((p for p in posters if p), ""), "tmdb_url": url}

class App(Gtk.Application):
    def __init__(self): super().__init__(application_id="es.joseflix.Requests", flags=Gio.ApplicationFlags.DEFAULT_FLAGS); self.store=Store()
    def do_activate(self):
        self.window=Gtk.ApplicationWindow(application=self, title="Joseflix — Peticiones", default_width=1100, default_height=700)
        root=Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8); root.set_margin_top(12); root.set_margin_bottom(12); root.set_margin_start(12); root.set_margin_end(12); self.window.set_child(root)
        bar=Gtk.Box(spacing=8); root.append(bar)
        self.search=Gtk.SearchEntry(placeholder_text="Buscar título o peticionario"); self.search.connect("search-changed", lambda *_: self.refresh()); bar.append(self.search)
        self.status=self.combo(["Todos"]+STATUSES); self.status.connect("changed", lambda *_: self.refresh()); bar.append(self.status)
        self.media=self.combo(["Todos", "Película", "Serie"]); self.media.connect("changed", lambda *_: self.refresh()); bar.append(self.media)
        self.requester=self.combo(["Todos"]); self.requester.connect("changed", lambda *_: self.refresh()); bar.append(self.requester)
        add=Gtk.Button(label="Nueva petición"); add.connect("clicked", lambda *_: self.edit_dialog()); bar.append(add)
        self.list=Gtk.ListBox(); self.list.set_selection_mode(Gtk.SelectionMode.SINGLE); self.list.connect("row-activated", lambda _,row: self.edit_dialog(row.req["id"])); root.append(self.list)
        self.refresh(); self.window.present()
    def combo(self, values):
        c=Gtk.ComboBoxText(); [c.append_text(x) for x in values]; c.set_active(0); return c
    def refresh(self):
        while (r:=self.list.get_row_at_index(0)): self.list.remove(r)
        rows=self.store.all(self.search.get_text(),self.status.get_active_text(),self.requester.get_active_text(),self.media.get_active_text())
        for item in rows:
            row=Gtk.ListBoxRow(); row.req=item; box=Gtk.Box(spacing=12); box.set_margin_top(8); box.set_margin_bottom(8); box.set_margin_start(8); box.set_margin_end(8)
            if item["poster_path"]:
                try:
                    pix=GdkPixbuf.Pixbuf.new_from_file_at_scale(str(APP_DIR/item["poster_path"].split("/")[-1]),80,110,True); box.append(Gtk.Image.new_from_pixbuf(pix))
                except Exception: pass
            label=Gtk.Label(label=f"{item['title']} ({item['year'] or '—'})\n{item['media_type']} · {item['requester']} · {item['status']}\n{item['download_method'] or 'Sin método'}", xalign=0); label.set_wrap(True); box.append(label); row.set_child(box); self.list.append(row)
        self.requester.remove_all(); self.requester.append_text("Todos"); [self.requester.append_text(x) for x in self.store.requesters()]; self.requester.set_active(0)
    def edit_dialog(self, ident=None):
        d=Gtk.MessageDialog(transient_for=self.window, modal=True, text="Nueva petición" if not ident else "Editar petición"); d.add_button("Cancelar",Gtk.ResponseType.CANCEL); d.add_button("Guardar",Gtk.ResponseType.OK)
        grid=Gtk.Grid(column_spacing=8,row_spacing=8,margin_top=8,margin_bottom=8,margin_start=8,margin_end=8); d.get_content_area().append(grid)
        fields=[("URL TMDB",Gtk.Entry()),("Peticionario",Gtk.Entry()),("Estado",self.combo(STATUSES)),("Tipo",self.combo(["Película","Serie"])),("Método",self.combo(METHODS)),("Enlace de descarga",Gtk.Entry()),("Notas",Gtk.Entry())]
        for i,(name,w) in enumerate(fields): grid.attach(Gtk.Label(label=name,xalign=0),0,i,1,1); grid.attach(w,1,i,1,1)
        def response(_, response):
            if response==Gtk.ResponseType.OK:
                try:
                    meta=tmdb_fetch(fields[0][1].get_text()); data={**meta,"requester":fields[1][1].get_text(),"status":fields[2][1].get_active_text(),"download_method":fields[4][1].get_active_text(),"download_url":fields[5][1].get_text(),"notes":fields[6][1].get_text()}; self.store.save(data,ident); d.destroy(); self.refresh()
                except Exception as e: d.set_property("secondary-text",str(e))
            else: d.destroy()
        d.connect("response",response); d.present()

if __name__ == "__main__": App().run()
