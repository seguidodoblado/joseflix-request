#!/usr/bin/env python3
import json, os, re, sqlite3, urllib.parse, urllib.request
from pathlib import Path
import gi
gi.require_version('Gtk','4.0')
from gi.repository import Gtk, Gio, GLib, GdkPixbuf, Gdk

APP_DIR=Path(os.environ.get('XDG_DATA_HOME',Path.home()/'.local/share'))/'joseflix-request'; APP_DIR.mkdir(parents=True,exist_ok=True)
DB=APP_DIR/'joseflix.sqlite3'; STATUSES=['📨 Solicitado','🔎 Buscando','📥 Descargado','📤 Subido','✅ Notificado']; TYPES=['🎬 Película','📺 Serie']; METHODS=['DD','Torrent','ED2K']; APP_VERSION=(Path(__file__).with_name('VERSION').read_text().strip() if Path(__file__).with_name('VERSION').exists() else '1.0.0')
CONFIG=APP_DIR/'config.json'
def get_token():
 try: return json.loads(CONFIG.read_text()).get('tmdb_token','')
 except (FileNotFoundError, json.JSONDecodeError): return os.environ.get('TMDB_API_KEY','')
def set_token(value): CONFIG.write_text(json.dumps({'tmdb_token':value}))
def plain(x): return x.split(' ',1)[-1]
class Store:
 def __init__(s):
  s.db=sqlite3.connect(DB); s.db.row_factory=sqlite3.Row; s.db.execute('CREATE TABLE IF NOT EXISTS requests (id INTEGER PRIMARY KEY,tmdb_id INTEGER,media_type TEXT,title TEXT,year TEXT,overview TEXT,poster_path TEXT,tmdb_url TEXT,requester TEXT,status TEXT,download_method TEXT,download_url TEXT,notes TEXT)'); s.db.execute('CREATE TABLE IF NOT EXISTS requesters (name TEXT PRIMARY KEY)'); s.db.execute('INSERT OR IGNORE INTO requesters SELECT DISTINCT requester FROM requests WHERE requester!=""'); s.db.commit()
 def rows(s,text='',status='Todos',typ='Todos',requester='Todos'):
  q='SELECT * FROM requests WHERE title LIKE ?'; a=[f'%{text}%']
  for v,c in [(plain(status),'status'),(plain(typ),'media_type'),(requester,'requester')]:
   if v!='Todos': q+=f' AND {c}=?'; a.append(v)
  return s.db.execute(q+' ORDER BY id DESC',a).fetchall()
 def requesters(s): return [x[0] for x in s.db.execute('SELECT name FROM requesters ORDER BY name')]
 def save(s,d,ident=None):
  if ident: s.db.execute('UPDATE requests SET '+','.join(f'{k}=?' for k in d)+' WHERE id=?',[*d.values(),ident])
  else: s.db.execute('INSERT INTO requests ('+','.join(d)+') VALUES ('+','.join('?' for _ in d)+')',list(d.values()))
  s.db.commit()
 def delete(s,i): s.db.execute('DELETE FROM requests WHERE id=?',(i,)); s.db.commit()
 def add_requester(s,n): s.db.execute('INSERT OR IGNORE INTO requesters(name) VALUES (?)',(n,)); s.db.commit()
 def rename_requester(s,o,n): s.db.execute('UPDATE requesters SET name=? WHERE name=?',(n,o)); s.db.execute('UPDATE requests SET requester=? WHERE requester=?',(n,o)); s.db.commit()
 def delete_requester(s,n): s.db.execute('DELETE FROM requesters WHERE name=?',(n,)); s.db.execute('UPDATE requests SET requester="" WHERE requester=?',(n,)); s.db.commit()
def tmdb(url):
 token=get_token(); p=urllib.parse.urlparse(url).path.strip('/').split('/'); m=re.match(r'(\d+)',p[1]) if len(p)>1 else None
 if not token: raise ValueError('Configura el token de TMDB desde Ajustes')
 if len(p)<2 or p[0] not in ('movie','tv') or not m: raise ValueError('URL TMDB no válida')
 req=urllib.request.Request(f'https://api.themoviedb.org/3/{p[0]}/{m.group(1)}?language=es-ES',headers={'Authorization':'Bearer '+token})
 with urllib.request.urlopen(req,timeout=15) as h: d=json.load(h)
 poster=d.get('poster_path') or ''; local=''
 if poster:
  local=str(APP_DIR/'posters'/f'{m.group(1)}.jpg'); Path(local).parent.mkdir(exist_ok=True)
  if not Path(local).exists():
   with urllib.request.urlopen('https://image.tmdb.org/t/p/w342'+poster,timeout=15) as h: Path(local).write_bytes(h.read())
 return {'tmdb_id':int(m.group(1)),'media_type':'Película' if p[0]=='movie' else 'Serie','title':d.get('title') or d.get('name',''),'year':(d.get('release_date') or d.get('first_air_date',''))[:4],'overview':d.get('overview',''),'poster_path':local,'tmdb_url':url}
class Editor(Gtk.Dialog):
 def __init__(s,parent,store,row=None):
  super().__init__(title='Editar petición' if row else 'Nueva petición',transient_for=parent,modal=True,default_width=900,default_height=850); s.store=store; s.row=row; outer=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=8); box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=8); box.set_margin_start(16); box.set_margin_end(16); box.set_margin_top(16); box.set_margin_bottom(16); scroll=Gtk.ScrolledWindow(); scroll.set_policy(Gtk.PolicyType.NEVER,Gtk.PolicyType.AUTOMATIC); scroll.set_vexpand(True); scroll.set_child(box); outer.append(scroll); s.set_child(outer)
  s.heading=Gtk.Label(); s.heading.set_markup(f'<big><b>{row["title"]} ({row["year"] or "—"})</b></big>' if row else '<big><b>Nueva petición</b></big>'); box.append(s.heading); s.preview=Gtk.Box(spacing=16); box.append(s.preview); s.poster=Gtk.Image(); s.poster.set_pixel_size(260); s.preview.append(s.poster); s.overview=Gtk.Label(label=row['overview'] if row else 'La sinopsis aparecerá al consultar TMDB.'); s.overview.set_wrap(True); s.overview.set_max_width_chars(65); s.overview.set_valign(Gtk.Align.START); s.preview.append(s.overview)
  grid=Gtk.Grid(column_spacing=10,row_spacing=8); box.append(grid); s.fields={}; vals=[('URL TMDB:',row['tmdb_url'] if row else ''),('Peticionario:',row['requester'] if row else ''),('Enlace de descarga:',row['download_url'] if row else ''),('Notas:',row['notes'] if row else '')]
  for i,(n,v) in enumerate([vals[0],vals[2]]): grid.attach(Gtk.Label(label=n,xalign=0),0,[0,2][i],1,1); e=Gtk.Entry(); e.set_text(v); e.set_hexpand(True); grid.attach(e,1,[0,2][i],1,1); s.fields[n]=e
  grid.attach(Gtk.Label(label='Notas:',xalign=0,valign=Gtk.Align.START),0,3,1,1); notes=Gtk.TextView(); notes.set_wrap_mode(Gtk.WrapMode.WORD_CHAR); notes.set_vexpand(True); notes.set_size_request(500,110); notes.get_buffer().set_text(vals[3][1]); notes_scroll=Gtk.ScrolledWindow(); notes_scroll.set_min_content_height(110); notes_scroll.set_hexpand(True); notes_scroll.set_child(notes); grid.attach(notes_scroll,1,3,1,1); s.fields['Notas:']=notes
  s.requester=Gtk.DropDown.new_from_strings(store.requesters() or ['Sin peticionario']); s.requester.set_selected(next((i for i,x in enumerate(store.requesters()) if row and x==row['requester']),0)); grid.attach(Gtk.Label(label='Peticionario:',xalign=0),0,1,1,1); grid.attach(s.requester,1,1,1,1)
  s.status=Gtk.DropDown.new_from_strings(STATUSES); s.status.set_selected(next((i for i,x in enumerate(STATUSES) if row and plain(x)==row['status']),0)); grid.attach(Gtk.Label(label='Estado:',xalign=0),0,4,1,1); grid.attach(s.status,1,4,1,1)
  s.typ=Gtk.DropDown.new_from_strings(TYPES); s.typ.set_selected(0 if not row or row['media_type']=='Película' else 1); grid.attach(Gtk.Label(label='Tipo:',xalign=0),0,5,1,1); grid.attach(s.typ,1,5,1,1)
  s.method=Gtk.DropDown.new_from_strings(METHODS); s.method.set_selected(METHODS.index(row['download_method']) if row and row['download_method'] in METHODS else 0); grid.attach(Gtk.Label(label='Método de descarga:',xalign=0),0,6,1,1); grid.attach(s.method,1,6,1,1)
  cancel=Gtk.Button(label='Cancelar'); save=Gtk.Button(label='Guardar'); actions=Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,spacing=8); actions.set_halign(Gtk.Align.END); actions.set_margin_start(16); actions.set_margin_end(16); actions.set_margin_bottom(16); actions.append(cancel)
  if row and row['download_url']:
   open_link=Gtk.Button(label='Abrir enlace'); open_link.connect('clicked',lambda *_: Gio.AppInfo.launch_default_for_uri(row['download_url'],None)); actions.append(open_link)
  if row:
   remove=Gtk.Button(label='Eliminar'); actions.append(remove)
   def confirm_delete(*_):
    confirm=Gtk.MessageDialog(transient_for=s,text=f'¿Eliminar la petición «{row["title"]}»?',buttons=Gtk.ButtonsType.YES_NO); confirm.connect('response',lambda dialog,response:(s.store.delete(row['id']),s.close()) if response==Gtk.ResponseType.YES else dialog.close()); confirm.present()
   remove.connect('clicked',confirm_delete)
  actions.append(save); outer.append(actions); cancel.connect('clicked',lambda *_:s.close()); save.connect('clicked',lambda *_:s.response(None,Gtk.ResponseType.OK)); s.present()
  if row and row['poster_path'] and Path(row['poster_path']).exists(): s.poster.set_from_file(row['poster_path'])
 def response(s,_,response):
  if response==Gtk.ResponseType.OK:
   try: s.data=tmdb(s.fields['URL TMDB:'].get_text()); s.data.update(requester='' if not s.store.requesters() else s.requester.get_selected_item().get_string(),download_url=s.fields['Enlace de descarga:'].get_text(),notes=s.fields['Notas:'].get_buffer().get_text(s.fields['Notas:'].get_buffer().get_start_iter(),s.fields['Notas:'].get_buffer().get_end_iter(),False),status=plain(s.status.get_selected_item().get_string()),media_type=plain(s.typ.get_selected_item().get_string()),download_method=s.method.get_selected_item().get_string()); s.store.save(s.data,s.row['id'] if s.row else None)
   except Exception as e: s.error=Gtk.MessageDialog(transient_for=s,text=str(e),buttons=Gtk.ButtonsType.OK); s.error.show(); return
  s.close()
class App(Gtk.Application):
 def __init__(s): super().__init__(application_id='es.joseflix.Request'); s.store=Store()
 def do_activate(s):
  s.win=Gtk.ApplicationWindow(application=s,title='Joseflix — Peticiones',default_width=1100,default_height=700); root=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=8); root.set_margin_start(12); root.set_margin_end(12); root.set_margin_top(8); root.set_margin_bottom(8); s.win.set_child(root); menu=Gio.Menu(); menu.append('Configurar TMDB…','app.settings'); menu.append('Gestionar peticionarios…','app.requesters'); view=Gio.Menu(); view.append('Modo claro','app.light'); view.append('Modo oscuro','app.dark'); helpm=Gio.Menu(); helpm.append('Acerca de','app.about'); menubar=Gtk.Box(spacing=8); ajustes=Gtk.MenuButton(label='⚙ Ajustes'); ver=Gtk.MenuButton(label='◐ Tema'); ayuda=Gtk.MenuButton(label='? Ayuda'); ajustes.set_menu_model(menu); ver.set_menu_model(view); ayuda.set_menu_model(helpm); menubar.append(ajustes); menubar.append(ver); menubar.append(ayuda); root.append(menubar)
  bar=Gtk.Box(spacing=8); root.append(bar); s.search=Gtk.SearchEntry(placeholder_text='Buscar título'); s.status=Gtk.DropDown.new_from_strings(['Todos']+STATUSES); s.typ=Gtk.DropDown.new_from_strings(['Todos']+TYPES); s.req=Gtk.DropDown.new_from_strings(['Todos']+s.store.requesters()); add=Gtk.Button(label='Nueva petición'); add.connect('clicked',lambda *_:s.new()); bar.append(s.search); bar.append(Gtk.Label(label='Estado:')); bar.append(s.status); bar.append(Gtk.Label(label='Tipo:')); bar.append(s.typ); bar.append(Gtk.Label(label='Peticionario:')); bar.append(s.req); bar.append(add); s.search.connect('search-changed',lambda *_:s.refresh()); [x.connect('notify::selected-item',lambda *_:s.refresh()) for x in [s.status,s.typ,s.req]]; s.list=Gtk.ListBox(); s.list.set_activate_on_single_click(False); s.list.connect('row-activated',lambda _,row:s.open(row.data)); scroll=Gtk.ScrolledWindow(); scroll.set_policy(Gtk.PolicyType.AUTOMATIC,Gtk.PolicyType.AUTOMATIC); scroll.set_vexpand(True); scroll.set_child(s.list); root.append(scroll); s.refresh(); s.add_actions()
  s.win.set_default_size(1100,700); s.win.set_decorated(True); s.win.set_resizable(True); s.win.present()
 def add_actions(s):
  for name,fn in [('settings',s.settings),('requesters',s.requesters),('about',s.about),('light',lambda:s.theme(False)),('dark',lambda:s.theme(True))]: a=Gio.SimpleAction.new(name,None); a.connect('activate',lambda _,__,f=fn:f()); s.add_action(a)
 def refresh(s):
  while (r:=s.list.get_row_at_index(0)): s.list.remove(r)
  for r in s.store.rows(s.search.get_text(),s.status.get_selected_item().get_string(),s.typ.get_selected_item().get_string(),s.req.get_selected_item().get_string()):
   row=Gtk.ListBoxRow(); row.data=r; box=Gtk.Box(spacing=12); image=Gtk.Image(); image.set_pixel_size(120); image.set_from_file(r['poster_path']) if r['poster_path'] and Path(r['poster_path']).exists() else None; box.append(image); box.append(Gtk.Label(label=f"{r['title']} ({r['year'] or '—'})  ·  {r['media_type']}  ·  {r['requester']}  ·  {r['status']}\n{r['download_url'] or 'Sin enlace de descarga'}",xalign=0)); row.set_child(box); s.list.append(row)
 def new(s):
  d=Editor(s.win,s.store); d.connect('response',lambda *_:s.refresh()); d.present()
 def open(s,r):
  d=Editor(s.win,s.store,r); d.connect('response',lambda *_:s.refresh()); d.connect('close-request',lambda *_:s.refresh()); d.present()
 def settings(s):
  d=Gtk.Dialog(title='Ajustes de TMDB',transient_for=s.win,modal=True); box=d.get_content_area(); box.append(Gtk.Label(label='Token de acceso de lectura de TMDB')); e=Gtk.Entry(); e.set_text(get_token()); e.set_hexpand(True); box.append(e); d.add_button('Cancelar',Gtk.ResponseType.CANCEL); d.add_button('Guardar',Gtk.ResponseType.OK); d.connect('response',lambda x,r:(set_token(e.get_text().strip()),x.close()) if r==Gtk.ResponseType.OK else x.close()); d.present()
 def requesters(s):
  d=Gtk.Dialog(title='Gestionar peticionarios',transient_for=s.win,modal=True); box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=8); box.set_margin_start(16); box.set_margin_end(16); box.set_margin_top(16); box.set_margin_bottom(16); d.set_child(box); lst=Gtk.ListBox(); lst.set_vexpand(True); box.append(lst); entry=Gtk.Entry(); entry.set_placeholder_text('Nuevo nombre'); box.append(entry); buttons=Gtk.Box(spacing=6); box.append(buttons)
  def load():
   while (r:=lst.get_row_at_index(0)): lst.remove(r)
   for n in s.store.requesters(): lst.append(Gtk.Label(label=n,xalign=0))
  add=Gtk.Button(label='Crear'); edit=Gtk.Button(label='Editar'); remove=Gtk.Button(label='Borrar'); buttons.append(add); buttons.append(edit); buttons.append(remove)
  def valid():
   name=entry.get_text().strip()
   if not name:
    warning=Gtk.MessageDialog(transient_for=d,text='El nombre del peticionario no puede estar vacío',buttons=Gtk.ButtonsType.OK); warning.connect('response',lambda dialog,_:dialog.close()); warning.present(); return None
   return name
  def create(*_):
   if (name:=valid()): s.store.add_requester(name); entry.set_text(''); load(); s.refresh()
  def rename(*_):
   selected=lst.get_selected_row()
   if selected and (name:=valid()): s.store.rename_requester(selected.get_child().get_text(),name); load(); lst.select_row(None); entry.set_text(''); s.refresh()
  def delete_requester(*_):
   selected=lst.get_selected_row()
   if not selected: return
   name=selected.get_child().get_text(); confirm=Gtk.MessageDialog(transient_for=d,text=f'¿Eliminar el peticionario «{name}»?',buttons=Gtk.ButtonsType.YES_NO); confirm.connect('response',lambda dialog,response:(s.store.delete_requester(name),load(),s.refresh(),dialog.close()) if response==Gtk.ResponseType.YES else dialog.close()); confirm.present()
  lst.connect('row-selected',lambda _,row: entry.set_text(row.get_child().get_text()) if row else entry.set_text('')); add.connect('clicked',create); edit.connect('clicked',rename); remove.connect('clicked',delete_requester); load(); d.present(); GLib.idle_add(lambda: (lst.select_row(None),entry.set_text(''),False)[-1])
 def about(s):
  d=Gtk.Dialog(title='Acerca de Joseflix Request',transient_for=s.win,modal=True); box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=10); box.set_margin_start(28); box.set_margin_end(28); box.set_margin_top(24); box.set_margin_bottom(24); d.set_child(box); icon=Gtk.Image(); icon_path='/usr/share/icons/hicolor/scalable/apps/joseflix-request.svg'; icon.set_from_file(icon_path if Path(icon_path).exists() else str(Path(__file__).with_name('joseflix-request.svg'))); icon.set_pixel_size(96); box.append(icon); info=Gtk.Label(); info.set_markup(f'<big><b>Joseflix Request</b></big>\n\nVersión {APP_VERSION}\nGestor de peticiones para Joseflix\n\nDesarrollador:\nseguidodoblado\njose.antonio.seguido@gmail.com\n\nDependencia:\nPyGObject + GTK 4'); info.set_justify(Gtk.Justification.CENTER); box.append(info); close=Gtk.Button(label='Cerrar'); close.set_halign(Gtk.Align.CENTER); close.connect('clicked',lambda *_:d.close()); box.append(close); d.present()
 def theme(s,dark):
  settings=Gtk.Settings.get_default(); settings.set_property('gtk-theme-name','Adwaita-dark' if dark else 'Adwaita'); settings.set_property('gtk-application-prefer-dark-theme',dark)
App().run()
