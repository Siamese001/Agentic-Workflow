"""Tier 4 metadata generator.

Reads ``docs/reference/contracts/tier4/TIER4_SELECTION.json`` and emits
the four normalized Tier 4 metadata surfaces plus a schema-validation
report. Phase 3 of Tier 4 Prompt A maps existing references only --
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
SELECTION_PATH = REPO_ROOT / "docs" / "reference" / "contracts" / "tier4" / "TIER4_SELECTION.json"
ARTIFACTS_DIR = REPO_ROOT / "artifacts" / "runtime" / "requirements_proof"

OUT_FILES: Dict[str, str] = {
    "index": "tier4_requirements_index.generated.json",
    "coverage": "tier4_coverage_matrix.generated.json",
    "impl": "tier4_implementation_map.generated.json",
    "artifact": "tier4_artifact_linkage.generated.json",
}
OUT_VALIDATION_REPORT = "tier4_schema_validation_report.md"

# ---------------------------------------------------------------------------
# Stable expected_fail_reason mapping. Populated when the requirement's
# fail-reason code is direct and durable from the REQ_ID + text. Rows
# without an obvious code remain blocked on NEEDS_EXPECTED_FAIL_REASON.
# ---------------------------------------------------------------------------

EXPECTED_FAIL_REASONS: Dict[str, str] = {
    "REQ-L5-AUTHORITY-REGISTRY-BIND-001":         "L5_AUTHORITY_REGISTRY_BIND_REQUIRED",
    "REQ-L5-RUNTIME-CERT-BIND-001":               "L5_RUNTIME_CERT_BIND_MISSING",
    "REQ-L5-GUARDRAIL-FAMILIES-001":              "L5_GUARDRAIL_FAMILY_MISSING",
    "REQ-L5-GOV-CONTEXT-INVARIANT-001":           "L5_GOV_CONTEXT_DRIFT_DETECTED",
    "REQ-UWG-DURABLE-WRITE-CTX-INVARIANT-001":    "UWG_DURABLE_WRITE_CTX_VIOLATION",
    "REQ-L4-POLICY-BLUEPRINT-STATE-001":          "L4_POLICY_BLUEPRINT_MUTATION_REJECTED",
    "REQ-GATE-LAYER-INVOCATION-MAP-001":          "GATE_LAYER_INVOCATION_MAP_MISSING",
    "REQ-U0-IDENTITY-TENANT-SESSION-001":         "U0_IDENTITY_TENANT_SESSION_REQUIRED",
    "REQ-U0-QUOTA-BASELINE-001":                  "U0_QUOTA_BASELINE_DRIFT_DETECTED",
    "REQ-U0-SCHEMA-NORMALIZATION-001":            "U0_SCHEMA_NORMALIZATION_REJECTED",
    "REQ-L1-INTENT-FRAME-001":                    "L1_INTENT_FRAME_MISSING",
    "REQ-L1-PLANNING-PRIORS-001":                 "L1_PLANNING_PRIORS_DRIFT_DETECTED",
    "REQ-L0-ROUTE-INPUT-PREFLIGHT-001":           "L0_ROUTE_INPUT_PREFLIGHT_REJECTED",
    "REQ-L0-CACHE-FALLBACK-HITL-001":             "L0_CACHE_FALLBACK_HITL_VIOLATION",
    "REQ-L0-ROUTECONTRACT-TELEMETRY-001":         "L0_ROUTECONTRACT_TELEMETRY_MISSING",
    "REQ-L3-MANAGED-WORKFLOW-001":                "L3_MANAGED_WORKFLOW_REJECTED",
    "REQ-C0-RETRIEVAL-PLAN-001":                  "C0_RETRIEVAL_PLAN_VIOLATION",
    "REQ-PA-LOAD-RESOLVE-BOM-001":                "PA_BOM_RESOLUTION_REJECTED",
    "REQ-PA-TOKEN-BUDGET-DETERMINISM-001":        "PA_TOKEN_BUDGET_DRIFT_DETECTED",
    "REQ-L2-E1-FROZEN-ROOM-001":                  "L2_FROZEN_ROOM_MUTATION_REJECTED",
    "REQ-L2-E5-SEAL-DISPATCH-001":                "L2_SEAL_DISPATCH_VIOLATION",
    "REQ-L2-SEQUENCER-CONTRACT-001":              "L2_SEQUENCER_CONTRACT_VIOLATION",
    "REQ-EXIT-HITL-FREEZE-001":                   "EXIT_HITL_FREEZE_BYPASS_BLOCKED",
    "REQ-L6-RUNTIME-EXHAUST-INGEST-001":          "L6_RUNTIME_EXHAUST_INGEST_LOSSY",
    "REQ-E2E-EVIDENCE-GROUNDEDNESS-001":          "E2E_EVIDENCE_GROUNDEDNESS_MISSING",
}

# ---------------------------------------------------------------------------
# Existing reference mappings (Phase 3). Empty by default. A subsequent
# Tier 4 prompt populates these dicts as static reference modules,
# fixtures, and tests are produced. Until then every row is blocked on
# NEEDS_CODE_REF/NEEDS_VALIDATOR_REF/etc. and the gate fails closed.
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Cluster mapping (Tier 4 Prompt B). Each REQ_ID maps to its cluster's
# static reference module. The same module is used for code/validator/
# otel_span/negative_control because it declares all four kinds of
# static metadata. Trace + replay fixtures live under traces/ and replay/.
# ---------------------------------------------------------------------------

_CLUSTER_REFS_DIR = "agentic_core/runtime/prove_requirements/tier4_cluster_refs"
_TRACES_DIR = "artifacts/runtime/requirements_proof/traces"
_REPLAY_DIR = "artifacts/runtime/requirements_proof/replay"
_TIER4_TEST = "tests/runtime/test_tier4_cluster_fixtures.py"

# (req_id, scenario_letters, scenario_slug, cluster_module_basename)
_TIER4_ROW_MAP: Tuple[Tuple[str, str, str, str], ...] = (
    ("REQ-L5-AUTHORITY-REGISTRY-BIND-001",        "AV", "l5_authority_registry_bind",      "governance_state_refs.py"),
    ("REQ-L5-RUNTIME-CERT-BIND-001",              "AW", "l5_runtime_cert_bind",            "governance_state_refs.py"),
    ("REQ-L5-GUARDRAIL-FAMILIES-001",             "AX", "l5_guardrail_families",           "governance_state_refs.py"),
    ("REQ-L5-GOV-CONTEXT-INVARIANT-001",          "AY", "l5_gov_context_invariant",        "governance_state_refs.py"),
    ("REQ-UWG-DURABLE-WRITE-CTX-INVARIANT-001",   "AZ", "uwg_durable_write_ctx_invariant", "governance_state_refs.py"),
    ("REQ-L4-POLICY-BLUEPRINT-STATE-001",         "BA", "l4_policy_blueprint_state",       "governance_state_refs.py"),
    ("REQ-GATE-LAYER-INVOCATION-MAP-001",         "BB", "gate_layer_invocation_map",       "governance_state_refs.py"),
    ("REQ-U0-IDENTITY-TENANT-SESSION-001",        "BC", "u0_identity_tenant_session",      "planning_routing_refs.py"),
    ("REQ-U0-QUOTA-BASELINE-001",                 "BD", "u0_quota_baseline",               "planning_routing_refs.py"),
    ("REQ-U0-SCHEMA-NORMALIZATION-001",           "BE", "u0_schema_normalization",         "planning_routing_refs.py"),
    ("REQ-L1-INTENT-FRAME-001",                   "BF", "l1_intent_frame",                 "planning_routing_refs.py"),
    ("REQ-L1-PLANNING-PRIORS-001",                "BG", "l1_planning_priors",              "planning_routing_refs.py"),
    ("REQ-L0-ROUTE-INPUT-PREFLIGHT-001",          "BH", "l0_route_input_preflight",        "planning_routing_refs.py"),
    ("REQ-L0-CACHE-FALLBACK-HITL-001",            "BI", "l0_cache_fallback_hitl",          "planning_routing_refs.py"),
    ("REQ-L0-ROUTECONTRACT-TELEMETRY-001",        "BJ", "l0_routecontract_telemetry",      "planning_routing_refs.py"),
    ("REQ-L3-MANAGED-WORKFLOW-001",               "BK", "l3_managed_workflow",             "planning_routing_refs.py"),
    ("REQ-C0-RETRIEVAL-PLAN-001",                 "BL", "c0_retrieval_plan",               "execution_output_refs.py"),
    ("REQ-PA-LOAD-RESOLVE-BOM-001",               "BM", "pa_load_resolve_bom",             "execution_output_refs.py"),
    ("REQ-PA-TOKEN-BUDGET-DETERMINISM-001",       "BN", "pa_token_budget_determinism",     "execution_output_refs.py"),
    ("REQ-L2-E1-FROZEN-ROOM-001",                 "BO", "l2_e1_frozen_room",               "execution_output_refs.py"),
    ("REQ-L2-E5-SEAL-DISPATCH-001",               "BP", "l2_e5_seal_dispatch",             "execution_output_refs.py"),
    ("REQ-L2-SEQUENCER-CONTRACT-001",             "BQ", "l2_sequencer_contract",           "execution_output_refs.py"),
    ("REQ-EXIT-HITL-FREEZE-001",                  "BR", "exit_hitl_freeze",                "execution_output_refs.py"),
    ("REQ-L6-RUNTIME-EXHAUST-INGEST-001",         "BS", "l6_runtime_exhaust_ingest",       "execution_output_refs.py"),
    ("REQ-E2E-EVIDENCE-GROUNDEDNESS-001",         "BT", "e2e_evidence_groundedness",       "execution_output_refs.py"),
)


def _cluster_module_path(basename: str) -> str:
    return f"{_CLUSTER_REFS_DIR}/{basename}"


def _trace_path(letters: str, slug: str) -> str:
    return f"{_TRACES_DIR}/scenario_{letters}_{slug}.json"


def _replay_pair(letters: str, slug: str) -> Tuple[str, str]:
    return (
        f"{_REPLAY_DIR}/replay_{letters}_{slug}_run_1.json",
        f"{_REPLAY_DIR}/replay_{letters}_{slug}_run_2.json",
    )


CODE_REFERENCES: Dict[str, Tuple[str, ...]] = {
    rid: (_cluster_module_path(mod),) for rid, _l, _s, mod in _TIER4_ROW_MAP
}
VALIDATOR_REFERENCES: Dict[str, Tuple[str, ...]] = {
    rid: (_cluster_module_path(mod),) for rid, _l, _s, mod in _TIER4_ROW_MAP
}
OTEL_SPAN_REFERENCES: Dict[str, Tuple[str, ...]] = {
    rid: (_cluster_module_path(mod),) for rid, _l, _s, mod in _TIER4_ROW_MAP
}
NEGATIVE_CONTROL_REFERENCES: Dict[str, Tuple[str, ...]] = {
    rid: (_cluster_module_path(mod),) for rid, _l, _s, mod in _TIER4_ROW_MAP
}
TEST_REFERENCES: Dict[str, Tuple[str, ...]] = {
    rid: (_TIER4_TEST,) for rid, _l, _s, _m in _TIER4_ROW_MAP
}
ARTIFACT_REFERENCES: Dict[str, Tuple[str, ...]] = {
    rid: (_trace_path(letters, slug),) for rid, letters, slug, _m in _TIER4_ROW_MAP
}
REPLAY_REFERENCES: Dict[str, Tuple[str, ...]] = {
    rid: _replay_pair(letters, slug) for rid, letters, slug, _m in _TIER4_ROW_MAP
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
        "tier": "TIER4",
        "step1_req_id": rid,
        "source_matrix_file": selected["source_matrix_file"],
        "owner_layer": selected["owner_layer"],
        "owner_subsystem": selected["owner_subsystem"],
        "requirement_text": selected["requirement_text"],
        "requirement_strength": selected["requirement_strength"],
        "release_gate_rule": selected["release_gate_rule"],
        "risk_category": selected["risk_category"],
        "why_tier4": selected["why_tier4"],
        "_tier4_cluster_module": next(
            (mod for rid_, _l, _s, mod in _TIER4_ROW_MAP if rid_ == rid),
            "",
        ),
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
        "tier": "TIER4",
        "surface": surface,
        "purpose": "Tier 4 metadata linkage. Selection-derived; no proof claims.",
        "generated_at": _utc_now_iso(),
        "source_files": {
            "selection": "docs/reference/contracts/tier4/TIER4_SELECTION.json",
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
        "why_tier4",
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
        if row.get("tier") != "TIER4":
            errors.append(f"{row.get('step1_req_id', '?')}: tier!=TIER4")
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
    report_lines.append("# Tier 4 Schema Validation Report")
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
    print(f"Tier 4 row count per file: {len(rows)}")
    print(f"Schema validation: {'OK' if not errors else 'FAILED'}")
    print(f"Linkage status counts: {linkage_counts}")
    print(f"Blocker counts: {blocker_counts}")
    return written


def main() -> int:
    generate()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
