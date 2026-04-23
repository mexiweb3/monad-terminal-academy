"""
Tests para `utils.monad_rpc`.

Mockeamos ``urllib.request.urlopen`` para ejercitar el RPC wrapper sin
tocar la red. Cubrimos los 4 branches que importan para el flujo de
``verify claude <tx>``:

    1. happy path — deploy válido, status 0x1, to=null, contractAddress
    2. tx es una llamada normal (to != null) → inválido
    3. tx fue reverted (status 0x0) → inválido
    4. tx no existe (RPC devuelve result=None) → inválido

Ejecutar (stdlib unittest):

    cd abyss-node/abyss_node
    python -m unittest tests.test_monad_rpc -v

Con pytest (si está disponible):

    cd abyss-node/abyss_node
    pytest tests/test_monad_rpc.py -v
"""

from __future__ import annotations

import io
import json
import os
import sys
import unittest
from typing import Any
from unittest.mock import patch


# Garantiza que `abyss_node/` esté en PYTHONPATH aunque los tests se corran
# desde otro directorio (p. ej. desde la raíz del repo o el worktree).
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from utils import monad_rpc  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers — mock de urlopen que escupe respuestas por-llamada
# ---------------------------------------------------------------------------


class _FakeResp:
    """Context-manager compatible con ``with urlopen(...) as r:``."""

    def __init__(self, body: dict):
        self._body = json.dumps(body).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def read(self) -> bytes:
        return self._body


def _make_urlopen(queue: list[dict]):
    """Factory que devuelve un fake_urlopen consumiendo de ``queue``.

    Cada llamada al mock consume un item. Permite secuenciar respuestas
    para tests multi-call (getTransactionByHash + getTransactionReceipt).
    """

    def fake(_req, timeout=None):  # noqa: ARG001
        if not queue:
            raise AssertionError("urlopen llamado más veces de las esperadas")
        body = queue.pop(0)
        return _FakeResp(body)

    return fake


# Tx hash canónico que usamos en todos los tests (66 chars, válido)
_TX_OK = "0x" + "a" * 64

# Receipt plantilla para un deploy exitoso
_RECEIPT_OK: dict[str, Any] = {
    "status": "0x1",
    "contractAddress": "0xAA61f22199f2436259Ce4c85fc15F4C87Ce77207",
    "from": "0xCaFeCaFeCaFeCaFeCaFeCaFeCaFeCaFeCaFeCaFe",
    "to": None,
    "blockNumber": "0x1a2b3c",
    "transactionHash": _TX_OK,
}

# Tx raw plantilla (deploy: "to" es null)
_RAW_TX_DEPLOY: dict[str, Any] = {
    "hash": _TX_OK,
    "from": "0xCaFeCaFeCaFeCaFeCaFeCaFeCaFeCaFeCaFeCaFe",
    "to": None,
    "input": "0x6080604052...",  # bytecode deploy
    "value": "0x0",
    "nonce": "0x5",
}


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


class VerifyDeployHappyPath(unittest.TestCase):
    """Deploy válido → verify_deploy devuelve valid=True con contract+from."""

    def test_valid_deploy_returns_contract_and_deployer(self):
        # monad_rpc llama PRIMERO getTransactionByHash, DESPUÉS getReceipt.
        # Verificamos que el resultado sea coherente.
        queue = [
            {"jsonrpc": "2.0", "id": 1, "result": _RAW_TX_DEPLOY},
            {"jsonrpc": "2.0", "id": 1, "result": _RECEIPT_OK},
        ]
        with patch.object(monad_rpc.urllib.request, "urlopen", _make_urlopen(queue)):
            result = monad_rpc.verify_deploy(_TX_OK)

        self.assertTrue(result["valid"])
        self.assertEqual(result["contract"], _RECEIPT_OK["contractAddress"])
        self.assertEqual(result["from"], _RECEIPT_OK["from"])
        self.assertEqual(result["block"], int("1a2b3c", 16))
        self.assertIsNone(result["error"])

    def test_valid_deploy_with_to_literal_0x(self):
        """Algunos nodes devuelven ``"to": "0x"`` en vez de null — debe valer."""
        raw = dict(_RAW_TX_DEPLOY)
        raw["to"] = "0x"  # variante conocida de "null"
        queue = [
            {"jsonrpc": "2.0", "id": 1, "result": raw},
            {"jsonrpc": "2.0", "id": 1, "result": _RECEIPT_OK},
        ]
        with patch.object(monad_rpc.urllib.request, "urlopen", _make_urlopen(queue)):
            result = monad_rpc.verify_deploy(_TX_OK)
        self.assertTrue(result["valid"])


# ---------------------------------------------------------------------------
# Error: tx no es deploy (tx.to existe)
# ---------------------------------------------------------------------------


class VerifyDeployNotADeploy(unittest.TestCase):
    """Si tx.to != null, la tx es un call normal, no un deploy."""

    def test_to_populated_returns_invalid(self):
        raw = dict(_RAW_TX_DEPLOY)
        raw["to"] = "0xDeaDBeeFdeadbeefDEADbeefDEADbEEFdeadBEEF"  # call a contrato
        queue = [
            {"jsonrpc": "2.0", "id": 1, "result": raw},
            {"jsonrpc": "2.0", "id": 1, "result": _RECEIPT_OK},
        ]
        with patch.object(monad_rpc.urllib.request, "urlopen", _make_urlopen(queue)):
            result = monad_rpc.verify_deploy(_TX_OK)

        self.assertFalse(result["valid"])
        self.assertIn("deploy", (result["error"] or "").lower())
        # El contract del receipt no se expone cuando la tx no es deploy
        self.assertIsNone(result["contract"])


# ---------------------------------------------------------------------------
# Error: tx failed (status 0x0)
# ---------------------------------------------------------------------------


class VerifyDeployTxFailed(unittest.TestCase):
    """receipt.status = 0x0 → la tx fue reverted."""

    def test_status_0x0_returns_invalid(self):
        receipt = dict(_RECEIPT_OK)
        receipt["status"] = "0x0"
        queue = [
            {"jsonrpc": "2.0", "id": 1, "result": _RAW_TX_DEPLOY},
            {"jsonrpc": "2.0", "id": 1, "result": receipt},
        ]
        with patch.object(monad_rpc.urllib.request, "urlopen", _make_urlopen(queue)):
            result = monad_rpc.verify_deploy(_TX_OK)

        self.assertFalse(result["valid"])
        self.assertIn("revert", (result["error"] or "").lower())


# ---------------------------------------------------------------------------
# Error: tx not found (result=None)
# ---------------------------------------------------------------------------


class VerifyDeployTxNotFound(unittest.TestCase):
    """RPC devuelve result=None cuando el hash no existe en la chain."""

    def test_both_null_returns_invalid(self):
        queue = [
            {"jsonrpc": "2.0", "id": 1, "result": None},
            {"jsonrpc": "2.0", "id": 1, "result": None},
        ]
        with patch.object(monad_rpc.urllib.request, "urlopen", _make_urlopen(queue)):
            result = monad_rpc.verify_deploy(_TX_OK)

        self.assertFalse(result["valid"])
        self.assertIn("no encontrada", (result["error"] or "").lower())

    def test_only_tx_found_but_no_receipt_returns_invalid(self):
        """Tx en mempool pero no minada todavía — devolvemos inválido."""
        queue = [
            {"jsonrpc": "2.0", "id": 1, "result": _RAW_TX_DEPLOY},
            {"jsonrpc": "2.0", "id": 1, "result": None},
        ]
        with patch.object(monad_rpc.urllib.request, "urlopen", _make_urlopen(queue)):
            result = monad_rpc.verify_deploy(_TX_OK)

        self.assertFalse(result["valid"])
        self.assertIsNotNone(result["error"])


# ---------------------------------------------------------------------------
# Error: tx hash mal formado (no llega al RPC)
# ---------------------------------------------------------------------------


class VerifyDeployInvalidHash(unittest.TestCase):
    """Hashes mal formados fallan en validación local, sin hit al RPC."""

    def test_short_hash_no_rpc_call(self):
        # Si el hash es inválido, urlopen no debería llamarse ni una vez.
        def fake_urlopen(_req, timeout=None):  # noqa: ARG001
            raise AssertionError("urlopen no debería llamarse")

        with patch.object(monad_rpc.urllib.request, "urlopen", fake_urlopen):
            result = monad_rpc.verify_deploy("0xabc")
        self.assertFalse(result["valid"])
        self.assertIn("inválido", (result["error"] or "").lower())

    def test_no_0x_prefix(self):
        result = monad_rpc.verify_deploy("a" * 66)
        self.assertFalse(result["valid"])
        self.assertIn("inválido", (result["error"] or "").lower())

    def test_empty_string(self):
        result = monad_rpc.verify_deploy("")
        self.assertFalse(result["valid"])

    def test_none_value(self):
        # type: ignore[arg-type] — defensivo
        result = monad_rpc.verify_deploy(None)  # type: ignore[arg-type]
        self.assertFalse(result["valid"])


# ---------------------------------------------------------------------------
# Sanity: _is_tx_hash
# ---------------------------------------------------------------------------


class IsTxHashTests(unittest.TestCase):
    def test_valid_tx_hash(self):
        self.assertTrue(monad_rpc._is_tx_hash("0x" + "a" * 64))
        self.assertTrue(monad_rpc._is_tx_hash("0x" + "0" * 64))
        # case-insensitive
        self.assertTrue(monad_rpc._is_tx_hash("0x" + "A" * 64))

    def test_invalid_length(self):
        self.assertFalse(monad_rpc._is_tx_hash("0x" + "a" * 63))
        self.assertFalse(monad_rpc._is_tx_hash("0x" + "a" * 65))

    def test_non_hex(self):
        self.assertFalse(monad_rpc._is_tx_hash("0x" + "z" * 64))

    def test_no_prefix(self):
        self.assertFalse(monad_rpc._is_tx_hash("a" * 66))

    def test_non_string(self):
        self.assertFalse(monad_rpc._is_tx_hash(None))  # type: ignore[arg-type]
        self.assertFalse(monad_rpc._is_tx_hash(12345))  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Hex conversion
# ---------------------------------------------------------------------------


class HexToIntTests(unittest.TestCase):
    def test_valid_hex(self):
        self.assertEqual(monad_rpc._hex_to_int("0x10143"), 65859)
        self.assertEqual(monad_rpc._hex_to_int("0x0"), 0)

    def test_invalid_returns_none(self):
        self.assertIsNone(monad_rpc._hex_to_int(None))
        self.assertIsNone(monad_rpc._hex_to_int("not-hex"))
        self.assertIsNone(monad_rpc._hex_to_int(123))  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Config invariants
# ---------------------------------------------------------------------------


class ConfigInvariants(unittest.TestCase):
    """Chequeos básicos — si alguien cambia la URL/chainId por error, lo pescamos."""

    def test_rpc_url_is_monad_testnet(self):
        self.assertIn("monad", monad_rpc.RPC_URL.lower())
        self.assertTrue(monad_rpc.RPC_URL.startswith("https://"))

    def test_chain_id_is_10143(self):
        self.assertEqual(monad_rpc.CHAIN_ID, 10143)


if __name__ == "__main__":
    unittest.main()
