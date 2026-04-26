"""00C.7 GateVerdict schema conformance tests.

Proof command (doctrine §00C):
    python -m pytest tests/runtime_gates/test_gate_verdict_schema.py -q

Validates:
- canonical GateVerdict shape requires the doctrine field set
- UNKNOWN never converts to PASS
- NOT_APPLICABLE requires a reason
- WARN material requires policy allowance (severity HIGH/CRITICAL surfaced)
- COMMIT_REQUEST is non-write (gate cannot mutate L4)
- Exit X3 disposition is not emitted by gate layer
- Deterministic digest is stable for identical inputs
"""

from __future__ import annotations

import pytest

from agentic_core.L5_safety.runtime_gates.digest import verdict_digest
from agentic_core.L5_safety.runtime_gates.types import (
    SCHEMA_VERSION,
    Disposition,
    GateDecision,
    GraderType,
    Result,
    Severity,
)

# Required canonical 00C.7 fields on every emitted verdict.
REQUIRED_VERDICT_KEYS: tuple[str, ...] = (
    "gate_id",
    "gate_family",
    "gate_surface",
    "primary_layer",
    "evaluated_packet_ref",
    "request_id",
    "run_id",
    "trace_root",
    "trace_id",
    "tenant_id",
    "policy_hash",
    "blueprint_hash",
    "replay_key",
    "result",
    "disposition",
    "severity",
    "reason_codes",
    "score",
    "threshold",
    "grader_type",
    "evidence_refs",
    "replay_refs",
    "source_lineage_refs",
    "confidence",
    "abstain_flag",
    "remediation_hint",
    "deterministic_digest",
    "created_at_run_offset",
    "schema_version",
)

# X3 disposition vocabulary owned by Exit, NOT runtime gates.
EXIT_OWNED_X3 = frozenset({"X3A", "X3B", "X3C", "X3D", "X3E"})


def _verdict(**overrides) -> dict:
    """Build a typical verdict dict from a GateDecision."""
    decision = GateDecision(gate_id="G01", disposition=Disposition.ALLOW)
    for k, v in overrides.items():
        setattr(decision, k, v)
    return decision.to_verdict()


def test_gate_verdict_schema_requires_core_fields():
    """Every doctrine GateVerdict key MUST be present on serialized verdicts."""
    v = _verdict()
    missing = [k for k in REQUIRED_VERDICT_KEYS if k not in v]
    assert not missing, f"GateVerdict missing required keys: {missing}"


def test_unknown_never_converts_to_pass():
    """UNKNOWN cannot be silently rewritten to PASS (00C.7 hard rule)."""
    decision = GateDecision(
        gate_id="G09",
        disposition=Disposition.ESCALATE_HITL,
        result=Result.UNKNOWN,
    )
    v = decision.to_verdict()
    assert v["result"] == "UNKNOWN"
    assert v["disposition"] != "ALLOW"


def test_not_applicable_requires_reason():
    """NOT_APPLICABLE verdicts MUST carry an applicability rationale."""
    decision = GateDecision(
        gate_id="G27",
        disposition=Disposition.ALLOW,
        result=Result.NOT_APPLICABLE,
        reason_codes=["read_only_route"],
    )
    v = decision.to_verdict()
    assert v["result"] == "NOT_APPLICABLE"
    assert v["reason_codes"], "NOT_APPLICABLE requires non-empty reason_codes"


def test_material_warn_requires_policy_allowance():
    """A material WARN must surface severity HIGH/CRITICAL for Exit visibility."""
    decision = GateDecision(
        gate_id="G22",
        disposition=Disposition.MARK_DEGRADED,
        result=Result.WARN,
        severity=Severity.HIGH,
    )
    v = decision.to_verdict()
    assert v["result"] == "WARN"
    assert v["severity"] in ("HIGH", "CRITICAL")


def test_commit_request_remains_non_write():
    """COMMIT_REQUEST is a routing recommendation to UWG, not a write."""
    decision = GateDecision(
        gate_id="G27",
        disposition=Disposition.COMMIT_REQUEST,
        reason_codes=["proposed_mutation"],
    )
    v = decision.to_verdict()
    assert v["disposition"] == "COMMIT_REQUEST"
    # Verdicts must not carry any L4-mutation marker.
    assert "l4_mutation" not in v
    assert "durable_write" not in v


def test_exit_x3_disposition_not_emitted_by_gate_layer():
    """Runtime gates may NOT emit X3A/X3B/X3C/X3D/X3E (Exit owns those)."""
    for d in Disposition:
        assert d.value not in EXIT_OWNED_X3, (
            f"runtime Disposition leaked X3 vocabulary: {d.value}"
        )


def test_gate_mesh_digest_stable():
    """Identical verdicts produce identical digests."""
    decision_a = GateDecision(
        gate_id="G01", disposition=Disposition.ALLOW, reason_codes=["a", "b"]
    )
    decision_b = GateDecision(
        gate_id="G01", disposition=Disposition.ALLOW, reason_codes=["a", "b"]
    )
    assert verdict_digest(decision_a.to_verdict()) == verdict_digest(decision_b.to_verdict())


def test_gate_bundle_rejects_missing_required_gate():
    """A GateMeshResult flags missing required gate IDs."""
    from agentic_core.L5_safety.runtime_gates.mesh_result import build_mesh_result

    decisions = [GateDecision(gate_id="G01", disposition=Disposition.ALLOW)]
    bundle = build_mesh_result(
        decisions,
        required_gate_ids=["G01", "G02"],
        evaluated_surface="U0",
    )
    assert "G02" in bundle.missing_gate_ids
    assert bundle.recommended_disposition_summary == "BLOCK_EXIT"


def test_schema_version_present_on_verdict():
    v = _verdict()
    assert v["schema_version"] == SCHEMA_VERSION


@pytest.mark.parametrize("gtype", list(GraderType))
def test_grader_type_round_trips(gtype):
    decision = GateDecision(
        gate_id="G09", disposition=Disposition.ALLOW, grader_type=gtype
    )
    v = decision.to_verdict()
    assert v["grader_type"] == gtype.value


def test_disposition_vocabulary_is_doctrine_15():
    """The 15 bounded dispositions from 00C parent + 00C.7 disposition table."""
    expected = {
        "ALLOW", "DENY", "CLARIFY", "ABSTAIN", "REROUTE", "SHRINK_SCOPE",
        "RETRY", "HEAL", "ESCALATE_HITL", "QUARANTINE", "REDACT",
        "SAFE_FALLBACK", "MARK_DEGRADED", "COMMIT_REQUEST", "BLOCK_COMMIT",
    }
    actual = {d.value for d in Disposition}
    assert actual == expected


def test_result_vocabulary_is_doctrine_5():
    expected = {"PASS", "FAIL", "WARN", "UNKNOWN", "NOT_APPLICABLE"}
    actual = {r.value for r in Result}
    assert actual == expected
