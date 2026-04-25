"""Tests for L0_routing.enforcement.boundary_contracts module."""

import pytest

from agentic_core.L0_routing.enforcement import boundary_contracts
from agentic_core.L0_routing.types.boundary_types import (
    BoundarySchemaDescriptor,
    ContextRetrievalRequest,
    InvariantCheck,
    InvariantSeverity,
    InvariantViolation,
    MetaInvariantReport,
    SchemaValidationStatus,
    SSOTBinding,
)


class TestBoundaryContracts:
    """Test suite for boundary contracts enforcement."""

    def test_resolve_ssot_binding_success(self):
        """Test successful SSOT binding resolution."""
        registry = {"node1": "entry1", "node2": "entry2"}
        binding = boundary_contracts.resolve_ssot_binding("node1", registry)
        
        assert isinstance(binding, SSOTBinding)
        assert binding.node_id == "node1"
        assert binding.blueprint_entry == "entry1"
        assert binding.resolved is True

    def test_resolve_ssot_binding_empty_node_id(self):
        """Test SSOT binding resolution fails on empty node_id."""
        registry = {"node1": "entry1"}
        with pytest.raises(boundary_contracts.SSOTBindingError, match="node_id must be non-empty"):
            boundary_contracts.resolve_ssot_binding("", registry)

    def test_resolve_ssot_binding_unknown_node(self):
        """Test SSOT binding resolution fails on unknown node."""
        registry = {"node1": "entry1"}
        with pytest.raises(boundary_contracts.SSOTBindingError, match="does not resolve"):
            boundary_contracts.resolve_ssot_binding("unknown", registry)

    def test_build_context_retrieval_request(self):
        """Test successful context retrieval request building."""
        request = boundary_contracts.build_context_retrieval_request(
            trace_id="trace123",
            query_hash="hash123",
            semantic_clock_tick=42,
        )
        
        assert isinstance(request, ContextRetrievalRequest)
        assert request.trace_id == "trace123"
        assert request.query_hash == "hash123"
        assert request.semantic_clock_tick == 42

    def test_build_context_retrieval_request_invalid(self):
        """Test context retrieval request fails on invalid input."""
        with pytest.raises(boundary_contracts.ContextRetrievalError):
            boundary_contracts.build_context_retrieval_request(
                trace_id="",
                query_hash="hash123",
                semantic_clock_tick=42,
            )

    def test_validate_context_retrieval_read_only(self):
        """Test context retrieval read-only validation."""
        request = boundary_contracts.build_context_retrieval_request(
            trace_id="trace123",
            query_hash="hash123",
            semantic_clock_tick=42,
        )
        result = boundary_contracts.validate_context_retrieval_read_only(request)
        assert result is True

    def test_validate_context_retrieval_not_read_only(self):
        """Test context retrieval validation fails on non-read-only request."""
        # Create a mock request with read_only=False
        from unittest.mock import MagicMock
        
        request = MagicMock(spec=ContextRetrievalRequest)
        request.read_only = False
        
        with pytest.raises(boundary_contracts.ContextRetrievalError, match="must be read-only"):
            boundary_contracts.validate_context_retrieval_read_only(request)

    def test_validate_boundary_schema_valid(self):
        """Test boundary schema validation for valid schema."""
        descriptor = BoundarySchemaDescriptor(
            schema_id="schema1",
            schema_version="1.0",
            source_layer="L0",
            target_layer="L1",
            validation_status=SchemaValidationStatus.VALID,
        )
        result = boundary_contracts.validate_boundary_schema(descriptor)
        assert result is True

    def test_validate_boundary_schema_invalid(self):
        """Test boundary schema validation fails for invalid schema."""
        descriptor = BoundarySchemaDescriptor(
            schema_id="schema1",
            schema_version="1.0",
            source_layer="L0",
            target_layer="L1",
            validation_status=SchemaValidationStatus.INVALID,
        )
        with pytest.raises(boundary_contracts.BoundarySchemaError, match="is INVALID"):
            boundary_contracts.validate_boundary_schema(descriptor)

    def test_validate_boundary_schema_missing(self):
        """Test boundary schema validation fails for missing schema."""
        descriptor = BoundarySchemaDescriptor(
            schema_id="schema1",
            schema_version="1.0",
            source_layer="L0",
            target_layer="L1",
            validation_status=SchemaValidationStatus.MISSING,
        )
        with pytest.raises(boundary_contracts.BoundarySchemaError, match="is MISSING"):
            boundary_contracts.validate_boundary_schema(descriptor)

    def test_validate_boundary_schema_wrong_type(self):
        """Test boundary schema validation fails on wrong type."""
        with pytest.raises(boundary_contracts.BoundarySchemaError, match="Expected BoundarySchemaDescriptor"):
            boundary_contracts.validate_boundary_schema("not a descriptor")

    def test_build_boundary_schema_valid(self):
        """Test building boundary schema descriptor (valid)."""
        descriptor = boundary_contracts.build_boundary_schema(
            schema_id="schema1",
            schema_version="1.0",
            source_layer="L0",
            target_layer="L1",
            known_schemas={"schema1": "1.0"},
        )
        
        assert descriptor.validation_status == SchemaValidationStatus.VALID

    def test_build_boundary_schema_missing(self):
        """Test building boundary schema descriptor (missing)."""
        descriptor = boundary_contracts.build_boundary_schema(
            schema_id="schema1",
            schema_version="1.0",
            source_layer="L0",
            target_layer="L1",
            known_schemas={},  # Schema not in known_schemas
        )
        
        assert descriptor.validation_status == SchemaValidationStatus.MISSING

    def test_build_boundary_schema_version_mismatch(self):
        """Test building boundary schema descriptor (version mismatch)."""
        descriptor = boundary_contracts.build_boundary_schema(
            schema_id="schema1",
            schema_version="2.0",
            source_layer="L0",
            target_layer="L1",
            known_schemas={"schema1": "1.0"},  # Version mismatch
        )
        
        assert descriptor.validation_status == SchemaValidationStatus.INVALID

    def test_assert_cross_run_pins_pass(self):
        """Test cross-run pins assertion when values match."""
        check, violation = boundary_contracts.assert_cross_run_pins(
            discovery_hash="hash1",
            expected_discovery_hash="hash1",
            schema_version="1.0",
            expected_schema_version="1.0",
        )
        
        assert check.passed is True
        assert violation is None

    def test_assert_cross_run_pins_discovery_mismatch(self):
        """Test cross-run pins assertion on discovery hash mismatch."""
        check, violation = boundary_contracts.assert_cross_run_pins(
            discovery_hash="hash1",
            expected_discovery_hash="hash2",
            schema_version="1.0",
            expected_schema_version="1.0",
        )
        
        assert check.passed is False
        assert violation is not None
        assert violation.severity == InvariantSeverity.CRITICAL

    def test_assert_cross_run_pins_schema_mismatch(self):
        """Test cross-run pins assertion on schema version mismatch."""
        check, violation = boundary_contracts.assert_cross_run_pins(
            discovery_hash="hash1",
            expected_discovery_hash="hash1",
            schema_version="2.0",
            expected_schema_version="1.0",
        )
        
        assert check.passed is False
        assert violation is not None
        assert violation.severity == InvariantSeverity.CRITICAL

    def test_assert_chain_closure_pass(self):
        """Test chain closure assertion when artifacts match."""
        expected = frozenset(["artifact1", "artifact2"])
        actual = frozenset(["artifact1", "artifact2"])
        
        check, violation = boundary_contracts.assert_chain_closure(expected, actual)
        
        assert check.passed is True
        assert violation is None

    def test_assert_chain_closure_missing(self):
        """Test chain closure assertion on missing artifacts."""
        expected = frozenset(["artifact1", "artifact2", "artifact3"])
        actual = frozenset(["artifact1", "artifact2"])
        
        check, violation = boundary_contracts.assert_chain_closure(expected, actual)
        
        assert check.passed is False
        assert violation is not None
        assert violation.severity == InvariantSeverity.HIGH

    def test_assert_chain_closure_orphans(self):
        """Test chain closure assertion on orphan artifacts."""
        expected = frozenset(["artifact1", "artifact2"])
        actual = frozenset(["artifact1", "artifact2", "artifact3"])
        
        check, violation = boundary_contracts.assert_chain_closure(expected, actual)
        
        assert check.passed is False
        assert violation is not None
        assert violation.severity == InvariantSeverity.HIGH

    def test_run_meta_invariants_pass(self):
        """Test running meta-invariants when all pass."""
        report = boundary_contracts.run_meta_invariants(
            trace_id="trace123",
            run_id="run1",
            semantic_clock_tick=42,
            discovery_hash="hash1",
            expected_discovery_hash="hash1",
            schema_version="1.0",
            expected_schema_version="1.0",
            expected_artifacts=frozenset(["artifact1"]),
            actual_artifacts=frozenset(["artifact1"]),
        )
        
        assert isinstance(report, MetaInvariantReport)
        assert report.pass_fail is True
        assert len(report.violations) == 0

    def test_run_meta_invariants_fail(self):
        """Test running meta-invariants when checks fail."""
        report = boundary_contracts.run_meta_invariants(
            trace_id="trace123",
            run_id="run1",
            semantic_clock_tick=42,
            discovery_hash="hash1",
            expected_discovery_hash="hash2",  # Mismatch
            schema_version="1.0",
            expected_schema_version="1.0",
            expected_artifacts=frozenset(["artifact1"]),
            actual_artifacts=frozenset(["artifact2"]),  # Mismatch
        )
        
        assert isinstance(report, MetaInvariantReport)
        assert report.pass_fail is False
        assert len(report.violations) > 0

    def test_fail_closed_on_violation_pass(self):
        """Test fail_closed on violation when report passes."""
        report = MetaInvariantReport(
            trace_id="trace123",
            run_id="run1",
            semantic_clock_tick=42,
            checks=(),
            pass_fail=True,
            violations=(),
        )
        result = boundary_contracts.fail_closed_on_violation(report)
        assert result is True

    def test_fail_closed_on_violation_fail(self):
        """Test fail_closed on violation raises when report fails."""
        report = MetaInvariantReport(
            trace_id="trace123",
            run_id="run1",
            semantic_clock_tick=42,
            checks=(),
            pass_fail=False,
            violations=(InvariantViolation(
                invariant_id="test",
                severity=InvariantSeverity.HIGH,
                evidence_paths=(),
                details="test violation",
            ),),
        )
        
        with pytest.raises(boundary_contracts.MetaInvariantError, match="Meta-invariant violations detected"):
            boundary_contracts.fail_closed_on_violation(report)

    def test_public_api_exports(self):
        """Test that public API functions are exported."""
        assert hasattr(boundary_contracts, "resolve_ssot_binding")
        assert hasattr(boundary_contracts, "build_context_retrieval_request")
        assert hasattr(boundary_contracts, "validate_context_retrieval_read_only")
        assert hasattr(boundary_contracts, "validate_boundary_schema")
        assert hasattr(boundary_contracts, "build_boundary_schema")
        assert hasattr(boundary_contracts, "assert_cross_run_pins")
        assert hasattr(boundary_contracts, "assert_chain_closure")
        assert hasattr(boundary_contracts, "run_meta_invariants")
        assert hasattr(boundary_contracts, "fail_closed_on_violation")
