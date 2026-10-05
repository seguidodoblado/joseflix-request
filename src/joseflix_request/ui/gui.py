"""Interfaz GTK 4: lista de peticiones, ficha de edición y diálogos."""
import subprocess
from datetime import datetime
from pathlib import Path

import gi

gi.require_version("Gdk", "4.0")
gi.require_version("Gtk", "4.0")
from gi.repository import Gdk, Gio, GLib, Gtk, Pango

from .. import __version__, config, tmdb
from ..i18n import _, ngettext
from ..models import METHODS, PRIORITIES, STATUSES, TYPES
from ..models import label as display
from ..models import name as name_of
from ..store import Store
from .theming import icon_choice, is_dark_theme, theme_variant

AUTHOR = "Jose Antonio Seguido Doblado"
AUTHOR_EMAIL = "jose.antonio.seguido@gmail.com"
REPO_URL = "https://github.com/seguidodoblado/joseflix-request"
APPLICATION_ID = "io.github.seguidodoblado.JoseflixRequest"
LANGUAGE_CODES = [None, "es", "en"]
LOGO = Path(__file__).resolve().parents[3] / "joseflix-request.svg"   # solo al ejecutar desde el repositorio


class Editor(Gtk.Dialog):
 def __init__(s,parent,store,row=None):
  super().__init__(title=_('Editar petición') if row else _('Nueva petición'),transient_for=parent,modal=True,default_width=900,default_height=850); s.store=store; s.row=row; outer=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=8); box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=8); box.set_margin_start(16); box.set_margin_end(16); box.set_margin_top(16); box.set_margin_bottom(16); scroll=Gtk.ScrolledWindow(); scroll.set_policy(Gtk.PolicyType.NEVER,Gtk.PolicyType.AUTOMATIC); scroll.set_vexpand(True); scroll.set_child(box); outer.append(scroll); s.set_child(outer)
  s.heading=Gtk.Label(); s.heading.set_markup(f'<big><b>{row["title"]} ({row["year"] or "—"})</b></big>' if row else '<big><b>'+_('Nueva petición')+'</b></big>'); box.append(s.heading); s.preview=Gtk.Box(spacing=16); box.append(s.preview); s.poster=Gtk.Image(); s.poster.set_pixel_size(260); s.preview.append(s.poster); s.overview=Gtk.Label(label=row['overview'] if row else _('La sinopsis aparecerá al consultar TMDB.')); s.overview.set_wrap(True); s.overview.set_justify(Gtk.Justification.FILL); s.overview.set_hexpand(True); s.overview.set_valign(Gtk.Align.START); s.preview.append(s.overview)
  grid=Gtk.Grid(column_spacing=10,row_spacing=8); box.append(grid); s.fields={}; vals=[('tmdb',row['tmdb_url'] if row else ''),('requester',row['requester'] if row else ''),('download',row['download_url'] if row else ''),('notes',row['notes'] if row else ''),('date',(row['request_date'] if row else None) or datetime.now().astimezone().strftime('%Y-%m-%d'))]
  captions={'tmdb':_('URL TMDB:'),'download':_('Enlace de descarga:')}
  for i,(n,v) in enumerate([vals[0],vals[2]]): grid.attach(Gtk.Label(label=captions[n],xalign=0),0,[0,2][i],1,1); e=Gtk.Entry(); e.set_text(v); e.set_hexpand(True); grid.attach(e,1,[0,2][i],1,1); s.fields[n]=e
  s.date_btn=Gtk.MenuButton(label=vals[4][1],halign=Gtk.Align.START); cal=Gtk.Calendar(); y,m,d=map(int,vals[4][1].split('-')); cal.select_day(GLib.DateTime.new_local(y,m,d,0,0,0)); cal.connect('day-selected',lambda c:(s.date_btn.set_label(c.get_date().format('%Y-%m-%d')),s.date_btn.popdown())); date_pop=Gtk.Popover(); date_pop.set_child(cal); s.date_btn.set_popover(date_pop); grid.attach(Gtk.Label(label=_('Fecha de solicitud:'),xalign=0),0,8,1,1); grid.attach(s.date_btn,1,8,1,1)
  grid.attach(Gtk.Label(label=_('Notas:'),xalign=0,valign=Gtk.Align.START),0,3,1,1); notes=Gtk.TextView(); notes.set_wrap_mode(Gtk.WrapMode.WORD_CHAR); notes.set_vexpand(True); notes.set_size_request(500,110); notes.get_buffer().set_text(vals[3][1]); notes_scroll=Gtk.ScrolledWindow(); notes_scroll.set_min_content_height(110); notes_scroll.set_hexpand(True); notes_scroll.set_child(notes); grid.attach(notes_scroll,1,3,1,1); s.fields['notes']=notes
  s.requester=Gtk.DropDown.new_from_strings(store.requesters() or [_('Sin peticionario')]); s.requester.set_selected(next((i for i,x in enumerate(store.requesters()) if row and x==row['requester']),0)); grid.attach(Gtk.Label(label=_('Peticionario:'),xalign=0),0,1,1,1); grid.attach(s.requester,1,1,1,1)
  s.status=Gtk.DropDown.new_from_strings([display(k) for k in STATUSES]); s.status.set_selected(next((i for i,k in enumerate(STATUSES) if row and k==row['status']),0)); grid.attach(Gtk.Label(label=_('Estado:'),xalign=0),0,4,1,1); grid.attach(s.status,1,4,1,1)
  s.typ=Gtk.DropDown.new_from_strings([display(k) for k in TYPES]); s.typ.set_selected(0 if not row or row['media_type']=='Película' else 1); grid.attach(Gtk.Label(label=_('Tipo:'),xalign=0),0,5,1,1); grid.attach(s.typ,1,5,1,1)
  s.method=Gtk.DropDown.new_from_strings([display(k) for k in METHODS]); s.method.set_selected(next((i for i,k in enumerate(METHODS) if k==(row['download_method'] if row else '')),0)); grid.attach(Gtk.Label(label=_('Método de descarga:'),xalign=0),0,6,1,1); grid.attach(s.method,1,6,1,1)
  s.priority=Gtk.DropDown.new_from_strings([display(k) for k in PRIORITIES]); s.priority.set_selected(next((i for i,k in enumerate(PRIORITIES) if row and k==row['priority']),1)); grid.attach(Gtk.Label(label=_('Prioridad:'),xalign=0),0,7,1,1); grid.attach(s.priority,1,7,1,1)
  cancel=Gtk.Button(label=_('Cancelar')); save=Gtk.Button(label=_('Guardar')); save.add_css_class('save-action'); actions=Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,spacing=8); actions.set_halign(Gtk.Align.END); actions.set_margin_start(16); actions.set_margin_end(16); actions.set_margin_bottom(16); actions.append(cancel)
  if row and row['download_url']:
   open_link=Gtk.Button(label=_('Abrir enlace')); open_link.connect('clicked',lambda *_args: Gio.AppInfo.launch_default_for_uri(row['download_url'],None)); actions.append(open_link)
  if row:
   remove=Gtk.Button(label=_('Eliminar')); remove.add_css_class('destructive-action'); actions.append(remove)
   def confirm_delete(*_args):
    confirm=Gtk.MessageDialog(transient_for=s,text=_('¿Eliminar la petición «{title}»?').format(title=row["title"]),buttons=Gtk.ButtonsType.NONE); confirm.add_button(_('Cancelar'),Gtk.ResponseType.CANCEL); confirm.add_button(_('Aceptar'),Gtk.ResponseType.OK); confirm.get_widget_for_response(Gtk.ResponseType.OK).add_css_class('destructive-action'); confirm.connect('response',lambda dialog,response:(s.store.delete(row['id']),dialog.close(),s.close()) if response==Gtk.ResponseType.OK else dialog.close()); confirm.present()
   remove.connect('clicked',confirm_delete)
  actions.append(save); outer.append(actions); cancel.connect('clicked',lambda *_args:s.close()); save.connect('clicked',lambda *_args:s.response(None,Gtk.ResponseType.OK)); s.present()
  if row and row['poster_path'] and Path(row['poster_path']).exists(): s.poster.set_from_file(row['poster_path'])
 def response(s,_,response):
  if response==Gtk.ResponseType.OK:
   try: s.data=tmdb.lookup(s.fields['tmdb'].get_text()); s.data.update(requester='' if not s.store.requesters() else s.requester.get_selected_item().get_string(),download_url=s.fields['download'].get_text(),notes=s.fields['notes'].get_buffer().get_text(s.fields['notes'].get_buffer().get_start_iter(),s.fields['notes'].get_buffer().get_end_iter(),False),status=STATUSES[s.status.get_selected()],media_type=TYPES[s.typ.get_selected()],download_method=METHODS[s.method.get_selected()],priority=PRIORITIES[s.priority.get_selected()],request_date=s.date_btn.get_label()); s.store.save(s.data,s.row['id'] if s.row else None)
   except Exception as e:  # noqa: BLE001 - el motivo se muestra al usuario, no debe cerrar la app
    s.error=Gtk.MessageDialog(transient_for=s,text=str(e),buttons=Gtk.ButtonsType.OK); s.error.connect('response',lambda dialog,_r:dialog.close()); s.error.present(); return
  s.close()
class App(Gtk.Application):
 def __init__(s): super().__init__(application_id=APPLICATION_ID); s.store=Store()
 def icon(s,names):
  names=(names,) if isinstance(names,str) else names
  return Gtk.Image.new_from_icon_name(icon_choice(names,s.dark,Gtk.IconTheme.get_for_display(Gdk.Display.get_default()).has_icon))
 def menu_popover(s,button,items):
  pop=Gtk.Popover(); box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=2); box.set_margin_start(6); box.set_margin_end(6); box.set_margin_top(6); box.set_margin_bottom(6)
  for label,icon,callback in items:
   b=Gtk.Button(); content=Gtk.Box(spacing=8); content.append(s.icon(icon)); content.append(Gtk.Label(label=label,xalign=0)); b.set_child(content); b.set_halign(Gtk.Align.FILL); b.connect('clicked',lambda _b,fn=callback:(pop.popdown(),fn())); box.append(b)
  pop.set_child(box); button.set_popover(pop)
 def view_menu(s,button):
  pop=Gtk.Popover(); box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=6); box.set_margin_start(10); box.set_margin_end(10); box.set_margin_top(8); box.set_margin_bottom(8)
  for label,icon,callback in [(_('Modo del sistema'),'preferences-desktop-theme',lambda:s.theme(None)),(_('Modo claro'),'weather-clear',lambda:s.theme(False)),(_('Modo oscuro'),'weather-clear-night',lambda:s.theme(True))]:
   b=Gtk.Button(); content=Gtk.Box(spacing=8); content.append(s.icon(icon)); content.append(Gtk.Label(label=label,xalign=0)); b.set_child(content); b.set_halign(Gtk.Align.FILL); b.connect('clicked',lambda _b,fn=callback:(pop.popdown(),fn())); box.append(b)
  box.append(Gtk.Separator()); box.append(Gtk.Label(label=_('Tamaño de póster'),xalign=0))
  scale=Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL,adjustment=Gtk.Adjustment(value=s.poster_size,lower=64,upper=240,step_increment=8,page_increment=16)); scale.set_digits(0); scale.set_draw_value(True); scale.set_size_request(140,-1); scale.set_hexpand(False)
  for v in (64,96,120,160,200,240): scale.add_mark(v,Gtk.PositionType.BOTTOM,None)
  scale.connect('value-changed',lambda sc:s.set_poster_size(int(sc.get_value()))); box.append(scale)
  pop.set_child(box); button.set_popover(pop)
 def do_activate(s):
  if s.get_windows(): s.get_windows()[0].present(); return
  s.system_theme=Gtk.Settings.get_default().get_property('gtk-theme-name'); s.poster_refresh_src=None
  saved=config.dark_mode()
  s.dark=saved if saved is not None else is_dark_theme(s.system_theme)
  if saved is not None: Gtk.Settings.get_default().set_property('gtk-theme-name',theme_variant(s.system_theme,saved))   # antes de presentar la ventana: en caliente Cinnamon no repinta
  css=Gtk.CssProvider(); css.load_from_string('label.priority-alta{color:#e01b24;} label.priority-normal{color:#e5a50a;} label.priority-baja{color:#26a269;} button.save-action{background-image:none;background-color:#26a269;color:#fff;} row.status-notificado:not(:selected){background-color:rgba(38,162,105,0.18);} row.status-buscando:not(:selected){background-color:rgba(224,27,36,0.18);} button.new-action{background-image:none;background-color:#3584e4;color:#fff;}'); Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(),css,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
  s.poster_size=config.poster_size(); s.sort_desc=config.sort_desc()
  s.win=Gtk.ApplicationWindow(application=s,title=_('Joseflix — Peticiones'),default_width=1100,default_height=700); root=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=8); root.set_margin_start(12); root.set_margin_end(12); root.set_margin_top(8); root.set_margin_bottom(8); s.win.set_child(root); menubar=Gtk.Box(spacing=8); ajustes=Gtk.MenuButton(); ver=Gtk.MenuButton(); ayuda=Gtk.MenuButton(); [(b.set_child(c),menubar.append(b)) for b,c in [(ajustes,Gtk.Box(spacing=6)),(ver,Gtk.Box(spacing=6)),(ayuda,Gtk.Box(spacing=6))]]; ajustes.get_child().append(s.icon('preferences-system')); ajustes.get_child().append(Gtk.Label(label=_('Ajustes'))); ver.get_child().append(s.icon('preferences-desktop-theme')); ver.get_child().append(Gtk.Label(label=_('Tema'))); ayuda.get_child().append(s.icon('help-browser')); ayuda.get_child().append(Gtk.Label(label=_('Ayuda'))); s.menu_popover(ajustes,[(_('Configurar TMDB…'),'system-lock-screen',s.settings),(_('Idioma…'),('preferences-desktop-locale','preferences-desktop-language'),s.choose_language),(_('Gestionar peticionarios…'),'system-users',s.requesters),(_('Copia de seguridad ahora'),'document-save',s.backup_now),(_('Restaurar copia de seguridad…'),'document-revert',s.restore_backup)]); s.view_menu(ver); s.menu_popover(ayuda,[(_('Acerca de'),'help-about',s.about)]); spacer=Gtk.Box(hexpand=True); menubar.append(spacer); clear_btn=Gtk.Button(label=_('Limpiar notificados')); clear_btn.add_css_class('save-action'); clear_btn.connect('clicked',lambda *_args:s.clear_notified()); menubar.append(clear_btn); root.append(menubar)
  bar=Gtk.Box(spacing=8); root.append(bar); s.search=Gtk.SearchEntry(placeholder_text=_('Buscar título')); s.status=Gtk.DropDown.new_from_strings([_('Todos')]+[display(k) for k in STATUSES]); s.typ=Gtk.DropDown.new_from_strings([_('Todos')]+[display(k) for k in TYPES]); s.req=Gtk.DropDown.new_from_strings([_('Todos')]+s.store.requesters()); s.priority=Gtk.DropDown.new_from_strings([_('Todos')]+[display(k) for k in PRIORITIES]); s.date=Gtk.SearchEntry(placeholder_text=_('AAAA-MM-DD')); add=Gtk.Button(label=_('Nueva petición')); add.add_css_class('new-action'); add.connect('clicked',lambda *_args:s.new()); bar.append(s.search); bar.append(Gtk.Label(label=_('Estado:'))); bar.append(s.status); bar.append(Gtk.Label(label=_('Tipo:'))); bar.append(s.typ); bar.append(Gtk.Label(label=_('Peticionario:'))); bar.append(s.req); bar.append(Gtk.Label(label=_('Prioridad:'))); bar.append(s.priority); bar.append(Gtk.Label(label=_('Fecha:'))); bar.append(s.date); s.sort_btn=Gtk.Button(); s.sort_btn.connect('clicked',lambda *_args:s.toggle_sort()); bar.append(s.sort_btn); s.update_sort_icon(); bar.append(add); s.search.connect('search-changed',lambda *_args:s.refresh()); s.date.connect('search-changed',lambda *_args:s.refresh()); [x.connect('notify::selected-item',lambda *_args:s.refresh()) for x in [s.status,s.typ,s.req,s.priority]]; s.list=Gtk.ListBox(); s.list.set_activate_on_single_click(False); s.list.connect('row-activated',lambda _l,row:s.open(row.data)); scroll=Gtk.ScrolledWindow(); scroll.set_policy(Gtk.PolicyType.AUTOMATIC,Gtk.PolicyType.AUTOMATIC); scroll.set_vexpand(True); scroll.set_child(s.list); root.append(scroll); s.count_label=Gtk.Label(xalign=1,halign=Gtk.Align.END); s.count_label.add_css_class('dim-label'); s.count_label.set_margin_top(2); root.append(s.count_label); s.refresh(); s.add_actions()
  s.win.set_default_size(1100,700); s.win.set_decorated(True); s.win.set_resizable(True)
  s.win.present(); s.presented=True
 def add_actions(s):
  for name,fn in [('settings',s.settings),('requesters',s.requesters),('about',s.about),('light',lambda:s.theme(False)),('dark',lambda:s.theme(True)),('backup',s.backup_now),('restore',s.restore_backup)]: a=Gio.SimpleAction.new(name,None); a.connect('activate',lambda _a,_c,f=fn:f()); s.add_action(a)
 def refresh(s):
  while (r:=s.list.get_row_at_index(0)): s.list.remove(r)
  rows=s.store.rows(s.search.get_text(),pick(s.status,STATUSES),pick(s.typ,TYPES),None if s.req.get_selected()==0 else s.req.get_selected_item().get_string(),pick(s.priority,PRIORITIES),s.date.get_text(),s.sort_desc)
  for r in rows:
   row=Gtk.ListBoxRow(); row.data=r; row_cls={'Notificado':'status-notificado','Buscando':'status-buscando'}.get(r['status']); row.add_css_class(row_cls) if row_cls else None; box=Gtk.Box(spacing=12); box.set_margin_top(6); box.set_margin_bottom(6); box.set_margin_start(4); box.set_margin_end(4)
   image=Gtk.Image(); image.set_pixel_size(s.poster_size); image.set_from_file(r['poster_path']) if r['poster_path'] and Path(r['poster_path']).exists() else None; box.append(image)
   method=display(r['download_method']) if r['download_method'] in METHODS else (r['download_method'] or _('Sin método')); status=display(r['status']); media=display(r['media_type']); priority=r['priority'] if r['priority'] in PRIORITIES else 'Normal'; nobody=_('Sin peticionario')
   content=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=2,hexpand=True,valign=Gtk.Align.CENTER); box.append(content)
   title_line=Gtk.Box(spacing=6); content.append(title_line); title=Gtk.Label(xalign=0,ellipsize=Pango.EllipsizeMode.END); title.set_markup(f"<b>{GLib.markup_escape_text(r['title'])}</b>"); title_line.append(title)
   year=Gtk.Label(label=f"({r['year'] or '—'})",xalign=0); year.add_css_class('dim-label'); title_line.append(year)
   meta=Gtk.Label(label=f"{media}  ·  {r['requester'] or nobody}  ·  {r['request_date'] or '—'}",xalign=0,ellipsize=Pango.EllipsizeMode.END); meta.add_css_class('dim-label'); content.append(meta)
   meth=Gtk.Label(label=method,xalign=0); meth.add_css_class('dim-label'); meth.add_css_class('caption'); content.append(meth)
   badges=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=4,halign=Gtk.Align.END,valign=Gtk.Align.CENTER); box.append(badges)
   prio=Gtk.Label(); prio.set_markup(f"<b>{name_of(priority)}</b>"); prio.add_css_class({'Alta':'priority-alta','Normal':'priority-normal','Baja':'priority-baja'}.get(priority,'dim-label')); badges.append(prio)
   stat=Gtk.Label(label=status); stat.add_css_class('dim-label'); stat.add_css_class('caption'); badges.append(stat)
   row.set_child(box); s.list.append(row)
  s.count_label.set_text(ngettext('{count} petición','{count} peticiones',len(rows)).format(count=len(rows)))
 def new(s):
  d=Editor(s.win,s.store); d.connect('response',lambda *_args:s.refresh()); d.present()
 def open(s,r):
  d=Editor(s.win,s.store,r); d.connect('response',lambda *_args:s.refresh()); d.connect('close-request',lambda *_args:s.refresh()); d.present()
 def settings(s):
  d=Gtk.Dialog(title=_('Ajustes de TMDB'),transient_for=s.win,modal=True); box=d.get_content_area(); box.append(Gtk.Label(label=_('Token de acceso de lectura de TMDB'))); e=Gtk.Entry(); e.set_text(config.get_token()); e.set_hexpand(True); box.append(e); d.add_button(_('Cancelar'),Gtk.ResponseType.CANCEL); d.add_button(_('Guardar'),Gtk.ResponseType.OK); d.connect('response',lambda x,r:(config.set_token(e.get_text().strip()),x.close()) if r==Gtk.ResponseType.OK else x.close()); d.present()
 def requesters(s):
  d=Gtk.Dialog(title=_('Gestionar peticionarios'),transient_for=s.win,modal=True,default_width=360,default_height=650); box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=8); box.set_margin_start(16); box.set_margin_end(16); box.set_margin_top(16); box.set_margin_bottom(16); d.set_child(box); lst=Gtk.ListBox(); lst.set_vexpand(True); list_scroll=Gtk.ScrolledWindow(); list_scroll.set_policy(Gtk.PolicyType.NEVER,Gtk.PolicyType.AUTOMATIC); list_scroll.set_min_content_height(300); list_scroll.set_max_content_height(500); list_scroll.set_propagate_natural_height(False); list_scroll.set_child(lst); box.append(list_scroll); entry=Gtk.Entry(); entry.set_placeholder_text(_('Nuevo nombre')); box.append(entry); buttons=Gtk.Box(spacing=6); box.append(buttons)
  def load():
   while (r:=lst.get_row_at_index(0)): lst.remove(r)
   for n in s.store.requesters(): lst.append(Gtk.Label(label=n,xalign=0))
  add=Gtk.Button(label=_('Crear')); edit=Gtk.Button(label=_('Editar')); remove=Gtk.Button(label=_('Borrar')); buttons.append(add); buttons.append(edit); buttons.append(remove)
  def valid():
   name=entry.get_text().strip()
   if not name:
    warning=Gtk.MessageDialog(transient_for=d,text=_('El nombre del peticionario no puede estar vacío'),buttons=Gtk.ButtonsType.OK); warning.connect('response',lambda dialog,_r:dialog.close()); warning.present(); return None
   return name
  def create(*_args):
   if (name:=valid()): s.store.add_requester(name); entry.set_text(''); load(); s.refresh()
  def rename(*_args):
   selected=lst.get_selected_row()
   if selected and (name:=valid()): s.store.rename_requester(selected.get_child().get_text(),name); load(); lst.select_row(None); entry.set_text(''); s.refresh()
  def delete_requester(*_args):
   selected=lst.get_selected_row()
   if not selected: return
   name=selected.get_child().get_text(); confirm=Gtk.MessageDialog(transient_for=d,text=_('¿Eliminar el peticionario «{name}»?').format(name=name),buttons=Gtk.ButtonsType.YES_NO); confirm.connect('response',lambda dialog,response:(s.store.delete_requester(name),load(),s.refresh(),dialog.close()) if response==Gtk.ResponseType.YES else dialog.close()); confirm.present()
  lst.connect('row-selected',lambda _l,row: entry.set_text(row.get_child().get_text()) if row else entry.set_text('')); add.connect('clicked',create); edit.connect('clicked',rename); remove.connect('clicked',delete_requester); load(); d.present(); GLib.idle_add(lambda: (lst.select_row(None),entry.set_text(''),False)[-1])
 def backup_now(s):
  s.store.db.commit(); dest=config.make_backup(); msg=_('Copia de seguridad creada:\n{dest}').format(dest=dest) if dest else _('No hay base de datos que respaldar todavía.'); info=Gtk.MessageDialog(transient_for=s.win,text=msg,buttons=Gtk.ButtonsType.OK); info.connect('response',lambda dialog,_r:dialog.close()); info.present()
 def restore_backup(s):
  backups=config.list_backups()
  if not backups:
   info=Gtk.MessageDialog(transient_for=s.win,text=_('No hay copias de seguridad disponibles.'),buttons=Gtk.ButtonsType.OK); info.connect('response',lambda dialog,_r:dialog.close()); info.present(); return
  d=Gtk.Dialog(title=_('Restaurar copia de seguridad'),transient_for=s.win,modal=True,default_width=420,default_height=420); box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=8); box.set_margin_start(16); box.set_margin_end(16); box.set_margin_top(16); box.set_margin_bottom(16); d.set_child(box); box.append(Gtk.Label(label=_('Selecciona una copia de seguridad para restaurar:'),xalign=0)); lst=Gtk.ListBox(); lst.set_vexpand(True); list_scroll=Gtk.ScrolledWindow(); list_scroll.set_policy(Gtk.PolicyType.NEVER,Gtk.PolicyType.AUTOMATIC); list_scroll.set_child(lst); box.append(list_scroll)
  for b in backups: lst.append(Gtk.Label(label=b.name,xalign=0))
  restore=Gtk.Button(label=_('Restaurar')); restore.set_halign(Gtk.Align.END); box.append(restore)
  def confirmed(dialog,response):
   dialog.close()
   if response!=Gtk.ResponseType.YES: return
   s.store.db.close(); config.restore_backup(backups[lst.get_selected_row().get_index()]); d.close(); done=Gtk.MessageDialog(transient_for=s.win,text=_('Copia restaurada correctamente. La aplicación se cerrará; vuelve a abrirla.'),buttons=Gtk.ButtonsType.OK); done.connect('response',lambda *_args:s.quit()); done.present()
  def do_restore(*_args):
   selected=lst.get_selected_row()
   if not selected: return
   confirm=Gtk.MessageDialog(transient_for=d,text=_('¿Restaurar «{name}»?\n\nSe sobrescribirán los datos actuales (se guarda antes una copia de seguridad del estado actual). La aplicación se cerrará para aplicar los cambios.').format(name=backups[selected.get_index()].name),buttons=Gtk.ButtonsType.YES_NO); confirm.connect('response',confirmed); confirm.present()
  restore.connect('clicked',do_restore); d.present()
 def clear_notified(s):
  count=s.store.notified_count()
  if count==0:
   info=Gtk.MessageDialog(transient_for=s.win,text=_('No hay peticiones en estado Notificado.'),buttons=Gtk.ButtonsType.OK); info.connect('response',lambda dialog,_r:dialog.close()); info.present(); return
  confirm=Gtk.MessageDialog(transient_for=s.win,text=ngettext('¿Eliminar {count} petición notificada?','¿Eliminar {count} peticiones notificadas?',count).format(count=count),buttons=Gtk.ButtonsType.NONE)
  confirm.add_button(_('Cancelar'),Gtk.ResponseType.CANCEL); confirm.add_button(_('Aceptar'),Gtk.ResponseType.OK); confirm.get_widget_for_response(Gtk.ResponseType.OK).add_css_class('save-action')
  confirm.connect('response',lambda dialog,response:(s.store.clear_notified(),dialog.close(),s.refresh()) if response==Gtk.ResponseType.OK else dialog.close()); confirm.present()
 def about(s):
  d=Gtk.AboutDialog(transient_for=s.win,modal=True,program_name='Joseflix Request',version=__version__,authors=[f'{AUTHOR} <{AUTHOR_EMAIL}>'],copyright=f'© 2026 {AUTHOR}',comments=_('Gestor de peticiones para Joseflix (Plex): registra, prioriza y sigue las peticiones de películas y series.'),website=REPO_URL,website_label=REPO_URL.removeprefix('https://'),license_type=Gtk.License.GPL_3_0_ONLY,translator_credits=_('translator-credits'))
  if Gtk.IconTheme.get_for_display(Gdk.Display.get_default()).has_icon('joseflix-request'): d.set_logo_icon_name('joseflix-request')
  elif LOGO.exists(): d.set_logo(Gdk.Texture.new_from_filename(str(LOGO)))
  d.add_credit_section(_('Datos de terceros'),['The Movie Database (TMDB) https://www.themoviedb.org/',_('Este producto usa la API de TMDB pero no está avalado ni certificado por TMDB.')]); d.present()
 def restart(s):
  """Reinicia la aplicación con un proceso nuevo (el idioma y el tema se aplican al arrancar)."""
  s.store.db.commit()
  subprocess.Popen(['/proc/self/exe','-m','joseflix_request'],start_new_session=True)
  s.quit()
 def theme(s,dark):
  """Guarda el tema (True oscuro, False claro, None el del sistema) y reinicia: en Cinnamon/Mint no se repinta en caliente."""
  config.set_option('dark_theme',dark); s.restart()
 def choose_language(s):
  d=Gtk.Dialog(title=_('Idioma'),transient_for=s.win,modal=True,resizable=False); box=d.get_content_area(); box.set_margin_start(16); box.set_margin_end(16); box.set_margin_top(16); box.set_margin_bottom(16); box.set_spacing(12)
  box.append(Gtk.Label(label=_('Idioma'),xalign=0)); drop=Gtk.DropDown.new_from_strings([_('Sistema'),'Español','English']); drop.set_selected(LANGUAGE_CODES.index(config.language())); box.append(drop)
  hint=Gtk.Label(label=_('Los cambios se aplican reiniciando la aplicación.'),xalign=0,wrap=True); hint.add_css_class('dim-label'); box.append(hint)
  d.add_button(_('Cancelar'),Gtk.ResponseType.CANCEL); d.add_button(_('Aplicar y reiniciar'),Gtk.ResponseType.OK)
  d.connect('response',lambda x,r:(config.set_option('language',LANGUAGE_CODES[drop.get_selected()]),x.close(),s.restart()) if r==Gtk.ResponseType.OK else x.close()); d.present()
 def set_poster_size(s,px):
  s.poster_size=px; config.set_option('poster_size',px)
  if s.poster_refresh_src: GLib.source_remove(s.poster_refresh_src)
  def do_refresh():
   s.poster_refresh_src=None; s.refresh(); return False
  s.poster_refresh_src=GLib.timeout_add(150,do_refresh)
 def update_sort_icon(s):
  s.sort_btn.set_icon_name('view-sort-descending-symbolic' if s.sort_desc else 'view-sort-ascending-symbolic')
  s.sort_btn.set_tooltip_text(_('Más recientes primero') if s.sort_desc else _('Más antiguas primero'))
 def toggle_sort(s):
  s.sort_desc=not s.sort_desc; config.set_option('sort_desc',s.sort_desc); s.update_sort_icon(); s.refresh()

def pick(dropdown,keys):
  """La clave elegida en un filtro cuya primera opción es «Todos» (None: sin filtro)."""
  i=dropdown.get_selected()
  return keys[i-1] if 0<i<=len(keys) else None


def run_gui():
  App().run()

