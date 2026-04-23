"""
Structured JSON logger — un renglón por evento, parseable por jq/loki/grafana.

Qué resuelve:
    Hoy los logs del juego son `print()` y `self.msg()` desparramados. Eso
    sirve para debug local pero en prod no se puede filtrar "¿qué tan seguido
    se completa la quest q01?" ni alertar por errores. Este helper emite JSON
    line-delimited a stdout; journald (vía systemd) lo captura y pasa por
    pipeline estándar (`journalctl -u terminal-academy -o cat | jq ...`).

Formato:
    {"ts": "2026-04-22T20:15:33.421Z", "level": "INFO",
     "event": "quest_completed", "user": "neo", "quest": "q01_ls"}

API pública:
    log_event(event, level="INFO", **fields)
    log_info(event, **fields)        # alias de log_event
    log_warn(event, **fields)
    log_error(event, exc=None, **fields)
    log_debug(event, **fields)

Uso típico:
    from utils.logger import log_event, log_error

    log_event("quest_completed", user=caller.key, quest="q01_ls",
              reward_term=100)

    try:
        do_onchain_claim(wallet, amount)
    except Exception as exc:
        log_error("onchain_claim_failed", exc=exc,
                  wallet=wallet, amount=amount)

Notas:
    * NO cambiar código existente — solo crear el helper. Otra sesión migrará
      prints/self.msg a log_event según convenga.
    * Timestamp ISO 8601 con sufijo "Z" (UTC, zulu). No TZ locales.
    * Campos reservados: ts, level, event, exc_type, exc_msg, traceback.
      Si `**fields` colisiona con uno de estos, se prefija con "f_".
    * Valores no serializables por `json.dumps` se convierten con `repr()`
      para no tumbar el proceso por un logging call.
    * Thread-safe: `logging.StreamHandler` de stdlib es thread-safe.
"""

from __future__ import annotations

import json
import logging
import sys
import traceback
from datetime import datetime, timezone
from typing import Any

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

_LOGGER_NAME = "terminal_academy"
# Los 3 sólo existen porque _emit los setea antes de mezclar fields. Si el
# caller pasa uno de esos nombres como kwarg, se prefija con f_ para evitar
# que pise la estructura base. `exc_type` / `exc_msg` / `traceback` SÍ se
# emiten como top-level (desde log_error) — por eso NO son reservados.
_RESERVED_FIELDS = {"ts", "level", "event"}


def _build_logger() -> logging.Logger:
    """Configura un logger con handler stdout y formatter no-op."""
    lg = logging.getLogger(_LOGGER_NAME)
    if getattr(lg, "_ta_configured", False):
        return lg

    lg.setLevel(logging.DEBUG)
    lg.propagate = False  # no bubblear al root (evita dobles)

    handler = logging.StreamHandler(stream=sys.stdout)
    # Mensaje ya viene pre-formateado como JSON desde _emit; formatter pasthru
    handler.setFormatter(logging.Formatter("%(message)s"))
    lg.addHandler(handler)

    # Flag custom para idempotencia si se reimporta el módulo
    lg._ta_configured = True  # type: ignore[attr-defined]
    return lg


_LOG = _build_logger()


# ---------------------------------------------------------------------------
# Serialización
# ---------------------------------------------------------------------------


def _now_iso() -> str:
    """Timestamp ISO 8601 UTC con milis y sufijo Z."""
    # datetime.utcnow() está deprecado en Python 3.12+; usar tz-aware.
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.") + \
        f"{datetime.now(timezone.utc).microsecond // 1000:03d}Z"


def _safe_value(value: Any) -> Any:
    """Convierte a algo JSON-serializable. Fallback: repr()."""
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, (list, tuple)):
        return [_safe_value(v) for v in value]
    if isinstance(value, dict):
        return {str(k): _safe_value(v) for k, v in value.items()}
    # datetime, Decimal, objetos custom, etc. → repr
    try:
        return repr(value)
    except Exception:
        return "<unrepresentable>"


def _namespaced(fields: dict[str, Any]) -> dict[str, Any]:
    """Prefija con f_ cualquier key que colisione con reservados."""
    out: dict[str, Any] = {}
    for k, v in fields.items():
        key = f"f_{k}" if k in _RESERVED_FIELDS else k
        out[key] = _safe_value(v)
    return out


def _emit(level: str, event: str, fields: dict[str, Any]) -> None:
    """Construye el JSON y lo manda por el logger configurado."""
    record: dict[str, Any] = {
        "ts": _now_iso(),
        "level": level,
        "event": event,
    }
    record.update(_namespaced(fields))

    try:
        payload = json.dumps(record, ensure_ascii=False, default=str)
    except Exception as exc:  # pragma: no cover — defensivo
        payload = json.dumps({
            "ts": _now_iso(),
            "level": "ERROR",
            "event": "logger_serialization_failed",
            "original_event": event,
            "exc_msg": repr(exc),
        })

    level_int = getattr(logging, level, logging.INFO)
    _LOG.log(level_int, payload)


# ---------------------------------------------------------------------------
# API pública
# ---------------------------------------------------------------------------


# Nota de API: los helpers usan `event` como parámetro POSICIONAL y no
# aceptan `event=` por kwarg (lo previene el `/` de Python 3.8+). Si el
# caller necesitara pasar una key literalmente llamada "event" como campo,
# se prefijará a "f_event" en _namespaced().

def log_event(event: str, /, level: str = "INFO", **fields: Any) -> None:
    """Log genérico. Ver log_info / log_warn / log_error para atajos."""
    _emit(level, event, fields)


def log_info(event: str, /, **fields: Any) -> None:
    _emit("INFO", event, fields)


def log_warn(event: str, /, **fields: Any) -> None:
    _emit("WARNING", event, fields)


def log_debug(event: str, /, **fields: Any) -> None:
    _emit("DEBUG", event, fields)


def log_error(event: str, /, exc: BaseException | None = None, **fields: Any) -> None:
    """Log de error opcionalmente con excepción adjunta.

    Si `exc` se pasa, añade exc_type / exc_msg / traceback.
    """
    if exc is not None:
        fields.setdefault("exc_type", type(exc).__name__)
        fields.setdefault("exc_msg", str(exc))
        fields.setdefault(
            "traceback",
            "".join(traceback.format_exception(type(exc), exc, exc.__traceback__)),
        )
    _emit("ERROR", event, fields)


__all__ = [
    "log_event",
    "log_info",
    "log_warn",
    "log_error",
    "log_debug",
]
