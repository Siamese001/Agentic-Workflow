"""Tests for Wave 16 P2 blast radius containment.

Tests that blast radius is deterministically bounded and proposals
exceeding limits are rejected.
"""

import pytest
from dataclasses import dataclass
from typing import Any, Dict, List

pytestmark = pytest.mark.governance

# Import the modules we're testing
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent / "agentic_core" / "L4_state" / "enforcement"))

try:
    from blast_radius import (
        BlastRadiusCalculator,
        BlastRadiusEnforcer,
        BlastRadiusMetrics,
        enforce_blast_radius,
        get_proposal_metrics,
        clear_proposal,
        validate_total_impact
    )
except ImportError:
    pytest.skip("blast_radius module not available", allow_module_level=True)

@dataclass(frozen=True)
class MockMetaLearningProposal:
    """Mock meta-learning proposal for testing."""
    proposal_id: str
    changes: Dict[str, Any]
    affected_files: List[str]
    confidence: float
    cross_layer_impacts: List[str]

@dataclass(frozen=True)
class ComplexProposal:
    """Complex proposal with nested structures."""
    proposal_id: str
    nested_data: Dict[str, Any]
    collection_data: List[Any]
    simple_field: str

class TestBlastRadiusCalculator:
    """Test blast radius calculation functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.calculator = BlastRadiusCalculator(max_radius=100, max_bytes=1000)

    def test_calculate_blast_radius_simple_proposal(self):
        """Test blast radius calculation for simple proposal."""
        # Given
        proposal = MockMetaLearningProposal(
            proposal_id="simple_001",
            changes={"add": "file.py"},
            affected_files=["file.py"],
            confidence=0.9,
            cross_layer_impacts=[]
        )

        # When
        metrics = self.calculator.calculate_blast_radius(proposal)

        # Then
        assert isinstance(metrics, BlastRadiusMetrics)
        assert metrics.total_affected_objects >= 1, "Should affect at least 1 object"
        assert metrics.state_surface_bytes > 0, "Should have positive byte count"
        assert metrics.mutation_depth >= 1, "Should have minimum depth of 1"
        assert metrics.cross_layer_impacts >= 0, "Cross layer impacts should be non-negative"

    def test_calculate_blast_radius_complex_proposal(self):
        """Test blast radius calculation for complex proposal."""
        # Given
        nested = {
            "inner_dict": {"key": "value"},
            "inner_list": [1, 2, 3]
        }
        collection = [{"item": i} for i in range(5)]

        proposal = ComplexProposal(
            proposal_id="complex_001",
            nested_data=nested,
            collection_data=collection,
            simple_field="test"
        )

        # When
        metrics = self.calculator.calculate_blast_radius(proposal)

        # Then
        assert metrics.total_affected_objects > 1, "Complex proposal should affect more objects"
        assert metrics.mutation_depth > 1, "Nested structures should increase depth"

    def test_blast_radius_exceeds_limit(self):
        """Test that exceeding blast radius limit raises error."""
        # Given - Create proposal that exceeds limit
        class LargeProposal:
            def __init__(self):
                # Create many attributes to exceed max_radius of 100
                for i in range(150):
                    setattr(self, f"attr_{i}", f"value_{i}")

        proposal = LargeProposal()

        # When/Then - Should raise ValueError
        with pytest.raises(ValueError, match="Blast radius .* exceeds maximum"):
            self.calculator.calculate_blast_radius(proposal)

    def test_state_surface_bytes_exceeds_limit(self):
        """Test that exceeding byte limit raises error."""
        # Given - Create proposal with large string content
        class LargeByteProposal:
            def __init__(self):
                self.large_data = "x" * 2000  # Exceed max_bytes of 1000

        proposal = LargeByteProposal()

        # When/Then - Should raise ValueError
        with pytest.raises(ValueError, match="State surface .* exceeds maximum"):
            self.calculator.calculate_blast_radius(proposal)

    def test_count_affected_objects(self):
        """Test counting of affected objects."""
        # Given
        proposal = MockMetaLearningProposal(
            proposal_id="count_test",
            changes={"a": 1, "b": 2, "c": 3, "d": 4},
            affected_files=["f1.py", "f2.py"],
            confidence=0.8,
            cross_layer_impacts=[]
        )

        # When
        count = self.calculator._count_affected_objects(proposal)

        # Then - Should count non-private attributes
        assert count >= 4, "Should count at least 4 change attributes"

    def test_estimate_state_surface(self):
        """Test state surface estimation."""
        # Given
        proposal = MockMetaLearningProposal(
            proposal_id="surface_test",
            changes={"test": "data with some length"},
            affected_files=["file1.py", "file2.py"],
            confidence=0.7,
            cross_layer_impacts=[]
        )

        # When
        bytes_est = self.calculator._estimate_state_surface(proposal)

        # Then - Should be positive
        assert bytes_est > 0, "Should estimate positive byte count"

    def test_calculate_mutation_depth(self):
        """Test mutation depth calculation."""
        # Given - Simple object
        simple = MockMetaLearningProposal("simple", {}, [], 0.5, [])

        # When
        depth = self.calculator._calculate_mutation_depth(simple)

        # Then - Should be 1 for simple objects
        assert depth == 1, "Simple object should have depth 1"

        # Given - Nested object
        nested = ComplexProposal("nested", {"inner": {}}, [], "test")

        # When
        nested_depth = self.calculator._calculate_mutation_depth(nested)

        # Then - Should be greater than 1
        assert nested_depth > 1, "Nested object should have depth > 1"

    def test_count_cross_layer_impacts(self):
        """Test counting cross-layer impacts."""
        # Given - Proposal with layer references
        proposal = MockMetaLearningProposal(
            proposal_id="cross_layer_test",
            changes={"modifies": "agentic_core/L1_cognition/file.py"},
            affected_files=["agentic_core/L2_execution/executor.py"],
            confidence=0.9,
            cross_layer_impacts=["L1_cognition", "L2_execution"]
        )

        # When
        cross_layer_count = self.calculator._count_cross_layer_impacts(proposal)

        # Then - Should detect layer patterns
        assert cross_layer_count >= 2, "Should detect at least 2 layer impacts"

class TestBlastRadiusEnforcer:
    """Test blast radius enforcement functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.enforcer = BlastRadiusEnforcer()

    def test_enforce_blast_radius_success(self):
        """Test successful blast radius enforcement."""
        # Given
        proposal_id = "enforce_test_001"
        proposal = MockMetaLearningProposal(
            proposal_id=proposal_id,
            changes={"test": "change"},
            affected_files=["test.py"],
            confidence=0.8,
            cross_layer_impacts=[]
        )

        # When
        metrics = self.enforcer.enforce_blast_radius(proposal_id, proposal)

        # Then
        assert isinstance(metrics, BlastRadiusMetrics)
        assert self.enforcer.get_proposal_metrics(proposal_id) == metrics

    def test_enforce_duplicate_proposal(self):
        """Test that duplicate proposals are rejected."""
        # Given
        proposal_id = "duplicate_test"
        proposal = MockMetaLearningProposal("test", {}, [], 0.5, [])

        # When - First enforcement should succeed
        self.enforcer.enforce_blast_radius(proposal_id, proposal)

        # Then - Second should fail
        with pytest.raises(RuntimeError, match="Proposal .* already exists"):
            self.enforcer.enforce_blast_radius(proposal_id, proposal)

    def test_get_proposal_metrics(self):
        """Test retrieving proposal metrics."""
        # Given
        proposal_id = "retrieve_test"
        proposal = MockMetaLearningProposal("retrieve", {}, [], 0.6, [])

        # When
        stored_metrics = self.enforcer.enforce_blast_radius(proposal_id, proposal)
        retrieved_metrics = self.enforcer.get_proposal_metrics(proposal_id)

        # Then
        assert stored_metrics == retrieved_metrics, "Retrieved metrics should match stored"

        # Non-existent proposal should return None
        assert self.enforcer.get_proposal_metrics("non_existent") is None

    def test_clear_proposal(self):
        """Test clearing a proposal."""
        # Given
        proposal_id = "clear_test"
        proposal = MockMetaLearningProposal("clear", {}, [], 0.7, [])
        self.enforcer.enforce_blast_radius(proposal_id, proposal)

        # Verify proposal exists
        assert self.enforcer.get_proposal_metrics(proposal_id) is not None

        # When
        clear_proposal(proposal_id)  # Using exported function

        # Then - Proposal should be cleared
        assert self.enforcer.get_proposal_metrics(proposal_id) is None

    def test_get_total_blast_radius(self):
        """Test calculating total blast radius."""
        # Given - Add multiple proposals
        for i in range(3):
            proposal_id = f"total_test_{i}"
            proposal = MockMetaLearningProposal(
                proposal_id=proposal_id,
                changes={f"change_{i}": f"value_{i}"},
                affected_files=[f"file_{i}.py"],
                confidence=0.8,
                cross_layer_impacts=[]
            )
            self.enforcer.enforce_blast_radius(proposal_id, proposal)

        # When
        total_radius = self.enforcer.get_total_blast_radius()

        # Then - Should be sum of all proposal radii
        assert total_radius >= 3, "Total radius should be at least 3 (one per proposal)"

    def test_validate_total_impact_success(self):
        """Test successful total impact validation."""
        # Given - Add small proposals
        for i in range(2):
            proposal_id = f"impact_test_{i}"
            proposal = MockMetaLearningProposal(
                proposal_id=proposal_id,
                changes={"small": "change"},
                affected_files=["small.py"],
                confidence=0.9,
                cross_layer_impacts=[]
            )
            self.enforcer.enforce_blast_radius(proposal_id, proposal)

        # When
        is_valid = validate_total_impact()  # Using exported function

        # Then
        assert is_valid is True, "Total impact should be valid"

    def test_validate_total_impact_exceeds_limit(self):
        """Test total impact exceeding limits."""
        # Given - Add proposals that collectively exceed limit
        # Create many proposals to exceed default max_radius of 1000
        for i in range(1200):  # More than default max
            proposal_id = f"overload_test_{i}"
            proposal = MockMetaLearningProposal(
                proposal_id=proposal_id,
                changes={"change": f"value_{i}"},
                affected_files=[f"file_{i}.py"],
                confidence=0.8,
                cross_layer_impacts=[]
            )
            self.enforcer.enforce_blast_radius(proposal_id, proposal)

        # When/Then - Should raise error
        with pytest.raises(ValueError, match="Total blast radius .* exceeds maximum"):
            validate_total_impact()

class TestBlastRadiusIntegration:
    """Test blast radius integration with other Wave 16 components."""

    def test_blast_radius_with_metrics_emission(self):
        """Test blast radius enforcement with metrics emission."""
        # Given
        proposal_id = "integration_test_001"
        proposal = MockMetaLearningProposal(
            proposal_id=proposal_id,
            changes={"integrated": "change"},
            affected_files=["integrated.py"],
            confidence=0.85,
            cross_layer_impacts=["L1_cognition"]
        )

        # When - Enforce blast radius
        metrics = enforce_blast_radius(proposal_id, proposal)

        # Then - Should be able to retrieve metrics
        retrieved = get_proposal_metrics(proposal_id)
        assert retrieved == metrics, "Should retrieve same metrics"

        # And should be able to clear
        clear_proposal(proposal_id)
        assert get_proposal_metrics(proposal_id) is None, "Should be cleared"

    def test_multiple_proposals_blast_radius(self):
        """Test blast radius across multiple proposals."""
        # Given - Create multiple proposals
        proposals = []
        for i in range(5):
            proposal_id = f"multi_test_{i}"
            proposal = MockMetaLearningProposal(
                proposal_id=proposal_id,
                changes={f"key_{i}": f"value_{i}"},
                affected_files=[f"file_{i}.py"],
                confidence=0.8 + i * 0.02,
                cross_layer_impacts=[f"L{i%7}_layer"]
            )
            proposals.append((proposal_id, proposal))

        # When - Enforce all proposals
        metrics_list = []
        for proposal_id, proposal in proposals:
            metrics = enforce_blast_radius(proposal_id, proposal)
            metrics_list.append(metrics)

        # Then - All should have valid metrics
        assert len(metrics_list) == 5, "Should have metrics for all proposals"

        for metrics in metrics_list:
            assert isinstance(metrics, BlastRadiusMetrics)
            assert metrics.total_affected_objects > 0
            assert metrics.state_surface_bytes > 0

        # Validate total impact
        assert validate_total_impact() is True, "Total impact should be valid"

    def test_proposal_with_cross_layer_impacts(self):
        """Test proposal that affects multiple layers."""
        # Given - Proposal with multiple layer impacts
        proposal = MockMetaLearningProposal(
            proposal_id="cross_layer_multi",
            changes={
                "l1_change": "agentic_core/L1_cognition/reasoning/agent.py",
                "l2_change": "agentic_core/L2_execution/engines/executor.py",
                "l4_change": "agentic_core/L4_state/storage/state.py"
            },
            affected_files=["agent.py", "executor.py", "state.py"],
            confidence=0.9,
            cross_layer_impacts=["L1_cognition", "L2_execution", "L4_state"]
        )

        # When
        metrics = enforce_blast_radius("cross_layer_test", proposal)

        # Then - Should detect cross-layer impacts
        assert metrics.cross_layer_impacts >= 3, "Should detect at least 3 cross-layer impacts"
        assert metrics.mutation_depth >= 1, "Should have positive mutation depth"
