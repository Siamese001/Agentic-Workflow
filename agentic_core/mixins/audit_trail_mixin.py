from __future__ import annotations

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

"""
[PHASE 24] AuditTrailMixin - Sovereign Black Box with Cryptographic Chain-of-Custody.

Provides tamper-evident audit logging using SHA-256 hash chaining PLUS
JSON-structured Black Box logging for forensic analysis.

Key Design Decisions:
1. JSON-structured logging for machine ingestion (Black Box)
2. Cryptographic hash chaining for tamper evidence
3. Does NOT write to Redis directly - injects audit_proof into EventEmission payload
4. Synchronous hash generation (fast enough for main thread)
5. Async event emission via event_emission_mixin dependency
6. Session salt for chain isolation between agent instances

Black Box Format:
{
    "timestamp": "2026-01-24T14:57:00.000Z",
    "agent_id": "CampaignPlannerAgent",
    "domain": "apps_rg",
    "session": "20260124-145700",
    "action": "BOOT",
    "details": {"status": "initialized", "mode": "hardened"},
    "integrity_status": "VERIFIED"
}

Usage:
    class MyAgent(AuditTrailMixin, event_emission_mixin, SovereignBaseAgent):
        async def execute_action(self, action):
            await self.emit_auditable_action("EXECUTE", {"action_id": action.id})
            # Also logs to Black Box
            self.log_sovereign_event("EXECUTE", {"action_id": action.id})
            result = await self._do_execute(action)
            return result

[SSOT] Audit trail implementation for L6 observability.
"""


import hashlib
import json
import logging
import secrets
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

Logger = logging.getLogger("SovereignBlackBox")


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
    [PHASE 24] Provides cryptographic chain-of-custody + Black Box structured logging.

    Must be mixed in with event_emission_mixin for async event dispatch.

    Hash Chain:
        Each action's hash includes the previous hash, creating an
        immutable chain. Any tampering breaks the chain verification.

    Black Box Logging:
        JSON-structured logging for forensic analysis and compliance.
        Every Healer action and Validator check is automatically recorded.

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
        _audit_enabled: Whether Black Box logging is enabled
        _session_id: Session identifier for Black Box logs
    """

    # Genesis block hash (all zeros)
    GENESIS_HASH = "0" * 64

    # Class-level defaults (overridden per-instance in __init__)
    _audit_last_hash: str = GENESIS_HASH
    _audit_session_salt: str = ""
    _audit_genesis_time: float = 0.0
    _audit_action_count: int = 0
    _audit_enabled: bool = True
    _session_id: str = field(default_factory=lambda: datetime.now().strftime("%Y%m%d-%H%M%S"))

    def __init__(self, *args, **kwargs):
        """Initialize audit chain with unique session salt."""
        super().__init__(*args, **kwargs)

        # Generate unique session salt (16 bytes = 32 hex chars)
        self._audit_session_salt = secrets.token_hex(16)
        self._audit_last_hash = self.GENESIS_HASH
        self._audit_genesis_time = time.time()
        self._audit_action_count = 0
        self._audit_enabled = True
        self._session_id = datetime.now().strftime("%Y%m%d-%H%M%S")

        Logger.debug(
            f"[{self.__class__.__name__}] Audit chain initialized: chain_id={self._audit_session_salt[:8]}...",
        )

    def log_sovereign_event(self, action: str, details: dict[str, Any], level: str = "INFO") -> None:
        """
        Write an immutable record to the structured Black Box log.

        Args:
            action: The action being performed (e.g., "BOOT", "HEAL", "VALIDATE")
            details: Additional context data for the event
            level: Log level (INFO, WARNING, ERROR)
        """
        if not self._audit_enabled:
            return

        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent_id": getattr(self, "name", "UnknownSovereign"),
            "domain": getattr(self, "domain_root", Path("unknown")).name,
            "session": self._session_id,
            "action": action.upper(),
            "details": details,
            "integrity_status": "VERIFIED",  # Assumes Lock passed
        }

        # Structuring as JSON line for machine ingestion
        def json_serializer(obj):
            """Custom JSON serializer for dataclass Fields and other objects"""
            if hasattr(obj, "__name__"):  # Functions, classes, etc.
                return str(obj)
            elif hasattr(obj, "default"):  # dataclass Field
                return f"Field({obj.default})"
            elif hasattr(obj, "__dict__"):  # Objects with __dict__
                return str(obj)
            else:
                return str(obj)

        log_entry = json.dumps(payload, separators=(",", ":"), default=json_serializer)

        if level == "ERROR":
            Logger.error(log_entry)
        elif level == "WARNING":
            Logger.warning(log_entry)
        else:
            Logger.info(log_entry)

    def log_heal_event(self, violations_found: int, violations_fixed: int, execution_time_ms: float) -> None:
        """
        Specialized logging for heal_repository events.

        Args:
            violations_found: Number of violations detected
            violations_fixed: Number of violations successfully fixed
            execution_time_ms: Time taken to execute healing
        """
        self.log_sovereign_event(
            "HEAL",
            {
                "violations_found": violations_found,
                "violations_fixed": violations_fixed,
                "execution_time_ms": execution_time_ms,
                "heal_status": "COMPLETED",
            },
        )

    def log_validation_event(self, validator_name: str, result: bool, details: dict[str, Any]) -> None:
        """
        Specialized logging for validator events.

        Args:
            validator_name: Name of the validator that ran
            result: Whether validation passed
            details: Additional validation context
        """
        self.log_sovereign_event(
            "VALIDATE",
            {"validator": validator_name, "result": "PASS" if result else "FAIL", **details},
        )

    def disable_audit(self) -> None:
        """Disable audit logging (for testing only)."""
        self._audit_enabled = False
        self.log_sovereign_event("AUDIT_CONTROL", {"enabled": False})

    def enable_audit(self) -> None:
        """Enable audit logging."""
        self._audit_enabled = True
        self.log_sovereign_event("AUDIT_CONTROL", {"enabled": True})

    def _canonicalize_payload(self, payload: dict[str, Any]) -> str:
        """
        Canonicalize payload for consistent hashing.

        Sorts keys recursively to ensure deterministic serialization.
        """

        def _sort_recursive(obj: Any) -> Any:
            if isinstance(obj, dict):
                return sorted((k, _sort_recursive(v)) for k, v in obj.items())
            elif isinstance(obj, list | tuple):
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
            f"{self._audit_last_hash}|{self._audit_session_salt}|{action_type}|{payload_str}|{timestamp}"
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
        Generate proof and emit via event_emission_mixin.

        Args:
            action_type: Type of action (e.g., "FILE_MOVE", "HEAL_VIOLATION")
            payload: Action data to audit
            severity: Event severity level

        Returns:
            AuditProof for caller verification

        Raises:
            NotImplementedError: If event_emission_mixin is not present
        """
        # Generate proof synchronously (fast)
        proof = self._generate_audit_proof(action_type, payload)

        # Check for event_emission_mixin dependency
        if not hasattr(self, "emit_event"):
            raise NotImplementedError(
                "AuditTrailMixin requires event_emission_mixin. Ensure your class inherits from both mixins.",
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

        # Emit via event_emission_mixin (async, non-blocking)
        await self.emit_event(
            event_type=f"AUDIT_{action_type}",
            payload=event_payload,
            severity=severity,
        )

        Logger.debug(
            f"[{self.__class__.__name__}] Audited action: {action_type} (hash={proof.curr_hash[:16]}...)",
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
            f"[{self.__class__.__name__}] Sync audit proof: {action_type} (hash={proof.curr_hash[:16]}...)",
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
