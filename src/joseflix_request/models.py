"""Estados, tipos, métodos de descarga y prioridades.

Las claves (`Solicitado`, `Película`…) son lo que se guarda en la base de datos y lo que compara el código;
no se traducen. Lo que ve el usuario es `label(clave)`: el emoji y el nombre traducido.
"""
from .i18n import _

STATUSES = ("Solicitado", "Buscando", "Descargado", "Subido", "Notificado", "Corregir")
TYPES = ("Película", "Serie")
METHODS = ("Sin método", "JDownloader", "Transmission", "aMule")
PRIORITIES = ("Alta", "Normal", "Baja")

EMOJI = {
    "Solicitado": "📨", "Buscando": "🔎", "Descargado": "📥", "Subido": "📤", "Notificado": "✅",
    "Corregir": "🔧", "Película": "🎬", "Serie": "📺", "Sin método": "❓", "JDownloader": "⬇️",
    "Transmission": "🧲", "aMule": "🐴", "Alta": "🔴", "Normal": "🟡", "Baja": "🟢",
}


def names() -> dict[str, str]:
    """El nombre de cada clave en el idioma del usuario (JDownloader, Transmission y aMule son marcas)."""
    return {
        "Solicitado": _("Solicitado"), "Buscando": _("Buscando"), "Descargado": _("Descargado"),
        "Subido": _("Subido"), "Notificado": _("Notificado"), "Corregir": _("Corregir"),
        "Película": _("Película"), "Serie": _("Serie"), "Sin método": _("Sin método"),
        "Alta": _("Alta"), "Normal": _("Normal"), "Baja": _("Baja"),
    }


def name(key: str) -> str:
    return names().get(key, key)


def label(key: str) -> str:
    """Emoji y nombre traducido; una clave desconocida (un dato antiguo) se muestra tal cual."""
    return f"{EMOJI[key]} {name(key)}" if key in EMOJI else key
