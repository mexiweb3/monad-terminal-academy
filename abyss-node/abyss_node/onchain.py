"""
onchain.py — helpers web3.py para Monad testnet.

Envía $ABYSS desde la game wallet (hot) al jugador cuando hace `claim`.
Config leída de /deploy/.env (fuera del repo).
"""

import os
import threading
from pathlib import Path

from dotenv import load_dotenv
from web3 import Web3


# Serializa las tx del claim para evitar nonce collision cuando varios
# jugadores hacen `claim` al mismo tiempo (hot wallet compartida).
_send_lock = threading.Lock()
_nonce_cache = {"addr": None, "next": None}


def _next_nonce(w3, addr: str) -> int:
    """Nonce incrementado en memoria; resetea al RPC al primer uso o tras fallo."""
    if _nonce_cache["addr"] != addr or _nonce_cache["next"] is None:
        _nonce_cache["addr"] = addr
        _nonce_cache["next"] = w3.eth.get_transaction_count(addr, "pending")
    n = _nonce_cache["next"]
    _nonce_cache["next"] = n + 1
    return n


def _reset_nonce_cache():
    _nonce_cache["next"] = None


# Carga /deploy/.env relativo al repo (monadmty/)
_HERE = Path(__file__).resolve()
# estructura: monadmty/abyss-node/abyss_node/onchain.py → subir 3 a monadmty/
_WORKSPACE = _HERE.parents[2]
_ENV_PATH = _WORKSPACE / "deploy" / ".env"
load_dotenv(_ENV_PATH)

RPC_URL = os.environ.get("MONAD_RPC_URL", "https://testnet-rpc.monad.xyz")
CHAIN_ID = int(os.environ.get("MONAD_CHAIN_ID", "10143"))
EXPLORER = os.environ.get("MONAD_EXPLORER", "https://testnet.monadexplorer.com")
PRIVATE_KEY = os.environ.get("PRIVATE_KEY", "")
CONTRACT_ADDR = os.environ.get("ABYSS_CONTRACT", "")


# ABI mínimo para transfer ERC-20
ERC20_ABI = [
    {
        "constant": False,
        "inputs": [{"name": "to", "type": "address"}, {"name": "value", "type": "uint256"}],
        "name": "transfer",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [{"name": "who", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "type": "function",
    },
]


def _web3():
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    return w3


def get_claim_stats(lookback_blocks: int = 20000) -> dict:
    """
    Lee eventos Transfer del contrato donde from == game wallet y agrega métricas.
    Retorna dict con total_claims, unique_players, total_distributed, top, last_tx.
    """
    if not CONTRACT_ADDR:
        raise RuntimeError("ABYSS_CONTRACT no configurado en /deploy/.env")
    w3 = _web3()
    contract_cs = Web3.to_checksum_address(CONTRACT_ADDR)
    game_addr = os.environ.get("GAME_WALLET_ADDRESS", "")
    if not game_addr:
        raise RuntimeError("GAME_WALLET_ADDRESS no configurado")
    game_cs = Web3.to_checksum_address(game_addr)

    current = w3.eth.block_number
    from_block = max(0, current - lookback_blocks)

    transfer_sig = Web3.keccak(text="Transfer(address,address,uint256)").hex()
    if not transfer_sig.startswith("0x"):
        transfer_sig = "0x" + transfer_sig
    from_topic = "0x" + game_cs[2:].lower().rjust(64, "0")

    # Monad testnet RPC limita `eth_getLogs` tanto en rango como en tamaño.
    # Iteramos en chunks pequeños y concatenamos.
    logs = []
    CHUNK = 400
    ptr = from_block
    while ptr <= current:
        to = min(ptr + CHUNK, current)
        try:
            batch = w3.eth.get_logs({
                "fromBlock": ptr,
                "toBlock": to,
                "address": contract_cs,
                "topics": [transfer_sig, from_topic],
            })
            logs.extend(batch)
        except Exception:
            # skip chunks que el RPC rechace y seguir
            pass
        ptr = to + 1

    total_sent = 0
    recipients: dict[str, int] = {}
    last_tx: str | None = None
    for log in logs:
        topic_to = log["topics"][2]
        to_hex = topic_to.hex() if hasattr(topic_to, "hex") else str(topic_to)
        if to_hex.startswith("0x"):
            to_hex = to_hex[2:]
        to_addr = Web3.to_checksum_address("0x" + to_hex[-40:])

        data = log["data"]
        if isinstance(data, (bytes, bytearray)):
            value = int.from_bytes(bytes(data), "big")
        else:
            ds = str(data)
            if ds.startswith("0x"):
                ds = ds[2:]
            value = int(ds, 16) if ds else 0

        total_sent += value
        recipients[to_addr] = recipients.get(to_addr, 0) + value

        tx_raw = log["transactionHash"]
        last_tx = tx_raw.hex() if hasattr(tx_raw, "hex") else str(tx_raw)
        if last_tx and not last_tx.startswith("0x"):
            last_tx = "0x" + last_tx

    top = sorted(recipients.items(), key=lambda x: x[1], reverse=True)[:5]
    return {
        "total_claims": len(logs),
        "unique_players": len(recipients),
        "total_distributed": total_sent / (10 ** 18),
        "top": [(addr, amt / (10 ** 18)) for addr, amt in top],
        "last_tx": last_tx,
        "contract": CONTRACT_ADDR,
        "explorer": EXPLORER,
    }


def send_abyss(to_address: str, amount_whole: int) -> tuple[str, str]:
    """
    Transfiere `amount_whole` tokens (unidades enteras, ya escaladas 1e18) a `to_address`.
    Retorna (tx_hash_hex, explorer_url).
    """
    if not CONTRACT_ADDR:
        raise RuntimeError("ABYSS_CONTRACT no configurado en /deploy/.env")
    if not PRIVATE_KEY:
        raise RuntimeError("PRIVATE_KEY no configurado en /deploy/.env")

    w3 = _web3()
    acct = w3.eth.account.from_key(PRIVATE_KEY)
    contract = w3.eth.contract(address=Web3.to_checksum_address(CONTRACT_ADDR), abi=ERC20_ABI)

    to_cs = Web3.to_checksum_address(to_address)
    value = int(amount_whole) * (10 ** 18)

    # Serializa la construcción+envío para que nonces y gas_price no colisionen
    with _send_lock:
        try:
            nonce = _next_nonce(w3, acct.address)
            tx = contract.functions.transfer(to_cs, value).build_transaction({
                "from": acct.address,
                "nonce": nonce,
                "chainId": CHAIN_ID,
                "gas": 120_000,
                "gasPrice": w3.eth.gas_price,
            })
            signed = acct.sign_transaction(tx)
            raw = getattr(signed, "rawTransaction", None) or getattr(signed, "raw_transaction", None)
            tx_hash = w3.eth.send_raw_transaction(raw)
        except Exception:
            # Fallback: reset cache para re-sync desde RPC en el siguiente claim
            _reset_nonce_cache()
            raise

    tx_hex = tx_hash.hex() if hasattr(tx_hash, "hex") else str(tx_hash)
    if not tx_hex.startswith("0x"):
        tx_hex = "0x" + tx_hex
    return tx_hex, f"{EXPLORER}/tx/{tx_hex}"
