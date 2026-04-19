"""
Engine de puzzles de Terminal Academy — Sesión D (gameplay).

Puzzles soportados:
  grep_token  → archivo crypto_log.txt con 150 líneas de ruido + 1 TOKEN.
                Se resuelve con `grep TOKEN crypto_log.txt`.
  pipe_count  → archivo mensaje.enc con líneas mezcladas; 3 tienen "clave".
                Se resuelve con `cat mensaje.enc | grep clave | wc -l` → 3.

El state por player vive en `caller.db.puzzles_done` (dict de bool).

El spawn de archivos cachea el contenido generado en `room.db.academy_files`
para que todos los players vean el mismo puzzle (determinístico por semilla).
"""

import hashlib
import random
from typing import Optional


# El TOKEN escondido en crypto_log.txt — determinístico, formato MTY-2026-XXXXXX
CRYPTO_TOKEN = "MTY-2026-4BYSS9"


# Palabras para generar ruido "realista" de log encriptado
_NOISE_WORDS = [
    "aaa111", "bbb222", "ccc333", "ddd444", "eee555", "fff666",
    "x9y", "qw4z", "r7t", "p0k", "lm2", "b3c",
    "null", "void", "zero", "hash", "byte", "word",
    "0xDEAD", "0xCAFE", "0xBEEF", "0xFACE", "0xC0DE", "0xF00D",
    "ok", "no", "maybe", "tbd", "wip", "rip",
]

_NOISE_PREFIXES = [
    "log", "sys", "pkt", "dat", "ent", "trx",
    "req", "res", "tmp", "buf", "q", "z",
]


def _seeded_line(rng: random.Random, i: int) -> str:
    """Genera una línea pseudoaleatoria de ~8 tokens, estilo log-de-hacker."""
    prefix = rng.choice(_NOISE_PREFIXES)
    n_tokens = rng.randint(4, 9)
    toks = [rng.choice(_NOISE_WORDS) for _ in range(n_tokens)]
    return f"{prefix}:{i:04d} " + " ".join(toks)


def generate_crypto_log(total_lines: int = 150, token: str = CRYPTO_TOKEN) -> str:
    """
    Genera 150 líneas de ruido + 1 línea oculta con el TOKEN.
    La línea del TOKEN se coloca en una posición pseudoaleatoria pero fija
    (seed fija → todos los players ven el mismo layout).
    """
    rng = random.Random(42)  # semilla fija → contenido determinístico
    token_line_idx = rng.randint(30, total_lines - 20)
    lines = []
    for i in range(total_lines):
        if i == token_line_idx:
            # Camuflada entre ruido pero grep-able por "TOKEN"
            lines.append(f"pkt:{i:04d} auth_ok {rng.choice(_NOISE_WORDS)} TOKEN: {token} {rng.choice(_NOISE_WORDS)}")
        else:
            lines.append(_seeded_line(rng, i))
    return "\n".join(lines)


def generate_mensaje_enc() -> str:
    """
    Archivo con 12 líneas mezcladas; exactamente 3 contienen la palabra 'clave'.
    Determinístico (seed fija).
    """
    rng = random.Random(777)
    lines = [
        "01 inicio del mensaje cifrado",
        "02 la senal viaja por el canal oscuro",
        "03 clave: el primer eco del corruptor",
        "04 ruido ruido ruido estatica",
        "05 pkt 0xDEAD 0xBEEF pkt",
        "06 clave: teclear es recordar",
        "07 otro fragmento sin pistas",
        "08 0xCAFE 0xF00D nada que ver",
        "09 clave: el que cuenta nunca olvida",
        "10 fin del bloque",
        "11 silencio silencio",
        "12 checksum ok",
    ]
    rng.shuffle(lines)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Definición de puzzles
# ---------------------------------------------------------------------------
PUZZLES = [
    {
        "id": "grep_token",
        "room": "ls_dojo",
        "filename": "crypto_log.txt",
        "title": "Cazador de patrones",
        "description": (
            "Hay un TOKEN escondido entre 150 líneas de ruido. "
            "Usa `grep TOKEN crypto_log.txt` para extraerlo."
        ),
        "reward": 40,
        "body": (
            "Encontraste el TOKEN entre 150 líneas de ruido — así funciona el "
            "pattern-matching en el mundo real."
        ),
    },
    {
        "id": "pipe_count",
        "room": "pipe_dojo",
        "filename": "mensaje.enc",
        "title": "Pipeline maestro",
        "description": (
            "Cuenta cuántas líneas del `mensaje.enc` contienen la palabra 'clave'. "
            "Pista: `cat mensaje.enc | grep clave | wc -l`."
        ),
        "reward": 50,
        "body": (
            "Encadenaste tres comandos con pipes. Ya piensas en pipelines, "
            "como un administrador de sistemas de verdad."
        ),
    },
]

PUZZLES_BY_ID = {p["id"]: p for p in PUZZLES}
PUZZLES_BY_FILE = {p["filename"]: p for p in PUZZLES}


# ---------------------------------------------------------------------------
# State & helpers
# ---------------------------------------------------------------------------
def ensure_puzzles_state(caller) -> dict:
    """Inicializa `caller.db.puzzles_done` como dict y lo devuelve."""
    if caller.db.puzzles_done is None:
        caller.db.puzzles_done = {}
    # Evennia _SaverDict → convertir a dict puro cuando hace falta
    if not isinstance(caller.db.puzzles_done, dict):
        caller.db.puzzles_done = {}
    return caller.db.puzzles_done


def is_puzzle_done(caller, puzzle_id: str) -> bool:
    state = ensure_puzzles_state(caller)
    return bool(state.get(puzzle_id))


def mark_puzzle_done(caller, puzzle_id: str) -> bool:
    """
    Marca un puzzle como resuelto. Devuelve True si es la primera vez,
    False si ya estaba resuelto (idempotente).
    """
    state = ensure_puzzles_state(caller)
    if state.get(puzzle_id):
        return False
    # Copiar para forzar persistencia (sorteando _SaverDict)
    new_state = dict(state)
    new_state[puzzle_id] = True
    caller.db.puzzles_done = new_state
    return True


def spawn_puzzle_files(caller=None) -> list:
    """
    Inyecta los archivos de los puzzles en `room.db.academy_files` para que
    todos los players los vean. Idempotente: sobreescribe cada vez con el
    contenido determinístico generado.

    Devuelve lista de rooms tocados (para log/debug).
    """
    from evennia.utils.search import search_object
    from typeclasses.rooms import Room

    touched = []
    for puzzle in PUZZLES:
        rooms = search_object(puzzle["room"], typeclass=Room)
        if not rooms:
            if caller:
                caller.msg(f"[puzzles] room {puzzle['room']} no existe aún")
            continue
        room = rooms[0]
        files = dict(room.db.academy_files or {})
        if puzzle["id"] == "grep_token":
            files[puzzle["filename"]] = generate_crypto_log()
        elif puzzle["id"] == "pipe_count":
            files[puzzle["filename"]] = generate_mensaje_enc()
        room.db.academy_files = files
        touched.append(puzzle["room"])
        if caller:
            caller.msg(f"[puzzles] spawn '{puzzle['filename']}' en {puzzle['room']}")
    return touched


# ---------------------------------------------------------------------------
# Mini-boss: El Eco del Corruptor
# ---------------------------------------------------------------------------
# Archivos del room `final_exam` que el Corruptor puede "corromper" durante
# la pelea. El jugador debe reconstruirlos con `reconstruct <nombre>`.
CORRUPTOR_FILES = [
    {
        "name": "secret.txt",
        "original": (
            "// secret.txt\n"
            "Tu identidad verdadera vive onchain. La clave es `claim`.\n"
        ),
    },
    {
        "name": "manifesto.txt",
        "original": (
            "// manifesto.txt\n"
            "Quien teclea no olvida. Quien olvida no teclea.\n"
            "Teclear es existir.\n"
        ),
    },
    {
        "name": "runa.txt",
        "original": (
            "// runa.txt\n"
            "ls -> cd -> cat -> mkdir -> touch -> grep\n"
            "echo -> head -> tail -> wc -> claude -> deploy\n"
            "link -> claim.\n"
        ),
    },
]

CORRUPTOR_FILES_BY_NAME = {f["name"]: f for f in CORRUPTOR_FILES}


# Texto que el Corruptor deja al "corromper" un archivo
def corrupt_text(name: str) -> str:
    """Genera texto corrupto reemplazando el contenido original."""
    glitch_chars = "#@%&*!?~^"
    seed = int(hashlib.sha256(name.encode()).hexdigest()[:8], 16)
    rng = random.Random(seed)
    lines = []
    lines.append(f"// {name} — CORRUPTED by the Eco")
    for _ in range(5):
        n = rng.randint(20, 40)
        lines.append("".join(rng.choice(glitch_chars) for _ in range(n)))
    lines.append("(el archivo fue comido por el Eco. reconstruye con `reconstruct`.)")
    return "\n".join(lines)
