"""
Helper para crear el superuser inicial sin prompt interactivo.

Uso (desde abyss_node/):
  python _init_admin.py
"""
import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.conf.settings")
sys.path.insert(0, ".")

import django  # noqa

django.setup()

from evennia.accounts.models import AccountDB  # noqa

USERNAME = "admin"
EMAIL = "admin@academy.local"
PASSWORD = "monadtestnet123"

if AccountDB.objects.filter(username=USERNAME).exists():
    print(f"[skip] Account '{USERNAME}' already exists")
else:
    acc = AccountDB.objects.create_superuser(
        username=USERNAME, email=EMAIL, password=PASSWORD
    )
    print(f"[ok] Created superuser: {acc} ({acc.dbref})")
