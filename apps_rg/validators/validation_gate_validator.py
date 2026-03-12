"""
[SSOT] Cryptographic Validation Gate.
Implements the 'Gate Signature' pattern from v61.27.10.
Ensures no content flows downstream without cryptographic proof of validation.
"""
import hashlib
import hmac
import json
import os
from typing import Any
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

class ValidationGate:
    """
    Signs validation results to prevent bypass of safety checks.
    """

    def __init__(self, gate_id: str):
        self.gate_id = gate_id
        self._secret = os.getenv('RG_VALIDATION_SECRET', 'dev_secret_key').encode()

    def sign_payload(self, payload: dict[str, Any]) -> str:
        """
        Generates an HMAC-SHA256 signature for the given payload.
        """
        signing_data = {'gate_id': self.gate_id, 'payload': payload}
        serialized = json.dumps(signing_data, sort_keys=True).encode()
        signature = hmac.new(self._secret, serialized, hashlib.sha256).hexdigest()
        return signature

    def verify(self, payload: dict[str, Any], signature: str) -> bool:
        """
        Verifies that the payload has not been tampered with since signing.
        """
        expected = self.sign_payload(payload)
        return hmac.compare_digest(expected, signature)
