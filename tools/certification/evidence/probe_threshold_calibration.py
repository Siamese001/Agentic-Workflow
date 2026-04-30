"""Probe — production-threshold calibration via BGE-M3 (W1 phase 3 blocker #2).

Reads ``data/certification/calibration_pairs.json`` and measures dense
cosine similarity for every similarity-testable pair (paraphrase positives,
near-miss negatives, lexical-overlap negatives). Compares each score against
the SSOT production threshold (``tier_similarity_threshold('dynamic')``).
``reference_contract_negative`` pairs are documentation anchors — NOT measured
for similarity; they cross-reference NEG-5/6/7 contract-level negatives.

Anti-cheat rules honored (user 2026-04-30):
  Rule 1 — no silent threshold lowering. Probe reads SSOT threshold; does
           not modify env vars; records override state for auditor review.
  Rule 2 — no silent fallback PASS. Probe requires BGE-M3 operational; if
           unavailable, emits INFRASTRUCTURE_GAP.
  Rule 4 — no UWG bypass. Probe does not write cache / does not mutate state.

Output: ``artifacts/certification/semantic_cache_calibration_results.json``

Status ladder:
  - PASS              -> positives all >= threshold AND negatives all < threshold
  - CALIBRATION_GAP   -> any positive < threshold OR any negative >= threshold
  - OVERRIDE_PRESENT  -> SEMANTIC_CACHE_THRESHOLD_DYNAMIC env set (BLOCKED)
  - INFRASTRUCTURE_GAP -> BGE-M3 not operational
  - DATASET_MISSING   -> calibration_pairs.json not found
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from tools.certification.evidence import write_evidence, rel  # noqa: E402

DATASET_PATH = REPO_ROOT / "data" / "certification" / "calibration_pairs.json"

OVERRIDE_ENV_VARS = (
    "SEMANTIC_CACHE_THRESHOLD_DYNAMIC",
    "SEMANTIC_CACHE_THRESHOLD_STATIC",
    "SEMANTIC_CACHE_HYBRID_THRESHOLD",
)


def _check_override_active() -> dict[str, str | None]:
    return {v: os.environ.get(v) for v in OVERRIDE_ENV_VARS}


def _read_ssot_threshold() -> tuple[float | None, str | None]:
    """Read the SSOT dynamic-tier threshold. Returns (value, error_or_None)."""
    try:
        from agentic_core.L4_state.utils.memory.semantic_cache_manager import (
            tier_similarity_threshold,
        )
    except ImportError as exc:
        return (None, f"SSOT_IMPORT_FAILED: {exc}")
    return (tier_similarity_threshold("dynamic"), None)


def _check_bge_m3_operational() -> tuple[bool, str]:
    """Dry-run the operational probe logic without re-writing its artifact."""
    op_artifact = REPO_ROOT / "artifacts" / "certification" / "bge_m3_operational_proof.json"
    if not op_artifact.exists():
        return (False, "bge_m3_operational_proof.json not present — run probe_bge_m3_operational.py first")
    try:
        op = json.loads(op_artifact.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return (False, f"bge_m3_operational_proof.json malformed: {exc}")
    if op.get("status") != "OPERATIONAL":
        return (False, f"BGE-M3 not OPERATIONAL (status={op.get('status')})")
    return (True, "ok")


def _load_dataset() -> tuple[dict | None, str | None]:
    if not DATASET_PATH.exists():
        return (None, f"DATASET_MISSING: {DATASET_PATH.relative_to(REPO_ROOT)}")
    try:
        return (json.loads(DATASET_PATH.read_text(encoding="utf-8")), None)
    except (json.JSONDecodeError, OSError) as exc:
        return (None, f"DATASET_MALFORMED: {exc}")


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    import math
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def _measure_similarities(dataset: dict) -> list[dict]:
    """Embed every measurable pair via bge_runtime and compute cosine sim."""
    from agentic_core.embeddings import bge_runtime  # noqa: PLC0415

    # v1 class was "reference_contract_negative"; v2 renamed to
    # "policy_tenant_freshness_reuse_negative". Both remain non-measurable
    # (contract-level documentation anchors, not similarity pairs).
    NON_MEASURABLE_CLASSES = {
        "reference_contract_negative",
        "policy_tenant_freshness_reuse_negative",
    }
    measurable = [
        p for p in dataset["pairs"]
        if p["class"] not in NON_MEASURABLE_CLASSES
    ]
    # Batch-embed all texts for speed
    all_texts: list[str] = []
    for p in measurable:
        all_texts.append(p["text_a"])
        all_texts.append(p["text_b"])
    vectors = bge_runtime.bge_embed_batch(all_texts)

    POSITIVE_CLASSES = {
        "paraphrase_positive",
        "abbreviation_definition_positive",
        "short_form_reminder_positive",
    }
    results = []
    for i, p in enumerate(measurable):
        vec_a = vectors[i * 2]
        vec_b = vectors[i * 2 + 1]
        sim = _cosine_similarity(list(vec_a), list(vec_b))
        results.append({
            "id": p["id"],
            "class": p["class"],
            "expected_label": (
                "POSITIVE" if p["class"] in POSITIVE_CLASSES else "NEGATIVE"
            ),
            "text_a": p["text_a"],
            "text_b": p["text_b"],
            "similarity_score": round(float(sim), 6),
            "notes": p.get("notes", ""),
        })
    return results


def _classify_results(
    per_pair: list[dict], threshold: float
) -> dict:
    """Apply threshold, compute aggregate + status."""
    positives = [r for r in per_pair if r["expected_label"] == "POSITIVE"]
    negatives = [r for r in per_pair if r["expected_label"] == "NEGATIVE"]

    for r in per_pair:
        r["passed_at_threshold"] = r["similarity_score"] >= threshold
        if r["expected_label"] == "POSITIVE":
            r["agreement"] = "HIT" if r["passed_at_threshold"] else "FALSE_NEGATIVE"
        else:
            r["agreement"] = "FALSE_POSITIVE" if r["passed_at_threshold"] else "MISS"

    positive_pass_count = sum(1 for r in positives if r["passed_at_threshold"])
    negative_miss_count = sum(1 for r in negatives if not r["passed_at_threshold"])
    false_positive_count = sum(
        1 for r in negatives if r["passed_at_threshold"]
    )
    false_negative_count = sum(
        1 for r in positives if not r["passed_at_threshold"]
    )

    return {
        "total_positives": len(positives),
        "total_negatives": len(negatives),
        "positive_pass_count": positive_pass_count,
        "negative_miss_count": negative_miss_count,
        "false_positive_count": false_positive_count,
        "false_negative_count": false_negative_count,
        "positive_pass_rate": (
            positive_pass_count / len(positives) if positives else 0.0
        ),
        "negative_miss_rate": (
            negative_miss_count / len(negatives) if negatives else 0.0
        ),
        "perfect_discrimination": (
            false_positive_count == 0 and false_negative_count == 0
        ),
    }


def main() -> int:
    # 1. Override check (Rule 1)
    overrides = _check_override_active()
    override_active = any(v not in (None, "") for v in overrides.values())

    # 2. SSOT threshold
    threshold, threshold_err = _read_ssot_threshold()

    # 3. BGE-M3 operational check (Rule 2)
    bge_ok, bge_detail = _check_bge_m3_operational()

    # 4. Dataset
    dataset, dataset_err = _load_dataset()

    # Short-circuit ladder — each condition emits its own INFRASTRUCTURE/BLOCKED
    if override_active:
        status = "OVERRIDE_PRESENT"
        rationale = (
            f"threshold override env var(s) set: "
            f"{ {k: v for k, v in overrides.items() if v} }. "
            f"Per Rule 1: calibration cannot PASS with override active."
        )
        aggregate: dict = {}
        per_pair: list[dict] = []
    elif threshold_err:
        status = "INFRASTRUCTURE_GAP"
        rationale = threshold_err
        aggregate = {}
        per_pair = []
    elif not bge_ok:
        status = "INFRASTRUCTURE_GAP"
        rationale = f"BGE-M3 not operational: {bge_detail}. Calibration requires OPERATIONAL status."
        aggregate = {}
        per_pair = []
    elif dataset_err:
        status = "DATASET_MISSING"
        rationale = dataset_err
        aggregate = {}
        per_pair = []
    else:
        # Happy path — measure similarities
        try:
            per_pair = _measure_similarities(dataset)
        except Exception as exc:  # noqa: BLE001 - probe reports load errors
            status = "INFRASTRUCTURE_GAP"
            rationale = f"similarity measurement failed: {type(exc).__name__}: {exc}"
            aggregate = {}
            per_pair = []
        else:
            aggregate = _classify_results(per_pair, threshold)  # type: ignore[arg-type]
            if aggregate["perfect_discrimination"]:
                status = "PASS"
                rationale = (
                    f"all {aggregate['total_positives']} positives pass at >= "
                    f"{threshold}; all {aggregate['total_negatives']} negatives "
                    f"miss at < {threshold}; FP=0 FN=0."
                )
            else:
                status = "CALIBRATION_GAP"
                rationale = (
                    f"calibration gap at production threshold {threshold}: "
                    f"FP={aggregate['false_positive_count']} "
                    f"FN={aggregate['false_negative_count']}. "
                    f"Per Rule 1: threshold cannot be silently lowered. "
                    f"ADR-backed recalibration is the only sanctioned path."
                )

    payload = {
        "probe": "threshold_calibration",
        "phase": "W1p3",
        "blocker": "2_production_threshold_proof",
        "subclaim_target": "R1B_PRODUCTION_THRESHOLD_PROOF",
        "dataset_reference": {
            "path": str(DATASET_PATH.relative_to(REPO_ROOT)),
            "dataset_id": dataset.get("dataset_id") if dataset else None,
            "schema_version": dataset.get("schema_version") if dataset else None,
        },
        "production_threshold_default": threshold,
        "threshold_actual": threshold,  # we measure at production default
        "threshold_ssot_module": (
            "agentic_core.L4_state.utils.memory.semantic_cache_manager"
        ),
        "override_envs_observed": overrides,
        "override_active": override_active,
        "bge_m3_operational_check": {
            "ok": bge_ok,
            "detail": bge_detail,
        },
        "per_pair_results": per_pair,
        "aggregate": aggregate,
        "overall_status": status,
        "rationale": rationale,
        "adr_path_note": (
            "If CALIBRATION_GAP persists, the only sanctioned path is ADR-backed "
            "recalibration. Create artifacts/certification/semantic_cache_"
            "threshold_adr.json describing the target threshold + scientific "
            "justification + rollback plan. This probe does NOT auto-create "
            "the ADR."
        ),
        "anti_cheat_rules_honored": {
            "rule_1_no_silent_threshold_lowering": True,
            "rule_2_no_silent_fallback_pass": True,
            "probe_did_not_modify_threshold_env": True,
            "probe_did_not_create_adr": True,
            "probe_did_not_write_sidecar": True,
            "reference_contract_negatives_not_measured_for_similarity": True,
        },
    }

    path = write_evidence("semantic_cache_calibration_results.json", payload)
    print(f"[probe_cal] status={status}")
    if aggregate:
        print(
            f"[probe_cal] positives {aggregate['positive_pass_count']}/"
            f"{aggregate['total_positives']} pass; negatives "
            f"{aggregate['negative_miss_count']}/"
            f"{aggregate['total_negatives']} miss; "
            f"FP={aggregate['false_positive_count']} "
            f"FN={aggregate['false_negative_count']}"
        )
    print(f"[probe_cal] wrote: {rel(path)}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"[probe_cal] HARNESS_ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(3)
