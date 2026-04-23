"""
CmdMint — graba el certificado NFT "Terminal Academy Graduate" onchain.

POR AHORA este comando SIMULA el mint (graba un tx hash fake + tokenId
secuencial en `caller.db.minted_cert`). Cuando tengamos el contrato
deployado, descomentar el bloque `# --- REAL MINT ---` y conectar a la
RPC de Monad testnet.

Spec del NFT a deployar (para la sesión que implemente el mint real):

    ERC-721 "Terminal Academy Graduate"
    symbol: TA-GRAD
    metadata (tokenURI, JSON IPFS):
      {
        "name":        "Academy Graduate #<tokenId>",
        "description": "Certificate of completion — Terminal Academy",
        "image":       "ipfs://<hash>/graduate.png",
        "attributes": [
          {"trait_type": "quests",          "value": 21},
          {"trait_type": "memories",        "value": 10},
          {"trait_type": "graduation_date", "value": <unix_ts>}
        ]
      }
    contract:  pendiente deploy (Monad testnet — mismo deployer que $TERM)
    access:    mint permissionless si el caller passes on-chain attestation
               del Terminal Academy registry (lookup: registry.isGraduate(addr))
    registry:  TBD — en paralelo a este contract hay que deployar el
               `TerminalAcademyRegistry` que marca la dirección como graduada
               cuando el backend firma el mensaje EIP-712 "Graduated(addr, ts)".

Requisitos previos para disponibilidad del comando:
  - todas las quests completadas: `len(quest_done) == len(QUESTS)`
  - wallet linkeada: `self.db.wallet` no vacío

Si falta algo, el comando lista QUÉ falta (quests + wallet).
"""

import time

from evennia import Command


class CmdMint(Command):
    """
    Graba tu certificado de Terminal Academy onchain como NFT.

    Usage:
      mint
      cert
      graduate

    Requiere: todas las quests completadas + wallet linkeada.
    Si faltan requisitos, el comando te dice qué te falta.
    """

    key = "mint"
    aliases = ["cert", "graduate"]
    locks = "cmd:all()"
    help_category = "Monad"

    def func(self):
        caller = self.caller

        # --- Precondiciones ---
        try:
            from commands.terminal_commands import QUESTS
        except Exception:
            QUESTS = []
        total_q = len(QUESTS) or 21
        done = list(caller.db.quest_done or [])
        wallet = caller.db.wallet or ""

        missing = []
        if len(done) < total_q:
            missing.append(
                f"|r·|n te faltan |w{total_q - len(done)}|n quests "
                f"(|w{len(done)}/{total_q}|n completadas). "
                "Usa |wquests|n para ver cuáles."
            )
        if not wallet:
            missing.append(
                "|r·|n no tienes wallet linkeada. "
                "Usa |wlink 0x...|n o |wlink nombre.eth|n."
            )
        if missing:
            caller.msg("\n|y⚠ Antes de graduarte necesitas:|n")
            for m in missing:
                caller.msg(f"  {m}")
            return

        # --- Idempotencia ---
        already = caller.db.minted_cert
        if isinstance(already, dict) and already.get("tx"):
            caller.msg(
                "\n|yYa tienes un certificado emitido|n:\n"
                f"  tokenId: |c#{already.get('tokenId', '?')}|n\n"
                f"  tx:      |w{already.get('tx', '?')}|n\n"
                f"  wallet:  |c{already.get('wallet', wallet)}|n\n"
                "  (un Graduate NFT por cuenta — si necesitas re-emitir, "
                "contacta a la Forjadora)"
            )
            return

        # --- Narrativa de la Forjadora ---
        try:
            from utils.narrator import scene, dialogue, narrate, achievement
        except Exception:
            scene = dialogue = narrate = achievement = None

        if scene:
            scene(
                caller,
                "RITUAL DE GRADUACIÓN",
                "La Forjadora aparece en el claude_dojo. Sus manos "
                "tejen hilos de bytecode alrededor de tu wallet. "
                "Algo permanente está a punto de suceder.",
            )
        if dialogue:
            dialogue(
                caller,
                "La Forjadora",
                "Has recorrido los diez rooms, recuperado los diez fragmentos "
                "y completado las quests del shell. Estás listx.",
            )
        if narrate:
            narrate(caller, "Preparando certificado onchain...")

        # --- SIMULACIÓN DEL MINT ---
        # (borrar este bloque cuando tengamos contrato real deployado)
        tx_fake, token_id = _simulate_mint(caller, wallet)
        ts = int(time.time())
        caller.db.minted_cert = {
            "tx": tx_fake,
            "tokenId": token_id,
            "wallet": wallet,
            "ts": ts,
            "simulated": True,
        }

        if achievement:
            achievement(
                caller,
                "GRADUATE NFT",
                (
                    f"Certificado emitido:\n"
                    f"Token ID: #{token_id}\n"
                    f"Wallet:   {_shorten(wallet)}\n"
                    f"TX:       {tx_fake}\n"
                    "(mint simulado — se va a re-emitir real cuando el contrato esté deployado)"
                ),
            )
        else:
            caller.msg(
                "\n|g★ GRADUATE NFT emitido|n\n"
                f"  tokenId: |c#{token_id}|n\n"
                f"  wallet:  |c{_shorten(wallet)}|n\n"
                f"  tx:      |w{tx_fake}|n\n"
                "  |x(mint simulado — pendiente contrato real)|n\n"
            )

        # --- REAL MINT — DESCOMENTAR CUANDO EL CONTRATO ESTÉ DEPLOYADO ---
        # from utils.monad import mint_graduate_nft
        # receipt = mint_graduate_nft(
        #     wallet=wallet,
        #     tokenId=None,                           # el contrato asigna secuencial
        #     attributes={
        #         "quests":           len(done),
        #         "memories":         len(caller.db.memories or []),
        #         "graduation_date":  ts,
        #     },
        # )
        # caller.db.minted_cert = {
        #     "tx":      receipt["tx_hash"],
        #     "tokenId": receipt["token_id"],
        #     "wallet":  wallet,
        #     "ts":      ts,
        #     "simulated": False,
        # }
        # Ver spec completa en la docstring del módulo.


# ---------- helpers ----------
def _simulate_mint(caller, wallet: str) -> tuple[str, int]:
    """Genera un tx hash y tokenId deterministas a partir del jugador + timestamp."""
    import hashlib
    seed = f"{caller.key}:{wallet}:{int(time.time())}".encode("utf-8")
    tx = "0x" + hashlib.sha256(seed).hexdigest()
    # TokenId incremental basado en un contador global persistido al servidor.
    # Esto es una simulación — el contrato real se encarga del incremento.
    try:
        from evennia.server.models import ServerConfig
        next_id = int(ServerConfig.objects.conf("ta_mint_counter", default=0) or 0) + 1
        ServerConfig.objects.conf("ta_mint_counter", next_id)
    except Exception:
        # Fallback si Server config no está disponible: usa ts
        next_id = int(time.time()) % 100000
    return tx, next_id


def _shorten(addr: str) -> str:
    if not addr:
        return ""
    if len(addr) > 12:
        return f"{addr[:6]}...{addr[-4:]}"
    return addr
