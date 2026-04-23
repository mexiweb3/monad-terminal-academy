"""
Tests offline para `commands/unloggedin/create_intercept.py`.

No levantan Evennia / Django. Validan:
    1. `_split_args` separa correctamente el 3er arg de idioma.
    2. Todas las claves de i18n que usa el create_intercept existen en
       ambos idiomas (ES + EN).
    3. Las claves nuevas de prologue/outro agregadas por F7 existen.
    4. El wrapper `_get_prologue` / `_get_outro` (via import directo de
       i18n.TRANSLATIONS) cubren las keys referenciadas en characters.py.

Ejecutar:
    cd abyss-node/abyss_node
    python3 -m unittest tests.test_create_intercept
"""

import os
import sys
import unittest

# Aseguramos que los módulos `commands` / `utils` del proyecto estén en el
# path cuando se corre desde otro cwd. Apuntamos al directorio padre del
# paquete `tests` (= abyss-node/abyss_node).
_HERE = os.path.abspath(os.path.dirname(__file__))
_PKG_ROOT = os.path.abspath(os.path.join(_HERE, ".."))
if _PKG_ROOT not in sys.path:
    sys.path.insert(0, _PKG_ROOT)


class TestSplitArgs(unittest.TestCase):
    """`_split_args` separa el 3er arg de idioma de forma robusta."""

    def setUp(self):
        from commands.unloggedin.create_intercept import _split_args
        self.split = _split_args

    def test_empty(self):
        self.assertEqual(self.split(""), ("", None))
        self.assertEqual(self.split("   "), ("", None))

    def test_two_args_no_lang(self):
        self.assertEqual(self.split("mexi pass123"), ("mexi pass123", None))

    def test_three_args_with_es(self):
        self.assertEqual(self.split("mexi pass123 es"), ("mexi pass123", "es"))

    def test_three_args_with_en(self):
        self.assertEqual(self.split("mexi pass123 en"), ("mexi pass123", "en"))

    def test_lang_uppercase_normalized(self):
        # Aceptamos "EN"/"ES"/"en"/"es" — hacemos .lower() antes de comparar
        # contra _VALID_LANGS, así el usuario puede escribir como quiera.
        self.assertEqual(self.split("mexi pass EN"), ("mexi pass", "en"))
        self.assertEqual(self.split("mexi pass Es"), ("mexi pass", "es"))

    def test_fourth_arg_unsupported_lang(self):
        # Si el último token es una palabra que no es es/en, no tocamos args.
        self.assertEqual(self.split("mexi pass fr"), ("mexi pass fr", None))

    def test_quoted_args_passthrough(self):
        # Las comillas indican que el password puede tener espacios —
        # mejor no intervenir.
        raw = 'mexi "my pass" en'
        self.assertEqual(self.split(raw), (raw, None))

    def test_user_picks_lang_as_password(self):
        # Caso borde: usuario eligió "en" como password real. Con 2 tokens
        # no lo detectamos como idioma (protección parcial — documentado).
        self.assertEqual(self.split("mexi en"), ("mexi en", None))


class TestI18nKeysExist(unittest.TestCase):
    """Las keys nuevas de F7 deben existir en ambos idiomas."""

    def setUp(self):
        from utils.i18n import TRANSLATIONS, SUPPORTED
        self.T = TRANSLATIONS
        self.LANGS = SUPPORTED

    def _assert_keys(self, keys):
        missing = []
        for key in keys:
            entry = self.T.get(key)
            if entry is None:
                missing.append(f"{key} (no key)")
                continue
            for lang in self.LANGS:
                if lang not in entry or not entry[lang]:
                    missing.append(f"{key} (missing '{lang}')")
        self.assertEqual(missing, [], f"claves faltantes/incompletas: {missing}")

    def test_create_keys(self):
        self._assert_keys([
            "create.detecting",
            "create.identity_written",
            "create.language_prompt",
            "create.sealed",
            "create.lang_set",
        ])

    def test_prologue_keys(self):
        self._assert_keys([
            "prologue.scene.title",
            "prologue.scene.body",
            "prologue.narrate_1",
            "prologue.narrate_2",
            "prologue.dialogue_1",
            "prologue.dialogue_2",
            "prologue.dialogue_3",
            "prologue.dialogue_4",
        ])

    def test_outro_keys(self):
        self._assert_keys([
            "outro.scene.title",
            "outro.scene.body",
            "outro.narrate_1",
            "outro.narrate_2",
            "outro.dialogue_1",
            "outro.dialogue_2",
            "outro.dialogue_3",
        ])

    def test_room_keys_seed(self):
        # Sembramos EN para los 6 rooms críticos. El swap en world/zones/
        # lo puede hacer F5 — acá validamos que el contenido esté listo.
        self._assert_keys([
            "room.home.desc",
            "room.ls_dojo.desc",
            "room.cd_dojo.desc",
            "room.cat_dojo.desc",
            "room.mkdir_dojo.desc",
            "room.claude_dojo.desc",
        ])

    def test_banner_keys_preserved(self):
        # F2 dejó estas keys; F7 no debe haberlas roto.
        self._assert_keys([
            "banner.title",
            "banner.subtitle",
            "banner.subtitle2",
            "tutorial.welcome",
            "tutorial.first_step",
            "tutorial.greet_prof",
        ])

    def test_language_cmd_keys_preserved(self):
        self._assert_keys([
            "cmd.language.current",
            "cmd.language.changed",
            "cmd.language.invalid",
        ])


class TestI18nResolution(unittest.TestCase):
    """`t()` resuelve y formatea correctamente sin levantar Django."""

    def setUp(self):
        from utils.i18n import t, get_lang, set_lang, SUPPORTED
        self.t = t
        self.get_lang = get_lang
        self.set_lang = set_lang
        self.SUPPORTED = SUPPORTED

    def test_default_lang_es(self):
        # Caller None → fallback a DEFAULT_LANG ("es").
        msg = self.t(None, "create.detecting")
        self.assertIn("DETECTING", msg)
        self.assertIn("neófito", msg)

    def test_format_kwargs(self):
        msg = self.t(None, "create.lang_set", lang="en")
        self.assertIn("en", msg)

    def test_supported_list(self):
        self.assertIn("es", self.SUPPORTED)
        self.assertIn("en", self.SUPPORTED)


class TestCreateInterceptClass(unittest.TestCase):
    """Smoke tests sobre la clase sin instanciar Evennia."""

    def setUp(self):
        from commands.unloggedin.create_intercept import CmdCreateIntercept
        self.cls = CmdCreateIntercept

    def test_key_is_create(self):
        self.assertEqual(self.cls.key, "create")

    def test_aliases_match_default(self):
        self.assertIn("cre", self.cls.aliases)
        self.assertIn("cr", self.cls.aliases)

    def test_extract_username_simple(self):
        self.assertEqual(self.cls._extract_username("mexi pass123"), "mexi")

    def test_extract_username_quoted(self):
        self.assertEqual(
            self.cls._extract_username('"Ana Banana" "my pass"'),
            "Ana Banana",
        )

    def test_extract_username_empty(self):
        self.assertIsNone(self.cls._extract_username(""))
        self.assertIsNone(self.cls._extract_username(None))


if __name__ == "__main__":
    unittest.main()
