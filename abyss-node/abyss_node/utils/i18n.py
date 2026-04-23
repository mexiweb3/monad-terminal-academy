"""
i18n — infraestructura de traducción ES/EN para Terminal Academy.

Arquitectura de plumbing + contenido. La idea es que cualquier string
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
#   create.*        -> UX narrativo del comando `create` pre-login
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

    # ------ Create intercept (bienvenida narrativa al crear cuenta) ------
    # Banners cortos que emite CmdCreateIntercept antes/después de delegar
    # a la creación real de cuenta de Evennia.
    "create.detecting": {
        "es": "|g> DETECTING SIGNAL...|n   |mneófito entrando al grid|n",
        "en": "|g> DETECTING SIGNAL...|n   |mnewcomer entering the grid|n",
    },
    "create.identity_written": {
        "es": "|g> IDENTITY WRITTEN TO /dev/academy/|n",
        "en": "|g> IDENTITY WRITTEN TO /dev/academy/|n",
    },
    "create.language_prompt": {
        "es": (
            "|g> LANGUAGE?|n Escribe |wlanguage es|n o |wlanguage en|n después de loguearte.\n"
            "|xDefault: español. En la pantalla de login puedes pasar idioma como 3er arg:|n\n"
            "|x  create <nombre> <clave> en|n"
        ),
        "en": (
            "|g> LANGUAGE?|n Type |wlanguage es|n or |wlanguage en|n after logging in.\n"
            "|xDefault: Spanish. On the login screen you can pass lang as 3rd arg:|n\n"
            "|x  create <name> <pass> en|n"
        ),
    },
    "create.sealed": {
        "es": (
            "|g> LEDGER ENTRY SEALED.|n\n"
            "|c> Prof. Shell te espera en /home.|n Conéctate con |wconnect <nombre> <clave>|n."
        ),
        "en": (
            "|g> LEDGER ENTRY SEALED.|n\n"
            "|c> Prof. Shell is waiting in /home.|n Log in with |wconnect <name> <pass>|n."
        ),
    },
    "create.lang_set": {
        "es": "|g> Idioma preferido registrado: |y{lang}|n.",
        "en": "|g> Preferred language recorded: |y{lang}|n.",
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
    "prologue.narrate_2": {
        "es": (
            "Si te pierdes, saluda al Profesor con `say hola prof`. "
            "Él vive aquí, en /home, y te espera."
        ),
        "en": (
            "If you get lost, greet the Professor with `say hi prof`. "
            "He lives here, in /home, waiting for you."
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

    # ------ Outro (world/lore/fragments.py OUTRO) ------------------------
    "outro.scene.title": {
        "es": "CAPÍTULO III · ASCENSIÓN",
        "en": "CHAPTER III · ASCENSION",
    },
    "outro.scene.body": {
        "es": (
            "Las paredes del /claude_dojo vibran. Los diez fragmentos de "
            "tu memoria se alinean como estrellas. Sabes leer, crear, "
            "conectar, persistir, invocar. Ya no eres un neófito: eres "
            "un intérprete del shell."
        ),
        "en": (
            "The walls of /claude_dojo vibrate. The ten fragments of "
            "your memory align like stars. You know how to read, create, "
            "connect, persist, invoke. You are no longer a neophyte: you "
            "are an interpreter of the shell."
        ),
    },
    "outro.narrate_1": {
        "es": (
            "El Corruptor retrocede. No lo has destruido — nadie lo destruye — "
            "pero le has arrebatado lo que devoraba: tu silencio."
        ),
        "en": (
            "The Corruptor retreats. You haven't destroyed it — no one ever does — "
            "but you've taken back what it used to devour: your silence."
        ),
    },
    "outro.narrate_2": {
        "es": "Has completado Terminal Academy. Bienvenide al siguiente plano.",
        "en": "You have completed Terminal Academy. Welcome to the next plane.",
    },
    "outro.dialogue_1": {
        "es": "Lo lograste. Ya no te enseño yo — desde hoy te enseña la práctica.",
        "en": "You did it. I'm no longer your teacher — from today on, practice is.",
    },
    "outro.dialogue_2": {
        "es": (
            "Sólo queda un ritual. Linkea tu wallet con `link 0x...` y luego "
            "`claim`. Tu identidad quedará grabada onchain en Monad, "
            "imposible de borrar, imposible de olvidar."
        ),
        "en": (
            "Only one ritual remains. Link your wallet with `link 0x...` and then "
            "`claim`. Your identity will be engraved onchain on Monad, "
            "impossible to erase, impossible to forget."
        ),
    },
    "outro.dialogue_3": {
        "es": (
            "Recuerda: el shell no se aprende una sola vez. "
            "Vuelve cuando quieras — siempre habrá algo nuevo que teclear."
        ),
        "en": (
            "Remember: the shell isn't something you learn only once. "
            "Come back whenever you want — there will always be something new to type."
        ),
    },

    # ------ Descripciones de rooms (world/zones/terminal_academy.py) -----
    # Solo sembramos EN para los 6 rooms iniciales críticos. El swap real
    # en las rooms (caller-aware) lo puede encarar F5 en otra sesión; aquí
    # garantizamos el contenido traducido para cuando se migre.
    "room.home.desc": {
        "es": (
            "Estás en |g/home|n, tu directorio base. Un cursor verde parpadea en la\n"
            "oscuridad. Prof. Shell te espera aquí. Teclea |wls|n para ver qué hay."
        ),
        "en": (
            "You are in |g/home|n, your base directory. A green cursor blinks in the\n"
            "darkness. Prof. Shell is waiting here. Type |wls|n to see what's around."
        ),
    },
    "room.ls_dojo.desc": {
        "es": (
            "Sala |gls_dojo|n — un espacio abierto lleno de archivos flotando como hojas.\n"
            "Aquí aprendes a |wlistar|n lo invisible. |wls -la|n revela los ocultos."
        ),
        "en": (
            "The |gls_dojo|n — an open space full of files drifting like leaves.\n"
            "Here you learn to |wlist|n what's hidden. |wls -la|n reveals the unseen."
        ),
    },
    "room.cd_dojo.desc": {
        "es": (
            "Sala |gcd_dojo|n — un cruce de caminos. Las salidas se ramifican como un\n"
            "árbol. Practica |wcd <dir>|n y |wpwd|n para saber siempre dónde estás."
        ),
        "en": (
            "The |gcd_dojo|n — a crossroads. Exits branch out like a tree.\n"
            "Practice |wcd <dir>|n and |wpwd|n so you always know where you are."
        ),
    },
    "room.cat_dojo.desc": {
        "es": (
            "Sala |gcat_dojo|n — un templo de lectura. Cada archivo es una puerta al\n"
            "pasado. |wcat <archivo>|n despierta lo que el texto guarda dormido."
        ),
        "en": (
            "The |gcat_dojo|n — a temple of reading. Every file is a door to the\n"
            "past. |wcat <file>|n awakens what the text keeps dormant."
        ),
    },
    "room.mkdir_dojo.desc": {
        "es": (
            "Sala |gmkdir_dojo|n — aquí se crea. |wmkdir <nombre>|n construye un\n"
            "directorio; |wtouch <archivo>|n crea un archivo vacío. Construye algo."
        ),
        "en": (
            "The |gmkdir_dojo|n — this is where things are made. |wmkdir <name>|n\n"
            "builds a directory; |wtouch <file>|n creates an empty file. Build something."
        ),
    },
    "room.claude_dojo.desc": {
        "es": (
            "Sala |gclaude_dojo|n — el altar de la IA. Aquí |wclaude|n abre un CLI\n"
            "capaz de generar y deployar contratos en Monad. El último fragmento vive aquí."
        ),
        "en": (
            "The |gclaude_dojo|n — the AI altar. Here |wclaude|n opens a CLI\n"
            "that can generate and deploy contracts on Monad. The last fragment lives here."
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
