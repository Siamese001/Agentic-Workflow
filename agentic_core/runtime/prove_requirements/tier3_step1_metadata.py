"""Tier 3 metadata generator.

Reads the Tier 3 selection (`docs/reference/contracts/tier3/TIER3_SELECTION.json`)
and emits four normalized metadata-surface files plus a schema validation
report under ``artifacts/runtime/requirements_proof/``.

This is metadata/linkage work only. It does NOT implement runtime behavior,
run tests, run proof harnesses, execute replay, or run OTEL exporters.
It does NOT claim proof, coverage, or readiness.

First-pass policy: only on-disk references that already map cleanly to a
Tier 3 row are populated. When a reference dict is empty for a REQ_ID,
the corresponding NEEDS_* blocker remains and the row is classified as
PARTIAL_LINK / LINKED_CONCEPTUAL / NO_LINK accordingly.

Status vocabulary used here:
  - LINKED_LITERAL / LINKED_CONCEPTUAL / PARTIAL_LINK / NO_LINK (linkage)
  - blocker codes per spec (NEEDS_*, NO_LINK)
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Sequence, Tuple

REPO_ROOT = Path(__file__).resolve().parents[3]
SELECTION_PATH = REPO_ROOT / "docs" / "reference" / "contracts" / "tier3" / "TIER3_SELECTION.json"
ARTIFACTS_DIR = REPO_ROOT / "artifacts" / "runtime" / "requirements_proof"

OUT_FILES: Dict[str, str] = {
    "index": "tier3_requirements_index.generated.json",
    "coverage": "tier3_coverage_matrix.generated.json",
    "impl": "tier3_implementation_map.generated.json",
    "artifact": "tier3_artifact_linkage.generated.json",
}
OUT_VALIDATION_REPORT = "tier3_schema_validation_report.md"

# ---------------------------------------------------------------------------
# Stable expected_fail_reason mapping. Populated when the requirement's
# failure mode is obvious from the REQ_ID + requirement text. Otherwise the
# row keeps the NEEDS_EXPECTED_FAIL_REASON blocker.
# ---------------------------------------------------------------------------
EXPECTED_FAIL_REASONS: Mapping[str, str] = {
    "REQ-L6-OBS-ANTI-BYPASS-001": "L6_OBS_BYPASS_BLOCKED",
    "REQ-C0-NO-WRITE-001": "C0_DURABLE_WRITE_BLOCKED",
    "REQ-L0-NO-EXECUTE-001": "L0_EXECUTION_BLOCKED",
    "REQ-L0-GROUNDED-ACTION-HANDOFF-001": "L0_GROUNDED_ACTION_HANDOFF_REQUIRED",
    "REQ-UWG-AUDIT-REPLAY-CONSISTENCY-001": "UWG_AUDIT_REPLAY_MISMATCH",
    "REQ-GATE-G01-G05-INGRESS-001": "GATE_G01_G05_INGRESS_REQUIRED",
    "REQ-GATE-G06-G10-HITL-ROUTE-001": "GATE_G06_G10_HITL_ROUTE_REQUIRED",
    "REQ-GATE-G11-G15-TOOL-MODEL-001": "GATE_G11_G15_TOOL_MODEL_REQUIRED",
    "REQ-GATE-G16-G20-MEMORY-WORKFLOW-001": "GATE_G16_G20_MEMORY_WORKFLOW_REQUIRED",
    "REQ-GATE-G21-G24-OUTPUT-REPLAY-001": "GATE_G21_G24_OUTPUT_REPLAY_REQUIRED",
    "REQ-GATE-G25-G29-EXIT-WRITE-001": "GATE_G25_G29_EXIT_WRITE_REQUIRED",
    "REQ-GATE-NO-OVERLAP-WITH-EXIT-001": "GATE_EXIT_OVERLAP_BLOCKED",
    "REQ-GATE-NO-OVERLAP-WITH-L5-001": "GATE_L5_OVERLAP_BLOCKED",
    "REQ-L5-REPLAY-AUDIT-CERT-001": "L5_REPLAY_AUDIT_CERT_MISSING",
    "REQ-U0-OBS-REPLAY-001": "U0_OBS_REPLAY_MISSING",
    "REQ-L1-OBS-OTEL-001": "L1_OBS_OTEL_MISSING",
    "REQ-L1-PLAN-VALIDATION-SELF-REPAIR-001": "L1_PLAN_VALIDATION_REQUIRED",
    "REQ-L1-AMBIGUITY-EVIDENCE-001": "L1_AMBIGUITY_EVIDENCE_MISSING",
    "REQ-U0-CHANNEL-VALIDATION-001": "U0_CHANNEL_VALIDATION_REJECTED",
    "REQ-EXIT-X1A-X1F-CHECKS-001": "EXIT_X1A_X1F_CHECKS_REQUIRED",
    "REQ-PA-VALIDATE-SLOT-CONTRACT-001": "PA_SLOT_CONTRACT_VIOLATION",
    "REQ-L5-EGRESS-PROVIDER-GOV-001": "L5_EGRESS_PROVIDER_GOV_MISSING",
    "REQ-E2E-FIXTURES-REPLAY-HARNESS-001": "E2E_REPLAY_HARNESS_BOUNDARY_BLOCKED",
    "REQ-C0-PREFLIGHT-GROUNDING-001": "C0_PREFLIGHT_GROUNDING_REQUIRED",
    "REQ-C0-GRAPH-RAG-001": "C0_GRAPH_RAG_BOUNDS_VIOLATION",
}

# ---------------------------------------------------------------------------
# On-disk reference candidates. First-pass policy: do NOT invent file names.
# Only paths verified to exist on disk are kept; missing paths are silently
# dropped via _filter_existing. Empty tuples → no reference yet; the
# corresponding NEEDS_* blocker remains and gate is BLOCKED. That is
# acceptable and preferred over fake readiness.
# ---------------------------------------------------------------------------

CODE_REFERENCES: Mapping[str, Sequence[str]] = {
    "REQ-L6-OBS-ANTI-BYPASS-001": (),
    "REQ-C0-NO-WRITE-001": (),
    "REQ-L0-NO-EXECUTE-001": (),
    "REQ-L0-GROUNDED-ACTION-HANDOFF-001": (),
    "REQ-UWG-AUDIT-REPLAY-CONSISTENCY-001": (),
    "REQ-GATE-G01-G05-INGRESS-001": (),
    "REQ-GATE-G06-G10-HITL-ROUTE-001": (),
    "REQ-GATE-G11-G15-TOOL-MODEL-001": (),
    "REQ-GATE-G16-G20-MEMORY-WORKFLOW-001": (),
    "REQ-GATE-G21-G24-OUTPUT-REPLAY-001": (),
    "REQ-GATE-G25-G29-EXIT-WRITE-001": (),
    "REQ-GATE-NO-OVERLAP-WITH-EXIT-001": (),
    "REQ-GATE-NO-OVERLAP-WITH-L5-001": (),
    "REQ-L5-REPLAY-AUDIT-CERT-001": (),
    "REQ-U0-OBS-REPLAY-001": (),
    "REQ-L1-OBS-OTEL-001": (),
    "REQ-L1-PLAN-VALIDATION-SELF-REPAIR-001": (),
    "REQ-L1-AMBIGUITY-EVIDENCE-001": (),
    "REQ-U0-CHANNEL-VALIDATION-001": (),
    "REQ-EXIT-X1A-X1F-CHECKS-001": (),
    "REQ-PA-VALIDATE-SLOT-CONTRACT-001": (),
    "REQ-L5-EGRESS-PROVIDER-GOV-001": (),
    "REQ-E2E-FIXTURES-REPLAY-HARNESS-001": (),
    "REQ-C0-PREFLIGHT-GROUNDING-001": (),
    "REQ-C0-GRAPH-RAG-001": (),
}

VALIDATOR_REFERENCES: Mapping[str, Sequence[str]] = {rid: () for rid in CODE_REFERENCES}
TEST_REFERENCES: Mapping[str, Sequence[str]] = {rid: () for rid in CODE_REFERENCES}
ARTIFACT_REFERENCES: Mapping[str, Sequence[str]] = {rid: () for rid in CODE_REFERENCES}
REPLAY_REFERENCES: Mapping[str, Sequence[str]] = {rid: () for rid in CODE_REFERENCES}
OTEL_SPAN_REFERENCES: Mapping[str, Sequence[str]] = {rid: () for rid in CODE_REFERENCES}
NEGATIVE_CONTROL_REFERENCES: Mapping[str, Sequence[str]] = {rid: () for rid in CODE_REFERENCES}

# ---------------------------------------------------------------------------
# Phase 3: Existing-reference enrichment. Only paths that already exist on
# disk and clearly map to the requirement may be added below. Inventing
# file names is forbidden by the prompt. Any ref added here is also gated
# at runtime by _filter_existing — stale paths are silently dropped.
# ---------------------------------------------------------------------------

# (Reserved for future enrichment passes. Empty for first-pass: gate is
# expected to be BLOCKED.)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _filter_existing(paths: Sequence[str]) -> List[str]:
    """Drop paths that do not exist on disk. Never invents files."""
    return [p for p in paths if (REPO_ROOT / p).exists()]


def _filter_matching_req_id(paths: Sequence[str], req_id: str) -> List[str]:
    """Drop JSON paths whose `step1_req_id` is present and does not match."""
    out: List[str] = []
    for p in paths:
        full = REPO_ROOT / p
        if not full.is_file() or not p.endswith(".json"):
            out.append(p)
            continue
        try:
            data = json.loads(full.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            out.append(p)
            continue
        if isinstance(data, dict) and "step1_req_id" in data:
            if data["step1_req_id"] != req_id:
                continue
        out.append(p)
    return out


def _load_selection() -> Dict[str, Any]:
    return json.loads(SELECTION_PATH.read_text(encoding="utf-8"))


def _is_applicable(gap_value: str) -> bool:
    if not gap_value:
        return False
    return "NOT_APPLICABLE" not in gap_value.upper()


def _build_row(selected: Mapping[str, Any]) -> Dict[str, Any]:
    rid = selected["req_id"]
    blockers: List[str] = []

    efr = EXPECTED_FAIL_REASONS.get(rid, "").strip()
    if not efr:
        blockers.append("NEEDS_EXPECTED_FAIL_REASON")

    code_refs = _filter_existing(CODE_REFERENCES.get(rid, ()))
    validator_refs = _filter_existing(VALIDATOR_REFERENCES.get(rid, ()))
    test_refs = _filter_existing(TEST_REFERENCES.get(rid, ()))
    artifact_refs = _filter_matching_req_id(
        _filter_existing(ARTIFACT_REFERENCES.get(rid, ())), rid
    )
    replay_refs = _filter_matching_req_id(
        _filter_existing(REPLAY_REFERENCES.get(rid, ())), rid
    )
    otel_span_refs = _filter_existing(OTEL_SPAN_REFERENCES.get(rid, ()))
    negative_control_refs = _filter_existing(NEGATIVE_CONTROL_REFERENCES.get(rid, ()))

    if not code_refs:
        blockers.append("NEEDS_CODE_REF")
    if not validator_refs:
        blockers.append("NEEDS_VALIDATOR_REF")
    if not otel_span_refs:
        blockers.append("NEEDS_OTEL_SPAN")
    if _is_applicable(selected.get("likely_test_gap", "")) and not test_refs:
        blockers.append("NEEDS_TEST_MAPPING")
    if _is_applicable(selected.get("likely_artifact_gap", "")) and not artifact_refs:
        blockers.append("NEEDS_ARTIFACT_FIELD")
    if _is_applicable(selected.get("likely_replay_gap", "")) and not replay_refs:
        blockers.append("NEEDS_REPLAY_FIELD")
    if _is_applicable(selected.get("likely_negative_control_gap", "")) and not negative_control_refs:
        blockers.append("NEEDS_NEGATIVE_CONTROL")

    if blockers:
        if (
            test_refs
            or artifact_refs
            or replay_refs
            or negative_control_refs
            or code_refs
            or validator_refs
            or otel_span_refs
        ):
            linkage_status = "PARTIAL_LINK"
        elif efr:
            linkage_status = "LINKED_CONCEPTUAL"
        else:
            linkage_status = "NO_LINK"
            if "NO_LINK" not in blockers:
                blockers.append("NO_LINK")
    else:
        linkage_status = "LINKED_LITERAL"

    return {
        "tier": "TIER3",
        "step1_req_id": rid,
        "source_matrix_file": selected["source_matrix_file"],
        "owner_layer": selected["owner_layer"],
        "owner_subsystem": selected["owner_subsystem"],
        "requirement_text": selected["requirement_text"],
        "requirement_strength": selected["requirement_strength"],
        "release_gate_rule": selected["release_gate_rule"],
        "risk_category": selected["risk_category"],
        "why_tier3": selected["why_tier3"],
        "expected_fail_reason": efr,
        "linkage_status": linkage_status,
        "blockers": blockers,
        "code_refs": code_refs,
        "validator_refs": validator_refs,
        "test_refs": test_refs,
        "test_executed": False,
        "artifact_refs": artifact_refs,
        "artifact_verified": False,
        "replay_refs": replay_refs,
        "replay_executed": False,
        "otel_span_refs": otel_span_refs,
        "negative_control_refs": negative_control_refs,
        "negative_control_executed": False,
    }


def _build_rows() -> List[Dict[str, Any]]:
    selection = _load_selection()
    return [_build_row(sel) for sel in selection["selected"]]


def _surface_payload(surface: str, rows: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "tier": "TIER3",
        "surface": surface,
        "purpose": "Tier 3 metadata linkage. Selection-derived; no proof claims.",
        "generated_at": _utc_now_iso(),
        "source_files": {
            "selection": "docs/reference/contracts/tier3/TIER3_SELECTION.json",
            "step1_matrices_dir": "docs/reference/contracts/step1/",
        },
        "row_count": len(rows),
        "rows": list(rows),
    }


def _validate(
    rows: Sequence[Mapping[str, Any]],
) -> Tuple[List[str], Dict[str, int], Dict[str, int]]:
    errors: List[str] = []
    allowed_linkage = {"LINKED_LITERAL", "LINKED_CONCEPTUAL", "PARTIAL_LINK", "NO_LINK"}
    allowed_blockers = {
        "NEEDS_STEP1_ROW",
        "NEEDS_EXPECTED_FAIL_REASON",
        "NEEDS_CODE_REF",
        "NEEDS_VALIDATOR_REF",
        "NEEDS_TEST_MAPPING",
        "NEEDS_ARTIFACT_FIELD",
        "NEEDS_REPLAY_FIELD",
        "NEEDS_OTEL_SPAN",
        "NEEDS_NEGATIVE_CONTROL",
        "NO_LINK",
    }
    required_fields = {
        "tier",
        "step1_req_id",
        "source_matrix_file",
        "owner_layer",
        "owner_subsystem",
        "requirement_text",
        "requirement_strength",
        "release_gate_rule",
        "risk_category",
        "why_tier3",
        "expected_fail_reason",
        "linkage_status",
        "blockers",
        "code_refs",
        "validator_refs",
        "test_refs",
        "artifact_refs",
        "replay_refs",
        "otel_span_refs",
        "negative_control_refs",
    }
    forbidden_tokens = {
        "PASS",
        "FAIL",
        "PROVEN",
        "FULLY_PROVEN",
        "ARCHITECTURE_PROVEN",
        "COMPLETE",
        "COVERED",
        "CLOSED",
    }

    linkage_counts: Dict[str, int] = {k: 0 for k in allowed_linkage}
    blocker_counts: Dict[str, int] = {k: 0 for k in allowed_blockers}

    for row in rows:
        missing = required_fields - set(row.keys())
        if missing:
            errors.append(f"{row.get('step1_req_id', '?')}: missing fields {sorted(missing)}")
        if row.get("tier") != "TIER3":
            errors.append(f"{row.get('step1_req_id', '?')}: tier!=TIER3")
        ls = row.get("linkage_status")
        if ls not in allowed_linkage:
            errors.append(f"{row.get('step1_req_id', '?')}: invalid linkage_status={ls!r}")
        else:
            linkage_counts[ls] += 1
        for b in row.get("blockers", []):
            if b not in allowed_blockers:
                errors.append(f"{row.get('step1_req_id', '?')}: invalid blocker={b!r}")
            else:
                blocker_counts[b] += 1
        for forbidden in forbidden_tokens:
            if row.get("linkage_status") == forbidden:
                errors.append(f"{row.get('step1_req_id', '?')}: forbidden status token {forbidden}")

    return errors, linkage_counts, blocker_counts


def generate() -> Dict[str, Path]:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    rows = _build_rows()
    written: Dict[str, Path] = {}
    for surface, fname in OUT_FILES.items():
        path = ARTIFACTS_DIR / fname
        path.write_text(
            json.dumps(_surface_payload(surface, rows), indent=2),
            encoding="utf-8",
        )
        written[surface] = path

    errors, linkage_counts, blocker_counts = _validate(rows)
    report_lines: List[str] = []
    report_lines.append("# Tier 3 Schema Validation Report")
    report_lines.append("")
    report_lines.append(f"- Generated at: {_utc_now_iso()}")
    report_lines.append(f"- Row count: {len(rows)}")
    report_lines.append(f"- Surface files: {len(written)}")
    report_lines.append(f"- Schema validation: {'OK' if not errors else 'FAILED'}")
    report_lines.append("")
    report_lines.append("## Linkage status counts")
    for k, v in linkage_counts.items():
        report_lines.append(f"- {k}: {v}")
    report_lines.append("")
    report_lines.append("## Blocker counts")
    for k, v in blocker_counts.items():
        report_lines.append(f"- {k}: {v}")
    if errors:
        report_lines.append("")
        report_lines.append("## Validation errors")
        for e in errors:
            report_lines.append(f"- {e}")
    report_path = ARTIFACTS_DIR / OUT_VALIDATION_REPORT
    report_path.write_text("\n".join(report_lines), encoding="utf-8")
    written["validation_report"] = report_path

    print(f"Generated {len(OUT_FILES)} files + report at {report_path}")
    print(f"Tier 3 row count per file: {len(rows)}")
    print(f"Schema validation: {'OK' if not errors else 'FAILED'}")
    print(f"Linkage status counts: {linkage_counts}")
    print(f"Blocker counts: {blocker_counts}")
    return written


def main() -> int:
    generate()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
