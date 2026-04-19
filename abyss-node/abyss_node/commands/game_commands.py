"""
game_commands.py — gameplay extendido de Terminal Academy (Sesión D).

Añade profundidad de juego más allá de teclear y recibir $TERM:
  solve <puzzle>         → verifica puzzles grep/pipe analizando historial
  fight corruptor        → inicia combate por turnos con el Eco del Corruptor
  scan                   → escanea el room actual (pistas de puzzles/corruptor)
  reconstruct <archivo>  → restaura archivo corrupto durante la pelea
  reconstruct memory     → cinemática final al tener los 10 fragmentos
  inventory_mem          → lista los fragmentos de memoria recolectados
  leaderboard            → top 10 speedruns (más rápidos en hacer claim)
  sudo                   → easter egg (sin args → chiste del Prof)
  rm -rf /               → easter egg con cuenta regresiva + 'cancel' → trophy

Hooks:
  - Al primer login (o primer comando), se setea `caller.db.run_started`.
  - Al `claim` exitoso, `onchain.send_abyss` debería triggerear el cálculo
    de `run_duration` (expuesto vía `capture_run_duration`).
"""

import time

from evennia import Command
from evennia.utils import delay, logger

from utils.narrator import (
    narrate,
    dialogue,
    scene,
    achievement,
    error_sys,
    terminal,
)

from world.quests.puzzles import (
    PUZZLES,
    PUZZLES_BY_ID,
    ensure_puzzles_state,
    mark_puzzle_done,
    is_puzzle_done,
    CRYPTO_TOKEN,
    CORRUPTOR_FILES,
    CORRUPTOR_FILES_BY_NAME,
    corrupt_text,
    generate_crypto_log,
    generate_mensaje_enc,
)


def _ensure_puzzle_file_in_room(room, puzzle_id: str):
    """
    Garantiza que el archivo del puzzle existe en room.db.academy_files.
    Idempotente: si ya está sembrado, no re-siembra (evita trabajo en cada ls).
    """
    if not room:
        return
    puzzle = PUZZLES_BY_ID.get(puzzle_id)
    if not puzzle or puzzle["room"] != room.key:
        return
    files = dict(room.db.academy_files or {})
    if puzzle["filename"] in files and files[puzzle["filename"]]:
        return
    if puzzle_id == "grep_token":
        files[puzzle["filename"]] = generate_crypto_log()
    elif puzzle_id == "pipe_count":
        files[puzzle["filename"]] = generate_mensaje_enc()
    else:
        return
    room.db.academy_files = files


# ---------------------------------------------------------------------------
# Utilidades comunes
# ---------------------------------------------------------------------------
def _ensure_run_timer(caller):
    """Si es el primer comando gameplay, arranca el speedrun timer."""
    if caller.db.run_started is None:
        caller.db.run_started = time.time()


def _record_run_duration(caller):
    """
    Llamar justo cuando el jugador completa `claim`. Si run_started está seteado
    y run_duration aún no, calcula delta y lo guarda.
    """
    if caller.db.run_duration is not None:
        return
    start = caller.db.run_started
    if start is None:
        return
    caller.db.run_duration = max(0.0, time.time() - float(start))


def capture_run_duration(caller):
    """
    Helper público: exporta `_record_run_duration` para que otros módulos
    (ej. `terminal_commands.CmdClaim` o `onchain`) puedan triggerearlo.
    """
    _record_run_duration(caller)


def _get_cmd_history(caller, n=5):
    """Devuelve las últimas N líneas de `caller.db.cmd_history` (lista de str)."""
    hist = list(caller.db.cmd_history or [])
    return hist[-n:] if hist else []


def _emit_prompt(caller):
    """Reemite el prompt estilo shell tras un comando gameplay."""
    loc = caller.location
    path = f"/academy/{loc.key}" if loc else "/academy"
    name = caller.key or "you"
    try:
        caller.msg(prompt=f"|g{name}@academy|n:|c{path}|n|w$|n ")
    except Exception:
        pass


def _apply_reward(caller, amount: int):
    """Suma $TERM pendientes de forma segura."""
    if caller.db.abyss_pending is None:
        caller.db.abyss_pending = 0
    caller.db.abyss_pending = int(caller.db.abyss_pending) + int(amount)


# ---------------------------------------------------------------------------
# Comando: solve <puzzle>
# ---------------------------------------------------------------------------
class CmdSolve(Command):
    """
    Verifica si resolviste un puzzle de este room.

    Usage:
      solve               (verifica puzzles del room actual)
      solve <puzzle_id>   (verifica puzzle específico: grep_token, pipe_count)

    Cómo funciona:
      - `solve` analiza tu `history` reciente en busca de la solución.
      - Si acertaste, marca el puzzle como completado y te da $TERM.
      - Para el puzzle `pipe_count`, ejecutaste algo tipo
        `cat mensaje.enc | grep clave | wc -l` → debe responder 3.
    """

    key = "solve"
    locks = "cmd:all()"
    help_category = "Gameplay"

    def func(self):
        caller = self.caller
        _ensure_run_timer(caller)
        ensure_puzzles_state(caller)
        arg = (self.args or "").strip().lower()
        loc = caller.location

        # Determinar qué puzzle verificar
        target_ids = []
        if arg:
            if arg in PUZZLES_BY_ID:
                target_ids = [arg]
            else:
                error_sys(caller, f"puzzle desconocido: '{arg}'. Prueba: grep_token, pipe_count")
                _emit_prompt(caller)
                return
        else:
            # Puzzles disponibles en el room actual
            if not loc:
                error_sys(caller, "sin ubicación")
                return
            target_ids = [p["id"] for p in PUZZLES if p["room"] == loc.key]
            if not target_ids:
                terminal(caller, "(este room no tiene puzzles — usa `scan` para buscar pistas)")
                _emit_prompt(caller)
                return

        history = _get_cmd_history(caller, n=10)
        any_solved = False

        for pid in target_ids:
            puzzle = PUZZLES_BY_ID[pid]
            if is_puzzle_done(caller, pid):
                terminal(caller, f"(ya habías resuelto el puzzle '{pid}')")
                continue

            solved = self._check_solution(pid, history, caller)
            if solved:
                any_solved = True
                mark_puzzle_done(caller, pid)
                _apply_reward(caller, puzzle["reward"])
                achievement(
                    caller,
                    puzzle["title"],
                    puzzle["body"],
                    reward=puzzle["reward"],
                )
            else:
                terminal(
                    caller,
                    f"(puzzle '{pid}' sin resolver — {puzzle['description']})",
                )

        if not any_solved and all(is_puzzle_done(caller, pid) for pid in target_ids):
            terminal(caller, "(ya habías resuelto todos los puzzles de este room)")

        _emit_prompt(caller)

    def _check_solution(self, puzzle_id: str, history: list, caller) -> bool:
        """
        Verifica si el historial reciente muestra una solución válida.
        Para puzzles que ya disparan reward al ejecutar el comando correcto,
        también respeta `caller.db.puzzles_done` si otro hook lo marcó.
        """
        # Permitir que otros hooks hayan marcado el puzzle
        state = ensure_puzzles_state(caller)
        if state.get(puzzle_id):
            return True

        joined = " ;; ".join(history).lower() if history else ""

        if puzzle_id == "grep_token":
            # Cualquier grep TOKEN sobre crypto_log.txt basta
            return (
                "grep" in joined
                and "token" in joined
                and "crypto_log.txt" in joined
            )

        if puzzle_id == "pipe_count":
            # Debe combinar: cat mensaje.enc  +  grep clave  +  wc -l
            has_cat = "cat mensaje.enc" in joined
            has_grep_clave = "grep clave" in joined
            has_wc_l = "wc -l" in joined or joined.rstrip().endswith(" wc")
            # La forma canónica es un one-liner con pipes, por eso todo en la
            # misma línea de historial cuenta más fuerte:
            for line in history:
                low = line.lower()
                if "cat mensaje.enc" in low and "grep clave" in low and "wc" in low:
                    return True
            return has_cat and has_grep_clave and has_wc_l

        return False


# ---------------------------------------------------------------------------
# Comando: scan (pistas contextuales del room)
# ---------------------------------------------------------------------------
class CmdScan(Command):
    """
    Escanea el room actual en busca de puzzles, fragmentos y actividad del Corruptor.

    Usage:
      scan

    No da reward — solo te orienta.
    """

    key = "scan"
    locks = "cmd:all()"
    help_category = "Gameplay"

    def func(self):
        caller = self.caller
        _ensure_run_timer(caller)
        loc = caller.location
        if not loc:
            error_sys(caller, "sin ubicación para escanear")
            return

        # Auto-siembra de archivos puzzle si el room es uno de ellos
        for p in PUZZLES:
            if p["room"] == loc.key:
                _ensure_puzzle_file_in_room(loc, p["id"])

        lines = [f"|cscan|n → |w{loc.key}|n"]
        # Puzzles
        room_puzzles = [p for p in PUZZLES if p["room"] == loc.key]
        if room_puzzles:
            lines.append("  |yPuzzles:|n")
            for p in room_puzzles:
                status = "|g✓ resuelto|n" if is_puzzle_done(caller, p["id"]) else "|r? pendiente|n"
                lines.append(f"    · |w{p['id']}|n ({status}) — {p['description']}")
        else:
            lines.append("  (sin puzzles en este room)")

        # Fragmento de memoria en este room
        try:
            from world.lore.fragments import FRAGMENTS
            frag_here = next((f for f in FRAGMENTS if f["room"] == loc.key), None)
            if frag_here:
                memories = set(caller.db.memories or [])
                collected = frag_here["id"] in memories
                mark = "|g✓ recolectado|n" if collected else "|r? pendiente|n"
                lines.append(
                    f"  |yFragmento:|n {mark} — |w{frag_here['filename']}|n "
                    f"(usa |wcat {frag_here['filename']}|n)"
                )
        except Exception:
            pass

        # Corruptor activity
        if loc.key == "final_exam":
            fight_state = caller.db.corruptor_fight
            if fight_state and fight_state.get("active"):
                lines.append(
                    f"  |rCombate activo:|n turno {fight_state.get('turn', 1)}/3 "
                    "— usa |wreconstruct <archivo>|n."
                )
            else:
                lines.append(
                    "  |yEco del Corruptor|n detectado. "
                    "Invoca el combate con |wfight corruptor|n."
                )

        # Hint de inventario si tiene fragmentos
        memories = list(caller.db.memories or [])
        if memories:
            lines.append(
                f"  |yMemoria:|n {len(memories)}/10 fragmentos — "
                "|winventory_mem|n para el detalle."
            )

        caller.msg("\n".join(lines))
        _emit_prompt(caller)


# ---------------------------------------------------------------------------
# Combate: El Eco del Corruptor
# ---------------------------------------------------------------------------
FIGHT_MAX_TURNS = 3

# Frases típicas del Corruptor en cada turno
_CORRUPTOR_LINES = [
    "Borro lo que no teclean. Este archivo ya no te pertenece.",
    "Tu sintaxis flaquea. ¿Puedes reconstruir lo que destruyo?",
    "Todavía queda algo por comerse. Tic-tac, neófito.",
]


def _new_fight_state() -> dict:
    return {
        "active": True,
        "turn": 0,
        "max_turns": FIGHT_MAX_TURNS,
        "corrupted": [],   # lista de nombres de archivos corrompidos
        "restored": [],    # lista de nombres reconstruidos
    }


def _pick_corruptor_target(state: dict) -> str:
    """Devuelve el siguiente archivo a corromper (sin repetir)."""
    used = set(state.get("corrupted", []))
    available = [f["name"] for f in CORRUPTOR_FILES if f["name"] not in used]
    if not available:
        # Si ya corrompió todos, recicla el primero
        return CORRUPTOR_FILES[0]["name"]
    return available[0]


def _apply_corruption(caller, room, target_name: str):
    """Escribe contenido corrupto en el archivo del room."""
    files = dict(room.db.academy_files or {})
    files[target_name] = corrupt_text(target_name)
    room.db.academy_files = files


def _restore_file(caller, room, target_name: str):
    """Restaura el contenido original del archivo."""
    orig = CORRUPTOR_FILES_BY_NAME.get(target_name)
    if not orig:
        return False
    files = dict(room.db.academy_files or {})
    files[target_name] = orig["original"]
    room.db.academy_files = files
    return True


def _end_fight(caller, win: bool):
    """Cierra el combate, aplica reward o castigo, emite cinemática."""
    state = caller.db.corruptor_fight or {}
    room = caller.location
    # Restaurar cualquier archivo aún corrupto (para que el room quede limpio)
    if room:
        for name in list(state.get("corrupted", [])):
            if name not in state.get("restored", []):
                _restore_file(caller, room, name)

    caller.db.corruptor_fight = None

    if win:
        scene(
            caller,
            "VICTORIA · PUREZA RESTAURADA",
            "El Eco retrocede al vacío. Los archivos vuelven a su forma. "
            "Por primera vez sientes que el filesystem respira.",
        )
        achievement(
            caller,
            "Pureza restaurada",
            "Venciste al Eco del Corruptor reconstruyendo todo lo que destruyó.",
            reward=100,
        )
        _apply_reward(caller, 100)
        # Flag de victoria persistente (para otros hooks)
        caller.db.corruptor_defeated = True
    else:
        scene(
            caller,
            "DERROTA · EL ECO SE RETIRA",
            "El Eco se desvanece riendo. Los archivos quedan medio comidos. "
            "Te llevas un escalofrío y pierdes 20 $TERM del bolsillo.",
        )
        # Penalización: restar 20 $TERM pendientes (sin bajar de 0)
        current = int(caller.db.abyss_pending or 0)
        caller.db.abyss_pending = max(0, current - 20)
        error_sys(caller, "Pierdes 20 $TERM pendientes. Inténtalo de nuevo con `fight corruptor`.")


def _do_corruptor_turn(caller):
    """
    Ejecuta el siguiente turno del Corruptor: incrementa turno y corrompe un
    nuevo archivo. Si tras corromper se llega al turno máximo y el jugador no
    reconstruyó todos los corrompidos → derrota. El chequeo de victoria se
    hace sólo tras reconstrucciones del jugador (ver `_reconstruct_file`).
    """
    state = caller.db.corruptor_fight
    if not state or not state.get("active"):
        return

    room = caller.location
    if not room:
        return

    state = dict(state)  # copy para evitar _SaverDict
    max_turns = state.get("max_turns", FIGHT_MAX_TURNS)
    turn = state.get("turn", 0) + 1
    state["turn"] = turn

    if turn > max_turns:
        # Se acabaron los turnos sin haber reconstruido todo → derrota
        caller.db.corruptor_fight = state
        _end_fight(caller, win=False)
        return

    corrupted = list(state.get("corrupted", []))
    target = _pick_corruptor_target(state)
    corrupted.append(target)
    state["corrupted"] = corrupted
    caller.db.corruptor_fight = state

    _apply_corruption(caller, room, target)

    line = _CORRUPTOR_LINES[(turn - 1) % len(_CORRUPTOR_LINES)]
    dialogue(caller, "Eco del Corruptor", f"{line} [corrompí {target}]")
    remaining = max_turns - turn
    caller.msg(
        f"|y[Turno {turn}/{max_turns}]|n El Corruptor destruyó |r{target}|n. "
        f"Reconstrúyelo con |wreconstruct {target}|n. "
        f"(quedan {remaining} turnos)"
    )

    # En el último turno, programar un check de derrota automática en 30s.
    # Si el jugador no reconstruye todo para entonces, se pierde.
    if turn >= max_turns:
        def _timeout_check(who):
            try:
                st = who.db.corruptor_fight
                if not st or not st.get("active"):
                    return
                corr = set(st.get("corrupted", []))
                rest = set(st.get("restored", []))
                if corr != rest:
                    _end_fight(who, win=False)
            except Exception:
                pass

        try:
            delay(30, _timeout_check, caller)
        except Exception:
            pass


class CmdFight(Command):
    """
    Inicia combate por turnos con el Eco del Corruptor (solo en /final_exam).

    Usage:
      fight corruptor

    Mecánica:
      - 3 turnos. En cada turno el Corruptor "corrompe" un archivo del room.
      - Tú debes `reconstruct <archivo>` para restaurar cada uno.
      - Reconstruye TODOS antes de que se acaben los turnos → ganas 100 $TERM.
      - Si fallas → pierdes 20 $TERM pendientes.
    """

    key = "fight"
    locks = "cmd:all()"
    help_category = "Gameplay"

    def func(self):
        caller = self.caller
        _ensure_run_timer(caller)
        arg = (self.args or "").strip().lower()
        loc = caller.location

        if arg not in ("corruptor", "eco", "boss", "el corruptor", "eco del corruptor"):
            terminal(caller, "Usage: |wfight corruptor|n  — solo en |c/final_exam|n.")
            _emit_prompt(caller)
            return

        if not loc or loc.key != "final_exam":
            error_sys(caller, "El Eco del Corruptor solo aparece en /final_exam. Ve primero con `cd final_exam`.")
            _emit_prompt(caller)
            return

        # Ya ganó antes → no dejar refarm
        if caller.db.corruptor_defeated:
            terminal(
                caller,
                "(ya derrotaste al Eco — su presencia aquí es sólo un recuerdo)",
            )
            _emit_prompt(caller)
            return

        # Ya hay pelea activa
        state = caller.db.corruptor_fight
        if state and state.get("active"):
            terminal(
                caller,
                f"(ya estás en combate, turno {state.get('turn', 1)}/{state.get('max_turns', FIGHT_MAX_TURNS)}). "
                "Usa |wreconstruct <archivo>|n.",
            )
            _emit_prompt(caller)
            return

        # Intro cinemática
        scene(
            caller,
            "COMBATE · EL ECO DEL CORRUPTOR",
            "El aire se vuelve estática. Los archivos del /final_exam "
            "empiezan a parpadear. Una voz sin cuerpo se pega a tu oído.",
        )
        dialogue(
            caller,
            "Eco del Corruptor",
            "Al fin nos vemos, neófito. Vine por lo que teclean los vivos. "
            "Veamos cuánto de ti puedes salvar en 3 turnos.",
        )
        caller.msg(
            "|yReglas del combate:|n\n"
            "  · Tienes 3 turnos. En cada turno corrompo un archivo del room.\n"
            "  · Reconstrúyelos con |wreconstruct <archivo>|n.\n"
            "  · Si reconstruyes todos → |g+100 $TERM|n. Si fallas → |r-20 $TERM|n."
        )

        caller.db.corruptor_fight = _new_fight_state()

        # Primer turno
        _do_corruptor_turn(caller)
        _emit_prompt(caller)


# ---------------------------------------------------------------------------
# reconstruct — doble uso: combate (archivo) + final (memory)
# ---------------------------------------------------------------------------
class CmdReconstruct(Command):
    """
    Reconstruye un archivo corrupto (durante el combate con el Corruptor)
    o la memoria completa (al tener los 10 fragmentos).

    Usage:
      reconstruct <archivo>   (durante `fight corruptor`)
      reconstruct memory      (cinemática final, requiere 10/10 fragmentos)
    """

    key = "reconstruct"
    aliases = ["restore"]
    locks = "cmd:all()"
    help_category = "Gameplay"

    def func(self):
        caller = self.caller
        _ensure_run_timer(caller)
        arg = (self.args or "").strip()
        if not arg:
            terminal(caller, "usage: reconstruct <archivo> | reconstruct memory")
            _emit_prompt(caller)
            return

        if arg.lower() == "memory":
            self._reconstruct_memory(caller)
            _emit_prompt(caller)
            return

        self._reconstruct_file(caller, arg)
        _emit_prompt(caller)

    # --- Reconstruir archivo durante el combate -----------------------------
    def _reconstruct_file(self, caller, fname: str):
        loc = caller.location
        state = caller.db.corruptor_fight
        if not state or not state.get("active"):
            error_sys(caller, "no hay combate activo. Inicia uno con `fight corruptor`.")
            return
        if not loc or loc.key != "final_exam":
            error_sys(caller, "solo puedes reconstruir archivos en /final_exam.")
            return
        if fname not in CORRUPTOR_FILES_BY_NAME:
            error_sys(caller, f"'{fname}' no es un archivo reconstruible.")
            return

        state = dict(state)
        corrupted = list(state.get("corrupted", []))
        restored = list(state.get("restored", []))
        if fname not in corrupted:
            terminal(caller, f"({fname} no ha sido corrompido en este combate)")
            return
        if fname in restored:
            terminal(caller, f"(ya reconstruiste {fname})")
            return

        _restore_file(caller, loc, fname)
        restored.append(fname)
        state["restored"] = restored
        caller.db.corruptor_fight = state

        caller.msg(
            f"|g→|n Reconstruiste |w{fname}|n. El archivo vuelve a su forma."
        )
        dialogue(
            caller,
            "Eco del Corruptor",
            "¡Ah! Todavía tienes sintaxis. Veremos cuánto te dura.",
        )

        # Condición de victoria: ya pasamos los 3 turnos Y reconstruimos todo
        turn = state.get("turn", 0)
        max_turns = state.get("max_turns", FIGHT_MAX_TURNS)
        if turn >= max_turns and set(corrupted) == set(restored):
            _end_fight(caller, win=True)
            return

        # Siguiente turno del Corruptor
        _do_corruptor_turn(caller)

    # --- Reconstruir memoria (cinemática final) -----------------------------
    def _reconstruct_memory(self, caller):
        memories = list(caller.db.memories or [])
        have = len(memories)
        if have < 10:
            error_sys(
                caller,
                f"necesitas los 10 fragmentos (tienes {have}/10). "
                "Busca archivos *.mem en cada room con `cat`.",
            )
            return

        # Idempotente: solo muestra la cinemática una vez
        if caller.db.memory_reconstructed:
            terminal(caller, "(ya reconstruiste tu memoria — eres libre)")
            return

        scene(
            caller,
            "CAPÍTULO III: ASCENSIÓN",
            "Los 10 fragmentos se alinean en tu mente como estrellas en "
            "fila. Recuerdas quién eres. Recuerdas por qué teclas. "
            "El filesystem no es tu prisión — es tu lengua materna.",
        )
        narrate(
            caller,
            "El Corruptor retrocede definitivamente. Las paredes del "
            "/claude_dojo vibran. Por primera vez ves tu propio nombre "
            "flotando sobre el prompt, escrito en la única tinta que "
            "El Corruptor no puede borrar: hex de 42 caracteres.",
        )
        dialogue(
            caller,
            "Prof. Shell",
            "Lo recordaste. Ahora solo queda grabarlo onchain. "
            "Linkea tu wallet (`link 0x...`) y haz `claim`. Quedarás para siempre.",
        )
        achievement(
            caller,
            "Memoria reconstruida",
            "Has recolectado los 10 fragmentos y recuperado tu identidad.",
            reward=150,
        )
        _apply_reward(caller, 150)
        caller.db.memory_reconstructed = True


# ---------------------------------------------------------------------------
# inventory_mem — lista los fragmentos recolectados
# ---------------------------------------------------------------------------
class CmdInventoryMem(Command):
    """
    Lista los fragmentos de memoria recolectados (0/10 → 10/10).

    Usage:
      inventory_mem
      mem
      fragments
    """

    key = "inventory_mem"
    aliases = ["mem", "fragments", "memorias"]
    locks = "cmd:all()"
    help_category = "Gameplay"

    def func(self):
        caller = self.caller
        _ensure_run_timer(caller)
        try:
            from world.lore.fragments import FRAGMENTS
        except Exception:
            FRAGMENTS = []

        memories = set(caller.db.memories or [])
        total = len(FRAGMENTS) or 10
        have = sum(1 for f in FRAGMENTS if f["id"] in memories)

        lines = [
            f"|y╭─ Fragmentos de memoria ({have}/{total}) ─╮|n",
        ]
        if not FRAGMENTS:
            lines.append("|y│|n  (fragmentos aún no definidos en este build)")
        else:
            for frag in FRAGMENTS:
                has = frag["id"] in memories
                mark = "|g✓|n" if has else "|x·|n"
                title = frag["title"]
                where = frag["room"]
                if has:
                    lines.append(f"|y│|n  {mark} |w{title}|n  |x(@{where})|n")
                else:
                    lines.append(
                        f"|y│|n  {mark} |x??? (aún no recuperado)|n  |x(pista: cat en {where})|n"
                    )
        if have >= total:
            lines.append("|y│|n")
            lines.append("|y│|n  |gReady:|n |wreconstruct memory|n para la cinemática final.")
        lines.append("|y╰──────────────────────────────────────╯|n")
        caller.msg("\n".join(lines))
        _emit_prompt(caller)


# ---------------------------------------------------------------------------
# leaderboard — top 10 speedruns
# ---------------------------------------------------------------------------
def _format_duration(seconds: float) -> str:
    """e.g. 123.4 → '2m03s'"""
    s = int(seconds)
    m = s // 60
    s = s % 60
    return f"{m}m{s:02d}s"


class CmdLeaderboard(Command):
    """
    Top 10 speedruns de Terminal Academy (tiempo desde primer comando → claim).

    Usage:
      leaderboard
      lb
    """

    key = "leaderboard"
    aliases = ["lb"]
    locks = "cmd:all()"
    help_category = "Gameplay"

    def func(self):
        caller = self.caller
        _ensure_run_timer(caller)
        # Lazy imports para evitar ciclos
        try:
            from evennia.objects.models import ObjectDB
        except Exception:
            error_sys(caller, "ObjectDB no disponible")
            return

        rows = []
        # Iteramos sobre todos los Characters con run_duration set
        try:
            for obj in ObjectDB.objects.all():
                try:
                    if obj.db.run_duration is None:
                        continue
                    # Solo queremos personajes jugables (no NPCs)
                    if obj.db.npc_type:
                        continue
                    dur = float(obj.db.run_duration)
                    rows.append((obj.key or "anon", dur, int(obj.db.abyss_pending or 0)))
                except Exception:
                    continue
        except Exception as e:
            logger.log_err(f"leaderboard scan failed: {e}")

        rows.sort(key=lambda r: r[1])
        rows = rows[:10]

        caller.msg("|y╭─ Terminal Academy · SPEEDRUN TOP 10 ─╮|n")
        if not rows:
            caller.msg("|y│|n  (aún no hay runs completos — sé el primero y haz `claim`)")
        else:
            for i, (name, dur, pending) in enumerate(rows, start=1):
                medal = {1: "|Y🥇|n", 2: "|w🥈|n", 3: "|y🥉|n"}.get(i, "  ")
                caller.msg(
                    f"|y│|n  {medal} #{i:>2}  |w{name:<18}|n  |c{_format_duration(dur):>8}|n  "
                    f"(pend: {pending} $TERM)"
                )
        my_dur = caller.db.run_duration
        if my_dur is not None:
            caller.msg(f"|y│|n")
            caller.msg(f"|y│|n  Tu tiempo: |c{_format_duration(float(my_dur))}|n")
        elif caller.db.run_started is not None:
            elapsed = time.time() - float(caller.db.run_started)
            caller.msg(f"|y│|n")
            caller.msg(
                f"|y│|n  (tu run en curso: {_format_duration(elapsed)} — hace `claim` para fijar tu time)"
            )
        caller.msg("|y╰──────────────────────────────────────╯|n")
        _emit_prompt(caller)


# ---------------------------------------------------------------------------
# Easter egg: sudo
# ---------------------------------------------------------------------------
class CmdSudo(Command):
    """
    sudo — comando de superusuario. En la Academia tiene un mensaje especial.

    Usage:
      sudo
      sudo <comando>
    """

    key = "sudo"
    locks = "cmd:all()"
    help_category = "Gameplay"

    def func(self):
        caller = self.caller
        _ensure_run_timer(caller)
        arg = (self.args or "").strip()
        if not arg:
            dialogue(
                caller,
                "Prof. Shell",
                "No necesitas permisos, neófito. Tú eres parte del sistema. "
                "En Terminal Academy no hay sudo — solo hay sintaxis.",
            )
        else:
            dialogue(
                caller,
                "Prof. Shell",
                f"No tengo permisos para elevar '{arg}' — y francamente, tú tampoco. "
                "Prueba sin sudo, a veces la terminal es más generosa de lo que crees.",
            )
        _emit_prompt(caller)


# ---------------------------------------------------------------------------
# Easter egg: rm -rf /
# ---------------------------------------------------------------------------
class CmdRm(Command):
    """
    rm — borrar archivos. En la Academia hay una trampa para los imprudentes.

    Usage:
      rm <archivo>
      rm -rf /    (NO LO HAGAS)
    """

    key = "rm"
    locks = "cmd:all()"
    help_category = "Gameplay"

    def func(self):
        caller = self.caller
        _ensure_run_timer(caller)
        raw = (self.args or "").strip()
        low = raw.lower()

        # Easter egg: rm -rf /
        is_rmrf = ("-rf" in low or "-fr" in low or "-r" in low and "-f" in low) and (
            low.endswith(" /") or low == "-rf /" or " /" in low
        )
        if is_rmrf:
            # Banner de catástrofe falsa + cuenta regresiva
            error_sys(caller, "DETECTADO rm -rf / — INICIANDO CATÁSTROFE")
            caller.msg(
                "|r╭─ SYSTEM CRITICAL ─────────────────────╮|n\n"
                "|r│|n  Borrando inodes...                \n"
                "|r│|n  Comiendo /bin, /etc, /home...     \n"
                "|r│|n  Tu realidad se desintegra en |Y3|r segundos|n\n"
                "|r│|n                                           \n"
                "|r│|n  Teclea |wcancel|n para abortar.          \n"
                "|r╰────────────────────────────────────────╯|n"
            )
            # Marca la ventana — el handler de `cancel` lo lee
            caller.db.rmrf_pending_until = time.time() + 3.0
            caller.db.rmrf_pending = True

            # Programa el "daño" si no cancela
            def _rmrf_consequence(who):
                try:
                    if not who.db.rmrf_pending:
                        return
                    # Si aún está activo, aplica castigo
                    who.db.rmrf_pending = False
                    who.db.rmrf_pending_until = None
                    error_sys(
                        who,
                        "Demasiado tarde. El filesystem devoró 10 $TERM. "
                        "La próxima vez: `cancel` o no hagas `rm -rf /`.",
                    )
                    current = int(who.db.abyss_pending or 0)
                    who.db.abyss_pending = max(0, current - 10)
                except Exception:
                    pass

            delay(3, _rmrf_consequence, caller)
            _emit_prompt(caller)
            return

        # rm normal: no implementado, aviso
        if not raw:
            terminal(caller, "usage: rm <archivo>")
        else:
            terminal(
                caller,
                f"rm: '{raw}': operación no soportada en la Academia. "
                "Los archivos de tutorial no se borran — usa `touch` y `mkdir` para construir.",
            )
        _emit_prompt(caller)


class CmdCancel(Command):
    """
    cancel — aborta una operación pendiente (ej. rm -rf /).

    Usage:
      cancel
    """

    key = "cancel"
    locks = "cmd:all()"
    help_category = "Gameplay"

    def func(self):
        caller = self.caller
        _ensure_run_timer(caller)
        pending_until = caller.db.rmrf_pending_until
        if caller.db.rmrf_pending and pending_until and time.time() < float(pending_until):
            caller.db.rmrf_pending = False
            caller.db.rmrf_pending_until = None
            caller.msg("|g→|n cancelado. El filesystem respira aliviado.")
            # Idempotente
            shown = list(caller.db.achievements_shown or [])
            if "rmrf_reflex" not in shown:
                shown.append("rmrf_reflex")
                caller.db.achievements_shown = shown
                achievement(
                    caller,
                    "Reflejos",
                    "Cancelaste un `rm -rf /` antes de que el filesystem te devorara.",
                    reward=25,
                )
                _apply_reward(caller, 25)
        else:
            terminal(caller, "(no hay nada que cancelar)")
        _emit_prompt(caller)


# ---------------------------------------------------------------------------
# Monkey-patch de comandos de terminal_commands (read-only) para auto-detectar
# resoluciones de puzzles sin editar el archivo original. Es idempotente —
# re-aplicarlo tras un reload no duplica el hook.
# ---------------------------------------------------------------------------
def _install_puzzle_grep_hook():
    """Envuelve CmdGREP.func: si hay hit de TOKEN en crypto_log.txt → marca puzzle."""
    try:
        from commands import terminal_commands
    except Exception:
        try:
            from abyss_node.commands import terminal_commands
        except Exception:
            return
    cls = getattr(terminal_commands, "CmdGREP", None)
    if cls is None:
        return
    original = cls.func
    if getattr(original, "_tacademy_puzzle_hook", False):
        return

    def wrapped(self):
        caller = getattr(self, "caller", None)
        raw = (self.args or "").strip() if hasattr(self, "args") else ""
        try:
            original(self)
        finally:
            # Criterio: grep con patrón TOKEN sobre crypto_log.txt y con hit real.
            try:
                if caller is None:
                    return
                parts = raw.split(None, 1)
                if len(parts) < 2:
                    return
                pat, fname = parts[0], parts[1]
                if pat.upper() != "TOKEN" or fname.strip() != "crypto_log.txt":
                    return
                # Verificar que el archivo realmente está en este room (hit)
                loc = caller.location
                if not loc:
                    return
                files = (loc.db.academy_files or {})
                content = files.get("crypto_log.txt", "") or ""
                if CRYPTO_TOKEN not in content:
                    # El archivo no está sembrado o fue alterado
                    return
                # Marca puzzle y aplica reward sólo la primera vez
                first = mark_puzzle_done(caller, "grep_token")
                if first:
                    puzzle = PUZZLES_BY_ID["grep_token"]
                    _apply_reward(caller, puzzle["reward"])
                    achievement(
                        caller,
                        puzzle["title"],
                        puzzle["body"],
                        reward=puzzle["reward"],
                    )
            except Exception as exc:
                try:
                    logger.log_trace(f"grep puzzle hook failed: {exc}")
                except Exception:
                    pass

    wrapped._tacademy_puzzle_hook = True
    cls.func = wrapped


def _install_pipe_puzzle_hook():
    """Envuelve CmdEcho/Cat-like ejecución para detectar pipe_count si ocurre."""
    # Detección por history: el `solve` ya lo hace; como backup auto,
    # envolvemos también CmdEcho porque el one-liner canónico no pasa por echo,
    # sino por un flujo del player. Dado que el CmdCat no tiene pipes, mejor
    # enganchamos al CmdHistory — cada vez que el player hace un comando,
    # terminal_commands registra historial. Pero _record_history es una función
    # local del módulo, no es feasible envolverla.
    # Decisión: el puzzle pipe_count lo verifica CmdSolve manualmente.
    # Aquí dejamos el hook como no-op, para dejar documentado el razonamiento.
    return


def _install_ls_seed_hook():
    """Envuelve CmdLS: al listar un room-puzzle, siembra el archivo si falta."""
    try:
        from commands import terminal_commands
    except Exception:
        try:
            from abyss_node.commands import terminal_commands
        except Exception:
            return
    cls = getattr(terminal_commands, "CmdLS", None)
    if cls is None:
        return
    original = cls.func
    if getattr(original, "_tacademy_seed_hook", False):
        return

    def wrapped(self):
        caller = getattr(self, "caller", None)
        try:
            if caller is not None:
                loc = caller.location
                if loc is not None:
                    for p in PUZZLES:
                        if p["room"] == loc.key:
                            _ensure_puzzle_file_in_room(loc, p["id"])
        except Exception as exc:
            try:
                logger.log_trace(f"ls seed hook failed: {exc}")
            except Exception:
                pass
        return original(self)

    wrapped._tacademy_seed_hook = True
    cls.func = wrapped


def _install_claim_hook():
    """Envuelve CmdClaim.func para capturar run_duration post-claim."""
    try:
        from commands import terminal_commands
    except Exception:
        try:
            from abyss_node.commands import terminal_commands
        except Exception:
            return
    cls = getattr(terminal_commands, "CmdClaim", None)
    if cls is None:
        return
    original = cls.func
    # Evita doble-wrapping en reloads
    if getattr(original, "_tacademy_run_hook", False):
        return

    def wrapped(self):
        caller = getattr(self, "caller", None)
        pending_before = 0
        if caller is not None:
            try:
                pending_before = int(caller.db.abyss_pending or 0)
            except Exception:
                pending_before = 0
            try:
                _ensure_run_timer(caller)
            except Exception:
                pass
        try:
            original(self)
        finally:
            if caller is not None:
                try:
                    # Consideramos "claim completado" si el pending pasó de >0 a 0.
                    pending_after = int(caller.db.abyss_pending or 0)
                    if pending_before > 0 and pending_after == 0:
                        _record_run_duration(caller)
                except Exception as exc:
                    logger.log_trace(f"run_duration hook failed: {exc}")

    wrapped._tacademy_run_hook = True
    cls.func = wrapped


# Instalar los hooks al importar el módulo.
for _fn in (_install_claim_hook, _install_puzzle_grep_hook, _install_pipe_puzzle_hook, _install_ls_seed_hook):
    try:
        _fn()
    except Exception as _e:
        # Nunca romper el import de comandos por un hook fallido.
        try:
            logger.log_trace(f"hook install failed ({_fn.__name__}): {_e}")
        except Exception:
            pass
