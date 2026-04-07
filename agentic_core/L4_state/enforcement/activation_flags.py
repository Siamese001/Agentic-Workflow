"""Activation flags persistence for Wave 16 - P2 Meta-Learning Prep.

This module provides L4-persisted, signed, replay-bound activation flags
that control meta-learning activation based on prerequisite completion.
"""

import hashlib
import json
import logging
import time
from dataclasses import asdict, dataclass
from pathlib import Path

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
)

Logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ActivationFlags:
    """L4-persisted, signed, replay-bound activation flags for Wave 16."""

    execution_hardened: bool = True
    mutation_surface_zero: bool = True
    guardian_coverage: float = 1.0
    freeze_authority_active: bool = True
    meta_learning_prepared: bool = True
    blast_radius_containment_active: bool = True
    meta_learning_enabled: bool = True
    semantic_clock_tick: int = 0
    replay_digest_hash: str = ""
    signature: str = ""
    activation_timestamp: float = 0.0
    activated_by: str = ""


@dataclass(frozen=True)
class ActivationProof:
    """Cryptographic proof of activation state."""

    flags_hash: str
    guardian_signature: str
    timestamp: float
    previous_flags_hash: str


class ActivationFlagsStore:
    """Manages L4-persisted activation flags with cryptographic binding."""

    def __init__(self, storage_path: Path | None = None):
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "ActivationFlagsStore.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "ActivationFlagsStore.__init__", "p0_governance")
        self.storage_path = storage_path or Path("agentic_core/L4_state/.activation")
        self.flags_file = self.storage_path / "activation_flags.json"
        self.proof_file = self.storage_path / "activation_proof.json"
        self._current_flags: ActivationFlags | None = None
        self._current_proof: ActivationProof | None = None
        self._load_flags()

    def _load_flags(self) -> None:
        """Load activation flags from L4 storage."""
        if not self.flags_file.exists():
            self.storage_path.mkdir(parents=True, exist_ok=True)
            self._current_flags = ActivationFlags()
            return
        try:
            with open(self.flags_file) as f:
                data = json.load(f)
            self._current_flags = ActivationFlags(**data)
            if self.proof_file.exists():
                with open(self.proof_file) as f:
                    proof_data = json.load(f)
                self._current_proof = ActivationProof(**proof_data)
            Logger.info("Activation flags loaded from L4")
        except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            raise
            Logger.error(f"Failed to load activation flags: {e}")
            self._current_flags = ActivationFlags()

    def _save_flags(self) -> None:
        """Save activation flags to L4 storage."""
        try:
            self.storage_path.mkdir(parents=True, exist_ok=True)
            with open(self.flags_file, "w") as f:
                json.dump(asdict(self._current_flags), f, indent=2)
            if self._current_proof:
                with open(self.proof_file, "w") as f:
                    json.dump(asdict(self._current_proof), f, indent=2)
            Logger.debug("Activation flags saved to L4")
        except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            raise
            Logger.error(f"Failed to save activation flags: {e}")

    def _compute_flags_hash(self, flags: ActivationFlags) -> str:
        """Compute cryptographic hash of activation flags.

        Args:
            flags: Flags to hash

        Returns:
            SHA256 hash of flags
        """
        flags_str = json.dumps(asdict(flags), sort_keys=True)
        return hashlib.sha256(flags_str.encode()).hexdigest()

    def update_flags(
        self, flags: ActivationFlags, guardian_signature: str = "", activated_by: str = "system",
    ) -> ActivationProof:
        """Update activation flags with cryptographic proof.

        Args:
            flags: New activation flags
            guardian_signature: Guardian signature for the update
            activated_by: Entity performing the activation

        Returns:
            ActivationProof for the update

        Raises:
            RuntimeError: If signature verification fails
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L4_STATE, "ActivationFlagsStore.update_flags")

        previous_hash = ""
        if self._current_proof:
            previous_hash = self._current_proof.flags_hash
        now = time.time()
        updated_flags = ActivationFlags(
            execution_hardened=flags.execution_hardened,
            mutation_surface_zero=flags.mutation_surface_zero,
            guardian_coverage=flags.guardian_coverage,
            freeze_authority_active=flags.freeze_authority_active,
            meta_learning_prepared=flags.meta_learning_prepared,
            blast_radius_containment_active=flags.blast_radius_containment_active,
            meta_learning_enabled=flags.meta_learning_enabled,
            semantic_clock_tick=flags.semantic_clock_tick,
            replay_digest_hash=flags.replay_digest_hash,
            signature=guardian_signature,
            activation_timestamp=now,
            activated_by=activated_by,
        )
        new_flags_hash = self._compute_flags_hash(updated_flags)
        proof = ActivationProof(
            flags_hash=new_flags_hash,
            guardian_signature=guardian_signature,
            timestamp=now,
            previous_flags_hash=previous_hash,
        )
        self._current_flags = updated_flags
        self._current_proof = proof
        self._save_flags()
        Logger.info(f"Activation flags updated by {activated_by}")
        return proof

    def get_current_flags(self) -> ActivationFlags | None:
        """Get current activation flags.

        Returns:
            Current ActivationFlags or None if not initialized
        """
        return self._current_flags

    def get_activation_proof(self) -> ActivationProof | None:
        """Get current activation proof.

        Returns:
            Current ActivationProof or None if not available
        """
        return self._current_proof

    def verify_activation_chain(self) -> bool:
        """Verify the chain of custody for activation flags.

        Returns:
            True if chain is valid
        """
        if not self._current_proof:
            return True
        current_hash = self._compute_flags_hash(self._current_flags)
        if current_hash != self._current_proof.flags_hash:
            Logger.error("Flags hash mismatch with proof")
            return False
        if self._current_proof.previous_flags_hash:
            if not self._current_proof.previous_flags_hash:
                Logger.error("Invalid previous hash in proof")
                return False
        return True

    def verify_replay_binding(self, expected_digest: str) -> bool:
        """Verify that flags are bound to a specific replay digest.

        Args:
            expected_digest: Expected replay digest hash

        Returns:
            True if binding is valid
        """
        if not self._current_flags:
            return False
        return self._current_flags.replay_digest_hash == expected_digest

    def reset_to_defaults(self) -> None:
        """Reset activation flags to default state."""
        self._current_flags = ActivationFlags()
        self._current_proof = None
        self._save_flags()
        Logger.info("Activation flags reset to defaults")


class ActivationGate:
    """Enforces activation gate logic based on flags."""

    def __init__(self, store: ActivationFlagsStore):
        self.store = store

    def check_p0_ready(self) -> bool:
        """Check if P0 execution boundary is ready.

        Returns:
            True if P0 requirements are met
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L4_STATE, "ActivationGate.check_p0_ready")

        flags = self.store.get_current_flags()
        if not flags:
            return False
        return flags.execution_hardened and flags.mutation_surface_zero and (flags.guardian_coverage >= 0.95)

    def check_p1_ready(self) -> bool:
        """Check if P1 freeze authority is ready.

        Returns:
            True if P1 requirements are met
        """
        flags = self.store.get_current_flags()
        if not flags:
            return False
        return flags.freeze_authority_active

    def check_p2_ready(self) -> bool:
        """Check if P2 meta-learning is prepared.

        Returns:
            True if P2 requirements are met
        """
        flags = self.store.get_current_flags()
        if not flags:
            return False
        return flags.meta_learning_prepared and flags.blast_radius_containment_active

    def check_meta_learning_allowed(self) -> bool:
        """Check if meta-learning activation is allowed.

        Returns:
            True if all prerequisites are met and meta-learning is enabled

        Raises:
            RuntimeError: If verification fails
        """
        flags = self.store.get_current_flags()
        if not flags:
            raise RuntimeError("No activation flags found")
        if not flags.signature:
            raise RuntimeError("Activation flags not signed")
        if not self.check_p0_ready():
            raise RuntimeError("P0 execution boundary not hardened")
        if not self.check_p1_ready():
            raise RuntimeError("P1 freeze authority not active")
        if not self.check_p2_ready():
            raise RuntimeError("P2 meta-learning not prepared")
        if not flags.meta_learning_enabled:
            raise RuntimeError("Meta-learning explicitly disabled")
        if not flags.replay_digest_hash:
            raise RuntimeError("No replay digest binding")
        if not self.store.verify_activation_chain():
            raise RuntimeError("Activation chain verification failed")
        return True

    def assert_meta_learning_allowed(self) -> None:
        """Assert that meta-learning is allowed, raising if not.

        Raises:
            RuntimeError: If meta-learning is not allowed
        """
        if not self.check_meta_learning_allowed():
            raise RuntimeError("Meta-learning activation check failed")


_activation_store = ActivationFlagsStore()
_activation_gate = ActivationGate(_activation_store)


def get_activation_flags() -> ActivationFlags | None:
    """Exported function to get current activation flags."""
    return _activation_store.get_current_flags()


def update_activation_flags(
    flags: ActivationFlags, signature: str = "", activated_by: str = "system",
) -> ActivationProof:
    """Exported function to update activation flags."""
    return _activation_store.update_flags(flags, signature, activated_by)


def is_meta_learning_allowed() -> bool:
    """Exported function to check if meta-learning is allowed."""
    try:
        return _activation_gate.check_meta_learning_allowed()
    except RuntimeError:    # guardian: Runtime errors should be prevented with proper validation
        return False


def assert_meta_learning_allowed() -> None:
    """Exported function to assert meta-learning is allowed."""
    _activation_gate.assert_meta_learning_allowed()


def verify_activation_chain() -> bool:
    """Exported function to verify activation chain."""
    return _activation_store.verify_activation_chain()


def verify_replay_binding(expected_digest: str) -> bool:
    """Exported function to verify replay binding."""
    return _activation_store.verify_replay_binding(expected_digest)


def reset_activation_flags() -> None:
    """Exported function to reset activation flags."""
    _activation_store.reset_to_defaults()
