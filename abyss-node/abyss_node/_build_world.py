"""
Construye la zona Monad Terminal Academy en la DB, sin necesidad de conexión.

Uso (desde abyss_node/ con .venv activo):
  python _build_world.py
"""
import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.conf.settings")
sys.path.insert(0, ".")

import django  # noqa
django.setup()

import evennia  # noqa
evennia._init()

from world.zones.terminal_academy import build_academy  # noqa

rooms = build_academy(None)
home = rooms["home"]
print(f"[ok] Academy built. Home dbref = {home.dbref}")

# Set START_LOCATION hint file (se aplica al reload si editamos settings)
from django.conf import settings  # noqa
print(f"[info] Current START_LOCATION = {getattr(settings, 'START_LOCATION', None)}")
print(f"[hint] Actualiza settings.py con START_LOCATION = '{home.dbref}' y reloadea")
