"""
V15 P6 Compliance Tests — Meta-Invariants & Typed Boundaries.

Regression tests proving all 4 P6 items + meta-governor are COMPLIANT:
  §1.5  — SSOT Binding (node_id resolves to structure_blueprint)
  §3.8  — Context Retrieval Request Artifact (L0→L4, read-only)
  §12.1 — Inter-agent schema validation
  §2.4  — Boundary schema validation
  META  — MetaInvariantReport + fail_closed_on_violation
"""

from __future__ import annotations

import dataclasses

import pytest

from agentic_core.L0_routing.enforcement.boundary_contracts import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

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
    ContextRetrievalRequest,
    InvariantCheck,
    InvariantSeverity,
    InvariantViolation,
    MetaInvariantReport,
    SchemaValidationStatus,
    SSOTBinding,
)

# ---- fixtures ---------------------------------------------------------------

SAMPLE_BLUEPRINT = {
    "module.StructureHealerAgent.heal_repository": "L5_safety/reasoning/StructureHealerAgent",
    "module.CodeHealerAgent.heal_all": "L5_safety/reasoning/CodeHealerAgent",
}

KNOWN_SCHEMAS = {
    "surgical_manifest_v1": "1.0.0",
    "evidence_pack_v1": "1.0.0",
    "boundary_snapshot_v1": "1.0.0",
}

PINNED_DISCOVERY_HASH = "f09ec166b82746f6d62cf1c7e9215de70ec29534f784bee95d13798b04da4fd4"
PINNED_SCHEMA_VERSION = "1.3.0"

EXPECTED_ARTIFACTS = frozenset(
    {
        "SurgicalManifest",
        "EvidencePack",
        "PolicyExceptionArtifact",
        "PolicyUpdateProposal",
        "SignatureEnvelope",
        "CognitiveDiffBundle",
    },
)


# =============================================================================
# §1.5 — SSOT Binding
# =============================================================================


class TestP6_15_SSOTBinding:
    """§1.5: node_id resolves to a valid SSOT definition."""

    def test_all_required_fields(self):
        required = {"node_id", "blueprint_entry", "resolved"}
        actual = {f.name for f in dataclasses.fields(SSOTBinding)}
        assert required.issubset(actual)

    def test_frozen(self):
        binding = resolve_ssot_binding(
            "module.StructureHealerAgent.heal_repository",
            SAMPLE_BLUEPRINT,
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            binding.node_id = "x"  # type: ignore[misc]

    def test_resolves_valid_node(self):
        binding = resolve_ssot_binding(
            "module.StructureHealerAgent.heal_repository",
            SAMPLE_BLUEPRINT,
        )
        assert binding.resolved is True
        assert "StructureHealerAgent" in binding.blueprint_entry

    def test_unresolved_node_fails(self):
        with pytest.raises(SSOTBindingError, match="does not resolve"):
            resolve_ssot_binding("nonexistent.node", SAMPLE_BLUEPRINT)

    def test_empty_node_id_fails(self):
        with pytest.raises(SSOTBindingError, match="non-empty"):
            resolve_ssot_binding("", SAMPLE_BLUEPRINT)


# =============================================================================
# §3.8 — Context Retrieval Request
# =============================================================================


class TestP6_38_ContextRetrievalRequest:
    """§3.8: Typed L0→L4 request, advisory-only, read-only."""

    def test_all_required_fields(self):
        required = {"trace_id", "query_hash", "semantic_clock_tick"}
        actual = {f.name for f in dataclasses.fields(ContextRetrievalRequest)}
        assert required.issubset(actual)

    def test_frozen(self):
        req = build_context_retrieval_request("t1", "hash123", 5)
        with pytest.raises(dataclasses.FrozenInstanceError):
            req.trace_id = "x"  # type: ignore[misc]

    def test_builds_valid(self):
        req = build_context_retrieval_request("t1", "hash123", 5)
        assert req.source_layer == "L0"
        assert req.target_layer == "L4"
        assert req.read_only is True

    def test_empty_trace_id_rejected(self):
        with pytest.raises(ContextRetrievalError, match="FAIL"):
            build_context_retrieval_request("", "hash", 0)

    def test_empty_query_hash_rejected(self):
        with pytest.raises(ContextRetrievalError, match="FAIL"):
            build_context_retrieval_request("t1", "", 0)

    def test_negative_tick_rejected(self):
        with pytest.raises(ContextRetrievalError, match="FAIL"):
            build_context_retrieval_request("t1", "hash", -1)

    def test_read_only_enforced(self):
        req = build_context_retrieval_request("t1", "hash", 0)
        assert validate_context_retrieval_read_only(req) is True

    def test_write_attempt_rejected(self):
        # Construct with read_only=False via direct init to bypass default
        with pytest.raises(ValueError, match="read_only"):
            ContextRetrievalRequest(
                trace_id="t1",
                query_hash="h",
                semantic_clock_tick=0,
                read_only=False,
            )


# =============================================================================
# §12.1 / §2.4 — Boundary Schema Validation
# =============================================================================


class TestP6_121_BoundarySchemaValidation:
    """§12.1 / §2.4: Inter-agent schema validation, typed boundaries."""

    def test_all_required_fields(self):
        required = {
            "schema_id",
            "schema_version",
            "source_layer",
            "target_layer",
            "validation_status",
        }
        actual = {f.name for f in dataclasses.fields(BoundarySchemaDescriptor)}
        assert required.issubset(actual)

    def test_frozen(self):
        desc = build_boundary_schema("s1", "1.0.0", "L0", "L2", KNOWN_SCHEMAS)
        with pytest.raises(dataclasses.FrozenInstanceError):
            desc.schema_id = "x"  # type: ignore[misc]

    def test_valid_schema_passes(self):
        desc = build_boundary_schema(
            "surgical_manifest_v1",
            "1.0.0",
            "L2",
            "L5",
            KNOWN_SCHEMAS,
        )
        assert desc.validation_status == SchemaValidationStatus.VALID
        assert validate_boundary_schema(desc) is True

    def test_missing_schema_detected(self):
        desc = build_boundary_schema(
            "unknown_schema",
            "1.0.0",
            "L0",
            "L4",
            KNOWN_SCHEMAS,
        )
        assert desc.validation_status == SchemaValidationStatus.MISSING

    def test_missing_schema_fails_validation(self):
        desc = build_boundary_schema(
            "unknown_schema",
            "1.0.0",
            "L0",
            "L4",
            KNOWN_SCHEMAS,
        )
        with pytest.raises(BoundarySchemaError, match="MISSING"):
            validate_boundary_schema(desc)

    def test_version_mismatch_detected(self):
        desc = build_boundary_schema(
            "surgical_manifest_v1",
            "2.0.0",
            "L2",
            "L5",
            KNOWN_SCHEMAS,
        )
        assert desc.validation_status == SchemaValidationStatus.INVALID

    def test_version_mismatch_fails_validation(self):
        desc = build_boundary_schema(
            "surgical_manifest_v1",
            "2.0.0",
            "L2",
            "L5",
            KNOWN_SCHEMAS,
        )
        with pytest.raises(BoundarySchemaError, match="INVALID"):
            validate_boundary_schema(desc)

    def test_no_registry_defaults_valid(self):
        desc = build_boundary_schema("any", "1.0.0", "L0", "L2")
        assert desc.validation_status == SchemaValidationStatus.VALID

    def test_non_descriptor_rejected(self):
        with pytest.raises(BoundarySchemaError, match="dict"):
            validate_boundary_schema({"schema_id": "x"})  # type: ignore[arg-type]

    def test_empty_schema_id_rejected(self):
        with pytest.raises(ValueError, match="schema_id"):
            BoundarySchemaDescriptor(
                schema_id="",
                schema_version="1.0",
                source_layer="L0",
                target_layer="L2",
                validation_status=SchemaValidationStatus.VALID,
            )


# =============================================================================
# Meta-Governor: Cross-Run Pins
# =============================================================================


class TestP6_MetaCrossRunPins:
    """Meta-governor: cross-run pinned values."""

    def test_matching_pins_pass(self):
        check, violation = assert_cross_run_pins(
            PINNED_DISCOVERY_HASH,
            PINNED_DISCOVERY_HASH,
            PINNED_SCHEMA_VERSION,
            PINNED_SCHEMA_VERSION,
        )
        assert check.passed is True
        assert violation is None

    def test_discovery_hash_mismatch_fails(self):
        check, violation = assert_cross_run_pins(
            "wrong_hash",
            PINNED_DISCOVERY_HASH,
            PINNED_SCHEMA_VERSION,
            PINNED_SCHEMA_VERSION,
        )
        assert check.passed is False
        assert violation is not None
        assert violation.severity == InvariantSeverity.CRITICAL
        assert "discovery_hash" in violation.details

    def test_schema_version_mismatch_fails(self):
        check, violation = assert_cross_run_pins(
            PINNED_DISCOVERY_HASH,
            PINNED_DISCOVERY_HASH,
            "9.9.9",
            PINNED_SCHEMA_VERSION,
        )
        assert check.passed is False
        assert violation is not None
        assert "schema_version" in violation.details

    def test_both_mismatch_captures_both(self):
        check, violation = assert_cross_run_pins(
            "wrong",
            PINNED_DISCOVERY_HASH,
            "wrong",
            PINNED_SCHEMA_VERSION,
        )
        assert check.passed is False
        assert violation is not None
        assert "discovery_hash" in violation.details
        assert "schema_version" in violation.details


# =============================================================================
# Meta-Governor: Chain Closure
# =============================================================================


class TestP6_MetaChainClosure:
    """Meta-governor: artifact chain closure detection."""

    def test_matching_sets_pass(self):
        check, violation = assert_chain_closure(
            EXPECTED_ARTIFACTS,
            EXPECTED_ARTIFACTS,
        )
        assert check.passed is True
        assert violation is None

    def test_missing_artifact_detected(self):
        actual = EXPECTED_ARTIFACTS - {"EvidencePack"}
        check, violation = assert_chain_closure(EXPECTED_ARTIFACTS, actual)
        assert check.passed is False
        assert violation is not None
        assert "missing" in violation.details

    def test_orphan_artifact_detected(self):
        actual = EXPECTED_ARTIFACTS | {"UnknownArtifact"}
        check, violation = assert_chain_closure(EXPECTED_ARTIFACTS, actual)
        assert check.passed is False
        assert violation is not None
        assert "orphans" in violation.details

    def test_both_missing_and_orphan(self):
        actual = (EXPECTED_ARTIFACTS - {"EvidencePack"}) | {"Orphan"}
        check, violation = assert_chain_closure(EXPECTED_ARTIFACTS, actual)
        assert check.passed is False
        assert "missing" in violation.details
        assert "orphans" in violation.details


# =============================================================================
# Meta-Governor: run_meta_invariants + fail_closed_on_violation
# =============================================================================


class TestP6_MetaGovernor:
    """Meta-governor: full report + fail-closed."""

    def test_all_green_report(self):
        report = run_meta_invariants(
            trace_id="t1",
            run_id="run-001",
            semantic_clock_tick=10,
            discovery_hash=PINNED_DISCOVERY_HASH,
            expected_discovery_hash=PINNED_DISCOVERY_HASH,
            schema_version=PINNED_SCHEMA_VERSION,
            expected_schema_version=PINNED_SCHEMA_VERSION,
            expected_artifacts=EXPECTED_ARTIFACTS,
            actual_artifacts=EXPECTED_ARTIFACTS,
        )
        assert report.pass_fail is True
        assert len(report.violations) == 0
        assert len(report.checks) == 2
        assert fail_closed_on_violation(report) is True

    def test_violation_report(self):
        report = run_meta_invariants(
            trace_id="t1",
            run_id="run-002",
            semantic_clock_tick=10,
            discovery_hash="wrong",
            expected_discovery_hash=PINNED_DISCOVERY_HASH,
            schema_version=PINNED_SCHEMA_VERSION,
            expected_schema_version=PINNED_SCHEMA_VERSION,
            expected_artifacts=EXPECTED_ARTIFACTS,
            actual_artifacts=EXPECTED_ARTIFACTS,
        )
        assert report.pass_fail is False
        assert len(report.violations) == 1

    def test_fail_closed_raises(self):
        report = run_meta_invariants(
            trace_id="t1",
            run_id="run-003",
            semantic_clock_tick=10,
            discovery_hash="wrong",
            expected_discovery_hash=PINNED_DISCOVERY_HASH,
            schema_version=PINNED_SCHEMA_VERSION,
            expected_schema_version=PINNED_SCHEMA_VERSION,
            expected_artifacts=EXPECTED_ARTIFACTS,
            actual_artifacts=EXPECTED_ARTIFACTS,
        )
        with pytest.raises(MetaInvariantError, match="FAIL"):
            fail_closed_on_violation(report)

    def test_report_frozen(self):
        report = run_meta_invariants(
            trace_id="t1",
            run_id="run-001",
            semantic_clock_tick=0,
            discovery_hash=PINNED_DISCOVERY_HASH,
            expected_discovery_hash=PINNED_DISCOVERY_HASH,
            schema_version=PINNED_SCHEMA_VERSION,
            expected_schema_version=PINNED_SCHEMA_VERSION,
            expected_artifacts=EXPECTED_ARTIFACTS,
            actual_artifacts=EXPECTED_ARTIFACTS,
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            report.pass_fail = False  # type: ignore[misc]

    def test_report_fields(self):
        required = {
            "trace_id",
            "run_id",
            "semantic_clock_tick",
            "checks",
            "pass_fail",
            "violations",
        }
        actual = {f.name for f in dataclasses.fields(MetaInvariantReport)}
        assert required.issubset(actual)

    def test_report_rejects_pass_with_violations(self):
        violation = InvariantViolation(
            invariant_id="test",
            severity=InvariantSeverity.HIGH,
            evidence_paths=("file.py",),
            details="test violation",
        )
        with pytest.raises(ValueError, match="pass_fail cannot be True"):
            MetaInvariantReport(
                trace_id="t1",
                run_id="r1",
                semantic_clock_tick=0,
                checks=(),
                pass_fail=True,
                violations=(violation,),
            )

    def test_multiple_violations_all_captured(self):
        report = run_meta_invariants(
            trace_id="t1",
            run_id="run-004",
            semantic_clock_tick=10,
            discovery_hash="wrong",
            expected_discovery_hash=PINNED_DISCOVERY_HASH,
            schema_version=PINNED_SCHEMA_VERSION,
            expected_schema_version=PINNED_SCHEMA_VERSION,
            expected_artifacts=EXPECTED_ARTIFACTS,
            actual_artifacts=EXPECTED_ARTIFACTS - {"EvidencePack"},
        )
        assert report.pass_fail is False
        assert len(report.violations) == 2

    def test_invariant_violation_fields(self):
        required = {"invariant_id", "severity", "evidence_paths", "details"}
        actual = {f.name for f in dataclasses.fields(InvariantViolation)}
        assert required.issubset(actual)

    def test_invariant_check_fields(self):
        required = {"check_id", "description", "passed", "evidence"}
        actual = {f.name for f in dataclasses.fields(InvariantCheck)}
        assert required.issubset(actual)
