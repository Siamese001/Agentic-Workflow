"""Tier 1 metadata generator.

Reads the Tier 1 selection (`docs/reference/contracts/tier1/TIER1_SELECTION.json`)
and emits four normalized metadata-surface files plus a schema validation
report under ``artifacts/runtime/requirements_proof/``.

This is metadata/linkage work only. It does NOT implement runtime behavior,
run tests, run proof harnesses, execute replay, or run OTEL exporters.
It does NOT claim proof, coverage, or readiness.

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
SELECTION_PATH = REPO_ROOT / "docs" / "reference" / "contracts" / "tier1" / "TIER1_SELECTION.json"
ARTIFACTS_DIR = REPO_ROOT / "artifacts" / "runtime" / "requirements_proof"

OUT_FILES: Dict[str, str] = {
    "index": "tier1_requirements_index.generated.json",
    "coverage": "tier1_coverage_matrix.generated.json",
    "impl": "tier1_implementation_map.generated.json",
    "artifact": "tier1_artifact_linkage.generated.json",
}
OUT_VALIDATION_REPORT = "tier1_schema_validation_report.md"

# ---------------------------------------------------------------------------
# Stable expected_fail_reason mapping. Only populated when the requirement's
# failure mode is obvious from the REQ_ID + requirement text. If it is not
# obvious, the row keeps the NEEDS_EXPECTED_FAIL_REASON blocker rather than
# inventing an obscure code.
# ---------------------------------------------------------------------------
EXPECTED_FAIL_REASONS: Mapping[str, str] = {
    "REQ-L4-NO-DIRECT-WRITE-FROM-L2-001": "DIRECT_L4_WRITE_BLOCKED",
    "REQ-L4-NO-DIRECT-WRITE-FROM-L6-001": "DIRECT_L4_WRITE_BLOCKED",
    "REQ-UWG-OBS-ANTI-BYPASS-001": "UWG_BYPASS_WRITE_BLOCKED",
    "REQ-GATE-OBS-ANTI-BYPASS-001": "RUNTIME_GATE_BYPASS_BLOCKED",
    "REQ-L5-ORIGIN-TRUST-BOUNDARY-001": "PROMPT_BOUNDARY_VIOLATION_BLOCKED",
    "REQ-PA-AUTHORITY-REDTEAM-001": "PROMPT_BOUNDARY_VIOLATION_BLOCKED",
    "REQ-C0-OBS-ANTI-BYPASS-001": "C0_EVIDENCE_CONTRACT_BYPASS_BLOCKED",
    "REQ-L2-OBS-ANTI-BYPASS-001": "ANTI_BYPASS_CONTROL_MISSING",
    "REQ-PA-FINAL-EMIT-ARTIFACT-001": "ARTIFACT_INTEGRITY_MISMATCH",
    "REQ-EXIT-X1G-X1I-REPLAY-001": "REPLAY_INTEGRITY_MISMATCH",
    "REQ-L4-REPLAY-SNAPSHOT-AUDIT-001": "REPLAY_INTEGRITY_MISMATCH",
    "REQ-L6-GAUNTLET-FUTURE-RUN-001": "L6_CURRENT_RUN_MUTATION_BLOCKED",
    "REQ-EXIT-OBS-ANTI-BYPASS-001": "ANTI_BYPASS_CONTROL_MISSING",
    # The following are intentionally OMITTED because their failure code is
    # not obvious from the requirement text alone — they keep the
    # NEEDS_EXPECTED_FAIL_REASON blocker:
    #   REQ-L5-SAFETY-ENFORCE-PLANE-001
    #   REQ-L5-STATIC-GOV-DRIFT-001
}

# ---------------------------------------------------------------------------
# On-disk reference candidates. Every path MUST exist (validated at build
# time). Empty tuples → no reference for that REQ; the corresponding NEEDS_*
# blocker remains.
# ---------------------------------------------------------------------------
_TRACES = "artifacts/runtime/requirements_proof/traces"
_REPLAY = "artifacts/runtime/requirements_proof/replay"
_PROOF = "artifacts/runtime/requirements_proof"

# The anti_bypass scenario D artifacts and tests demonstrate UWG bypass
# detection, which is exactly what the three write_sovereignty Tier 1 rows
# are about. They are referenced (not invented).
_ANTI_BYPASS_ARTIFACTS: Tuple[str, ...] = (
    f"{_TRACES}/scenario_D_anti_bypass.json",
    f"{_PROOF}/anti_bypass_results.json",
)
_ANTI_BYPASS_REPLAY: Tuple[str, ...] = (
    f"{_REPLAY}/replay_D_anti_bypass_run_1.json",
    f"{_REPLAY}/replay_D_anti_bypass_run_2.json",
)
_ANTI_BYPASS_TESTS: Tuple[str, ...] = (
    "tests/runtime/test_uwg_write_sovereignty.py",
    "tests/runtime/test_anti_bypass_runtime_cheat_proof.py",
    "tests/unit/L6_observability/shadow_eval/test_06_8_anti_bypass.py",
)
_ANTI_BYPASS_NEGATIVE_CONTROLS: Tuple[str, ...] = (f"{_PROOF}/anti_bypass_results.json",)

TEST_REFERENCES: Mapping[str, Sequence[str]] = {
    "REQ-L4-NO-DIRECT-WRITE-FROM-L2-001": _ANTI_BYPASS_TESTS,
    "REQ-L4-NO-DIRECT-WRITE-FROM-L6-001": _ANTI_BYPASS_TESTS,
    "REQ-UWG-OBS-ANTI-BYPASS-001": _ANTI_BYPASS_TESTS,
}
ARTIFACT_REFERENCES: Mapping[str, Sequence[str]] = {
    "REQ-L4-NO-DIRECT-WRITE-FROM-L2-001": _ANTI_BYPASS_ARTIFACTS,
    "REQ-L4-NO-DIRECT-WRITE-FROM-L6-001": _ANTI_BYPASS_ARTIFACTS,
    "REQ-UWG-OBS-ANTI-BYPASS-001": _ANTI_BYPASS_ARTIFACTS,
}
REPLAY_REFERENCES: Mapping[str, Sequence[str]] = {
    "REQ-L4-NO-DIRECT-WRITE-FROM-L2-001": _ANTI_BYPASS_REPLAY,
    "REQ-L4-NO-DIRECT-WRITE-FROM-L6-001": _ANTI_BYPASS_REPLAY,
    "REQ-UWG-OBS-ANTI-BYPASS-001": _ANTI_BYPASS_REPLAY,
}
NEGATIVE_CONTROL_REFERENCES: Mapping[str, Sequence[str]] = {
    "REQ-L4-NO-DIRECT-WRITE-FROM-L2-001": _ANTI_BYPASS_NEGATIVE_CONTROLS,
    "REQ-L4-NO-DIRECT-WRITE-FROM-L6-001": _ANTI_BYPASS_NEGATIVE_CONTROLS,
    "REQ-UWG-OBS-ANTI-BYPASS-001": _ANTI_BYPASS_NEGATIVE_CONTROLS,
}

# Code references, validator references, and OTEL span refs are not yet
# mapped for any Tier 1 row — those gaps are tracked via blockers.
CODE_REFERENCES: Mapping[str, Sequence[str]] = {}
VALIDATOR_REFERENCES: Mapping[str, Sequence[str]] = {}
OTEL_SPAN_REFERENCES: Mapping[str, Sequence[str]] = {}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _filter_existing(paths: Sequence[str]) -> List[str]:
    """Drop paths that do not exist on disk. Never invents files."""
    return [p for p in paths if (REPO_ROOT / p).exists()]


def _load_selection() -> Dict[str, Any]:
    return json.loads(SELECTION_PATH.read_text(encoding="utf-8"))


def _is_applicable(gap_value: str) -> bool:
    """A gap field marks evidence as applicable unless it is NOT_APPLICABLE."""
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
    artifact_refs = _filter_existing(ARTIFACT_REFERENCES.get(rid, ()))
    replay_refs = _filter_existing(REPLAY_REFERENCES.get(rid, ()))
    otel_span_refs = list(OTEL_SPAN_REFERENCES.get(rid, ()))
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

    # Linkage classification.
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
        "tier": "TIER1",
        "step1_req_id": rid,
        "source_matrix_file": selected["source_matrix_file"],
        "owner_layer": selected["owner_layer"],
        "owner_subsystem": selected["owner_subsystem"],
        "requirement_text": selected["requirement_text"],
        "requirement_strength": selected["requirement_strength"],
        "release_gate_rule": selected["release_gate_rule"],
        "risk_category": selected["risk_category"],
        "why_tier1": selected["why_tier1"],
        "expected_fail_reason": efr,
        "linkage_status": linkage_status,
        "blockers": blockers,
        "code_refs": code_refs,
        "validator_refs": validator_refs,
        "test_refs": test_refs,
        "artifact_refs": artifact_refs,
        "replay_refs": replay_refs,
        "otel_span_refs": otel_span_refs,
        "negative_control_refs": negative_control_refs,
    }


def _build_rows() -> List[Dict[str, Any]]:
    selection = _load_selection()
    return [_build_row(sel) for sel in selection["selected"]]


def _surface_payload(surface: str, rows: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "tier": "TIER1",
        "surface": surface,
        "purpose": ("Tier 1 metadata linkage. Selection-derived; no proof claims."),
        "generated_at": _utc_now_iso(),
        "source_files": {
            "selection": "docs/reference/contracts/tier1/TIER1_SELECTION.json",
            "step1_matrices_dir": "docs/reference/contracts/step1/",
        },
        "row_count": len(rows),
        "rows": list(rows),
    }


def _validate(rows: Sequence[Mapping[str, Any]]) -> Tuple[List[str], Dict[str, int], Dict[str, int]]:
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
        "why_tier1",
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
        if row.get("tier") != "TIER1":
            errors.append(f"{row.get('step1_req_id', '?')}: tier!=TIER1")
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
    report_lines.append("# Tier 1 Schema Validation Report")
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
    print(f"Tier 1 row count per file: {len(rows)}")
    print(f"Schema validation: {'OK' if not errors else 'FAILED'}")
    print(f"Linkage status counts: {linkage_counts}")
    print(f"Blocker counts: {blocker_counts}")
    return written


def main() -> int:
    generate()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
