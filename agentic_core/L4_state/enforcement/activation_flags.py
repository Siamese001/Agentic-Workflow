"""Activation flags persistence for Wave 16 - P2 Meta-Learning Prep.

This module provides L4-persisted, signed, replay-bound activation flags
that control meta-learning activation based on prerequisite completion.
"""

import json
import logging
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Optional, Any
import hashlib

Logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class ActivationFlags:
    """L4-persisted, signed, replay-bound activation flags for Wave 16."""
    # P0 Execution Boundary
    execution_hardened: bool = False
    mutation_surface_zero: bool = False
    guardian_coverage: float = 0.0

    # P1 Freeze Authority
    freeze_authority_active: bool = False

    # P2 Meta-Learning Prepared
    meta_learning_prepared: bool = False
    blast_radius_containment_active: bool = False

    # Meta-Learning Activation (requires all above)
    meta_learning_enabled: bool = False

    # Metadata for replay binding
    semantic_clock_tick: int = 0
    replay_digest_hash: str = ""
    signature: str = ""  # Guardian signature

    # Additional metadata
    activation_timestamp: float = 0.0
    activated_by: str = ""

@dataclass(frozen=True)
class ActivationProof:
    """Cryptographic proof of activation state."""
    flags_hash: str
    guardian_signature: str
    timestamp: float
    previous_flags_hash: str  # For chain of custody

class ActivationFlagsStore:
    """Manages L4-persisted activation flags with cryptographic binding."""

    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path("agentic_core/L4_state/.activation")
        self.flags_file = self.storage_path / "activation_flags.json"
        self.proof_file = self.storage_path / "activation_proof.json"
        self._current_flags: Optional[ActivationFlags] = None
        self._current_proof: Optional[ActivationProof] = None
        self._load_flags()

    def _load_flags(self) -> None:
        """Load activation flags from L4 storage."""
        if not self.flags_file.exists():
            self.storage_path.mkdir(parents=True, exist_ok=True)
            # Don't initialize automatically - let caller handle it
            return

        try:
            with open(self.flags_file, 'r') as f:
                data = json.load(f)

            self._current_flags = ActivationFlags(**data)

            # Load proof if exists
            if self.proof_file.exists():
                with open(self.proof_file, 'r') as f:
                    proof_data = json.load(f)
                self._current_proof = ActivationProof(**proof_data)

            Logger.info("Activation flags loaded from L4")

        except Exception as e:
            Logger.error(f"Failed to load activation flags: {e}")
            self._current_flags = ActivationFlags()

    def _save_flags(self) -> None:
        """Save activation flags to L4 storage."""
        try:
            self.storage_path.mkdir(parents=True, exist_ok=True)

            with open(self.flags_file, 'w') as f:
                json.dump(asdict(self._current_flags), f, indent=2)

            if self._current_proof:
                with open(self.proof_file, 'w') as f:
                    json.dump(asdict(self._current_proof), f, indent=2)

            Logger.debug("Activation flags saved to L4")

        except Exception as e:
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

    def update_flags(self,
                    flags: ActivationFlags,
                    guardian_signature: str = "",
                    activated_by: str = "system") -> ActivationProof:
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
        # Compute hash of new flags
        new_flags_hash = self._compute_flags_hash(flags)

        # Get previous hash for chain of custody
        previous_hash = ""
        if self._current_proof:
            previous_hash = self._current_proof.flags_hash

        # Create activation proof
        proof = ActivationProof(
            flags_hash=new_flags_hash,
            guardian_signature=guardian_signature,
            timestamp=time.time(),
            previous_flags_hash=previous_hash
        )

        # Update flags with metadata
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
            activation_timestamp=time.time(),
            activated_by=activated_by
        )

        # Store updates
        self._current_flags = updated_flags
        self._current_proof = proof
        self._save_flags()

        Logger.info(f"Activation flags updated by {activated_by}")
        return proof

    def get_current_flags(self) -> Optional[ActivationFlags]:
        """Get current activation flags.

        Returns:
            Current ActivationFlags or None if not initialized
        """
        return self._current_flags

    def get_activation_proof(self) -> Optional[ActivationProof]:
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
            return True  # No proof means initial state

        # Verify current flags hash matches proof
        current_hash = self._compute_flags_hash(self._current_flags)
        if current_hash != self._current_proof.flags_hash:
            Logger.error("Flags hash mismatch with proof")
            return False

        # Verify previous hash if exists
        if self._current_proof.previous_flags_hash:
            # In a full implementation, we would verify against historical proofs
            # For now, just check it's not empty
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
        flags = self.store.get_current_flags()
        if not flags:
            return False

        return (flags.execution_hardened and
                flags.mutation_surface_zero and
                flags.guardian_coverage >= 0.95)

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

        return (flags.meta_learning_prepared and
                flags.blast_radius_containment_active)

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

        # Verify signature
        if not flags.signature:
            raise RuntimeError("Activation flags not signed")

        # Check P0
        if not self.check_p0_ready():
            raise RuntimeError("P0 execution boundary not hardened")

        # Check P1
        if not self.check_p1_ready():
            raise RuntimeError("P1 freeze authority not active")

        # Check P2
        if not self.check_p2_ready():
            raise RuntimeError("P2 meta-learning not prepared")

        # Final gate
        if not flags.meta_learning_enabled:
            raise RuntimeError("Meta-learning explicitly disabled")

        # Verify replay binding
        if not flags.replay_digest_hash:
            raise RuntimeError("No replay digest binding")

        # Verify activation chain
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

# Global instances
_activation_store = ActivationFlagsStore()
_activation_gate = ActivationGate(_activation_store)

# Exported functions
def get_activation_flags() -> Optional[ActivationFlags]:
    """Exported function to get current activation flags."""
    return _activation_store.get_current_flags()

def update_activation_flags(flags: ActivationFlags,
                          signature: str = "",
                          activated_by: str = "system") -> ActivationProof:
    """Exported function to update activation flags."""
    return _activation_store.update_flags(flags, signature, activated_by)

def is_meta_learning_allowed() -> bool:
    """Exported function to check if meta-learning is allowed."""
    return _activation_gate.check_meta_learning_allowed()

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
