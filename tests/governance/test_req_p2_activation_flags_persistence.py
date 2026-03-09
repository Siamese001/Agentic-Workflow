"""Tests for Wave 16 P2 activation flags persistence.

Tests that activation flags persist in L4, survive restart,
and are replay-bound.
"""

import shutil
import tempfile
from pathlib import Path

import pytest

pytestmark = pytest.mark.governance

# Import the modules we're testing
import sys

sys.path.append(str(Path(__file__).parent.parent.parent / "agentic_core" / "L4_state" / "enforcement"))

try:
    from activation_flags import (
        ActivationFlags,
        ActivationFlagsStore,
        ActivationGate,
        ActivationProof,
        get_activation_flags,
        is_meta_learning_allowed,
        reset_activation_flags,
        update_activation_flags,
        verify_activation_chain,
        verify_replay_binding,
    )
except ImportError:
    pytest.fail("activation_flags module not available", allow_module_level=True)


class TestActivationFlags:
    """Test activation flags dataclass."""

    def test_activation_flags_creation(self):
        """Test creating activation flags."""
        # Given
        flags = ActivationFlags(
            execution_hardened=True,
            mutation_surface_zero=True,
            guardian_coverage=0.96,
            freeze_authority_active=True,
            meta_learning_prepared=True,
            blast_radius_containment_active=True,
            meta_learning_enabled=False,
            semantic_clock_tick=42,
            replay_digest_hash="digest123",
            signature="guardian_sig",
        )

        # Then
        assert flags.execution_hardened is True
        assert flags.mutation_surface_zero is True
        assert flags.guardian_coverage == 0.96
        assert flags.freeze_authority_active is True
        assert flags.meta_learning_prepared is True
        assert flags.blast_radius_containment_active is True
        assert flags.meta_learning_enabled is False
        assert flags.semantic_clock_tick == 42
        assert flags.replay_digest_hash == "digest123"
        assert flags.signature == "guardian_sig"

    def test_activation_flags_immutability(self):
        """Test that activation flags are immutable."""
        # Given
        flags = ActivationFlags()

        # When/Then - Attempting to modify should fail
        with pytest.raises(AttributeError):
            flags.execution_hardened = True

        with pytest.raises(AttributeError):
            flags.guardian_coverage = 1.0

        with pytest.raises(AttributeError):
            flags.meta_learning_enabled = True

    def test_activation_flags_defaults(self):
        """Test activation flags default values (mandatory application mode)."""
        # Given
        flags = ActivationFlags()

        # Then — all prerequisite flags default to True (mandatory application)
        assert flags.execution_hardened is True
        assert flags.mutation_surface_zero is True
        assert flags.guardian_coverage == 1.0
        assert flags.freeze_authority_active is True
        assert flags.meta_learning_prepared is True
        assert flags.blast_radius_containment_active is True
        assert flags.meta_learning_enabled is True
        assert flags.semantic_clock_tick == 0
        assert flags.replay_digest_hash == ""
        assert flags.signature == ""


class TestActivationFlagsStore:
    """Test activation flags persistence store."""

    def setup_method(self):
        """Set up test environment."""
        # Create temporary directory for test storage
        self.temp_dir = Path(tempfile.mkdtemp())
        self.store = ActivationFlagsStore(self.temp_dir)

    def teardown_method(self):
        """Clean up test environment."""
        # Remove temporary directory
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_persist_and_restore_flags(self):
        """Test persisting and restoring activation flags."""
        # Given
        flags = ActivationFlags(
            execution_hardened=True,
            mutation_surface_zero=True,
            guardian_coverage=0.95,
            freeze_authority_active=True,
            meta_learning_prepared=True,
            blast_radius_containment_active=True,
            meta_learning_enabled=False,
            semantic_clock_tick=100,
            replay_digest_hash="test_digest",
            signature="test_signature",
        )

        # When - Persist flags
        proof = self.store.update_flags(flags, "test_signature", "test_suite")

        # Then - Should be able to restore
        restored_flags = self.store.get_current_flags()
        assert restored_flags is not None, "Flags should be restored"

        assert restored_flags.execution_hardened == flags.execution_hardened
        assert restored_flags.mutation_surface_zero == flags.mutation_surface_zero
        assert restored_flags.guardian_coverage == flags.guardian_coverage
        assert restored_flags.freeze_authority_active == flags.freeze_authority_active
        assert restored_flags.meta_learning_prepared == flags.meta_learning_prepared
        assert restored_flags.blast_radius_containment_active == flags.blast_radius_containment_active
        assert restored_flags.meta_learning_enabled == flags.meta_learning_enabled
        assert restored_flags.semantic_clock_tick == flags.semantic_clock_tick
        assert restored_flags.replay_digest_hash == flags.replay_digest_hash
        assert restored_flags.signature == flags.signature

        # Verify proof was created
        assert proof is not None
        assert proof.guardian_signature == "test_signature"
        assert proof.flags_hash is not None
        assert proof.timestamp > 0

    def test_persistence_across_instances(self):
        """Test persistence across store instances."""
        # Given - Create flags in first instance
        flags = ActivationFlags(execution_hardened=True, freeze_authority_active=True, semantic_clock_tick=50)
        self.store.update_flags(flags, "sig1", "test")

        # When - Create new store instance
        store2 = ActivationFlagsStore(self.temp_dir)

        # Then - Flags should be persisted
        restored = store2.get_current_flags()
        assert restored is not None, "Flags should persist across instances"
        assert restored.execution_hardened is True
        assert restored.freeze_authority_active is True
        assert restored.semantic_clock_tick == 50

    def test_activation_proof_creation(self):
        """Test activation proof creation."""
        # Given
        flags = ActivationFlags(execution_hardened=True)

        # When
        proof = self.store.update_flags(flags, "proof_sig", "prover")

        # Then
        assert isinstance(proof, ActivationProof)
        assert proof.guardian_signature == "proof_sig"
        assert proof.timestamp > 0
        assert proof.flags_hash is not None
        assert proof.previous_flags_hash == ""  # First update has no previous

    def test_chain_of_custody(self):
        """Test chain of custody in activation proofs."""
        # Given - First update
        flags1 = ActivationFlags(execution_hardened=True)
        proof1 = self.store.update_flags(flags1, "sig1", "updater1")

        # When - Second update
        flags2 = ActivationFlags(execution_hardened=True, freeze_authority_active=True)
        proof2 = self.store.update_flags(flags2, "sig2", "updater2")

        # Then - Chain should be maintained
        assert proof2.previous_flags_hash == proof1.flags_hash, "Should link to previous proof"

        # Verify chain integrity
        current_proof = self.store.get_activation_proof()
        assert current_proof == proof2, "Should get latest proof"

    def test_verify_activation_chain(self):
        """Test activation chain verification."""
        # Given - Create valid chain
        flags = ActivationFlags(execution_hardened=True)
        self.store.update_flags(flags, "valid_sig", "validator")

        # When
        is_valid = self.store.verify_activation_chain()

        # Then
        assert is_valid is True, "Valid chain should verify"

    def test_verify_replay_binding(self):
        """Test replay binding verification."""
        # Given
        expected_digest = "replay_digest_123"
        flags = ActivationFlags(execution_hardened=True, replay_digest_hash=expected_digest)
        self.store.update_flags(flags, "replay_sig", "replay_test")

        # When
        is_bound = self.store.verify_replay_binding(expected_digest)

        # Then
        assert is_bound is True, "Should verify correct digest"

        # Wrong digest should fail
        is_bound_wrong = self.store.verify_replay_binding("wrong_digest")
        assert is_bound_wrong is False, "Should reject wrong digest"

    def test_reset_to_defaults(self):
        """Test resetting flags to defaults."""
        # Given - Set some flags
        flags = ActivationFlags(
            execution_hardened=True, freeze_authority_active=True, meta_learning_enabled=True
        )
        self.store.update_flags(flags, "reset_sig", "resetter")

        # Verify flags are set
        current = self.store.get_current_flags()
        assert current.execution_hardened is True
        assert current.meta_learning_enabled is True

        # When - Reset
        self.store.reset_to_defaults()

        # Then - Should be back to defaults (mandatory application mode)
        reset_flags = self.store.get_current_flags()
        assert reset_flags.execution_hardened is True
        assert reset_flags.freeze_authority_active is True
        assert reset_flags.meta_learning_enabled is True
        assert reset_flags.guardian_coverage == 1.0

    def test_missing_storage_initialization(self):
        """Test initialization with missing storage."""
        # Given - Remove storage file
        storage_file = self.temp_dir / ".activation" / "activation_flags.json"
        if storage_file.exists():
            storage_file.unlink()

        # When - Create new store
        new_store = ActivationFlagsStore(self.temp_dir)

        # Then - Should initialize with defaults
        flags = new_store.get_current_flags()
        assert flags is not None, "Should initialize with default flags"
        assert flags.execution_hardened is True, "Should have default values (mandatory application)"


class TestActivationGate:
    """Test activation gate logic."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.store = ActivationFlagsStore(self.temp_dir)
        self.gate = ActivationGate(self.store)

    def teardown_method(self):
        """Clean up test environment."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_p0_readiness_check(self):
        """Test P0 readiness check."""
        # Given - Flags not ready
        flags = ActivationFlags()
        self.store.update_flags(flags, "test", "test")

        # When/Then - Should be ready with defaults (mandatory application mode)
        assert self.gate.check_p0_ready(), "Should be ready with defaults"

        # Given - Set P0 flags
        p0_flags = ActivationFlags(
            execution_hardened=True, mutation_surface_zero=True, guardian_coverage=0.96
        )
        self.store.update_flags(p0_flags, "test", "test")

        # When/Then - Should be ready
        assert self.gate.check_p0_ready(), "Should be ready with P0 flags set"

    def test_p1_readiness_check(self):
        """Test P1 readiness check."""
        # Given - Default flags (mandatory application mode — all True)
        flags = ActivationFlags()
        self.store.update_flags(flags, "test", "test")

        # When/Then - Should be ready with defaults
        assert self.gate.check_p1_ready(), "Should be ready with default flags"

        # Given - Explicitly disable P1
        p1_flags = ActivationFlags(freeze_authority_active=False)
        self.store.update_flags(p1_flags, "test", "test")

        # When/Then - Should not be ready
        assert not self.gate.check_p1_ready(), "Should not be ready with freeze_authority_active=False"

    def test_p2_readiness_check(self):
        """Test P2 readiness check."""
        # Given - Default flags (mandatory application mode — all True)
        flags = ActivationFlags()
        self.store.update_flags(flags, "test", "test")

        # When/Then - Should be ready with defaults
        assert self.gate.check_p2_ready(), "Should be ready with default flags"

        # Given - Explicitly disable P2
        p2_flags = ActivationFlags(meta_learning_prepared=False, blast_radius_containment_active=False)
        self.store.update_flags(p2_flags, "test", "test")

        # When/Then - Should not be ready
        assert not self.gate.check_p2_ready(), "Should not be ready with P2 flags disabled"

    def test_meta_learning_allowed_all_prerequisites(self):
        """Test meta-learning allowed with all prerequisites."""
        # Given - All prerequisites met
        flags = ActivationFlags(
            execution_hardened=True,
            mutation_surface_zero=True,
            guardian_coverage=0.96,
            freeze_authority_active=True,
            meta_learning_prepared=True,
            blast_radius_containment_active=True,
            meta_learning_enabled=True,
            replay_digest_hash="valid_digest",
            signature="guardian_signature",
        )
        self.store.update_flags(flags, "test", "test")

        # When
        is_allowed = self.gate.check_meta_learning_allowed()

        # Then
        assert is_allowed is True, "Should be allowed with all prerequisites"

    def test_meta_learning_not_allowed_missing_p0(self):
        """Test meta-learning not allowed without P0."""
        # Given - Missing P0
        flags = ActivationFlags(
            execution_hardened=False,  # Missing
            mutation_surface_zero=True,
            guardian_coverage=0.96,
            freeze_authority_active=True,
            meta_learning_prepared=True,
            blast_radius_containment_active=True,
            meta_learning_enabled=True,
            replay_digest_hash="digest",
            signature="sig",
        )
        self.store.update_flags(flags, "test", "test")

        # When/Then - Should raise error
        with pytest.raises(RuntimeError, match="P0 execution boundary not hardened"):
            self.gate.check_meta_learning_allowed()

    def test_meta_learning_not_allowed_missing_signature(self):
        """Test meta-learning not allowed without signature."""
        # Given - Missing signature
        flags = ActivationFlags(
            execution_hardened=True,
            mutation_surface_zero=True,
            guardian_coverage=0.96,
            freeze_authority_active=True,
            meta_learning_prepared=True,
            blast_radius_containment_active=True,
            meta_learning_enabled=True,
            replay_digest_hash="digest",
            signature="",  # Missing
        )
        # Pass empty guardian_signature so stored flags.signature stays empty
        self.store.update_flags(flags, "", "test")

        # When/Then - Should raise error
        with pytest.raises(RuntimeError, match="Activation flags not signed"):
            self.gate.check_meta_learning_allowed()

    def test_meta_learning_not_allowed_explicitly_disabled(self):
        """Test meta-learning not allowed when explicitly disabled."""
        # Given - All prerequisites but meta_learning_disabled
        flags = ActivationFlags(
            execution_hardened=True,
            mutation_surface_zero=True,
            guardian_coverage=0.96,
            freeze_authority_active=True,
            meta_learning_prepared=True,
            blast_radius_containment_active=True,
            meta_learning_enabled=False,  # Explicitly disabled
            replay_digest_hash="digest",
            signature="sig",
        )
        self.store.update_flags(flags, "test", "test")

        # When/Then - Should raise error
        with pytest.raises(RuntimeError, match="Meta-learning explicitly disabled"):
            self.gate.check_meta_learning_allowed()

    def test_assert_meta_learning_allowed(self):
        """Test assert_meta_learning_allowed function."""
        # Given - All prerequisites met
        flags = ActivationFlags(
            execution_hardened=True,
            mutation_surface_zero=True,
            guardian_coverage=0.96,
            freeze_authority_active=True,
            meta_learning_prepared=True,
            blast_radius_containment_active=True,
            meta_learning_enabled=True,
            replay_digest_hash="digest",
            signature="sig",
        )
        self.store.update_flags(flags, "test", "test")

        # When/Then - Should not raise
        self.gate.assert_meta_learning_allowed()

        # Given - Missing prerequisite
        incomplete_flags = ActivationFlags(
            execution_hardened=False,
            mutation_surface_zero=True,
            guardian_coverage=0.96,
            freeze_authority_active=True,
            meta_learning_prepared=True,
            blast_radius_containment_active=True,
            meta_learning_enabled=True,
            replay_digest_hash="digest",
            signature="sig",
        )
        self.store.update_flags(incomplete_flags, "test", "test")

        # When/Then - Should raise
        with pytest.raises(RuntimeError):
            self.gate.assert_meta_learning_allowed()


class TestActivationFlagsIntegration:
    """Test activation flags integration with exported functions."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        import activation_flags

        activation_flags.ActivationFlagsStore._instance = None
        self.original_store = activation_flags._activation_store
        self.original_gate = activation_flags._activation_gate
        new_store = ActivationFlagsStore(self.temp_dir)
        activation_flags._activation_store = new_store
        activation_flags._activation_gate = ActivationGate(new_store)

    def teardown_method(self):
        """Clean up test environment."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
        import activation_flags

        activation_flags._activation_store = self.original_store
        activation_flags._activation_gate = self.original_gate

    def test_exported_functions(self):
        """Test exported functions work correctly."""
        # Given - Create flags
        flags = ActivationFlags(execution_hardened=True, freeze_authority_active=True, semantic_clock_tick=25)

        # When - Use exported functions
        update_result = update_activation_flags(flags, "test_sig", "integration_test")
        current_flags = get_activation_flags()

        # Then
        assert update_result is not None, "Update should return proof"
        assert current_flags is not None, "Should get current flags"
        assert current_flags.execution_hardened is True
        assert current_flags.freeze_authority_active is True
        assert current_flags.semantic_clock_tick == 25

    def test_is_meta_learning_allowed_function(self):
        """Test is_meta_learning_allowed exported function."""
        # Given - Not allowed
        flags = ActivationFlags()
        update_activation_flags(flags, "test", "test")

        # When/Then
        assert not is_meta_learning_allowed(), "Should not be allowed by default"

        # Given - Allowed
        allowed_flags = ActivationFlags(
            execution_hardened=True,
            mutation_surface_zero=True,
            guardian_coverage=0.96,
            freeze_authority_active=True,
            meta_learning_prepared=True,
            blast_radius_containment_active=True,
            meta_learning_enabled=True,
            replay_digest_hash="digest",
            signature="sig",
        )
        update_activation_flags(allowed_flags, "test", "test")

        # When/Then
        assert is_meta_learning_allowed(), "Should be allowed with all prerequisites"

    def test_verify_functions(self):
        """Test verification exported functions."""
        # Given - Create valid flags
        flags = ActivationFlags(execution_hardened=True, replay_digest_hash="test_digest")
        update_activation_flags(flags, "test_sig", "test")

        # When/Then
        assert verify_activation_chain(), "Chain should verify"
        assert verify_replay_binding("test_digest"), "Should verify correct digest"
        assert not verify_replay_binding("wrong_digest"), "Should reject wrong digest"

    def test_reset_function(self):
        """Test reset exported function."""
        # Given - Set some flags
        flags = ActivationFlags(execution_hardened=True, meta_learning_enabled=True)
        update_activation_flags(flags, "test", "test")

        # Verify flags are set
        current = get_activation_flags()
        assert current.execution_hardened is True

        # When - Reset
        reset_activation_flags()

        # Then - Should be defaults
        reset_flags = get_activation_flags()
        assert reset_flags.execution_hardened is True
        assert reset_flags.meta_learning_enabled is True
