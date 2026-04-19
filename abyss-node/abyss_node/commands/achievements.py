"""
Achievements narrativos — hitos progresivos basados en `caller.db.quest_done`.

Los achievements se disparan de manera **idempotente** (cada uno se muestra
una sola vez, registrado en `caller.db.achievements_shown`). La función
`check_achievements(caller)` se puede llamar desde cualquier punto tras
una quest completada; típicamente la llama el idle-watcher de
`typeclasses/characters.py` y también los comandos de onboarding.

Los textos usan `achievement()` del narrator para mantener la grammar
visual del juego (box warm amber). Si el narrator no está disponible por
alguna razón (test aislado, import circular), hacemos fallback a
`caller.msg()` con el mismo contenido en texto plano.

Umbrales:
  1  quest  — "Primer respiro"
  5  quests — "Memoria despertando"
  10 quests — "Hacker novato"
  15 quests — "Maestro del shell"
  todas     — "Neo del shell"
"""

from __future__ import annotations


# (id, umbral, título, body)
ACHIEVEMENT_TIERS = [
    (
        "first_breath",
        1,
        "Primer respiro",
        "El filesystem responde a tu llamada. Ya no estás solo en el mar de texto.",
    ),
    (
        "memory_waking",
        5,
        "Memoria despertando",
        "Recuerdas fragmentos. Cada comando es un pedazo de tu identidad que regresa.",
    ),
    (
        "novice_hacker",
        10,
        "Hacker novato",
        "Puedes moverte en cualquier terminal Unix del mundo real. El Corruptor tiembla.",
    ),
    (
        "shell_master",
        15,
        "Maestro del shell",
        "Tu sintaxis es limpia, tus pipes precisos. La Academia te reconoce.",
    ),
    (
        "neo_of_shell",
        None,  # None = "todas las quests"
        "Neo del shell",
        "Has recuperado tu identidad completa. Estás listo para el siguiente plano.",
    ),
]


def _narrator_safe():
    """Importa helpers narrator con fallback seguro."""
    try:
        from utils.narrator import achievement as _ach
        return _ach
    except Exception:  # pragma: no cover — sólo entra en tests aislados
        return None


def _quests_total():
    """Total de quests del juego — leído dinámicamente para sobrevivir a cambios."""
    try:
        from commands.terminal_commands import QUESTS
        return len(QUESTS)
    except Exception:
        return 23  # fallback al valor del plan


def _emit(caller, title: str, body: str):
    ach = _narrator_safe()
    if ach is not None:
        ach(caller, title, body)
        return
    # Fallback plano (sin warm box)
    caller.msg(f"\n|y★ {title}|n\n  |y{body}|n\n")


def check_achievements(caller) -> list[str]:
    """
    Muestra los achievements narrativos correspondientes al progreso del
    jugador. Idempotente (nunca repite un achievement ya mostrado).

    Retorna la lista de ids disparados en esta llamada (útil para tests).
    """
    if caller is None:
        return []
    # Normaliza `achievements_shown` a un set persistido como lista.
    shown = list(caller.db.achievements_shown or [])
    quest_done = list(caller.db.quest_done or [])
    count = len(quest_done)
    total = _quests_total()

    triggered = []
    for aid, threshold, title, body in ACHIEVEMENT_TIERS:
        if aid in shown:
            continue
        hit = False
        if threshold is None:
            # "todas las quests"
            hit = total > 0 and count >= total
        else:
            hit = count >= threshold
        if hit:
            _emit(caller, title, body)
            shown.append(aid)
            triggered.append(aid)

    if triggered:
        caller.db.achievements_shown = shown
    return triggered
