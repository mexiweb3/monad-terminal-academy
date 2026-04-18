"""
Smoke test específico de Sesión B — valida criterios de aceptación:

1) Nuevo usuario ve banner + tutorial al primer login (idempotente en re-login).
2) `help` muestra recomendación contextual de la próxima quest.
3) Prof. Shell responde a al menos 3 interacciones distintas (`hola prof`,
   `ayuda`, `claim`).
4) `claim` sigue emitiendo tx onchain — sin regresiones de Sesión A.

Corre desde abyss_node/ con .venv activo:
  python _smoke_sesion_b.py
"""
import re
import socket
import sys
import time
import uuid

HOST = "127.0.0.1"
PORT = 4100
ADMIN_USER = "admin"
ADMIN_PASS = "monadtestnet123"
TEST_WALLET = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"


def strip_ansi(s: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*m", "", s)


class Session:
    def __init__(self, host=HOST, port=PORT):
        self.s = socket.create_connection((host, port), timeout=6)
        self.s.settimeout(2.5)
        self.buffer = ""

    def send(self, cmd):
        self.s.sendall((cmd + "\r\n").encode())
        time.sleep(0.7)

    def recv(self):
        chunks = []
        try:
            while True:
                c = self.s.recv(8192)
                if not c:
                    break
                chunks.append(c)
        except socket.timeout:
            pass
        text = strip_ansi(b"".join(chunks).decode(errors="replace"))
        self.buffer += text
        return text

    def cmd(self, line):
        self.send(line)
        return self.recv()

    def close(self):
        try:
            self.s.close()
        except Exception:
            pass


def assert_contains(label, haystack, *needles):
    hay = haystack.lower()
    missing = [n for n in needles if n.lower() not in hay]
    if missing:
        print(f"  |FAIL| {label}: falta {missing!r}")
        print("  --- output ---")
        print(haystack[-1500:])
        print("  --- end ---")
        return False
    print(f"  |PASS| {label}")
    return True


def main():
    ok = True

    # ---------------------------------------------------------------
    # 1) Nuevo usuario → banner + tutorial + help + Prof. Shell
    # ---------------------------------------------------------------
    suffix = uuid.uuid4().hex[:6]
    new_user = f"demo_{suffix}"
    new_pass = "monadacademy1"

    print(f"\n[1] Nuevo usuario: {new_user}")
    s = Session()
    s.recv()
    first = s.cmd(f"create {new_user} {new_pass}")
    # Evennia pide confirmación [Y]/N?
    if "intended" in first.lower() or "[Y]".lower() in first.lower():
        first += s.cmd("Y")
    # Ahora sí connect — debe disparar at_post_puppet y el banner.
    time.sleep(0.5)
    first += s.cmd(f"connect {new_user} {new_pass}")
    # Esperamos un poco para que llegue todo el output del login
    time.sleep(1.0)
    first += s.recv()
    ok &= assert_contains(
        "banner + tutorial en primer login",
        first,
        "MONAD TERMINAL ACADEMY",
        "escribe",
        "ls",
    )

    # Confirmamos que estamos en /home viendo Prof. Shell en ls
    ls_out = s.cmd("ls")
    ok &= assert_contains("ls muestra Prof. Shell en /home", ls_out, "Prof. Shell")

    # ---------------------------------------------------------------
    # 2) help con recomendación contextual
    # ---------------------------------------------------------------
    print("\n[2] help contextual")
    help_out = s.cmd("help")
    ok &= assert_contains(
        "help muestra secciones + recomendación",
        help_out,
        "terminal",
        "monad",
        "¿cuál intento?",
    )

    # ---------------------------------------------------------------
    # 3) Prof. Shell responde a 3 interacciones distintas
    # ---------------------------------------------------------------
    print("\n[3] Prof. Shell — 3+ interacciones")
    r1 = s.cmd("say hola prof")
    time.sleep(1.2)
    r1 += s.recv()
    ok &= assert_contains(
        "hola prof → saludo + recomendación quest",
        r1,
        "Prof. Shell",
        "Llevas",
        "$TERM",
    )

    r2 = s.cmd("say ayuda")
    time.sleep(1.2)
    r2 += s.recv()
    ok &= assert_contains("ayuda → tips", r2, "Prof. Shell", "pwd")

    r3 = s.cmd("say como hago claim")
    time.sleep(1.2)
    r3 += s.recv()
    ok &= assert_contains("claim → explica flujo onchain", r3, "Prof. Shell", "link")

    # ---------------------------------------------------------------
    # 4) claim end-to-end (avanzamos unas quests y reclamamos)
    # ---------------------------------------------------------------
    print("\n[4] claim onchain sigue funcionando")
    # Sumamos varias quests rápido
    for c in ("ls", "pwd", "cd ls_dojo", "cd cd_dojo", "cd cat_dojo", "cat secret.txt"):
        s.cmd(c)
    s.cmd(f"link {TEST_WALLET}")
    time.sleep(0.3)
    claim_out = s.cmd("claim")
    # Dar tiempo al RPC
    for _ in range(10):
        time.sleep(1.5)
        extra = s.recv()
        if extra:
            claim_out += extra
        if "tx:" in claim_out.lower() or "0x" in claim_out:
            break
    ok &= assert_contains(
        "claim emite tx hash onchain",
        claim_out,
        "claim enviado",
        "0x",
        "explorer",
    )

    # ---------------------------------------------------------------
    # 5) Re-login NO repite banner (idempotencia)
    # ---------------------------------------------------------------
    print("\n[5] Banner idempotente en re-login")
    s.close()
    time.sleep(0.5)
    s2 = Session()
    s2.recv()
    relogin = s2.cmd(f"connect {new_user} {new_pass}")
    banner_found = "MONAD TERMINAL ACADEMY" in relogin
    if banner_found:
        print("  |FAIL| re-login mostró banner otra vez (no es idempotente)")
        print(relogin[-1500:])
        ok = False
    else:
        print("  |PASS| re-login no repite banner")
    s2.close()

    # ---------------------------------------------------------------
    print("\n" + ("=" * 60))
    if ok:
        print("TODOS LOS CRITERIOS DE SESIÓN B — PASS")
        sys.exit(0)
    else:
        print("HAY FAILURES — revisar arriba")
        sys.exit(2)


if __name__ == "__main__":
    main()
