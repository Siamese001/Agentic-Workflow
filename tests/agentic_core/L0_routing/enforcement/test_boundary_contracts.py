"""Tests for boundary_contracts.py module."""

from __future__ import annotations

import pytest

from agentic_core.L0_routing.enforcement.boundary_contracts import (
    SSOTBindingError,
    resolve_ssot_binding,
    ContextRetrievalError,
    build_context_retrieval_request,
    validate_context_retrieval_read_only,
    BoundarySchemaError,
    validate_boundary_schema,
    build_boundary_schema,
    MetaInvariantError,
    assert_cross_run_pins,
    assert_chain_closure,
    run_meta_invariants,
    fail_closed_on_violation,
)
from agentic_core.L0_routing.types.boundary_types import (
    SSOTBinding,
    ContextRetrievalRequest,
    BoundarySchemaDescriptor,
    SchemaValidationStatus,
    InvariantCheck,
    InvariantViolation,
    InvariantSeverity,
    MetaInvariantReport,
)


class TestSSOTBindingResolution:
    """Tests for SSOT binding resolution functions."""

    def test_resolve_ssot_binding_success(self):
        """Test resolve_ssot_binding with valid node_id."""
        registry = {"node1": "entry1", "node2": "entry2"}
        binding = resolve_ssot_binding("node1", registry)
        assert binding.node_id == "node1"
        assert binding.blueprint_entry == "entry1"
        assert binding.resolved is True

    def test_resolve_ssot_binding_empty_node_id(self):
        """Test resolve_ssot_binding raises error for empty node_id."""
        registry = {"node1": "entry1"}
        with pytest.raises(SSOTBindingError, match="node_id must be non-empty"):
            resolve_ssot_binding("", registry)

    def test_resolve_ssot_binding_unresolved(self):
        """Test resolve_ssot_binding raises error for unresolved node_id."""
        registry = {"node1": "entry1"}
        with pytest.raises(SSOTBindingError, match="does not resolve"):
            resolve_ssot_binding("unknown_node", registry)


class TestContextRetrievalRequest:
    """Tests for context retrieval request functions."""

    def test_build_context_retrieval_request_success(self):
        """Test build_context_retrieval_request with valid inputs."""
        request = build_context_retrieval_request("trace-123", "hash-abc", 1)
        assert request.trace_id == "trace-123"
        assert request.query_hash == "hash-abc"
        assert request.semantic_clock_tick == 1

    def test_build_context_retrieval_request_invalid_type_error(self):
        """Test build_context_retrieval_request raises ContextRetrievalError on type error."""
        with pytest.raises(ContextRetrievalError, match="ContextRetrievalRequest construction failed"):
            build_context_retrieval_request(123, "hash-abc", 1)

    def test_validate_context_retrieval_read_only_true(self):
        """Test validate_context_retrieval_read_only with read-only request."""
        request = ContextRetrievalRequest(
            trace_id="trace-123",
            query_hash="hash-abc",
            semantic_clock_tick=1,
            read_only=True,
        )
        assert validate_context_retrieval_read_only(request) is True

    def test_validate_context_retrieval_read_only_false(self):
        """Test validate_context_retrieval_read_only raises error for non-read-only."""
        request = ContextRetrievalRequest(
            trace_id="trace-123",
            query_hash="hash-abc",
            semantic_clock_tick=1,
            read_only=False,
        )
        with pytest.raises(ContextRetrievalError, match="must be read-only"):
            validate_context_retrieval_read_only(request)


class TestBoundarySchemaValidation:
    """Tests for boundary schema validation functions."""

    def test_validate_boundary_schema_valid(self):
        """Test validate_boundary_schema with valid descriptor."""
        descriptor = BoundarySchemaDescriptor(
            schema_id="schema1",
            schema_version="1.0",
            source_layer="L0_routing",
            target_layer="L1_cognition",
            validation_status=SchemaValidationStatus.VALID,
        )
        assert validate_boundary_schema(descriptor) is True

    def test_validate_boundary_schema_invalid_type(self):
        """Test validate_boundary_schema raises error for invalid type."""
        with pytest.raises(BoundarySchemaError, match="Expected BoundarySchemaDescriptor"):
            validate_boundary_schema("not_a_descriptor")

    def test_validate_boundary_schema_invalid_status(self):
        """Test validate_boundary_schema raises error for INVALID status."""
        descriptor = BoundarySchemaDescriptor(
            schema_id="schema1",
            schema_version="1.0",
            source_layer="L0_routing",
            target_layer="L1_cognition",
            validation_status=SchemaValidationStatus.INVALID,
        )
        with pytest.raises(BoundarySchemaError, match="is INVALID"):
            validate_boundary_schema(descriptor)

    def test_validate_boundary_schema_missing_status(self):
        """Test validate_boundary_schema raises error for MISSING status."""
        descriptor = BoundarySchemaDescriptor(
            schema_id="schema1",
            schema_version="1.0",
            source_layer="L0_routing",
            target_layer="L1_cognition",
            validation_status=SchemaValidationStatus.MISSING,
        )
        with pytest.raises(BoundarySchemaError, match="is MISSING"):
            validate_boundary_schema(descriptor)

    def test_build_boundary_schema_valid(self):
        """Test build_boundary_schema with valid inputs."""
        descriptor = build_boundary_schema(
            schema_id="schema1",
            schema_version="1.0",
            source_layer="L0_routing",
            target_layer="L1_cognition",
        )
        assert descriptor.schema_id == "schema1"
        assert descriptor.validation_status == SchemaValidationStatus.VALID

    def test_build_boundary_schema_missing_schema(self):
        """Test build_boundary_schema with unknown schema returns MISSING."""
        known_schemas = {"schema1": "1.0"}
        descriptor = build_boundary_schema(
            schema_id="unknown_schema",
            schema_version="1.0",
            source_layer="L0_routing",
            target_layer="L1_cognition",
            known_schemas=known_schemas,
        )
        assert descriptor.validation_status == SchemaValidationStatus.MISSING

    def test_build_boundary_schema_version_mismatch(self):
        """Test build_boundary_schema with version mismatch returns INVALID."""
        known_schemas = {"schema1": "1.0"}
        descriptor = build_boundary_schema(
            schema_id="schema1",
            schema_version="2.0",
            source_layer="L0_routing",
            target_layer="L1_cognition",
            known_schemas=known_schemas,
        )
        assert descriptor.validation_status == SchemaValidationStatus.INVALID


class TestMetaInvariantChecks:
    """Tests for meta-invariant check functions."""

    def test_assert_cross_run_pins_passed(self):
        """Test assert_cross_run_pins when values match."""
        check, violation = assert_cross_run_pins(
            discovery_hash="hash1",
            expected_discovery_hash="hash1",
            schema_version="1.0",
            expected_schema_version="1.0",
        )
        assert check.passed is True
        assert violation is None

    def test_assert_cross_run_pins_discovery_mismatch(self):
        """Test assert_cross_run_pins with discovery hash mismatch."""
        check, violation = assert_cross_run_pins(
            discovery_hash="hash2",
            expected_discovery_hash="hash1",
            schema_version="1.0",
            expected_schema_version="1.0",
        )
        assert check.passed is False
        assert violation is not None
        assert violation.severity == InvariantSeverity.CRITICAL

    def test_assert_cross_run_pins_schema_mismatch(self):
        """Test assert_cross_run_pins with schema version mismatch."""
        check, violation = assert_cross_run_pins(
            discovery_hash="hash1",
            expected_discovery_hash="hash1",
            schema_version="2.0",
            expected_schema_version="1.0",
        )
        assert check.passed is False
        assert violation is not None
        assert violation.severity == InvariantSeverity.CRITICAL

    def test_assert_chain_closure_passed(self):
        """Test assert_chain_closure when artifacts match."""
        expected = frozenset(["artifact1", "artifact2"])
        actual = frozenset(["artifact1", "artifact2"])
        check, violation = assert_chain_closure(expected, actual)
        assert check.passed is True
        assert violation is None

    def test_assert_chain_closure_missing_artifacts(self):
        """Test assert_chain_closure with missing artifacts."""
        expected = frozenset(["artifact1", "artifact2", "artifact3"])
        actual = frozenset(["artifact1", "artifact2"])
        check, violation = assert_chain_closure(expected, actual)
        assert check.passed is False
        assert violation is not None
        assert violation.severity == InvariantSeverity.HIGH

    def test_assert_chain_closure_orphan_artifacts(self):
        """Test assert_chain_closure with orphan artifacts."""
        expected = frozenset(["artifact1"])
        actual = frozenset(["artifact1", "artifact2"])
        check, violation = assert_chain_closure(expected, actual)
        assert check.passed is False
        assert violation is not None
        assert violation.severity == InvariantSeverity.HIGH


class TestRunMetaInvariants:
    """Tests for run_meta_invariants function."""

    def test_run_meta_invariants_all_passed(self):
        """Test run_meta_invariants when all checks pass."""
        report = run_meta_invariants(
            trace_id="trace-123",
            run_id="run-123",
            semantic_clock_tick=1,
            discovery_hash="hash1",
            expected_discovery_hash="hash1",
            schema_version="1.0",
            expected_schema_version="1.0",
            expected_artifacts=frozenset(["artifact1"]),
            actual_artifacts=frozenset(["artifact1"]),
        )
        assert report.pass_fail is True
        assert len(report.checks) == 2
        assert len(report.violations) == 0

    def test_run_meta_invariants_with_violations(self):
        """Test run_meta_invariants when checks fail."""
        report = run_meta_invariants(
            trace_id="trace-123",
            run_id="run-123",
            semantic_clock_tick=1,
            discovery_hash="hash2",
            expected_discovery_hash="hash1",
            schema_version="2.0",
            expected_schema_version="1.0",
            expected_artifacts=frozenset(["artifact1"]),
            actual_artifacts=frozenset(["artifact1", "artifact2"]),
        )
        assert report.pass_fail is False
        assert len(report.checks) == 2
        assert len(report.violations) == 2

    def test_run_meta_invariants_report_structure(self):
        """Test run_meta_invariants report structure."""
        report = run_meta_invariants(
            trace_id="trace-123",
            run_id="run-123",
            semantic_clock_tick=1,
            discovery_hash="hash1",
            expected_discovery_hash="hash1",
            schema_version="1.0",
            expected_schema_version="1.0",
            expected_artifacts=frozenset(),
            actual_artifacts=frozenset(),
        )
        assert report.trace_id == "trace-123"
        assert report.run_id == "run-123"
        assert report.semantic_clock_tick == 1
        assert isinstance(report.checks, tuple)
        assert isinstance(report.violations, tuple)


class TestFailClosedOnViolation:
    """Tests for fail_closed_on_violation function."""

    def test_fail_closed_on_violation_passed(self):
        """Test fail_closed_on_violation with passing report."""
        report = MetaInvariantReport(
            trace_id="trace-123",
            run_id="run-123",
            semantic_clock_tick=1,
            checks=(),
            pass_fail=True,
            violations=(),
        )
        assert fail_closed_on_violation(report) is True

    def test_fail_closed_on_violation_raises(self):
        """Test fail_closed_on_violation raises error on violations."""
        report = MetaInvariantReport(
            trace_id="trace-123",
            run_id="run-123",
            semantic_clock_tick=1,
            checks=(),
            pass_fail=False,
            violations=(InvariantViolation(
                invariant_id="test",
                severity=InvariantSeverity.HIGH,
                evidence_paths=(),
                details="test violation",
            ),),
        )
        with pytest.raises(MetaInvariantError, match="Meta-invariant violations"):
            fail_closed_on_violation(report)
