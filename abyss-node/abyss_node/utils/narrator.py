"""
Helpers narrativos — separa visualmente el mundo-de-juego de la terminal-real.

Regla mental del jugador: si ves emoji/bordes/colores warm → es el mundo hablándote.
Si ves monoespaciado raw → es el filesystem respondiendo.

Modos soportados:
  narrate(caller, text)                  🎙  Narrador (magenta)
  dialogue(caller, npc, text)            » NPC: ...  (cyan)
  scene(caller, title, body)             ━━━ CAPÍTULO ━━━  (cinemático)
  achievement(caller, title, body, reward)  ★ box warm
  error_sys(caller, msg)                 ⚠ Error (rojo)
  terminal(caller, text)                 raw output (semántico, sin decoración)

Ejemplo:
    from utils.narrator import narrate, dialogue, scene, achievement

    scene(caller, "CAPÍTULO I: DESPERTAR",
          "Abres los ojos. No recuerdas cómo llegaste aquí.")
    dialogue(caller, "Prof. Shell",
             "Respira, Neófito. Te encontré justo a tiempo.")
    achievement(caller, "Primer respiro",
                "El filesystem responde a tu llamada.", reward=10)
"""

import textwrap

from evennia.utils.ansi import strip_ansi


WIDTH = 62


def _wrap(text: str, width: int) -> list[str]:
    """Word-wrap respetando saltos de línea existentes."""
    out = []
    for paragraph in (text or "").split("\n"):
        if not paragraph.strip():
            out.append("")
            continue
        wrapped = textwrap.wrap(
            paragraph,
            width=width,
            break_long_words=False,
            replace_whitespace=False,
            drop_whitespace=True,
        )
        out.extend(wrapped or [""])
    return out


def _pad_visible(line: str, width: int) -> str:
    """Padding derecho ignorando los códigos ANSI que Evennia interpreta como |x."""
    visible = strip_ansi(line)
    # Evennia usa |x como códigos, strip_ansi los deja; contamos chars reales
    raw = _strip_evennia_tags(visible)
    pad = max(0, width - len(raw))
    return line + " " * pad


def _strip_evennia_tags(text: str) -> str:
    """Quita markers |x|X|c|y|m|r|g|n|... de Evennia para medir ancho real."""
    import re
    return re.sub(r"\|[a-zA-Z#*][0-9a-fA-F]?", "", text or "")


def narrate(caller, text: str):
    """Narrador omnisciente — magenta con prefix 🎙 y ancho 62."""
    lines = _wrap(text, WIDTH - 4)
    if not lines:
        return
    out = []
    for i, line in enumerate(lines):
        prefix = "🎙  " if i == 0 else "   "
        out.append(f"|M{prefix}|n|m{line}|n")
    caller.msg("\n".join(out))


def dialogue(caller, npc_name: str, text: str):
    """NPC diálogo — cyan, nombre resaltado."""
    lines = _wrap(text, WIDTH - 6)
    if not lines:
        return
    out = [f"|C» {npc_name}|n|c: {lines[0]}|n"]
    indent = " " * (len(npc_name) + 4)
    for line in lines[1:]:
        out.append(f"|c{indent}{line}|n")
    caller.msg("\n".join(out))


def scene(caller, title: str, body: str = ""):
    """Cinemática de capítulo — separadores dobles + título centrado."""
    sep = "━" * WIDTH
    inner_w = WIDTH - 2
    title_line = title.upper()
    title_pad = max(0, (inner_w - len(title_line)) // 2)
    title_fmt = " " * title_pad + title_line
    title_fmt = title_fmt + " " * max(0, inner_w - len(title_fmt))
    out = [
        "",
        f"|M{sep}|n",
        f"|M{title_fmt}|n",
        f"|M{sep}|n",
        "",
    ]
    for line in _wrap(body, WIDTH - 2):
        out.append(f"|m  {line}|n")
    out.append("")
    caller.msg("\n".join(out))


def achievement(caller, title: str, body: str = "", reward: int = 0):
    """Logro — box warm con ★ y reward."""
    lines = [f"|Y★ {title}|n"]
    if body:
        for line in _wrap(body, WIDTH - 6):
            lines.append(f"|y  {line}|n")
    if reward:
        lines.append(f"|y  +{reward} $TERM|n")

    inner_w = max(_visible_len(l) for l in lines) + 2
    inner_w = max(inner_w, 30)
    top = "|y╭─" + "─" * inner_w + "─╮|n"
    bot = "|y╰─" + "─" * inner_w + "─╯|n"
    out = [top]
    for line in lines:
        pad = inner_w - _visible_len(line)
        out.append(f"|y│|n {line}{' ' * max(0, pad)} |y│|n")
    out.append(bot)
    caller.msg("\n".join(out))


def _visible_len(line: str) -> int:
    return len(_strip_evennia_tags(strip_ansi(line)))


def error_sys(caller, msg: str):
    """Error del sistema — rojo con icono."""
    caller.msg(f"|r⚠  {msg}|n")


def terminal(caller, text: str):
    """Output de terminal real — raw, sin decoración (alias semántico)."""
    caller.msg(text)


def prompt(caller):
    """Re-emite el prompt actual (conveniente para llamar desde contextos custom)."""
    loc = caller.location
    path = f"/academy/{loc.key}" if loc else "/academy"
    name = caller.key or "neo"
    try:
        caller.msg(prompt=f"|g{name}@academy|n:|c{path}|n|w$|n ")
    except Exception:
        pass
