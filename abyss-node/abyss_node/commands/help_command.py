"""
CmdHelpCustom — reemplaza el `help` default de Evennia con una vista pensada
para principiantes de Monad Terminal Academy.

Estructura:
  - sección Terminal básico  (ls, pwd, cd, cat, touch, mkdir, grep)
  - sección Terminal interm. (echo/|/>/>>, head, tail, wc, whoami, man, history, clear)
  - sección Claude CLI       (claude, skills list/install, new contract, deploy)
  - sección Monad            (link, quests, claim)
  - '¿Cuál intento?' → recomienda la próxima quest pendiente leyendo QUESTS del
    módulo terminal_commands (19 quests actualmente).

En la room `claude_dojo` usa caller.db.installed_skills y
caller.db.deployed_contracts para sugerir el siguiente paso del flujo IA→onchain.
"""

from evennia import Command


TERMINAL_BASIC = [
    ("ls",          "lista el directorio actual"),
    ("pwd",         "imprime dónde estás"),
    ("cd <dir>",    "cambia de directorio (salida)"),
    ("cat <f>",     "muestra el contenido de un archivo"),
    ("touch <f>",   "crea un archivo vacío"),
    ("mkdir <d>",   "crea un directorio"),
    ("grep <pat> <f>", "busca texto en un archivo"),
]

TERMINAL_INTERMEDIATE = [
    ("echo <txt>",      "imprime texto (acepta `| wc`, `> file`, `>> file`)"),
    ("head [-n N] <f>", "primeras N líneas de un archivo"),
    ("tail [-n N] <f>", "últimas N líneas de un archivo"),
    ("wc <f>",          "cuenta líneas / palabras / chars"),
    ("whoami",          "tu usuario actual"),
    ("man <cmd>",       "manual de un comando"),
    ("history",         "tus últimos comandos"),
    ("clear",           "limpia la pantalla"),
]

CLAUDE_CMDS = [
    ("claude",                                "abre el CLI de IA (banner + ayuda)"),
    ("claude skills list",                    "ver skills disponibles"),
    ("claude skills installed",               "ver skills instalados"),
    ("claude skills install <owner/slug>",    "instala un skill"),
    ("claude new contract <Nombre>",          "genera <Nombre>.sol con IA"),
    ("claude deploy <file.sol>",              "simula deploy a Monad testnet"),
]

MONAD_CMDS = [
    ("link <0x...>", "vincula tu wallet EVM (Monad testnet)"),
    ("quests",       "muestra tus quests completadas y pendientes"),
    ("claim",        "recibe tus $TERM pendientes onchain"),
]

GENERAL_CMDS = [
    ("look / l",    "inspecciona la sala o un objeto"),
    ("say <msg>",   "habla en voz alta (prueba `say hola prof` en /home)"),
    ("help",        "este menú"),
]


def _pad(rows, width=None):
    """Renderiza pares (cmd, desc) alineados."""
    width = width or max(len(c) for c, _ in rows) + 1
    out = []
    for cmd, desc in rows:
        out.append(f"  |w{cmd.ljust(width)}|n  {desc}")
    return out


def _recommend_next(caller, quests):
    """
    Devuelve una línea 'próximo paso' adaptada al progreso del jugador.

    Reglas:
      1. Si hay quests pendientes por orden (q01→q19), sugerir la primera.
      2. Si está en `claude_dojo` y tiene quests del flujo Claude pendientes,
         priorizar ese flujo: install → new → deploy.
      3. Si todo completo, guiar a link/claim según wallet + pending.
    """
    try:
        from commands.terminal_commands import DEPLOY_ENABLING_SKILLS
    except Exception:
        DEPLOY_ENABLING_SKILLS = frozenset(("austin-griffith/monad-kit",))

    done = set(caller.db.quest_done or [])
    installed = list(caller.db.installed_skills or [])
    deployed = list(caller.db.deployed_contracts or [])
    wallet = caller.db.wallet or ""
    pending = int(caller.db.abyss_pending or 0)

    loc_key = (caller.location.key if caller.location else "") or ""
    has_deploy_skill = bool(set(installed) & DEPLOY_ENABLING_SKILLS)

    # Atajo contextual: si estás en claude_dojo, prioriza el flujo IA→onchain
    if loc_key == "claude_dojo":
        if not has_deploy_skill:
            return (
                "  Estás en |cclaude_dojo|n. Instala un kit con soporte de deploy:\n"
                "  |wclaude skills install portdeveloper/monad-development|n (oficial,\n"
                "  auto-verify en 3 explorers), o |waustin-griffith/monad-kit|n. (+40 $TERM)"
            )
        if not deployed:
            # ¿Tiene ya un .sol generado en este room?
            loc = caller.location
            room_files = (caller.db.fs_files or {}).get(loc.dbref, {}) if loc else {}
            has_sol = any(f.endswith(".sol") for f in room_files)
            if not has_sol:
                return (
                    "  Ya tienes skill instalado. Ahora genera un contrato:\n"
                    "  |wclaude new contract MiToken|n (+50 $TERM)"
                )
            sol_file = next(f for f in room_files if f.endswith(".sol"))
            return (
                f"  Ya generaste |w{sol_file}|n. Deploya a Monad testnet:\n"
                f"  |wclaude deploy {sol_file}|n (+60 $TERM)"
            )

    # Flujo general: siguiente quest pendiente por orden.
    next_quest = None
    for q in quests:
        if q["id"] not in done:
            next_quest = q
            break

    if next_quest:
        cmd = next_quest["cmd"]
        # Pretty-print para claude:* que son sub-quests
        if cmd.startswith("claude:"):
            sub = cmd.split(":", 1)[1]
            pretty = {
                "skill":  "claude skills install austin-griffith/monad-kit",
                "new":    "claude new contract MiToken",
                "deploy": "claude deploy MiToken.sol",
            }.get(sub, f"claude {sub}")
            return (
                f"  Próximo: |w{pretty}|n\n"
                f"  └─ {next_quest['desc']} (+|y{next_quest['reward']} $TERM|n)"
            )
        tip_by_cmd = {
            "ls":      "Tip: escribe |gls|n y presiona Enter.",
            "cd":      "Tip: mira las salidas con |gls|n, luego |gcd <nombre>|n.",
            "link":    "Tip: usa cualquier EVM address de 42 chars (0x...).",
            "echo":    "Tip: prueba |wecho hola mundo|n o con redirect |wecho x > file|n.",
            "head":    "Tip: |whead -n 3 log.txt|n (hay log.txt en pipe_dojo).",
            "tail":    "Tip: |wtail -n 3 log.txt|n (hay log.txt en pipe_dojo).",
            "wc":      "Tip: |wecho hola mundo | wc|n te cuenta líneas/palabras/bytes.",
            "man":     "Tip: |wman echo|n o |wman grep|n.",
            "history": "Tip: solo escribe |whistory|n (lista tus últimos comandos).",
            "claude":  "Tip: sólo escribe |wclaude|n (abre el CLI de IA).",
        }
        line = (
            f"  Próximo: |w{cmd}|n — {next_quest['desc']} "
            f"(+|y{next_quest['reward']} $TERM|n)"
        )
        if cmd in tip_by_cmd:
            line += f"\n  {tip_by_cmd[cmd]}"
        return line

    # Todo completo
    if not wallet:
        return (
            "  Todas las quests están |gcompletas|n. Ahora |wlink 0x...|n "
            "(tu wallet EVM) y luego |wclaim|n para recibir tus $TERM."
        )
    if pending > 0:
        return (
            f"  Todo listo: |y{pending} $TERM|n pendientes para |c{wallet[:10]}…|n. "
            f"Escribe |wclaim|n y recibes el tx hash."
        )
    return (
        "  Eres oficialmente |gshell-ninja|n graduade. "
        "Todas las quests reclamadas. Share en Discord."
    )


class CmdHelpCustom(Command):
    """
    Muestra ayuda de Monad Terminal Academy: comandos terminal (básico +
    intermedio), Claude CLI, comandos Monad y una recomendación contextual
    de la próxima quest pendiente (o del siguiente paso IA→onchain en
    claude_dojo).

    Usage:
      help
      ?
      ayuda
    """

    key = "help"
    aliases = ["?", "ayuda"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller

        # Import perezoso: terminal_commands lo edita Sesión A, no queremos
        # crear import circular a nivel módulo.
        try:
            from commands.terminal_commands import QUESTS
        except Exception:
            QUESTS = []

        done = set(caller.db.quest_done or [])
        wallet = caller.db.wallet or ""
        pending = int(caller.db.abyss_pending or 0)
        installed = list(caller.db.installed_skills or [])
        deployed = list(caller.db.deployed_contracts or [])

        lines = []
        lines.append("|g╭─ MONAD TERMINAL ACADEMY — help ────────────────────────────╮|n")
        lines.append("")
        lines.append("|yTerminal básico|n   (ls/pwd/cd/cat/touch/mkdir/grep)")
        lines.extend(_pad(TERMINAL_BASIC))
        lines.append("")
        lines.append("|yTerminal intermedio|n  (pipes |, redirects >/>>, etc.)")
        lines.extend(_pad(TERMINAL_INTERMEDIATE))
        lines.append("")
        lines.append("|yClaude CLI|n        (IA para generar y deployar código)")
        lines.extend(_pad(CLAUDE_CMDS))
        lines.append("")
        lines.append("|yMonad onchain|n")
        lines.extend(_pad(MONAD_CMDS))
        lines.append("")
        lines.append("|yGeneral|n")
        lines.extend(_pad(GENERAL_CMDS))
        lines.append("")

        # --- Recomendación contextual ---------------------------------
        lines.append("|c¿Cuál intento?|n")
        lines.append(_recommend_next(caller, QUESTS))
        lines.append("")

        # Estado compacto
        skills_line = (
            ", ".join(installed) if installed else "(ninguno — `claude skills install ...`)"
        )
        deploys_line = (
            f"{len(deployed)} deployado(s)" if deployed else "(ninguno — `claude deploy ...`)"
        )
        lines.append(
            f"  Progreso: |y{len(done)}/{len(QUESTS)}|n quests   "
            f"|y{pending} $TERM|n pendientes   "
            f"wallet: |c{wallet or '(sin linkear)'}|n"
        )
        lines.append(f"  Skills:   {skills_line}")
        lines.append(f"  Contratos: {deploys_line}")
        lines.append("|g╰─────────────────────────────────────────────────────────────╯|n")

        caller.msg("\n".join(lines))
