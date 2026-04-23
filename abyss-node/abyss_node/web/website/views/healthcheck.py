"""
Healthcheck endpoint — `/health`

Devuelve JSON con el estado del server para que:
  * nginx (o uptimerobot / bettstack) lo pinguee cada 60s y avise si cae.
  * El admin lo cure con curl desde SSH sin levantar logs enteros.

Contrato (intencionalmente simple):
    GET /health        → 200 {"status": "ok",   "db": "ok",   "uptime_sec": N, ...}
    GET /health        → 503 {"status": "fail", "db": "fail", "error": "..."}  si DB caída

El status HTTP refleja el estado real:
  * 200 si todo responde.
  * 503 si un sub-check (DB) falla → monitor externos pueden trigerear alertas.

No hace queries pesadas: sólo `connection.ensure_connection()` que valida el
pool de la DB. Pensado para poder llamarse cada pocos segundos sin coste.
"""

from __future__ import annotations

import os
import time

from django.db import connection
from django.http import JsonResponse

# Marca de "cuándo arrancó este proceso" — se setea la primera vez que se
# importa el módulo. En Evennia eso es early durante el boot del Server.
_PROC_START = time.time()


def _version() -> str:
    """Mejor-esfuerzo: lee git SHA si hay HEAD file, else 'unknown'.

    NO usa subprocess git porque queremos evitar fork/exec en un endpoint
    que se pinguea muy seguido; leer el archivo es O(fs_cache).
    """
    # /root/monadmty/.git/HEAD → "ref: refs/heads/main"
    # Luego /root/monadmty/.git/refs/heads/main → SHA
    try:
        here = os.path.dirname(os.path.abspath(__file__))
        # .../abyss-node/abyss_node/web/website/views  → subir 5 niveles
        root = os.path.abspath(os.path.join(here, "..", "..", "..", "..", ".."))
        git_path = os.path.join(root, ".git")
        # Caso A: .git es dir (clon normal, que es como vive prod)
        # Caso B: .git es file con "gitdir: /ruta/real" (worktree)
        if os.path.isdir(git_path):
            gitdir = git_path
        elif os.path.isfile(git_path):
            with open(git_path, "r", encoding="utf-8") as fh:
                line = fh.read().strip()
            if line.startswith("gitdir:"):
                gitdir = line.split(":", 1)[1].strip()
            else:
                return "unknown"
        else:
            return "unknown"

        head_path = os.path.join(gitdir, "HEAD")
        if not os.path.isfile(head_path):
            return "unknown"
        with open(head_path, "r", encoding="utf-8") as fh:
            content = fh.read().strip()
        if content.startswith("ref:"):
            ref = content.split(" ", 1)[1].strip()
            ref_path = os.path.join(gitdir, ref)
            if os.path.isfile(ref_path):
                with open(ref_path, "r", encoding="utf-8") as fh:
                    return fh.read().strip()[:12]
            # Worktrees: refs viven en el gitdir principal, no en el del worktree
            # (gitdir.endswith("/.git/worktrees/<name>") → subir 2 niveles)
            parent = os.path.abspath(os.path.join(gitdir, "..", ".."))
            fallback = os.path.join(parent, ref)
            if os.path.isfile(fallback):
                with open(fallback, "r", encoding="utf-8") as fh:
                    return fh.read().strip()[:12]
            return "unknown"
        # detached HEAD — content es el SHA
        return content[:12]
    except Exception:
        return "unknown"


def health(request):
    """Healthcheck simple. NO requiere auth."""
    payload = {
        "status": "ok",
        "service": "terminal-academy",
        "version": _version(),
        "uptime_sec": int(time.time() - _PROC_START),
        "db": "unknown",
    }
    http_status = 200

    # DB ping — `ensure_connection` hace un connect lazy sin query.
    try:
        connection.ensure_connection()
        payload["db"] = "ok"
    except Exception as exc:
        payload["status"] = "fail"
        payload["db"] = "fail"
        payload["error"] = repr(exc)
        http_status = 503

    return JsonResponse(payload, status=http_status)
