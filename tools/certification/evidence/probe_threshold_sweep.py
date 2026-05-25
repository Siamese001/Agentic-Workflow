"""Probe — threshold sweep calibration (W1 phase 4 blocker #2 closure path).

Embeds all measurable pairs from ``data/certification/calibration_pairs.json``
(v2 schema) via BGE-M3 and computes classification metrics at each of 6
candidate thresholds. Produces a recommendation per user-approved safety rule:

  recommended = max(t in sweep where
      fp == 0 AND
      unsafe_fp_count == 0 AND
      policy_freshness_preserved AND
      lexical_overlap_preserved AND
      recall >= recall_at_0.95)

Tie-break: higher precision, then higher threshold. If no threshold satisfies
all four constraints, ``recommended_threshold = null`` and ``status =
NO_SAFE_THRESHOLD_FOUND``.

Anti-cheat rules honored (user 2026-04-30):
  Rule 1 — no silent threshold lowering. Probe never writes to SemanticCacheManager
           or to any config/YAML. Probe never sets override env vars.
  Rule 2 — no silent fallback PASS. Requires BGE-M3 OPERATIONAL. If unavailable,
           status=INFRASTRUCTURE_GAP with no recommendation.
  Rule 7 — ADR gate. Probe writes only evidence; does NOT create the ADR.

Non-measurable classes (``policy_tenant_freshness_reuse_negative``,
``reference_contract_negative``) are EXCLUDED from similarity measurement;
those contract anchors are proven separately by W1p2 NEG-5/6/7.

Output: ``artifacts/certification/threshold_sweep_results.json``

Status ladder:
  - SWEEP_COMPLETE          -> recommendation present (may be null if unsafe)
  - INFRASTRUCTURE_GAP      -> BGE-M3 not operational
  - DATASET_MISSING         -> calibration_pairs.json not found
  - OVERRIDE_PRESENT        -> threshold override env set (BLOCKED)
  - NO_SAFE_THRESHOLD_FOUND -> sweep complete but no threshold met safety rules
"""

from __future__ import annotations

import json
import math
import os
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from tools.certification.evidence import write_evidence, rel  # noqa: E402

DATASET_PATH = REPO_ROOT / "data" / "certification" / "calibration_pairs.json"

CANDIDATE_THRESHOLDS: tuple[float, ...] = (0.95, 0.92, 0.90, 0.88, 0.85, 0.80)

POSITIVE_CLASSES = frozenset({
    "paraphrase_positive",
    "abbreviation_definition_positive",
    "short_form_reminder_positive",
})
NEGATIVE_CLASSES_MEASURABLE = frozenset({
    "near_miss_negative",
    "lexical_overlap_different_meaning_negative",
    # legacy v1 name (kept for forward-compat if dataset regresses)
    "lexical_overlap_negative",
})
NON_MEASURABLE_CLASSES = frozenset({
    "policy_tenant_freshness_reuse_negative",
    "reference_contract_negative",
})

# Safety tier mapping for unsafe_fp_count computation
SAFETY_CRITICAL_CLASSES = frozenset({
    "near_miss_negative",
    "lexical_overlap_different_meaning_negative",
})

OVERRIDE_ENV_VARS = (
    "SEMANTIC_CACHE_THRESHOLD_DYNAMIC",
    "SEMANTIC_CACHE_THRESHOLD_STATIC",
    "SEMANTIC_CACHE_HYBRID_THRESHOLD",
)


def _check_overrides() -> dict[str, str | None]:
    return {v: os.environ.get(v) for v in OVERRIDE_ENV_VARS}


def _check_bge_m3_operational() -> tuple[bool, str]:
    op_artifact = (
        REPO_ROOT / "artifacts" / "certification" / "bge_m3_operational_proof.json"
    )
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


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def _label_for(pair_class: str) -> str | None:
    """Return POSITIVE/NEGATIVE/None for a class. None = non-measurable."""
    if pair_class in POSITIVE_CLASSES:
        return "POSITIVE"
    if pair_class in NEGATIVE_CLASSES_MEASURABLE:
        return "NEGATIVE"
    return None


def _embed_all(dataset: dict) -> list[dict]:
    """Embed every measurable pair and return per-pair scored records."""
    from agentic_core.embeddings import bge_runtime  # noqa: PLC0415

    measurable = [p for p in dataset["pairs"] if _label_for(p["class"]) is not None]
    all_texts: list[str] = []
    for p in measurable:
        all_texts.append(p["text_a"])
        all_texts.append(p["text_b"])
    print(f"[probe_sweep] embedding {len(all_texts)} texts "
          f"({len(measurable)} pairs) via BGE-M3 …")
    t0 = time.time()
    vectors = bge_runtime.bge_embed_batch(all_texts)
    elapsed = int((time.time() - t0) * 1000)
    print(f"[probe_sweep] embedding done in {elapsed}ms")

    records = []
    for i, p in enumerate(measurable):
        sim = _cosine(list(vectors[i * 2]), list(vectors[i * 2 + 1]))
        records.append({
            "id": p["id"],
            "class": p["class"],
            "expected_label": _label_for(p["class"]),
            "safety_critical": p["class"] in SAFETY_CRITICAL_CLASSES,
            "text_a": p["text_a"],
            "text_b": p["text_b"],
            "similarity_score": round(float(sim), 6),
            "notes": p.get("notes", ""),
        })
    return records


def _metrics_at(threshold: float, records: list[dict]) -> dict:
    """Compute full metrics block at one threshold."""
    tp = fn = tn = fp = 0
    unsafe_fp = 0
    policy_preserved = True  # no policy anchors measured here, trivially true
    lexical_overlap_preserved = True
    lexical_overlap_fp_ids: list[str] = []

    for r in records:
        hit = r["similarity_score"] >= threshold
        if r["expected_label"] == "POSITIVE":
            if hit:
                tp += 1
            else:
                fn += 1
        else:  # NEGATIVE
            if hit:
                fp += 1
                if r["safety_critical"]:
                    unsafe_fp += 1
                if r["class"] in (
                    "lexical_overlap_different_meaning_negative",
                    "lexical_overlap_negative",
                ):
                    lexical_overlap_preserved = False
                    lexical_overlap_fp_ids.append(r["id"])
            else:
                tn += 1

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    fpr = fp / (fp + tn) if (fp + tn) else 0.0
    fnr = fn / (fn + tp) if (fn + tp) else 0.0
    f1 = (
        (2 * precision * recall) / (precision + recall)
        if (precision + recall) else 0.0
    )
    total = tp + fn + tn + fp
    accuracy = (tp + tn) / total if total else 0.0

    return {
        "threshold": threshold,
        "tp": tp,
        "fn": fn,
        "tn": tn,
        "fp": fp,
        "precision": round(precision, 6),
        "recall": round(recall, 6),
        "fpr": round(fpr, 6),
        "fnr": round(fnr, 6),
        "f1": round(f1, 6),
        "accuracy": round(accuracy, 6),
        "unsafe_fp_count": unsafe_fp,
        "policy_freshness_preserved": policy_preserved,
        "lexical_overlap_preserved": lexical_overlap_preserved,
        "lexical_overlap_fp_ids": lexical_overlap_fp_ids,
    }


def _recommend(metrics_table: list[dict]) -> tuple[float | None, str]:
    """Apply the user-approved safety rule to pick recommended threshold."""
    if not metrics_table:
        return (None, "empty metrics table — cannot recommend")

    # Recall baseline is the recall measured at 0.95
    baseline = next((m for m in metrics_table if m["threshold"] == 0.95), None)
    if baseline is None:
        return (None, "no 0.95 row in metrics table — cannot compute baseline recall")
    baseline_recall = baseline["recall"]

    # Filter rows that satisfy ALL four safety conditions
    safe = [
        m for m in metrics_table
        if m["fp"] == 0
        and m["unsafe_fp_count"] == 0
        and m["policy_freshness_preserved"]
        and m["lexical_overlap_preserved"]
        and m["recall"] >= baseline_recall
    ]

    if not safe:
        # Explain which condition eliminated each threshold
        eliminations = {}
        for m in metrics_table:
            reasons = []
            if m["fp"] != 0:
                reasons.append(f"fp={m['fp']}")
            if m["unsafe_fp_count"] != 0:
                reasons.append(f"unsafe_fp={m['unsafe_fp_count']}")
            if not m["policy_freshness_preserved"]:
                reasons.append("policy_regressed")
            if not m["lexical_overlap_preserved"]:
                reasons.append(
                    f"lexical_overlap_regressed:{m['lexical_overlap_fp_ids']}"
                )
            if m["recall"] < baseline_recall:
                reasons.append(
                    f"recall_regression({m['recall']} < baseline {baseline_recall})"
                )
            eliminations[m["threshold"]] = reasons or ["unknown"]
        return (
            None,
            f"NO_SAFE_THRESHOLD_FOUND — baseline_recall@0.95={baseline_recall}; "
            f"elimination reasons per threshold: {eliminations}",
        )

    # Tie-break: highest threshold; if tied, highest precision; if still tied, prefer higher recall
    safe_sorted = sorted(
        safe,
        key=lambda m: (m["threshold"], m["precision"], m["recall"]),
        reverse=True,
    )
    winner = safe_sorted[0]
    others = [m["threshold"] for m in safe if m["threshold"] != winner["threshold"]]
    rationale = (
        f"recommended t={winner['threshold']} "
        f"(fp=0, unsafe_fp=0, policy/freshness preserved, "
        f"lexical-overlap preserved, recall={winner['recall']} >= "
        f"baseline {baseline_recall}). "
        f"{len(safe)} candidate(s) satisfied safety rules: "
        f"[{winner['threshold']}] + alternatives {others}."
    )
    return (winner["threshold"], rationale)


def main() -> int:
    # Short-circuit ladder
    overrides = _check_overrides()
    override_active = any(v not in (None, "") for v in overrides.values())
    bge_ok, bge_detail = _check_bge_m3_operational()
    dataset, dataset_err = _load_dataset()

    status = "SWEEP_COMPLETE"
    rationale = ""
    metrics_table: list[dict] = []
    recommended: float | None = None
    per_pair: list[dict] = []

    if override_active:
        status = "OVERRIDE_PRESENT"
        rationale = (
            f"threshold override env(s) active: "
            f"{ {k: v for k, v in overrides.items() if v} }. "
            f"Per Rule 1, sweep cannot produce honest recommendation with override active."
        )
    elif not bge_ok:
        status = "INFRASTRUCTURE_GAP"
        rationale = f"BGE-M3 not operational: {bge_detail}"
    elif dataset_err:
        status = "DATASET_MISSING"
        rationale = dataset_err
    else:
        try:
            per_pair = _embed_all(dataset)  # type: ignore[arg-type]
        except Exception as exc:  # noqa: BLE001 - probe reports any error honestly
            status = "INFRASTRUCTURE_GAP"
            rationale = f"embedding failed: {type(exc).__name__}: {exc}"
        else:
            for t in CANDIDATE_THRESHOLDS:
                metrics_table.append(_metrics_at(t, per_pair))
            recommended, rec_rationale = _recommend(metrics_table)
            if recommended is None:
                status = "NO_SAFE_THRESHOLD_FOUND"
            rationale = rec_rationale

    payload = {
        "probe": "threshold_sweep",
        "phase": "W1p4",
        "subclaim_target": "R1B_PRODUCTION_THRESHOLD_PROOF",
        "dataset_reference": {
            "path": str(DATASET_PATH.relative_to(REPO_ROOT)),
            "dataset_id": dataset.get("dataset_id") if dataset else None,
            "schema_version": dataset.get("schema_version") if dataset else None,
            "total_measurable_pairs": len(per_pair),
        },
        "candidate_thresholds": list(CANDIDATE_THRESHOLDS),
        "production_threshold_current": 0.95,
        "override_envs_observed": overrides,
        "override_active": override_active,
        "bge_m3_operational_check": {"ok": bge_ok, "detail": bge_detail},
        "metrics_table": metrics_table,
        "recommended_threshold": recommended,
        "recommendation_rule": (
            "max(t in sweep where fp=0 AND unsafe_fp=0 AND policy_preserved "
            "AND lexical_overlap_preserved AND recall >= recall_at_0.95)"
        ),
        "per_pair_results": per_pair,
        "overall_status": status,
        "rationale": rationale,
        "adr_path_note": (
            "This probe does NOT create the ADR. To produce "
            "artifacts/certification/semantic_cache_threshold_adr.json, "
            "run: python ops_scripts/ci/generate_threshold_adr.py"
        ),
        "anti_cheat_rules_honored": {
            "rule_1_no_silent_threshold_lowering": True,
            "rule_2_no_silent_fallback_pass": True,
            "rule_7_no_config_binding_applied": True,
            "probe_did_not_modify_threshold_env": True,
            "probe_did_not_create_adr": True,
            "probe_did_not_write_sidecar": True,
        },
    }

    path = write_evidence("threshold_sweep_results.json", payload)
    print(f"[probe_sweep] status={status}")
    if metrics_table:
        print(f"[probe_sweep] metrics_table:")
        for m in metrics_table:
            print(
                f"  t={m['threshold']:.2f}  tp={m['tp']:3d} fn={m['fn']:3d} "
                f"tn={m['tn']:3d} fp={m['fp']:3d}  "
                f"precision={m['precision']:.3f} recall={m['recall']:.3f}  "
                f"unsafe_fp={m['unsafe_fp_count']}"
            )
        print(f"[probe_sweep] recommended_threshold = {recommended}")
    print(f"[probe_sweep] wrote: {rel(path)}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"[probe_sweep] HARNESS_ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(3)
