#!/usr/bin/env python3
import os, re, sqlite3, urllib.parse, urllib.request, json
from pathlib import Path
from PySide6.QtWidgets import QApplication,QMainWindow,QWidget,QVBoxLayout,QHBoxLayout,QLineEdit,QComboBox,QPushButton,QListWidget,QListWidgetItem,QDialog,QFormLayout,QDialogButtonBox,QMessageBox,QTextEdit,QLabel,QMenu,QInputDialog
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPalette, QColor, QIcon, QPixmap
from PySide6.QtCore import QSettings
APP=Path(os.environ.get('XDG_DATA_HOME',Path.home()/'.local/share'))/'joseflix-request'; APP.mkdir(parents=True,exist_ok=True); DB=APP/'joseflix.sqlite3'
APP_VERSION='0.1.0'; STATUS_LABELS=['📨 Solicitado','🔎 Buscando','📥 Descargado','📤 Subido','✅ Notificado']; STATUSES=['Solicitado','Buscando','Descargado','Subido','Notificado']; METHODS=['DD','Torrent','ED2K']
class Store:
 def __init__(s): s.d=sqlite3.connect(DB); s.d.row_factory=sqlite3.Row; s.d.execute('CREATE TABLE IF NOT EXISTS requests (id INTEGER PRIMARY KEY,tmdb_id INTEGER,media_type TEXT,title TEXT,year TEXT,overview TEXT,poster_path TEXT,tmdb_url TEXT,requester TEXT,status TEXT,download_method TEXT,download_url TEXT,notes TEXT)'); s.d.execute('CREATE TABLE IF NOT EXISTS requesters (name TEXT PRIMARY KEY)'); s.d.execute('INSERT OR IGNORE INTO requesters SELECT DISTINCT requester FROM requests WHERE requester IS NOT NULL AND requester != ""'); s.d.commit()
 def rows(s,t='',st='Todos',mt='Todos',rq='Todos'):
  q='SELECT * FROM requests WHERE title LIKE ?'; a=[f'%{t}%']
  for v,c in [(st,'status'),(mt,'media_type'),(rq,'requester')]:
   if v!='Todos': q+=f' AND {c}=?'; a.append(v)
  return s.d.execute(q+' ORDER BY id DESC',a).fetchall()
 def save(s,x,ident=None):
  if ident: s.d.execute('UPDATE requests SET '+','.join(f'{k}=?' for k in x)+' WHERE id=?',[*x.values(),ident])
  else: s.d.execute('INSERT INTO requests ('+','.join(x)+') VALUES ('+','.join('?' for _ in x)+')',list(x.values()))
  if x.get('requester'): s.d.execute('INSERT OR IGNORE INTO requesters(name) VALUES (?)',(x['requester'],))
  s.d.commit()
 def delete(s,ident): s.d.execute('DELETE FROM requests WHERE id=?',(ident,)); s.d.commit()
 def requesters(s): return [x[0] for x in s.d.execute('SELECT name FROM requesters ORDER BY name')]
 def rename_requester(s,old,new): s.d.execute('UPDATE requesters SET name=? WHERE name=?',(new,old)); s.d.execute('UPDATE requests SET requester=? WHERE requester=?',(new,old)); s.d.commit()
 def add_requester(s,name): s.d.execute('INSERT OR IGNORE INTO requesters(name) VALUES (?)',(name,)); s.d.commit()
 def delete_requester(s,name): s.d.execute('DELETE FROM requesters WHERE name=?',(name,)); s.d.execute('UPDATE requests SET requester="" WHERE requester=?',(name,)); s.d.commit()
def fetch(url):
 k=QSettings('Joseflix','Request').value('tmdb_token','') or os.environ.get('TMDB_API_KEY',''); p=urllib.parse.urlparse(url).path.strip('/').split('/')
 if not k: raise ValueError('Configura el token de TMDB desde Ajustes')
 if len(p)<2 or p[0] not in ('movie','tv'): raise ValueError('URL TMDB no válida')
 match=re.match(r'(\d+)',p[1])
 if not match: raise ValueError('La URL no contiene un identificador TMDB válido')
 req=urllib.request.Request(f'https://api.themoviedb.org/3/{p[0]}/{match.group(1)}?language=es-ES',headers={'Authorization':f'Bearer {k}','accept':'application/json'})
 with urllib.request.urlopen(req,timeout=15) as r: x=json.load(r)
 poster=x.get('poster_path') or ''; local=''
 if poster:
  local=str(APP/'posters'/f"{match.group(1)}.jpg"); Path(local).parent.mkdir(exist_ok=True)
  if not Path(local).exists():
   with urllib.request.urlopen('https://image.tmdb.org/t/p/w342'+poster,timeout=15) as r: Path(local).write_bytes(r.read())
 return {'tmdb_id':int(match.group(1)),'media_type':'Película' if p[0]=='movie' else 'Serie','title':x.get('title') or x.get('name',''),'year':(x.get('release_date') or x.get('first_air_date',''))[:4],'overview':x.get('overview',''),'poster_path':local,'tmdb_url':url}
class Editor(QDialog):
 def __init__(s,p,r=None):
  super().__init__(p); s.record=r; s.setWindowTitle('Editar petición' if r else 'Nueva petición'); s.resize(760,760); f=QFormLayout(s); title=QLabel(f"<h2>{r['title']} ({r['year'] or '—'})</h2>" if r else '<h2>Nueva petición</h2>'); title.setTextFormat(Qt.RichText); f.addRow(title); poster=QLabel(); poster.setAlignment(Qt.AlignCenter); poster.setMinimumHeight(220); poster.setMaximumHeight(300); poster.setPixmap(QPixmap(r['poster_path']).scaled(190,280,Qt.KeepAspectRatio,Qt.SmoothTransformation) if r and r['poster_path'] and Path(r['poster_path']).exists() else QPixmap()); overview=QLabel(r['overview'] if r else 'La sinopsis aparecerá después de consultar TMDB.'); overview.setWordWrap(True); overview.setAlignment(Qt.AlignTop|Qt.AlignLeft); overview.setMinimumWidth(430); preview=QHBoxLayout(); preview.addWidget(poster); preview.addWidget(overview,1); f.addRow(preview); s.url=QLineEdit(r['tmdb_url'] if r else ''); s.req=QLineEdit(r['requester'] if r else ''); s.st=QComboBox(); s.st.addItems(STATUS_LABELS); s.st.setCurrentText(next((x for x in STATUS_LABELS if r and x.endswith(r['status'])), '📨 Solicitado')); s.mt=QComboBox(); s.mt.addItems(['🎬 Película','📺 Serie']); s.mt.setCurrentText(('🎬 ' if not r or r['media_type']=='Película' else '📺 ')+(r['media_type'] if r else 'Película')); s.me=QComboBox(); s.me.addItems(METHODS); s.me.setCurrentText(r['download_method'] if r else 'DD'); s.link=QLineEdit(r['download_url'] if r else ''); s.notes=QTextEdit(r['notes'] if r else '')
  for n,w in [('URL TMDB:',s.url),('Peticionario:',s.req),('Estado:',s.st),('Tipo:',s.mt),('Método de descarga:',s.me),('Enlace de descarga:',s.link),('Notas:',s.notes)]: f.addRow(n,w)
  b=QDialogButtonBox(QDialogButtonBox.Save|QDialogButtonBox.Cancel); b.accepted.connect(s.accept); b.rejected.connect(s.reject); f.addRow(b)
 def data(s): x=fetch(s.url.text()); x.update(requester=s.req.text(),status=s.st.currentText().split(' ',1)[-1],media_type=s.mt.currentText().split(' ',1)[-1],download_method=s.me.currentText(),download_url=s.link.text(),notes=s.notes.toPlainText()); return x
class SettingsDialog(QDialog):
 def __init__(s,p):
  super().__init__(p); s.setWindowTitle('Ajustes'); f=QFormLayout(s); s.token=QTextEdit(); s.token.setPlainText(QSettings('Joseflix','Request').value('tmdb_token','') or ''); s.token.setPlaceholderText('Token de acceso de lectura de TMDB'); s.token.setMinimumWidth(520); s.token.setMinimumHeight(90); f.addRow('Token TMDB',s.token); b=QDialogButtonBox(QDialogButtonBox.Save|QDialogButtonBox.Cancel); b.accepted.connect(s.save); b.rejected.connect(s.reject); f.addRow(b)
 def save(s): QSettings('Joseflix','Request').setValue('tmdb_token',s.token.toPlainText().strip()); s.accept()
class Window(QMainWindow):
 def __init__(s):
  super().__init__(); s.setWindowTitle('Joseflix — Peticiones'); s.resize(1050,700); s.db=Store(); menu=s.menuBar().addMenu('Ajustes'); menu.addAction('Configurar TMDB…',s.settings); menu.addAction('Gestionar peticionarios…',s.manage_requesters); view=s.menuBar().addMenu('Ver'); view.addAction('Modo claro',lambda:s.theme(False)); view.addAction('Modo oscuro',lambda:s.theme(True)); help_menu=s.menuBar().addMenu('Ayuda'); help_menu.addAction('Acerca de',s.about); w=QWidget(); s.setCentralWidget(w); l=QVBoxLayout(w); bar=QHBoxLayout(); l.addLayout(bar); s.search=QLineEdit(); s.search.setPlaceholderText('Buscar título'); s.st=s.combo(['Todos']+STATUS_LABELS); s.mt=s.combo(['Todos','🎬 Película','📺 Serie']); s.rq=s.combo(['Todos']); add=QPushButton('Nueva petición'); add.clicked.connect(s.new); bar.addWidget(s.search); bar.addWidget(QLabel('Estado:')); bar.addWidget(s.st); bar.addWidget(QLabel('Tipo:')); bar.addWidget(s.mt); bar.addWidget(QLabel('Peticionario:')); bar.addWidget(s.rq); bar.addWidget(add); s.search.textChanged.connect(s.refresh); [x.currentTextChanged.connect(s.refresh) for x in [s.st,s.mt,s.rq]]; s.list=QListWidget(); s.list.itemDoubleClicked.connect(s.open_record); l.addWidget(s.list); s.refresh(); s.theme(QSettings('Joseflix','Request').value('dark_mode',False,type=bool))
 def combo(s,x): c=QComboBox(); c.addItems(x); return c
 def refresh(s):
  s.list.clear(); old=s.rq.currentText(); s.rq.blockSignals(True); s.rq.clear(); s.rq.addItem('Todos'); s.rq.addItems(s.db.requesters()); s.rq.setCurrentText(old if old in [s.rq.itemText(i) for i in range(s.rq.count())] else 'Todos'); s.rq.blockSignals(False)
  s.list.setIconSize(QPixmap(110,150).size()); st=s.st.currentText().split(' ',1)[-1]; mt=s.mt.currentText().split(' ',1)[-1]
  for r in s.db.rows(s.search.text(),st,mt,s.rq.currentText()):
   status=next((x for x in STATUS_LABELS if x.endswith(r['status'])),r['status']); media=('🎬 ' if r['media_type']=='Película' else '📺 ')+r['media_type']; i=QListWidgetItem(f"{r['title']} ({r['year'] or '—'})  ·  {media}  ·  {r['requester']}  ·  {status}"); i.setData(Qt.UserRole,dict(r));
   if r['poster_path'] and Path(r['poster_path']).exists(): i.setIcon(QIcon(r['poster_path']))
   s.list.addItem(i)
 def new(s):
  d=Editor(s)
  if d.exec()==QDialog.Accepted:
   try: s.db.save(d.data()); s.refresh()
   except Exception as e: QMessageBox.critical(s,'No se pudo guardar',str(e))
 def open_record(s,item):
  r=item.data(Qt.UserRole); d=Editor(s,r)
  save=d.findChild(QDialogButtonBox); save.accepted.disconnect(); save.accepted.connect(d.accept)
  delete=QPushButton('Eliminar'); save.addButton(delete,QDialogButtonBox.DestructiveRole)
  delete.clicked.connect(lambda: (s.db.delete(r['id']),d.reject(),s.refresh()))
  if d.exec()==QDialog.Accepted:
   try: s.db.save(d.data(),r['id']); s.refresh()
   except Exception as e: QMessageBox.critical(s,'No se pudo guardar',str(e))
 def manage_requesters(s):
  d=QDialog(s); d.setWindowTitle('Gestionar peticionarios'); d.resize(360,300); l=QVBoxLayout(d); lst=QListWidget(); l.addWidget(lst); buttons=QHBoxLayout(); l.addLayout(buttons)
  def load(): lst.clear(); lst.addItems(s.db.requesters())
  def add():
   n,ok=QInputDialog.getText(d,'Nuevo peticionario','Nombre:')
   if ok and n.strip(): s.db.add_requester(n.strip()); load(); s.refresh()
  def edit():
   if not lst.currentItem(): return
   old=lst.currentItem().text(); n,ok=QInputDialog.getText(d,'Editar peticionario','Nombre:',text=old)
   if ok and n.strip(): s.db.rename_requester(old,n.strip()); load(); s.refresh()
  def remove():
   if lst.currentItem() and QMessageBox.question(d,'Borrar peticionario','También se quitará de sus peticiones.')==QMessageBox.Yes: s.db.delete_requester(lst.currentItem().text()); load(); s.refresh()
  for label,fn in [('Crear',add),('Editar',edit),('Borrar',remove)]: b=QPushButton(label); b.clicked.connect(fn); buttons.addWidget(b)
  load(); d.exec()
 def settings(s): SettingsDialog(s).exec()
 def theme(s,dark):
  p=QPalette()
  if dark:
   p.setColor(QPalette.Window,QColor('#202124')); p.setColor(QPalette.WindowText,Qt.white); p.setColor(QPalette.Base,QColor('#303134')); p.setColor(QPalette.Text,Qt.white); p.setColor(QPalette.Button,QColor('#3c4043')); p.setColor(QPalette.ButtonText,Qt.white)
  QApplication.instance().setPalette(p); font=QFont('Ubuntu Sans',13); font.setFamilies(['Ubuntu Sans','Noto Color Emoji','Noto Emoji','DejaVu Sans']); QApplication.instance().setFont(font); s.list.setStyleSheet('QListWidget { font-family: "Ubuntu Sans", "Noto Color Emoji", "Noto Emoji"; font-size: 13pt; }'); s.st.setStyleSheet('QComboBox { font-family: "Ubuntu Sans", "Noto Color Emoji", "Noto Emoji"; font-size: 13pt; }'); s.mt.setStyleSheet('QComboBox { font-family: "Ubuntu Sans", "Noto Color Emoji", "Noto Emoji"; font-size: 13pt; }'); QSettings('Joseflix','Request').setValue('dark_mode',dark)
 def about(s):
  d=QDialog(s); d.setWindowTitle('Acerca de Joseflix Request'); l=QVBoxLayout(d); icon=QLabel(); icon.setAlignment(Qt.AlignCenter); icon.setPixmap(QPixmap('/usr/share/icons/hicolor/scalable/apps/joseflix-request.svg').scaled(96,96,Qt.KeepAspectRatio,Qt.SmoothTransformation)); l.addWidget(icon); text=QLabel(f'<h2>Joseflix Request</h2><p>Versión {APP_VERSION}</p><p>Gestor de peticiones de películas y series.</p><p><b>Desarrollador:</b><br>seguidodoblado<br>jose.antonio.seguido@gmail.com</p><p><b>Dependencia:</b><br>PySide6</p>'); text.setAlignment(Qt.AlignCenter); l.addWidget(text); b=QDialogButtonBox(QDialogButtonBox.Close); b.rejected.connect(d.reject); b.accepted.connect(d.accept); l.addWidget(b); d.exec()
app=QApplication([]); w=Window(); w.show(); app.exec()
