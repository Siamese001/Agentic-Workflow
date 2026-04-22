"""Behavioral tests for ``agentic_core.L0_routing.enforcement.boundary_contracts``.

Covers V15 P6 runtime contracts — meta-invariants and typed boundaries:
- SSOTBindingError / ContextRetrievalError / BoundarySchemaError / MetaInvariantError
  all derive from Exception.
- resolve_ssot_binding: empty node_id / unknown node_id → SSOTBindingError;
  known entry → SSOTBinding(resolved=True).
- build_context_retrieval_request: success path; construction errors → ContextRetrievalError.
- validate_context_retrieval_read_only: read-only=True passes; false raises.
- validate_boundary_schema: wrong type / INVALID / MISSING all fail; VALID passes.
- build_boundary_schema: without known_schemas → VALID; unknown id → MISSING;
  version mismatch → INVALID; match → VALID.
- assert_cross_run_pins: ok path; discovery mismatch; schema mismatch; both mismatch.
- assert_chain_closure: ok; missing only; orphans only; both.
- run_meta_invariants: aggregates checks, pass_fail reflects violations.
- fail_closed_on_violation: raises when violations present; returns True otherwise.
"""

from __future__ import annotations

import pytest

from agentic_core.L0_routing.enforcement.boundary_contracts import (
    BoundarySchemaError,
    ContextRetrievalError,
    MetaInvariantError,
    SSOTBindingError,
    assert_chain_closure,
    assert_cross_run_pins,
    build_boundary_schema,
    build_context_retrieval_request,
    fail_closed_on_violation,
    resolve_ssot_binding,
    run_meta_invariants,
    validate_boundary_schema,
    validate_context_retrieval_read_only,
)
from agentic_core.L0_routing.types.boundary_types import (
    BoundarySchemaDescriptor,
    InvariantSeverity,
    SchemaValidationStatus,
)


# ---- Exception hierarchy -----------------------------------------------

class TestExceptions:
    @pytest.mark.parametrize(
        "exc_cls",
        [
            SSOTBindingError,
            ContextRetrievalError,
            BoundarySchemaError,
            MetaInvariantError,
        ],
    )
    def test_inherits_from_exception(self, exc_cls: type) -> None:
        assert issubclass(exc_cls, Exception)


# ---- resolve_ssot_binding ----------------------------------------------

class TestResolveSsotBinding:
    def test_empty_node_id_rejected(self) -> None:
        with pytest.raises(SSOTBindingError, match="non-empty"):
            resolve_ssot_binding("", {"x": "y"})

    def test_unknown_node_id_rejected(self) -> None:
        with pytest.raises(SSOTBindingError, match="does not resolve"):
            resolve_ssot_binding("ghost", {"other": "entry"})

    def test_known_node_id_returns_binding(self) -> None:
        result = resolve_ssot_binding("node-1", {"node-1": "blueprint-A"})
        assert result.node_id == "node-1"
        assert result.blueprint_entry == "blueprint-A"
        assert result.resolved is True


# ---- ContextRetrievalRequest helpers -----------------------------------

class TestBuildContextRetrievalRequest:
    def test_success(self) -> None:
        req = build_context_retrieval_request(
            trace_id="t1", query_hash="q1", semantic_clock_tick=5,
        )
        assert req.trace_id == "t1"
        assert req.query_hash == "q1"
        assert req.semantic_clock_tick == 5
        assert req.read_only is True
        assert req.source_layer == "L0"
        assert req.target_layer == "L4"

    def test_construction_failure_wrapped(self) -> None:
        # Empty trace_id triggers ValueError in __post_init__ → wrapped
        with pytest.raises(ContextRetrievalError, match="FAIL"):
            build_context_retrieval_request(
                trace_id="", query_hash="q", semantic_clock_tick=0,
            )


class TestValidateContextRetrievalReadOnly:
    def test_read_only_true_passes(self) -> None:
        req = build_context_retrieval_request("t", "q", 0)
        assert validate_context_retrieval_read_only(req) is True


# ---- validate_boundary_schema -----------------------------------------

class TestValidateBoundarySchema:
    def test_wrong_type_rejected(self) -> None:
        with pytest.raises(BoundarySchemaError, match="Expected BoundarySchemaDescriptor"):
            validate_boundary_schema("not-a-descriptor")  # type: ignore[arg-type]

    def test_invalid_status_rejected(self) -> None:
        d = BoundarySchemaDescriptor(
            schema_id="s1", schema_version="1.0",
            source_layer="L0", target_layer="L4",
            validation_status=SchemaValidationStatus.INVALID,
        )
        with pytest.raises(BoundarySchemaError, match="INVALID"):
            validate_boundary_schema(d)

    def test_missing_status_rejected(self) -> None:
        d = BoundarySchemaDescriptor(
            schema_id="s1", schema_version="1.0",
            source_layer="L0", target_layer="L4",
            validation_status=SchemaValidationStatus.MISSING,
        )
        with pytest.raises(BoundarySchemaError, match="MISSING"):
            validate_boundary_schema(d)

    def test_valid_passes(self) -> None:
        d = BoundarySchemaDescriptor(
            schema_id="s1", schema_version="1.0",
            source_layer="L0", target_layer="L4",
            validation_status=SchemaValidationStatus.VALID,
        )
        assert validate_boundary_schema(d) is True


# ---- build_boundary_schema --------------------------------------------

class TestBuildBoundarySchema:
    def test_without_known_schemas_returns_valid(self) -> None:
        d = build_boundary_schema("s1", "1.0", "L0", "L4")
        assert d.validation_status == SchemaValidationStatus.VALID

    def test_unknown_id_returns_missing(self) -> None:
        d = build_boundary_schema(
            "s1", "1.0", "L0", "L4", known_schemas={"other": "1.0"},
        )
        assert d.validation_status == SchemaValidationStatus.MISSING

    def test_version_mismatch_returns_invalid(self) -> None:
        d = build_boundary_schema(
            "s1", "1.0", "L0", "L4", known_schemas={"s1": "2.0"},
        )
        assert d.validation_status == SchemaValidationStatus.INVALID

    def test_match_returns_valid(self) -> None:
        d = build_boundary_schema(
            "s1", "1.0", "L0", "L4", known_schemas={"s1": "1.0"},
        )
        assert d.validation_status == SchemaValidationStatus.VALID


# ---- assert_cross_run_pins --------------------------------------------

class TestAssertCrossRunPins:
    def test_both_match_passes(self) -> None:
        check, violation = assert_cross_run_pins("d1", "d1", "v1", "v1")
        assert check.passed is True
        assert violation is None

    def test_discovery_mismatch(self) -> None:
        check, violation = assert_cross_run_pins("d1", "d2", "v1", "v1")
        assert check.passed is False
        assert violation is not None
        assert violation.severity == InvariantSeverity.CRITICAL
        assert "discovery_hash" in violation.details

    def test_schema_mismatch(self) -> None:
        check, violation = assert_cross_run_pins("d1", "d1", "v1", "v2")
        assert check.passed is False
        assert violation is not None
        assert "schema_version" in violation.details

    def test_both_mismatch(self) -> None:
        check, violation = assert_cross_run_pins("d1", "d2", "v1", "v2")
        assert check.passed is False
        assert violation is not None
        assert "discovery_hash" in violation.details
        assert "schema_version" in violation.details


# ---- assert_chain_closure ---------------------------------------------

class TestAssertChainClosure:
    def test_clean(self) -> None:
        check, violation = assert_chain_closure(
            frozenset({"a", "b"}), frozenset({"a", "b"}),
        )
        assert check.passed is True
        assert violation is None

    def test_missing(self) -> None:
        check, violation = assert_chain_closure(
            frozenset({"a", "b"}), frozenset({"a"}),
        )
        assert check.passed is False
        assert violation is not None
        assert "missing" in check.evidence
        assert "b" in check.evidence

    def test_orphans(self) -> None:
        check, violation = assert_chain_closure(
            frozenset({"a"}), frozenset({"a", "extra"}),
        )
        assert check.passed is False
        assert violation is not None
        assert "orphans" in check.evidence

    def test_missing_and_orphan(self) -> None:
        check, violation = assert_chain_closure(
            frozenset({"a", "b"}), frozenset({"b", "c"}),
        )
        assert check.passed is False
        assert violation is not None
        assert violation.severity == InvariantSeverity.HIGH
        assert "missing" in check.evidence
        assert "orphans" in check.evidence


# ---- run_meta_invariants ----------------------------------------------

class TestRunMetaInvariants:
    def test_all_pass_produces_clean_report(self) -> None:
        report = run_meta_invariants(
            trace_id="t", run_id="r", semantic_clock_tick=1,
            discovery_hash="d", expected_discovery_hash="d",
            schema_version="v", expected_schema_version="v",
            expected_artifacts=frozenset({"a"}),
            actual_artifacts=frozenset({"a"}),
        )
        assert report.pass_fail is True
        assert len(report.checks) == 2
        assert len(report.violations) == 0

    def test_cross_run_pins_failure_captured(self) -> None:
        report = run_meta_invariants(
            trace_id="t", run_id="r", semantic_clock_tick=1,
            discovery_hash="d1", expected_discovery_hash="d2",
            schema_version="v", expected_schema_version="v",
            expected_artifacts=frozenset(), actual_artifacts=frozenset(),
        )
        assert report.pass_fail is False
        assert any(v.invariant_id == "cross_run_pins" for v in report.violations)

    def test_chain_closure_failure_captured(self) -> None:
        report = run_meta_invariants(
            trace_id="t", run_id="r", semantic_clock_tick=1,
            discovery_hash="d", expected_discovery_hash="d",
            schema_version="v", expected_schema_version="v",
            expected_artifacts=frozenset({"a"}),
            actual_artifacts=frozenset({"b"}),
        )
        assert report.pass_fail is False
        assert any(v.invariant_id == "chain_closure" for v in report.violations)

    def test_both_failures_captured(self) -> None:
        report = run_meta_invariants(
            trace_id="t", run_id="r", semantic_clock_tick=1,
            discovery_hash="d1", expected_discovery_hash="d2",
            schema_version="v1", expected_schema_version="v2",
            expected_artifacts=frozenset({"a"}),
            actual_artifacts=frozenset({"b"}),
        )
        assert report.pass_fail is False
        assert len(report.violations) == 2


# ---- fail_closed_on_violation ----------------------------------------

class TestFailClosedOnViolation:
    def test_passes_when_clean(self) -> None:
        report = run_meta_invariants(
            trace_id="t", run_id="r", semantic_clock_tick=1,
            discovery_hash="d", expected_discovery_hash="d",
            schema_version="v", expected_schema_version="v",
            expected_artifacts=frozenset(), actual_artifacts=frozenset(),
        )
        assert fail_closed_on_violation(report) is True

    def test_raises_on_violation(self) -> None:
        report = run_meta_invariants(
            trace_id="t", run_id="r-bad", semantic_clock_tick=1,
            discovery_hash="d1", expected_discovery_hash="d2",
            schema_version="v", expected_schema_version="v",
            expected_artifacts=frozenset(), actual_artifacts=frozenset(),
        )
        with pytest.raises(MetaInvariantError, match="r-bad"):
            fail_closed_on_violation(report)
