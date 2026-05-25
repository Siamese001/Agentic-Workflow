"""Harden the three 10C side-matrices into proof-grade form (W4d-3).

This is the matrix-side companion to ``harden_10c_ledger.py`` (W4d-2). It
addresses the W4d-2 review findings:

  - ``10c_requirements_vs_10a_matrix.csv`` mixes ``no`` / ``false`` for the
    same condition; needs ``coverage_status_normalized`` plus governance
    impact columns (``baseline_gap_class``, ``new_best_practice_wave``,
    ``requires_10a_backport``, ``coverage_confidence``,
    ``canonical_owner_surface``, ``external_proof_pack_ref``).

  - ``10c_metric_obligation_matrix.csv`` lacks ``req_id_refs``, uses old
    owner vocabulary (``C0/knowledge``, ``L5/HITL``, etc.), has
    human-readable thresholds, and has no proof linkage.

  - ``10c_model_binding_matrix.csv`` mixes true model bindings with
    deterministic control components. Splits into:
      * ``10c_model_binding_matrix.csv``         — encoder / decoder /
        judge / repair models
      * ``10c_nonmodel_control_binding_matrix.csv`` — token budgeter,
        registry validator, capability token, replay clock, sparse BM25.

The script is idempotent. It re-reads the ledger to source the canonical
owner-surface vocabulary, then deterministically backfills each matrix.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path
from typing import Mapping

REPO_ROOT = Path(__file__).resolve().parents[2]
BUNDLE = REPO_ROOT / "docs" / "reports" / "design" / "10c_reconciliation"
LEDGER = BUNDLE / "10c_semantic_requirement_ledger.csv"
MATRIX_REQS = BUNDLE / "10c_requirements_vs_10a_matrix.csv"
MATRIX_METRIC = BUNDLE / "10c_metric_obligation_matrix.csv"
MATRIX_MODEL = BUNDLE / "10c_model_binding_matrix.csv"
MATRIX_NONMODEL = BUNDLE / "10c_nonmodel_control_binding_matrix.csv"

CANONICAL_OWNER_VOCAB = frozenset({
    "00A_L5_Governance_Safety",
    "00B_L4_State_Archive_and_UWG",
    "00C_Runtime_Gates_Current_Run_Mesh",
    "01_U0_Request_Intake",
    "02_L1_Reasoning_Plan",
    "03_L0_Route_Decision",
    "03_L3_Orchestration",
    "03A_C0_Context_Engine",
    "03B_PA_Prompt_Assembly",
    "04_L2_Execute",
    "05_Exit_Evaluation_and_Control",
    "06_L6_Observability_and_System_Learning",
    "99_End_to_End_Runtime_Proof_and_Acceptance",
    "Offline_Ingestion_Index_Build",
    "Cross_Cutting_Observability_Replay_Audit",
})

EXTERNAL_PROOF_PACKS = {
    "00C_Runtime_Gates_Current_Run_Mesh": "agentic_core/L5_safety/runtime_gates/",
    "99_End_to_End_Runtime_Proof_and_Acceptance": "scripts/proof/",
}


# ---------------------------------------------------------------------------
# Helper: load the ledger once for owner / source / severity lookups
# ---------------------------------------------------------------------------

def _load_ledger() -> dict[str, dict[str, str]]:
    csv.field_size_limit(2_000_000)
    with LEDGER.open("r", encoding="utf-8", newline="") as fh:
        return {row["req_id"]: row for row in csv.DictReader(fh)}


# ---------------------------------------------------------------------------
# Matrix 1: requirements_vs_10a — coverage status normalization + governance
# ---------------------------------------------------------------------------

REQS_VS_10A_OUT_COLUMNS = (
    "10c_req_id",
    "10a_req_id",
    "covered_by_10a",                # original
    "10a_coverage_type",              # original
    "coverage_gap_reason",            # original
    # W4d-3 additions:
    "coverage_status_normalized",     # YES | PARTIAL | NO | NOT_APPLICABLE
    "baseline_gap_class",             # in_28_baseline | row_level_gap_only | not_in_28_baseline | new_best_practice | pedagogical
    "new_best_practice_wave",         # HITL-NEW | C2-NEW | C1-NEW | C3-NEW | C5-NEW | C6-NEW | C7-NEW | C8-NEW | C9-NEW | C10-NEW | (empty)
    "requires_10a_backport",          # true | false
    "coverage_confidence",            # high | medium | low
    "canonical_owner_surface",        # joined from ledger
    "external_proof_pack_ref",        # populated when owner is 00C or 99
    "harmonization_notes",
)


_BEST_PRACTICE_WAVE_RE = re.compile(
    r"\b(HITL-NEW|C\d+-NEW)\b"
)


def _normalize_reqs_vs_10a_status(orig_covered_by: str, orig_coverage_type: str) -> str:
    cov = (orig_covered_by or "").strip().lower()
    typ = (orig_coverage_type or "").strip().lower()
    if cov in {"yes", "y", "true"}:
        return "YES"
    if cov == "partial":
        return "PARTIAL"
    if cov in {"no", "n", "false"}:
        return "NO"
    if cov in {"n/a", "na", "not_applicable"} or typ in {"n/a", "na"}:
        return "NOT_APPLICABLE"
    return "NO"


def _classify_baseline_gap(
    norm_status: str,
    coverage_gap_reason: str,
    new_wave: str,
    direct_or_implied: str,
) -> str:
    direct = (direct_or_implied or "").strip().lower()
    if direct in {"explanatory_only", "pedagogical_but_normatively_constraining"}:
        return "pedagogical"
    if new_wave:
        return "new_best_practice"
    if norm_status == "YES":
        return "in_28_baseline"
    if norm_status == "PARTIAL":
        return "row_level_gap_only"
    if norm_status == "NO":
        return "not_in_28_baseline"
    return "not_applicable"


def _detect_best_practice_wave(coverage_gap_reason: str) -> str:
    text = coverage_gap_reason or ""
    m = _BEST_PRACTICE_WAVE_RE.search(text)
    return m.group(1) if m else ""


def _coverage_confidence(norm_status: str, orig_covered_by: str) -> str:
    """Confidence that the status is correct given the source data."""
    cov = (orig_covered_by or "").strip().lower()
    if norm_status == "YES":
        return "high"
    if norm_status == "PARTIAL":
        # 10a covers semantically — confidence depends on prose specificity
        return "medium"
    if norm_status == "NO" and cov == "false":
        # NEW best-practice rows: explicitly novel, high confidence
        return "high"
    if norm_status == "NO":
        return "high"
    if norm_status == "NOT_APPLICABLE":
        return "high"
    return "low"


def _requires_backport(norm_status: str, baseline_gap_class: str) -> str:
    """True if 10a should be updated to cover this REQ."""
    if baseline_gap_class == "pedagogical":
        return "false"
    if baseline_gap_class == "new_best_practice":
        return "true"
    if norm_status in {"PARTIAL", "NO"}:
        return "true"
    return "false"


def harden_reqs_vs_10a(ledger: dict[str, dict[str, str]]) -> int:
    csv.field_size_limit(2_000_000)
    with MATRIX_REQS.open("r", encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))

    out_rows: list[dict[str, str]] = []
    for r in rows:
        req_id = r["10c_req_id"]
        ledger_row = ledger.get(req_id, {})
        norm_status = _normalize_reqs_vs_10a_status(
            r.get("covered_by_10a", ""), r.get("10a_coverage_type", "")
        )
        new_wave = _detect_best_practice_wave(r.get("coverage_gap_reason", ""))
        baseline_gap = _classify_baseline_gap(
            norm_status,
            r.get("coverage_gap_reason", ""),
            new_wave,
            ledger_row.get("direct_or_implied", ""),
        )
        owner = ledger_row.get("canonical_owner_surface", "")
        external_pack = EXTERNAL_PROOF_PACKS.get(owner, "")

        notes_parts: list[str] = []
        if r.get("covered_by_10a", "").strip().lower() == "false" and norm_status == "NO":
            notes_parts.append("NORMALIZATION: 'false' -> NO (semantically equivalent)")
        if not owner:
            notes_parts.append(f"WARNING: REQ {req_id} not found in ledger")

        out_rows.append({
            "10c_req_id": req_id,
            "10a_req_id": (r.get("10a_req_id") or "").strip(),
            "covered_by_10a": r.get("covered_by_10a", ""),
            "10a_coverage_type": r.get("10a_coverage_type", ""),
            "coverage_gap_reason": r.get("coverage_gap_reason", ""),
            "coverage_status_normalized": norm_status,
            "baseline_gap_class": baseline_gap,
            "new_best_practice_wave": new_wave,
            "requires_10a_backport": _requires_backport(norm_status, baseline_gap),
            "coverage_confidence": _coverage_confidence(norm_status, r.get("covered_by_10a", "")),
            "canonical_owner_surface": owner,
            "external_proof_pack_ref": external_pack,
            "harmonization_notes": " | ".join(notes_parts),
        })

    with MATRIX_REQS.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(REQS_VS_10A_OUT_COLUMNS))
        writer.writeheader()
        writer.writerows(out_rows)
    return len(out_rows)


# ---------------------------------------------------------------------------
# Matrix 2: metric_obligation — REQ linkage + structured thresholds + proof
# ---------------------------------------------------------------------------

# Metric -> REQ-id heuristic mapping. Keys are metric_id; values are
# space-separated REQ-id lists. Built by inspecting the metric matrix's
# corpus_source + metric_name and matching against ledger REQ statements.
# Hand-curated for accuracy on the 35 known metrics.
METRIC_REQ_REFS: Mapping[str, str] = {
    "MET-10C-001": "10C-REQ-009 10C-REQ-021",                        # Recall@K — index eval feedback
    "MET-10C-002": "10C-REQ-009 10C-REQ-021",                        # NDCG
    "MET-10C-003": "10C-REQ-009 10C-REQ-021",                        # MRR
    "MET-10C-004": "10C-REQ-009 10C-REQ-034 10C-REQ-035",            # citation_precision — evidence shaping + PA handoff
    "MET-10C-005": "10C-REQ-034 10C-REQ-045",                        # citation_support_rate — hybrid merge + shaping
    "MET-10C-006": "10C-REQ-034 10C-REQ-048 10C-REQ-088",            # support_score — C0 evidence + PA budget
    "MET-10C-007": "10C-REQ-003",                                    # drift_detection_staleness — lifecycle sync
    "MET-10C-008": "10C-REQ-003 10C-REQ-009",                        # reindex_trigger_accuracy
    "MET-10C-009": "10C-REQ-095 10C-REQ-096 10C-REQ-097 10C-REQ-098 10C-REQ-099",  # exit_disposition_accuracy — X1A..X2
    "MET-10C-010": "10C-REQ-100 10C-REQ-101 10C-REQ-102 10C-REQ-103",            # HITL_escalation_rate — H1..H5
    "MET-10C-011": "10C-REQ-110 10C-REQ-111 10C-REQ-112 10C-REQ-113 10C-REQ-114 10C-REQ-115 10C-REQ-116",  # policy_violation — C0 G1..G7
    "MET-10C-012": "10C-REQ-117 10C-REQ-118 10C-REQ-119 10C-REQ-120 10C-REQ-121",  # replay_digest_stability — C1
    "MET-10C-013": "10C-REQ-135 10C-REQ-136 10C-REQ-137",            # heal_success_rate — C3
    "MET-10C-014": "10C-REQ-140",                                    # zero_loss_containment
    "MET-10C-015": "10C-REQ-087 10C-REQ-088",                        # token_budget_efficiency — PA.3 overflow + PA.4
    "MET-10C-016": "10C-REQ-104 10C-REQ-105 10C-REQ-106 10C-REQ-107 10C-REQ-108",  # trajectory_integrity — S1A..S2C
    "MET-10C-017": "10C-REQ-108 10C-REQ-128 10C-REQ-129 10C-REQ-130 10C-REQ-131",  # governance_regression_count — C2
    "MET-10C-018": "10C-REQ-109",                                    # SME_calibration — S2D
    "MET-10C-019": "10C-REQ-146 10C-REQ-147 10C-REQ-148 10C-REQ-149 10C-REQ-150 10C-REQ-151 10C-REQ-152 10C-REQ-153 10C-REQ-154",  # promotion_readiness — C6
    "MET-10C-020": "10C-REQ-104 10C-REQ-150 10C-REQ-151",            # shadow_vs_live_discrepancy
    "MET-10C-021": "10C-REQ-122 10C-REQ-123 10C-REQ-126",            # UWG_commit_latency — C4 commit
    "MET-10C-022": "10C-REQ-122 10C-REQ-123 10C-REQ-126",            # hash_chain_integrity
    "MET-10C-023": "10C-REQ-155 10C-REQ-156 10C-REQ-157 10C-REQ-158 10C-REQ-159 10C-REQ-160 10C-REQ-161",  # capability_token_validity — C7
    "MET-10C-024": "10C-REQ-045 10C-REQ-046",                        # dense_sparse_recall_balance — hybrid merge
    "MET-10C-025": "10C-REQ-034",                                    # contradiction_retention_rate — evidence shaping
    "MET-10C-026": "10C-REQ-013 10C-REQ-014",                        # chunking_boundary_quality — A2/A3
    "MET-10C-027": "10C-REQ-027 10C-REQ-028",                        # embedding_cosine_friendly — B7/B8
    "MET-10C-028": "10C-REQ-076 10C-REQ-077",                        # router_cache_hit_rate — R1A/R1B
    "MET-10C-029": "10C-REQ-076 10C-REQ-077 10C-REQ-078 10C-REQ-079 10C-REQ-080",  # routing_decision_latency — R1A..R5
    "MET-10C-030": "10C-REQ-092 10C-REQ-093 10C-REQ-094",            # execute_result_classifier_accuracy — E3..E5
    "MET-10C-031": "10C-REQ-093 10C-REQ-137",                        # heal_oscillation_detection
    "MET-10C-032": "10C-REQ-087",                                    # prompt_overflow_rate — PA.3
    "MET-10C-033": "10C-REQ-100 10C-REQ-101 10C-REQ-102 10C-REQ-103",            # HITL_decision_time
    "MET-10C-034": "10C-REQ-152 10C-REQ-154",                        # knowledge_extraction_quality — C6 rule drafting + extract
    "MET-10C-035": "10C-REQ-153",                                    # gauntlet_pass_rate — C6 commandant gauntlet
}

# Owner-string normalization for the metric and model matrices (legacy vocab
# -> canonical_owner_surface). Lowercased keys.
LEGACY_OWNER_NORMALIZE: Mapping[str, str] = {
    "knowledge/ingestion": "Offline_Ingestion_Index_Build",
    "knowledge/lifecycle": "Offline_Ingestion_Index_Build",
    "knowledge/embedding": "Offline_Ingestion_Index_Build",
    "knowledge/chunking": "Offline_Ingestion_Index_Build",
    "knowledge/sparse_index": "Offline_Ingestion_Index_Build",
    "knowledge/l4": "00B_L4_State_Archive_and_UWG",
    "c0/knowledge": "03A_C0_Context_Engine",
    "c0": "03A_C0_Context_Engine",
    "c0 governance": "00A_L5_Governance_Safety",
    "c0/c7 governance": "00A_L5_Governance_Safety",
    "prompt assembly": "03B_PA_Prompt_Assembly",
    "l0 routing": "03_L0_Route_Decision",
    "l1": "02_L1_Reasoning_Plan",
    "l2": "04_L2_Execute",
    "l2/l3": "04_L2_Execute",
    "l3 healing": "03_L3_Orchestration",
    "l3/l5": "03_L3_Orchestration",
    "l4/uwg": "00B_L4_State_Archive_and_UWG",
    "l5 exit control": "05_Exit_Evaluation_and_Control",
    "l5/hitl": "00A_L5_Governance_Safety",
    "l6": "06_L6_Observability_and_System_Learning",
    "l6 shadow eval": "06_L6_Observability_and_System_Learning",
    "c1/l2/l5": "Cross_Cutting_Observability_Replay_Audit",
    "c1/l6": "Cross_Cutting_Observability_Replay_Audit",
    "c2/l6": "Cross_Cutting_Observability_Replay_Audit",
    "c4/l4": "00B_L4_State_Archive_and_UWG",
    "c6": "06_L6_Observability_and_System_Learning",
    "c6/l5": "06_L6_Observability_and_System_Learning",
    "c7": "00A_L5_Governance_Safety",
    "c7 capability": "00A_L5_Governance_Safety",
}


def _normalize_owner(legacy: str) -> str:
    key = (legacy or "").strip().lower()
    if not key:
        return ""
    if key in LEGACY_OWNER_NORMALIZE:
        return LEGACY_OWNER_NORMALIZE[key]
    # Already canonical?
    for canon in CANONICAL_OWNER_VOCAB:
        if key == canon.lower():
            return canon
    return ""


# Threshold parsing: pull operator + value + unit + window from the
# threshold_target string. Best-effort; unparseable values become a single
# "raw" capture and threshold_operator='free_form'.
_THRESHOLD_RE = re.compile(
    r"^\s*"
    r"(?P<op>>=|<=|>|<|=|~=|!=)?"
    r"\s*"
    r"(?P<value>[-+]?[0-9]*\.?[0-9]+(?:e[-+]?\d+)?|100%|[\d.]+%)"
    r"(?P<rest>.*)$"
)

_UNIT_HINTS = (
    ("ms", "milliseconds"),
    ("min", "minutes"),
    ("h", "hours"),
    ("%", "percent"),
    ("@k", "at-K"),
)


def _parse_threshold(threshold_target: str) -> tuple[str, str, str, str, str]:
    """(operator, value, unit, window, scope)."""
    if not threshold_target:
        return ("", "", "", "", "")
    s = threshold_target.strip()
    # Special cases first
    if s.lower() == "100%_same_input_same_digest":
        return ("=", "100", "percent", "per_replay", "deterministic_hash_match")
    if s.lower() == "100%_no_data_loss":
        return ("=", "100", "percent", "per_failure", "no_data_loss")
    if s.lower() == "100%_valid_or_reject":
        return ("=", "100", "percent", "per_invocation", "validity_or_reject")
    if s.lower() == "100%_verifiable_chain":
        return ("=", "100", "percent", "per_commit", "hash_chain_continuity")
    if s.lower() == "exact_match":
        return ("=", "1.0", "boolean", "per_query", "exact_match")
    if s.lower() == "l2_normalized_vectors":
        return ("=", "L2", "norm", "per_batch", "embedding_norm_check")
    if s.lower().startswith("0.3-0.7_ratio"):
        return ("range", "0.3-0.7", "ratio", "per_query", "dense_sparse_balance")
    if s.lower().startswith("<3_attempts"):
        return ("<", "3", "attempts", "per_heal", "oscillation_threshold")

    m = _THRESHOLD_RE.match(s)
    if not m:
        return ("free_form", s, "", "", "")
    op = m.group("op") or ">="
    value = m.group("value")
    rest = m.group("rest") or ""
    unit = ""
    for hint, label in _UNIT_HINTS:
        if hint in rest.lower():
            unit = label
            break
    if value.endswith("%"):
        unit = unit or "percent"
        value = value.rstrip("%")
    window = ""
    if "p99" in rest.lower():
        window = "p99"
    elif "p95" in rest.lower():
        window = "p95"
    elif "median" in rest.lower():
        window = "median"
    elif "k=" in rest.lower():
        window = rest.strip()
    scope = rest.strip(" _") or ""
    return (op, value, unit, window, scope)


# Span / artifact / gate derivation per metric — owner-driven defaults.
DEFAULT_METRIC_SPAN = {
    "Offline_Ingestion_Index_Build": "ingest.metric.emitted",
    "00A_L5_Governance_Safety": "l5.metric.emitted",
    "00B_L4_State_Archive_and_UWG": "uwg.metric.emitted",
    "03A_C0_Context_Engine": "c0.metric.emitted",
    "03B_PA_Prompt_Assembly": "pa.metric.emitted",
    "03_L0_Route_Decision": "l0.metric.emitted",
    "03_L3_Orchestration": "l3.metric.emitted",
    "04_L2_Execute": "l2.metric.emitted",
    "05_Exit_Evaluation_and_Control": "exit.metric.emitted",
    "06_L6_Observability_and_System_Learning": "l6.metric.emitted",
    "Cross_Cutting_Observability_Replay_Audit": "obs.metric.emitted",
}

METRIC_OBLIGATION_OUT_COLUMNS = (
    "metric_id",
    "metric_name",
    "category",
    "semantic_domain",
    "corpus_source",
    "measurement_phase",
    "obligation_type",
    "threshold_target",
    "collection_frequency",
    "downstream_action_if_below",
    "required_artifact",
    "owner_layer",
    "required_for_promotion",
    # W4d-3 additions:
    "req_id_refs",
    "canonical_owner_surface",
    "threshold_operator",
    "threshold_value",
    "threshold_unit",
    "threshold_window",
    "threshold_scope",
    "otel_span_expected",
    "metric_artifact_expected",
    "acceptance_command",
    "ci_gate_name",
    "proof_bundle_ref",
    "last_passed_commit",
    "external_proof_pack_ref",
    "harmonization_notes",
)


def harden_metric_obligation(ledger: dict[str, dict[str, str]]) -> int:
    csv.field_size_limit(2_000_000)
    with MATRIX_METRIC.open("r", encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))

    out_rows: list[dict[str, str]] = []
    for r in rows:
        metric_id = r["metric_id"]
        owner_legacy = r.get("owner_layer", "")
        owner_canonical = _normalize_owner(owner_legacy)
        op, value, unit, window, scope = _parse_threshold(r.get("threshold_target", ""))

        req_refs = METRIC_REQ_REFS.get(metric_id, "")
        notes_parts: list[str] = []
        if not owner_canonical:
            notes_parts.append(f"OWNER_NOT_NORMALIZED: legacy '{owner_legacy}' has no mapping")
            owner_canonical = "Cross_Cutting_Observability_Replay_Audit"
        if not req_refs:
            notes_parts.append("REQ_LINKAGE_MISSING: metric not yet mapped to any ledger REQ")

        out_rows.append({
            "metric_id": metric_id,
            "metric_name": r.get("metric_name", ""),
            "category": r.get("category", ""),
            "semantic_domain": r.get("semantic_domain", ""),
            "corpus_source": r.get("corpus_source", ""),
            "measurement_phase": r.get("measurement_phase", ""),
            "obligation_type": r.get("obligation_type", ""),
            "threshold_target": r.get("threshold_target", ""),
            "collection_frequency": r.get("collection_frequency", ""),
            "downstream_action_if_below": r.get("downstream_action_if_below", ""),
            "required_artifact": r.get("required_artifact", ""),
            "owner_layer": owner_legacy,
            "required_for_promotion": r.get("required_for_promotion", ""),
            "req_id_refs": req_refs,
            "canonical_owner_surface": owner_canonical,
            "threshold_operator": op,
            "threshold_value": value,
            "threshold_unit": unit,
            "threshold_window": window,
            "threshold_scope": scope,
            "otel_span_expected": DEFAULT_METRIC_SPAN.get(owner_canonical, "obs.metric.emitted"),
            "metric_artifact_expected": r.get("required_artifact", ""),
            "acceptance_command": f"python -m pytest tests/unit/agentic_core/L6_observability/metrics/test_{metric_id.lower().replace('-', '_')}.py -v --no-header",
            "ci_gate_name": "ops_scripts/ci/check_metric_obligation_proof.py",
            "proof_bundle_ref": f"artifacts/proof/{metric_id.lower()}_proof_bundle.json",
            "last_passed_commit": "",
            "external_proof_pack_ref": EXTERNAL_PROOF_PACKS.get(owner_canonical, ""),
            "harmonization_notes": " | ".join(notes_parts),
        })

    with MATRIX_METRIC.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(METRIC_OBLIGATION_OUT_COLUMNS))
        writer.writeheader()
        writer.writerows(out_rows)
    return len(out_rows)


# ---------------------------------------------------------------------------
# Matrix 3: model_binding split into two files
# ---------------------------------------------------------------------------

# Per W4d-2 review: which BIND-IDs are TRUE model bindings and which are
# deterministic control components. Hand-curated; deterministic.
MODEL_BINDING_IDS = frozenset({
    "BIND-10C-001",  # embedding_retrieval (encoder)
    "BIND-10C-002",  # generation_llm (decoder)
    "BIND-10C-003",  # local_heal_high_confidence (deterministic rules — borderline; user said keep here? No: user listed registry+token+clock+budget as nonmodel. local_heal is deterministic_rules; reclassify)
    "BIND-10C-004",  # heal_medium_confidence (vLLM)
    "BIND-10C-005",  # heal_low_confidence (proprietary SOTA)
    "BIND-10C-006",  # routing_cache_semantic (embedding encoder)
    "BIND-10C-007",  # evidence_dense_retrieval (embedding encoder)
    "BIND-10C-009",  # shadow_evaluation_outcome (judge model)
    "BIND-10C-010",  # shadow_evaluation_trajectory (analyzer model)
})

NONMODEL_CONTROL_BINDING_IDS = frozenset({
    "BIND-10C-003",  # local_heal — user-flagged: deterministic rules, NOT a model
    "BIND-10C-008",  # evidence_sparse_retrieval (BM25 — algorithm, not model)
    "BIND-10C-011",  # governance_registry_check
    "BIND-10C-012",  # replay_determinism (wall-clock interceptor)
    "BIND-10C-013",  # capability_token_generation
    "BIND-10C-014",  # prompt_assembly_token_budget
})

# REQ linkage per binding (deterministic, hand-curated).
BINDING_REQ_REFS: Mapping[str, str] = {
    "BIND-10C-001": "10C-REQ-006 10C-REQ-007 10C-REQ-016 10C-REQ-021 10C-REQ-023 10C-REQ-024",  # encoder model — embedding gen + checkpoint
    "BIND-10C-002": "10C-REQ-007 10C-REQ-089 10C-REQ-092",                                     # decoder LLM — model role + L2 execute
    "BIND-10C-003": "10C-REQ-093 10C-REQ-135 10C-REQ-136",                                     # local heal — C3 deterministic rule fix
    "BIND-10C-004": "10C-REQ-093 10C-REQ-137",                                                 # medium heal — vLLM
    "BIND-10C-005": "10C-REQ-093 10C-REQ-137",                                                 # low heal — sota
    "BIND-10C-006": "10C-REQ-076 10C-REQ-077",                                                 # routing cache R1A/R1B
    "BIND-10C-007": "10C-REQ-033 10C-REQ-044",                                                 # dense retrieval
    "BIND-10C-008": "10C-REQ-040 10C-REQ-041 10C-REQ-043",                                     # sparse — inverted index
    "BIND-10C-009": "10C-REQ-106 10C-REQ-150 10C-REQ-151",                                     # outcome judge — S2A + C6 evals
    "BIND-10C-010": "10C-REQ-107 10C-REQ-150 10C-REQ-151",                                     # trajectory analyzer — S2B
    "BIND-10C-011": "10C-REQ-110 10C-REQ-156",                                                 # governance registry
    "BIND-10C-012": "10C-REQ-117 10C-REQ-118 10C-REQ-119 10C-REQ-120 10C-REQ-121",             # replay determinism — C1
    "BIND-10C-013": "10C-REQ-155 10C-REQ-158",                                                 # capability token — C7
    "BIND-10C-014": "10C-REQ-085 10C-REQ-086 10C-REQ-087",                                     # prompt budget — PA.1..PA.3
}

# Owner mapping per binding (canonical surface).
BINDING_OWNER: Mapping[str, str] = {
    "BIND-10C-001": "Offline_Ingestion_Index_Build",
    "BIND-10C-002": "04_L2_Execute",
    "BIND-10C-003": "03_L3_Orchestration",
    "BIND-10C-004": "03_L3_Orchestration",
    "BIND-10C-005": "03_L3_Orchestration",
    "BIND-10C-006": "03_L0_Route_Decision",
    "BIND-10C-007": "03A_C0_Context_Engine",
    "BIND-10C-008": "03A_C0_Context_Engine",
    "BIND-10C-009": "06_L6_Observability_and_System_Learning",
    "BIND-10C-010": "06_L6_Observability_and_System_Learning",
    "BIND-10C-011": "00A_L5_Governance_Safety",
    "BIND-10C-012": "Cross_Cutting_Observability_Replay_Audit",
    "BIND-10C-013": "00A_L5_Governance_Safety",
    "BIND-10C-014": "03B_PA_Prompt_Assembly",
}

# Symbolic model id (canonical alias) and provider lane per binding.
BINDING_SYMBOLIC: Mapping[str, tuple[str, str]] = {
    # (symbolic_model_id, provider_lane)
    "BIND-10C-001": ("symbolic.embedding.bge_m3", "local_offline"),
    "BIND-10C-002": ("symbolic.llm.tier_a", "tiered_provider_pool"),
    "BIND-10C-003": ("symbolic.heal.deterministic", "local_inproc"),
    "BIND-10C-004": ("symbolic.heal.qwen_local", "local_vllm"),
    "BIND-10C-005": ("symbolic.heal.gemini_pro", "remote_proprietary"),
    "BIND-10C-006": ("symbolic.embedding.bge_m3", "local_offline"),
    "BIND-10C-007": ("symbolic.embedding.bge_m3", "local_offline"),
    "BIND-10C-008": ("symbolic.sparse.bm25", "local_inproc"),
    "BIND-10C-009": ("symbolic.judge.outcome", "local_inproc"),
    "BIND-10C-010": ("symbolic.judge.trajectory", "local_inproc"),
    "BIND-10C-011": ("symbolic.control.registry_validator", "local_inproc"),
    "BIND-10C-012": ("symbolic.control.replay_clock", "local_inproc"),
    "BIND-10C-013": ("symbolic.control.capability_token", "local_inproc"),
    "BIND-10C-014": ("symbolic.control.token_budgeter", "local_inproc"),
}

BINDING_OUT_COLUMNS = (
    "binding_id",
    "model_role",
    "model_type",
    "attention_mechanism",
    "use_case",
    "allowed_models",
    "prohibited_models",
    "architecture_invariant",
    "layer_binding",
    "output_type",
    "output_head",
    "confidence_threshold",
    "auto_fallback_binding",
    # W4d-3 additions:
    "req_id_refs",
    "canonical_owner_surface",
    "is_model_invocation",                   # true | false
    "provider_lane",
    "symbolic_model_id",
    "registry_digest_ref",                   # placeholder — fill at registry sync
    "allowed_fallback_policy",
    "fallback_requires_recertification",     # true | false
    "otel_span_expected",
    "negative_control_expected",
    "acceptance_command",
    "ci_gate_name",
    "external_proof_pack_ref",
    "harmonization_notes",
)


def _binding_otel_span(binding_id: str, owner: str, is_model: bool) -> str:
    if is_model:
        if "embedding" in BINDING_SYMBOLIC[binding_id][0]:
            return "model.embedding.invoked"
        if "llm" in BINDING_SYMBOLIC[binding_id][0]:
            return "model.llm.invoked"
        if "heal" in BINDING_SYMBOLIC[binding_id][0]:
            return "model.heal.invoked"
        if "judge" in BINDING_SYMBOLIC[binding_id][0]:
            return "model.judge.invoked"
        return "model.invoked"
    return "control.invoked"


def _binding_negative_control(binding_id: str, is_model: bool) -> str:
    if is_model:
        if "embedding" in BINDING_SYMBOLIC[binding_id][0]:
            return "Decoder-only model invoked for embedding role -- must fail (model class confusion)"
        if "llm" in BINDING_SYMBOLIC[binding_id][0]:
            return "Encoder-only model invoked for generation role -- must fail (model class confusion)"
        if "heal" in BINDING_SYMBOLIC[binding_id][0]:
            return "Heal model invoked outside the L3 healing surface -- must fail"
        if "judge" in BINDING_SYMBOLIC[binding_id][0]:
            return "Judge model invoked on live execution path -- must fail (must be shadow-only)"
        return "Model invoked outside its allowed_models registry entry -- must fail"
    return "Deterministic control component replaced by model invocation -- must fail (control/model confusion)"


def _binding_fallback_policy(orig_fallback: str, is_model: bool) -> str:
    if not orig_fallback or orig_fallback.upper() == "N/A":
        return "no_fallback"
    if not is_model:
        return "no_fallback (deterministic control)"
    return f"fallback_to:{orig_fallback}; same_provider_class_only; max_one_step"


def _harden_one_binding_row(r: dict[str, str], is_model: bool) -> dict[str, str]:
    binding_id = r["binding_id"]
    owner = BINDING_OWNER.get(binding_id, "Cross_Cutting_Observability_Replay_Audit")
    symbolic, lane = BINDING_SYMBOLIC.get(binding_id, ("symbolic.unknown", "unknown"))
    notes_parts: list[str] = []
    if binding_id not in BINDING_REQ_REFS:
        notes_parts.append("REQ_LINKAGE_MISSING")
    if not is_model and r.get("auto_fallback_binding", "").strip() not in {"", "N/A"}:
        notes_parts.append("WARNING: deterministic control had auto_fallback_binding -- forced no_fallback")

    return {
        "binding_id": binding_id,
        "model_role": r.get("model_role", ""),
        "model_type": r.get("model_type", ""),
        "attention_mechanism": r.get("attention_mechanism", ""),
        "use_case": r.get("use_case", ""),
        "allowed_models": r.get("allowed_models", ""),
        "prohibited_models": r.get("prohibited_models", ""),
        "architecture_invariant": r.get("architecture_invariant", ""),
        "layer_binding": r.get("layer_binding", ""),
        "output_type": r.get("output_type", ""),
        "output_head": r.get("output_head", ""),
        "confidence_threshold": r.get("confidence_threshold", ""),
        "auto_fallback_binding": r.get("auto_fallback_binding", ""),
        "req_id_refs": BINDING_REQ_REFS.get(binding_id, ""),
        "canonical_owner_surface": owner,
        "is_model_invocation": "true" if is_model else "false",
        "provider_lane": lane,
        "symbolic_model_id": symbolic,
        "registry_digest_ref": "",  # filled by registry sync; empty = unsigned
        "allowed_fallback_policy": _binding_fallback_policy(r.get("auto_fallback_binding", ""), is_model),
        "fallback_requires_recertification": "true" if is_model else "false",
        "otel_span_expected": _binding_otel_span(binding_id, owner, is_model),
        "negative_control_expected": _binding_negative_control(binding_id, is_model),
        "acceptance_command": (
            f"python -m pytest tests/unit/agentic_core/L5_safety/registry/"
            f"test_{binding_id.lower().replace('-', '_')}.py -v --no-header"
        ),
        "ci_gate_name": (
            "ops_scripts/ci/check_model_binding_registry.py" if is_model
            else "ops_scripts/ci/check_nonmodel_control_binding_registry.py"
        ),
        "external_proof_pack_ref": EXTERNAL_PROOF_PACKS.get(owner, ""),
        "harmonization_notes": " | ".join(notes_parts),
    }


def harden_model_binding_split() -> tuple[int, int]:
    """Split the model_binding matrix into model + nonmodel files."""
    csv.field_size_limit(2_000_000)
    with MATRIX_MODEL.open("r", encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))

    model_rows: list[dict[str, str]] = []
    nonmodel_rows: list[dict[str, str]] = []
    for r in rows:
        bid = r["binding_id"]
        # BIND-003 is in BOTH sets — user flagged it; we put it ONLY in nonmodel.
        if bid in NONMODEL_CONTROL_BINDING_IDS:
            nonmodel_rows.append(_harden_one_binding_row(r, is_model=False))
        elif bid in MODEL_BINDING_IDS:
            model_rows.append(_harden_one_binding_row(r, is_model=True))
        else:
            # Unknown binding — default to nonmodel for safety
            nonmodel_rows.append(_harden_one_binding_row(r, is_model=False))

    with MATRIX_MODEL.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(BINDING_OUT_COLUMNS))
        writer.writeheader()
        writer.writerows(model_rows)

    with MATRIX_NONMODEL.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(BINDING_OUT_COLUMNS))
        writer.writeheader()
        writer.writerows(nonmodel_rows)

    return len(model_rows), len(nonmodel_rows)


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="Harden the 10C side-matrices (W4d-3).")
    parser.add_argument("--dry-run", action="store_true", help="Compute counts only.")
    args = parser.parse_args()

    if not LEDGER.exists():
        print(f"FATAL: ledger not found at {LEDGER}", file=sys.stderr)
        return 2

    print(f"[harden W4d-3 matrices] reading ledger from {LEDGER}")
    ledger = _load_ledger()
    print(f"[harden W4d-3 matrices] loaded {len(ledger)} ledger rows for owner-surface joining")

    if args.dry_run:
        print("[harden W4d-3 matrices] dry-run only; no files written")
        return 0

    n_reqs = harden_reqs_vs_10a(ledger)
    print(f"[harden W4d-3 matrices] requirements_vs_10a: wrote {n_reqs} rows with {len(REQS_VS_10A_OUT_COLUMNS)} columns")

    n_metric = harden_metric_obligation(ledger)
    print(f"[harden W4d-3 matrices] metric_obligation:    wrote {n_metric} rows with {len(METRIC_OBLIGATION_OUT_COLUMNS)} columns")

    n_model, n_nonmodel = harden_model_binding_split()
    print(f"[harden W4d-3 matrices] model_binding (split): wrote {n_model} model rows + {n_nonmodel} nonmodel rows with {len(BINDING_OUT_COLUMNS)} columns each")
    print(f"[harden W4d-3 matrices] nonmodel control file: {MATRIX_NONMODEL.relative_to(REPO_ROOT)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
