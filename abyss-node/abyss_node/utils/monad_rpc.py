"""
Monad testnet JSON-RPC wrapper.

Minimal client sobre ``urllib.request`` (stdlib, sin dependencias) para
verificar transacciones que el alumno ejecutó en su terminal real
(Claude Code / OpenClaw / Hermes → Monad testnet) y volver al MUD a
pegar el tx hash para que el MUD lo valide.

Uso desde comandos del MUD::

    from utils.monad_rpc import verify_deploy

    result = verify_deploy("0xabc...123")
    if result["valid"]:
        contract = result["contract"]
        deployer = result["from"]
        ...

Este módulo **no** firma tx ni envía transacciones; sólo lee estado
onchain. Toda la firma la hace el alumno con su wallet en su máquina.

El RPC público por default es ``https://testnet-rpc.monad.xyz``
(chainId ``10143``). Si Monad rota el endpoint, basta con cambiar
``RPC_URL`` — no hay estado persistido en el módulo.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from typing import Any


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

RPC_URL = "https://testnet-rpc.monad.xyz"
CHAIN_ID = 10143

# timeout por request (segundos) — el alumno está en un comando
# interactivo, no queremos bloquear más que esto
_DEFAULT_TIMEOUT = 8

# reintentos con backoff exponencial (0.5s, 1s) antes de dar error
_RETRY_COUNT = 2
_RETRY_BACKOFF = 0.5


# ---------------------------------------------------------------------------
# Low-level JSON-RPC
# ---------------------------------------------------------------------------


def _rpc_call(method: str, params: list[Any], timeout: int = _DEFAULT_TIMEOUT) -> dict:
    """Manda un request JSON-RPC 2.0 al RPC de Monad testnet.

    Reintenta hasta ``_RETRY_COUNT`` veces con backoff ante errores de
    red/5xx. Retorna el body parseado (dict con "result" o "error").

    Raises:
        RuntimeError: si todos los intentos fallan con un error
            identificable (red, timeout, body no-JSON).
    """
    payload = json.dumps({
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": 1,
    }).encode("utf-8")

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "terminal-academy-mud/1.0 (+blitz.mexi.wtf)",
    }

    last_err: Exception | None = None
    attempts = _RETRY_COUNT + 1
    for attempt in range(attempts):
        try:
            req = urllib.request.Request(RPC_URL, data=payload, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read()
                try:
                    return json.loads(raw.decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError) as e:
                    raise RuntimeError(f"RPC devolvió body no-JSON: {e}") from e
        except urllib.error.HTTPError as e:
            # 4xx casi siempre es fatal (el RPC rechaza el body) — no retry
            if 400 <= e.code < 500:
                raise RuntimeError(f"RPC HTTP {e.code}: {e.reason}") from e
            last_err = e
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            last_err = e

        # backoff antes del próximo retry (solo si no fue el último intento)
        if attempt < attempts - 1:
            time.sleep(_RETRY_BACKOFF * (2 ** attempt))

    raise RuntimeError(f"RPC {method} falló tras {attempts} intentos: {last_err!r}")


def _is_tx_hash(value: str | None) -> bool:
    """Sanity check barato — 0x + 64 hex chars."""
    if not isinstance(value, str):
        return False
    v = value.lower().strip()
    if not v.startswith("0x"):
        return False
    hex_part = v[2:]
    if len(hex_part) != 64:
        return False
    try:
        int(hex_part, 16)
    except ValueError:
        return False
    return True


def _normalize_tx_hash(value: str) -> str:
    """Trim + lowercase — el RPC es case-insensitive pero conviene ser consistente."""
    return (value or "").strip().lower()


# ---------------------------------------------------------------------------
# High-level helpers
# ---------------------------------------------------------------------------


def get_transaction_receipt(tx_hash: str, timeout: int = _DEFAULT_TIMEOUT) -> dict | None:
    """Retorna el receipt de una tx, o ``None`` si aún no fue minada / no existe.

    El receipt incluye ``status`` (``"0x1"`` / ``"0x0"``),
    ``contractAddress`` (para deploys), ``from``, ``to`` y ``blockNumber``.
    """
    tx = _normalize_tx_hash(tx_hash)
    if not _is_tx_hash(tx):
        return None
    resp = _rpc_call("eth_getTransactionReceipt", [tx], timeout=timeout)
    return resp.get("result") or None


def get_transaction(tx_hash: str, timeout: int = _DEFAULT_TIMEOUT) -> dict | None:
    """Retorna la tx cruda del mempool/chain, o ``None`` si no existe.

    Útil para leer ``to``/``input``/``value``/``nonce`` — datos que un
    receipt no incluye.
    """
    tx = _normalize_tx_hash(tx_hash)
    if not _is_tx_hash(tx):
        return None
    resp = _rpc_call("eth_getTransactionByHash", [tx], timeout=timeout)
    return resp.get("result") or None


def _hex_to_int(value: Any) -> int | None:
    """Convierte un int hex (``"0x10143"``) a int decimal. Tolera None/basura."""
    if not isinstance(value, str):
        return None
    try:
        return int(value, 16)
    except (TypeError, ValueError):
        return None


def verify_deploy(tx_hash: str, timeout: int = _DEFAULT_TIMEOUT) -> dict:
    """Valida que ``tx_hash`` es un contract deploy exitoso en Monad testnet.

    Returns:
        dict con el shape::

            {
              "valid":    bool,                # True si es deploy OK
              "contract": str | None,          # address del contrato (0x...)
              "from":     str | None,          # deployer address
              "error":    str | None,          # mensaje user-facing si !valid
              "block":    int | None,          # block number (decimal)
            }

    Un deploy válido cumple:
        * la tx existe y fue minada (hay receipt + getTransactionByHash)
        * receipt.status == ``"0x1"``
        * la tx.to es null (deploy, no call)
        * receipt.contractAddress está presente
    """
    result: dict = {
        "valid": False,
        "contract": None,
        "from": None,
        "error": None,
        "block": None,
    }

    tx = _normalize_tx_hash(tx_hash)
    if not _is_tx_hash(tx):
        result["error"] = "tx hash inválido (esperaba 0x + 64 hex chars)"
        return result

    try:
        raw_tx = get_transaction(tx, timeout=timeout)
        receipt = get_transaction_receipt(tx, timeout=timeout)
    except RuntimeError as e:
        result["error"] = f"no pude conectar al RPC de Monad: {e}"
        return result

    if raw_tx is None or receipt is None:
        result["error"] = "tx no encontrada en Monad testnet (¿hash correcto? ¿ya fue minada?)"
        return result

    # status del receipt: "0x1" éxito, "0x0" reverted
    status = receipt.get("status")
    if status != "0x1":
        result["error"] = "tx falló on-chain (status=0x0 / reverted) — revisa el deploy"
        return result

    # "to" == null identifica un contract-creation tx
    raw_to = raw_tx.get("to")
    if raw_to not in (None, "0x", "0x0"):
        result["error"] = (
            f"esta tx es una llamada normal, no un deploy (to={raw_to}). "
            "Pegá el hash del tx que CREA el contrato, no el que lo llama."
        )
        return result

    contract_addr = receipt.get("contractAddress")
    if not contract_addr:
        result["error"] = "deploy detectado pero sin contractAddress — RPC raro, probá de nuevo"
        return result

    result["valid"] = True
    result["contract"] = contract_addr
    result["from"] = receipt.get("from") or raw_tx.get("from")
    result["block"] = _hex_to_int(receipt.get("blockNumber"))
    return result
