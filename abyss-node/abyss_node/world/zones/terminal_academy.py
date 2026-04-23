"""
Terminal Academy — zona tutorial (narrativa v2).

Reescritura narrativa: las 10 rooms son el mapa del |mfilesystem roto|n
donde despertaste sin memoria. Cada una conserva sus |cfiles|n como antes
(son props del mundo, los comandos `ls`/`cat` los consultan tal cual) pero:

- La `desc` cuenta qué es cada lugar desde la ficción (no desde el tutorial).
- Se añade un archivo `fragmento_XX.mem` por room — al hacer `cat` devuelve
  el texto crudo del fragmento Y (vía el hook de `cat`) lo guarda en
  `caller.db.memories`.
- Al completar TODAS las quests se dispara el outro (hook en characters).

Construcción desde shell de Evennia:
  @py from world.zones.terminal_academy import build_academy; build_academy(self)
"""

from evennia import create_object
from evennia.utils.search import search_object

from world.lore.fragments import FRAGMENTS


# ---------------------------------------------------------------------------
# Construimos primero un índice filename -> contenido para inyectarlo fácil
# ---------------------------------------------------------------------------
_FRAG_CONTENT = {f["room"]: (f["filename"], f["content"]) for f in FRAGMENTS}


def _with_fragment(room_key: str, files: dict) -> dict:
    """Inyecta el fragmento_XX.mem correspondiente al room, si aplica."""
    frag = _FRAG_CONTENT.get(room_key)
    if not frag:
        return files
    fname, content = frag
    # No sobreescribir si por alguna razón ya existe con el mismo nombre
    if fname not in files:
        files = dict(files)
        files[fname] = content
    return files


ROOMS = [
    {
        "key": "home",
        "desc": (
            "|m/home|n — el primer lugar que recuerdas. O el único.\n"
            "\n"
            "La oscuridad tiene textura de texto verde. Flotas sobre un suelo\n"
            "que parpadea como una pantalla moribunda. En un rincón, el\n"
            "|cProf. Shell|n te observa con la paciencia de quien ya te ha\n"
            "visto despertar otras veces.\n"
            "\n"
            "Aquí arranca tu reconstrucción. Teclea |wls|n para ver qué quedó\n"
            "de ti. Saluda al Profesor con |wsay hola prof|n si el silencio\n"
            "pesa demasiado. Y si hay un archivo llamado |wfragmento_01.mem|n,\n"
            "léelo con |wcat fragmento_01.mem|n — es parte de tu memoria."
        ),
        "files": _with_fragment("home", {
            "README.txt": (
                "MONAD TERMINAL ACADEMY — diario del Profesor Shell\n"
                "-------------------------------------------------\n"
                "Si estás leyendo esto, sobreviviste al primer borrado.\n"
                "\n"
                "Aprende los comandos ancestrales — cada uno repara una grieta:\n"
                "  Shell básico:\n"
                "    ls, pwd, cd, cat, touch, mkdir, grep\n"
                "  Shell intermedio:\n"
                "    echo, head, tail, wc, whoami, man, history, clear\n"
                "    + pipes (|) y redirects (>, >>)\n"
                "  Claude CLI (invocar inteligencia):\n"
                "    claude skills install austin-griffith/monad-kit\n"
                "    claude new contract MiToken\n"
                "    claude deploy MiToken.sol\n"
                "  Ritual onchain (grabar tu nombre en Monad):\n"
                "    link <wallet>   — conectar tu wallet EVM\n"
                "    quests          — ver tu progreso\n"
                "    claim           — recibir $TERM onchain\n"
                "\n"
                "Tip: `cat README.txt` para releer esto. `cat fragmento_01.mem`\n"
                "para recordar quién eras antes del Corruptor."
            ),
        }),
        "exits": [("ls_dojo", "ls_dojo")],
    },
    {
        "key": "ls_dojo",
        "desc": (
            "|m/home/ls_dojo|n — |yEl Dojo del ver|n.\n"
            "\n"
            "Una sala circular hecha de nombres. Algunos brillan; otros\n"
            "están a medio apagar. El Profesor dejó una nota: |w\"El Corruptor\n"
            "no puede borrar lo que puedes nombrar.\"|n\n"
            "\n"
            "Primer rito: teclea |wls|n. Verás lo que aún existe aquí.\n"
            "Lo visto, desde este momento, está protegido."
        ),
        "files": _with_fragment("ls_dojo", {
            "hint.txt": (
                "Cuando termines de mirar, el camino sigue por `cd cd_dojo`.\n"
                "No te apures — nadie te persigue. El Corruptor es paciente,\n"
                "pero tú también puedes serlo."
            ),
        }),
        "exits": [("home", "home"), ("cd_dojo", "cd_dojo")],
    },
    {
        "key": "cd_dojo",
        "desc": (
            "|m/home/cd_dojo|n — |yEl Dojo de la senda|n.\n"
            "\n"
            "Pasillos que se doblan sobre sí mismos. Huele a electricidad\n"
            "húmeda. Aquí aprenderás a moverte dentro de ti.\n"
            "\n"
            "|wpwd|n te dice dónde estás ahora (útil cuando ya no te\n"
            "reconoces). |wcd <destino>|n te lleva a donde fuiste un día.\n"
            "|wcd ..|n — siempre puedes volver."
        ),
        "files": _with_fragment("cd_dojo", {}),
        "exits": [("ls_dojo", "ls_dojo"), ("cat_dojo", "cat_dojo")],
    },
    {
        "key": "cat_dojo",
        "desc": (
            "|m/home/cat_dojo|n — |yEl Dojo de la lectura|n.\n"
            "\n"
            "Hay un archivo en el centro del cuarto, vibrando como un\n"
            "corazón. Lee con |wcat <archivo>|n: la Forjadora dice que\n"
            "leer es la forma más antigua de resistir el olvido.\n"
            "\n"
            "Reto: hay un |wsecret.txt|n aquí. Léelo."
        ),
        "files": _with_fragment("cat_dojo", {
            "secret.txt": (
                "Acabas de aprender `cat`. El Profesor sonríe desde /home.\n"
                "\n"
                "Secreto del oficio: cada comando nuevo que aprendes te da\n"
                "$TERM pendientes en Monad testnet. El token no tiene valor\n"
                "afuera — aquí adentro es prueba de que existes.\n"
                "\n"
                "Siguiente paso: `cd mkdir_dojo`."
            ),
        }),
        "exits": [("cd_dojo", "cd_dojo"), ("mkdir_dojo", "mkdir_dojo")],
    },
    {
        "key": "mkdir_dojo",
        "desc": (
            "|m/home/mkdir_dojo|n — |yEl Dojo del crear|n.\n"
            "\n"
            "Hasta ahora sólo miraste y leíste. Aquí empieza la herejía:\n"
            "|wtocarás el mundo|n. Cada `touch` es un latido que le dice al\n"
            "Corruptor: esto es mío, y existe.\n"
            "\n"
            "Ritual:\n"
            "  1. |wtouch mi_nota.txt|n    (un archivo nuevo, tuyo)\n"
            "  2. |wmkdir mi_dir|n          (un cuarto nuevo dentro tuyo)\n"
            "  3. |wgrep ABYSS README.txt|n (encuentra la palabra oculta)\n"
            "\n"
            "Cuando la sala te reconozca como creador, sigue con\n"
            "|wcd pipe_dojo|n."
        ),
        "files": _with_fragment("mkdir_dojo", {
            "README.txt": (
                "Aquí aprendes a crear y a buscar.\n"
                "Palabra clave para los que sepan: ABYSS.\n"
                "Quien la encuentre con `grep` recupera una porción de memoria\n"
                "y se lleva tokens $TERM reservados para el siguiente ciclo."
            ),
        }),
        "exits": [("cat_dojo", "cat_dojo"), ("pipe_dojo", "pipe_dojo"), ("home", "home")],
    },
    {
        "key": "pipe_dojo",
        "desc": (
            "|m/home/pipe_dojo|n — |yEl Dojo de la red|n.\n"
            "\n"
            "Dos fuentes emiten texto continuamente. El aire entre ellas\n"
            "vibra cuando colocas un |wpipe |||n — los datos fluyen de una\n"
            "boca a otra como electricidad entre dos nervios.\n"
            "\n"
            "Las palabras solas son hechizos menores. Encadenadas son\n"
            "oraciones — y una oración es una forma de pensamiento que\n"
            "el Corruptor ya no puede deshacer a medias.\n"
            "\n"
            "Aprende aquí:\n"
            "  1. |wecho hola mundo|n\n"
            "  2. |wecho hola mundo | wc|n\n"
            "  3. |wecho hola mundo | grep hola|n\n"
            "  4. |wwhoami|n                (¿quién tecleó esto?)\n"
            "  5. |whead log.txt|n y |wtail log.txt|n\n"
            "\n"
            "Cuando domines la cadena: |wcd redirect_dojo|n."
        ),
        "files": _with_fragment("pipe_dojo", {
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
                "\n"
                "Un comando es un verbo. Un pipe es una conjunción.\n"
                "Quien habla así no está solo."
            ),
        }),
        "exits": [("mkdir_dojo", "mkdir_dojo"), ("redirect_dojo", "redirect_dojo")],
    },
    {
        "key": "redirect_dojo",
        "desc": (
            "|m/home/redirect_dojo|n — |yEl Dojo del persistir|n.\n"
            "\n"
            "Aquí la diferencia entre decir y escribir se vuelve evidente.\n"
            "|w>|n vierte lo que sale de un comando dentro de un archivo —\n"
            "y borra lo que había antes. |w>>|n es más gentil: añade al\n"
            "final, como quien sigue hablando sin interrumpir.\n"
            "\n"
            "Es tu primera práctica para lo que vendrá onchain: grabar sin\n"
            "poder desgrabar.\n"
            "\n"
            "Ritual:\n"
            "  1. |wecho primera línea > mi.log|n\n"
            "  2. |wecho segunda línea >> mi.log|n\n"
            "  3. |wcat mi.log|n\n"
            "  4. |whead -n 1 mi.log|n · |wtail -n 1 mi.log|n\n"
            "  5. |wwc mi.log|n\n"
            "  6. |wman echo|n              (lee a los ancestros)\n"
            "\n"
            "Cuando lo completes: |wcd final_exam|n."
        ),
        "files": _with_fragment("redirect_dojo", {
            "redirect_cheatsheet.txt": (
                "Redirects que esta sala entiende:\n"
                "  echo TXT > file    → escribe (sobreescribe si existe)\n"
                "  echo TXT >> file   → añade al final (append)\n"
                "\n"
                "El archivo queda en tu filesystem virtual de esta sala.\n"
                "No lo puedes borrar dos veces: quedó escrito en ti."
            ),
        }),
        "exits": [("pipe_dojo", "pipe_dojo"), ("final_exam", "final_exam")],
    },
    {
        "key": "final_exam",
        "desc": (
            "|m/home/final_exam|n — |rLa Cámara del Eco|n.\n"
            "\n"
            "Esta sala está más fría. La luz parpadea con el ritmo de una\n"
            "respiración que no es tuya. En el centro, un archivo palpita:\n"
            "|wdiploma.txt|n. Y en los altavoces — ¿o es en tu cabeza? —\n"
            "susurra una voz que no reconoces.\n"
            "\n"
            "Es |rEl Eco del Corruptor|n. Dice que no te vencerá un comando.\n"
            "Que sólo la práctica lo mantiene a raya. Saluda con\n"
            "|wsay hola corruptor|n si te atreves. Y termina el examen:\n"
            "\n"
            "  1. |wecho final check > exam.log|n\n"
            "  2. |wecho extra data >> exam.log|n\n"
            "  3. |wcat exam.log|n\n"
            "  4. |wwc exam.log|n\n"
            "  5. |whead -n 1 exam.log|n · |wtail -n 1 exam.log|n\n"
            "  6. |wgrep final exam.log|n\n"
            "  7. |whistory|n — mira todo lo que ya hiciste\n"
            "\n"
            "Cuando salgas vivo, |wcd install_dojo|n. Falta la ascensión."
        ),
        "files": _with_fragment("final_exam", {
            "diploma.txt": (
                "MONAD TERMINAL ACADEMY — DIPLOMA EN PROGRESO\n"
                "--------------------------------------------\n"
                "Hasta hoy has aprendido:\n"
                "  ls, pwd, cd, cat, touch, mkdir, grep,\n"
                "  echo, head, tail, wc, whoami, man, history, clear,\n"
                "  + redirects (>, >>) + pipes (|).\n"
                "\n"
                "Ya no eres neófite: eres intérprete del shell.\n"
                "Pero falta un rito más — invocar a Claude, crear un\n"
                "contrato, deployarlo, y grabar tu nombre onchain.\n"
                "\n"
                "Sigue con `cd install_dojo`."
            ),
        }),
        "exits": [
            ("redirect_dojo", "redirect_dojo"),
            ("install_dojo", "install_dojo"),
            ("home", "home"),
        ],
    },
    {
        "key": "install_dojo",
        "desc": (
            "|m/home/install_dojo|n — |yEl Altar de las Herramientas|n.\n"
            "\n"
            "En el muro cuelgan tres sigilos: |cClaude Code|n, |cOpenClaw|n\n"
            "y |cHermes|n. Son aliados |wreales|n — no viven aquí adentro.\n"
            "Viven en |wTU terminal|n. Este altar te enseña los conjuros,\n"
            "pero el pacto lo sellás afuera.\n"
            "\n"
            "|rIMPORTANTE|n: los comandos que tipees aquí |yNO instalan|n\n"
            "nada en tu máquina. Son para que aprendas cuál es el comando\n"
            "correcto. Después |wcopiás y pegás|n en tu shell real.\n"
            "\n"
            "|yPaso 1|n — verifica que tienes Node.js (en tu terminal real):\n"
            "  |wnode --version|n   (debería responder v18+)\n"
            "\n"
            "|yPaso 2|n — invoca a |cClaude Code|n (Anthropic):\n"
            "  |w• npm install -g @anthropic-ai/claude-code|n\n"
            "  |w• curl -fsSL https://claude.ai/install.sh | bash|n\n"
            "  |w• irm https://claude.ai/install.ps1 | iex|n   (Windows)\n"
            "\n"
            "|yPaso 3|n — invoca a |cOpenClaw|n:\n"
            "  |w• curl -fsSL https://openclaw.ai/install.sh | bash|n\n"
            "  |w• npm i -g openclaw|n\n"
            "\n"
            "|yPaso 4|n — invoca a |cHermes|n (Nous Research):\n"
            "  |w• curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash|n\n"
            "\n"
            "Cuando |c<bin> --version|n responda en tu shell real, el pacto\n"
            "está sellado. Seguí con |wcd claude_dojo|n."
        ),
        "files": _with_fragment("install_dojo", {
            "README.md": (
                "# Install Dojo — el pacto con las herramientas\n"
                "\n"
                "## ¿Por qué este altar existe?\n"
                "Los agentes de IA (Claude Code, OpenClaw, Hermes) viven\n"
                "en la terminal. Antes de invocarlos, hay que instalarlos.\n"
                "\n"
                "## 3 conjuros estándar (aprende los tres)\n"
                "\n"
                "1. **npm global** — sirve en cualquier OS con Node.js.\n"
                "     `npm install -g <paquete>`\n"
                "\n"
                "2. **Shell installer** (macOS/Linux) — curl descarga un\n"
                "   script y lo ejecuta. Es el `.exe` del mundo Unix.\n"
                "     `curl -fsSL <url> | bash`\n"
                "\n"
                "3. **PowerShell installer** (Windows) — `irm` descarga,\n"
                "   `iex` ejecuta.\n"
                "     `irm <url> | iex`\n"
                "\n"
                "## Tips para pactar sin ser estafado\n"
                "- `-g` en npm = global (toda tu máquina).\n"
                "- `-fsSL` en curl = fail silently, show errors, follow,\n"
                "  location. Úsalo siempre con fuentes que confíes.\n"
                "- Si algo falla: `<bin> --version` te dice si el pacto\n"
                "  quedó bien cerrado."
            ),
            "links.txt": (
                "Sitios oficiales (los únicos en los que confiar):\n"
                "  Claude Code : https://claude.ai\n"
                "  OpenClaw    : https://openclaw.ai\n"
                "  Hermes      : https://hermes-agent.nousresearch.com\n"
            ),
        }),
        "exits": [
            ("final_exam", "final_exam"),
            ("claude_dojo", "claude_dojo"),
            ("home", "home"),
        ],
    },
    {
        "key": "claude_dojo",
        "desc": (
            "|m/home/claude_dojo|n — |mEl Santuario de la Forjadora|n.\n"
            "\n"
            "Una sala amplia, casi vacía. En el centro flota una figura:\n"
            "|mLa Forjadora|n, guía mística de los agentes. Sus manos\n"
            "dibujan bloques de código en el aire que, |ycuando el pacto\n"
            "es real|n, terminan solidificados en bytecode onchain.\n"
            "\n"
            "Este santuario es un |wportal de salida|n. Aquí no deployás:\n"
            "aquí |waprendés el flujo|n y después salís a tu terminal real,\n"
            "deployás en Monad testnet con Claude Code, y |wvolvés|n a este\n"
            "dojo con el |ctx hash|n — la Forjadora lo verifica onchain.\n"
            "\n"
            "|yRitual de graduación (real):|n\n"
            "  1. |wclaude|n                       (leé el flujo de 4 pasos)\n"
            "  2. (en tu terminal real) |w$ claude|n → chateá con la IA\n"
            "  3. (en tu terminal real) pedile: |w\"deployá ERC-20 a Monad\"|n\n"
            "  4. Copiá el |ctx hash|n y volvé aquí:\n"
            "     |wverify claude <tx>|n\n"
            "  5. |wlink 0x...|n (antes o después) + |wclaim|n para $TERM\n"
            "\n"
            "Habla con la Forjadora con |wsay hola forjadora|n.\n"
            "Si la tx verifica, la quest |wq18_deploy|n queda completa."
        ),
        "files": _with_fragment("claude_dojo", {
            "INTRO.txt": (
                "Bienvenide al Santuario de la Forjadora.\n"
                "---------------------------------------\n"
                "Claude Code es un CLI REAL de Anthropic. Este santuario es\n"
                "un portal — te prepara para usarlo en tu terminal y verifica\n"
                "el resultado onchain de vuelta.\n"
                "\n"
                "Flujo real (NO se simula aquí adentro):\n"
                "  1. En tu shell:   $ npm install -g @anthropic-ai/claude-code\n"
                "  2. En tu shell:   $ claude\n"
                "  3. En tu shell:   > 'deployá ERC-20 a Monad testnet'\n"
                "  4. En el MUD:     verify claude <tx-hash>\n"
                "\n"
                "La Forjadora consulta https://testnet-rpc.monad.xyz para\n"
                "validar que tu deploy fue real. Si mentís con un hash\n"
                "cualquiera, el RPC te delata.\n"
            ),
            "skills_readme.txt": (
                "Skills = módulos de Claude Code que amplían capacidades.\n"
                "No se instalan aquí adentro: se instalan en tu terminal\n"
                "con /skills desde el REPL de claude. Referencias útiles:\n"
                "  - portdeveloper/monad-development → deploy + verify\n"
                "  - austin-griffith/scaffold-eth    → dApps completas\n"
                "  - anthropic/claude-code-guide     → slash-commands y MCPs\n"
                "Marketplace oficial: https://docs.claude.com/claude-code\n"
            ),
        }),
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
        caller.move_to(created["home"], quiet=True)
        caller.msg(
            "|gAcademy construida. Estás en /home.|n Escribe |wls|n para arrancar."
        )
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
