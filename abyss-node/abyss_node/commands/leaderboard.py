"""
CmdLeaderboardCourse — top 20 jugadores por $TERM ganados.

Este leaderboard es DIFERENTE al de game_commands (que rankea speedruns).
Aquí rankeamos por total de $TERM acumulados (pending + claimed), porque es
la métrica más natural en cohortes grandes donde no todos terminan al mismo
ritmo — te da sensación de avance sin depender de `claim`.

Cache:
  Para escalar a cohortes grandes evitamos un escaneo de ObjectDB en cada
  request. Cacheamos el resultado de la query por `_CACHE_TTL` segundos
  (default: 60s) en un dict a nivel de módulo. Es un cache por proceso —
  si hay múltiples servidores Evennia detrás de un proxy habría que mover
  esto a Redis, pero para el scope actual (single-server, <200 cohortantes)
  basta.

Pendientes para otra sesión:
  - Paginación (top 20 ahora; >100 players querrá `leaderboard page 2`).
  - Filtro por cohorte (añadir `caller.db.cohort_id` y filtrar aquí).
  - Reset semanal para competencias.
"""

import time

from evennia import Command
from evennia.utils import logger


# --- Config ---
_CACHE_TTL = 60  # segundos de vida del cache en memoria
_TOP_N = 20

# --- Cache global (proceso) ---
# Estructura: {"ts": float, "rows": list[tuple]}
_CACHE: dict = {}


class CmdLeaderboardCourse(Command):
    """
    Top 20 jugadores de Terminal Academy por |y$TERM|n ganados.

    Usage:
      leaderboard
      ranking
      top

    El ranking se calcula sobre la suma de tus $TERM pendientes +
    reclamados. Se actualiza como máximo cada 60s (cache), así que si
    acabas de reclamar puede tardar un poquito en reflejarse.
    """

    key = "leaderboard"
    aliases = ["ranking", "top"]
    locks = "cmd:all()"
    help_category = "Monad"

    def func(self):
        caller = self.caller
        rows = _get_leaderboard()

        lines = [
            "",
            "|M╭── Terminal Academy · Leaderboard ($TERM) ──────────────────────╮|n",
            (
                "|M│|n  |yrank  jugador              $TERM    quests  memorias|n"
            ),
            "|M│|n  " + "|x" + ("─" * 60) + "|n",
        ]

        if not rows:
            lines.append(
                "|M│|n  |x(aún no hay jugadores con $TERM — sé el primero con `quests`)|n"
            )
        else:
            me_key = caller.key or ""
            my_rank = None
            for i, (name, term, quests, mems) in enumerate(rows, start=1):
                medal = _medal(i)
                mark = "|Y*|n" if name == me_key else " "
                if name == me_key:
                    my_rank = i
                lines.append(
                    f"|M│|n  {mark} {medal}{i:>2}  "
                    f"|w{_pad_name(name, 18)}|n "
                    f"|y{term:>6}|n  "
                    f"{quests:>6}  {mems:>6}"
                )

            # Si el caller no está en el top 20, mostramos su posición abajo.
            if my_rank is None and caller and not caller.db.npc_type:
                my_term, my_q, my_m = _player_stats(caller)
                if my_term > 0 or my_q > 0:
                    lines.append("|M│|n")
                    lines.append(
                        f"|M│|n  |c(tu ranking actual:|n fuera del top {_TOP_N} — "
                        f"|y{my_term}|n $TERM, {my_q} quests, {my_m} memorias|c)|n"
                    )

        # Cache freshness hint (útil para debugging durante la presentación).
        age = _cache_age()
        if age is not None:
            lines.append(
                f"|M│|n  |x(actualizado hace {int(age)}s · cache {_CACHE_TTL}s)|n"
            )
        lines.append("|M╰───────────────────────────────────────────────────────────────╯|n")

        caller.msg("\n".join(lines))


# ---------- helpers ----------
def _cache_age():
    if not _CACHE.get("ts"):
        return None
    return time.time() - _CACHE["ts"]


def _get_leaderboard():
    """Devuelve lista de tuplas (name, total_term, quests_done, memories).

    Ordenada desc por total_term. Trunca a _TOP_N.
    Usa cache de _CACHE_TTL segundos para no golpear la DB en cada request.
    """
    now = time.time()
    ts = _CACHE.get("ts", 0)
    if ts and (now - ts) < _CACHE_TTL:
        return _CACHE.get("rows", [])

    rows = _query_leaderboard()
    _CACHE["ts"] = now
    _CACHE["rows"] = rows
    return rows


def _query_leaderboard():
    """Escanea todos los Character jugables y rankea por $TERM total."""
    try:
        from typeclasses.characters import Character
    except Exception as exc:
        logger.log_err(f"leaderboard: cannot import Character: {exc}")
        return []

    out = []
    try:
        # Filtramos NPCs por db.npc_type. Los players no tienen esa attr seteada.
        for char in Character.objects.all():
            try:
                if getattr(char.db, "npc_type", None):
                    continue
                pending = int(char.db.abyss_pending or 0)
                claimed = int(char.db.abyss_claimed or 0)
                total = pending + claimed
                if total <= 0 and not char.db.quest_done:
                    # Descarta characters vacíos (bots de test, NPCs mal taggeados)
                    continue
                quests = len(list(char.db.quest_done or []))
                mems = len(list(char.db.memories or []))
                out.append((char.key or "anon", total, quests, mems))
            except Exception:
                continue
    except Exception as exc:
        logger.log_err(f"leaderboard: query failed: {exc}")
        return []

    out.sort(key=lambda r: (-r[1], -r[2], -r[3], r[0]))
    return out[:_TOP_N]


def _player_stats(caller):
    pending = int(caller.db.abyss_pending or 0)
    claimed = int(caller.db.abyss_claimed or 0)
    quests = len(list(caller.db.quest_done or []))
    mems = len(list(caller.db.memories or []))
    return pending + claimed, quests, mems


def _medal(rank: int) -> str:
    return {1: "|Y#|n", 2: "|w#|n", 3: "|y#|n"}.get(rank, " ")


def _pad_name(name: str, width: int) -> str:
    """Trunca/padea a width (por longitud VISIBLE)."""
    s = name or ""
    if len(s) > width:
        return s[: width - 1] + "…"
    return s + " " * (width - len(s))
