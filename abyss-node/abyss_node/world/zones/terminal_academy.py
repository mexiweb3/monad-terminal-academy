"""
Terminal Academy — zona tutorial.

Crea un "filesystem" navegable con 5 rooms que enseñan comandos básicos:
  /home (spawn) → /home/ls_dojo → /home/cd_dojo → /home/cat_dojo → /home/mkdir_dojo

Construcción desde shell de Evennia:
  @py from world.zones.terminal_academy import build_academy; build_academy(self)
"""

from evennia import create_object
from evennia.utils.search import search_object


ROOMS = [
    {
        "key": "home",
        "desc": (
            "Bienvenido a |gTerminal Academy|n.\n"
            "\n"
            "Estás en tu |cdirectorio home|n. Aquí aprenderás los comandos de una terminal real.\n"
            "Cada comando nuevo que aprendas te regala |y$TERM|n (token ERC-20 en Monad testnet).\n"
            "\n"
            "|yPrimer reto:|n escribe |wls|n y presiona Enter para listar este directorio.\n"
            "También puedes escribir |wquests|n en cualquier momento para ver tu progreso."
        ),
        "files": {
            "README.txt": (
                "MONAD TERMINAL ACADEMY\n"
                "----------------------\n"
                "Shell básico:\n"
                "  ls, pwd, cd, cat, touch, mkdir, grep\n"
                "Shell intermedio:\n"
                "  echo, head, tail, wc, whoami, man, history, clear\n"
                "  + pipes (|) y redirects (>, >>)\n"
                "Claude CLI (IA para generar código):\n"
                "  claude skills install austin-griffith/monad-kit\n"
                "  claude new contract MiToken\n"
                "  claude deploy MiToken.sol\n"
                "Onchain Monad:\n"
                "  link <wallet>   — conectar tu wallet EVM\n"
                "  quests          — ver tu progreso\n"
                "  claim           — recibir $TERM onchain\n"
                "\n"
                "Tip: escribe 'cat README.txt' para leer este archivo."
            ),
        },
        "exits": [("ls_dojo", "ls_dojo")],
    },
    {
        "key": "ls_dojo",
        "desc": (
            "|cls_dojo|n — aquí practicas el comando |wls|n.\n"
            "\n"
            "|wls|n lista los archivos y subdirectorios de tu ubicación actual.\n"
            "En este MUD, las salidas son tus |csubdirectorios|n y los objetos son tus archivos.\n"
            "\n"
            "|yReto:|n escribe |wls|n. Luego muévete al siguiente con |wcd cd_dojo|n."
        ),
        "files": {
            "hint.txt": "Siguiente: 'cd cd_dojo'",
        },
        "exits": [("home", "home"), ("cd_dojo", "cd_dojo")],
    },
    {
        "key": "cd_dojo",
        "desc": (
            "|ccd_dojo|n — practica |wpwd|n y |wcd|n.\n"
            "\n"
            "|wpwd|n = print working directory (dónde estás).\n"
            "|wcd <destino>|n = change directory. Usa |wcd ..|n para volver atrás.\n"
            "\n"
            "|yReto:|n escribe |wpwd|n para ver dónde estás, luego |wcd cat_dojo|n."
        ),
        "files": {},
        "exits": [("ls_dojo", "ls_dojo"), ("cat_dojo", "cat_dojo")],
    },
    {
        "key": "cat_dojo",
        "desc": (
            "|ccat_dojo|n — practica |wcat|n.\n"
            "\n"
            "|wcat <archivo>|n imprime el contenido de un archivo.\n"
            "\n"
            "|yReto:|n en este directorio hay un archivo |wsecret.txt|n. Léelo con |wcat secret.txt|n."
        ),
        "files": {
            "secret.txt": (
                "¡Muy bien! Acabas de aprender 'cat'.\n"
                "Secreto: cada comando nuevo que aprendes te da $TERM en Monad testnet.\n"
                "Siguiente: escribe 'cd mkdir_dojo'."
            ),
        },
        "exits": [("cd_dojo", "cd_dojo"), ("mkdir_dojo", "mkdir_dojo")],
    },
    {
        "key": "mkdir_dojo",
        "desc": (
            "|cmkdir_dojo|n — practica |wmkdir|n, |wtouch|n y |wgrep|n.\n"
            "\n"
            "|wtouch <file>|n crea un archivo vacío.\n"
            "|wmkdir <dir>|n crea un directorio.\n"
            "|wgrep <patrón> <archivo>|n busca texto.\n"
            "\n"
            "|yReto:|n\n"
            "  1. |wtouch mi_nota.txt|n\n"
            "  2. |wmkdir mi_dir|n\n"
            "  3. |wgrep ABYSS README.txt|n (hay un README.txt aquí).\n"
            "\n"
            "Cuando termines, avanza con |wcd pipe_dojo|n."
        ),
        "files": {
            "README.txt": "Busca 'ABYSS' aquí con grep y gana tokens en MONAD testnet.",
        },
        "exits": [("cat_dojo", "cat_dojo"), ("pipe_dojo", "pipe_dojo"), ("home", "home")],
    },
    {
        "key": "pipe_dojo",
        "desc": (
            "|cpipe_dojo|n — practica el operador |w||n (pipe) y el comando |wecho|n.\n"
            "\n"
            "|wecho <texto>|n imprime texto en stdout.\n"
            "El pipe |w||n conecta el stdout de un comando con el stdin del siguiente.\n"
            "\n"
            "|yRetos:|n\n"
            "  1. |wecho hola mundo|n                (imprime hola mundo)\n"
            "  2. |wecho hola mundo | wc|n          (líneas palabras bytes)\n"
            "  3. |wecho hola mundo | grep hola|n   (filtra líneas con 'hola')\n"
            "  4. |wwhoami|n                         (descubre tu usuario)\n"
            "\n"
            "También aprende |whead|n y |wtail|n sobre el archivo |wlog.txt|n de este room.\n"
            "Siguiente: |wcd redirect_dojo|n."
        ),
        "files": {
            "log.txt": (
                "línea 01 — boot\n"
                "línea 02 — init\n"
                "línea 03 — mount /dev/fs\n"
                "línea 04 — load modules\n"
                "línea 05 — ready\n"
                "línea 06 — user logged in\n"
                "línea 07 — heartbeat\n"
                "línea 08 — heartbeat\n"
                "línea 09 — heartbeat\n"
                "línea 10 — heartbeat\n"
                "línea 11 — heartbeat\n"
                "línea 12 — shutdown requested\n"
            ),
            "pipe_cheatsheet.txt": (
                "Pipes que esta sala entiende:\n"
                "  echo TXT | wc            → líneas palabras bytes\n"
                "  echo TXT | grep PAT      → líneas que contienen PAT\n"
                "  echo TXT | head [-n N]   → primeras N líneas\n"
                "  echo TXT | tail [-n N]   → últimas N líneas\n"
            ),
        },
        "exits": [("mkdir_dojo", "mkdir_dojo"), ("redirect_dojo", "redirect_dojo")],
    },
    {
        "key": "redirect_dojo",
        "desc": (
            "|credirect_dojo|n — practica los redirects |w>|n y |w>>|n.\n"
            "\n"
            "|w>|n escribe el stdout a un archivo (sobreescribe si existe).\n"
            "|w>>|n hace append al final del archivo.\n"
            "\n"
            "|yRetos:|n\n"
            "  1. |wecho primera línea > mi.log|n\n"
            "  2. |wecho segunda línea >> mi.log|n\n"
            "  3. |wcat mi.log|n             (ves ambas)\n"
            "  4. |whead -n 1 mi.log|n\n"
            "  5. |wtail -n 1 mi.log|n\n"
            "  6. |wwc mi.log|n\n"
            "  7. |wman echo|n                (lee el manual de echo)\n"
            "\n"
            "Cuando tengas echo, head, tail, wc y man completados: |wcd final_exam|n."
        ),
        "files": {
            "redirect_cheatsheet.txt": (
                "Redirects soportados:\n"
                "  echo TXT > file    (write, sobreescribe)\n"
                "  echo TXT >> file   (append)\n"
                "El archivo se guarda en tu fs virtual del room actual.\n"
            ),
        },
        "exits": [("pipe_dojo", "pipe_dojo"), ("final_exam", "final_exam")],
    },
    {
        "key": "final_exam",
        "desc": (
            "|cfinal_exam|n — examen final de la Academia.\n"
            "\n"
            "Combina |wtres o más comandos|n para superar esta sala:\n"
            "\n"
            "|yRetos finales:|n\n"
            "  1. |wecho final check > exam.log|n\n"
            "     └─ redirect + echo\n"
            "  2. |wecho extra data >> exam.log|n\n"
            "     └─ append\n"
            "  3. |wcat exam.log|n\n"
            "     └─ leer\n"
            "  4. |wwc exam.log|n\n"
            "     └─ contar\n"
            "  5. |whead -n 1 exam.log|n     |wtail -n 1 exam.log|n\n"
            "  6. |wgrep final exam.log|n\n"
            "  7. |whistory|n\n"
            "     └─ revisa todos los comandos que ejecutaste\n"
            "\n"
            "Cuando completes todas las 15 quests (escribe |wquests|n para ver):\n"
            "  |wlink <tu_wallet_0x...>|n y |wclaim|n — recibe tus $TERM onchain.\n"
        ),
        "files": {
            "diploma.txt": (
                "MONAD TERMINAL ACADEMY — DIPLOMA\n"
                "--------------------------------\n"
                "Has aprendido:\n"
                "  ls, pwd, cd, cat, touch, mkdir, grep,\n"
                "  echo, head, tail, wc, whoami, man, history, clear,\n"
                "  + redirects (>, >>) + pipes (|).\n"
                "Ya puedes moverte como un hacker en cualquier terminal Unix.\n"
                "\n"
                "Ahora reclama tus $TERM: `link <wallet>` y `claim`.\n"
            ),
        },
        "exits": [("redirect_dojo", "redirect_dojo"), ("install_dojo", "install_dojo"), ("home", "home")],
    },
    {
        "key": "install_dojo",
        "desc": (
            "|cinstall_dojo|n — aprende a instalar herramientas CLI reales.\n"
            "\n"
            "Aquí practicas cómo se instalan los agentes que usarás en el siguiente dojo.\n"
            "Elige el método que coincida con tu sistema operativo:\n"
            "\n"
            "|yPaso 1|n — verifica que tienes Node.js:\n"
            "  |wnode --version|n   (debería responder v18+)\n"
            "\n"
            "|yPaso 2|n — instala |cClaude Code|n (de Anthropic) con CUALQUIERA de estos:\n"
            "  |w• npm install -g @anthropic-ai/claude-code|n    (cross-platform si hay Node)\n"
            "  |w• curl -fsSL https://claude.ai/install.sh | bash|n    (macOS / Linux)\n"
            "  |w• irm https://claude.ai/install.ps1 | iex|n    (Windows PowerShell)\n"
            "\n"
            "|yPaso 3|n — instala |cOpenClaw|n (framework open-source de agentes):\n"
            "  |w• curl -fsSL https://openclaw.ai/install.sh | bash|n\n"
            "  |w• (alt) npm i -g openclaw|n\n"
            "\n"
            "|yPaso 4|n — instala |cHermes|n (Nous Research):\n"
            "  |w• curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash|n\n"
            "\n"
            "Cada herramienta instalada te da |y+50 $TERM|n. Cuando termines → |wcd claude_dojo|n."
        ),
        "files": {
            "README.md": (
                "# Install Dojo\n"
                "\n"
                "## ¿Por qué este dojo existe?\n"
                "Todos los agentes de IA para coding (Claude Code, OpenClaw, Hermes)\n"
                "viven en la terminal. Antes de usarlos, tienes que instalarlos.\n"
                "\n"
                "## 3 métodos estándar, aprende los 3\n"
                "\n"
                "1. **npm global** — funciona en cualquier OS con Node.js instalado.\n"
                "     `npm install -g <paquete>`\n"
                "\n"
                "2. **Shell installer** (macOS / Linux) — un curl que descarga y ejecuta\n"
                "   un script. Es como un `.exe` para Unix.\n"
                "     `curl -fsSL <url> | bash`\n"
                "\n"
                "3. **PowerShell installer** (Windows) — el equivalente de Windows.\n"
                "   `irm` descarga, `iex` ejecuta.\n"
                "     `irm <url> | iex`\n"
                "\n"
                "## Tips para principiantes\n"
                "- El `-g` en npm = global (disponible en toda tu máquina).\n"
                "- `-fsSL` en curl = fail silently, show errors, follow redirects, location.\n"
                "- Si algo falla: `<bin> --version` te dice si está bien instalado.\n"
            ),
            "links.txt": (
                "Sitios oficiales (confía solo en estos):\n"
                "  Claude Code : https://claude.ai\n"
                "  OpenClaw    : https://openclaw.ai\n"
                "  Hermes      : https://hermes-agent.nousresearch.com\n"
            ),
        },
        "exits": [("final_exam", "final_exam"), ("claude_dojo", "claude_dojo"), ("home", "home")],
    },
    {
        "key": "claude_dojo",
        "desc": (
            "|cclaude_dojo|n — graduación: aprende a usar |wclaude|n (CLI de IA).\n"
            "\n"
            "Aquí no sólo moves archivos — ahora |wle pides a la IA que los genere|n.\n"
            "Claude puede instalar skills (como los de |yAustin Griffith|n para Scaffold-ETH\n"
            "o el Monad kit), generar contratos Solidity y simular deploy a Monad testnet.\n"
            "\n"
            "|yFlujo de graduación:|n\n"
            "  1. |wclaude|n                                            (ver menú CLI)\n"
            "  2. |wclaude skills list|n                                 (ver skills)\n"
            "  3. |wclaude skills install austin-griffith/monad-kit|n   (instalar)\n"
            "  4. |wclaude new contract MiPrimerToken|n                  (generar)\n"
            "  5. |wcat MiPrimerToken.sol|n                              (leer código IA)\n"
            "  6. |wclaude deploy MiPrimerToken.sol|n                    (deploy testnet)\n"
            "\n"
            "Cuando termines, |wquests|n te dirá el progreso. Luego |wclaim|n tu premio."
        ),
        "files": {
            "INTRO.txt": (
                "Bienvenido al claude_dojo.\n"
                "--------------------------\n"
                "Claude es un CLI de IA: le pides código en lenguaje natural y lo genera.\n"
                "En la práctica real:\n"
                "  $ claude                    # abre el agente interactivo\n"
                "  > genera un ERC-20 llamado MiToken\n"
                "En esta academia simulamos ese flujo con subcomandos explícitos\n"
                "para que entiendas cada paso.\n"
            ),
            "skills_readme.txt": (
                "Skills = paquetes de conocimiento que Claude aprende a usar.\n"
                "Austin Griffith (creador de Scaffold-ETH) publica skills para:\n"
                "  - scaffold-eth         → generar dApps\n"
                "  - solidity-basics      → patrones de contratos\n"
                "  - monad-kit            → deploy directo a Monad\n"
                "Instalalos con: `claude skills install <slug>`.\n"
            ),
        },
        "exits": [("install_dojo", "install_dojo"), ("home", "home")],
    },
]


def build_academy(caller=None):
    """
    Crea (o rehace) la zona Terminal Academy.
    Llamar desde @py: from world.zones.terminal_academy import build_academy; build_academy(self)
    """
    from typeclasses.rooms import Room
    from typeclasses.exits import Exit

    created = {}
    # 1) crear rooms
    for spec in ROOMS:
        existing = search_object(spec["key"], typeclass=Room)
        if existing:
            room = existing[0]
            if caller:
                caller.msg(f"Reutilizando room existente: {spec['key']} ({room.dbref})")
        else:
            room = create_object(Room, key=spec["key"])
            if caller:
                caller.msg(f"Creado room: {spec['key']} ({room.dbref})")
        room.db.desc = spec["desc"]
        room.db.academy_files = spec.get("files", {})
        created[spec["key"]] = room

    # 2) crear exits
    for spec in ROOMS:
        src = created[spec["key"]]
        for exit_key, dest_key in spec["exits"]:
            dest = created[dest_key]
            # evitar duplicados
            has = any(
                ex.key == exit_key and ex.destination == dest
                for ex in src.exits
            )
            if has:
                continue
            ex = create_object(
                Exit,
                key=exit_key,
                location=src,
                destination=dest,
            )
            if caller:
                caller.msg(f"Exit {src.key} -> {exit_key} -> {dest.key}")

    # 3) sembrar archivos virtuales en caller (si se pasa)
    if caller:
        if caller.db.fs_files is None:
            caller.db.fs_files = {}
        for spec in ROOMS:
            room = created[spec["key"]]
            if spec.get("files"):
                caller.db.fs_files[room.dbref] = dict(spec["files"])
        caller.db.fs_files = caller.db.fs_files
        # mover al home
        caller.move_to(created["home"], quiet=True)
        caller.msg("|gAcademy construida. Estás en /home.|n Escribe |wls|n para arrancar.")
    return created


def seed_player_files(player):
    """Copia los archivos canónicos de cada room a la vista del player."""
    if player.db.fs_files is None:
        player.db.fs_files = {}
    from typeclasses.rooms import Room
    for spec in ROOMS:
        rs = search_object(spec["key"], typeclass=Room)
        if not rs:
            continue
        room = rs[0]
        if spec.get("files"):
            player.db.fs_files[room.dbref] = dict(spec["files"])
    player.db.fs_files = player.db.fs_files
