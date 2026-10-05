from joseflix_request import models


def test_keys_are_the_values_stored_in_the_database():
    assert models.STATUSES == ("Solicitado", "Buscando", "Descargado", "Subido", "Notificado", "Corregir")
    assert models.TYPES == ("Película", "Serie")
    assert models.PRIORITIES == ("Alta", "Normal", "Baja")
    assert "Sin método" in models.METHODS


def test_every_key_has_an_emoji_and_a_label():
    for key in (*models.STATUSES, *models.TYPES, *models.METHODS, *models.PRIORITIES):
        assert key in models.EMOJI
        assert models.label(key).startswith(models.EMOJI[key])


def test_label_in_the_source_language_is_emoji_and_key():
    assert models.label("Solicitado") == "📨 Solicitado"
    assert models.label("JDownloader") == "⬇️ JDownloader"   # las marcas no se traducen
    assert models.name("Baja") == "Baja"


def test_an_unknown_key_from_an_old_database_is_shown_as_it_is():
    assert models.label("Algo antiguo") == "Algo antiguo"
    assert models.name("Algo antiguo") == "Algo antiguo"
