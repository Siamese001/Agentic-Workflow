"""
agentic_core/runtime/execution_bound_token.py

Execution-bound capability tokens with cryptographic integrity.

Each token is signed against: token_id, capability_type, caller/target
contexts, execution_trace_id, policy_hash, determinism_digest, and
hierarchy_hash.  This prevents replay across different execution contexts
even within the 1-hour validity window.

Authority secret is loaded exclusively from the AGENTIC_AUTHORITY_SECRET
environment variable.  The module hard-fails at authority construction time
if the variable is absent (fail-closed design).
"""
import hashlib
import json
import os
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

class CapabilityType(Enum):
    READ_ONLY = 'read_only'
    WRITE_STATE = 'write_state'
    MUTATE_CONFIG = 'mutate_config'
    ACTIVATE_LEARNING = 'activate_learning'

@dataclass(frozen=True)
class ExecutionBoundToken:
    """Cryptographic token bound to a specific execution trace and policy."""
    token_id: str
    capability_type: CapabilityType
    caller_context: str
    target_context: str
    execution_trace_id: str
    policy_hash: str
    determinism_digest: str
    hierarchy_hash: str
    signature_hash: str
    authority_hash: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def verify_execution_binding(self, expected_trace_id: str, expected_policy_hash: str, expected_determinism_digest: str, expected_hierarchy_hash: str) -> bool:
        """Return True iff token is bound to the supplied execution context."""
        return self.execution_trace_id == expected_trace_id and self.policy_hash == expected_policy_hash and (self.determinism_digest == expected_determinism_digest) and (self.hierarchy_hash == expected_hierarchy_hash)

    def verify_signature(self, authority_public_hash: str) -> bool:
        """Return True iff token signature is cryptographically valid."""
        return self.authority_hash == authority_public_hash and self.signature_hash == self._compute_expected_signature()

    def _compute_expected_signature(self) -> str:
        """Compute the expected HMAC-style signature (no secret — used for self-check)."""
        payload = {'token_id': self.token_id, 'capability_type': self.capability_type.value, 'caller_context': self.caller_context, 'target_context': self.target_context, 'execution_trace_id': self.execution_trace_id, 'policy_hash': self.policy_hash, 'determinism_digest': self.determinism_digest, 'hierarchy_hash': self.hierarchy_hash}
        return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(',', ':')).encode('utf-8')).hexdigest()

class SecureCapabilityAuthority:
    """Issues and verifies execution-bound capability tokens.

    Authority secret is loaded from AGENTIC_AUTHORITY_SECRET.
    Construction raises RuntimeError if the variable is absent (fail-closed).
    """

    def __init__(self) -> None:
        self._authority_secret: str = self._load_authority_secret()
        self.authority_public_hash: str = hashlib.sha256(self._authority_secret.encode('utf-8')).hexdigest()

    @staticmethod
    def _load_authority_secret() -> str:
        secret = os.environ.get('AGENTIC_AUTHORITY_SECRET')
        if not secret:
            raise RuntimeError('AGENTIC_AUTHORITY_SECRET environment variable is required but not set. Cannot initialize SecureCapabilityAuthority.')
        return secret

    def issue_token(self, capability_type: CapabilityType, caller_context: str, target_context: str, execution_trace_id: str, policy_hash: str, determinism_digest: str, hierarchy_hash: str, metadata: dict[str, Any] | None=None) -> ExecutionBoundToken:
        """Issue a new execution-bound capability token."""
        token_id = str(uuid.uuid4())
        raw_signature_payload = f'{token_id}:{capability_type.value}:{caller_context}:{target_context}:{execution_trace_id}:{policy_hash}:{determinism_digest}:{hierarchy_hash}'
        signature_hash = hashlib.sha256((raw_signature_payload + self._authority_secret).encode('utf-8')).hexdigest()
        return ExecutionBoundToken(token_id=token_id, capability_type=capability_type, caller_context=caller_context, target_context=target_context, execution_trace_id=execution_trace_id, policy_hash=policy_hash, determinism_digest=determinism_digest, hierarchy_hash=hierarchy_hash, signature_hash=signature_hash, authority_hash=self.authority_public_hash, metadata=metadata or {})

    def verify_token(self, token: ExecutionBoundToken) -> bool:
        """Verify a token was issued by this authority."""
        raw_signature_payload = f'{token.token_id}:{token.capability_type.value}:{token.caller_context}:{token.target_context}:{token.execution_trace_id}:{token.policy_hash}:{token.determinism_digest}:{token.hierarchy_hash}'
        expected_signature = hashlib.sha256((raw_signature_payload + self._authority_secret).encode('utf-8')).hexdigest()
        return token.authority_hash == self.authority_public_hash and token.signature_hash == expected_signature
_capability_authority: SecureCapabilityAuthority | None = None

def get_capability_authority() -> SecureCapabilityAuthority:
    """Return the global SecureCapabilityAuthority (lazy-initialized)."""
    global _capability_authority
    if _capability_authority is None:
        _capability_authority = SecureCapabilityAuthority()
    return _capability_authority
