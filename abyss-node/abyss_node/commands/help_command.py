"""
CmdHelpCustom — reemplaza el `help` default de Evennia con una vista pensada
para principiantes de Monad Terminal Academy.

Dos modos:

  help                — Prof. Shell te da una sugerencia de próxima quest
                        + resumen de categorías de comandos disponibles.

  help <cmd>          — explica ese comando con ejemplo real + tip narrativo
                        de 1–2 líneas en tono de Prof. Shell.

Los comandos cubiertos incluyen ls, cd, cat, grep, echo, touch, mkdir, head,
tail, wc, whoami, man, history, clear, claude (+ subcommands), link, claim,
quests, tutorial, bitacora.
"""

from evennia import Command

try:
    from utils.narrator import dialogue, narrate
except Exception:  # pragma: no cover — fallback si narrator no cargó
    def dialogue(caller, npc, text):
        caller.msg(f"{npc}: {text}")
    def narrate(caller, text):
        caller.msg(text)


TERMINAL_BASIC = [
    ("ls",             "lista el directorio actual"),
    ("pwd",            "imprime dónde estás"),
    ("cd <dir>",       "cambia de directorio (salida)"),
    ("cat <f>",        "muestra el contenido de un archivo"),
    ("touch <f>",      "crea un archivo vacío"),
    ("mkdir <d>",      "crea un directorio"),
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
    ("claude",                             "abre el CLI de IA (banner + ayuda)"),
    ("claude skills list",                 "ver skills disponibles"),
    ("claude skills installed",            "ver skills instalados"),
    ("claude skills install <owner/slug>", "instala un skill"),
    ("claude new contract <Nombre>",       "genera <Nombre>.sol con IA"),
    ("claude deploy <file.sol>",           "simula deploy a Monad testnet"),
]

MONAD_CMDS = [
    ("link <0x...>", "vincula tu wallet EVM (Monad testnet)"),
    ("quests",       "muestra tus quests completadas y pendientes"),
    ("claim",        "recibe tus $TERM pendientes onchain"),
]

ONBOARDING_CMDS = [
    ("tutorial",       "índice de tutoriales guiados"),
    ("tutorial wallet", "cómo conectar MetaMask con Monad testnet"),
    ("tutorial monad",  "qué es Monad + cómo usar el faucet"),
    ("tutorial shell",  "repaso de comandos básicos"),
    ("bitacora",        "dashboard con progreso, $TERM y próximo reto"),
]

GENERAL_CMDS = [
    ("look / l",  "inspecciona la sala o un objeto"),
    ("say <msg>", "habla en voz alta (prueba `say hola prof` en /home)"),
    ("help",      "este menú · `help <cmd>` explica un comando"),
]


# ------------ Entradas de ayuda por comando individual --------------------
#
# Cada entry es (explicación, ejemplo, tip_narrativo).

HELP_ENTRIES = {
    "ls": (
        "Lista archivos y subdirectorios del directorio actual. En la Academia,\n"
        "las salidas de la sala son subdirectorios y los items visibles son archivos.",
        "ls",
        "Tip: escribe |gls|n y presiona Enter. Es el primer comando que tecleaste al despertar.",
    ),
    "pwd": (
        "Imprime la ruta del directorio (sala) en que estás.\n"
        "Útil cuando te pierdes entre varios `cd`.",
        "pwd",
        "Tip: si dudas de dónde estás, |wpwd|n te sitúa en el mapa.",
    ),
    "cd": (
        "Cambia de directorio. En la Academia equivale a moverte entre salas.\n"
        "`cd ..` regresa al anterior; `cd -` vuelve al último dir que visitaste.",
        "cd ls_dojo",
        "Tip: primero |gls|n para ver las salidas, luego |gcd <nombre>|n.",
    ),
    "cat": (
        "Imprime el contenido completo de un archivo. Los archivos de la Academia\n"
        "a veces esconden fragmentos de memoria perdida.",
        "cat README.txt",
        "Tip: los cantos del filesystem son `cat`. Escucha lo que los archivos dicen.",
    ),
    "touch": (
        "Crea un archivo vacío en el directorio actual. Útil para ensayar\n"
        "combinaciones con `echo >` y `echo >>`.",
        "touch notas.txt",
        "Tip: un archivo vacío es potencial puro — luego llénalo con |wecho ... > notas.txt|n.",
    ),
    "mkdir": (
        "Crea un subdirectorio real — Evennia lo instancia como room con salidas\n"
        "ida/vuelta. Podés entrar con `cd <nombre>` y volver con `cd ..`.",
        "mkdir experimentos",
        "Tip: la magia de `mkdir` — cada directorio es un lugar nuevo en el mundo.",
    ),
    "grep": (
        "Busca un patrón en un archivo. En Terminal Academy es tu herramienta\n"
        "para encontrar tokens ocultos entre líneas de ruido.",
        "grep TOKEN crypto_log.txt",
        "Tip: piensa en |wgrep|n como un radar: ignora todo lo que no coincide.",
    ),
    "echo": (
        "Imprime texto. Con `>` lo escribes a archivo, con `>>` lo añades,\n"
        "con `|` envías el output a otro comando (wc, grep, head, tail).",
        "echo hola mundo > saludo.txt",
        "Tip: |wecho|n es la voz de la shell. Lo que digas aquí queda escrito.",
    ),
    "head": (
        "Muestra las primeras N líneas de un archivo (10 por defecto).\n"
        "Con `-n N` eliges cuántas.",
        "head -n 5 log.txt",
        "Tip: cuando los archivos son enormes, |whead|n te dice cómo empiezan.",
    ),
    "tail": (
        "Muestra las últimas N líneas (10 por defecto). Con `-n N` eliges cuántas.\n"
        "Útil para logs: el final suele tener lo más reciente.",
        "tail -n 5 log.txt",
        "Tip: |wtail|n lee el final — lo último que el sistema susurró antes de dormir.",
    ),
    "wc": (
        "Cuenta líneas, palabras y bytes. Con `-l`, `-w`, `-c` te da solo uno.\n"
        "También sirve en pipes: `echo ... | wc -l`.",
        "wc -l mensaje.txt",
        "Tip: |wwc|n pesa los archivos. Es el primer paso para muchos puzzles.",
    ),
    "whoami": (
        "Imprime tu nombre de usuario. En la Academia confirma tu identidad\n"
        "recuperada — el Corruptor quiso borrarla, pero sobreviviste.",
        "whoami",
        "Tip: cuando dudes de quién eres, |wwhoami|n responde. Literalmente.",
    ),
    "man": (
        "Páginas de manual — documentación formal de un comando.\n"
        "Formato clásico Unix: NAME, USAGE, DESCRIPTION.",
        "man grep",
        "Tip: los manuales son los libros sagrados del Profesor Shell. Léelos.",
    ),
    "history": (
        "Lista los comandos que ejecutaste en esta cuenta (últimos 200).\n"
        "Opcionalmente `history <N>` muestra solo los últimos N.",
        "history 10",
        "Tip: tu historial es memoria persistente — úsalo para no repetir errores.",
    ),
    "clear": (
        "Limpia la pantalla enviando saltos de línea al cliente.\n"
        "En la webshell y telnet funciona visualmente aunque no borre buffer real.",
        "clear",
        "Tip: cuando el ruido acumulado te abruma, |wclear|n es aire limpio.",
    ),
    "link": (
        "Conecta tu wallet EVM (0x... o ENS .eth) para recibir $TERM.\n"
        "Requerido antes de `claim`.",
        "link 0x1234abcd5678ef901234abcd5678ef901234abcd",
        "Tip: si nunca configuraste una wallet, corre primero |wtutorial wallet|n.",
    ),
    "quests": (
        "Lista tus quests completadas (✓) y pendientes (·) con sus recompensas\n"
        "en $TERM. Es la manera rápida de saber cuánto te falta.",
        "quests",
        "Tip: |wquests|n es tu mapa completo — |wstatus|n es el resumen ejecutivo.",
    ),
    "claim": (
        "Reclama tus $TERM pendientes. Requiere wallet linkeada.\n"
        "Cuando el contrato está deployado, ejecuta una transferencia real en Monad.",
        "claim",
        "Tip: |wclaim|n es el ritual onchain que graba tu identidad para siempre.",
    ),
    "claude": (
        "CLI de IA para generar código, instalar skills y simular deploys.\n"
        "Flujo pedagógico: `skills install` → `new contract` → `deploy`.",
        "claude skills install portdeveloper/monad-development",
        "Tip: |wclaude|n sin args te muestra el banner y los subcomandos.",
    ),
    "tutorial": (
        "Tutoriales guiados con tono de Prof. Shell. Temas: wallet, monad,\n"
        "shell, claim. Sin args muestra el índice.",
        "tutorial wallet",
        "Tip: si llevas más de 30 segundos sin saber qué hacer, prueba |wtutorial shell|n.",
    ),
    "bitacora": (
        "Dashboard en caja con tu progreso: acto actual, quests hechas, $TERM\n"
        "pendientes, próximo reto y estado de la wallet.",
        "bitacora",
        "Tip: |wbitacora|n es tu brújula. Úsalo cada vez que te sientas perdide.",
    ),
    "status": (
        "Sin args, muestra tu status de combate (HP, stats). Para el dashboard\n"
        "de la Academia con progreso de quests, usa |wbitacora|n.",
        "status",
        "Tip: |wstatus|n = combate, |wbitacora|n = progreso narrativo.",
    ),
    "look": (
        "Inspecciona tu entorno o un objeto. Es el comando nativo de Evennia\n"
        "(no de Unix) — equivale a mirar alrededor.",
        "look npc",
        "Tip: a diferencia de `ls`, |wlook|n te cuenta la historia del room.",
    ),
    "say": (
        "Habla en voz alta. Los NPCs responden a saludos en lenguaje natural.\n"
        "Prueba `say hola prof` cerca del Prof. Shell.",
        "say hola prof",
        "Tip: |wsay|n es magia — los NPCs te responden según tu progreso.",
    ),
    "help": (
        "Sin args, Prof. Shell te sugiere tu próxima quest pendiente.\n"
        "Con args (`help ls`), explica ese comando con ejemplo + tip narrativo.",
        "help cat",
        "Tip: si nada te cuadra, escribe |whelp|n sin args. El Profe te guía.",
    ),
}


# ---------- Aliases a la entrada principal (para que `help l` funcione)
HELP_ALIASES = {
    "l": "look",
    "ayuda": "help",
    "dir": "ls",
    "cls": "clear",
    "st": "bitacora",
    "dashboard": "bitacora",
    "progress": "bitacora",
    "wallet": "link",
    "q": "quests",
    "guia": "tutorial",
    "tutoriales": "tutorial",
}


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
    """
    try:
        from commands.terminal_commands import DEPLOY_ENABLING_SKILLS
    except Exception:
        DEPLOY_ENABLING_SKILLS = frozenset(("portdeveloper/monad-development",))

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
                "  auto-verify en 3 explorers). (+40 $TERM)"
            )
        if not deployed:
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

    next_quest = None
    for q in quests:
        if q["id"] not in done:
            next_quest = q
            break

    if next_quest:
        cmd = next_quest["cmd"]
        if cmd.startswith("claude:"):
            sub = cmd.split(":", 1)[1]
            pretty = {
                "skill":  "claude skills install portdeveloper/monad-development",
                "new":    "claude new contract MiToken",
                "deploy": "claude deploy MiToken.sol",
            }.get(sub, f"claude {sub}")
            return (
                f"  Próximo: |w{pretty}|n\n"
                f"  └─ {next_quest['desc']} (+|y{next_quest['reward']} $TERM|n)"
            )
        if cmd.startswith("install:"):
            sub = cmd.split(":", 1)[1]
            pretty = {
                "claude":   "curl -fsSL https://claude.ai/install.sh | bash",
                "openclaw": "curl -fsSL https://openclaw.ai/install.sh | bash",
                "hermes":   "curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash",
            }.get(sub, cmd)
            return (
                f"  Próximo: |w{pretty}|n\n"
                f"  └─ {next_quest['desc']} (+|y{next_quest['reward']} $TERM|n)"
            )
        tip_by_cmd = {
            "ls":      "Tip: escribe |gls|n y presiona Enter.",
            "cd":      "Tip: mira las salidas con |gls|n, luego |gcd <nombre>|n.",
            "link":    "Tip: usa cualquier EVM address de 42 chars (0x...). O |wtutorial wallet|n.",
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
            "(tu wallet EVM) y luego |wclaim|n para recibir tus $TERM.\n"
            "  Tip: si no sabes cómo, prueba |wtutorial wallet|n."
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


def _help_specific(caller, cmd_name: str):
    """Busca `cmd_name` en HELP_ENTRIES (resuelve aliases) y emite explicación."""
    key = cmd_name.lower().strip()
    key = HELP_ALIASES.get(key, key)
    entry = HELP_ENTRIES.get(key)

    if entry is None:
        # Intento suave: prefijo
        matches = [k for k in HELP_ENTRIES if k.startswith(key)]
        if len(matches) == 1:
            entry = HELP_ENTRIES[matches[0]]
            key = matches[0]

    if entry is None:
        dialogue(
            caller,
            "Prof. Shell",
            f"No reconozco '|w{cmd_name}|n'. Prueba |whelp|n sin args, "
            "o |wman <comando>|n si existe en el manual.",
        )
        return

    explanation, example, tip = entry
    dialogue(caller, "Prof. Shell", f"Te explico |w{key}|n:")
    narrate(caller, explanation)
    caller.msg(f"\n  |xEjemplo:|n |w{example}|n\n")
    narrate(caller, tip)


class CmdHelpCustom(Command):
    """
    Prof. Shell te guía. Dos modos:

    Sin argumentos:
      help
      ?
      ayuda
        — muestra una sugerencia de próxima quest + lista de categorías
          (Terminal básico, intermedio, Claude CLI, Monad, Onboarding).

    Con argumento:
      help <comando>
        — explica ese comando con ejemplo real + tip narrativo.
          Ejemplos: help ls · help cat · help claude · help claim · help link.

    Consejo: si el output te abruma, |wstatus|n te da la versión corta.
    """

    key = "help"
    aliases = ["?", "ayuda"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        arg = (self.args or "").strip()

        # Modo 2 — `help <cmd>`
        if arg:
            _help_specific(caller, arg)
            return

        # Modo 1 — sin args: sugerencia contextual + menú
        try:
            from commands.terminal_commands import QUESTS
        except Exception:
            QUESTS = []

        done = set(caller.db.quest_done or [])
        wallet = caller.db.wallet or ""
        pending = int(caller.db.abyss_pending or 0)
        installed = list(caller.db.installed_skills or [])
        deployed = list(caller.db.deployed_contracts or [])

        # Sugerencia de Prof. Shell arriba de todo
        dialogue(
            caller,
            "Prof. Shell",
            "Déjame ver tu bitácora... aquí va tu próximo paso:",
        )
        caller.msg(_recommend_next(caller, QUESTS))
        caller.msg("")

        lines = []
        lines.append("|g╭─ MONAD TERMINAL ACADEMY — comandos ─────────────────────────╮|n")
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
        lines.append("|yOnboarding|n")
        lines.extend(_pad(ONBOARDING_CMDS))
        lines.append("")
        lines.append("|yGeneral|n")
        lines.extend(_pad(GENERAL_CMDS))
        lines.append("")
        lines.append("  Para detalles de un comando: |whelp <comando>|n  "
                     "(ej. |whelp ls|n, |whelp claim|n)")
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
