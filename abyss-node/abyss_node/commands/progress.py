"""
CmdProgress — dashboard compacto del progreso del jugador.

Muestra en una caja Unicode:
  - nombre + idioma (si `account.db.language` está seteado)
  - quests completadas (con barra ASCII)
  - fragmentos recuperados
  - $TERM pendientes
  - wallet linkeada (truncada si existe)
  - rooms visitadas (con checkmark)
  - hint contextual de siguiente paso

El hint sigue una lógica progresiva:
  - si falta la quest q01 (ls) → teclea `ls`
  - si completó todas las quests pero no tiene wallet → `link 0x...`
  - si tiene wallet + pendientes > 0 → `claim`
  - si todo al corriente → `mint` (certificado onchain)
  - fallback: mostrar la siguiente quest desbloqueada según visited_rooms
"""

from evennia import Command

# Rooms canónicos de Terminal Academy, en orden narrativo.
# Se usan para el bloque "rooms visitadas N/10".
ACADEMY_ROOMS = [
    "home",
    "ls_dojo",
    "cd_dojo",
    "cat_dojo",
    "mkdir_dojo",
    "pipe_dojo",
    "redirect_dojo",
    "final_exam",
    "install_dojo",
    "claude_dojo",
]


class CmdProgress(Command):
    """
    Dashboard de tu progreso en Terminal Academy.

    Usage:
      progreso
      progress
      status
      stats

    Muestra quests completadas, fragmentos recuperados, $TERM pendientes,
    wallet linkeada, rooms visitadas y el siguiente paso sugerido.
    """

    key = "progreso"
    aliases = ["progress", "status", "stats"]
    locks = "cmd:all()"
    help_category = "Monad"

    def func(self):
        caller = self.caller
        # Lazy imports — evitamos ciclos y permiten probar el módulo aislado.
        try:
            from commands.terminal_commands import QUESTS
        except Exception:
            QUESTS = []
        try:
            from world.lore.fragments import FRAGMENTS
        except Exception:
            FRAGMENTS = []

        done_ids = list(caller.db.quest_done or [])
        done = len(done_ids)
        total_q = len(QUESTS) or 21
        memories = list(caller.db.memories or [])
        total_m = len(FRAGMENTS) or 10
        pending = int(caller.db.abyss_pending or 0)
        wallet = caller.db.wallet or ""
        wallet_ens = caller.db.wallet_ens or ""
        visited = set(caller.db.visited_rooms or [])
        if caller.location and caller.location.key:
            visited.add(caller.location.key)

        # Idioma desde la cuenta (opcional).
        lang = ""
        try:
            acc = caller.account
            if acc and acc.db and acc.db.language:
                lang = str(acc.db.language)
        except Exception:
            lang = ""

        # Wallet display truncada si es hex, completa si es ENS.
        if wallet_ens:
            wallet_display = f"|y{wallet_ens}|n |x({_truncate_addr(wallet)})|n"
        elif wallet and wallet.startswith("0x"):
            wallet_display = f"|c{_truncate_addr(wallet)}|n"
        elif wallet:
            wallet_display = f"|c{wallet}|n"
        else:
            wallet_display = "|x(sin linkear)|n"

        # Barra de progreso de quests.
        bar = _progress_bar(done, total_q, width=20)
        pct = int((done / total_q) * 100) if total_q else 0

        # Lista de rooms con checkmark.
        room_lines = []
        for r in ACADEMY_ROOMS:
            if r in visited:
                room_lines.append(f"|g✓ {r}|n")
            else:
                room_lines.append(f"|x· {r}|n")
        # Rompe en filas de 3 para que el box no explote.
        room_block = _chunk_rows(room_lines, per_row=3)

        # Hint contextual.
        hint = _next_step_hint(caller, done_ids, total_q, wallet, pending, visited, QUESTS)

        # Construcción del box.
        name = caller.key or "neófito"
        header = f" {name} " + (f"|x· lang={lang}|n " if lang else "")

        box_lines = []
        box_lines.append("|M╭────────────── Terminal Academy · Progreso ──────────────╮|n")
        box_lines.append(f"|M│|n  |w{header}|n")
        box_lines.append("|M│|n")
        box_lines.append(
            f"|M│|n  |yQuests:|n    |w{done:>2}/{total_q}|n  {bar}  |y{pct:>3}%|n"
        )
        box_lines.append(
            f"|M│|n  |yFragmentos:|n {len(memories):>2}/{total_m}  "
            f"|y$TERM pend:|n {pending}"
        )
        box_lines.append(f"|M│|n  |yWallet:|n    {wallet_display}")
        box_lines.append("|M│|n")
        box_lines.append(
            f"|M│|n  |yRooms visitados:|n |w{len(visited & set(ACADEMY_ROOMS))}/{len(ACADEMY_ROOMS)}|n"
        )
        for row in room_block:
            box_lines.append(f"|M│|n    {row}")
        box_lines.append("|M│|n")
        box_lines.append(f"|M│|n  |cSiguiente paso:|n {hint}")
        box_lines.append("|M╰──────────────────────────────────────────────────────────╯|n")

        caller.msg("\n".join(box_lines))


# ---------- helpers ----------
def _truncate_addr(addr: str) -> str:
    """0x1234...abcd (mantiene 6 chars iniciales y 4 finales)."""
    if not addr or len(addr) <= 12:
        return addr or ""
    return f"{addr[:6]}...{addr[-4:]}"


def _progress_bar(done: int, total: int, width: int = 20) -> str:
    if total <= 0:
        return "|x[" + "·" * width + "]|n"
    filled = int((done / total) * width)
    filled = max(0, min(width, filled))
    return "|g[" + ("█" * filled) + "|x" + ("░" * (width - filled)) + "|g]|n"


def _chunk_rows(items: list, per_row: int = 3) -> list:
    """Divide una lista de strings en filas de `per_row` items, como columnas.

    Cada celda se padea a 16 chars (aprox — los tags |c|n no cuentan aquí).
    """
    out = []
    for i in range(0, len(items), per_row):
        chunk = items[i:i + per_row]
        # 18 chars por celda — suficiente para nombres tipo 'redirect_dojo'
        padded = [_pad(c, 18) for c in chunk]
        out.append("".join(padded))
    return out


def _pad(line: str, width: int) -> str:
    """Padding por longitud VISIBLE (sin contar |x tags)."""
    import re
    visible = re.sub(r"\|[a-zA-Z#*][0-9a-fA-F]?", "", line or "")
    pad = max(0, width - len(visible))
    return line + " " * pad


def _next_step_hint(caller, done_ids, total_q, wallet, pending, visited, QUESTS) -> str:
    """Devuelve el texto del hint contextual.

    Prioridad:
      1. si no tecleó `ls` (q01_ls) → "teclea `ls` en /home"
      2. si completó todas las quests y NO tiene wallet → "linkea tu wallet"
      3. si tiene wallet + pendientes → "teclea `claim`"
      4. si todo completo (quests + wallet) y pending==0 → "teclea `mint`"
      5. fallback: primera quest desbloqueada (room visitado) no completada
    """
    done_set = set(done_ids)
    if "q01_ls" not in done_set:
        return "teclea |wls|n para dar tu primer comando."
    if len(done_set) >= total_q and not wallet:
        return "linkea tu wallet con |wlink 0x...|n para reclamar $TERM."
    if wallet and pending > 0:
        return "teclea |wclaim|n para recibir |y$TERM|n onchain."
    if len(done_set) >= total_q and wallet and pending == 0:
        return "teclea |wmint|n para grabar tu certificado NFT onchain."
    # Fallback: próxima quest desbloqueada
    for q in QUESTS:
        if q["id"] in done_set:
            continue
        room = q.get("room", "home")
        if room in visited or room == "home":
            return (
                f"en |c{room}|n, teclea |w{q['cmd']}|n — "
                f"{q['desc']}"
            )
    # Último fallback: explora
    return "explora los dojos — usa |wquests|n para ver el mapa."
