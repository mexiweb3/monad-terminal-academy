"""
i18n — infraestructura de traducción ES/EN para Terminal Academy.

Arquitectura de plumbing, no de contenido. La idea es que cualquier string
player-facing del MUD pueda resolverse con `t(caller, "clave.punteada")` y
que el jugador pueda cambiar idioma con el comando `language` (setea
`account.db.language`).

Uso básico
----------
    from utils.i18n import t

    msg = t(caller, "banner.title")
    caller.msg(msg)

Con formato:
    caller.msg(t(caller, "cmd.language.changed", lang="en"))

Resolución de idioma
--------------------
`get_lang(caller)` mira, en orden:
    1. caller.account.db.language   (prioridad máxima: preferencia del jugador)
    2. caller.db.language            (fallback: en el character)
    3. DEFAULT_LANG                  (fallback final)

Fallback de traducciones
------------------------
Si `key` no existe en el idioma resuelto → cae a DEFAULT_LANG (ES).
Si tampoco existe en DEFAULT_LANG → devuelve la key cruda y emite un warning.

Para agregar traducciones
-------------------------
Solo poblar el dict `TRANSLATIONS` con nuevas keys. Formato:
    "dominio.subclave": {"es": "...", "en": "..."}

No se requiere ningún cambio en el código que invoca `t()`.
"""

DEFAULT_LANG = "es"
SUPPORTED = ("es", "en")


def _log_warn(msg: str) -> None:
    """Loguea un warning si Evennia está disponible.

    Import lazy para que el módulo sea importable fuera del runtime de
    Evennia (ej: tests unitarios sin DJANGO_SETTINGS_MODULE). Si el import
    falla, silenciamos — este helper es puramente best-effort.
    """
    try:
        from evennia.utils import logger
        logger.log_warn(msg)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# TRANSLATIONS — tabla de cadenas traducibles
# ---------------------------------------------------------------------------
# Estructura: TRANSLATIONS[clave][lang] = str
#
# Convención de claves:
#   banner.*        -> ACADEMY_BANNER (typeclasses/characters.py)
#   tutorial.*      -> ACADEMY_TUTORIAL (typeclasses/characters.py)
#   prologue.*      -> world/lore/fragments.py PROLOGUE
#   outro.*         -> world/lore/fragments.py OUTRO
#   cmd.<name>.*    -> strings del comando <name>
#   room.<key>.*    -> descripciones de rooms
#   npc.<key>.*     -> diálogos de NPCs
#   quest.<id>.*    -> descripciones de quests
#
# Las claves faltantes caen a DEFAULT_LANG automáticamente.
TRANSLATIONS = {
    # ------ Banner (ACADEMY_BANNER) --------------------------------------
    "banner.title": {
        "es": "M O N A D   T E R M I N A L   A C A D E M Y",
        "en": "M O N A D   T E R M I N A L   A C A D E M Y",
    },
    "banner.subtitle": {
        "es": "aprende la terminal · gana $TERM onchain en Monad",
        "en": "learn the terminal · earn $TERM onchain on Monad",
    },
    "banner.subtitle2": {
        "es": "+ Claude CLI para generar y deployar contratos",
        "en": "+ Claude CLI to generate and deploy contracts",
    },

    # ------ Tutorial (ACADEMY_TUTORIAL) ----------------------------------
    "tutorial.welcome": {
        "es": (
            "|wBienvenide a la Academia.|n Este es un curso interactivo de terminal\n"
            "que paga en |y$TERM|n (ERC-20 en Monad testnet) cuando terminas quests."
        ),
        "en": (
            "|wWelcome to the Academy.|n This is an interactive terminal course\n"
            "that pays in |y$TERM|n (ERC-20 on Monad testnet) when you finish quests."
        ),
    },
    "tutorial.first_step": {
        "es": (
            "|yPrimer paso:|n escribe |gls|n y presiona Enter para listar este directorio.\n"
            "En cualquier momento escribe |ghelp|n para ver comandos + tu próxima quest."
        ),
        "en": (
            "|yFirst step:|n type |gls|n and press Enter to list this directory.\n"
            "At any time type |ghelp|n to see commands + your next quest."
        ),
    },
    "tutorial.greet_prof": {
        "es": "También puedes saludar a |cProf. Shell|n con |wsay hola prof|n si estás perdide.",
        "en": "You can also greet |cProf. Shell|n with |wsay hi prof|n if you feel lost.",
    },

    # ------ Prólogo (world/lore/fragments.py PROLOGUE) -------------------
    "prologue.scene.title": {
        "es": "CAPÍTULO I · DESPERTAR",
        "en": "CHAPTER I · AWAKENING",
    },
    "prologue.scene.body": {
        "es": (
            "Estática. Un zumbido bajo. Abres los ojos y no recuerdas "
            "cómo llegaste aquí. Sólo hay texto verde flotando en la "
            "oscuridad — y una voz familiar que no termina de nombrarte."
        ),
        "en": (
            "Static. A low hum. You open your eyes and don't remember "
            "how you got here. There's only green text floating in the "
            "darkness — and a familiar voice that never quite names you."
        ),
    },
    "prologue.narrate_1": {
        "es": (
            "Un filesystem roto se extiende hasta donde alcanza tu memoria. "
            "Los directorios parpadean como constelaciones a punto de apagarse."
        ),
        "en": (
            "A broken filesystem stretches as far as your memory reaches. "
            "Directories flicker like constellations about to go out."
        ),
    },
    "prologue.dialogue_1": {
        "es": "Respira, Neófito. Te encontré justo a tiempo.",
        "en": "Breathe, Neophyte. I found you just in time.",
    },
    "prologue.dialogue_2": {
        "es": (
            "El Corruptor ha borrado tu memoria, pero no tu sintaxis. "
            "Los comandos todavía responden a tus dedos."
        ),
        "en": (
            "The Corruptor has erased your memory, but not your syntax. "
            "Commands still respond to your fingers."
        ),
    },
    "prologue.dialogue_3": {
        "es": (
            "Empieza por lo básico: teclea `ls` para ver dónde estás. "
            "Cada comando que aprendas recuperará un fragmento de ti."
        ),
        "en": (
            "Start with the basics: type `ls` to see where you are. "
            "Each command you learn will recover a fragment of you."
        ),
    },
    "prologue.dialogue_4": {
        "es": (
            "Si te pierdes, saluda al Profesor con `say hola prof`. "
            "Él vive aquí, en /home, y te espera."
        ),
        "en": (
            "If you get lost, greet the Professor with `say hi prof`. "
            "He lives here, in /home, and he's waiting for you."
        ),
    },

    # ------ Comando `language` -------------------------------------------
    "cmd.language.current": {
        "es": (
            "Idioma actual: |y{lang}|n ({label}).\n"
            "Idiomas disponibles: {supported}.\n"
            "Para cambiar escribe |wlanguage <código>|n (ej: |wlanguage en|n)."
        ),
        "en": (
            "Current language: |y{lang}|n ({label}).\n"
            "Available languages: {supported}.\n"
            "To change type |wlanguage <code>|n (e.g. |wlanguage es|n)."
        ),
    },
    "cmd.language.changed": {
        "es": "Idioma cambiado a |y{lang}|n ({label}).",
        "en": "Language changed to |y{lang}|n ({label}).",
    },
    "cmd.language.invalid": {
        "es": (
            "|rIdioma '{lang}' no soportado.|n "
            "Soportados: {supported}."
        ),
        "en": (
            "|rLanguage '{lang}' not supported.|n "
            "Supported: {supported}."
        ),
    },
}


# ---------------------------------------------------------------------------
# Etiquetas legibles (para mensajería UI del propio comando language)
# ---------------------------------------------------------------------------
_LANG_LABELS = {
    "es": {"es": "Español", "en": "Spanish"},
    "en": {"es": "Inglés", "en": "English"},
}


def _lang_label(code: str, shown_in: str) -> str:
    """Devuelve el nombre del idioma `code` escrito en el idioma `shown_in`.

    Si no hay entrada, cae al código crudo.
    """
    try:
        return _LANG_LABELS.get(code, {}).get(shown_in, code)
    except Exception:
        return code


# ---------------------------------------------------------------------------
# API pública
# ---------------------------------------------------------------------------
def get_lang(caller) -> str:
    """Resuelve el idioma del caller.

    Orden de resolución:
        1. caller.account.db.language
        2. caller.db.language
        3. DEFAULT_LANG

    Valida contra SUPPORTED — si la preferencia guardada es inválida, cae a
    DEFAULT_LANG.
    """
    candidates = []
    try:
        account = getattr(caller, "account", None)
        if account is not None:
            lang = getattr(account.db, "language", None)
            if lang:
                candidates.append(lang)
    except Exception:
        pass
    try:
        if hasattr(caller, "db"):
            lang = getattr(caller.db, "language", None)
            if lang:
                candidates.append(lang)
    except Exception:
        pass

    for lang in candidates:
        if lang in SUPPORTED:
            return lang

    return DEFAULT_LANG


def t(caller, key: str, **kwargs) -> str:
    """Traduce `key` al idioma del caller.

    Si la key no existe en el idioma resuelto, cae a DEFAULT_LANG.
    Si tampoco existe en DEFAULT_LANG, devuelve la key cruda + warning al log.

    Los kwargs se aplican con `str.format` al resultado. Si el format falla
    (ej: llave sin proveer), devuelve el template crudo y loguea el error.
    """
    lang = get_lang(caller)
    entry = TRANSLATIONS.get(key)

    if entry is None:
        _log_warn(f"[i18n] key no registrada: '{key}'")
        return key

    template = entry.get(lang)
    if template is None:
        template = entry.get(DEFAULT_LANG)
    if template is None:
        _log_warn(
            f"[i18n] key '{key}' sin traducción en '{lang}' ni en '{DEFAULT_LANG}'"
        )
        return key

    if not kwargs:
        return template
    try:
        return template.format(**kwargs)
    except (KeyError, IndexError, ValueError) as err:
        _log_warn(f"[i18n] format de '{key}' falló: {err}")
        return template


def set_lang(account, lang: str) -> bool:
    """Setea `account.db.language` al código indicado.

    Devuelve True si se seteó, False si el código no está en SUPPORTED o si
    la cuenta no tiene `db` accesible.
    """
    if lang not in SUPPORTED:
        return False
    try:
        account.db.language = lang
    except Exception:
        return False
    return True
