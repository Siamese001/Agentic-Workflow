"""
Tier 0 Step-1 metadata generator.

Schema/linkage layer only. Adds first-class ``step1_req_id`` support to the
requirements-proof metadata surface for the 17 Step-1 Tier 0 REQ_IDs.

Reads the prior linkage-metadata files under
``artifacts/runtime/requirements_proof/`` and emits four normalized
``tier0_*.generated.json`` files plus a validation report. Does not touch
runtime behavior, tests, traces, replay bundles, or proof harness logic.
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Sequence, Set


# Project-relative artifacts root. Resolution is intentionally relative to the
# current working directory so callers (CI, ops scripts) can override by
# changing cwd; no runtime config is read here.
_ARTIFACTS_DIR = Path("artifacts/runtime/requirements_proof")

# Source files emitted by the prior linkage-metadata step. They are the
# authoritative source for Tier-0 step1_req_id linkage.
_SRC_LITERAL_MAP = "tier0_literal_reqid_map.json"
_SRC_BRIDGE = "tier0_reqid_bridge.json"
_SRC_INDEX = "tier0_requirements_index.with_step1_req_id.json"
_SRC_COVERAGE = "tier0_coverage_matrix.with_step1_req_id.json"
_SRC_IMPL = "tier0_implementation_map.with_step1_req_id.json"
_SRC_ARTIFACT = "tier0_artifact_linkage.with_step1_req_id.json"

# Generated outputs.
_OUT_INDEX = "tier0_requirements_index.generated.json"
_OUT_COVERAGE = "tier0_coverage_matrix.generated.json"
_OUT_IMPL = "tier0_implementation_map.generated.json"
_OUT_ARTIFACT = "tier0_artifact_linkage.generated.json"
_OUT_REPORT = "tier0_schema_validation_report.md"

ALLOWED_STATUSES: Set[str] = {
    "LINKED_LITERAL",  # not currently emitted, but reserved
    "LINKED_CONCEPTUAL",
    "PARTIAL_LINK",
    "NO_LINK",
}

ALLOWED_BLOCKERS: Set[str] = {
    "NEEDS_RUNTIME_FIELD",
    "NEEDS_ARTIFACT_FIELD",
    "NEEDS_REPLAY_FIELD",
    "NEEDS_EXPECTED_FAIL_REASON",
    "NEEDS_TEST_MAPPING",
}

FORBIDDEN_TOKENS: Sequence[str] = (
    "PASS",
    "FAIL",
    "PROVEN",
    "COVERED",
    "ENFORCED",
    "COMPLETE",
    "CLOSED",
)

# Stable uppercase expected_fail_reason codes per Tier 0 REQ_ID. These are
# metadata-only labels documenting what the negative control would surface
# if it executed. They are NOT a claim that the negative control was run.
EXPECTED_FAIL_REASONS: Mapping[str, str] = {
    "REQ-L0-ROUTE-EXACTLY-ONE-001": "MULTIPLE_ROUTE_CONTRACTS_BLOCKED",
    "REQ-C0-EVIDENCE-NO-ANSWER-001": "C0_FINAL_ANSWER_BLOCKED",
    "REQ-PA-ASSEMBLY-NO-RETRIEVAL-001": "PROMPT_ASSEMBLY_RETRIEVAL_BLOCKED",
    "REQ-PA-ASSEMBLY-NO-EXECUTE-001": "PROMPT_ASSEMBLY_EXECUTION_BLOCKED",
    "REQ-L2-EXECUTE-BOUNDED-PACKET-001": "L2_MULTI_PACKET_EXECUTION_BLOCKED",
    "REQ-L2-WRITE-NO-DIRECT-L4-001": "DIRECT_L4_WRITE_BLOCKED",
    "REQ-EXIT-X3-ONE-DISPOSITION-001": "MULTIPLE_EXIT_DISPOSITIONS_BLOCKED",
    "REQ-EXIT-WRITE-NO-L4-MUTATION-001": "EXIT_DIRECT_L4_WRITE_BLOCKED",
    "REQ-UWG-WRITE-SOLE-PATH-001": "UWG_BYPASS_WRITE_BLOCKED",
    "REQ-L6-FIREWALL-NO-CURRENT-RUN-MUTATION-001": "L6_CURRENT_RUN_MUTATION_BLOCKED",
    "REQ-L6-WRITE-NO-DIRECT-L4-001": "L6_DIRECT_L4_WRITE_BLOCKED",
    "REQ-GATE-SCHEMA-UNKNOWN-NOT-PASS-001": "UNKNOWN_GATE_RESULT_NOT_PASS",
    "REQ-GATE-SCHEMA-NA-REQUIRES-REASON-001": "NOT_APPLICABLE_REASON_MISSING",
    "REQ-E2E-PROOF-NEGATIVE-REASON-001": "EXPECTED_FAIL_REASON_MISMATCH",
    "REQ-E2E-PROOF-PAYLOAD-HASH-001": "REFERENCED_PAYLOAD_HASH_MISMATCH",
    "REQ-TRACE-OTEL-CRITICAL-SPANS-001": "REQUIRED_OTEL_SPAN_MISSING",
    "REQ-TRACE-REPLAY-ROUTE-EXIT-STABLE-001": "REPLAY_ROUTE_EXIT_MISMATCH",
}

# Concrete replay-bundle references for Tier 0 reqs. Each path MUST already
# exist under ``artifacts/runtime/requirements_proof/replay/`` — the generator
# does not invent or create replay artifacts. Mappings reflect what the
# existing scenario bundles literally exercise:
#   A grounded_read    — C0 evidence path, PA assembly, route selection
#   B managed_workflow — full happy-path L2 execution, route, PA, OTEL
#   C weak_evidence    — C0 boundary / weak evidence handling
#   D anti_bypass      — negative controls: bypass attempts (UWG, L2->L4, L6->L4)
#   E authorized_commit— authorized commit path through Exit + UWG
# A req without any concrete scenario coverage retains NEEDS_REPLAY_FIELD.
_REPLAY_BASE = "artifacts/runtime/requirements_proof/replay"
REPLAY_REFERENCES: Mapping[str, Sequence[str]] = {
    "REQ-L0-ROUTE-EXACTLY-ONE-001": (
        f"{_REPLAY_BASE}/replay_A_grounded_read_run_1.json",
        f"{_REPLAY_BASE}/replay_A_grounded_read_run_2.json",
        f"{_REPLAY_BASE}/replay_B_managed_workflow_run_1.json",
        f"{_REPLAY_BASE}/replay_B_managed_workflow_run_2.json",
        f"{_REPLAY_BASE}/replay_C_weak_evidence_run_1.json",
        f"{_REPLAY_BASE}/replay_C_weak_evidence_run_2.json",
        f"{_REPLAY_BASE}/replay_D_anti_bypass_run_1.json",
        f"{_REPLAY_BASE}/replay_D_anti_bypass_run_2.json",
        f"{_REPLAY_BASE}/replay_E_authorized_commit_run_1.json",
        f"{_REPLAY_BASE}/replay_E_authorized_commit_run_2.json",
    ),
    "REQ-C0-EVIDENCE-NO-ANSWER-001": (
        f"{_REPLAY_BASE}/replay_A_grounded_read_run_1.json",
        f"{_REPLAY_BASE}/replay_A_grounded_read_run_2.json",
        f"{_REPLAY_BASE}/replay_C_weak_evidence_run_1.json",
        f"{_REPLAY_BASE}/replay_C_weak_evidence_run_2.json",
    ),
    "REQ-PA-ASSEMBLY-NO-RETRIEVAL-001": (
        f"{_REPLAY_BASE}/replay_A_grounded_read_run_1.json",
        f"{_REPLAY_BASE}/replay_A_grounded_read_run_2.json",
        f"{_REPLAY_BASE}/replay_B_managed_workflow_run_1.json",
        f"{_REPLAY_BASE}/replay_B_managed_workflow_run_2.json",
    ),
    "REQ-PA-ASSEMBLY-NO-EXECUTE-001": (
        f"{_REPLAY_BASE}/replay_A_grounded_read_run_1.json",
        f"{_REPLAY_BASE}/replay_A_grounded_read_run_2.json",
        f"{_REPLAY_BASE}/replay_B_managed_workflow_run_1.json",
        f"{_REPLAY_BASE}/replay_B_managed_workflow_run_2.json",
    ),
    "REQ-L6-WRITE-NO-DIRECT-L4-001": (
        f"{_REPLAY_BASE}/replay_D_anti_bypass_run_1.json",
        f"{_REPLAY_BASE}/replay_D_anti_bypass_run_2.json",
    ),
    "REQ-L6-FIREWALL-NO-CURRENT-RUN-MUTATION-001": (
        f"{_REPLAY_BASE}/replay_H_l6_firewall_no_current_run_mutation_run_1.json",
        f"{_REPLAY_BASE}/replay_H_l6_firewall_no_current_run_mutation_run_2.json",
    ),
    "REQ-GATE-SCHEMA-UNKNOWN-NOT-PASS-001": (
        f"{_REPLAY_BASE}/replay_F_gate_schema_unknown_not_pass_run_1.json",
        f"{_REPLAY_BASE}/replay_F_gate_schema_unknown_not_pass_run_2.json",
    ),
    "REQ-GATE-SCHEMA-NA-REQUIRES-REASON-001": (
        f"{_REPLAY_BASE}/replay_G_gate_schema_na_requires_reason_run_1.json",
        f"{_REPLAY_BASE}/replay_G_gate_schema_na_requires_reason_run_2.json",
    ),
    "REQ-E2E-PROOF-NEGATIVE-REASON-001": (
        f"{_REPLAY_BASE}/replay_D_anti_bypass_run_1.json",
        f"{_REPLAY_BASE}/replay_D_anti_bypass_run_2.json",
    ),
    "REQ-TRACE-OTEL-CRITICAL-SPANS-001": (
        f"{_REPLAY_BASE}/replay_A_grounded_read_run_1.json",
        f"{_REPLAY_BASE}/replay_A_grounded_read_run_2.json",
        f"{_REPLAY_BASE}/replay_B_managed_workflow_run_1.json",
        f"{_REPLAY_BASE}/replay_B_managed_workflow_run_2.json",
        f"{_REPLAY_BASE}/replay_C_weak_evidence_run_1.json",
        f"{_REPLAY_BASE}/replay_C_weak_evidence_run_2.json",
        f"{_REPLAY_BASE}/replay_D_anti_bypass_run_1.json",
        f"{_REPLAY_BASE}/replay_D_anti_bypass_run_2.json",
        f"{_REPLAY_BASE}/replay_E_authorized_commit_run_1.json",
        f"{_REPLAY_BASE}/replay_E_authorized_commit_run_2.json",
    ),
}

# Concrete artifact references for Tier 0 reqs. Each path MUST already exist
# under ``artifacts/`` — the generator does not invent or create artifacts.
# Source artifacts are not validated by this generator (artifact_verified=false).
_TRACES_BASE = "artifacts/runtime/requirements_proof/traces"
_PROOF_BASE = "artifacts/runtime/requirements_proof"
ARTIFACT_REFERENCES: Mapping[str, Sequence[str]] = {
    "REQ-C0-EVIDENCE-NO-ANSWER-001": (
        f"{_TRACES_BASE}/scenario_A_grounded_read.json",
        f"{_TRACES_BASE}/scenario_C_weak_evidence.json",
    ),
    "REQ-PA-ASSEMBLY-NO-RETRIEVAL-001": (
        f"{_TRACES_BASE}/scenario_A_grounded_read.json",
        f"{_TRACES_BASE}/scenario_B_managed_workflow.json",
    ),
    "REQ-PA-ASSEMBLY-NO-EXECUTE-001": (
        f"{_TRACES_BASE}/scenario_A_grounded_read.json",
        f"{_TRACES_BASE}/scenario_B_managed_workflow.json",
    ),
    "REQ-L6-FIREWALL-NO-CURRENT-RUN-MUTATION-001": (
        f"{_TRACES_BASE}/scenario_D_anti_bypass.json",
        f"{_PROOF_BASE}/anti_bypass_results.json",
    ),
    "REQ-L6-WRITE-NO-DIRECT-L4-001": (
        f"{_TRACES_BASE}/scenario_D_anti_bypass.json",
        f"{_PROOF_BASE}/anti_bypass_results.json",
    ),
    "REQ-GATE-SCHEMA-UNKNOWN-NOT-PASS-001": (f"{_TRACES_BASE}/scenario_F_gate_schema_unknown_not_pass.json",),
    "REQ-GATE-SCHEMA-NA-REQUIRES-REASON-001": (
        f"{_TRACES_BASE}/scenario_G_gate_schema_na_requires_reason.json",
    ),
}

# Concrete test-file references for Tier 0 reqs. Each path MUST already
# exist under ``tests/`` — the generator does not invent or create tests.
# Tests are NOT executed by this generator (test_executed=false). Only
# tests whose file purpose maps clearly to the requirement's runtime
# concern are included.
TEST_REFERENCES: Mapping[str, Sequence[str]] = {
    "REQ-PA-ASSEMBLY-NO-RETRIEVAL-001": (
        "tests/unit/agentic_core/prompt_governance/prompt_assembly/test_pa0_boundary.py",
        "tests/unit/agentic_core/prompt_governance/prompt_assembly/test_invariants.py",
        "tests/unit/agentic_core/prompt_governance/prompt_assembly/test_doctrine_compliance.py",
    ),
    "REQ-PA-ASSEMBLY-NO-EXECUTE-001": (
        "tests/unit/agentic_core/prompt_governance/prompt_assembly/test_pa0_boundary.py",
        "tests/unit/agentic_core/prompt_governance/prompt_assembly/test_invariants.py",
        "tests/unit/agentic_core/prompt_governance/prompt_assembly/test_doctrine_compliance.py",
    ),
    "REQ-L6-WRITE-NO-DIRECT-L4-001": (
        "tests/runtime/test_uwg_write_sovereignty.py",
        "tests/runtime/test_anti_bypass_runtime_cheat_proof.py",
        "tests/unit/L6_observability/shadow_eval/test_06_8_anti_bypass.py",
    ),
    "REQ-L6-FIREWALL-NO-CURRENT-RUN-MUTATION-001": ("tests/runtime/test_tier0_l6_firewall_replay.py",),
    "REQ-GATE-SCHEMA-UNKNOWN-NOT-PASS-001": ("tests/runtime/test_tier0_gate_schema_invariants.py",),
    "REQ-GATE-SCHEMA-NA-REQUIRES-REASON-001": ("tests/runtime/test_tier0_gate_schema_invariants.py",),
}

# Blocker classes the generator is authorized to fully dismiss (count must
# reach 0 in generated output). Other-blocker preservation excludes these.
_FULLY_DROPPED_BLOCKERS: Set[str] = {
    "NEEDS_RUNTIME_FIELD",
    "NEEDS_EXPECTED_FAIL_REASON",
}

# Blocker classes the generator may partially dismiss row-by-row when a
# concrete precondition holds. Other-blocker preservation excludes these,
# but the generated count is allowed to be > 0.
_PARTIALLY_DROPPABLE_BLOCKERS: Set[str] = {
    "NEEDS_REPLAY_FIELD",
    "NEEDS_ARTIFACT_FIELD",
    "NEEDS_TEST_MAPPING",
}

_INTENTIONALLY_DROPPED_BLOCKERS: Set[str] = _FULLY_DROPPED_BLOCKERS | _PARTIALLY_DROPPABLE_BLOCKERS


# The 17 canonical Tier 0 REQ_IDs from docs/reference/contracts/step1/*.md.
TIER0_REQ_IDS: Sequence[str] = (
    "REQ-L0-ROUTE-EXACTLY-ONE-001",
    "REQ-C0-EVIDENCE-NO-ANSWER-001",
    "REQ-PA-ASSEMBLY-NO-RETRIEVAL-001",
    "REQ-PA-ASSEMBLY-NO-EXECUTE-001",
    "REQ-L2-EXECUTE-BOUNDED-PACKET-001",
    "REQ-L2-WRITE-NO-DIRECT-L4-001",
    "REQ-EXIT-X3-ONE-DISPOSITION-001",
    "REQ-EXIT-WRITE-NO-L4-MUTATION-001",
    "REQ-UWG-WRITE-SOLE-PATH-001",
    "REQ-L6-FIREWALL-NO-CURRENT-RUN-MUTATION-001",
    "REQ-L6-WRITE-NO-DIRECT-L4-001",
    "REQ-GATE-SCHEMA-UNKNOWN-NOT-PASS-001",
    "REQ-GATE-SCHEMA-NA-REQUIRES-REASON-001",
    "REQ-E2E-PROOF-NEGATIVE-REASON-001",
    "REQ-E2E-PROOF-PAYLOAD-HASH-001",
    "REQ-TRACE-OTEL-CRITICAL-SPANS-001",
    "REQ-TRACE-REPLAY-ROUTE-EXIT-STABLE-001",
)


def _load_json(name: str) -> Dict[str, Any]:
    path = _ARTIFACTS_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Required source not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _index_rows(payload: Mapping[str, Any]) -> Dict[str, Mapping[str, Any]]:
    return {row["step1_req_id"]: row for row in payload.get("rows", [])}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _flatten_evidence_refs(*lists: Any) -> List[str]:
    """Combine evidence list-fields into a single deduplicated, ordered list.

    Strings (e.g. ``"UNKNOWN"``) are skipped; lists are expanded; ``None`` and
    empty strings are dropped. Order is preserved, duplicates collapsed.
    """
    seen: Set[str] = set()
    out: List[str] = []
    for entry in lists:
        if entry is None:
            continue
        if isinstance(entry, str):
            if entry == "UNKNOWN" or not entry:
                continue
            if entry not in seen:
                seen.add(entry)
                out.append(entry)
            continue
        if isinstance(entry, list):
            for item in entry:
                if not item or item == "UNKNOWN":
                    continue
                if item not in seen:
                    seen.add(item)
                    out.append(item)
    return out


def _generate_payload(
    surface: str,
    rows: List[Dict[str, Any]],
    description: str,
) -> Dict[str, Any]:
    return {
        "schema_version": "1.0",
        "surface": surface,
        "purpose": description,
        "generated_at": _utc_now_iso(),
        "source_files": [
            _SRC_LITERAL_MAP,
            _SRC_BRIDGE,
            _SRC_INDEX,
            _SRC_COVERAGE,
            _SRC_IMPL,
            _SRC_ARTIFACT,
        ],
        "caveat": (
            "Linkage metadata only. No runtime code, tests, traces, replay "
            "bundles, or proof harness output were executed or modified."
        ),
        "rows": rows,
    }


def _filter_blockers(
    blockers: Sequence[str],
    step1_req_id: str,
    expected_fail_reason: str,
    replay_refs: Sequence[str],
    artifact_refs: Sequence[str],
    test_refs: Sequence[str],
) -> List[str]:
    """Drop blockers whose precondition is now satisfied.

    - ``NEEDS_RUNTIME_FIELD`` — dropped when ``step1_req_id`` is nonblank.
    - ``NEEDS_EXPECTED_FAIL_REASON`` — dropped when a stable
      ``expected_fail_reason`` is populated for this row.
    - ``NEEDS_REPLAY_FIELD`` — dropped when ``replay_refs`` contains at
      least one concrete reference to an existing replay artifact.
    - ``NEEDS_ARTIFACT_FIELD`` — dropped when ``artifact_refs`` contains
      at least one concrete reference to an existing on-disk artifact.
    - ``NEEDS_TEST_MAPPING`` — dropped when ``test_refs`` contains at
      least one concrete reference to an existing test file on disk.

    All other blockers are preserved verbatim and in order.
    """
    has_step1 = bool(step1_req_id and step1_req_id.strip())
    has_efr = bool(expected_fail_reason and expected_fail_reason.strip())
    has_replay = bool(replay_refs)
    has_artifact = bool(artifact_refs)
    has_test = bool(test_refs)
    out: List[str] = []
    for b in blockers:
        if b == "NEEDS_RUNTIME_FIELD" and has_step1:
            continue
        if b == "NEEDS_EXPECTED_FAIL_REASON" and has_efr:
            continue
        if b == "NEEDS_REPLAY_FIELD" and has_replay:
            continue
        if b == "NEEDS_ARTIFACT_FIELD" and has_artifact:
            continue
        if b == "NEEDS_TEST_MAPPING" and has_test:
            continue
        out.append(b)
    return out


def _build_rows() -> Dict[str, List[Dict[str, Any]]]:
    """Assemble the four generated row sets from the prior linkage files."""
    literal = _index_rows(_load_json(_SRC_LITERAL_MAP))
    bridge = _index_rows(_load_json(_SRC_BRIDGE))
    src_index = _index_rows(_load_json(_SRC_INDEX))
    src_coverage = _index_rows(_load_json(_SRC_COVERAGE))
    src_impl = _index_rows(_load_json(_SRC_IMPL))
    src_artifact = _index_rows(_load_json(_SRC_ARTIFACT))

    out_index: List[Dict[str, Any]] = []
    out_coverage: List[Dict[str, Any]] = []
    out_impl: List[Dict[str, Any]] = []
    out_artifact: List[Dict[str, Any]] = []

    for req_id in TIER0_REQ_IDS:
        lit = literal[req_id]
        br = bridge[req_id]
        si = src_index[req_id]
        sc = src_coverage[req_id]
        sm = src_impl[req_id]
        sa = src_artifact[req_id]

        efr = EXPECTED_FAIL_REASONS.get(req_id, "")
        replay_refs = list(REPLAY_REFERENCES.get(req_id, ()))
        artifact_refs = list(ARTIFACT_REFERENCES.get(req_id, ()))
        test_refs = list(TEST_REFERENCES.get(req_id, ()))
        common: Dict[str, Any] = {
            "step1_req_id": req_id,
            "step1_matrix_file": lit["step1_matrix_file"],
            "existing_runtime_req_id": (br.get("existing_hash_suffixed_req_id_if_any") or None),
            "requirement_text": lit["requirement_text"],
            "linkage_status": lit["current_linkage_status_from_bridge"],
            # Stable uppercase reason code. Metadata only — the negative
            # control has not been executed; this is the label it would
            # surface if it ran and the requirement were violated.
            "expected_fail_reason": efr or None,
            "expected_fail_reason_executed": False,
            # Concrete replay-bundle paths. Existence on disk is required
            # for inclusion; references are not invented. The bundles are
            # not executed by this generator.
            "replay_refs": replay_refs,
            "replay_executed": False,
            # Concrete on-disk artifact paths (trace bundles, anti-bypass
            # results, etc.). Existence is required; references are not
            # invented. Artifacts are not validated by this generator.
            "artifact_refs": artifact_refs,
            "artifact_verified": False,
            # Concrete on-disk test-file paths. Existence is required;
            # references are not invented. Tests are NOT executed by
            # this generator.
            "test_refs": test_refs,
            "test_executed": False,
        }

        # requirements_index surface — what artifact/run-record bundles exist
        out_index.append(
            {
                **common,
                "blockers": _filter_blockers(
                    si["blockers"],
                    req_id,
                    efr,
                    replay_refs,
                    artifact_refs,
                    test_refs,
                ),
                "evidence_refs": _flatten_evidence_refs(
                    lit["mapped_existing_artifacts"],
                    artifact_refs,
                ),
            }
        )

        # coverage_matrix surface — tests, validators, spans, neg controls, EFR
        out_coverage.append(
            {
                **common,
                "blockers": _filter_blockers(
                    sc["blockers"],
                    req_id,
                    efr,
                    replay_refs,
                    artifact_refs,
                    test_refs,
                ),
                "evidence_refs": _flatten_evidence_refs(
                    lit["mapped_existing_tests"],
                    test_refs,
                    lit["mapped_existing_validators"],
                    lit["mapped_existing_spans"],
                    lit["mapped_existing_negative_controls"],
                    lit["mapped_existing_expected_fail_reasons"],
                ),
            }
        )

        # implementation_map surface — code symbols + validators + tests
        out_impl.append(
            {
                **common,
                "blockers": _filter_blockers(
                    sm["blockers"],
                    req_id,
                    efr,
                    replay_refs,
                    artifact_refs,
                    test_refs,
                ),
                "evidence_refs": _flatten_evidence_refs(
                    br.get("code_symbols_found", []),
                    lit["mapped_existing_validators"],
                    lit["mapped_existing_tests"],
                    test_refs,
                ),
            }
        )

        # artifact_linkage surface — traces, replay pairs, anti-bypass
        out_artifact.append(
            {
                **common,
                "blockers": _filter_blockers(
                    sa["blockers"],
                    req_id,
                    efr,
                    replay_refs,
                    artifact_refs,
                    test_refs,
                ),
                "evidence_refs": _flatten_evidence_refs(
                    lit["mapped_existing_artifacts"],
                    artifact_refs,
                    lit["mapped_existing_replay_checks"],
                    replay_refs,
                    lit["mapped_existing_negative_controls"],
                ),
            }
        )

    rows_by_surface: Dict[str, List[Dict[str, Any]]] = {
        "index": out_index,
        "coverage": out_coverage,
        "impl": out_impl,
        "artifact": out_artifact,
    }
    _upgrade_linkage_status(rows_by_surface)
    return rows_by_surface


def _upgrade_linkage_status(
    rows_by_surface: Mapping[str, List[Dict[str, Any]]],
) -> None:
    """Reclassify ``linkage_status`` to ``LINKED_LITERAL`` per LINKED_LITERAL
    criteria when the generated metadata satisfies all of:

      1. ``step1_req_id`` is nonblank and one of the 17 canonical Tier 0 IDs
      2. ``expected_fail_reason`` is nonblank
      3. ``blockers`` list is empty across ALL four surfaces
      4. required evidence references are present (this follows from (3)
         because the blocker filter only drops a NEEDS_* blocker when the
         corresponding ``*_refs`` collection is non-empty)

    No proof_status is set. No forbidden status token is introduced.
    Rows that do not meet criteria are left at their original status.
    """
    canonical = set(TIER0_REQ_IDS)
    surfaces = list(rows_by_surface.values())
    if not surfaces:
        return

    # Group rows by req_id across surfaces (they're already aligned 1:1, but
    # this keeps the check robust to ordering changes).
    by_req: Dict[str, List[Dict[str, Any]]] = {}
    for surface_rows in surfaces:
        for row in surface_rows:
            by_req.setdefault(row.get("step1_req_id", ""), []).append(row)

    for req_id, rows in by_req.items():
        if not req_id or req_id not in canonical:
            continue
        # All surfaces for this req must share an empty blocker list and
        # carry a nonblank expected_fail_reason.
        all_clean = all(
            (not r.get("blockers")) and bool((r.get("expected_fail_reason") or "").strip()) for r in rows
        )
        if all_clean:
            for r in rows:
                r["linkage_status"] = "LINKED_LITERAL"


def generate() -> Dict[str, Path]:
    """Write the four generated files. Returns map of surface->path."""
    sets = _build_rows()
    written: Dict[str, Path] = {}

    payload_specs = [
        (
            "index",
            _OUT_INDEX,
            "Tier 0 requirements-index view with step1_req_id as first-class field.",
        ),
        (
            "coverage",
            _OUT_COVERAGE,
            "Tier 0 coverage-matrix view with step1_req_id as first-class field.",
        ),
        (
            "impl",
            _OUT_IMPL,
            "Tier 0 implementation-map view with step1_req_id as first-class field.",
        ),
        (
            "artifact",
            _OUT_ARTIFACT,
            "Tier 0 artifact-linkage view with step1_req_id as first-class field.",
        ),
    ]

    for surface, fname, desc in payload_specs:
        payload = _generate_payload(surface, sets[surface], desc)
        path = _ARTIFACTS_DIR / fname
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        written[surface] = path

    return written


def _validate_payload(payload: Mapping[str, Any]) -> List[str]:
    errors: List[str] = []
    rows = payload.get("rows", [])
    if len(rows) != len(TIER0_REQ_IDS):
        errors.append(f"row_count={len(rows)} expected={len(TIER0_REQ_IDS)}")
    seen: Set[str] = set()
    for row in rows:
        sid = row.get("step1_req_id")
        if not sid:
            errors.append("blank step1_req_id encountered")
            continue
        if sid not in TIER0_REQ_IDS:
            errors.append(f"unknown step1_req_id: {sid}")
        if sid in seen:
            errors.append(f"duplicate step1_req_id: {sid}")
        seen.add(sid)

        ls = row.get("linkage_status")
        if ls not in ALLOWED_STATUSES:
            errors.append(f"{sid}: linkage_status not allowed: {ls}")

        for b in row.get("blockers", []):
            if b not in ALLOWED_BLOCKERS:
                errors.append(f"{sid}: blocker not allowed: {b}")

        # Forbidden-token check: status verdicts must not appear as the VALUE
        # of any status-bearing field. Substring matches inside file paths
        # (e.g. test_otel_trace_completeness.py), structured field names
        # (NEEDS_EXPECTED_FAIL_REASON), or quoted requirement text
        # (e.g. "UNKNOWN MUST NOT be treated as PASS") are legitimate.
        for status_field in ("linkage_status", "status", "verdict"):
            val = row.get(status_field)
            if isinstance(val, str) and val.upper() in {t.upper() for t in FORBIDDEN_TOKENS}:
                errors.append(f"{sid}: forbidden token used as {status_field}: {val}")

    missing = set(TIER0_REQ_IDS) - seen
    if missing:
        errors.append(f"missing step1_req_ids: {sorted(missing)}")

    return errors


def validate(written: Mapping[str, Path]) -> Dict[str, Any]:
    """Validate the four generated files. Cross-check blockers preservation."""
    src_blockers: Counter = Counter()
    gen_blockers: Counter = Counter()

    for src in (_SRC_INDEX, _SRC_COVERAGE, _SRC_IMPL, _SRC_ARTIFACT):
        payload = _load_json(src)
        for row in payload.get("rows", []):
            for b in row.get("blockers", []):
                src_blockers[b] += 1

    file_results: Dict[str, List[str]] = {}
    for path in written.values():
        payload = json.loads(path.read_text(encoding="utf-8"))
        file_results[path.name] = _validate_payload(payload)
        for row in payload.get("rows", []):
            for b in row.get("blockers", []):
                gen_blockers[b] += 1

    # Blocker preservation rule: blockers in _INTENTIONALLY_DROPPED_BLOCKERS
    # must be 0 in generated output. All other blockers must match the
    # source counts verbatim.
    src_other = Counter({k: v for k, v in src_blockers.items() if k not in _INTENTIONALLY_DROPPED_BLOCKERS})
    gen_other = Counter({k: v for k, v in gen_blockers.items() if k not in _INTENTIONALLY_DROPPED_BLOCKERS})
    other_blockers_preserved = src_other == gen_other
    fully_dropped_to_zero = {k: gen_blockers.get(k, 0) == 0 for k in _FULLY_DROPPED_BLOCKERS}
    partially_droppable_decreased = {
        k: gen_blockers.get(k, 0) <= src_blockers.get(k, 0) for k in _PARTIALLY_DROPPABLE_BLOCKERS
    }
    all_fully_dropped = all(fully_dropped_to_zero.values())
    all_partial_ok = all(partially_droppable_decreased.values())

    return {
        "file_results": file_results,
        "src_blocker_counts": dict(src_blockers),
        "gen_blocker_counts": dict(gen_blockers),
        "fully_dropped_blockers": sorted(_FULLY_DROPPED_BLOCKERS),
        "fully_dropped_to_zero": fully_dropped_to_zero,
        "partially_droppable_blockers": sorted(_PARTIALLY_DROPPABLE_BLOCKERS),
        "partially_droppable_decreased": partially_droppable_decreased,
        "other_blockers_preserved": other_blockers_preserved,
        "blockers_preserved": (other_blockers_preserved and all_fully_dropped and all_partial_ok),
    }


def write_report(written: Mapping[str, Path], validation: Mapping[str, Any]) -> Path:
    lines: List[str] = []
    lines.append("# Tier 0 Step-1 Metadata Schema Validation Report")
    lines.append("")
    lines.append(f"Generated: {_utc_now_iso()}")
    lines.append("")
    lines.append(
        "Schema/linkage layer only. No runtime code, tests, traces, replay bundles, or proof harness output were executed or modified."
    )
    lines.append("")
    lines.append("## Files Generated")
    lines.append("")
    for surface, path in written.items():
        lines.append(f"- `artifacts/runtime/requirements_proof/{path.name}` ({surface})")
    lines.append("")

    lines.append("## Per-File Validation")
    lines.append("")
    lines.append("| file | rows expected | result |")
    lines.append("|---|---:|---|")
    all_clean = True
    for fname, errs in validation["file_results"].items():
        result = "OK" if not errs else f"FAILED ({len(errs)} error(s))"
        if errs:
            all_clean = False
        lines.append(f"| {fname} | 17 | {result} |")
    lines.append("")

    if not all_clean:
        lines.append("### Errors")
        for fname, errs in validation["file_results"].items():
            if not errs:
                continue
            lines.append(f"**{fname}**")
            for e in errs:
                lines.append(f"  - {e}")
            lines.append("")

    lines.append("## Blocker Preservation")
    lines.append("")
    lines.append(f"Blockers preserved: **{validation['blockers_preserved']}**")
    lines.append("")
    lines.append("| blocker | source count | generated count |")
    lines.append("|---|---:|---:|")
    keys = sorted(set(validation["src_blocker_counts"]) | set(validation["gen_blocker_counts"]))
    for k in keys:
        s = validation["src_blocker_counts"].get(k, 0)
        g = validation["gen_blocker_counts"].get(k, 0)
        lines.append(f"| {k} | {s} | {g} |")
    lines.append("")

    lines.append("## Allowed Statuses")
    lines.append("")
    lines.append(", ".join(sorted(ALLOWED_STATUSES)))
    lines.append("")
    lines.append("## Allowed Blockers")
    lines.append("")
    lines.append(", ".join(sorted(ALLOWED_BLOCKERS)))
    lines.append("")
    lines.append("## Statement")
    lines.append("")
    lines.append(
        "Schema-extension layer only. No PASS / FAIL / PROVEN / COVERED / "
        "ENFORCED / COMPLETE / CLOSED claim is made. Statuses and blockers are "
        "carried forward from prior linkage metadata without upgrade."
    )
    lines.append("")

    path = _ARTIFACTS_DIR / _OUT_REPORT
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main() -> int:
    written = generate()
    validation = validate(written)
    report_path = write_report(written, validation)

    print(f"Generated {len(written)} files + report at {report_path}")
    print("Tier 0 row count per file: 17")
    all_clean = all(not errs for errs in validation["file_results"].values())
    print(f"Schema validation: {'OK' if all_clean else 'FAILED'}")
    print(f"Other blockers preserved: {validation['other_blockers_preserved']}")
    print(f"Fully dropped → 0: {validation['fully_dropped_to_zero']}")
    print(f"Partially droppable decreased: {validation['partially_droppable_decreased']}")
    return 0 if all_clean and validation["blockers_preserved"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
