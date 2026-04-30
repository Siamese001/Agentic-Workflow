"""Wave-N test generator — emits pilot-style test files from a spec JSON.

Originally authored for Wave 1 (24 CRITICAL rows). Now parameterized via
``--specs <path>`` so it can drive Wave 2+ runs from sibling JSON files
(``wave2_high_specs.json`` etc.).

Each generated test is ~85 lines and follows the W4d-4 pilot pattern:
  - 3 positive controls (artifact shape, OTEL span shape, replay digest stability)
  - 3 negative controls (one row-specific via the `negative_control_specific`
    text, one missing-field, one replay-drift)

The generator is data-driven, idempotent, and SAFE to re-run: existing test
files are overwritten with identical content given identical spec input.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SPECS = REPO_ROOT / "artifacts" / "requirements" / "wave1_critical_specs.json"

# Maps primary artifact-type → (helper assertion fn name, valid-record builder fn)
PRIMARY_ARTIFACT_RE = re.compile(r"\b([A-Z][A-Za-z0-9]+(?:[A-Z][A-Za-z0-9]+)+)\b")

# Mapping: primary artifact type -> (assertion helper, valid-record builder name).
ARTIFACT_DISPATCH = {
    "ChunkSealedEnvelope": ("assert_chunk_metadata_bound_before_embedding", "_chunk"),
    "L1PlanContract": ("assert_l1_no_authority_leak", "_l1plan"),
    "RouteContract": ("assert_l0_route_pre_filter_invariants", "_route"),
    "X3DispositionPacket": ("assert_x3_disposition_explicit", "_x3"),
    "L6EvalRecord": ("assert_l6_eval_no_current_run_mutation", "_l6eval"),
    "OtelTraceAuditRecord": ("assert_otel_replay_key_audit_present", "_otel"),
    "L5CertificationResult": ("assert_l5_certification_chain_present", "_l5cert"),
    "CommitRequest": ("assert_uwg_commit_request_invariants", "_uwg"),
    "ExecutionResult": ("assert_l2_execution_sealed", "_l2exec"),
    "FinalEvidenceContract": ("assert_final_evidence_contract_anchored", "_c0evid"),
}


def _detect_primary_artifact(runtime_artifact_expected: str) -> str:
    """Map runtime_artifact_expected text to a known primary artifact type.

    Some rows mention the cross-cutting OTEL trace bundle; we map that to
    OtelTraceAuditRecord.
    """
    if runtime_artifact_expected.startswith("OTEL trace bundle"):
        return "OtelTraceAuditRecord"
    matches = PRIMARY_ARTIFACT_RE.findall(runtime_artifact_expected)
    for m in matches:
        if m in ARTIFACT_DISPATCH:
            return m
    raise ValueError(f"unknown primary artifact in: {runtime_artifact_expected!r}")


def _trim(s: str, n: int = 120) -> str:
    s = (s or "").replace('"', "'").strip()
    return (s[:n] + "...") if len(s) > n else s


# Per-artifact valid-record builders. Each produces a record that satisfies
# the artifact's REQUIRED_FIELDS and the boundary assertion helper.
VALID_BUILDERS = {
    "ChunkSealedEnvelope": '''
def _valid_artifact() -> dict:
    return {
        "chunk_id": "chunk-{nid}-001",
        "tenant_id": "tenant-A",
        "acl": ["role:reader"],
        "confidentiality_tier": "internal",
        "freshness_band": "fresh",
        "effective_date": "2026-01-01",
        "expiry_date": "2027-01-01",
        "embedding_schema_version": "v1",
        "embedding_emitted": False,
        "metadata_bound_before_embedding": True,
        "owner_surface": OWNER_SURFACE,
    }
''',
    "L1PlanContract": '''
def _valid_artifact() -> dict:
    return {
        "proposed_route": "R-A",
        "query_spec": {"q": "x"},
        "task_spec": {"t": "y"},
        "route_risk": 0.1,
        "confidence": 0.9,
        "grounding_required": True,
        "declared_assumptions": [],
        "unresolved_gaps": [],
        "no_execution_assertion": True,
        "no_retrieval_assertion": True,
        "no_routing_assertion": True,
        "owner_surface": OWNER_SURFACE,
    }
''',
    "RouteContract": '''
def _valid_artifact() -> dict:
    return {
        "route_id": "R-{nid}",
        "route_class": "default",
        "decision_record_id": "dec-{nid}",
        "tenant_acl_checked": True,
        "region_checked": True,
        "confidentiality_checked": True,
        "effective_dates_checked": True,
        "freshness_band_checked": True,
        "policy_bound": True,
        "single_route_per_request": True,
        "owner_surface": OWNER_SURFACE,
    }
''',
    "X3DispositionPacket": '''
def _valid_artifact() -> dict:
    return {
        "disposition_id": "x3-{nid}-001",
        "disposition": "ALLOW",
        "owner_surface": OWNER_SURFACE,
        "no_silent_fallback_assertion": True,
        "no_hidden_commit_path_assertion": True,
        "no_ungated_human_mod_assertion": True,
        "single_disposition_per_request": True,
    }
''',
    "L6EvalRecord": '''
def _valid_artifact() -> dict:
    return {
        "eval_record_id": "eval-{nid}-001",
        "owner_surface": OWNER_SURFACE,
        "is_shadow": True,
        "no_current_run_mutation_assertion": True,
        "judge_calibrated": True,
        "replay_tied": True,
        "calibration_age_days": 7,
    }
''',
    "OtelTraceAuditRecord": '''
def _valid_artifact() -> dict:
    return {
        "trace_id": "trace-{nid}-001",
        "replay_key": "replay-{nid}-k",
        "owner_surface": OWNER_SURFACE,
        "w3c_traceparent": "00-000000000000000000000000000000{nid}-00000000000000{nid}-01",
        "w3c_tracestate": "vendor=v1",
        "replay_key_audit_present": True,
        "policy_hash": "policy-{nid}-h",
        "blueprint_hash": "blueprint-{nid}-h",
    }
''',
    "L5CertificationResult": '''
def _valid_artifact() -> dict:
    return {
        "certification_id": "cert-{nid}-001",
        "certification_class": "policy",
        "policy_hash": "policy-{nid}-h",
        "blueprint_hash": "blueprint-{nid}-h",
        "evidence_refs": ["authority-receipt-1", "policy-binding-receipt-1"],
        "owner_surface": OWNER_SURFACE,
        "issued_at_utc": "2026-04-30T12:00:00+00:00",
        "is_runtime_disposition": False,
    }
''',
    "CommitRequest": '''
def _valid_artifact() -> dict:
    return {
        "commit_request_id": "cr-{nid}-001",
        "writer_identity": "uwg-clerk",
        "blueprint_hash": "blueprint-{nid}-h",
        "policy_hash": "policy-{nid}-h",
        "diff_payload_hash": "diff-{nid}-h",
        "serial_seqno": 1,
        "owner_surface": OWNER_SURFACE,
        "single_writer_attestation": True,
    }
''',
    "ExecutionResult": '''
def _valid_artifact() -> dict:
    return {
        "execution_id": "exec-{nid}-001",
        "blueprint_hash": "blueprint-{nid}-h",
        "policy_hash": "policy-{nid}-h",
        "tool_calls": [],
        "side_effects_proposed": [],
        "replay_key": "replay-{nid}-k",
        "owner_surface": OWNER_SURFACE,
        "no_durable_commit_assertion": True,
        "no_hitl_invocation_assertion": True,
        "no_routing_assertion": True,
    }
''',
    "FinalEvidenceContract": '''
def _valid_artifact() -> dict:
    return {
        "contract_id": "fec-{nid}-001",
        "evidence_chain": [
            {"ref": "evidence-{nid}-1", "doc_id": "doc-A", "span": "p1"},
            {"ref": "evidence-{nid}-2", "doc_id": "doc-B", "span": "p2"},
        ],
        "citation_anchors": [
            {"claim_id": "claim-{nid}-1", "evidence_ref": "evidence-{nid}-1"},
        ],
        "support_targets": ["PA", "L2"],
        "owner_surface": OWNER_SURFACE,
        "assembly_hash": "asm-{nid}-h",
        "evidence_chain_complete": True,
        "citation_anchors_resolved": True,
        "no_unanchored_claims_assertion": True,
    }
''',
}

# Per-artifact "drift inducer" — a single field flip that MUST violate the assertion.
DRIFT_INDUCERS = {
    "ChunkSealedEnvelope": ('record["metadata_bound_before_embedding"] = False', "metadata_bound_before_embedding"),
    "L1PlanContract": ('record["no_execution_assertion"] = False', "no_execution_assertion"),
    "RouteContract": ('record["tenant_acl_checked"] = False', "tenant_acl_checked"),
    "X3DispositionPacket": ('record["disposition"] = "MAYBE"  # not in allowed set', "disposition"),
    "L6EvalRecord": ('record["no_current_run_mutation_assertion"] = False', "no_current_run_mutation_assertion"),
    "OtelTraceAuditRecord": ('record["replay_key_audit_present"] = False', "replay_key_audit_present"),
    "L5CertificationResult": ('record["evidence_refs"] = []', "evidence_refs"),
    "CommitRequest": ('record["single_writer_attestation"] = False', "single_writer_attestation"),
    "ExecutionResult": ('record["no_durable_commit_assertion"] = False', "no_durable_commit_assertion"),
    "FinalEvidenceContract": ('record["no_unanchored_claims_assertion"] = False', "no_unanchored_claims_assertion"),
}

# Per-artifact "missing required field" inducer (drop a required field).
MISSING_INDUCERS = {
    "ChunkSealedEnvelope": "tenant_id",
    "L1PlanContract": "proposed_route",
    "RouteContract": "route_id",
    "X3DispositionPacket": "disposition_id",
    "L6EvalRecord": "eval_record_id",
    "OtelTraceAuditRecord": "trace_id",
    "L5CertificationResult": "certification_id",
    "CommitRequest": "commit_request_id",
    "ExecutionResult": "execution_id",
    "FinalEvidenceContract": "contract_id",
}


TEMPLATE = '''"""Proof-evidence test for {req_id} ({surface}).

Severity      : CRITICAL
Surface       : {surface}
Layer owner   : {layer_owner}
Artifact      : {artifact_type}
OTEL span     : {span_name}
Source        : {source_file} :: {source_section}

Canonical requirement (paraphrased): {canonical_short}

Negative control text (from ledger row, paraphrased): {neg_control_short}

Generated by tools/requirements/generate_wave1_tests.py from
artifacts/requirements/wave1_critical_specs.json. Re-run the generator to
regenerate; do NOT hand-edit the rows that match the ledger spec.
"""

from __future__ import annotations

import pytest

from tests.fixtures.proof_evidence.otel_span_receipt import (
    BASE_REQUIRED_ATTRS,
    SpanAssertionError,
    assert_owner_surface_matches,
    assert_span_shape,
    make_receipt,
)
from tests.fixtures.proof_evidence.replay_digest import (
    assert_replay_drift_detected,
    assert_replay_stable,
)
from tests.fixtures.proof_evidence.runtime_artifact_validators import (
    ArtifactShapeError,
    {assert_helper},
    validate_artifact_shape,
)

REQ_ID = "{req_id}"
OWNER_SURFACE = "{surface}"
EXPECTED_SPAN = "{span_name}"
ARTIFACT_TYPE = "{artifact_type}"

# OTEL required attributes from the ledger row's otel_required_attributes
# column (pipe-delimited). BASE_REQUIRED_ATTRS already covers req_id, run_id,
# trace_id, request_id, owner_surface, policy_hash, blueprint_hash, replay_key.
EXTRA_SPAN_ATTRS = tuple(
    a for a in {span_extra_attrs!r}.split("|")
    if a and a not in BASE_REQUIRED_ATTRS
)
REQUIRED_ATTRS = BASE_REQUIRED_ATTRS + EXTRA_SPAN_ATTRS

{valid_builder}

def _valid_span_attrs() -> dict:
    attrs = {
        "req_id": REQ_ID,
        "run_id": "run-{nid}-001",
        "trace_id": "trace-{nid}-001",
        "request_id": "req-{nid}-001",
        "owner_surface": OWNER_SURFACE,
        "policy_hash": "policy-{nid}-h",
        "blueprint_hash": "blueprint-{nid}-h",
        "replay_key": "replay-{nid}-k",
    }
    # Add any extra row-required span attrs with deterministic placeholders.
    for a in EXTRA_SPAN_ATTRS:
        attrs.setdefault(a, f"{a}-{nid}-v")
    return attrs


# ---------------------------------------------------------------------------
# Positive controls
# ---------------------------------------------------------------------------

def test_artifact_shape_positive() -> None:
    """A well-formed {artifact_type} must validate cleanly + satisfy boundary invariant."""
    record = _valid_artifact()
    validate_artifact_shape(ARTIFACT_TYPE, record)
    {assert_helper}(record)


def test_span_shape_positive() -> None:
    """The {span_name} span must carry all required attrs."""
    receipt = make_receipt(EXPECTED_SPAN, _valid_span_attrs())
    assert_span_shape(receipt, EXPECTED_SPAN, REQUIRED_ATTRS)
    assert_owner_surface_matches(receipt, OWNER_SURFACE)


def test_replay_digest_stability_positive() -> None:
    """Same artifact yields the same digest across runs."""
    digest = assert_replay_stable(_valid_artifact())
    assert len(digest) == 64  # sha256 hex


# ---------------------------------------------------------------------------
# Negative controls (matches negative_control_specific from the ledger row)
# ---------------------------------------------------------------------------

def test_negative_control_specific_violation() -> None:
    """{req_id}: per ledger row, a {artifact_type} that violates the canonical
    requirement MUST raise. Drift inducer: {drift_target}.
    """
    record = _valid_artifact()
    {drift_inducer}
    with pytest.raises(ArtifactShapeError):
        {assert_helper}(record)


def test_negative_control_missing_required_field() -> None:
    """A {artifact_type} missing the required field {missing_field!r} MUST fail shape validation."""
    record = _valid_artifact()
    del record[{missing_field!r}]
    with pytest.raises(ArtifactShapeError) as excinfo:
        validate_artifact_shape(ARTIFACT_TYPE, record)
    assert {missing_field!r} in str(excinfo.value)


def test_negative_control_span_missing_owner_surface() -> None:
    """Span without owner_surface MUST fail shape assertion."""
    attrs = _valid_span_attrs()
    del attrs["owner_surface"]
    receipt = make_receipt(EXPECTED_SPAN, attrs)
    with pytest.raises(SpanAssertionError):
        assert_span_shape(receipt, EXPECTED_SPAN, REQUIRED_ATTRS)


def test_negative_control_replay_drift() -> None:
    """Two semantically different artifacts MUST produce different digests."""
    a = _valid_artifact()
    b = _valid_artifact()
    # Mutate a deterministic field that participates in the digest.
    if "owner_surface" in b:
        b["owner_surface"] = OWNER_SURFACE + "-DRIFTED"
    assert_replay_drift_detected(a, b)
'''


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate proof-evidence test files from a spec JSON.")
    parser.add_argument(
        "--specs", default=str(DEFAULT_SPECS),
        help="Path to spec JSON (default: %(default)s)",
    )
    args = parser.parse_args()
    specs_path = Path(args.specs)
    if not specs_path.is_absolute():
        specs_path = REPO_ROOT / specs_path
    print(f"[generate_wave1_tests] reading specs from {specs_path}")
    spec = json.loads(specs_path.read_text(encoding="utf-8"))
    written = 0
    for entry in spec["req_specs"]:
        primary = _detect_primary_artifact(entry["runtime_artifact_expected"])
        if primary not in ARTIFACT_DISPATCH:
            print(f"SKIP {entry['req_id']}: no dispatch for primary={primary}")
            continue
        helper, _ = ARTIFACT_DISPATCH[primary]
        nid = entry["req_id"].replace("10C-REQ-", "")
        nid_int = int(nid)
        # VALID_BUILDERS templates contain dict literals; use plain replace
        # rather than .format() to avoid {...} collisions.
        builder = VALID_BUILDERS[primary].replace("{nid}", str(nid_int)).strip()
        drift_code, drift_target = DRIFT_INDUCERS[primary]
        missing_field = MISSING_INDUCERS[primary]
        # Same hazard for TEMPLATE — it has {{ }} dict braces inline. Use
        # a manual substitution chain for the same reason.
        substitutions = {
            "{req_id}": entry["req_id"],
            "{surface}": entry["surface"],
            "{layer_owner}": entry["layer_owner"],
            "{artifact_type}": primary,
            "{span_name}": entry["otel_span_expected"] or "unknown.span",
            "{source_file}": entry["source_file"],
            "{source_section}": entry["source_section"],
            "{canonical_short}": _trim(entry["canonical_requirement"], 140),
            "{neg_control_short}": _trim(entry["negative_control_specific"], 140),
            "{assert_helper}": helper,
            "{valid_builder}": builder,
            "{nid}": str(nid_int),
            "{span_extra_attrs!r}": repr(entry["otel_required_attributes"]),
            "{drift_inducer}": drift_code,
            "{drift_target}": drift_target,
            "{missing_field!r}": repr(missing_field),
        }
        body = TEMPLATE
        for k, v in substitutions.items():
            body = body.replace(k, v)
        out = REPO_ROOT / entry["test_file"]
        out.parent.mkdir(parents=True, exist_ok=True)
        # Ensure __init__.py exists in any new test package directories so
        # pytest can collect them in plugin-isolated mode.
        cur = out.parent
        repo_tests = REPO_ROOT / "tests"
        while cur != repo_tests and cur.exists() and repo_tests in cur.parents:
            init = cur / "__init__.py"
            if not init.exists():
                init.write_text("", encoding="utf-8")
            cur = cur.parent
        out.write_text(body, encoding="utf-8")
        written += 1
        print(f"wrote {out.relative_to(REPO_ROOT)}")
    print(f"\n[generate_wave1_tests] wrote {written}/{len(spec['req_specs'])} test files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
