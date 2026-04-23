"""
CmdMemories — muestra los fragmentos de memoria coleccionados.

Lee `caller.db.memories` (lista de ids tipo "m01") y los cruza con la
definición canónica en `world.lore.fragments.FRAGMENTS`. Los fragmentos
coleccionados se listan verdes con su título + primer párrafo del `body`.
Los pendientes se muestran en gris con placeholder `???`.

Diseño intencional:
- NO spoilea contenido de fragmentos pendientes (sólo los que tienes).
- Numeración visual `[N/TOTAL]` para sensación de progreso.
- Separador Unicode entre entradas para legibilidad en logs largos.

Ver también:
- `world/lore/fragments.py` — definición de los 10 fragmentos.
- `typeclasses/characters.py::_detect_memory_fragment` — es el hook que
  llena `db.memories` cuando el jugador hace `cat fragmento_XX.mem`.
"""

from evennia import Command


class CmdMemories(Command):
    """
    Muestra los fragmentos de memoria que has recuperado hasta ahora.

    Usage:
      memories
      memoria
      fragmentos

    Cada `cat fragmento_XX.mem` agrega uno a tu colección. El listado
    completo son 10 fragmentos distribuidos en los 10 rooms.
    """

    key = "memories"
    aliases = ["memoria", "fragmentos"]
    locks = "cmd:all()"
    help_category = "Monad"

    def func(self):
        caller = self.caller
        # Import defensivo — si falla la lore, damos mensaje claro sin romper.
        try:
            from world.lore.fragments import FRAGMENTS
        except Exception as exc:
            caller.msg(f"|r⚠|n no pude cargar los fragmentos: {exc}")
            return

        collected = list(caller.db.memories or [])
        total = len(FRAGMENTS)
        got = sum(1 for f in FRAGMENTS if f["id"] in collected)

        sep = "  |x" + ("·" * 58) + "|n"

        lines = [
            "",
            f"|MFragmentos de memoria|n  |y{got}/{total}|n recuperados",
            "",
        ]

        for idx, frag in enumerate(FRAGMENTS, start=1):
            got_it = frag["id"] in collected
            label = f"[{idx:>2}/{total}]"
            if got_it:
                # Primer párrafo del body (dividido por doble \n o fallback al body completo)
                body = (frag.get("body") or "").strip()
                first_para = body.split("\n\n", 1)[0]
                lines.append(f"  |g{label} Fragmento {_roman(idx)} · {frag['title']}|n")
                for bline in _wrap_plain(first_para, 60):
                    lines.append(f"    |g{bline}|n")
            else:
                lines.append(f"  |x{label} ??? — sigue aprendiendo|n")
            lines.append(sep)

        # Hint de cierre — orienta al jugador al siguiente paso.
        if got < total:
            lines.append(
                f"  |yHas recuperado {got} de {total} fragmentos.|n "
                "Encuentra más archivos `.mem` con `ls` y `cat`."
            )
        else:
            lines.append(
                "  |GHas recuperado los 10 fragmentos.|n "
                "Usa |wmint|n para grabar tu certificado onchain."
            )

        caller.msg("\n".join(lines))


# ---------- helpers locales ----------
def _roman(n: int) -> str:
    """Convierte 1..10 a romanos (I..X). Simple, sólo para UI."""
    mapping = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V",
               6: "VI", 7: "VII", 8: "VIII", 9: "IX", 10: "X"}
    return mapping.get(n, str(n))


def _wrap_plain(text: str, width: int) -> list[str]:
    """Wrap simple por palabras, sin ANSI. Mantiene saltos de línea originales."""
    out = []
    for paragraph in (text or "").split("\n"):
        if not paragraph.strip():
            out.append("")
            continue
        words = paragraph.split()
        cur = ""
        for w in words:
            if len(cur) + len(w) + 1 <= width:
                cur = (cur + " " + w).strip()
            else:
                if cur:
                    out.append(cur)
                cur = w
        if cur:
            out.append(cur)
    return out
