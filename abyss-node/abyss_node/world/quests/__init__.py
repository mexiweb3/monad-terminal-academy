"""
Terminal Academy — puzzles & gameplay extendido.

Submódulos:
  puzzles  → engine de puzzles (grep token, pipe count), estado por player,
             verificación de soluciones y spawn de archivos puzzle.
"""

from .puzzles import (
    PUZZLES,
    PUZZLES_BY_ID,
    ensure_puzzles_state,
    spawn_puzzle_files,
    mark_puzzle_done,
    is_puzzle_done,
    generate_crypto_log,
    generate_mensaje_enc,
    CRYPTO_TOKEN,
)

__all__ = [
    "PUZZLES",
    "PUZZLES_BY_ID",
    "ensure_puzzles_state",
    "spawn_puzzle_files",
    "mark_puzzle_done",
    "is_puzzle_done",
    "generate_crypto_log",
    "generate_mensaje_enc",
    "CRYPTO_TOKEN",
]
