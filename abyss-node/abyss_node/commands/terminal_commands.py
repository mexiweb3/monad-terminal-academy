"""
Terminal Academy — comandos estilo terminal + quests + wallet/claim onchain.

El jugador aprende comandos reales de shell ejecutándolos dentro del MUD.
Cada comando usado por primera vez completa una quest y suma $TERM pendientes.
`link <wallet>` asocia address EVM y `claim` transfiere los tokens al player.
"""

from evennia import Command
from evennia.utils import logger

# ---------- Quests ----------
# Cada quest se completa la primera vez que el jugador usa su comando target.
QUESTS = [
    # Acto I — Despertar (rooms: home, ls_dojo, cd_dojo, cat_dojo)
    {"id": "q01_ls",      "cmd": "ls",      "reward": 10,  "room": "home",     "act": 1, "desc": "Corre `ls` para listar el directorio actual."},
    {"id": "q02_pwd",     "cmd": "pwd",     "reward": 10,  "room": "cd_dojo",  "act": 1, "desc": "Corre `pwd` para ver en qué directorio estás."},
    {"id": "q03_cd",      "cmd": "cd",      "reward": 20,  "room": "ls_dojo",  "act": 1, "desc": "Usa `cd <destino>` para moverte entre directorios."},
    {"id": "q04_cat",     "cmd": "cat",     "reward": 30,  "room": "cat_dojo", "act": 1, "desc": "Lee un archivo con `cat <archivo>`."},
    # Acto II — Entrenamiento (rooms: mkdir_dojo, pipe_dojo, redirect_dojo, final_exam)
    {"id": "q05_mkdir",   "cmd": "mkdir",   "reward": 30,  "room": "mkdir_dojo",   "act": 2, "desc": "Crea un directorio con `mkdir <nombre>`."},
    {"id": "q06_touch",   "cmd": "touch",   "reward": 30,  "room": "mkdir_dojo",   "act": 2, "desc": "Crea un archivo vacío con `touch <nombre>`."},
    {"id": "q07_grep",    "cmd": "grep",    "reward": 50,  "room": "mkdir_dojo",   "act": 2, "desc": "Busca texto con `grep <patrón> <archivo>`."},
    {"id": "q08_echo",    "cmd": "echo",    "reward": 10,  "room": "pipe_dojo",    "act": 2, "desc": "Imprime texto con `echo <texto>`."},
    {"id": "q09_whoami",  "cmd": "whoami",  "reward": 10,  "room": "pipe_dojo",    "act": 2, "desc": "Averigua tu usuario con `whoami`."},
    {"id": "q10_head",    "cmd": "head",    "reward": 20,  "room": "pipe_dojo",    "act": 2, "desc": "Lee las primeras líneas con `head <archivo>`."},
    {"id": "q11_tail",    "cmd": "tail",    "reward": 20,  "room": "pipe_dojo",    "act": 2, "desc": "Lee las últimas líneas con `tail <archivo>`."},
    {"id": "q12_wc",      "cmd": "wc",      "reward": 20,  "room": "pipe_dojo",    "act": 2, "desc": "Cuenta líneas/palabras/chars con `wc <archivo>`."},
    {"id": "q13_man",     "cmd": "man",     "reward": 20,  "room": "redirect_dojo","act": 2, "desc": "Consulta el manual de un comando con `man <cmd>`."},
    {"id": "q14_history", "cmd": "history", "reward": 30,  "room": "redirect_dojo","act": 2, "desc": "Revisa tus últimos comandos con `history`."},
    # Acto III — Ascensión (rooms: install_dojo, claude_dojo)
    {"id": "q20_node",            "cmd": "node",             "reward": 10, "room": "install_dojo", "act": 3, "desc": "Verifica Node con `node --version`."},
    {"id": "q21_install_claude",  "cmd": "install:claude",   "reward": 50, "room": "install_dojo", "act": 3, "desc": "Instala Claude Code (npm, curl o PowerShell — tú eliges)."},
    {"id": "q22_install_openclaw","cmd": "install:openclaw", "reward": 50, "room": "install_dojo", "act": 3, "desc": "Instala OpenClaw: `curl -fsSL https://openclaw.ai/install.sh | bash`."},
    {"id": "q23_install_hermes",  "cmd": "install:hermes",   "reward": 50, "room": "install_dojo", "act": 3, "desc": "Instala Hermes: `curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash`."},
    {"id": "q15_claude",     "cmd": "claude",       "reward": 30, "room": "claude_dojo", "act": 3, "desc": "Ejecuta `claude` para abrir el CLI de IA."},
    {"id": "q16_skill",      "cmd": "claude:skill", "reward": 40, "room": "claude_dojo", "act": 3, "desc": "Instala un skill con `claude skills install <slug>`."},
    {"id": "q17_newcontract","cmd": "claude:new",   "reward": 50, "room": "claude_dojo", "act": 3, "desc": "Genera un contrato con `claude new contract <Nombre>`."},
    {"id": "q18_deploy",     "cmd": "claude:deploy","reward": 60, "room": "claude_dojo", "act": 3, "desc": "Deploya el contrato con `claude deploy <archivo.sol>`."},
    # Ritual onchain — unlocked desde que entras a claude_dojo
    {"id": "q19_link",    "cmd": "link",    "reward": 50, "room": "claude_dojo", "act": 3, "desc": "Conecta tu wallet con `link 0x...` o `link tuens.eth`."},
]
QUEST_BY_CMD = {q["cmd"]: q for q in QUESTS}


def _ensure_state(caller):
    if caller.db.quest_done is None:
        caller.db.quest_done = []
    if caller.db.abyss_pending is None:
        caller.db.abyss_pending = 0
    if caller.db.wallet is None:
        caller.db.wallet = ""
    if caller.db.fs_files is None:
        # Estructura de "archivos virtuales" por room. dict: room_dbref -> dict(filename -> contents)
        caller.db.fs_files = {}
    if caller.db.cmd_history is None:
        caller.db.cmd_history = []


HISTORY_LIMIT = 200


def _record_history(caller, cmd_key, args):
    """Guarda la línea ejecutada en la historia del jugador (últimas HISTORY_LIMIT)."""
    _ensure_state(caller)
    line = cmd_key if not args else f"{cmd_key} {args}".rstrip()
    hist = list(caller.db.cmd_history or [])
    hist.append(line)
    if len(hist) > HISTORY_LIMIT:
        hist = hist[-HISTORY_LIMIT:]
    caller.db.cmd_history = hist


def _get_room_files(loc, caller):
    """Unión de archivos canónicos del room y los personales del caller (player overrides)."""
    if loc is None:
        return {}
    room_files = (loc.db.academy_files or {})
    player_files = (caller.db.fs_files or {}).get(loc.dbref, {}) if caller else {}
    return {**room_files, **player_files}


def _write_player_file(caller, loc, fname, content, append=False):
    """Escribe/append un archivo en el fs virtual del player para el room actual.

    Clona explícitamente el dict para esquivar rarezas de _SaverDict y asegurar persistencia.
    """
    _ensure_state(caller)
    if not loc:
        return False
    fs = dict(caller.db.fs_files or {})
    room_files = dict(fs.get(loc.dbref, {}))
    if append and fname in room_files:
        prev = room_files[fname] or ""
        if prev and not prev.endswith("\n"):
            prev += "\n"
        room_files[fname] = prev + content
    else:
        room_files[fname] = content
    fs[loc.dbref] = room_files
    caller.db.fs_files = fs
    return True


def _emit_prompt(caller):
    """Muestra el prompt tipo shell al final de cada comando (user@academy:/path$)."""
    loc = caller.location
    path = f"/academy/{loc.key}" if loc else "/academy"
    name = caller.key or "you"
    try:
        caller.msg(prompt=f"|g{name}@academy|n:|c{path}|n|w$|n ")
    except Exception:
        pass


def _reward_if_quest(caller, cmd_key):
    """Si este comando completa una quest pendiente, aplica reward y notifica."""
    _ensure_state(caller)
    quest = QUEST_BY_CMD.get(cmd_key)
    if quest and quest["id"] not in caller.db.quest_done:
        caller.db.quest_done.append(quest["id"])
        caller.db.abyss_pending += quest["reward"]
        caller.msg(
            f"\n|g╭─ QUEST COMPLETADA ────────────────╮|n\n"
            f"|g│|n  {quest['desc']}\n"
            f"|g│|n  |y+{quest['reward']} $TERM|n pendientes — total |y{caller.db.abyss_pending}|n\n"
            f"|g│|n  Cuando tengas wallet linkeada, usa |w|lcclaim|ltclaim|le|n para reclamar onchain.\n"
            f"|g╰────────────────────────────────────╯|n"
        )
    _emit_prompt(caller)


# ---------- Comandos terminal básicos ----------
class CmdLS(Command):
    """
    Lista el contenido del "directorio" actual (la sala donde estás).

    Usage:
      ls
    """
    key = "ls"
    aliases = ["dir"]
    locks = "cmd:all()"
    help_category = "Terminal"

    def func(self):
        caller = self.caller
        _ensure_state(caller)
        _record_history(caller, "ls", self.args.strip() if self.args else "")
        loc = caller.location
        if not loc:
            caller.msg("(sin ubicación)")
            return
        entries = []
        # Subdirectorios = salidas
        for ex in loc.exits:
            entries.append(f"|c{ex.key}/|n")
        # Archivos canónicos del room + archivos personales del caller
        room_files = (loc.db.academy_files or {}) if loc else {}
        player_files = caller.db.fs_files.get(loc.dbref, {})
        merged = {**room_files, **player_files}
        for fname in sorted(merged.keys()):
            entries.append(f"|w{fname}|n")
        # Objetos del room (items, NPCs) como "archivos especiales"
        for obj in loc.contents:
            if obj == caller or obj in loc.exits:
                continue
            if obj.has_account:
                continue
            prefix = "@" if (hasattr(obj, "db") and obj.db.npc_type) else ""
            entries.append(f"|g{prefix}{obj.key}|n")
        caller.msg(f"{loc.key}:")
        if entries:
            caller.msg("  " + "   ".join(entries))
        else:
            caller.msg("  (vacío)")
        _reward_if_quest(caller, "ls")


class CmdPWD(Command):
    """
    Imprime el "directorio" (sala) actual.

    Usage:
      pwd
    """
    key = "pwd"
    locks = "cmd:all()"
    help_category = "Terminal"

    def func(self):
        caller = self.caller
        _ensure_state(caller)
        _record_history(caller, "pwd", "")
        loc = caller.location
        path = loc.key if loc else "(ninguno)"
        caller.msg(f"|w/academy/{path}|n")
        _reward_if_quest(caller, "pwd")


class CmdCD(Command):
    """
    Cámbiate a un subdirectorio (sala adyacente).

    Usage:
      cd <destino>
      cd ..          (intenta volver — usa la salida 'back' si existe)
    """
    key = "cd"
    locks = "cmd:all()"
    help_category = "Terminal"

    def func(self):
        caller = self.caller
        _ensure_state(caller)
        arg = (self.args or "").strip()
        _record_history(caller, "cd", arg)
        loc = caller.location
        if not loc:
            caller.msg("(sin ubicación)")
            return

        # cd sin args → /home
        if not arg:
            from evennia.utils.search import search_object
            from typeclasses.rooms import Room
            home_rooms = search_object("home", typeclass=Room)
            if home_rooms:
                caller.db.last_room = loc
                caller.move_to(home_rooms[0], quiet=False)
                _reward_if_quest(caller, "cd")
            else:
                caller.msg("cd: no hay home room")
            return

        # cd - → último dir
        if arg == "-":
            last = caller.db.last_room
            if last:
                caller.db.last_room = loc
                caller.move_to(last, quiet=False)
                _reward_if_quest(caller, "cd")
            else:
                caller.msg("cd: OLDPWD no establecido")
            return

        # `..` busca exit literal "..", con fallback al alias "back"
        target_name = arg
        for ex in loc.exits:
            aliases = [a.lower() for a in ex.aliases.all()]
            if ex.key.lower() == target_name.lower() or target_name.lower() in aliases:
                caller.db.last_room = loc
                ex.at_traverse(caller, ex.destination)
                _reward_if_quest(caller, "cd")
                return
        # Fallback histórico: si el usuario tipea `..`, intenta un exit llamado "back"
        if arg == "..":
            for ex in loc.exits:
                if ex.key.lower() == "back":
                    caller.db.last_room = loc
                    ex.at_traverse(caller, ex.destination)
                    _reward_if_quest(caller, "cd")
                    return
        caller.msg(f"cd: no such directory: {arg}")


class CmdCAT(Command):
    """
    Muestra el contenido de un archivo.

    Usage:
      cat <archivo>
    """
    key = "cat"
    locks = "cmd:all()"
    help_category = "Terminal"

    def func(self):
        caller = self.caller
        _ensure_state(caller)
        arg = (self.args or "").strip()
        _record_history(caller, "cat", arg)
        if not arg:
            caller.msg("usage: cat <archivo>")
            return
        loc = caller.location
        merged = _get_room_files(loc, caller)
        # 1) archivos virtuales (player overrides room)
        if arg in merged:
            content = merged[arg] or "(archivo vacío)"
            caller.msg(f"|x────── {arg} ──────|n\n{content}\n|x──────|n")
            _reward_if_quest(caller, "cat")
            return
        # 2) objetos del room como "archivos especiales"
        if loc:
            obj = loc.search(arg, quiet=True)
            if obj:
                obj = obj[0] if isinstance(obj, list) else obj
                desc = obj.db.desc or obj.key
                caller.msg(f"|x────── {arg} ──────|n\n{desc}\n|x──────|n")
                _reward_if_quest(caller, "cat")
                return
        caller.msg(f"cat: {arg}: No such file or directory")


class CmdTOUCH(Command):
    """
    Crea un archivo vacío en el directorio actual.

    Usage:
      touch <archivo>
    """
    key = "touch"
    locks = "cmd:all()"
    help_category = "Terminal"

    def func(self):
        caller = self.caller
        _ensure_state(caller)
        arg = (self.args or "").strip()
        _record_history(caller, "touch", arg)
        if not arg:
            caller.msg("usage: touch <archivo>")
            return
        loc = caller.location
        if not loc:
            caller.msg("(sin ubicación)")
            return
        files = caller.db.fs_files.setdefault(loc.dbref, {})
        files[arg] = ""
        caller.db.fs_files = caller.db.fs_files  # trigger save
        caller.msg(f"(creado) {arg}")
        _reward_if_quest(caller, "touch")


class CmdMKDIR(Command):
    """
    Crea un subdirectorio real — podés entrar con `cd <nombre>`.

    Usage:
      mkdir <nombre>
    """
    key = "mkdir"
    locks = "cmd:all()"
    help_category = "Terminal"

    def func(self):
        caller = self.caller
        _ensure_state(caller)
        arg = (self.args or "").strip()
        _record_history(caller, "mkdir", arg)
        if not arg:
            caller.msg("usage: mkdir <nombre>")
            return
        if "/" in arg or arg.startswith(".") or len(arg) > 40:
            caller.msg(f"mkdir: nombre inválido: {arg}")
            return
        loc = caller.location
        if not loc:
            caller.msg("(sin ubicación)")
            return
        # Si ya existe un exit con ese nombre, abortar
        for ex in loc.exits:
            if ex.key.lower() == arg.lower():
                caller.msg(f"mkdir: cannot create directory '{arg}': File exists")
                return

        # Crear room real + exit ida + exit vuelta
        from evennia import create_object
        from typeclasses.rooms import Room
        from typeclasses.exits import Exit

        new_room = create_object(Room, key=arg)
        new_room.db.desc = (
            f"|c{arg}/|n — subdirectorio creado por |w{caller.key}|n.\n"
            f"\nDirectorio vacío. Usá |wtouch <archivo>|n para crear archivos "
            f"o |wcd ..|n para volver."
        )
        new_room.db.academy_files = {}

        create_object(Exit, key=arg, location=loc, destination=new_room)
        create_object(
            Exit,
            key="..",
            aliases=["back", loc.key.lower()],
            location=new_room,
            destination=loc,
        )

        caller.msg(
            f"(creado) |c{arg}/|n — entrá con |wcd {arg}|n, volvé con |wcd ..|n"
        )
        _reward_if_quest(caller, "mkdir")


class CmdGREP(Command):
    """
    Busca un patrón en un archivo.

    Usage:
      grep <patrón> <archivo>
    """
    key = "grep"
    locks = "cmd:all()"
    help_category = "Terminal"

    def func(self):
        caller = self.caller
        _ensure_state(caller)
        raw = (self.args or "").strip()
        _record_history(caller, "grep", raw)
        parts = raw.split(None, 1)
        if len(parts) < 2:
            caller.msg("usage: grep <patrón> <archivo>")
            return
        pattern, fname = parts[0], parts[1]
        loc = caller.location
        merged = _get_room_files(loc, caller)
        content = None
        if fname in merged:
            content = merged[fname]
        elif loc:
            obj = loc.search(fname, quiet=True)
            if obj:
                obj = obj[0] if isinstance(obj, list) else obj
                content = obj.db.desc or obj.key
        if content is None:
            caller.msg(f"grep: {fname}: No such file or directory")
            return
        hits = [line for line in (content or "").splitlines() if pattern in line]
        if hits:
            caller.msg("\n".join(f"|y{fname}:|n {line}" for line in hits))
        else:
            caller.msg(f"(sin coincidencias de '{pattern}' en {fname})")
        _reward_if_quest(caller, "grep")


# ---------- Wallet / claim onchain ----------
# ---------- Install Dojo: node + npm simulados ----------
class CmdNode(Command):
    """
    Node.js runtime (simulado — muestra versión instalada en la Academia).

    Usage:
      node --version
      node -v
    """
    key = "node"
    locks = "cmd:all()"
    help_category = "Install"

    def func(self):
        caller = self.caller
        _ensure_state(caller)
        arg = (self.args or "").strip()
        _record_history(caller, "node", arg)
        if arg in ("--version", "-v", ""):
            caller.msg("|gv22.22.2|n")
            _reward_if_quest(caller, "node")
            return
        caller.msg(
            "node: REPL interactivo no soportado en la Academia.\n"
            "Usa |wnode --version|n para verificar la instalación."
        )


# Catálogo de packages que el `npm install -g` reconoce en este mundo.
NPM_PACKAGES = {
    "@anthropic-ai/claude-code": {
        "quest": "install:claude",
        "bin": "claude",
        "version": "1.2.0",
        "desc": "Claude Code — CLI oficial de Anthropic para pair-programar con IA",
    },
    "openclaw": {
        "quest": "install:openclaw",
        "bin": "openclaw",
        "version": "0.8.3",
        "desc": "OpenClaw — framework open-source de agentes (openclaw.ai)",
    },
}


# URLs reconocidas por curl/irm para simular install scripts
INSTALL_SCRIPTS = {
    "claude.ai/install.sh": {
        "quest": "install:claude",
        "bin": "claude",
        "version": "1.2.0",
        "source": "Anthropic · claude.ai",
        "shell": "bash",
    },
    "claude.ai/install.ps1": {
        "quest": "install:claude",
        "bin": "claude",
        "version": "1.2.0",
        "source": "Anthropic · claude.ai (Windows PowerShell)",
        "shell": "powershell",
    },
    "openclaw.ai/install.sh": {
        "quest": "install:openclaw",
        "bin": "openclaw",
        "version": "0.8.3",
        "source": "OpenClaw · openclaw.ai",
        "shell": "bash",
    },
    "hermes-agent.nousresearch.com/install.sh": {
        "quest": "install:hermes",
        "bin": "hermes",
        "version": "0.5.2",
        "source": "Nous Research · hermes-agent.nousresearch.com",
        "shell": "bash",
    },
}


def _simulate_install(caller, cfg, install_cmd: str, platform_label: str):
    """Imprime output realista de un install script + aplica reward de quest."""
    bin_name = cfg["bin"]
    caller.msg(
        f"|x{platform_label} detected. Fetching installer...|n\n"
        f"|x  → {install_cmd}|n\n"
        f"\n"
        f"  [|g✓|n] descargando de {cfg['source']}\n"
        f"  [|g✓|n] verificando checksum\n"
        f"  [|g✓|n] instalando binario {bin_name}\n"
        f"  [|g✓|n] agregando al PATH\n"
        f"\n"
        f"|g╭─ Instalado ─────────────────────────╮|n\n"
        f"|g│|n  |c{bin_name}|n |wv{cfg['version']}|n\n"
        f"|g│|n  {cfg['source']}\n"
        f"|g╰─────────────────────────────────────╯|n\n"
        f"\n"
        f"Verifica con |w{bin_name} --version|n"
    )
    _reward_if_quest(caller, cfg["quest"])


def _match_install_url(raw_args: str):
    """Dado los args de curl/irm, detecta qué install script se está ejecutando."""
    low = (raw_args or "").lower()
    for path, cfg in INSTALL_SCRIPTS.items():
        if path.lower() in low:
            return path, cfg
    return None, None


class CmdNpm(Command):
    """
    Gestor de paquetes de Node (simulado — solo soporta `install -g` de un set curado).

    Usage:
      npm --version
      npm install -g <package>

    Paquetes soportados en la Academia:
      @anthropic-ai/claude-code · opencode-ai · hermes-cli
    """
    key = "npm"
    locks = "cmd:all()"
    help_category = "Install"

    def func(self):
        caller = self.caller
        _ensure_state(caller)
        raw = (self.args or "").strip()
        _record_history(caller, "npm", raw)
        parts = raw.split()

        if not parts or parts[0] in ("--version", "-v"):
            caller.msg("|g10.9.2|n")
            return

        if parts[0] == "help" or parts[0] == "-h":
            caller.msg(self.__doc__)
            return

        if parts[0] != "install" and parts[0] != "i":
            caller.msg(f"npm: subcomando '{parts[0]}' no soportado en la Academia.")
            return

        # Parsear flags y package name
        flags = [p for p in parts[1:] if p.startswith("-")]
        args_rest = [p for p in parts[1:] if not p.startswith("-")]
        if "-g" not in flags and "--global" not in flags:
            caller.msg(
                "npm: en la Academia solo soportamos |winstall global|n.\n"
                "Usa: |wnpm install -g <package>|n"
            )
            return
        if not args_rest:
            caller.msg("usage: npm install -g <package>")
            return

        pkg_name = args_rest[0]
        pkg = NPM_PACKAGES.get(pkg_name)
        if not pkg:
            known = ", ".join(NPM_PACKAGES.keys())
            caller.msg(
                f"npm ERR! 404 Not Found: '|y{pkg_name}|n'\n"
                f"La Academia reconoce: |w{known}|n"
            )
            return

        # Simular output realista de npm
        bin_name = pkg["bin"]
        caller.msg(
            f"|xadded 1 package, and audited 1 package in 3s|n\n"
            f"\n"
            f"|gfound 0 vulnerabilities|n\n"
            f"\n"
            f"|g╭─ Instalado ─────────────────────────╮|n\n"
            f"|g│|n  |c{pkg_name}@{pkg['version']}|n\n"
            f"|g│|n  {pkg['desc']}\n"
            f"|g│|n  bin: |w/usr/local/bin/{bin_name}|n\n"
            f"|g╰─────────────────────────────────────╯|n\n"
            f"\n"
            f"Verifica con |w{bin_name} --version|n"
        )
        _reward_if_quest(caller, pkg["quest"])


class CmdCurl(Command):
    """
    Simula `curl` para ejecutar install scripts del Install Dojo.

    Uso típico:
      curl -fsSL <url> | bash
      curl -fsSL https://claude.ai/install.sh | bash
      curl -fsSL https://openclaw.ai/install.sh | bash
      curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
    """
    key = "curl"
    locks = "cmd:all()"
    help_category = "Install"

    def func(self):
        caller = self.caller
        _ensure_state(caller)
        raw = (self.args or "").strip()
        _record_history(caller, "curl", raw)

        if not raw:
            caller.msg("curl: usage: curl <url> [| bash]")
            return

        # Detectar si el pipeline es un install script conocido
        path, cfg = _match_install_url(raw)
        low = raw.lower()
        pipes_to_shell = any(s in low for s in ("| bash", "| sh", "| zsh"))

        if path and pipes_to_shell:
            install_cmd = f"curl {raw}"
            _simulate_install(caller, cfg, install_cmd, "macOS/Linux")
            return

        if path and not pipes_to_shell:
            caller.msg(
                f"Descargando {path}...\n"
                f"(recibí {cfg.get('bytes', 1240)} bytes)\n"
                f"Tip: para ejecutar el script, pípealo a bash: |wcurl ...{path} | bash|n"
            )
            return

        caller.msg(
            "curl: en la Academia solo simulamos los install scripts del Install Dojo.\n"
            "Prueba uno de estos:\n"
            "  |wcurl -fsSL https://claude.ai/install.sh | bash|n\n"
            "  |wcurl -fsSL https://openclaw.ai/install.sh | bash|n\n"
            "  |wcurl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash|n"
        )


class CmdIrm(Command):
    """
    PowerShell `Invoke-RestMethod` (alias `irm`) — simulado para Windows install.

    Uso típico:
      irm <url> | iex
      irm https://claude.ai/install.ps1 | iex
    """
    key = "irm"
    aliases = ["Invoke-RestMethod", "iwr", "Invoke-WebRequest"]
    locks = "cmd:all()"
    help_category = "Install"

    def func(self):
        caller = self.caller
        _ensure_state(caller)
        raw = (self.args or "").strip()
        _record_history(caller, "irm", raw)

        if not raw:
            caller.msg(
                "irm (Invoke-RestMethod) — PowerShell / Windows.\n"
                "Usage: |wirm <url> | iex|n\n"
                "Ej: |wirm https://claude.ai/install.ps1 | iex|n"
            )
            return

        path, cfg = _match_install_url(raw)
        low = raw.lower()
        pipes_to_iex = any(s in low for s in ("| iex", "| invoke-expression"))

        if path and pipes_to_iex:
            install_cmd = f"irm {raw}"
            _simulate_install(caller, cfg, install_cmd, "Windows PowerShell")
            return

        if path:
            caller.msg(
                f"Descargado {path}.\n"
                f"Tip: pípealo a iex para ejecutar: |wirm ...{path} | iex|n"
            )
            return

        caller.msg(
            "irm: en la Academia solo simulamos install scripts del Install Dojo (Windows).\n"
            "Prueba: |wirm https://claude.ai/install.ps1 | iex|n"
        )


def _resolve_ens(name: str):
    """Resuelve un ENS name (.eth, etc.) a una address 0x usando Ethereum mainnet.
    Retorna (address, None) en éxito, (None, error_str) en fallo.
    """
    try:
        from web3 import Web3
        from ens import ENS
    except Exception as e:
        return None, f"web3/ens no disponible: {e}"
    rpcs = [
        "https://ethereum-rpc.publicnode.com",
        "https://eth.drpc.org",
        "https://rpc.flashbots.net",
        "https://cloudflare-eth.com",
        "https://rpc.ankr.com/eth",
        "https://eth.llamarpc.com",
    ]
    last_err = None
    for rpc in rpcs:
        try:
            w3 = Web3(Web3.HTTPProvider(rpc, request_kwargs={"timeout": 6}))
            ns = ENS.from_web3(w3) if hasattr(ENS, "from_web3") else ENS.fromWeb3(w3)
            addr = ns.address(name)
            if addr:
                return str(addr), None
            last_err = "no encontrado"
        except Exception as e:
            last_err = f"{type(e).__name__}: {str(e)[:80]}"
            continue
    return None, last_err or "no resuelto"


class CmdLink(Command):
    """
    Conecta tu wallet EVM (0x... o ENS como `vitalik.eth`) para recibir $TERM en Monad testnet.

    Usage:
      link <0x...>
      link <nombre.eth>
    """
    key = "link"
    aliases = ["wallet"]
    locks = "cmd:all()"
    help_category = "Monad"

    def func(self):
        caller = self.caller
        _ensure_state(caller)
        arg = (self.args or "").strip()
        _record_history(caller, "link", arg)
        if not arg:
            current = caller.db.wallet or "(sin linkear)"
            ens = caller.db.wallet_ens or ""
            display = f"|c{current}|n" + (f" ({ens})" if ens else "")
            caller.msg(f"wallet actual: {display}\nusage: link <0x...> | link <nombre.eth>")
            return

        addr = None
        ens_display = ""

        # Caso 1: address hex directa
        if arg.startswith("0x") and len(arg) == 42:
            addr = arg
        # Caso 2: parece ENS (tiene punto, no empieza con 0x)
        elif "." in arg and not arg.startswith("0x"):
            caller.msg(f"|yResolviendo {arg} via ENS (Ethereum mainnet)...|n")
            resolved, err = _resolve_ens(arg)
            if not resolved:
                caller.msg(f"|rError:|n no pude resolver '{arg}' — {err}")
                return
            addr = resolved
            ens_display = arg
            caller.msg(f"|gENS resuelto:|n {arg} → |c{addr}|n")
        else:
            caller.msg(
                "|rError:|n formato inválido.\n"
                "  Usa |w0x...|n (40 hex chars) o un |wnombre.eth|n."
            )
            return

        caller.db.wallet = addr
        caller.db.wallet_ens = ens_display

        pretty = f"|c{addr}|n" + (f" (|y{ens_display}|n)" if ens_display else "")
        caller.msg(f"|gOK|n — wallet linkeada: {pretty}\nAhora usa |wclaim|n para recibir tus $TERM onchain.")
        _reward_if_quest(caller, "link")


class CmdQuests(Command):
    """
    Muestra tus quests (completadas y pendientes).

    Usage:
      quests
    """
    key = "quests"
    aliases = ["q"]
    locks = "cmd:all()"
    help_category = "Monad"

    def func(self):
        caller = self.caller
        _ensure_state(caller)
        _record_history(caller, "quests", "")
        done = set(caller.db.quest_done or [])
        visited = set(caller.db.visited_rooms or [])
        # La room actual siempre cuenta como visitada
        if caller.location:
            visited.add(caller.location.key)
        # 'home' siempre desbloqueada (ahí arrancas)
        visited.add("home")

        # Agrupamos por acto
        ACT_NAMES = {1: "I · Despertar", 2: "II · Entrenamiento", 3: "III · Ascensión"}
        by_act = {1: [], 2: [], 3: []}
        for q in QUESTS:
            by_act.setdefault(q.get("act", 1), []).append(q)

        lines = ["|MTerminal Academy — Bitácora de quests|n", ""]
        hidden = 0
        visible_any = False

        for act_num in sorted(by_act):
            act_quests = by_act[act_num]
            # Solo muestra el acto si alguna quest está desbloqueada/completa
            any_visible = any(
                (q["id"] in done) or (q.get("room", "home") in visited)
                for q in act_quests
            )
            if not any_visible:
                # Acto oculto entero
                hidden += len(act_quests)
                continue
            visible_any = True
            lines.append(f"  |yActo {ACT_NAMES.get(act_num, act_num)}|n")
            for q in act_quests:
                room = q.get("room", "home")
                if q["id"] in done:
                    mark = "|g✓|n"
                elif room in visited:
                    mark = "|x·|n"
                else:
                    hidden += 1
                    continue
                cmd_label = q["cmd"]
                # Etiquetas más legibles para cmds con :
                if ":" in cmd_label:
                    cmd_label = cmd_label.replace(":", " ")
                lines.append(
                    f"    {mark} |w{cmd_label:<18}|n +{q['reward']:>3} $TERM — {q['desc']}"
                )
            lines.append("")

        if hidden:
            lines.append(
                f"  |x· {hidden} quest(s) oculta(s) — explora más rooms para descubrirlas.|n"
            )
            lines.append("")

        if not visible_any:
            lines.append("  (sin quests aún — empieza con |wls|n)")
            lines.append("")

        total = sum(q["reward"] for q in QUESTS)
        earned = sum(q["reward"] for q in QUESTS if q["id"] in done)
        lines.append(
            f"  |yProgreso:|n {len(done)}/{len(QUESTS)} quests · "
            f"{earned}/{total} $TERM ganados"
        )
        lines.append(f"  |yPendientes:|n |y{caller.db.abyss_pending} $TERM|n  (usa |wclaim|n)")
        w = caller.db.wallet or "(sin linkear)"
        ens = caller.db.wallet_ens or ""
        wdisplay = f"|c{w}|n" + (f" |y({ens})|n" if ens else "")
        lines.append(f"  |yWallet:|n     {wdisplay}")
        caller.msg("\n".join(lines))


class CmdClaim(Command):
    """
    Reclama tus $TERM pendientes en Monad testnet (transfer onchain).

    Usage:
      claim
    """
    key = "claim"
    locks = "cmd:all()"
    help_category = "Monad"

    def func(self):
        caller = self.caller
        _ensure_state(caller)
        _record_history(caller, "claim", "")
        wallet = caller.db.wallet
        pending = int(caller.db.abyss_pending or 0)
        if not wallet:
            caller.msg("|rError:|n no tienes wallet linkeada. Usa |wlink 0x...|n primero.")
            return
        if pending <= 0:
            caller.msg("No tienes $TERM pendientes. Completa quests primero con |wquests|n.")
            return

        try:
            from abyss_node.onchain import send_abyss, CONTRACT_ADDR
        except Exception:
            from onchain import send_abyss, CONTRACT_ADDR  # fallback

        # Fallback UX cuando el contrato aún no está deployado
        if not CONTRACT_ADDR:
            caller.msg(
                f"\n|y╭─ CLAIM PENDIENTE ────────────────╮|n\n"
                f"|y│|n  Contrato |yaún no deployado|n en Monad testnet.\n"
                f"|y│|n  Tienes |y{pending} $TERM|n reservados para |c{wallet}|n.\n"
                f"|y│|n  Cuando el admin deploye, re-corre |wclaim|n y recibes onchain.\n"
                f"|y╰────────────────────────────────────╯|n"
            )
            return

        try:
            tx_hash, explorer_url = send_abyss(wallet, pending)
        except Exception as e:
            logger.log_err(f"claim failed: {e}")
            caller.msg(f"|rError onchain:|n {e}")
            return

        caller.db.abyss_pending = 0
        caller.msg(
            f"\n|g╭─ CLAIM ENVIADO ──────────────────╮|n\n"
            f"|g│|n  |y{pending} $TERM|n → |c{wallet}|n\n"
            f"|g│|n  tx: |w{tx_hash}|n\n"
            f"|g│|n  explorer: {explorer_url}\n"
            f"|g╰────────────────────────────────────╯|n"
        )


# ---------- Comandos extendidos (Sesión A) ----------
def _wc_stats(text):
    """Imita `wc`: (líneas, palabras, bytes) — wc cuenta `\\n`, así que 'foo' (sin \\n) = 0 líneas."""
    raw = text or ""
    lines = raw.count("\n")
    words = len(raw.split())
    chars = len(raw.encode("utf-8"))
    return lines, words, chars


def _head_lines(text, n=10):
    lines = (text or "").splitlines()
    return "\n".join(lines[:n])


def _tail_lines(text, n=10):
    lines = (text or "").splitlines()
    return "\n".join(lines[-n:]) if lines else ""


def _apply_pipe(text, pipe_cmd, pipe_args):
    """Aplica un comando de pipe simulado al 'stdout' (text). Devuelve nuevo string."""
    pipe_cmd = (pipe_cmd or "").lower()
    pipe_args = (pipe_args or "").strip()
    if pipe_cmd == "wc":
        # `wc -l` → líneas, `wc -w` → palabras, `wc -c` → bytes, default → "L W C"
        l, w, c = _wc_stats(text if text.endswith("\n") else text + "\n")
        if pipe_args == "-l":
            return str(l)
        if pipe_args == "-w":
            return str(w)
        if pipe_args == "-c":
            return str(c)
        return f"{l} {w} {c}"
    if pipe_cmd == "grep":
        if not pipe_args:
            return "grep: usage: grep <patrón>"
        pat = pipe_args.split(None, 1)[0]
        hits = [ln for ln in (text or "").splitlines() if pat in ln]
        return "\n".join(hits)
    if pipe_cmd == "head":
        n = 10
        if pipe_args.startswith("-n"):
            try:
                n = int(pipe_args[2:].strip() or "10")
            except ValueError:
                pass
        return _head_lines(text, n)
    if pipe_cmd == "tail":
        n = 10
        if pipe_args.startswith("-n"):
            try:
                n = int(pipe_args[2:].strip() or "10")
            except ValueError:
                pass
        return _tail_lines(text, n)
    return f"{pipe_cmd}: command not supported in pipe"


def _parse_echo_args(args):
    """
    Parser sencillo: detecta '|', '>>', '>'. Sin soporte de quotes.
    Retorna (text, pipe_cmd, pipe_args, redirect_op, redirect_file).
    """
    pipe_cmd = None
    pipe_args = None
    redirect_op = None
    redirect_file = None
    remainder = args

    # 1) pipe (primera aparición)
    if "|" in remainder:
        left, right = remainder.split("|", 1)
        remainder = left
        pipe_parts = right.strip().split(None, 1)
        if pipe_parts:
            pipe_cmd = pipe_parts[0]
            pipe_args = pipe_parts[1] if len(pipe_parts) > 1 else ""

    # 2) redirect (>> antes que >)
    for op in (">>", ">"):
        if op in remainder:
            text_part, file_part = remainder.rsplit(op, 1)
            remainder = text_part
            redirect_op = op
            redirect_file = file_part.strip()
            break

    # Shell echo normaliza espacios — igualamos: strip externo, un espacio interno
    text = " ".join(remainder.split())
    return text, pipe_cmd, pipe_args, redirect_op, redirect_file


class CmdEcho(Command):
    """
    Imprime texto en stdout. Soporta redirect (`>`, `>>`) y pipe (`|`).

    Usage:
      echo <texto>
      echo <texto> > <archivo>      (escribe sobreescribiendo)
      echo <texto> >> <archivo>     (añade al final)
      echo <texto> | wc             (cuenta líneas, palabras, bytes)
      echo <texto> | grep <pat>     (filtra líneas que contienen pat)
      echo <texto> | head [-n N]
      echo <texto> | tail [-n N]
    """
    key = "echo"
    locks = "cmd:all()"
    help_category = "Terminal"

    def func(self):
        caller = self.caller
        _ensure_state(caller)
        raw = self.args or ""
        if raw.startswith(" "):
            raw = raw[1:]
        _record_history(caller, "echo", raw)
        loc = caller.location

        text, pipe_cmd, pipe_args, redirect_op, redirect_file = _parse_echo_args(raw)

        # Pipeline: primero el pipe, luego el redirect del resultado
        output = text
        if pipe_cmd:
            output = _apply_pipe(text, pipe_cmd, pipe_args)

        if redirect_op:
            if not redirect_file:
                caller.msg("echo: redirección sin destino")
                return
            if not loc:
                caller.msg("(sin ubicación)")
                return
            append = (redirect_op == ">>")
            _write_player_file(caller, loc, redirect_file, output + "\n", append=append)
            caller.msg(f"(escrito) {redirect_file}")
        else:
            caller.msg(output)

        _reward_if_quest(caller, "echo")


class CmdHead(Command):
    """
    Muestra las primeras líneas de un archivo (10 por defecto).

    Usage:
      head <archivo>
      head -n <N> <archivo>
    """
    key = "head"
    locks = "cmd:all()"
    help_category = "Terminal"

    def func(self):
        caller = self.caller
        _ensure_state(caller)
        raw = (self.args or "").strip()
        _record_history(caller, "head", raw)
        if not raw:
            caller.msg("usage: head [-n N] <archivo>")
            return
        n = 10
        parts = raw.split()
        if parts[0] == "-n" and len(parts) >= 3:
            try:
                n = int(parts[1])
            except ValueError:
                caller.msg(f"head: invalid number of lines: '{parts[1]}'")
                return
            fname = " ".join(parts[2:])
        else:
            fname = raw
        merged = _get_room_files(caller.location, caller)
        if fname not in merged:
            caller.msg(f"head: {fname}: No such file or directory")
            return
        caller.msg(_head_lines(merged[fname] or "", n))
        _reward_if_quest(caller, "head")


class CmdTail(Command):
    """
    Muestra las últimas líneas de un archivo (10 por defecto).

    Usage:
      tail <archivo>
      tail -n <N> <archivo>
    """
    key = "tail"
    locks = "cmd:all()"
    help_category = "Terminal"

    def func(self):
        caller = self.caller
        _ensure_state(caller)
        raw = (self.args or "").strip()
        _record_history(caller, "tail", raw)
        if not raw:
            caller.msg("usage: tail [-n N] <archivo>")
            return
        n = 10
        parts = raw.split()
        if parts[0] == "-n" and len(parts) >= 3:
            try:
                n = int(parts[1])
            except ValueError:
                caller.msg(f"tail: invalid number of lines: '{parts[1]}'")
                return
            fname = " ".join(parts[2:])
        else:
            fname = raw
        merged = _get_room_files(caller.location, caller)
        if fname not in merged:
            caller.msg(f"tail: {fname}: No such file or directory")
            return
        caller.msg(_tail_lines(merged[fname] or "", n))
        _reward_if_quest(caller, "tail")


class CmdWC(Command):
    """
    Cuenta líneas, palabras y bytes de un archivo.

    Usage:
      wc <archivo>
      wc -l <archivo>   (solo líneas)
      wc -w <archivo>   (solo palabras)
      wc -c <archivo>   (solo bytes)
    """
    key = "wc"
    locks = "cmd:all()"
    help_category = "Terminal"

    def func(self):
        caller = self.caller
        _ensure_state(caller)
        raw = (self.args or "").strip()
        _record_history(caller, "wc", raw)
        if not raw:
            caller.msg("usage: wc [-l|-w|-c] <archivo>")
            return
        parts = raw.split()
        flag = None
        if parts[0] in ("-l", "-w", "-c"):
            if len(parts) < 2:
                caller.msg("usage: wc [-l|-w|-c] <archivo>")
                return
            flag = parts[0]
            fname = " ".join(parts[1:])
        else:
            fname = raw
        merged = _get_room_files(caller.location, caller)
        if fname not in merged:
            caller.msg(f"wc: {fname}: No such file or directory")
            return
        content = merged[fname] or ""
        # wc cuenta líneas como \n — aseguramos un trailing newline si falta
        padded = content if content.endswith("\n") or content == "" else content + "\n"
        l, w, c = _wc_stats(padded)
        if flag == "-l":
            caller.msg(f"{l} {fname}")
        elif flag == "-w":
            caller.msg(f"{w} {fname}")
        elif flag == "-c":
            caller.msg(f"{c} {fname}")
        else:
            caller.msg(f"{l:>7} {w:>7} {c:>7} {fname}")
        _reward_if_quest(caller, "wc")


class CmdWhoAmI(Command):
    """
    Imprime el nombre del usuario actual.

    Usage:
      whoami
    """
    key = "whoami"
    locks = "cmd:all()"
    help_category = "Terminal"

    def func(self):
        caller = self.caller
        _ensure_state(caller)
        _record_history(caller, "whoami", "")
        name = caller.key or "player"
        caller.msg(name.lower())
        _reward_if_quest(caller, "whoami")


MAN_PAGES = {
    "ls": (
        "LS(1) — lista contenido de directorios\n\n"
        "USAGE\n    ls\n\nDESCRIPTION\n"
        "    Muestra archivos y subdirectorios del directorio actual.\n"
        "    En Terminal Academy las salidas son subdirectorios y los items del room son archivos."
    ),
    "pwd": (
        "PWD(1) — print working directory\n\n"
        "USAGE\n    pwd\n\nDESCRIPTION\n"
        "    Imprime la ruta del directorio (sala) actual."
    ),
    "cd": (
        "CD(1) — change directory\n\n"
        "USAGE\n    cd <destino>\n    cd ..\n\nDESCRIPTION\n"
        "    Muévete a un subdirectorio adyacente. `cd ..` intenta volver al anterior."
    ),
    "cat": (
        "CAT(1) — concatenar/mostrar archivos\n\n"
        "USAGE\n    cat <archivo>\n\nDESCRIPTION\n"
        "    Imprime el contenido completo de un archivo."
    ),
    "touch": (
        "TOUCH(1) — crea archivo vacío\n\n"
        "USAGE\n    touch <archivo>\n\nDESCRIPTION\n"
        "    Crea un archivo nuevo y vacío si no existe."
    ),
    "mkdir": (
        "MKDIR(1) — crea directorio\n\n"
        "USAGE\n    mkdir <nombre>\n\nDESCRIPTION\n"
        "    Crea un directorio virtual en el fs actual."
    ),
    "grep": (
        "GREP(1) — busca patrón en archivo\n\n"
        "USAGE\n    grep <patrón> <archivo>\n\nDESCRIPTION\n"
        "    Imprime las líneas de <archivo> que contienen <patrón>."
    ),
    "echo": (
        "ECHO(1) — imprime texto\n\n"
        "USAGE\n    echo <texto>\n    echo <texto> > <archivo>\n"
        "    echo <texto> >> <archivo>\n    echo <texto> | <cmd>\n\n"
        "DESCRIPTION\n"
        "    Imprime <texto>. Con `>` escribe al archivo, con `>>` hace append, con `|`\n"
        "    envía el output a otro comando (wc, grep, head, tail)."
    ),
    "head": (
        "HEAD(1) — primeras líneas\n\n"
        "USAGE\n    head <archivo>\n    head -n <N> <archivo>\n\nDESCRIPTION\n"
        "    Imprime las primeras N líneas (default 10)."
    ),
    "tail": (
        "TAIL(1) — últimas líneas\n\n"
        "USAGE\n    tail <archivo>\n    tail -n <N> <archivo>\n\nDESCRIPTION\n"
        "    Imprime las últimas N líneas (default 10)."
    ),
    "wc": (
        "WC(1) — cuenta líneas/palabras/bytes\n\n"
        "USAGE\n    wc <archivo>\n    wc -l|-w|-c <archivo>\n\nDESCRIPTION\n"
        "    Con flags: -l solo líneas, -w solo palabras, -c solo bytes."
    ),
    "whoami": (
        "WHOAMI(1) — nombre del usuario actual\n\n"
        "USAGE\n    whoami\n\nDESCRIPTION\n"
        "    Imprime el nombre (login) del usuario que corre la shell."
    ),
    "man": (
        "MAN(1) — páginas de manual\n\n"
        "USAGE\n    man <comando>\n\nDESCRIPTION\n"
        "    Muestra documentación del comando indicado."
    ),
    "history": (
        "HISTORY(1) — historial de comandos\n\n"
        "USAGE\n    history\n\nDESCRIPTION\n"
        "    Muestra los comandos que has ejecutado en esta sesión, numerados."
    ),
    "clear": (
        "CLEAR(1) — limpia la terminal\n\n"
        "USAGE\n    clear\n\nDESCRIPTION\n"
        "    Envía saltos de línea para limpiar visualmente la pantalla del cliente."
    ),
    "link": (
        "LINK(1) — conecta wallet EVM\n\n"
        "USAGE\n    link <0x...>\n\nDESCRIPTION\n"
        "    Asocia tu wallet EVM (42 chars) para recibir $TERM onchain con `claim`."
    ),
    "quests": (
        "QUESTS(1) — lista de quests\n\n"
        "USAGE\n    quests\n\nDESCRIPTION\n"
        "    Muestra quests completadas y pendientes con sus recompensas en $TERM."
    ),
    "claim": (
        "CLAIM(1) — reclama $TERM onchain\n\n"
        "USAGE\n    claim\n\nDESCRIPTION\n"
        "    Transfiere tus $TERM pendientes a la wallet linkeada en Monad testnet."
    ),
    "claude": (
        "CLAUDE(1) — CLI de IA para generar código\n\n"
        "USAGE\n"
        "    claude                               (info y flujo)\n"
        "    claude skills list                   (ver skills disponibles)\n"
        "    claude skills installed              (los tuyos)\n"
        "    claude skills install <owner/slug>   (descargar e instalar)\n"
        "    claude new contract <Nombre>         (genera <Nombre>.sol)\n"
        "    claude new token <SYMBOL>            (genera token.sol)\n"
        "    claude deploy <archivo.sol>          (simula deploy Monad testnet)\n\n"
        "DESCRIPTION\n"
        "    Meta-tool que simula el CLI real de Claude Code. El flujo pedagógico:\n"
        "      1) `claude skills install portdeveloper/monad-development`\n"
        "      2) `claude new contract MiToken`\n"
        "      3) `claude deploy MiToken.sol`\n"
        "    Cada paso completa una quest y acumula $TERM."
    ),
}


class CmdMan(Command):
    """
    Consulta el manual de un comando.

    Usage:
      man <comando>
    """
    key = "man"
    locks = "cmd:all()"
    help_category = "Terminal"

    def func(self):
        caller = self.caller
        _ensure_state(caller)
        arg = (self.args or "").strip().lower()
        _record_history(caller, "man", arg)
        if not arg:
            caller.msg("What manual page do you want?\nusage: man <comando>")
            return
        page = MAN_PAGES.get(arg)
        if page is None:
            caller.msg(f"No manual entry for {arg}")
            return
        caller.msg(f"|x──────|n\n{page}\n|x──────|n")
        _reward_if_quest(caller, "man")


class CmdClear(Command):
    """
    Limpia la terminal (envía saltos de línea al cliente).

    Usage:
      clear
    """
    key = "clear"
    aliases = ["cls"]
    locks = "cmd:all()"
    help_category = "Terminal"

    def func(self):
        caller = self.caller
        _ensure_state(caller)
        _record_history(caller, "clear", "")
        # No hay forma universal de borrar el buffer de Evennia webclient — emulamos con \n
        caller.msg("\n" * 40)


class CmdHistory(Command):
    """
    Muestra los últimos comandos que ejecutaste en esta cuenta.

    Usage:
      history
      history <N>      (mostrar solo las últimas N)
    """
    key = "history"
    locks = "cmd:all()"
    help_category = "Terminal"

    def func(self):
        caller = self.caller
        _ensure_state(caller)
        arg = (self.args or "").strip()
        _record_history(caller, "history", arg)
        hist = list(caller.db.cmd_history or [])
        if arg:
            try:
                n = int(arg)
                hist = hist[-n:]
            except ValueError:
                caller.msg(f"history: numeric argument required, got '{arg}'")
                return
        if not hist:
            caller.msg("(sin historial)")
            return
        # Excluye el propio `history` que acabamos de registrar
        display = hist[:-1] if hist and hist[-1].startswith("history") else hist
        lines = [f"  {i+1:>4}  {cmd}" for i, cmd in enumerate(display)]
        caller.msg("\n".join(lines) if lines else "(sin historial)")
        _reward_if_quest(caller, "history")


# ---------- Claude CLI: meta-tool para generar código con IA ----------
AVAILABLE_SKILLS = {
    "austin-griffith/scaffold-eth": {
        "name": "Scaffold-ETH starter",
        "author": "Austin Griffith",
        "desc": "Quickstart para dApps: Hardhat + Next.js + Wagmi preconfigurados.",
    },
    "austin-griffith/solidity-basics": {
        "name": "Solidity basics",
        "author": "Austin Griffith",
        "desc": "Patrones de Solidity: ERC-20, ERC-721, access control, eventos.",
    },
    "portdeveloper/monad-development": {
        "name": "Monad development (oficial)",
        "author": "portdeveloper",
        "desc": (
            "Skill real open-source para Monad: Foundry + viem + wagmi, faucet "
            "via agents.devnads.com, verificación automática en MonadVision + "
            "Socialscan + Monadscan, evmVersion 'prague' por default."
        ),
    },
    "anthropic/claude-code-guide": {
        "name": "Claude Code usage guide",
        "author": "Anthropic",
        "desc": "Cómo usar Claude Code CLI eficientemente (hooks, slash commands, MCP).",
    },
}

# Skills que desbloquean `claude deploy` en Monad testnet.
# NOTA: el skill oficial de Monad es portdeveloper/monad-development (no es de Austin Griffith;
# Austin publica otros skills para Solidity/Scaffold-ETH, pero el de Monad es independiente).
DEPLOY_ENABLING_SKILLS = frozenset({
    "portdeveloper/monad-development",
})


_CONTRACT_TEMPLATE = """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// @title {name}
/// @notice Contrato generado por Claude en Terminal Academy.
/// @dev ERC-20 mínimo — sin dependencias externas.
contract {name} {{
    string public constant name = "{name}";
    string public constant symbol = "{symbol}";
    uint8  public constant decimals = 18;
    uint256 public totalSupply;
    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;

    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);

    constructor(uint256 initialSupply) {{
        totalSupply = initialSupply;
        balanceOf[msg.sender] = initialSupply;
        emit Transfer(address(0), msg.sender, initialSupply);
    }}

    function transfer(address to, uint256 value) external returns (bool) {{
        _transfer(msg.sender, to, value);
        return true;
    }}

    function approve(address spender, uint256 value) external returns (bool) {{
        allowance[msg.sender][spender] = value;
        emit Approval(msg.sender, spender, value);
        return true;
    }}

    function transferFrom(address from, address to, uint256 value) external returns (bool) {{
        uint256 allowed = allowance[from][msg.sender];
        require(allowed >= value, "allowance");
        if (allowed != type(uint256).max) allowance[from][msg.sender] = allowed - value;
        _transfer(from, to, value);
        return true;
    }}

    function _transfer(address from, address to, uint256 value) internal {{
        require(balanceOf[from] >= value, "balance");
        unchecked {{ balanceOf[from] -= value; }}
        balanceOf[to] += value;
        emit Transfer(from, to, value);
    }}
}}
"""


class CmdClaude(Command):
    """
    Claude CLI — el meta-tool de IA para generar código, instalar skills y deployar.

    Usage:
      claude                               (info y flujo)
      claude skills                        (lista skills disponibles)
      claude skills list
      claude skills installed              (lo que tienes instalado)
      claude skills install <owner/slug>   (descarga e instala un skill)
      claude new contract <Nombre>         (genera <Nombre>.sol en tu fs)
      claude new token <SYMBOL>            (genera token.sol)
      claude deploy <archivo.sol>          (simula deploy en Monad testnet)

    Ejemplo del flujo completo que enseña la Academia:
      1) claude skills install portdeveloper/monad-development
      2) claude new contract MiToken
      3) claude deploy MiToken.sol
    """
    key = "claude"
    locks = "cmd:all()"
    help_category = "Claude"

    # --- helpers -----------------------------------------------------------
    def _ensure_claude_state(self, caller):
        if caller.db.installed_skills is None:
            caller.db.installed_skills = []
        if caller.db.deployed_contracts is None:
            caller.db.deployed_contracts = []

    def _banner(self, caller):
        caller.msg(
            "\n|c╭─ Claude CLI ─────────────────────────────────────────╮|n\n"
            "|c│|n  IA que genera, debuggea y deploya código desde la terminal.\n"
            "|c│|n  Modelo activo: |wclaude-opus-4-7|n · cwd: |w{cwd}|n\n"
            "|c│|n\n"
            "|c│|n  Subcomandos:\n"
            "|c│|n    |wclaude skills list|n                     — ver skills\n"
            "|c│|n    |wclaude skills install <owner/slug>|n     — instalar\n"
            "|c│|n    |wclaude new contract <Nombre>|n           — Solidity stub\n"
            "|c│|n    |wclaude deploy <file.sol>|n               — Monad testnet\n"
            "|c╰──────────────────────────────────────────────────────╯|n".format(
                cwd=f"/academy/{caller.location.key}" if caller.location else "/",
            )
        )

    # --- subcommand dispatch ----------------------------------------------
    def func(self):
        caller = self.caller
        _ensure_state(caller)
        self._ensure_claude_state(caller)
        raw = (self.args or "").strip()
        _record_history(caller, "claude", raw)

        if not raw:
            self._banner(caller)
            _reward_if_quest(caller, "claude")
            return

        parts = raw.split()
        sub = parts[0].lower()
        rest = parts[1:]

        if sub in ("help", "-h", "--help"):
            self._banner(caller)
            _reward_if_quest(caller, "claude")
            return

        if sub == "skills":
            self._cmd_skills(caller, rest)
            _reward_if_quest(caller, "claude")
            return

        if sub == "new":
            self._cmd_new(caller, rest)
            _reward_if_quest(caller, "claude")
            return

        if sub == "deploy":
            self._cmd_deploy(caller, rest)
            _reward_if_quest(caller, "claude")
            return

        caller.msg(f"claude: subcomando desconocido '{sub}'. Prueba: |wclaude help|n")
        _reward_if_quest(caller, "claude")

    # --- subcommand: skills -----------------------------------------------
    def _cmd_skills(self, caller, rest):
        if not rest or rest[0] in ("list", "ls"):
            caller.msg("|ySkills disponibles:|n")
            for slug, meta in AVAILABLE_SKILLS.items():
                caller.msg(f"  |w{slug}|n  — {meta['name']} ({meta['author']})\n      {meta['desc']}")
            caller.msg("\nInstala con: |wclaude skills install <slug>|n")
            return

        action = rest[0].lower()
        if action == "installed":
            inst = list(caller.db.installed_skills or [])
            if not inst:
                caller.msg("(sin skills instalados — usa |wclaude skills install <slug>|n)")
                return
            caller.msg("|ySkills instalados:|n")
            for slug in inst:
                meta = AVAILABLE_SKILLS.get(slug, {"name": slug, "author": "?", "desc": ""})
                caller.msg(f"  |g✓|n |w{slug}|n — {meta.get('name', slug)}")
            return

        if action == "install":
            if len(rest) < 2:
                caller.msg("usage: claude skills install <owner/slug>")
                return
            slug = rest[1]
            if slug not in AVAILABLE_SKILLS:
                caller.msg(
                    f"|rclaude:|n skill '{slug}' no encontrado.\n"
                    f"Lista disponibles con: |wclaude skills list|n"
                )
                return
            inst = list(caller.db.installed_skills or [])
            if slug in inst:
                caller.msg(f"(ya tenías '{slug}' instalado)")
                return
            inst.append(slug)
            caller.db.installed_skills = inst
            meta = AVAILABLE_SKILLS[slug]
            caller.msg(
                f"\n|g→|n Descargando |w{slug}|n ...\n"
                f"|g→|n {meta['desc']}\n"
                f"|g✓|n Skill instalado. Ya puedes invocar sus capacidades (ej. "
                f"|wclaude new contract <Nombre>|n)."
            )
            _reward_if_quest(caller, "claude:skill")
            return

        caller.msg(f"claude skills: acción desconocida '{action}'")

    # --- subcommand: new --------------------------------------------------
    def _cmd_new(self, caller, rest):
        if len(rest) < 2:
            caller.msg("usage: claude new <contract|token> <Nombre>")
            return
        kind = rest[0].lower()
        name = rest[1]

        if not caller.db.installed_skills:
            caller.msg(
                "|yclaude:|n ningún skill instalado todavía.\n"
                "Instala primero: |wclaude skills install austin-griffith/solidity-basics|n"
            )
            return

        if kind not in ("contract", "token"):
            caller.msg("usage: claude new <contract|token> <Nombre>")
            return

        if not name.isidentifier():
            caller.msg(f"|rclaude:|n '{name}' no es un identificador Solidity válido.")
            return

        symbol = (name[:4]).upper() if kind == "token" else name.upper()[:6]
        contents = _CONTRACT_TEMPLATE.format(name=name, symbol=symbol)
        filename = f"{name}.sol"
        loc = caller.location
        if not loc:
            caller.msg("(sin ubicación)")
            return
        _write_player_file(caller, loc, filename, contents, append=False)
        lines = contents.count("\n")
        caller.msg(
            f"\n|g→|n Generando |w{filename}|n con Claude (skill: solidity-basics)...\n"
            f"|g✓|n Escrito {lines} líneas en |w{filename}|n.\n"
            f"Revisa con |wcat {filename}|n. Deploya con |wclaude deploy {filename}|n."
        )
        _reward_if_quest(caller, "claude:new")

    # --- subcommand: deploy -----------------------------------------------
    def _cmd_deploy(self, caller, rest):
        if not rest:
            caller.msg("usage: claude deploy <archivo.sol>")
            return
        fname = rest[0]
        loc = caller.location
        merged = _get_room_files(loc, caller)
        if fname not in merged:
            caller.msg(f"|rclaude deploy:|n {fname}: No such file or directory")
            return
        src = merged[fname] or ""
        if "contract " not in src:
            caller.msg(f"|rclaude deploy:|n {fname} no parece Solidity (sin `contract`).")
            return
        installed = set(caller.db.installed_skills or [])
        if not (installed & DEPLOY_ENABLING_SKILLS):
            caller.msg(
                "|yclaude:|n para deployar en Monad necesitas el skill oficial.\n"
                "Instálalo: |wclaude skills install portdeveloper/monad-development|n\n"
                "(incluye verificación auto en MonadVision / Socialscan / Monadscan, "
                "Foundry + viem + wagmi, faucet via agents.devnads.com)"
            )
            return

        # Construir una address + tx hash pseudo-determinísticos (no onchain real).
        import hashlib
        seed = f"{caller.key}:{fname}:{len(caller.db.deployed_contracts or [])}".encode()
        h = hashlib.sha256(seed).hexdigest()
        fake_addr = "0x" + h[:40]
        fake_tx = "0x" + h[24:88]

        deployed = list(caller.db.deployed_contracts or [])
        deployed.append({"file": fname, "address": fake_addr, "tx": fake_tx})
        caller.db.deployed_contracts = deployed

        # Si instaló el skill oficial con auto-verify, mostramos una línea extra
        verify_line = ""
        if "portdeveloper/monad-development" in installed:
            verify_line = (
                f"|g│|n  verify:   |gauto-verificado|n en MonadVision + Socialscan + Monadscan\n"
                f"|g│|n            POST agents.devnads.com/v1/verify (skill portdeveloper)\n"
            )

        caller.msg(
            f"\n|g╭─ claude deploy → Monad testnet ──────────────────╮|n\n"
            f"|g│|n  source:   |w{fname}|n ({src.count(chr(10))} líneas)\n"
            f"|g│|n  network:  |wMonad testnet (chainId 10143)|n\n"
            f"|g│|n  address:  |y{fake_addr}|n\n"
            f"|g│|n  tx:       |w{fake_tx}|n\n"
            f"|g│|n  explorer: https://testnet.monadexplorer.com/address/{fake_addr}\n"
            f"{verify_line}"
            f"|g│|n  |x(deploy simulado — para deploy real usa Foundry + PRIVATE_KEY)|n\n"
            f"|g╰──────────────────────────────────────────────────╯|n"
        )
        _reward_if_quest(caller, "claude:deploy")
