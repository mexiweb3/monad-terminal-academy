"""
CmdVerify — portal de vuelta: verifica onchain lo que el alumno hizo en
SU terminal real.

Terminal Academy enseña Claude Code / OpenClaw / Hermes **de verdad**:
el alumno sale del MUD, instala la herramienta, la usa para deployar
un contrato a Monad testnet, y vuelve aquí a pegar el tx hash.

Este comando es el único "juez" del flujo real — lee la cadena con
``utils.monad_rpc.verify_deploy`` y, si la tx chequea, completa la
quest ``q18_deploy`` y guarda el contrato en
``caller.db.deployed_contracts``.

Subcomandos::

    verify claude <tx>       valida deploy de ERC-20 con Claude Code
    verify openclaw <tx>     valida deploy con OpenClaw
    verify hermes <tx>       valida deploy con Hermes

El comportamiento es idéntico para los tres: lo que cambia es la
narrativa de la Forjadora y el mapeo a quests. Si querés diferenciar
criterios (ej. "openclaw requiere ERC-721", "hermes requiere batch"),
ese es el hook — extendé ``_TOOL_CONFIG``.
"""

from __future__ import annotations

import time

from evennia import Command


# ---------------------------------------------------------------------------
# Config por herramienta
# ---------------------------------------------------------------------------

# slug → config. La quest `q18_deploy` acepta cualquiera de las tres
# tools como "supo deployar" — su trigger (`verify:claude`) se dispara
# cuando el alumno verifica CON CUALQUIER tool; es el alias canónico.
# Si querés quests separadas por tool más adelante (ej. q24_verify_openclaw),
# cambiá ``quest_cmd`` aquí y añadilas a QUESTS.
_TOOL_CONFIG: dict[str, dict] = {
    "claude": {
        "label": "Claude Code",
        "quest_cmd": "verify:claude",
        "tag": "claude-code",
        "bonus_line": (
            "La Forjadora reconoce la firma de Anthropic en tu bytecode. "
            "El contrato queda registrado en tu bitácora."
        ),
    },
    "openclaw": {
        "label": "OpenClaw",
        "quest_cmd": "verify:claude",
        "tag": "openclaw",
        "bonus_line": (
            "La Forjadora estudia el deploy open-source. "
            "Un agente que nadie controla también es digno."
        ),
    },
    "hermes": {
        "label": "Hermes",
        "quest_cmd": "verify:claude",
        "tag": "hermes",
        "bonus_line": (
            "La Forjadora saluda al mensajero de Nous. "
            "El deploy queda en la bitácora junto al resto."
        ),
    },
}

# bonus extra (en $TERM) que se suma SOLO si el deployer == caller.db.wallet
# (la tx de deploy fue firmada por la misma wallet que el alumno linkeó).
_WALLET_MATCH_BONUS = 50


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _usage(caller) -> None:
    caller.msg(
        "|cverify|n — valida onchain lo que hiciste en tu terminal real.\n"
        "\n"
        "Subcomandos:\n"
        "  |wverify claude <tx>|n     deploy con Claude Code\n"
        "  |wverify openclaw <tx>|n   deploy con OpenClaw\n"
        "  |wverify hermes <tx>|n     deploy con Hermes\n"
        "\n"
        "El <tx> es el hash que te devuelve tu CLI al deployar en Monad\n"
        "testnet (chainId |y10143|n). Empieza con |w0x|n y tiene 66 chars."
    )


def _ensure_state(caller) -> None:
    """Idempotente: prepara los attrs que el comando va a leer/escribir."""
    if caller.db.deployed_contracts is None:
        caller.db.deployed_contracts = []
    if caller.db.quest_done is None:
        caller.db.quest_done = []
    if caller.db.abyss_pending is None:
        caller.db.abyss_pending = 0


def _record_history(caller, args: str) -> None:
    """Best-effort: graba la línea en ``caller.db.cmd_history`` si existe."""
    try:
        from commands.terminal_commands import _record_history as _rh
        _rh(caller, "verify", args)
    except Exception:
        pass


def _reward_quest(caller, cmd_key: str) -> None:
    """Delega al helper de terminal_commands para mantener un único camino
    de rewards (mensaje/prompt consistentes con el resto del MUD)."""
    try:
        from commands.terminal_commands import _reward_if_quest
        _reward_if_quest(caller, cmd_key)
    except Exception:
        pass


def _addrs_equal(a: str | None, b: str | None) -> bool:
    """Compara dos addresses EVM case-insensitive (ignora checksumming)."""
    if not a or not b:
        return False
    return a.strip().lower() == b.strip().lower()


# ---------------------------------------------------------------------------
# CmdVerify
# ---------------------------------------------------------------------------


class CmdVerify(Command):
    """
    Verifica onchain un deploy real que hiciste en tu terminal
    (Claude Code / OpenClaw / Hermes) contra Monad testnet.

    Usage:
      verify claude <tx>
      verify openclaw <tx>
      verify hermes <tx>

    Flujo pedagógico:
      1) Instalás la tool en TU terminal real (ver install_dojo).
      2) Usás la tool para generar + deployar un ERC-20 en Monad testnet.
      3) Copiás el tx hash que la tool te devuelve.
      4) Pegás aquí: `verify claude 0xabc...`
      5) El MUD consulta https://testnet-rpc.monad.xyz y, si el deploy es
         real y exitoso, desbloquea la quest `q18_deploy` y suma $TERM.

    Si tenés wallet linkeada (`link 0x...`) y el deployer == tu wallet,
    sumás |y+50 $TERM|n extra.
    """

    key = "verify"
    locks = "cmd:all()"
    help_category = "Monad"

    def func(self):
        caller = self.caller
        _ensure_state(caller)
        raw = (self.args or "").strip()
        _record_history(caller, raw)

        if not raw:
            _usage(caller)
            return

        parts = raw.split()
        sub = parts[0].lower()

        if sub in ("help", "-h", "--help"):
            _usage(caller)
            return

        if sub not in _TOOL_CONFIG:
            caller.msg(
                f"|rverify:|n subcomando desconocido '|y{sub}|n'.\n"
                "Válidos: |wclaude|n · |wopenclaw|n · |whermes|n. "
                "Teclea |wverify|n sin args para ayuda."
            )
            return

        if len(parts) < 2:
            caller.msg(f"usage: |wverify {sub} <tx-hash>|n")
            return

        tx_hash = parts[1]
        cfg = _TOOL_CONFIG[sub]
        self._verify_deploy_flow(caller, tx_hash, sub, cfg)

    # ------------------------------------------------------------------
    # Core flow
    # ------------------------------------------------------------------
    def _verify_deploy_flow(self, caller, tx_hash: str, tool_slug: str, cfg: dict) -> None:
        """Consulta el RPC de Monad y, si chequea, reparte rewards + guarda."""
        label = cfg["label"]
        caller.msg(
            f"|y⋯|n consultando Monad testnet por tu deploy con |c{label}|n...\n"
            f"   tx: |w{tx_hash}|n"
        )

        try:
            from utils.monad_rpc import verify_deploy
        except Exception as e:  # pragma: no cover — import solo falla en dev
            caller.msg(f"|rverify:|n error interno importando monad_rpc: {e}")
            return

        try:
            result = verify_deploy(tx_hash)
        except Exception as e:  # defensivo — monad_rpc levanta RuntimeError bien
            caller.msg(
                f"|rverify:|n no pude consultar el RPC de Monad — {e}\n"
                "Probá de nuevo en unos segundos. Si persiste, puede ser rate-limit."
            )
            return

        if not result["valid"]:
            err = result.get("error") or "verificación falló (error desconocido)"
            caller.msg(
                f"|r✗ verify {tool_slug}:|n {err}\n"
                "\n"
                "Checklist:\n"
                "  · el hash empieza con |w0x|n y tiene 66 chars\n"
                "  · deployaste a Monad testnet (chainId |y10143|n), no a otra chain\n"
                "  · esperaste a que la tx se mineara (1-2 segundos)\n"
                "  · pegaste el hash de la tx de |wdeploy|n, no de una llamada posterior"
            )
            return

        # ----- deploy válido ------------------------------------------
        contract = result["contract"]
        deployer = result["from"]
        block = result["block"]

        # Guardar el contrato en la bitácora del alumno (idempotente).
        deployed = list(caller.db.deployed_contracts or [])
        # evitá duplicados exactos (mismo tx)
        if not any(d.get("tx", "").lower() == tx_hash.strip().lower() for d in deployed):
            deployed.append({
                "address": contract,
                "tx": tx_hash.strip(),
                "from": deployer,
                "block": block,
                "tool": tool_slug,
                "ts": int(time.time()),
                "verified_by": "monad_rpc",
            })
            caller.db.deployed_contracts = deployed

        # ¿La wallet linkeada matchea al deployer?
        wallet = (caller.db.wallet or "").strip()
        wallet_match = _addrs_equal(wallet, deployer)
        bonus_awarded = 0
        if wallet_match:
            caller.db.abyss_pending = int(caller.db.abyss_pending or 0) + _WALLET_MATCH_BONUS
            bonus_awarded = _WALLET_MATCH_BONUS

        # Narrativa de la Forjadora + receipt visual
        explorer = f"https://testnet.monadexplorer.com/address/{contract}"
        block_str = f"{block}" if block is not None else "pending"

        caller.msg(
            f"\n|g╭─ verify {tool_slug} → Monad testnet ✓ ─────────╮|n\n"
            f"|g│|n  tool:      |c{label}|n\n"
            f"|g│|n  contract:  |y{contract}|n\n"
            f"|g│|n  deployer:  |c{deployer}|n\n"
            f"|g│|n  block:     |w{block_str}|n\n"
            f"|g│|n  tx:        |w{tx_hash}|n\n"
            f"|g│|n  explorer:  {explorer}\n"
            f"|g╰────────────────────────────────────────────────╯|n"
        )

        if wallet_match:
            caller.msg(
                f"|g★ WALLET MATCH|n — deploy firmado con tu wallet linkeada.\n"
                f"  |y+{bonus_awarded} $TERM|n extra (total pendiente: |y{caller.db.abyss_pending}|n)"
            )
        elif wallet:
            caller.msg(
                "|y!|n Tu wallet linkeada no matchea al deployer de esta tx.\n"
                f"  wallet:   |c{wallet}|n\n"
                f"  deployer: |c{deployer}|n\n"
                "  Sin match no hay bonus +50 — pero el deploy igual cuenta como quest."
            )
        else:
            caller.msg(
                "|y!|n Sin wallet linkeada no puedo asociarte este deploy en el "
                "leaderboard por wallet — teclea |wlink 0x...|n y después "
                f"|wverify {tool_slug} {tx_hash}|n otra vez para sumar el bonus +50."
            )

        # Flavor narrativo de la Forjadora (una línea, no satura al player)
        caller.msg(f"|m✦ {cfg['bonus_line']}|n")

        # Quest: usamos el mismo helper que el resto del MUD para que el
        # mensaje de reward y el prompt sean idénticos al flujo original.
        _reward_quest(caller, cfg["quest_cmd"])
