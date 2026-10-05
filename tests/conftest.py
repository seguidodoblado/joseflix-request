import os
import tempfile

# Las pruebas nunca tocan los datos reales: antes de importar nada del paquete (que fija sus rutas al importarse)
# se apunta XDG_DATA_HOME a una carpeta temporal. También se fija el idioma, para que los textos sean los del
# idioma fuente (español) vengan los .mo compilados o no.
os.environ["XDG_DATA_HOME"] = tempfile.mkdtemp(prefix="joseflix-tests-")
os.environ["LANGUAGE"] = "es"
os.environ.pop("TMDB_API_KEY", None)
