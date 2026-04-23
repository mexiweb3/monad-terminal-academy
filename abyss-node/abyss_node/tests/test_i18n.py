"""
Tests unitarios para `utils.i18n`.

No requieren Evennia runtime: se mockea `caller` y `account` con
`unittest.mock.MagicMock`, probando solo la capa pura de resolución de
idioma y traducción.

Ejecutar (stdlib unittest):
    cd abyss-node/abyss_node
    python -m unittest tests.test_i18n -v

Con pytest (si está disponible):
    cd abyss-node/abyss_node
    pytest tests/test_i18n.py -v
"""

import os
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock

# Garantiza que `abyss_node/` esté en PYTHONPATH aunque los tests se corran
# desde otro directorio (p. ej. desde la raíz del repo).
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from utils.i18n import (  # noqa: E402
    DEFAULT_LANG,
    SUPPORTED,
    TRANSLATIONS,
    get_lang,
    set_lang,
    t,
)


def _make_caller(account_lang=None, character_lang=None, has_account=True):
    """Construye un mock de caller con estructura minimal.

    caller.account.db.language y caller.db.language apuntan a los valores
    recibidos. Los atributos que no se especifiquen quedan como None (que es
    lo que Evennia devuelve por default en AttributeHandler cuando la key
    no existe).
    """
    caller = MagicMock()
    # caller.db simula el AttributeHandler del character
    caller.db = SimpleNamespace(language=character_lang)

    if has_account:
        account = MagicMock()
        account.db = SimpleNamespace(language=account_lang)
        caller.account = account
    else:
        caller.account = None

    return caller


class GetLangTests(unittest.TestCase):
    """Resolución de idioma desde caller."""

    def test_account_language_en_returns_en(self):
        """Si account.db.language='en', get_lang devuelve 'en'."""
        caller = _make_caller(account_lang="en")
        self.assertEqual(get_lang(caller), "en")

    def test_no_language_attribute_returns_default(self):
        """Sin account.db.language ni caller.db.language, cae a DEFAULT_LANG."""
        caller = _make_caller(account_lang=None, character_lang=None)
        self.assertEqual(get_lang(caller), DEFAULT_LANG)

    def test_account_takes_precedence_over_character(self):
        """Si ambos tienen language, gana el de account."""
        caller = _make_caller(account_lang="en", character_lang="es")
        self.assertEqual(get_lang(caller), "en")

    def test_invalid_language_falls_back_to_default(self):
        """Un código no en SUPPORTED se ignora → DEFAULT_LANG."""
        caller = _make_caller(account_lang="fr")
        self.assertEqual(get_lang(caller), DEFAULT_LANG)

    def test_character_language_when_no_account(self):
        """Sin account pero con caller.db.language, usa el character."""
        caller = _make_caller(has_account=False, character_lang="en")
        self.assertEqual(get_lang(caller), "en")


class TranslateTests(unittest.TestCase):
    """Función pública `t`."""

    def test_banner_title_returns_non_empty(self):
        """t(caller, 'banner.title') devuelve string no vacío."""
        caller = _make_caller(account_lang="es")
        result = t(caller, "banner.title")
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)

    def test_translates_to_en_when_account_en(self):
        """Con account.db.language='en', t devuelve la versión EN."""
        caller_en = _make_caller(account_lang="en")
        caller_es = _make_caller(account_lang="es")
        # subtitle tiene traducciones distintas en ES y EN
        self.assertNotEqual(
            t(caller_en, "banner.subtitle"),
            t(caller_es, "banner.subtitle"),
        )
        self.assertIn("onchain", t(caller_en, "banner.subtitle"))

    def test_missing_key_returns_raw_key(self):
        """Si la key no existe en TRANSLATIONS, devuelve la key cruda."""
        caller = _make_caller(account_lang="es")
        result = t(caller, "no.existe.nunca.jamas")
        self.assertEqual(result, "no.existe.nunca.jamas")

    def test_missing_lang_falls_back_to_default(self):
        """Si la key existe pero no tiene traducción al idioma pedido, usa DEFAULT_LANG."""
        # Insertar una key temporal solo con DEFAULT_LANG y probar el fallback
        key = "test.only_es_tmp"
        TRANSLATIONS[key] = {DEFAULT_LANG: "hola"}
        try:
            caller_en = _make_caller(account_lang="en")
            self.assertEqual(t(caller_en, key), "hola")
        finally:
            TRANSLATIONS.pop(key, None)

    def test_format_kwargs_are_applied(self):
        """Los kwargs se aplican via str.format al template."""
        caller = _make_caller(account_lang="es")
        result = t(
            caller,
            "cmd.language.changed",
            lang="en",
            label="Inglés",
        )
        self.assertIn("en", result)
        self.assertIn("Inglés", result)

    def test_format_missing_kwarg_returns_template(self):
        """Si el format falla por kwargs faltantes, devuelve el template crudo."""
        caller = _make_caller(account_lang="es")
        # cmd.language.changed espera {lang} y {label}
        # si no pasamos ninguno, format falla — debe devolver template sin reventar
        result = t(caller, "cmd.language.changed")
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)


class SetLangTests(unittest.TestCase):
    """Función pública `set_lang`."""

    def test_set_valid_language(self):
        """set_lang con 'en' setea account.db.language='en' y devuelve True."""
        account = MagicMock()
        account.db = SimpleNamespace(language=None)
        self.assertTrue(set_lang(account, "en"))
        self.assertEqual(account.db.language, "en")

    def test_set_invalid_language_returns_false(self):
        """set_lang con código no soportado devuelve False y no toca db."""
        account = MagicMock()
        account.db = SimpleNamespace(language="es")
        self.assertFalse(set_lang(account, "fr"))
        self.assertEqual(account.db.language, "es")

    def test_all_supported_are_settable(self):
        """Cualquier code en SUPPORTED es seteable."""
        for code in SUPPORTED:
            account = MagicMock()
            account.db = SimpleNamespace(language=None)
            self.assertTrue(set_lang(account, code), f"code={code}")
            self.assertEqual(account.db.language, code)


if __name__ == "__main__":
    unittest.main()
