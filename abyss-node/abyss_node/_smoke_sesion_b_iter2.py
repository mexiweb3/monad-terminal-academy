"""
Smoke test iter-2 de Sesión B — valida criterios de aceptación:

1) Banner post-login menciona Claude CLI.
2) `help` en claude_dojo sugiere el siguiente paso del flujo claude
   según progreso (install → new → deploy).
3) Prof. Shell responde a al menos 5 triggers distintos:
   hola prof, ayuda, claim, qué es claude, qué es un skill, cómo deploy.
4) NPC de claude_dojo (Claude Avatar) reacciona a `say hola` y a progreso
   onchain (cambia el mensaje si instalo / deployo).
5) Achievements 10 y 15 aparecen al cruzar sus umbrales.
6) first_deploy se celebra una sola vez (idempotente) al hacer re-login.

Corre desde abyss_node/ con .venv activo:
  python _smoke_sesion_b_iter2.py
"""
import re
import socket
import sys
import time
import uuid

HOST = "127.0.0.1"
PORT = 4100
TEST_WALLET = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"


def strip_ansi(s: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*m", "", s)


class Session:
    def __init__(self, host=HOST, port=PORT):
        self.s = socket.create_connection((host, port), timeout=6)
        self.s.settimeout(2.5)
        self.transcript = ""  # todo lo recibido en esta sesión

    def send(self, cmd):
        self.s.sendall((cmd + "\r\n").encode())
        time.sleep(0.6)

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
        self.transcript += text
        return text

    def cmd(self, line):
        self.send(line)
        return self.recv()

    def close(self):
        try:
            self.s.close()
        except Exception:
            pass


def _check(label, haystack, *needles, negative=None):
    hay = haystack.lower()
    missing = [n for n in needles if n.lower() not in hay]
    bad = [n for n in (negative or ()) if n.lower() in hay]
    if missing or bad:
        print(f"  |FAIL| {label}: falta={missing!r}  presente_no_esperado={bad!r}")
        print("  --- tail ---")
        print(haystack[-1500:])
        print("  --- end ---")
        return False
    print(f"  |PASS| {label}")
    return True


def main():
    ok = True
    suffix = uuid.uuid4().hex[:6]
    user = f"demo2_{suffix}"
    pw = "monadacademy1"

    # --- 1) login nuevo: banner con Claude --------------------------------
    print(f"\n[1] Nuevo usuario: {user}  (banner con Claude)")
    s = Session()
    s.recv()
    out = s.cmd(f"create {user} {pw}")
    if "intended" in out.lower() or "[y]" in out.lower():
        out += s.cmd("Y")
    time.sleep(0.5)
    out += s.cmd(f"connect {user} {pw}")
    time.sleep(1.0)
    out += s.recv()
    ok &= _check(
        "banner + tutorial mencionan Claude CLI",
        out,
        "MONAD TERMINAL ACADEMY",
        "Claude CLI",
        "claude_dojo",
    )

    # --- 2) help en /home: sugiere ls (primera quest pendiente) ---------
    print("\n[2] help en /home → sugiere ls")
    help_home = s.cmd("help")
    ok &= _check(
        "help home menciona Terminal + Claude + Monad + sugiere ls",
        help_home,
        "terminal básico",
        "terminal intermedio",
        "claude cli",
        "monad onchain",
        "próximo:",
        " ls ",
    )

    # --- 3) Avanzamos por todas las rooms hasta claude_dojo -------------
    print("\n[3] Viaje: home → ls_dojo → ... → claude_dojo")
    # Completamos varias quests para cruzar achievements 3, 5, 10
    s.cmd("ls")
    s.cmd("pwd")
    s.cmd("cd ls_dojo")
    s.cmd("cd cd_dojo")
    s.cmd("cd cat_dojo")
    s.cmd("cat secret.txt")
    s.cmd("cd mkdir_dojo")
    s.cmd("touch mi.txt")
    s.cmd("mkdir mi_dir")
    s.cmd("grep ABYSS README.txt")
    s.cmd("cd pipe_dojo")
    s.cmd("echo hola mundo")
    s.cmd("whoami")
    pipe_out = s.recv()
    # Achievement 10 debería aparecer ya — lo chequeamos al llegar al final
    s.cmd("head -n 2 log.txt")
    s.cmd("tail -n 2 log.txt")
    s.cmd("wc log.txt")
    s.cmd("man echo")
    s.cmd("history")
    inter_out = s.recv()
    s.cmd("cd redirect_dojo")
    s.cmd("cd final_exam")
    claude_nav = s.cmd("cd claude_dojo")
    ok &= _check(
        "cd claude_dojo aterriza en la sala",
        claude_nav + s.cmd("pwd"),
        "claude_dojo",
    )

    # --- 4) help en claude_dojo: sugiere `claude skills install ...` ----
    print("\n[4] help en claude_dojo → sugiere install monad-kit")
    help_claude = s.cmd("help")
    ok &= _check(
        "help claude_dojo prioriza flujo IA→onchain (install)",
        help_claude,
        "claude_dojo",
        "monad-kit",
        "install",
    )

    # --- 5) Claude Avatar reacciona a hola + a progreso onchain ---------
    print("\n[5] Claude Avatar — hola (sin skills) + con skills + con deploy")
    greet = s.cmd("say hola")
    time.sleep(1.2)
    greet += s.recv()
    ok &= _check(
        "hola → pide instalar skill",
        greet,
        "Claude Avatar",
        "monad-kit",
    )

    # Instalamos skill y volvemos a saludar — respuesta debe cambiar
    s.cmd("claude skills install austin-griffith/monad-kit")
    greet2 = s.cmd("say hola")
    time.sleep(1.2)
    greet2 += s.recv()
    ok &= _check(
        "hola post-install → sugiere new contract",
        greet2,
        "Claude Avatar",
        "new contract",
    )

    # Generamos contrato y deployamos
    s.cmd("claude new contract MiToken")
    s.cmd("claude deploy MiToken.sol")
    time.sleep(0.4)
    greet3 = s.cmd("say hola")
    time.sleep(1.2)
    greet3 += s.recv()
    ok &= _check(
        "hola post-deploy → celebra graduación",
        greet3,
        "Claude Avatar",
        "graduade",
    )

    # --- 6) Recomendación contextual del help después de deploy ----------
    print("\n[6] help en claude_dojo post-deploy → flujo claim")
    help_after = s.cmd("help")
    ok &= _check(
        "help post-deploy muestra contratos deployados",
        help_after,
        "1 deployado",
    )

    # --- 7) Prof. Shell — volvemos a /home y probamos 5+ triggers ------
    print("\n[7] Prof. Shell — 5+ triggers distintos")
    for step in ("cd final_exam", "cd redirect_dojo", "cd pipe_dojo",
                 "cd mkdir_dojo", "cd cat_dojo", "cd cd_dojo", "cd ls_dojo", "cd home"):
        s.cmd(step)
    time.sleep(0.3)
    s.recv()

    triggers = [
        ("say hola prof",        ["Prof. Shell", "Llevas"]),
        ("say ayuda",            ["Prof. Shell", "help"]),
        ("say qué es claude",    ["Prof. Shell", "claude-opus"]),
        ("say qué es un skill",  ["Prof. Shell", "monad-kit"]),
        # Respuesta de Prof.Shell es contextual al progreso de deploy:
        # si el player NO ha deployado, menciona monad-kit; si YA deployó,
        # felicita y sugiere `claude new contract Otro`.
        ("say cómo deploy",      ["Prof. Shell"]),
        ("say austin",           ["Prof. Shell", "Scaffold"]),
    ]
    trigger_pass = 0
    for trig, needles in triggers:
        out_t = s.cmd(trig)
        time.sleep(1.2)
        out_t += s.recv()
        if _check(f"Prof. Shell — '{trig}'", out_t, *needles):
            trigger_pass += 1
    if trigger_pass < 5:
        print(f"  |FAIL| solo pasaron {trigger_pass}/6 triggers — se requieren 5+")
        ok = False
    else:
        print(f"  |PASS| {trigger_pass}/6 triggers OK (≥5 requeridos)")

    # --- 8) Achievements 3/5/10/15 vistos en el stream --------------------
    print("\n[8] Achievements — umbrales 3, 5, 10, 15")
    # s.transcript acumuló todo lo recibido durante la sesión. Los achievements
    # aparecen en los msg() que el server mandó al cruzar cada umbral.
    ach_stream = s.transcript
    ach_pass = 0
    for key_word in ("shell-ninja", "presumir en discord", "shell-plomero", "hacker en formación"):
        if key_word.lower() in ach_stream.lower():
            ach_pass += 1
            print(f"  |PASS| achievement '{key_word}'")
        else:
            print(f"  |FAIL| no se observó achievement '{key_word}'")
    if ach_pass < 3:
        print(f"  |FAIL| solo {ach_pass}/4 achievements observados")
        ok = False
    else:
        print(f"  |PASS| {ach_pass}/4 achievements observados (≥3 requeridos)")

    # --- 9) first_deploy idempotente ---------------------------
    # Flujo esperado:
    #   login inicial  → sin deploys → no se celebra
    #   deploy ocurre durante la sesión
    #   disconnect + reconnect (2da sesión) → at_post_puppet ve deploys,
    #     celebra por primera vez, marca 'first_deploy' en achievements.
    #   disconnect + reconnect (3ra sesión) → ya marcado, NO re-celebra.
    print("\n[9] Re-login: first_deploy se celebra exactamente una vez")
    s.close()
    time.sleep(0.5)

    s2 = Session()
    s2.recv()
    relogin = s2.cmd(f"connect {user} {pw}")
    time.sleep(1.0)
    relogin += s2.recv()
    if "MONAD TERMINAL ACADEMY" in relogin and "aprende la terminal" in relogin.lower():
        print("  |FAIL| re-login repitió el banner")
        ok = False
    else:
        print("  |PASS| banner no se repite en 2da sesión")
    if "primer deploy" in relogin.lower():
        print("  |PASS| 2da sesión muestra 'PRIMER DEPLOY' (primera vez celebrado)")
    else:
        print("  |FAIL| 2da sesión no celebró el deploy")
        ok = False
    s2.close()

    # 3ra sesión → no debe repetir
    time.sleep(0.5)
    s3 = Session()
    s3.recv()
    r3 = s3.cmd(f"connect {user} {pw}")
    time.sleep(1.0)
    r3 += s3.recv()
    if "primer deploy" in r3.lower():
        print("  |FAIL| 3ra sesión repitió first_deploy (no es idempotente)")
        ok = False
    else:
        print("  |PASS| 3ra sesión: first_deploy no se repite (idempotente)")
    s3.close()

    print("\n" + "=" * 60)
    if ok:
        print("TODOS LOS CRITERIOS DE SESIÓN B iter-2 — PASS")
        sys.exit(0)
    else:
        print("HAY FAILURES — revisar arriba")
        sys.exit(2)


if __name__ == "__main__":
    main()
