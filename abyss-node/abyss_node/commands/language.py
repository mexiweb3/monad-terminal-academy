"""
Comando `language` — permite al jugador cambiar el idioma del MUD.

Uso:
    language            → muestra idioma actual + lista + cómo cambiarlo
    language es         → cambia el idioma a español
    language en         → cambia el idioma a inglés
    lang / idioma       → aliases

La preferencia se guarda en `account.db.language`, por lo que persiste entre
personajes y sesiones del mismo account. Si no hay account (p. ej. NPCs), cae
al character.db.language.

Todas las strings del comando pasan por `utils.i18n.t`, así que una vez
cambiado el idioma, la confirmación ya sale en el nuevo idioma.
"""

from evennia import Command

from utils.i18n import (
    DEFAULT_LANG,
    SUPPORTED,
    get_lang,
    set_lang,
    t,
    _lang_label,
)


class CmdLanguage(Command):
    """
    Cambia el idioma del MUD / Change the MUD language.

    Usage:
      language              # muestra idioma actual y cómo cambiarlo
      language <code>       # cambia el idioma (códigos: es, en)

    Aliases: lang, idioma

    Examples:
      language              → ver idioma actual
      language en           → cambiar a inglés
      language es           → cambiar a español
    """

    key = "language"
    aliases = ["lang", "idioma"]
    locks = "cmd:all()"
    help_category = "System"

    def func(self):
        caller = self.caller
        arg = (self.args or "").strip().lower()

        # Sin argumentos: mostrar idioma actual + instrucciones
        if not arg:
            current = get_lang(caller)
            supported_str = ", ".join(SUPPORTED)
            label = _lang_label(current, current)
            caller.msg(
                t(
                    caller,
                    "cmd.language.current",
                    lang=current,
                    label=label,
                    supported=supported_str,
                )
            )
            return

        # Con argumento: intentar cambiar
        if arg not in SUPPORTED:
            supported_str = ", ".join(SUPPORTED)
            caller.msg(
                t(
                    caller,
                    "cmd.language.invalid",
                    lang=arg,
                    supported=supported_str,
                )
            )
            return

        # Target: preferimos account, fallback a character.
        account = getattr(caller, "account", None)
        target = account if account is not None else caller
        ok = set_lang(target, arg)

        if not ok:
            # Raro (SUPPORTED chequeado arriba) — mostrar error inválido igual
            supported_str = ", ".join(SUPPORTED)
            caller.msg(
                t(
                    caller,
                    "cmd.language.invalid",
                    lang=arg,
                    supported=supported_str,
                )
            )
            return

        # Confirmación ya en el NUEVO idioma (get_lang leerá el valor recién
        # seteado en account.db.language).
        label = _lang_label(arg, arg)
        caller.msg(
            t(
                caller,
                "cmd.language.changed",
                lang=arg,
                label=label,
            )
        )
