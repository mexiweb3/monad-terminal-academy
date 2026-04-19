"""
Lore module — fragmentos de memoria, textos del prólogo y outro de Terminal Academy.

Regla: este módulo no tiene efectos secundarios — solo constantes y helpers puros.
El hook que los dispara vive en `typeclasses/characters.py`.
"""

from .fragments import (
    FRAGMENTS,
    FRAGMENTS_BY_FILE,
    PROLOGUE,
    OUTRO,
    collect_fragment,
)

__all__ = [
    "FRAGMENTS",
    "FRAGMENTS_BY_FILE",
    "PROLOGUE",
    "OUTRO",
    "collect_fragment",
]
