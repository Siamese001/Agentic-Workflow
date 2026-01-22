from __future__ import annotations

"""
[PHASE 23] AuditTrailMixin - Cryptographic Chain-of-Custody for Agent Actions.

Provides tamper-evident audit logging using SHA-256 hash chaining.
Optimized for performance: hashes locally, emits asynchronously.

Key Design Decisions:
1. Does NOT write to Redis directly - injects audit_proof into EventEmission payload
2. Synchronous hash generation (fast enough for main thread)
3. Async event emission via EventEmissionMixin dependency
4. Session salt for chain isolation between agent instances

Hash Chain Structure:
    Current Hash = SHA256(Previous_Hash | Session_Salt | Action_Type | Payload | Timestamp)

Usage:
    class MyAgent(AuditTrailMixin, EventEmissionMixin, SovereignBaseAgent):
        async def execute_action(self, action):
            await self.emit_auditable_action("EXECUTE", {"action_id": action.id})
            result = await self._do_execute(action)
            return result

[SSOT] Audit trail implementation for L6 observability.
"""


import hashlib
import logging
import secrets
import time
from dataclasses import dataclass
from typing import Any

Logger = logging.getLogger(__name__)


@dataclass
class AuditProof:
    """
    Cryptographic proof of an audited action.

    Attributes:
        action_id: Unique identifier for this action
        prev_hash: Hash of the previous action in the chain
        curr_hash: Hash of this action (includes prev_hash for chaining)
        timestamp: Unix timestamp when proof was generated
        chain_id: Session salt identifying this chain
    """

    action_id: str
    prev_hash: str
    curr_hash: str
    timestamp: float
    chain_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "action_id": self.action_id,
            "prev_hash": self.prev_hash,
            "curr_hash": self.curr_hash,
            "timestamp": self.timestamp,
            "chain_id": self.chain_id,
        }

    def verify_chain_link(self, expected_prev_hash: str) -> bool:
        """Verify this proof links to the expected previous hash."""
        return self.prev_hash == expected_prev_hash


@dataclass
class AuditChainStats:
    """Statistics for an audit chain."""

    chain_id: str
    genesis_time: float
    last_action_time: float
    total_actions: int
    last_hash: str


class AuditTrailMixin:
    """
    [PHASE 23] Provides cryptographic chain-of-custody for agent actions.

    Must be mixed in with EventEmissionMixin for async event dispatch.

    Hash Chain:
        Each action's hash includes the previous hash, creating an
        immutable chain. Any tampering breaks the chain verification.

    Session Isolation:
        Each agent instance gets a unique session salt, isolating
        its chain from other instances.

    Performance:
        Hash generation is synchronous and fast (~0.1ms per action).
        Event emission is async and non-blocking.

    Attributes:
        _audit_last_hash: Hash of the last action in the chain
        _audit_session_salt: Random salt for this session
        _audit_genesis_time: When this chain was created
        _audit_action_count: Total actions in this chain
    """

    # Genesis block hash (all zeros)
    GENESIS_HASH = "0" * 64

    # Class-level defaults (overridden per-instance in __init__)
    _audit_last_hash: str = GENESIS_HASH
    _audit_session_salt: str = ""
    _audit_genesis_time: float = 0.0
    _audit_action_count: int = 0

    def __init__(self, *args, **kwargs):
        """Initialize audit chain with unique session salt."""
        super().__init__(*args, **kwargs)

        # Generate unique session salt (16 bytes = 32 hex chars)
        self._audit_session_salt = secrets.token_hex(16)
        self._audit_last_hash = self.GENESIS_HASH
        self._audit_genesis_time = time.time()
        self._audit_action_count = 0

        Logger.debug(
            f"[{self.__class__.__name__}] Audit chain initialized: "
            f"chain_id={self._audit_session_salt[:8]}..."
        )

    def _canonicalize_payload(self, payload: dict[str, Any]) -> str:
        """
        Canonicalize payload for consistent hashing.

        Sorts keys recursively to ensure deterministic serialization.
        """

        def _sort_recursive(obj: Any) -> Any:
            if isinstance(obj, dict):
                return sorted((k, _sort_recursive(v)) for k, v in obj.items())
            elif isinstance(obj, (list, tuple)):
                return [_sort_recursive(item) for item in obj]
            return obj

        return str(_sort_recursive(payload))

    def _generate_audit_proof(
        self,
        action_type: str,
        payload: dict[str, Any],
    ) -> AuditProof:
        """
        Synchronous cryptographic proof generation.

        Fast enough to run in main thread (~0.1ms).

        Args:
            action_type: Type of action being audited
            payload: Action payload data

        Returns:
            AuditProof with hash chain link
        """
        timestamp = time.time()

        # Canonicalize payload for consistent hashing
        payload_str = self._canonicalize_payload(payload)

        # Create chain link: prev_hash | salt | action | payload | timestamp
        raw_data = (
            f"{self._audit_last_hash}|"
            f"{self._audit_session_salt}|"
            f"{action_type}|"
            f"{payload_str}|"
            f"{timestamp}"
        )

        # SHA-256 hash
        curr_hash = hashlib.sha256(raw_data.encode()).hexdigest()

        # Create proof
        proof = AuditProof(
            action_id=f"act_{self._audit_action_count}_{int(timestamp * 1000)}",
            prev_hash=self._audit_last_hash,
            curr_hash=curr_hash,
            timestamp=timestamp,
            chain_id=self._audit_session_salt,
        )

        # Advance chain
        self._audit_last_hash = curr_hash
        self._audit_action_count += 1

        return proof

    async def emit_auditable_action(
        self,
        action_type: str,
        payload: dict[str, Any],
        severity: str = "INFO",
    ) -> AuditProof:
        """
        Generate proof and emit via EventEmissionMixin.

        Args:
            action_type: Type of action (e.g., "FILE_MOVE", "HEAL_VIOLATION")
            payload: Action data to audit
            severity: Event severity level

        Returns:
            AuditProof for caller verification

        Raises:
            NotImplementedError: If EventEmissionMixin is not present
        """
        # Generate proof synchronously (fast)
        proof = self._generate_audit_proof(action_type, payload)

        # Check for EventEmissionMixin dependency
        if not hasattr(self, "emit_event"):
            raise NotImplementedError(
                "AuditTrailMixin requires EventEmissionMixin. "
                "Ensure your class inherits from both mixins."
            )

        # Build event payload with audit proof
        event_payload = {
            "data": payload,
            "audit_proof": {
                "hash": proof.curr_hash,
                "prev": proof.prev_hash,
                "chain_id": proof.chain_id,
                "action_id": proof.action_id,
            },
        }

        # Emit via EventEmissionMixin (async, non-blocking)
        await self.emit_event(
            event_type=f"AUDIT_{action_type}",
            payload=event_payload,
            severity=severity,
        )

        Logger.debug(
            f"[{self.__class__.__name__}] Audited action: {action_type} "
            f"(hash={proof.curr_hash[:16]}...)"
        )

        return proof

    def emit_auditable_action_sync(
        self,
        action_type: str,
        payload: dict[str, Any],
    ) -> AuditProof:
        """
        Synchronous version for non-async contexts.

        Generates proof but does NOT emit event (no async dispatch).
        Use this when you need the proof but can't await.

        Args:
            action_type: Type of action
            payload: Action data

        Returns:
            AuditProof for caller verification
        """
        proof = self._generate_audit_proof(action_type, payload)

        Logger.debug(
            f"[{self.__class__.__name__}] Sync audit proof: {action_type} "
            f"(hash={proof.curr_hash[:16]}...)"
        )

        return proof

    def verify_chain_integrity(self, proofs: list[AuditProof]) -> tuple[bool, int | None]:
        """
        Verify a sequence of proofs forms a valid chain.

        Args:
            proofs: List of AuditProof objects in order

        Returns:
            Tuple of (is_valid, first_broken_index)
            If valid, returns (True, None)
            If broken, returns (False, index_of_first_break)
        """
        if not proofs:
            return (True, None)

        # First proof should link to genesis
        if proofs[0].prev_hash != self.GENESIS_HASH:
            # Check if it's a continuation from a known hash
            pass  # Allow non-genesis starts for partial chain verification

        # Verify each link
        for i in range(1, len(proofs)):
            if proofs[i].prev_hash != proofs[i - 1].curr_hash:
                return (False, i)

        return (True, None)

    def get_audit_chain_stats(self) -> AuditChainStats:
        """Get statistics for this audit chain."""
        return AuditChainStats(
            chain_id=self._audit_session_salt,
            genesis_time=self._audit_genesis_time,
            last_action_time=time.time(),
            total_actions=self._audit_action_count,
            last_hash=self._audit_last_hash,
        )

    def get_chain_head(self) -> str:
        """Get the current head of the hash chain."""
        return self._audit_last_hash
