"""
Smoke test Sesión A — usa el API interno de Evennia para:
  1) crear un account + character de prueba limpio
  2) correr los comandos de las 15 quests vía caller.execute_cmd()
  3) verificar que las 15 quests quedaron completadas
  4) probar `claim` onchain (tx real si el contrato está deployado)

Uso (desde abyss_node/ con .venv activo):
  python _smoke_session_a.py
"""
import os
import re
import sys
import uuid

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.conf.settings")
sys.path.insert(0, ".")

import django  # noqa
django.setup()

import evennia  # noqa
evennia._init()

from evennia.accounts.models import AccountDB  # noqa
from evennia.objects.models import ObjectDB  # noqa
from evennia.utils import create  # noqa
from evennia.utils.search import search_object  # noqa
from typeclasses.characters import Character  # noqa

TEST_WALLET = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"


def make_fresh_account():
    """Crea (o rehace) un account+character de test limpio."""
    name = f"qa_{uuid.uuid4().hex[:6]}"
    email = f"{name}@local.test"
    password = "Monad-Test-X-9f8e7d"
    account = create.create_account(name, email, password, typeclass=None)
    # crear character ligado
    home_rooms = search_object("home")
    home = home_rooms[0] if home_rooms else None
    char = create.create_object(
        Character,
        key=name,
        location=home,
        home=home,
        permissions=["Player"],
    )
    account.db._playable_characters = [char]
    char.db.account = account
    account.attributes.add("_last_puppet", char)
    return account, char


def run(char, cmd):
    """Ejecuta un comando como si el character lo tipeara, capturando su output."""
    captured = []

    def grabber(text=None, **kwargs):
        if text is None:
            return
        if isinstance(text, (list, tuple)):
            text = " ".join(str(t) for t in text)
        captured.append(str(text))

    original = char.msg
    char.msg = grabber
    try:
        char.execute_cmd(cmd)
    finally:
        char.msg = original
    out = re.sub(r"\|[rgybcwxn]", "", "\n".join(captured))
    return out


def main():
    account, char = make_fresh_account()
    print(f"[info] test account: {account.key}  char.dbref={char.dbref}  location={char.location}")

    # Secuencia que toca las 15 quests + pipes/redirects + navegación completa
    sequence = [
        "pwd",
        "ls",
        "cd ls_dojo",
        "ls",
        "cd cd_dojo",
        "pwd",
        "cd cat_dojo",
        "cat secret.txt",
        "cd mkdir_dojo",
        "touch mi_nota.txt",
        "mkdir mi_dir",
        "grep ABYSS README.txt",
        "cd pipe_dojo",
        "echo hola mundo",
        "whoami",
        "head log.txt",
        "tail log.txt",
        "echo hola | wc",
        "echo hola | grep hola",
        "cd redirect_dojo",
        "echo primera > mi.log",
        "echo segunda >> mi.log",
        "cat mi.log",
        "wc mi.log",
        "man echo",
        "cd final_exam",
        "echo final check > exam.log",
        "echo extra >> exam.log",
        "cat exam.log",
        "wc exam.log",
        "grep final exam.log",
        "history",
        "cat diploma.txt",
        # --- Claude CLI flow (claude_dojo) ---
        "cd claude_dojo",
        "cat INTRO.txt",
        "claude",                                         # q_claude
        "claude skills list",
        "claude skills install austin-griffith/monad-kit",  # q_skill
        "claude skills installed",
        "claude new contract MiPrimerToken",              # q_new
        "cat MiPrimerToken.sol",
        "claude deploy MiPrimerToken.sol",                # q_deploy
        # --- Onchain claim ---
        f"link {TEST_WALLET}",
        "quests",
    ]

    for cmd in sequence:
        out = run(char, cmd)
        short = out.strip().splitlines()[0] if out.strip() else "(sin output)"
        print(f"  $ {cmd:<34}  →  {short[:80]}")

    done = list(char.db.quest_done or [])
    pending = int(char.db.abyss_pending or 0)
    print(f"\n[info] quest_done ({len(done)}/15): {done}")
    print(f"[info] abyss_pending: {pending} $TERM")

    if len(done) < 19:
        print("[FAIL] no se completaron las 19 quests")
        sys.exit(1)
    print("[ok] 19/19 quests completadas")

    # Claim onchain
    claim_out = run(char, "claim")
    print("\n[info] claim output:")
    print(claim_out[-1500:])
    if "CLAIM ENVIADO" in claim_out:
        tx = re.search(r"tx:\s*(0x[0-9a-fA-F]{40,})", claim_out)
        print(f"[ok] claim onchain exitoso — tx={tx.group(1) if tx else '?'}")
    elif "CLAIM PENDIENTE" in claim_out:
        print("[warn] CONTRACT_ADDR vacío — claim UI-only (no regresión)")
    else:
        print("[FAIL] claim no produjo tx ni mensaje pendiente")
        sys.exit(2)

    # Cleanup — borra el account y el char de prueba
    char.delete()
    account.delete()
    print("\n[DONE] Smoke test Sesión A pasó.")


if __name__ == "__main__":
    main()
