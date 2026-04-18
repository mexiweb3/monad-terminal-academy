"""
Monad Terminal Academy — `stats` command.

Lee eventos Transfer del contrato $TERM donde from == game wallet,
y muestra métricas del juego en tiempo real (total claims, top jugadores, etc).
Ideal para efecto wow en pitch live.
"""

from evennia import Command


class CmdStats(Command):
    """
    Muestra estadísticas onchain del juego (claims, top wallets, total distribuido).

    Usage:
      stats
    """
    key = "stats"
    aliases = ["leaderboard", "lb"]
    locks = "cmd:all()"
    help_category = "Monad"

    def func(self):
        caller = self.caller

        try:
            from abyss_node.onchain import get_claim_stats
        except Exception:
            from onchain import get_claim_stats

        try:
            s = get_claim_stats()
        except Exception as e:
            caller.msg(f"|rError leyendo onchain:|n {e}")
            return

        contract = s["contract"]
        c_short = f"{contract[:10]}...{contract[-6:]}"

        lines = [
            "",
            "|y╭─ Monad Terminal Academy — Stats Onchain ──────────╮|n",
            f"|y│|n  Contrato: |c{c_short}|n",
            f"|y│|n  Total claims:       |y{s['total_claims']}|n",
            f"|y│|n  Jugadores únicos:   |y{s['unique_players']}|n",
            f"|y│|n  Total distribuido:  |y{s['total_distributed']:.0f} $TERM|n",
        ]

        if s["last_tx"]:
            tx = s["last_tx"]
            tx_short = f"{tx[:10]}...{tx[-6:]}"
            lines.append(f"|y│|n  Último claim:       |w{tx_short}|n")
            lines.append(f"|y│|n  |x{s['explorer']}/tx/{tx}|n")

        lines.append("|y│|n")
        lines.append("|y│|n  |yLeaderboard — Top 5 wallets:|n")
        if s["top"]:
            medals = ["🥇", "🥈", "🥉", " 4.", " 5."]
            for i, (addr, amt) in enumerate(s["top"]):
                medal = medals[i] if i < len(medals) else f"{i+1:>2}."
                short = f"{addr[:6]}...{addr[-4:]}"
                lines.append(
                    f"|y│|n   {medal} |c{short}|n  |y{amt:>7.0f} $TERM|n"
                )
        else:
            lines.append(
                "|y│|n   (aún nadie hace claim — |wsé el primero|n con |wlink|n y |wclaim|n)"
            )

        lines.append("|y╰────────────────────────────────────────────────────╯|n")
        caller.msg("\n".join(lines))
