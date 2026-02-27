"""Tests for Wave 16 P2 metrics emission enforcement.

Tests that metrics artifacts are emitted from single control-spine point
and duplicate emissions are rejected.
"""

import pytest
import time
from dataclasses import dataclass
from typing import Any, Dict

pytestmark = pytest.mark.governance

# Import the modules we're testing
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent / "agentic_core" / "L4_state" / "enforcement"))

try:
    from metrics_emission import (
        MetricsEmissionEnforcer,
        BlastRadiusEnforcer,
        single_authoritative_emission,
        validate_blast_radius,
        persist_phase_lock,
        restore_phase_lock,
        persist_activation_flags,
        restore_activation_flags,
        ActivationFlags
    )
    from blast_radius import BlastRadiusMetrics, enforce_blast_radius
except ImportError:
    pytest.skip("metrics_emission or blast_radius modules not available", allow_module_level=True)

@dataclass(frozen=True)
class MockMetricArtifact:
    """Mock metric artifact for testing."""
    metric_id: str
    value: float
    metadata: Dict[str, Any]

@dataclass(frozen=True)
class MockMetaLearningProposal:
    """Mock meta-learning proposal for blast radius testing."""
    proposal_id: str
    changes: Dict[str, Any]
    confidence: float

class TestMetricsEmissionEnforcement:
    """Test metrics emission enforcement functionality."""

    def setup_method(self):
        """Set up test environment."""
        # Get fresh enforcer instance for each test
        self.enforcer = MetricsEmissionEnforcer()

    def test_single_authoritative_emission_success(self):
        """Test successful emission through chokepoint."""
        # Given
        trace_id = "test_trace_001"
        artifact_type = "MetaLearningMetrics"
        artifact = MockMetricArtifact(
            metric_id="ml_001",
            value=0.85,
            metadata={"model": "test", "version": "1.0"}
        )

        # When
        self.enforcer.single_authoritative_emission(trace_id, artifact_type, artifact)

        # Then
        assert self.enforcer.verify_emission_chokepoint(trace_id, artifact_type)

    def test_duplicate_emission_rejection(self):
        """Test that duplicate emissions are rejected."""
        # Given
        trace_id = "test_trace_002"
        artifact_type = "MetaLearningMetrics"
        artifact = MockMetricArtifact("ml_002", 0.9, {})

        # When - First emission should succeed
        self.enforcer.single_authoritative_emission(trace_id, artifact_type, artifact)

        # Then - Second emission should fail
        with pytest.raises(RuntimeError, match="Duplicate emission detected"):
            self.enforcer.single_authoritative_emission(trace_id, artifact_type, artifact)

    def test_different_artifacts_same_trace(self):
        """Test that different artifact types can be emitted for same trace."""
        # Given
        trace_id = "test_trace_003"
        artifact1 = MockMetricArtifact("ml_003a", 0.8, {})
        artifact2 = MockMetricArtifact("ml_003b", 0.7, {})

        # When - Emit different artifact types
        self.enforcer.single_authoritative_emission(trace_id, "Metrics1", artifact1)
        self.enforcer.single_authoritative_emission(trace_id, "Metrics2", artifact2)

        # Then - Both should be recorded
        assert self.enforcer.verify_emission_chokepoint(trace_id, "Metrics1")
        assert self.enforcer.verify_emission_chokepoint(trace_id, "Metrics2")

    def test_emission_record_creation(self):
        """Test that emission records are created correctly."""
        # Given
        trace_id = "test_trace_004"
        artifact_type = "TestMetrics"
        artifact = MockMetricArtifact("test_004", 0.95, {"key": "value"})

        # When
        self.enforcer.single_authoritative_emission(trace_id, artifact_type, artifact)

        # Then - Verify emission was recorded
        emission_key = f"{trace_id}:{artifact_type}"
        assert emission_key in self.enforcer._emissions

        record = self.enforcer._emissions[emission_key]
        assert record.trace_id == trace_id
        assert record.artifact_type == artifact_type
        assert record.artifact_hash is not None
        assert record.emission_timestamp > 0

    def test_clear_emissions_for_trace(self):
        """Test clearing emissions for a specific trace."""
        # Given
        trace_id = "test_trace_005"
        self.enforcer.single_authoritative_emission(trace_id, "Metrics1", MockMetricArtifact("m1", 0.1, {}))
        self.enforcer.single_authoritative_emission(trace_id, "Metrics2", MockMetricArtifact("m2", 0.2, {}))
        self.enforcer.single_authoritative_emission("other_trace", "Metrics1", MockMetricArtifact("m3", 0.3, {}))

        # Verify initial state
        assert self.enforcer.verify_emission_chokepoint(trace_id, "Metrics1")
        assert self.enforcer.verify_emission_chokepoint(trace_id, "Metrics2")
        assert self.enforcer.verify_emission_chokepoint("other_trace", "Metrics1")

        # When - Clear emissions for trace
        self.enforcer.clear_emissions_for_trace(trace_id)

        # Then - Only specified trace emissions should be cleared
        assert not self.enforcer.verify_emission_chokepoint(trace_id, "Metrics1")
        assert not self.enforcer.verify_emission_chokepoint(trace_id, "Metrics2")
        assert self.enforcer.verify_emission_chokepoint("other_trace", "Metrics1")  # Should remain

    def test_blast_radius_calculation(self):
        """Test blast radius calculation for artifacts."""
        # Given - Simple artifact
        simple_artifact = MockMetricArtifact("simple", 0.5, {})

        # When
        radius = self.enforcer._calculate_blast_radius(simple_artifact)

        # Then - Should be 1 for simple objects
        assert radius == 1, "Simple artifact should have blast radius of 1"

    def test_blast_radius_complex_object(self):
        """Test blast radius for complex objects with mutable attributes."""
        # Given - Complex object with mutable attributes
        class ComplexArtifact:
            def __init__(self):
                self.mutable_list = [1, 2, 3]
                self.mutable_dict = {"key": "value"}
                self._private_attr = "private"
                self.public_attr = "public"

        artifact = ComplexArtifact()

        # When
        radius = self.enforcer._calculate_blast_radius(artifact)

        # Then - Should count non-private attributes
        assert radius == 2, "Should count 2 mutable attributes (list and dict)"

class TestBlastRadiusEnforcement:
    """Test blast radius enforcement functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.enforcer = BlastRadiusEnforcer()

    def test_validate_blast_radius_success(self):
        """Test successful blast radius validation."""
        # Given
        proposal = MockMetaLearningProposal(
            proposal_id="prop_001",
            changes={"add": "file.py", "modify": "config.json"},
            confidence=0.9
        )
        state_surface_bytes = 1000  # Small size

        # When
        result = self.enforcer.validate_blast_radius(proposal, state_surface_bytes)

        # Then
        assert result is True, "Blast radius validation should succeed"

    def test_blast_radius_exceeds_limit(self):
        """Test blast radius exceeding limits."""
        # Given - Proposal with many attributes
        class LargeProposal:
            def __init__(self):
                for i in range(2000):  # Exceed default max of 1000
                    setattr(self, f"attr_{i}", f"value_{i}")

        proposal = LargeProposal()

        # When/Then - Should raise error
        with pytest.raises(ValueError, match="Blast radius .* exceeds maximum"):
            self.enforcer.validate_blast_radius(proposal, 1000)

    def test_state_surface_bytes_exceeds_limit(self):
        """Test state surface size exceeding limits."""
        # Given
        proposal = MockMetaLearningProposal("prop", {}, 0.8)
        large_surface = 20_000_000  # Exceed default max of 10MB

        # When/Then - Should raise error
        with pytest.raises(ValueError, match="State surface .* exceeds maximum"):
            self.enforcer.validate_blast_radius(proposal, large_surface)

    def test_proposal_radius_calculation(self):
        """Test proposal blast radius calculation."""
        # Given
        proposal = MockMetaLearningProposal("prop", {"a": 1, "b": 2, "c": 3}, 0.7)

        # When
        radius = self.enforcer._calculate_proposal_radius(proposal)

        # Then - Should count dictionary attributes
        assert radius == len(proposal.__dict__), "Should count all attributes"

class TestPhaseLockPersistence:
    """Test phase lock persistence functionality."""

    def test_phase_lock_persistence_cycle(self):
        """Test complete phase lock persistence cycle."""
        # Given
        phase = 5
        metadata = {"test": "persistence"}

        # When - Persist phase lock
        persist_phase_lock(phase, True, metadata)

        # Then - Should be able to restore
        restored = restore_phase_lock()
        assert restored is not None, "Phase lock should be restored"
        assert restored["phase"] == phase, "Phase should match"
        assert restored["locked"] is True, "Lock status should match"
        assert restored["metadata"] == metadata, "Metadata should match"

    def test_phase_lock_unlock_cycle(self):
        """Test phase lock unlock cycle."""
        # Given - Lock a phase
        phase = 3
        persist_phase_lock(phase, True, {"initial": "lock"})

        # When - Unlock the phase
        persist_phase_lock(phase, False, {"unlocked": True})

        # Then - Should reflect unlocked state
        restored = restore_phase_lock()
        assert restored["locked"] is False, "Phase should be unlocked"

class TestActivationFlagsPersistence:
    """Test activation flags persistence functionality."""

    def test_activation_flags_persistence_cycle(self):
        """Test complete activation flags persistence cycle."""
        # Given
        flags = ActivationFlags(
            execution_hardened=True,
            mutation_surface_zero=True,
            guardian_coverage=0.96,
            freeze_authority_active=True,
            meta_learning_prepared=True,
            blast_radius_containment_active=True,
            meta_learning_enabled=False,  # Not yet enabled
            semantic_clock_tick=42,
            replay_digest_hash="digest123",
            signature="guardian_sig"
        )

        # When - Persist flags
        persist_activation_flags(flags)

        # Then - Should be able to restore
        restored = restore_activation_flags()
        assert restored is not None, "Activation flags should be restored"

        assert restored.execution_hardened == flags.execution_hardened
        assert restored.mutation_surface_zero == flags.mutation_surface_zero
        assert restored.guardian_coverage == flags.guardian_coverage
        assert restored.freeze_authority_active == flags.freeze_authority_active
        assert restored.meta_learning_prepared == flags.meta_learning_prepared
        assert restored.blast_radius_containment_active == flags.blast_radius_containment_active
        assert restored.meta_learning_enabled == flags.meta_learning_enabled
        assert restored.semantic_clock_tick == flags.semantic_clock_tick
        assert restored.replay_digest_hash == flags.replay_digest_hash
        assert restored.signature == flags.signature

    def test_activation_flags_default_initialization(self):
        """Test activation flags default initialization."""
        # When - Restore without prior persistence
        restored = restore_activation_flags()

        # Then - Should return None (no flags persisted yet)
        assert restored is None, "Should return None when no flags exist"

class TestIntegratedWave16Functionality:
    """Test integrated Wave 16 functionality."""

    def test_metrics_emission_with_blast_radius(self):
        """Test metrics emission with blast radius validation."""
        # Given
        trace_id = "integrated_test_001"
        artifact = MockMetricArtifact("integrated", 0.88, {"complex": True})

        # When - Emit with blast radius validation
        blast_valid = validate_blast_radius(artifact, 1000)
        assert blast_valid is True, "Blast radius should validate"

        single_authoritative_emission(trace_id, "IntegratedMetrics", artifact)

        # Then - Emission should be recorded
        enforcer = MetricsEmissionEnforcer()
        assert enforcer.verify_emission_chokepoint(trace_id, "IntegratedMetrics")

    def test_enforce_blast_radius_function(self):
        """Test blast radius enforcement function."""
        # Given
        proposal_id = "test_proposal_001"
        proposal = MockMetaLearningProposal(
            proposal_id=proposal_id,
            changes={"test": "change"},
            confidence=0.9
        )

        # When
        metrics = enforce_blast_radius(proposal_id, proposal)

        # Then
        assert isinstance(metrics, BlastRadiusMetrics)
        assert metrics.total_affected_objects > 0
        assert metrics.state_surface_bytes > 0

        # Should be able to retrieve metrics
        from blast_radius import get_proposal_metrics
        retrieved = get_proposal_metrics(proposal_id)
        assert retrieved == metrics
