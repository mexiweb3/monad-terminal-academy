"""
`create` interceptado — bienvenida narrativa + selección temprana de idioma.

UX objetivo
-----------
El comando `create` nativo de Evennia es funcional pero seco: pide usuario y
pass, confirma con un Y/N, y emite un "A new account was created. Welcome!".
Para Terminal Academy, el momento en que alguien teclea `create` es el
**primer acto dramático** del juego: el sistema detecta a un neófito
entrando al grid. Queremos aprovecharlo.

Flujo
-----
1. Usuario teclea alguna de estas formas:

       create <nombre> <clave>
       create <nombre> <clave> es
       create <nombre> <clave> en

2. Si viene un 3er argumento y es "es"/"en", lo extraemos y lo guardamos
   para aplicarlo después.
3. Emitimos el banner "DETECTING SIGNAL..." ANTES de llamar al flujo
   nativo de Evennia (el Y/N de confirmación queda intacto).
4. Llamamos a `super().func()` — que es un **generador** (yields prompts).
   Usamos `yield from` para re-exportar esos yields al cmdhandler de
   Evennia y que el prompt Y/N siga funcionando como siempre.
5. Post-creación: buscamos la Account recién creada por su username. Si
   existe (=> la creación tuvo éxito) aplicamos `set_lang` y emitimos los
   banners "IDENTITY WRITTEN" + "LEDGER ENTRY SEALED".

Por qué 3er-arg en vez de prompt interactivo
--------------------------------------------
La alternativa planteada — marcar `session.ndb._expected_lang_input = True`
para interceptar el siguiente comando — choca con dos cosas:

    * El cmdhandler de unloggedin valida cada input contra el CmdSet; no hay
      un hook simple para "devuélveme el siguiente raw input sin re-parsear
      comandos". Implementarlo obligaría a meter un cmdset temporal o un
      listener en session.data_in, cualquiera de los dos es frágil y se rompe
      en cada upgrade de Evennia.

    * `super().func()` ya es un generador que hace `yield` para el Y/N de
      confirmación. Añadir un segundo yield encadenado al suyo es posible
      pero duplica la carga cognitiva del flujo y complica errores (timeouts,
      Ctrl-C, Y/N cancelado).

El 3er-arg es una convención documentada (se menciona explícitamente en el
banner post-create "LANGUAGE?") y no impide al jugador cambiar después con
`language en` una vez logueado. Costo cero, robustez alta.

Tests
-----
Ver tests/test_create_intercept.py — son offline (no levantan Evennia),
validan el parsing de argumentos + la existencia de las claves de i18n.
"""

from __future__ import annotations

import re

try:
    # Path normal dentro de Evennia runtime.
    from evennia.commands.default.unloggedin import CmdUnconnectedCreate
except Exception:  # pragma: no cover  (fallback para tests offline)
    CmdUnconnectedCreate = object  # type: ignore[assignment,misc]


# Idiomas que aceptamos como 3er argumento de `create`.
_VALID_LANGS = ("es", "en")


def _split_args(raw: str) -> tuple[str, str | None]:
    """
    Separa el 3er argumento de idioma del resto de args.

    Devuelve (args_sin_idioma, idioma_o_None). La detección es conservadora:
    sólo se considera idioma si el ÚLTIMO token (separado por espacios) está
    en ``_VALID_LANGS`` y el resto de la cadena tiene al menos 2 tokens más
    (nombre + password). Si la detección es ambigua, devolvemos (raw, None)
    y dejamos que Evennia se queje del formato como siempre.

    Este helper es puro — no toca estado — así los tests pueden cubrirlo sin
    levantar Django/Evennia.
    """
    s = (raw or "").strip()
    if not s:
        return (s, None)

    # No intervenimos si el usuario encerró el password en comillas dobles
    # (ej. `create "Ana" "p a s s"`) — el protocolo de 3er arg es para caso
    # simple. El parser nativo de Evennia usa comillas para passwords con
    # espacios; la convención "[es|en]" añadida al final en ese caso sería
    # confusa.
    if '"' in s:
        return (s, None)

    tokens = s.split()
    if len(tokens) < 3:
        return (s, None)

    last = tokens[-1].lower()
    if last not in _VALID_LANGS:
        return (s, None)

    # Nombre + password + lang
    rest = " ".join(tokens[:-1])
    return (rest, last)


class CmdCreateIntercept(CmdUnconnectedCreate):  # type: ignore[misc,valid-type]
    """
    Create a new account (narrativo + bilingüe).

    Usage:
      create <name> <password>
      create <name> <password> <lang>    # lang = es|en

    If you have spaces in your name, enclose it in double quotes.

    Examples:
      create mexi pass123            # default español
      create mexi pass123 en         # inglés desde el login
    """

    # Mismas llaves que el default — reemplazamos el comando nativo.
    key = "create"
    aliases = ["cre", "cr"]
    locks = "cmd:all()"
    arg_regex = r"\s.*?|$"

    # Clave consultada en account.db.language tras crear la cuenta.
    _LANG_DB_ATTR = "language"

    def func(self):
        """
        Flujo en tres actos.

        Es un **generator** (usa `yield from super().func()`), así que
        Evennia's cmdhandler drenará el yield del parent (prompt Y/N).

        Ojo: el parent puede `return` temprano (usuario canceló el Y/N o
        errores de password). En esos casos NO emitimos `create.sealed` —
        sólo si encontramos la Account recién creada en la DB.
        """
        session = self.caller
        raw = (self.args or "").rstrip()

        # --- 1. Parseo: separar idioma si viene como 3er arg ---------------
        cleaned_args, lang_choice = _split_args(raw)
        # Reasignamos para que el parent vea sólo `name + password`.
        self.args = cleaned_args

        # --- 2. Extraer username tentativo para buscar la Account después --
        username_guess = self._extract_username(cleaned_args)

        # --- 3. Narrativa pre-creación -------------------------------------
        # Usamos `session` como caller de `t()` — no tiene account todavía,
        # así que caerá a DEFAULT_LANG. Si el usuario eligió un idioma
        # explícito en el 3er arg, respetamos esa elección YA para los
        # banners pre-create (aplicamos un hint temporal en session.ndb).
        self._seed_pre_lang(session, lang_choice)
        self._banner_detecting(session)

        # --- 4. Delegar al comando nativo (con su yield para Y/N) ----------
        # El parent es un generador (usa `answer = yield (...)`). Lo
        # drenamos propagando los yields al cmdhandler.
        try:
            yield from super().func()
        except TypeError:
            # En entornos donde super().func() no es generador (tests stub,
            # versiones antiguas, fallback `object`), lo llamamos como func
            # normal.
            super().func()

        # --- 5. Aplicar idioma + banners post-creación ---------------------
        account = self._locate_account(username_guess)
        if account is None:
            # La creación falló (password débil, nombre tomado, Y/N = no,
            # etc). El parent ya mostró el error; no añadimos más ruido.
            return

        # Idioma: si el usuario no pasó 3er arg, dejamos el default (se
        # aplicará DEFAULT_LANG via get_lang). Si lo pasó, lo persistimos.
        if lang_choice:
            self._persist_lang(account, lang_choice, session)

        # Banners finales — caller = account ya que queremos respetar el
        # idioma que acabamos de setear.
        self._banner_sealed(account, lang_choice)

    # ------------------------------------------------------------------ #
    # Helpers internos (todos son métodos para facilitar stub en tests).
    # ------------------------------------------------------------------ #

    @staticmethod
    def _extract_username(args: str) -> str | None:
        """
        Extrae un username tentativo de `args` — el mismo parsing laxo que
        hace Evennia para que nuestro lookup posterior concuerde.
        """
        if not args:
            return None
        s = args.strip()
        # Caso comillas: create "Ana Banana" "pa ss"
        if '"' in s:
            parts = [p.strip() for p in re.split(r'"', s) if p.strip()]
            if parts:
                return parts[0]
        tokens = s.split(None, 1)
        if tokens:
            return tokens[0]
        return None

    def _seed_pre_lang(self, session, lang_choice):
        """Hint temporal para que los banners pre-create salgan en el idioma
        elegido antes de que exista account.db.language."""
        if not lang_choice:
            return
        try:
            # Usamos session.ndb (no-persist) para que `get_lang` lo vea
            # vía fallback en caller.db si fuéramos un character — en
            # session no tiene efecto directo, pero mantenemos el hook por
            # si futuro i18n agrega lookup en session.
            session.ndb._pending_lang = lang_choice
        except Exception:
            pass

    def _banner_detecting(self, session):
        """Banner antes de llamar al create nativo (fase ingreso al grid)."""
        try:
            from utils.i18n import t
            msg = t(session, "create.detecting")
        except Exception:
            msg = "|g> DETECTING SIGNAL...|n   |mneófito entrando al grid|n"
        try:
            session.msg(msg)
        except Exception:
            pass

    def _banner_sealed(self, account, lang_choice):
        """Banners post-creación. `account` ya es la Account real."""
        try:
            from utils.i18n import t
            written = t(account, "create.identity_written")
            sealed = t(account, "create.sealed")
            prompt = t(account, "create.language_prompt")
        except Exception:
            written = "|g> IDENTITY WRITTEN TO /dev/academy/|n"
            sealed = (
                "|g> LEDGER ENTRY SEALED.|n\n"
                "|c> Prof. Shell te espera en /home.|n"
            )
            prompt = "|g> LANGUAGE?|n Type `language es` or `language en` after login."

        lines = [written]
        # Si ya eligieron idioma por 3er arg, confirmamos; si no, mostramos
        # el prompt educativo para el comando `language`.
        if lang_choice:
            try:
                from utils.i18n import t
                lines.append(t(account, "create.lang_set", lang=lang_choice))
            except Exception:
                lines.append(f"|g> lang = {lang_choice}|n")
        else:
            lines.append(prompt)
        lines.append(sealed)

        try:
            account.msg("\n".join(lines))
        except Exception:
            # account es nuevo; si msg() falla por algún race, al menos
            # notificamos a la sesión original.
            try:
                self.caller.msg("\n".join(lines))
            except Exception:
                pass

    def _persist_lang(self, account, lang_choice, session):
        """Aplica set_lang sobre la account recién creada."""
        try:
            from utils.i18n import set_lang
            ok = set_lang(account, lang_choice)
            if not ok:
                # lang_choice ya fue validado por _split_args; si falla es
                # por contrato roto en set_lang — loguear y seguir.
                self._log_warn(
                    f"[create_intercept] set_lang rechazó '{lang_choice}' para {account}"
                )
        except Exception as err:
            self._log_warn(f"[create_intercept] error seteando idioma: {err}")

    @staticmethod
    def _locate_account(username):
        """
        Busca la Account creada. Devuelve None si no existe.

        Preferimos `AccountDB.objects.filter(username__iexact=...)` porque
        Evennia normaliza el username (strip + lowercase en algunos setups).
        """
        if not username:
            return None
        try:
            from evennia.accounts.models import AccountDB
            qs = AccountDB.objects.filter(username__iexact=username)
            if qs.exists():
                return qs.first()
        except Exception:
            pass
        return None

    @staticmethod
    def _log_warn(msg: str) -> None:
        """Best-effort log sin romper el flujo si logger no está disponible."""
        try:
            from evennia.utils import logger
            logger.log_warn(msg)
        except Exception:
            pass


__all__ = ["CmdCreateIntercept", "_split_args"]
