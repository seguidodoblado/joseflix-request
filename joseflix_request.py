#!/usr/bin/env python3
import json, os, re, shutil, sqlite3, urllib.parse, urllib.request
from datetime import datetime
from pathlib import Path
import gi
gi.require_version('Gtk','4.0')
from gi.repository import Gtk, Gio, GLib, GdkPixbuf, Gdk, Pango

APP_DIR=Path(os.environ.get('XDG_DATA_HOME',Path.home()/'.local/share'))/'joseflix-request'; APP_DIR.mkdir(parents=True,exist_ok=True)
DB=APP_DIR/'joseflix.sqlite3'; STATUSES=['📨 Solicitado','🔎 Buscando','📥 Descargado','📤 Subido','✅ Notificado','🔧 Corregir']; TYPES=['🎬 Película','📺 Serie']; METHODS=['❓ Sin método','⬇️ JDownloader','🧲 Transmission','🐴 aMule']; PRIORITIES=['🔴 Alta','🟡 Normal','🟢 Baja']; APP_VERSION=(Path(__file__).with_name('VERSION').read_text().strip() if Path(__file__).with_name('VERSION').exists() else '1.0.0')
CONFIG=APP_DIR/'config.json'
def get_token():
 try: return json.loads(CONFIG.read_text()).get('tmdb_token','')
 except (FileNotFoundError, json.JSONDecodeError): return os.environ.get('TMDB_API_KEY','')
def set_token(value):
    cfg = {}
    try: cfg = json.loads(CONFIG.read_text())
    except (FileNotFoundError, json.JSONDecodeError): pass
    cfg['tmdb_token'] = value
    CONFIG.write_text(json.dumps(cfg))
BACKUPS_DIR=APP_DIR/'backups'; BACKUPS_DIR.mkdir(exist_ok=True)
def make_backup():
 if not DB.exists(): return None
 dest=BACKUPS_DIR/f'joseflix-{datetime.now().strftime("%Y%m%d-%H%M%S-%f")}.sqlite3'; shutil.copy2(DB,dest)
 for old in sorted(BACKUPS_DIR.glob('joseflix-*.sqlite3'))[:-10]: old.unlink()
 return dest
def list_backups(): return sorted(BACKUPS_DIR.glob('joseflix-*.sqlite3'),reverse=True)
def plain(x): return x.split(' ',1)[-1]
class Store:
 def __init__(s):
  make_backup(); s.db=sqlite3.connect(DB); s.db.row_factory=sqlite3.Row; s.db.execute('CREATE TABLE IF NOT EXISTS requests (id INTEGER PRIMARY KEY,tmdb_id INTEGER,media_type TEXT,title TEXT,year TEXT,overview TEXT,poster_path TEXT,tmdb_url TEXT,requester TEXT,status TEXT,download_method TEXT,download_url TEXT,notes TEXT,priority TEXT,request_date TEXT)')
  for col in ('priority TEXT','request_date TEXT'):
   try: s.db.execute(f'ALTER TABLE requests ADD COLUMN {col}')
   except sqlite3.OperationalError: pass
  s.db.execute('CREATE TABLE IF NOT EXISTS requesters (name TEXT PRIMARY KEY)'); s.db.execute('INSERT OR IGNORE INTO requesters SELECT DISTINCT requester FROM requests WHERE requester!=""'); s.db.commit()
 def rows(s,text='',status='Todos',typ='Todos',requester='Todos',priority='Todos',date=''):
  q='SELECT * FROM requests WHERE title LIKE ?'; a=[f'%{text}%']
  for v,c in [(plain(status),'status'),(plain(typ),'media_type'),(requester,'requester'),(plain(priority),'priority')]:
   if v!='Todos': q+=f' AND {c}=?'; a.append(v)
  if date: q+=' AND request_date LIKE ?'; a.append(f'%{date}%')
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
  s.heading=Gtk.Label(); s.heading.set_markup(f'<big><b>{row["title"]} ({row["year"] or "—"})</b></big>' if row else '<big><b>Nueva petición</b></big>'); box.append(s.heading); s.preview=Gtk.Box(spacing=16); box.append(s.preview); s.poster=Gtk.Image(); s.poster.set_pixel_size(260); s.preview.append(s.poster); s.overview=Gtk.Label(label=row['overview'] if row else 'La sinopsis aparecerá al consultar TMDB.'); s.overview.set_wrap(True); s.overview.set_justify(Gtk.Justification.FILL); s.overview.set_hexpand(True); s.overview.set_valign(Gtk.Align.START); s.preview.append(s.overview)
  grid=Gtk.Grid(column_spacing=10,row_spacing=8); box.append(grid); s.fields={}; vals=[('URL TMDB:',row['tmdb_url'] if row else ''),('Peticionario:',row['requester'] if row else ''),('Enlace de descarga:',row['download_url'] if row else ''),('Notas:',row['notes'] if row else ''),('Fecha de solicitud:',(row['request_date'] if row else None) or datetime.now().strftime('%Y-%m-%d'))]
  for i,(n,v) in enumerate([vals[0],vals[2]]): grid.attach(Gtk.Label(label=n,xalign=0),0,[0,2][i],1,1); e=Gtk.Entry(); e.set_text(v); e.set_hexpand(True); grid.attach(e,1,[0,2][i],1,1); s.fields[n]=e
  s.date_btn=Gtk.MenuButton(label=vals[4][1],halign=Gtk.Align.START); cal=Gtk.Calendar(); y,m,d=map(int,vals[4][1].split('-')); cal.select_day(GLib.DateTime.new_local(y,m,d,0,0,0)); cal.connect('day-selected',lambda c:(s.date_btn.set_label(c.get_date().format('%Y-%m-%d')),s.date_btn.popdown())); date_pop=Gtk.Popover(); date_pop.set_child(cal); s.date_btn.set_popover(date_pop); grid.attach(Gtk.Label(label='Fecha de solicitud:',xalign=0),0,8,1,1); grid.attach(s.date_btn,1,8,1,1)
  grid.attach(Gtk.Label(label='Notas:',xalign=0,valign=Gtk.Align.START),0,3,1,1); notes=Gtk.TextView(); notes.set_wrap_mode(Gtk.WrapMode.WORD_CHAR); notes.set_vexpand(True); notes.set_size_request(500,110); notes.get_buffer().set_text(vals[3][1]); notes_scroll=Gtk.ScrolledWindow(); notes_scroll.set_min_content_height(110); notes_scroll.set_hexpand(True); notes_scroll.set_child(notes); grid.attach(notes_scroll,1,3,1,1); s.fields['Notas:']=notes
  s.requester=Gtk.DropDown.new_from_strings(store.requesters() or ['Sin peticionario']); s.requester.set_selected(next((i for i,x in enumerate(store.requesters()) if row and x==row['requester']),0)); grid.attach(Gtk.Label(label='Peticionario:',xalign=0),0,1,1,1); grid.attach(s.requester,1,1,1,1)
  s.status=Gtk.DropDown.new_from_strings(STATUSES); s.status.set_selected(next((i for i,x in enumerate(STATUSES) if row and plain(x)==row['status']),0)); grid.attach(Gtk.Label(label='Estado:',xalign=0),0,4,1,1); grid.attach(s.status,1,4,1,1)
  s.typ=Gtk.DropDown.new_from_strings(TYPES); s.typ.set_selected(0 if not row or row['media_type']=='Película' else 1); grid.attach(Gtk.Label(label='Tipo:',xalign=0),0,5,1,1); grid.attach(s.typ,1,5,1,1)
  s.method=Gtk.DropDown.new_from_strings(METHODS); s.method.set_selected(next((i for i,x in enumerate(METHODS) if plain(x)==(row['download_method'] if row else '')),0)); grid.attach(Gtk.Label(label='Método de descarga:',xalign=0),0,6,1,1); grid.attach(s.method,1,6,1,1)
  s.priority=Gtk.DropDown.new_from_strings(PRIORITIES); s.priority.set_selected(next((i for i,x in enumerate(PRIORITIES) if row and plain(x)==row['priority']),1)); grid.attach(Gtk.Label(label='Prioridad:',xalign=0),0,7,1,1); grid.attach(s.priority,1,7,1,1)
  cancel=Gtk.Button(label='Cancelar'); save=Gtk.Button(label='Guardar'); actions=Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,spacing=8); actions.set_halign(Gtk.Align.END); actions.set_margin_start(16); actions.set_margin_end(16); actions.set_margin_bottom(16); actions.append(cancel)
  if row and row['download_url']:
   open_link=Gtk.Button(label='Abrir enlace'); open_link.connect('clicked',lambda *_: Gio.AppInfo.launch_default_for_uri(row['download_url'],None)); actions.append(open_link)
  if row:
   remove=Gtk.Button(label='Eliminar'); actions.append(remove)
   def confirm_delete(*_):
    confirm=Gtk.MessageDialog(transient_for=s,text=f'¿Eliminar la petición «{row["title"]}»?',buttons=Gtk.ButtonsType.YES_NO); confirm.connect('response',lambda dialog,response:(s.store.delete(row['id']),dialog.close(),s.close()) if response==Gtk.ResponseType.YES else dialog.close()); confirm.present()
   remove.connect('clicked',confirm_delete)
  actions.append(save); outer.append(actions); cancel.connect('clicked',lambda *_:s.close()); save.connect('clicked',lambda *_:s.response(None,Gtk.ResponseType.OK)); s.present()
  if row and row['poster_path'] and Path(row['poster_path']).exists(): s.poster.set_from_file(row['poster_path'])
 def response(s,_,response):
  if response==Gtk.ResponseType.OK:
   try: s.data=tmdb(s.fields['URL TMDB:'].get_text()); s.data.update(requester='' if not s.store.requesters() else s.requester.get_selected_item().get_string(),download_url=s.fields['Enlace de descarga:'].get_text(),notes=s.fields['Notas:'].get_buffer().get_text(s.fields['Notas:'].get_buffer().get_start_iter(),s.fields['Notas:'].get_buffer().get_end_iter(),False),status=plain(s.status.get_selected_item().get_string()),media_type=plain(s.typ.get_selected_item().get_string()),download_method=plain(s.method.get_selected_item().get_string()),priority=plain(s.priority.get_selected_item().get_string()),request_date=s.date_btn.get_label()); s.store.save(s.data,s.row['id'] if s.row else None)
   except Exception as e: s.error=Gtk.MessageDialog(transient_for=s,text=str(e),buttons=Gtk.ButtonsType.OK); s.error.connect('response',lambda dialog,_:dialog.close()); s.error.present(); return
  s.close()
class App(Gtk.Application):
 def __init__(s): super().__init__(application_id='es.joseflix.Request'); s.store=Store()
 def menu_popover(s,button,items):
  pop=Gtk.Popover(); box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=2); box.set_margin_start(6); box.set_margin_end(6); box.set_margin_top(6); box.set_margin_bottom(6)
  for label,icon,callback in items:
   b=Gtk.Button(); content=Gtk.Box(spacing=8); content.append(Gtk.Image.new_from_icon_name(icon)); content.append(Gtk.Label(label=label,xalign=0)); b.set_child(content); b.set_halign(Gtk.Align.FILL); b.connect('clicked',lambda _,fn=callback:(pop.popdown(),fn())); box.append(b)
  pop.set_child(box); button.set_popover(pop)
 def do_activate(s):
  css=Gtk.CssProvider(); css.load_from_string('label.priority-alta{color:#e01b24;} label.priority-normal{color:#e5a50a;} label.priority-baja{color:#26a269;}'); Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(),css,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
  s.win=Gtk.ApplicationWindow(application=s,title='Joseflix — Peticiones',default_width=1100,default_height=700); root=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=8); root.set_margin_start(12); root.set_margin_end(12); root.set_margin_top(8); root.set_margin_bottom(8); s.win.set_child(root); menubar=Gtk.Box(spacing=8); ajustes=Gtk.MenuButton(); ver=Gtk.MenuButton(); ayuda=Gtk.MenuButton(); [(b.set_child(c),menubar.append(b)) for b,c in [(ajustes,Gtk.Box(spacing=6)),(ver,Gtk.Box(spacing=6)),(ayuda,Gtk.Box(spacing=6))]]; ajustes.get_child().append(Gtk.Image.new_from_icon_name('preferences-system')); ajustes.get_child().append(Gtk.Label(label='Ajustes')); ver.get_child().append(Gtk.Image.new_from_icon_name('preferences-desktop-theme')); ver.get_child().append(Gtk.Label(label='Tema')); ayuda.get_child().append(Gtk.Image.new_from_icon_name('help-browser')); ayuda.get_child().append(Gtk.Label(label='Ayuda')); s.menu_popover(ajustes,[('Configurar TMDB…','system-lock-screen',s.settings),('Gestionar peticionarios…','system-users',s.requesters),('Copia de seguridad ahora','document-save',s.backup_now),('Restaurar copia de seguridad…','document-revert',s.restore_backup)]); s.menu_popover(ver,[('Modo claro','weather-clear',lambda:s.theme(False)),('Modo oscuro','weather-clear-night',lambda:s.theme(True))]); s.menu_popover(ayuda,[('Acerca de','help-about',s.about)]); root.append(menubar)
  bar=Gtk.Box(spacing=8); root.append(bar); s.search=Gtk.SearchEntry(placeholder_text='Buscar título'); s.status=Gtk.DropDown.new_from_strings(['Todos']+STATUSES); s.typ=Gtk.DropDown.new_from_strings(['Todos']+TYPES); s.req=Gtk.DropDown.new_from_strings(['Todos']+s.store.requesters()); s.priority=Gtk.DropDown.new_from_strings(['Todos']+PRIORITIES); s.date=Gtk.SearchEntry(placeholder_text='AAAA-MM-DD'); add=Gtk.Button(label='Nueva petición'); add.connect('clicked',lambda *_:s.new()); bar.append(s.search); bar.append(Gtk.Label(label='Estado:')); bar.append(s.status); bar.append(Gtk.Label(label='Tipo:')); bar.append(s.typ); bar.append(Gtk.Label(label='Peticionario:')); bar.append(s.req); bar.append(Gtk.Label(label='Prioridad:')); bar.append(s.priority); bar.append(Gtk.Label(label='Fecha:')); bar.append(s.date); bar.append(add); s.search.connect('search-changed',lambda *_:s.refresh()); s.date.connect('search-changed',lambda *_:s.refresh()); [x.connect('notify::selected-item',lambda *_:s.refresh()) for x in [s.status,s.typ,s.req,s.priority]]; s.list=Gtk.ListBox(); s.list.set_activate_on_single_click(False); s.list.connect('row-activated',lambda _,row:s.open(row.data)); scroll=Gtk.ScrolledWindow(); scroll.set_policy(Gtk.PolicyType.AUTOMATIC,Gtk.PolicyType.AUTOMATIC); scroll.set_vexpand(True); scroll.set_child(s.list); root.append(scroll); s.refresh(); s.add_actions()
  s.win.set_default_size(1100,700); s.win.set_decorated(True); s.win.set_resizable(True)
  try:
   cfg=json.loads(CONFIG.read_text())
   if 'dark_theme' in cfg: s.theme(cfg['dark_theme'])
  except (FileNotFoundError, json.JSONDecodeError): pass
  s.win.present()
 def add_actions(s):
  for name,fn in [('settings',s.settings),('requesters',s.requesters),('about',s.about),('light',lambda:s.theme(False)),('dark',lambda:s.theme(True)),('backup',s.backup_now),('restore',s.restore_backup)]: a=Gio.SimpleAction.new(name,None); a.connect('activate',lambda _,__,f=fn:f()); s.add_action(a)
 def refresh(s):
  while (r:=s.list.get_row_at_index(0)): s.list.remove(r)
  for r in s.store.rows(s.search.get_text(),s.status.get_selected_item().get_string(),s.typ.get_selected_item().get_string(),s.req.get_selected_item().get_string(),s.priority.get_selected_item().get_string(),s.date.get_text()):
   row=Gtk.ListBoxRow(); row.data=r; box=Gtk.Box(spacing=12); box.set_margin_top(6); box.set_margin_bottom(6); box.set_margin_start(4); box.set_margin_end(4)
   image=Gtk.Image(); image.set_pixel_size(64); image.set_from_file(r['poster_path']) if r['poster_path'] and Path(r['poster_path']).exists() else None; box.append(image)
   method=next((x for x in METHODS if plain(x)==r['download_method']),r['download_method'] or 'Sin método'); status=next((x for x in STATUSES if plain(x)==r['status']),r['status']); media=next((x for x in TYPES if plain(x)==r['media_type']),r['media_type']); priority=next((x for x in PRIORITIES if plain(x)==r['priority']),'🟡 Normal')
   content=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=2,hexpand=True,valign=Gtk.Align.CENTER); box.append(content)
   title_line=Gtk.Box(spacing=6); content.append(title_line); title=Gtk.Label(xalign=0,ellipsize=Pango.EllipsizeMode.END); title.set_markup(f"<b>{GLib.markup_escape_text(r['title'])}</b>"); title_line.append(title)
   year=Gtk.Label(label=f"({r['year'] or '—'})",xalign=0); year.add_css_class('dim-label'); title_line.append(year)
   meta=Gtk.Label(label=f"{media}  ·  {r['requester'] or 'Sin peticionario'}  ·  {r['request_date'] or '—'}",xalign=0,ellipsize=Pango.EllipsizeMode.END); meta.add_css_class('dim-label'); content.append(meta)
   meth=Gtk.Label(label=method,xalign=0); meth.add_css_class('dim-label'); meth.add_css_class('caption'); content.append(meth)
   badges=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=4,halign=Gtk.Align.END,valign=Gtk.Align.CENTER); box.append(badges)
   prio=Gtk.Label(); prio.set_markup(f"<b>{plain(priority)}</b>"); prio.add_css_class({'Alta':'priority-alta','Normal':'priority-normal','Baja':'priority-baja'}.get(plain(priority),'dim-label')); badges.append(prio)
   stat=Gtk.Label(label=status); stat.add_css_class('dim-label'); stat.add_css_class('caption'); badges.append(stat)
   row.set_child(box); s.list.append(row)
 def new(s):
  d=Editor(s.win,s.store); d.connect('response',lambda *_:s.refresh()); d.present()
 def open(s,r):
  d=Editor(s.win,s.store,r); d.connect('response',lambda *_:s.refresh()); d.connect('close-request',lambda *_:s.refresh()); d.present()
 def settings(s):
  d=Gtk.Dialog(title='Ajustes de TMDB',transient_for=s.win,modal=True); box=d.get_content_area(); box.append(Gtk.Label(label='Token de acceso de lectura de TMDB')); e=Gtk.Entry(); e.set_text(get_token()); e.set_hexpand(True); box.append(e); d.add_button('Cancelar',Gtk.ResponseType.CANCEL); d.add_button('Guardar',Gtk.ResponseType.OK); d.connect('response',lambda x,r:(set_token(e.get_text().strip()),x.close()) if r==Gtk.ResponseType.OK else x.close()); d.present()
 def requesters(s):
  d=Gtk.Dialog(title='Gestionar peticionarios',transient_for=s.win,modal=True,default_width=360,default_height=650); box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=8); box.set_margin_start(16); box.set_margin_end(16); box.set_margin_top(16); box.set_margin_bottom(16); d.set_child(box); lst=Gtk.ListBox(); lst.set_vexpand(True); list_scroll=Gtk.ScrolledWindow(); list_scroll.set_policy(Gtk.PolicyType.NEVER,Gtk.PolicyType.AUTOMATIC); list_scroll.set_min_content_height(300); list_scroll.set_max_content_height(500); list_scroll.set_propagate_natural_height(False); list_scroll.set_child(lst); box.append(list_scroll); entry=Gtk.Entry(); entry.set_placeholder_text('Nuevo nombre'); box.append(entry); buttons=Gtk.Box(spacing=6); box.append(buttons)
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
 def backup_now(s):
  s.store.db.commit(); dest=make_backup(); msg=f'Copia de seguridad creada:\n{dest}' if dest else 'No hay base de datos que respaldar todavía.'; info=Gtk.MessageDialog(transient_for=s.win,text=msg,buttons=Gtk.ButtonsType.OK); info.connect('response',lambda dialog,_:dialog.close()); info.present()
 def restore_backup(s):
  backups=list_backups()
  if not backups:
   info=Gtk.MessageDialog(transient_for=s.win,text='No hay copias de seguridad disponibles.',buttons=Gtk.ButtonsType.OK); info.connect('response',lambda dialog,_:dialog.close()); info.present(); return
  d=Gtk.Dialog(title='Restaurar copia de seguridad',transient_for=s.win,modal=True,default_width=420,default_height=420); box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=8); box.set_margin_start(16); box.set_margin_end(16); box.set_margin_top(16); box.set_margin_bottom(16); d.set_child(box); box.append(Gtk.Label(label='Selecciona una copia de seguridad para restaurar:',xalign=0)); lst=Gtk.ListBox(); lst.set_vexpand(True); list_scroll=Gtk.ScrolledWindow(); list_scroll.set_policy(Gtk.PolicyType.NEVER,Gtk.PolicyType.AUTOMATIC); list_scroll.set_child(lst); box.append(list_scroll)
  for b in backups: lst.append(Gtk.Label(label=b.name,xalign=0))
  restore=Gtk.Button(label='Restaurar'); restore.set_halign(Gtk.Align.END); box.append(restore)
  def confirmed(dialog,response):
   dialog.close()
   if response!=Gtk.ResponseType.YES: return
   make_backup(); s.store.db.close(); shutil.copy2(backups[lst.get_selected_row().get_index()],DB); d.close(); done=Gtk.MessageDialog(transient_for=s.win,text='Copia restaurada correctamente. La aplicación se cerrará; vuelve a abrirla.',buttons=Gtk.ButtonsType.OK); done.connect('response',lambda *_:s.quit()); done.present()
  def do_restore(*_):
   selected=lst.get_selected_row()
   if not selected: return
   confirm=Gtk.MessageDialog(transient_for=d,text=f'¿Restaurar «{backups[selected.get_index()].name}»?\n\nSe sobrescribirán los datos actuales (se guarda antes una copia de seguridad del estado actual). La aplicación se cerrará para aplicar los cambios.',buttons=Gtk.ButtonsType.YES_NO); confirm.connect('response',confirmed); confirm.present()
  restore.connect('clicked',do_restore); d.present()
 def about(s):
  d=Gtk.Dialog(title='Acerca de Joseflix Request',transient_for=s.win,modal=True); box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=10); box.set_margin_start(28); box.set_margin_end(28); box.set_margin_top(24); box.set_margin_bottom(24); d.set_child(box); icon=Gtk.Image(); icon_path='/usr/share/icons/hicolor/scalable/apps/joseflix-request.svg'; icon.set_from_file(icon_path if Path(icon_path).exists() else str(Path(__file__).with_name('joseflix-request.svg'))); icon.set_pixel_size(96); box.append(icon); info=Gtk.Label(); info.set_markup(f'<big><b>Joseflix Request</b></big>\n\nVersión {APP_VERSION}\nGestor de peticiones para Joseflix\n\nDesarrollador:\nseguidodoblado\njose.antonio.seguido@gmail.com\n\nDependencia:\nPyGObject + GTK 4'); info.set_justify(Gtk.Justification.CENTER); box.append(info); close=Gtk.Button(label='Cerrar'); close.set_halign(Gtk.Align.CENTER); close.connect('clicked',lambda *_:d.close()); box.append(close); d.present()
 def theme(s,dark):
    settings=Gtk.Settings.get_default(); settings.set_property('gtk-theme-name','Adwaita-dark' if dark else 'Adwaita'); settings.set_property('gtk-application-prefer-dark-theme',dark)
    cfg = {}
    try: cfg = json.loads(CONFIG.read_text())
    except (FileNotFoundError, json.JSONDecodeError): pass
    cfg['dark_theme'] = dark
    CONFIG.write_text(json.dumps(cfg))
App().run()
