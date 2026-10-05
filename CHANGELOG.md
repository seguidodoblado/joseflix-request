# Changelog

Todos los cambios relevantes de este proyecto se documentarán
en este archivo.

## [Unreleased]

### Añadido
- **Interfaz en español e inglés** (`gettext`): el español es el idioma fuente y el inglés está en `po/en.po`. Se elige en **Ajustes → Idioma…** (Sistema, Español o English; reinicia la aplicación). Con «Sistema» se usa el idioma del escritorio o `$LANGUAGE`. Los estados, tipos, métodos y prioridades se guardan en la base con su clave en español y solo cambia lo que se muestra
- **Tema Sistema / Claro / Oscuro**: el menú «Tema» gana «Modo del sistema», que sigue el tema del escritorio. «Claro» y «Oscuro» eligen el tema GTK hermano conservando el acento
- «Acerca de» con créditos de traducción, el correo del autor como enlace y la licencia GPL-3.0 o posterior predefinida de GTK
- Pruebas (45), `ruff` y empaquetado comprobado con `lintian`; integración continua (`ci.yml`) y despliegue (`cd.yml`: al subir una etiqueta `vX.Y.Z` ejecuta el CI y, solo si pasa, deja la release en borrador con el mismo `.deb` que construyó el CI)
- `README.en.md`, `PRIVACY`, `CONTRIBUTING`, `SECURITY`, `SUPPORT` y `CODE_OF_CONDUCT` en español e inglés, y este `CHANGELOG.md`

### Cambiado
- La licencia pasa a **GPL-3.0 o posterior** (antes, solo versión 3), como en el resto de proyectos: `debian/copyright` (GPL-3+), `pyproject.toml`, README y «Acerca de»
- El código pasa de un único fichero a un paquete `src/joseflix_request/`: la lógica (`config`, `store`, `tmdb`, `models`) separada de la interfaz, que queda en `ui/`
- Empaquetado conforme a Debian: la aplicación se instala en `/usr/share/joseflix-request` (antes en `/opt/joseflix-request`), con `copyright`, `changelog.Debian.gz`, páginas de manual en inglés y español y `md5sums`; el `.deb` pasa lintian sin errores. El lanzador pasa a `joseflix-request-launcher`. La versión sale de `debian/changelog` y `build-deb.sh` comprueba que coincida con `pyproject.toml` y `__init__.py`
- El identificador de la aplicación (`Gtk.Application`) pasa de `es.joseflix.Request` a `io.github.seguidodoblado.JoseflixRequest`, la forma que exige Flathub para proyectos alojados en GitHub; no cambia ningún dato guardado
- Los iconos del menú se eligen con la misma lógica que Comic Identify y Bloguero: simbólicos en el tema oscuro y de color en el claro
- Al cambiar el tema o el idioma, la aplicación se relanza con un proceso nuevo en lugar de `os.execvpe`
- Los filtros comparan por clave y no por el texto mostrado, para no depender del idioma
- `config.json`, donde se guarda el token de TMDB en claro, pasa a tener permisos 600 (solo lo lee su dueño) la próxima vez que se guarda un ajuste
- Las copias de seguridad llevan la hora con zona horaria local en el nombre; el formato no cambia

### Corregido
- `debian/changelog`: el campo `Maintainer` ya no usa un correo `localhost` y se arregla el formato de dos firmas antiguas

## [1.0.3-1] - 2026-10-03

### Cambiado
- «Acerca de» usa la ventana estándar de GNOME, como Telegraph Writer y Comic Identify

## [1.0.2-1] - 2026-09-26

### Cambiado
- El tema oscuro usa iconos simbólicos monocromos en los menús (el claro mantiene los de color)

## [1.0.1-1] - 2026-09-22

### Cambiado
- Rango de tamaño de póster más amplio (hasta 240 px) y reconstrucción de la lista con retardo al arrastrar el control deslizante

### Corregido
- Un fallo de GTK al cancelar el arrastre reiniciaba el control deslizante cuando la reconstrucción se disparaba a mitad del arrastre

## [1.0.0-2ubuntu14] - 2026-09-22

### Cambiado
- El cambio de tema claro u oscuro reinicia la aplicación para aplicarse de verdad (GTK 4 ignora los cambios de `gtk-theme-name` con la ventana ya mostrada) y deriva la variante del tema del sistema para conservar el acento
- Las filas en estado Notificado o Buscando ya no tapan el resaltado de la selección, y el cambio de tema ya no fuerza Adwaita: pide la variante clara u oscura del tema del escritorio
- Botón para cambiar el orden de la fecha de solicitud

## [1.0.0-2ubuntu11] - 2026-09-22

Primera release publicada en GitHub. Reúne los cambios de las revisiones 1.0.0-2 a 1.0.0-2ubuntu11.

### Añadido
- Botón «Limpiar notificados»
- Colores de fondo en los estados Buscando y Notificado
- Contador de peticiones visibles en pantalla
- Fecha de solicitud, con calendario, y vista principal ordenada por ella; tamaños de póster ajustables
- Opciones de copia de seguridad y de restaurar una copia

### Cambiado
- Migración a GTK 4 y PyGObject (1.0.0-1)
- Desplazamiento en la ventana de gestión de peticionarios (1.0.0-2)
- Sinopsis justificada y menos espacio ocupado por ella

### Corregido
- Persistencia del tema claro u oscuro al arrancar
- Error al hacer doble clic en una petición sin fecha de solicitud
