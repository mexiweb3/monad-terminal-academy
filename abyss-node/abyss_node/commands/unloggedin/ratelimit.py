"""
Rate limit para el comando `create` (alta de cuenta) en la pantalla de login.

Contexto:
    Abrir una cuenta nueva en Terminal Academy cuesta 0 esfuerzo para el atacante
    y otorga 700 $TERM + acceso al tutorial. Sin freno, un bot puede spamear
    `create user1 pass; create user2 pass; ...` y drenar la hot wallet a través
    de los onboarding rewards. Evennia trae un rate limit por IP en el loop de
    unlogged-in, pero es muy permisivo (y bots rotan IP, por eso hace falta una
    capa lógica adicional que luego podamos endurecer con email/captcha/SIWE).

Este módulo expone `check_rate_limit(ip)` como *helper*; NO registra nada en el
cmdset por sí mismo. La integración (override del `CmdUnconnectedCreate` de
Evennia) la hace F7 — ver deploy/RUNBOOK_HARDENING.md, sección "Integración
ratelimit".

Política actual:
    MAX_CREATES = 5
    WINDOW_SEC  = 3600   # 60 min

    → Un atacante desde una misma IP sólo puede crear 5 cuentas por hora.
      La 6ª falla con mensaje claro hasta que expire el bucket.

Persistencia:
    In-memory dict. Se pierde al restart del server; eso es ACEPTABLE para:
      * single-server (nuestro caso, cpx11 único).
      * ventanas cortas (60 min) donde no es crítico sobrevivir reinicios.

    Si escalamos a multi-server con load balancer (ver TODO #16), hay que
    mover el bucket a Redis/Memcached para que todas las instancias compartan
    el contador. Hasta entonces, este módulo es suficiente.

Thread-safety:
    `threading.Lock()` protege la lectura+escritura del dict. Evennia corre
    comandos en un event loop de Twisted (single-threaded), pero si un día
    alguien añade hilos para I/O, el lock lo cubre sin overhead notable.
"""

from __future__ import annotations

import threading
import time
from collections import deque
from typing import Deque, Dict, Tuple

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

MAX_CREATES = 5
WINDOW_SEC = 60 * 60  # 60 minutos

# ---------------------------------------------------------------------------
# Estado
# ---------------------------------------------------------------------------

# ip -> deque de timestamps (monotonic) de intentos dentro de la ventana
_BUCKETS: Dict[str, Deque[float]] = {}
_LOCK = threading.Lock()


def _prune(ip: str, now: float) -> Deque[float]:
    """Elimina timestamps fuera de la ventana y devuelve el deque limpio."""
    bucket = _BUCKETS.get(ip)
    if bucket is None:
        bucket = deque()
        _BUCKETS[ip] = bucket

    cutoff = now - WINDOW_SEC
    while bucket and bucket[0] < cutoff:
        bucket.popleft()
    return bucket


# ---------------------------------------------------------------------------
# API pública
# ---------------------------------------------------------------------------


def check_rate_limit(ip: str) -> Tuple[bool, str]:
    """Chequea y cuenta un intento de `create` para la IP dada.

    Devuelve:
        (True, "") si la IP puede crear cuenta — el intento queda registrado.
        (False, msg) si excedió el bucket — msg lista-para-mostrar al player
        y el intento NO se cuenta (evita que sigan sumando durante el bloqueo).

    IMPORTANTE:
        * Se cuenta SOLO si la llamada es aceptada. El cmd debe invocar este
          helper ANTES de crear la cuenta; si más adelante se quisiera contar
          solo los intentos exitosos, mover el registro al punto post-éxito.
        * Si `ip` viene vacía / None (ej. test local por stdin), se usa el
          literal "unknown" para no crashar y no saltarse el bucket.
    """
    if not ip:
        ip = "unknown"

    now = time.monotonic()

    with _LOCK:
        bucket = _prune(ip, now)

        if len(bucket) >= MAX_CREATES:
            oldest = bucket[0]
            retry_in = int(WINDOW_SEC - (now - oldest)) + 1
            mins = max(1, retry_in // 60)
            msg = (
                f"Demasiadas cuentas creadas desde tu IP en la última hora "
                f"({len(bucket)}/{MAX_CREATES}). "
                f"Intenta de nuevo en ~{mins} min."
            )
            return (False, msg)

        bucket.append(now)
        return (True, "")


def reset_for_ip(ip: str) -> None:
    """Limpia el bucket de una IP (uso admin/debug/tests)."""
    with _LOCK:
        _BUCKETS.pop(ip, None)


def snapshot() -> Dict[str, int]:
    """Devuelve {ip: count} actual, sólo para observabilidad/tests."""
    now = time.monotonic()
    with _LOCK:
        out = {}
        for ip in list(_BUCKETS.keys()):
            bucket = _prune(ip, now)
            if bucket:
                out[ip] = len(bucket)
            else:
                # deque vacío: limpiamos para no acumular memoria
                del _BUCKETS[ip]
        return out


__all__ = [
    "check_rate_limit",
    "reset_for_ip",
    "snapshot",
    "MAX_CREATES",
    "WINDOW_SEC",
]
