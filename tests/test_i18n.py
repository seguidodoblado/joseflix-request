import gettext
import string

import pytest

from joseflix_request import i18n, models
from joseflix_request.i18n import _, ngettext

MO = i18n.LOCALE_DIR / "en" / "LC_MESSAGES" / f"{i18n.DOMAIN}.mo"
needs_catalog = pytest.mark.skipif(not MO.exists(), reason="Falta compilar po/en.po (ver po/README.md)")


def english():
    return gettext.translation(i18n.DOMAIN, localedir=str(i18n.LOCALE_DIR), languages=["en"])


def placeholders(text):
    return {name for _literal, name, _spec, _conv in string.Formatter().parse(text) if name}


def test_spanish_is_the_source_language_and_needs_no_catalog():
    assert _("Cancelar") == "Cancelar"
    assert ngettext("{count} petición", "{count} peticiones", 3) == "{count} peticiones"
    assert models.label("Notificado") == "✅ Notificado"


@needs_catalog
def test_english_catalog_translates():
    translation = english()
    assert translation.gettext("Cancelar") == "Cancel"
    assert translation.gettext("Ajustes") == "Settings"
    assert translation.gettext("Notificado") == "Notified"
    assert translation.gettext("Solicitado") == "Requested"


@needs_catalog
def test_english_plural_forms():
    translation = english()
    assert translation.ngettext("{count} petición", "{count} peticiones", 1) == "{count} request"
    assert translation.ngettext("{count} petición", "{count} peticiones", 5) == "{count} requests"


@needs_catalog
def test_translator_credits_entry_is_filled():
    assert "@" in english().gettext("translator-credits")


@needs_catalog
def test_every_translation_keeps_the_placeholders_of_the_original():
    """Si el inglés perdiera un {nombre}, .format() fallaría en pleno uso."""
    translation = english()
    messages = [m for m in translation._catalog if isinstance(m, str) and m]
    assert messages
    for message in messages:
        assert placeholders(translation.gettext(message)) == placeholders(message), message


@needs_catalog
def test_every_status_type_method_and_priority_is_translated():
    translation = english()
    for key, translated in models.names().items():
        assert translation.gettext(translated) != translated or key == "Normal", key
