"""Tier 6 metadata generator.

Reads ``docs/reference/contracts/tier6/TIER6_SELECTION.json`` and emits
the four normalized Tier 6 metadata surfaces plus a schema-validation
report. Phase 3 of Tier 6 Prompt A maps existing references only --
this module declares per-REQ_ID reference dicts and any future prompt
populates them as evidence is produced. No fixtures are created here;
no runtime is executed.

Status vocabulary: LINKED_LITERAL | LINKED_CONCEPTUAL | PARTIAL_LINK |
NO_LINK. Blocker vocabulary: NEEDS_STEP1_ROW, NEEDS_EXPECTED_FAIL_REASON,
NEEDS_CODE_REF, NEEDS_VALIDATOR_REF, NEEDS_TEST_MAPPING,
NEEDS_ARTIFACT_FIELD, NEEDS_REPLAY_FIELD, NEEDS_OTEL_SPAN,
NEEDS_NEGATIVE_CONTROL, NO_LINK.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Sequence, Tuple

REPO_ROOT = Path(__file__).resolve().parents[3]
SELECTION_PATH = REPO_ROOT / "docs" / "reference" / "contracts" / "tier6" / "TIER6_SELECTION.json"
ARTIFACTS_DIR = REPO_ROOT / "artifacts" / "runtime" / "requirements_proof"

OUT_FILES: Dict[str, str] = {
    "index": "tier6_requirements_index.generated.json",
    "coverage": "tier6_coverage_matrix.generated.json",
    "impl": "tier6_implementation_map.generated.json",
    "artifact": "tier6_artifact_linkage.generated.json",
}
OUT_VALIDATION_REPORT = "tier6_schema_validation_report.md"

# ---------------------------------------------------------------------------
# Stable expected_fail_reason mapping. Populated when the requirement's
# fail-reason code is direct and durable from the REQ_ID + text. Rows
# without an obvious code remain blocked on NEEDS_EXPECTED_FAIL_REASON.
# ---------------------------------------------------------------------------

REFERENCE_ONLY_EFR = "REFERENCE_ONLY_ROW_NOT_RELEASE_BLOCKING"

EXPECTED_FAIL_REASONS: Dict[str, str] = {
    # 6 MUST / RELEASE_BLOCKING rows -- durable per-row codes.
    "REQ-C0-WEAK-SUPPORT-REFINEMENT-001": "C0_WEAK_SUPPORT_REFINEMENT_REQUIRED",
    "REQ-EXIT-RUNTIME-TO-REGRESSION-001": "EXIT_RUNTIME_TO_REGRESSION_MISSING",
    "REQ-L6-HUMAN-CALIBRATION-001": "L6_HUMAN_CALIBRATION_MISSING",
    "REQ-E2E-ROUTE-PATH-COVERAGE-001": "E2E_ROUTE_PATH_COVERAGE_MISSING",
    "REQ-E2E-GOLDEN-PATH-001": "E2E_GOLDEN_PATH_MISSING",
    "REQ-E2E-ACCEPTANCE-COMMANDS-001": "E2E_ACCEPTANCE_COMMANDS_MISSING",
    # 15 NON_BLOCKING_REFERENCE rows -- single stable reference-only code.
    "REQ-C0-OVERVIEW-REFERENCE-001": REFERENCE_ONLY_EFR,
    "REQ-C0-TRACEABILITY-MATRIX-REF-001": REFERENCE_ONLY_EFR,
    "REQ-E2E-OVERVIEW-REFERENCE-001": REFERENCE_ONLY_EFR,
    "REQ-E2E-REQ-TO-EVIDENCE-COMPILER-001": REFERENCE_ONLY_EFR,
    "REQ-EXIT-OVERVIEW-REFERENCE-001": REFERENCE_ONLY_EFR,
    "REQ-L0-OVERVIEW-REFERENCE-001": REFERENCE_ONLY_EFR,
    "REQ-L1-OVERVIEW-REFERENCE-001": REFERENCE_ONLY_EFR,
    "REQ-L2-COVERAGE-MATRIX-REF-001": REFERENCE_ONLY_EFR,
    "REQ-L4-OVERVIEW-REFERENCE-001": REFERENCE_ONLY_EFR,
    "REQ-L5-V5-COVERAGE-MATRIX-REF-001": REFERENCE_ONLY_EFR,
    "REQ-L6-OVERVIEW-REFERENCE-001": REFERENCE_ONLY_EFR,
    "REQ-L6-V6-COVERAGE-MATRIX-REF-001": REFERENCE_ONLY_EFR,
    "REQ-PA-OVERVIEW-REFERENCE-001": REFERENCE_ONLY_EFR,
    "REQ-PA-TRACEABILITY-MATRIX-REF-001": REFERENCE_ONLY_EFR,
    "REQ-U0-OVERVIEW-REFERENCE-001": REFERENCE_ONLY_EFR,
}

_MUST_REFS_MOD = "agentic_core/runtime/prove_requirements/tier6_refs/must_release_blocking_refs.py"
_REF_REFS_MOD = "agentic_core/runtime/prove_requirements/tier6_refs/reference_only_policy_refs.py"
_TIER6_TEST = "tests/runtime/test_tier6_final_rows_fixtures.py"
_REFERENCE_ONLY_POLICY = "artifacts/runtime/requirements_proof/tier6_reference_only_policy.json"

_TIER6_MUST_SCENARIOS: Dict[str, str] = {
    "REQ-C0-WEAK-SUPPORT-REFINEMENT-001": "CT_c0_weak_support_refinement",
    "REQ-E2E-ACCEPTANCE-COMMANDS-001": "CU_e2e_acceptance_commands",
    "REQ-E2E-GOLDEN-PATH-001": "CV_e2e_golden_path",
    "REQ-E2E-ROUTE-PATH-COVERAGE-001": "CW_e2e_route_path_coverage",
    "REQ-EXIT-RUNTIME-TO-REGRESSION-001": "CX_exit_runtime_to_regression",
    "REQ-L6-HUMAN-CALIBRATION-001": "CY_l6_human_calibration",
}

_REFERENCE_ONLY_REQ_IDS: Tuple[str, ...] = (
    "REQ-C0-OVERVIEW-REFERENCE-001",
    "REQ-C0-TRACEABILITY-MATRIX-REF-001",
    "REQ-E2E-OVERVIEW-REFERENCE-001",
    "REQ-E2E-REQ-TO-EVIDENCE-COMPILER-001",
    "REQ-EXIT-OVERVIEW-REFERENCE-001",
    "REQ-L0-OVERVIEW-REFERENCE-001",
    "REQ-L1-OVERVIEW-REFERENCE-001",
    "REQ-L2-COVERAGE-MATRIX-REF-001",
    "REQ-L4-OVERVIEW-REFERENCE-001",
    "REQ-L5-V5-COVERAGE-MATRIX-REF-001",
    "REQ-L6-OVERVIEW-REFERENCE-001",
    "REQ-L6-V6-COVERAGE-MATRIX-REF-001",
    "REQ-PA-OVERVIEW-REFERENCE-001",
    "REQ-PA-TRACEABILITY-MATRIX-REF-001",
    "REQ-U0-OVERVIEW-REFERENCE-001",
)

# ---------------------------------------------------------------------------
# Existing reference mappings (Phase 3). Empty by default. A subsequent
# Tier 6 prompt populates these dicts as static reference modules,
# fixtures, and tests are produced. Until then every row is blocked on
# NEEDS_CODE_REF/NEEDS_VALIDATOR_REF/etc. and the gate fails closed.
# ---------------------------------------------------------------------------

CODE_REFERENCES: Dict[str, Tuple[str, ...]] = {
    **{rid: (_MUST_REFS_MOD,) for rid in _TIER6_MUST_SCENARIOS},
    **{rid: (_REF_REFS_MOD,) for rid in _REFERENCE_ONLY_REQ_IDS},
}

VALIDATOR_REFERENCES: Dict[str, Tuple[str, ...]] = {
    **{rid: (_MUST_REFS_MOD,) for rid in _TIER6_MUST_SCENARIOS},
    **{rid: (_REF_REFS_MOD,) for rid in _REFERENCE_ONLY_REQ_IDS},
}

TEST_REFERENCES: Dict[str, Tuple[str, ...]] = {
    **{rid: (_TIER6_TEST,) for rid in _TIER6_MUST_SCENARIOS},
    **{rid: (_TIER6_TEST,) for rid in _REFERENCE_ONLY_REQ_IDS},
}

ARTIFACT_REFERENCES: Dict[str, Tuple[str, ...]] = {
    **{
        rid: (f"artifacts/runtime/requirements_proof/traces/scenario_{slug}.json",)
        for rid, slug in _TIER6_MUST_SCENARIOS.items()
    },
    **{rid: (_REFERENCE_ONLY_POLICY,) for rid in _REFERENCE_ONLY_REQ_IDS},
}

REPLAY_REFERENCES: Dict[str, Tuple[str, ...]] = {
    rid: (
        f"artifacts/runtime/requirements_proof/replay/replay_{slug}_run_1.json",
        f"artifacts/runtime/requirements_proof/replay/replay_{slug}_run_2.json",
    )
    for rid, slug in _TIER6_MUST_SCENARIOS.items()
}

OTEL_SPAN_REFERENCES: Dict[str, Tuple[str, ...]] = {rid: (_MUST_REFS_MOD,) for rid in _TIER6_MUST_SCENARIOS}

NEGATIVE_CONTROL_REFERENCES: Dict[str, Tuple[str, ...]] = {
    rid: (f"artifacts/runtime/requirements_proof/traces/scenario_{slug}.json",)
    for rid, slug in _TIER6_MUST_SCENARIOS.items()
}


# ---------------------------------------------------------------------------
# Generation pipeline.
# ---------------------------------------------------------------------------


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _filter_existing(paths: Sequence[str]) -> List[str]:
    """Drop paths that do not exist on disk. Never invents files."""
    return [p for p in paths if (REPO_ROOT / p).exists()]


def _filter_matching_req_id(paths: Sequence[str], req_id: str) -> List[str]:
    """Drop JSON paths whose ``step1_req_id`` is present and does not match."""
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
    is_reference_only = selected.get("release_gate_rule") == "NON_BLOCKING_REFERENCE"

    efr = EXPECTED_FAIL_REASONS.get(rid, "").strip()
    if not efr:
        blockers.append("NEEDS_EXPECTED_FAIL_REASON")

    code_refs = _filter_existing(CODE_REFERENCES.get(rid, ()))
    validator_refs = _filter_existing(VALIDATOR_REFERENCES.get(rid, ()))
    test_refs = _filter_existing(TEST_REFERENCES.get(rid, ()))
    artifact_refs = _filter_matching_req_id(_filter_existing(ARTIFACT_REFERENCES.get(rid, ())), rid)
    replay_refs = _filter_matching_req_id(_filter_existing(REPLAY_REFERENCES.get(rid, ())), rid)
    otel_span_refs = _filter_existing(OTEL_SPAN_REFERENCES.get(rid, ()))
    negative_control_refs = _filter_existing(NEGATIVE_CONTROL_REFERENCES.get(rid, ()))

    if not code_refs:
        blockers.append("NEEDS_CODE_REF")
    if not validator_refs:
        blockers.append("NEEDS_VALIDATOR_REF")
    if is_reference_only:
        # Reference-only policy: documentation-integrity contract only.
        # Do NOT require otel/replay/negative_control runtime artifacts.
        # Test + artifact (the policy JSON) are still required so the row
        # is machine-checkable.
        if not test_refs:
            blockers.append("NEEDS_TEST_MAPPING")
        if not artifact_refs:
            blockers.append("NEEDS_ARTIFACT_FIELD")
    else:
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
        "tier": "TIER6",
        "step1_req_id": rid,
        "source_matrix_file": selected["source_matrix_file"],
        "owner_layer": selected["owner_layer"],
        "owner_subsystem": selected["owner_subsystem"],
        "requirement_text": selected["requirement_text"],
        "requirement_strength": selected["requirement_strength"],
        "release_gate_rule": selected["release_gate_rule"],
        "risk_category": selected["risk_category"],
        "why_tier6": selected["why_tier6"],
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
        "tier": "TIER6",
        "surface": surface,
        "purpose": "Tier 6 metadata linkage. Selection-derived; no proof claims.",
        "generated_at": _utc_now_iso(),
        "source_files": {
            "selection": "docs/reference/contracts/tier6/TIER6_SELECTION.json",
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
        "why_tier6",
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
        if row.get("tier") != "TIER6":
            errors.append(f"{row.get('step1_req_id', '?')}: tier!=TIER6")
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
    report_lines.append("# Tier 6 Schema Validation Report")
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
    print(f"Tier 6 row count per file: {len(rows)}")
    print(f"Schema validation: {'OK' if not errors else 'FAILED'}")
    print(f"Linkage status counts: {linkage_counts}")
    print(f"Blocker counts: {blocker_counts}")
    return written


def main() -> int:
    generate()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
