"""
Spawnea (o reusa) los NPCs de Monad Terminal Academy.

Uso (desde abyss_node/ con .venv activo):
  python _spawn_npcs.py

Idempotente: correr múltiples veces no duplica NPCs. Si existe con typeclass
equivocada (p.ej. Character genérico), lo swap-ea al typeclass correcto.

NPCs:
  - Prof. Shell    en /home         (instructora general)
  - Claude Avatar  en /claude_dojo  (proyección del CLI de IA, iter-2)
"""
import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.conf.settings")
sys.path.insert(0, ".")

import django  # noqa: E402
django.setup()

import evennia  # noqa: E402
evennia._init()

from world.npcs.academy_npcs import spawn_all_academy_npcs  # noqa: E402


def main():
    npcs = spawn_all_academy_npcs(verbose=True)
    missing = [k for k, v in npcs.items() if v is None]
    if missing:
        print(f"[fail] NPCs sin spawnear: {missing}")
        sys.exit(1)
    for name, npc in npcs.items():
        print(f"[ok] {name}: {npc.key} en {npc.location.key} (dbref {npc.dbref})")


if __name__ == "__main__":
    main()
