"""
Onboarding — comandos `tutorial` y `bitacora` pensados para los primeros 3
minutos mágicos de un player que nunca tocó una terminal.

- `tutorial` (sin args) muestra un índice narrativo de subtutoriales.
- `tutorial <tema>` abre un flujo guiado con scene() + dialogue() + narrate().
  Temas soportados: wallet, monad, shell, claim.
- `bitacora` (alias: `st`, `dashboard`) imprime un dashboard con progreso,
  wallet, $TERM pendientes y el próximo reto pendiente. No se llama
  `status` porque ese key pertenece al CmdStatus de combate (Sesión D).

Toda la salida pasa por los helpers de `utils.narrator` para respetar la
grammar visual (magenta-narrador, cyan-npc, amber-achievement).
"""

from __future__ import annotations

from evennia import Command

try:
    from utils.narrator import narrate, dialogue, scene
except Exception:  # pragma: no cover
    # Fallbacks si narrator no está disponible (tests aislados).
    def narrate(caller, text):
        caller.msg(text)
    def dialogue(caller, npc, text):
        caller.msg(f"{npc}: {text}")
    def scene(caller, title, body=""):
        caller.msg(f"=== {title} ===\n{body}")


# ---------------- Contenido de los subtutoriales --------------------------

def _tutorial_index(caller):
    """Índice de tutoriales disponibles."""
    scene(
        caller,
        "TUTORIALES — Prof. Shell",
        "Elige un tema. Cada uno son 30–60 segundos de lectura guiada.",
    )
    caller.msg(
        "\n"
        "  |wtutorial basics|n    — |yempezar desde cero|n (nunca usaste terminal)\n"
        "  |wtutorial windows|n   — si tienes Windows (PowerShell / CMD / WSL)\n"
        "  |wtutorial mac|n       — si tienes macOS (Terminal.app / iTerm2 / brew)\n"
        "  |wtutorial linux|n     — si tienes Linux (todo funciona copy-paste)\n"
        "  |wtutorial wallet|n    — configurar MetaMask con Monad testnet\n"
        "  |wtutorial monad|n     — por qué Monad + cómo funciona el faucet\n"
        "  |wtutorial shell|n     — repaso de comandos básicos\n"
        "  |wtutorial claim|n     — cómo recibir |y$TERM|n onchain\n"
        "\n"
        "  (también |wbitacora|n para ver tu progreso, |whelp <cmd>|n para "
        "detalles de un comando.)\n"
    )


def _tutorial_wallet(caller):
    """Guía de wallet → MetaMask → Monad testnet → link."""
    scene(
        caller,
        "TUTORIAL — WALLET",
        "Una wallet es tu identidad onchain. Es como un usuario "
        "que firma transacciones con criptografía en vez de password.",
    )
    dialogue(
        caller,
        "Prof. Shell",
        "Para recibir tus $TERM necesitas una dirección EVM. "
        "La más fácil de conseguir: MetaMask.",
    )
    narrate(
        caller,
        "Paso 1 — instala MetaMask en tu navegador (metamask.io) o "
        "abre la app móvil. Crea una wallet nueva si no tienes.",
    )
    narrate(
        caller,
        "Paso 2 — añade Monad testnet. Copia y pega esto "
        "en 'Añadir red → manual':",
    )
    caller.msg(
        "\n"
        "  |wRed:|n       Monad Testnet\n"
        "  |wChain ID:|n  10143\n"
        "  |wRPC URL:|n   https://testnet-rpc.monad.xyz\n"
        "  |wSímbolo:|n   MON\n"
        "  |wExplorer:|n  https://testnet.monadexplorer.com\n"
    )
    narrate(
        caller,
        "Paso 3 — copia tu address (empieza con 0x, tiene 42 caracteres). "
        "La ves arriba a la izquierda de MetaMask.",
    )
    dialogue(
        caller,
        "Prof. Shell",
        "De vuelta en la Academia, pega tu address con |wlink 0x...|n. "
        "Si tienes un ENS (.eth), también sirve: |wlink vitalik.eth|n.",
    )
    narrate(
        caller,
        "Cuando quieras reclamar tus $TERM acumulados, escribe |wclaim|n. "
        "El contrato transfiere los tokens a tu wallet.",
    )


def _tutorial_monad(caller):
    """Por qué Monad + faucet + cómo verificar una tx."""
    scene(
        caller,
        "TUTORIAL — MONAD",
        "Monad es una blockchain EVM-compatible con ejecución paralela. "
        "Apunta a 10.000 TPS, contrato-por-contrato idéntico a Ethereum.",
    )
    dialogue(
        caller,
        "Prof. Shell",
        "Testnet significa tokens sin valor real — perfecto para aprender. "
        "Cada cuenta recibe MON gratis desde el faucet.",
    )
    narrate(
        caller,
        "Faucet oficial: https://faucet.monad.xyz — conectas tu wallet, "
        "resuelves captcha y recibes MON para pagar gas.",
    )
    narrate(
        caller,
        "Para verificar cualquier tx: copia el hash y pégalo en "
        "https://testnet.monadexplorer.com. Verás confirmaciones, "
        "gas usado, eventos emitidos.",
    )
    dialogue(
        caller,
        "Prof. Shell",
        "En la Academia acumulas |y$TERM|n como recompensa por completar "
        "quests. Cuando uses |wclaim|n, eso es una tx real en Monad testnet.",
    )


def _tutorial_shell(caller):
    """Repaso de comandos básicos."""
    scene(
        caller,
        "TUTORIAL — SHELL",
        "La terminal es texto puro. Escribes un comando, pulsas Enter, "
        "el sistema responde. Nada más.",
    )
    dialogue(
        caller,
        "Prof. Shell",
        "Los 6 comandos que te abrirán cualquier terminal del mundo:",
    )
    caller.msg(
        "\n"
        "  |wls|n              — lista archivos y subdirectorios\n"
        "  |wpwd|n             — imprime el path actual\n"
        "  |wcd <dir>|n        — cambia de directorio\n"
        "  |wcat <archivo>|n   — muestra el contenido de un archivo\n"
        "  |wmkdir <nombre>|n  — crea un directorio\n"
        "  |wgrep <pat> <f>|n  — busca un patrón en un archivo\n"
    )
    dialogue(
        caller,
        "Prof. Shell",
        "Cada uno completa una quest la primera vez que lo usas. "
        "Escribe |wquests|n para ver tu progreso.",
    )
    narrate(
        caller,
        "Tip de supervivencia: si no sabes qué hacer, escribe |whelp|n sin "
        "argumentos. Te doy una pista adaptada a tu progreso.",
    )


def _tutorial_claim(caller):
    """Claim → onchain."""
    scene(
        caller,
        "TUTORIAL — CLAIM",
        "`claim` es el ritual final: convierte tus $TERM pendientes "
        "(acumulados por quests) en tokens reales en tu wallet.",
    )
    dialogue(
        caller,
        "Prof. Shell",
        "Dos requisitos antes de |wclaim|n:",
    )
    caller.msg(
        "\n"
        "  1. Tener una wallet linkeada — ejecuta |wlink 0x...|n primero.\n"
        "  2. Tener al menos 1 |y$TERM|n pendiente (gana completando quests).\n"
    )
    narrate(
        caller,
        "Al ejecutar |wclaim|n, el contrato ERC-20 transfiere tus tokens "
        "a la address linkeada. Recibes el tx hash y un link al explorer.",
    )
    dialogue(
        caller,
        "Prof. Shell",
        "Puedes hacer claim varias veces — cada vez recibes lo acumulado "
        "desde el último claim. Tus quests no se resetean.",
    )
    narrate(
        caller,
        "Si el contrato aún no está deployado, |wclaim|n te muestra un "
        "recibo pendiente con tu balance reservado para esa wallet.",
    )


def _tutorial_basics(caller):
    """Para quien nunca ha tocado una terminal. Desde cero absoluto."""
    scene(caller, "TUTORIAL · ¿QUÉ ES ESTO?",
          "Si nunca abriste una terminal en tu vida, este es tu punto de partida.")
    narrate(
        caller,
        "Una |wterminal|n es como una ventana del explorador de archivos "
        "(Windows Explorer, Finder de Mac), pero manejada con palabras en "
        "vez de clics. Tú tecleas una orden, presionas Enter, y el sistema "
        "te responde con texto.",
    )
    narrate(
        caller,
        "Tres conceptos básicos:\n"
        " 1. |wComando|n: una palabra que le dice al sistema qué hacer. "
        "Ej: |wls|n significa \"muéstrame qué hay aquí\".\n"
        " 2. |wDirectorio|n: lo mismo que una carpeta. Los comandos "
        "trabajan dentro del directorio donde estás parado.\n"
        " 3. |wPrompt|n: la línea que termina en |w$|n. Ahí escribes.",
    )
    narrate(
        caller,
        "En este juego las salas SON directorios, los items SON archivos. "
        "Cuando te muevas con |wcd|n te movés a otro cuarto. "
        "Cuando leas con |wcat|n lees un archivo real.",
    )
    dialogue(
        caller,
        "Prof. Shell",
        "No hay manera de \"romperlo\", Neófito. Si te equivocas, el sistema "
        "te lo dirá y podrás intentar otra vez. Aquí nada es permanente — "
        "salvo los $TERM que ganes onchain."
    )
    narrate(
        caller,
        "Tu primer comando: teclea |wls|n y presiona |wEnter|n. Ya está. "
        "Si quieres orientarte por sistema operativo (Windows / Mac / Linux), "
        "corre |wtutorial windows|n, |wtutorial mac|n o |wtutorial linux|n.",
    )


def _tutorial_windows(caller):
    """Para Windows users. Muestra equivalencias y cómo abrir la terminal real."""
    scene(caller, "TUTORIAL · WINDOWS",
          "Cómo llevar lo que aprendes aquí a tu máquina Windows real.")
    narrate(
        caller,
        "Windows tiene DOS terminales. La que te recomendamos es "
        "|wPowerShell|n (moderna). La otra es |wCMD|n (clásica, más vieja).",
    )
    narrate(
        caller,
        "|yPara abrir PowerShell:|n\n"
        "  1. Presiona |wWin + R|n (abre \"Ejecutar\").\n"
        "  2. Teclea |wpowershell|n y dale Enter.\n"
        "  3. Aparece una ventana con fondo azul oscuro y un prompt con |w>|n.",
    )
    narrate(
        caller,
        "|yBuena noticia:|n PowerShell acepta varios de los comandos Unix "
        "que aprendes aquí como alias nativos. Estos funcionan igual:\n"
        "  |wls|n  |wcd|n  |wpwd|n  |wcat|n  |wecho|n  |wclear|n",
    )
    narrate(
        caller,
        "|yCMD clásico|n usa otros nombres. Tabla de equivalencias:\n"
        "  |wls|n        → |wdir|n\n"
        "  |wcat|n       → |wtype|n\n"
        "  |wpwd|n       → |wcd|n (sin argumentos)\n"
        "  |wgrep|n      → |wfindstr|n\n"
        "  |wrm|n        → |wdel|n\n"
        "  |wcp|n        → |wcopy|n\n"
        "  |wmv|n        → |wmove|n",
    )
    dialogue(
        caller,
        "Prof. Shell",
        "Si tienes Windows 10/11, puedes instalar |wWSL|n (Windows Subsystem "
        "for Linux) desde Microsoft Store. Te da una terminal Linux COMPLETA "
        "dentro de Windows — y todo lo que aprendes aquí funciona copy-paste. "
        "Es lo que yo uso."
    )
    narrate(
        caller,
        "|yInstalar Claude Code en Windows:|n\n"
        "  |wnpm install -g @anthropic-ai/claude-code|n (si tienes Node)\n"
        "  o en PowerShell: |wirm https://claude.ai/install.ps1 | iex|n\n"
        "Prueba esos dos comandos en la Academia primero (|wcd install_dojo|n).",
    )


def _tutorial_mac(caller):
    """Para macOS users. Quick win: todos los comandos funcionan idéntico."""
    scene(caller, "TUTORIAL · macOS",
          "Tu Mac ya trae todo lo que necesitas. Lo único nuevo: dónde está.")
    narrate(
        caller,
        "macOS usa por default |wzsh|n (antes era bash). Ambas entienden "
        "TODOS los comandos de la Academia idénticos — sin cambios.",
    )
    narrate(
        caller,
        "|yPara abrir la terminal:|n\n"
        "  Opción 1: |wCmd + Espacio|n, teclea \"Terminal\", Enter.\n"
        "  Opción 2: Finder → Aplicaciones → Utilidades → Terminal.\n"
        "  Pro tip: instala |wiTerm2|n (iterm2.com) — es mejor y gratis.",
    )
    narrate(
        caller,
        "|yComandos que funcionan 1:1 desde aquí a tu Mac:|n\n"
        "  ls, cd, pwd, cat, touch, mkdir, grep, echo, head, tail, wc, man,\n"
        "  history, clear — todos idénticos.",
    )
    dialogue(
        caller,
        "Prof. Shell",
        "Si te preguntan por Homebrew (|wbrew|n): es un gestor de paquetes "
        "para instalar herramientas en Mac. Instálalo de brew.sh con un "
        "sólo comando. Una vez instalado, |wbrew install node|n te da Node "
        "para poder hacer |wnpm install -g ...|n igual que aquí."
    )
    narrate(
        caller,
        "|yInstalar Claude Code en Mac:|n\n"
        "  |wnpm install -g @anthropic-ai/claude-code|n\n"
        "  o: |wcurl -fsSL https://claude.ai/install.sh | bash|n\n"
        "Los practicas aquí en |wcd install_dojo|n y los corres igual en tu Mac.",
    )


def _tutorial_linux(caller):
    """Para Linux users. También funciona copy-paste."""
    scene(caller, "TUTORIAL · LINUX",
          "La Academia habla tu idioma nativo. Bienvenido a casa.")
    narrate(
        caller,
        "Si usas Linux ya sabes lo básico. Todo lo que aprendas aquí "
        "funciona 1:1 en tu máquina — sin traducción.",
    )
    narrate(
        caller,
        "|yPara abrir la terminal:|n\n"
        "  Ubuntu/Debian/Mint: |wCtrl + Alt + T|n\n"
        "  Arch/Manjaro: depende del desktop environment\n"
        "  Fedora: Super key → teclea \"Terminal\" → Enter",
    )
    narrate(
        caller,
        "|yShells comunes:|n bash (default en la mayoría), zsh, fish. "
        "Los comandos que enseña la Academia son |wPOSIX|n, funcionan "
        "en cualquiera de ellos.",
    )
    dialogue(
        caller,
        "Prof. Shell",
        "Bonus: si usas Linux y quieres Claude Code, usa "
        "|wcurl -fsSL https://claude.ai/install.sh | bash|n — es el "
        "mismo comando que simulas en |wcd install_dojo|n aquí adentro."
    )
    narrate(
        caller,
        "|yTip:|n para que los comandos hagan auto-completar con Tab como "
        "en la Academia, tu shell ya lo hace. Prueba en tu terminal: "
        "teclea |wc|n y dale Tab — verás los comandos que empiezan con 'c'.",
    )


TUTORIAL_TOPICS = {
    "basics": _tutorial_basics,
    "basico": _tutorial_basics,
    "windows": _tutorial_windows,
    "win": _tutorial_windows,
    "mac": _tutorial_mac,
    "macos": _tutorial_mac,
    "linux": _tutorial_linux,
    "wallet": _tutorial_wallet,
    "monad": _tutorial_monad,
    "shell": _tutorial_shell,
    "claim": _tutorial_claim,
}


# ---------------- Comando: tutorial ---------------------------------------

class CmdTutorial(Command):
    """
    Tutoriales guiados para los primeros minutos en la Academia.

    Usage:
      tutorial                 — muestra el índice de subtemas
      tutorial basics          — DESDE CERO si nunca usaste terminal
      tutorial windows|mac|linux — guía por sistema operativo
      tutorial wallet          — configurar MetaMask + Monad testnet
      tutorial monad           — qué es Monad y cómo funciona el faucet
      tutorial shell           — repaso de comandos básicos
      tutorial claim           — cómo recibir $TERM onchain

    Cada subtema es narrativo y no consume ninguna quest. Puedes repetirlo
    las veces que quieras. Si te sientes perdide, arranca con `tutorial
    shell`.
    """

    key = "tutorial"
    aliases = ["tutoriales", "guia"]
    locks = "cmd:all()"
    help_category = "Onboarding"

    def func(self):
        caller = self.caller
        arg = (self.args or "").strip().lower()

        if not arg:
            _tutorial_index(caller)
            return

        # Aceptar prefijos parciales: `tutorial wa` → wallet
        topic = None
        for key in TUTORIAL_TOPICS:
            if key == arg or key.startswith(arg):
                topic = key
                break
        if topic is None:
            caller.msg(
                f"tutorial: tema desconocido '{arg}'.\n"
                f"Opciones: |w{', '.join(TUTORIAL_TOPICS.keys())}|n."
            )
            return
        TUTORIAL_TOPICS[topic](caller)


# ---------------- Comando: status -----------------------------------------

# Determina cuál es el Acto I/II/III según quest_done.
ACT_I_QUESTS = {"q01_ls", "q02_pwd", "q03_cd", "q04_cat", "q08_echo", "q09_whoami"}
ACT_II_QUESTS = {
    "q05_mkdir", "q06_touch", "q07_grep",
    "q10_head", "q11_tail", "q12_wc", "q13_man", "q14_history",
}
ACT_III_QUESTS = {
    "q15_claude", "q16_skill", "q17_newcontract", "q18_deploy",
    "q20_node", "q21_install_claude", "q22_install_openclaw", "q23_install_hermes",
    "q19_link",
}


def _current_act(done: set) -> str:
    """Determina el acto narrativo actual según progreso."""
    act1_done = ACT_I_QUESTS.issubset(done)
    act2_done = act1_done and ACT_II_QUESTS.issubset(done)
    if act2_done:
        return "III — Ascensión"
    if act1_done:
        return "II — Entrenamiento"
    return "I — Despertar"


def _next_challenge(caller) -> tuple[str, str]:
    """
    Devuelve (short_cmd, detail) del próximo reto pendiente según QUESTS.
    Si todo está completo, guía hacia link/claim.
    """
    try:
        from commands.terminal_commands import QUESTS
    except Exception:
        QUESTS = []

    done = set(caller.db.quest_done or [])
    wallet = caller.db.wallet or ""
    pending = int(caller.db.abyss_pending or 0)

    for q in QUESTS:
        if q["id"] not in done:
            cmd = q["cmd"]
            # Sub-quests con prefijo claude: o install: muestran algo legible
            pretty = {
                "claude:skill": "claude skills install portdeveloper/monad-development",
                "claude:new": "claude new contract MiToken",
                # `verify:claude` reemplaza a `claude:deploy` — ahora la
                # quest sólo se completa con un deploy REAL verificado onchain.
                "verify:claude": "verify claude <tx-hash>  (deployá con claude real primero)",
                "claude:deploy": "claude deploy MiToken.sol",
                "install:claude": "curl -fsSL https://claude.ai/install.sh | bash",
                "install:openclaw": "curl -fsSL https://openclaw.ai/install.sh | bash",
                "install:hermes": "curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash",
            }.get(cmd, cmd)
            return pretty, q["desc"]

    # Todo done
    if not wallet:
        return "link 0x...", "Conecta tu wallet EVM para reclamar."
    if pending > 0:
        return "claim", f"Reclama {pending} $TERM en Monad testnet."
    return "(todo listo)", "Eres oficialmente shell-ninja."


def _box(title: str, rows: list[str], width: int = 48) -> list[str]:
    """
    Devuelve líneas con box-drawing. Respeta el ancho interior (width)
    y aplica color amarillo al borde.
    """
    top = "|y┌─ " + title + " " + "─" * max(0, width - len(title) - 3) + "┐|n"
    bot = "|y└" + "─" * (width + 1) + "┘|n"
    out = [top]
    for r in rows:
        # Calcular padding visible ignorando tags de color |x|
        from evennia.utils.ansi import strip_ansi
        import re
        visible = re.sub(r"\|[a-zA-Z#*][0-9a-fA-F]?", "", strip_ansi(r))
        pad = max(0, width - len(visible))
        out.append(f"|y│|n {r}{' ' * pad}|y│|n")
    out.append(bot)
    return out


class CmdBitacora(Command):
    """
    Bitácora — dashboard con progreso, wallet, $TERM y próximo reto.

    Usage:
      bitacora
      st
      dashboard

    Muestra en un solo pantallazo:
      - Acto narrativo actual (I, II, III)
      - Quests completadas / totales
      - $TERM pendientes
      - Próximo reto sugerido
      - Estado de la wallet

    Nota: `status` (sin args) muestra HP/combate de Sesión D. Este comando
    es el dashboard de Terminal Academy — más narrativo, sin stats de combate.
    """

    key = "bitacora"
    aliases = ["st", "dashboard", "progress"]
    locks = "cmd:all()"
    help_category = "Onboarding"

    def func(self):
        caller = self.caller
        try:
            from commands.terminal_commands import QUESTS
        except Exception:
            QUESTS = []

        done = set(caller.db.quest_done or [])
        total = len(QUESTS) if QUESTS else 23
        pending = int(caller.db.abyss_pending or 0)
        wallet = caller.db.wallet or ""
        ens = caller.db.wallet_ens or ""

        name = (
            caller.db.narrative_name
            or caller.key
            or "neofite"
        )
        act = _current_act(done)
        next_cmd, next_desc = _next_challenge(caller)

        wallet_disp = (
            f"|c{wallet[:10]}…{wallet[-4:]}|n" + (f" ({ens})" if ens else "")
            if wallet
            else "|x(sin linkear)|n"
        )

        # Filas del dashboard
        rows = [
            f"|wActo actual:|n {act}",
            f"|wQuests:|n     |y{len(done)}/{total}|n · |y$TERM pendientes: {pending}|n",
            f"|wPróximo:|n    |w{next_cmd}|n",
            f"|x              {next_desc}|n",
            f"|wWallet:|n     {wallet_disp} · Monad testnet",
        ]

        title = f"Bitácora de {name}"
        for line in _box(title, rows, width=52):
            caller.msg(line)

        # Tip contextual si están atorados sin wallet y ya ganaron $TERM
        if pending > 0 and not wallet:
            caller.msg(
                "\n  |yTienes $TERM listos|n — conecta tu wallet con "
                "|wlink 0x...|n o mira |wtutorial wallet|n."
            )
