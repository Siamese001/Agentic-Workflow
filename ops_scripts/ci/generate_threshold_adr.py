"""Generate the semantic-cache threshold ADR from W1p4 sweep evidence.

Reads ``artifacts/certification/threshold_sweep_results.json`` and emits
BOTH:

  1. ``artifacts/certification/semantic_cache_threshold_adr.json`` —
     machine-readable ADR with owner_approval.status=PENDING_APPROVAL and
     implementation_status=PROPOSED_NOT_APPLIED and config_binding.applied=false.

  2. ``docs/adr/semantic_cache_threshold_recalibration.md`` — human-readable
     ADR pulled from the same source-of-truth.

This script NEVER sets owner_approval.status to APPROVED and NEVER flips
config_binding.applied to true. An approver must edit the JSON by hand and
commit separately. The composer refuses to flip
R1B_PRODUCTION_THRESHOLD_PROOF to PASS without APPROVED + APPLIED + threshold
match + FP=0 at that threshold (see scripts/compose_semantic_cache_subclaims.py).

Exit codes:
  - 0 on successful ADR emit
  - 2 when sweep_results is absent or the sweep did not complete
  - 3 on unexpected error
"""

from __future__ import annotations

from agentic_core.config.model_catalog import (
    BGE_M3_MODEL_ID,
)

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SWEEP_PATH = REPO_ROOT / "artifacts" / "certification" / "threshold_sweep_results.json"
ADR_JSON_PATH = REPO_ROOT / "artifacts" / "certification" / "semantic_cache_threshold_adr.json"
ADR_MD_PATH = REPO_ROOT / "docs" / "adr" / "semantic_cache_threshold_recalibration.md"
DATASET_PATH = REPO_ROOT / "data" / "certification" / "calibration_pairs.json"

ADR_ID = "SEMCACHE-THRESH-001"
ADR_VERSION = "1.0"
OLD_THRESHOLD = 0.95


def _now_utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_sweep() -> tuple[dict | None, str | None]:
    if not SWEEP_PATH.exists():
        return (None, f"sweep_results_missing: {SWEEP_PATH.relative_to(REPO_ROOT)}")
    try:
        return (json.loads(SWEEP_PATH.read_text(encoding="utf-8")), None)
    except (json.JSONDecodeError, OSError) as exc:
        return (None, f"sweep_results_malformed: {exc}")


def _safety_rationale(sweep: dict, recommended: float | None) -> str:
    if recommended is None:
        return (
            "NO_SAFE_THRESHOLD_FOUND. At every candidate threshold in the sweep, "
            "at least one of the four safety conditions was violated: "
            "(fp=0 AND unsafe_fp=0 AND policy/freshness preserved AND "
            "lexical-overlap preserved AND recall >= recall_at_0.95). "
            "The honest finding is that this dataset contains adversarial "
            "lexical-overlap pairs (e.g. 'cancel order' vs 'place order', "
            "'enable 2FA' vs 'disable 2FA') where dense cosine similarity "
            "cannot discriminate semantically opposite intents. "
            "Deploying any of the candidate thresholds would admit at least "
            "one safety-critical false positive. Per Rule 1 (no silent "
            "threshold lowering), this ADR records the finding and does NOT "
            "recommend any change. Remediation paths documented in the "
            "recommendation section."
        )
    # Find the recommended row
    m = next(
        (r for r in sweep.get("metrics_table", []) if r["threshold"] == recommended),
        None,
    )
    if not m:
        return f"recommended={recommended} but metrics row missing — regenerate sweep."
    return (
        f"At threshold {recommended}, the calibration sweep reports "
        f"fp={m['fp']}, unsafe_fp={m['unsafe_fp_count']}, "
        f"precision={m['precision']}, recall={m['recall']}, "
        f"accuracy={m['accuracy']}. All four safety invariants hold: "
        f"fp=0, unsafe_fp=0, policy/freshness negatives preserved, "
        f"lexical-overlap negatives preserved, and recall does not "
        f"regress against the 0.95 baseline. Safety-critical false "
        f"positives are zero across {sum(1 for _ in sweep.get('per_pair_results', []) if not _.get('expected_label') == 'POSITIVE')} "
        f"measured negatives."
    )


def _rollback_rule(recommended: float | None) -> str:
    if recommended is None:
        return (
            "Not applicable — no threshold change is recommended. If the "
            "dataset is expanded or the model is upgraded such that a "
            "safe threshold emerges, regenerate the ADR via "
            "`python ops_scripts/ci/generate_threshold_adr.py`."
        )
    return (
        f"If, after deployment at threshold {recommended}, production "
        f"telemetry reports any of: (a) cache_hit_correctness_rate < 99%, "
        f"(b) any safety-critical mis-reuse incident, (c) drift-detected "
        f"signal from UWG receipts inspection, THEN revert to {OLD_THRESHOLD} "
        f"immediately by unsetting SEMANTIC_CACHE_THRESHOLD_DYNAMIC (if set) "
        f"or by rolling back the config commit that applied the change. "
        f"Hold at {OLD_THRESHOLD} for 7 days minimum; re-run sweep on the "
        f"enlarged dataset before reattempting."
    )


def _compose_adr_json(sweep: dict) -> dict:
    recommended = sweep.get("recommended_threshold")
    dataset = json.loads(DATASET_PATH.read_text(encoding="utf-8"))
    metrics_table = sweep.get("metrics_table", [])

    return {
        "adr_id": ADR_ID,
        "adr_version": ADR_VERSION,
        "created_utc": _now_utc(),
        "created_by": "w1_phase_4_threshold_calibration",
        "generator": "ops_scripts/ci/generate_threshold_adr.py",
        "old_threshold": OLD_THRESHOLD,
        "recommended_threshold": recommended,
        "recommendation_status": sweep.get("overall_status"),
        "model": {
            "identifier": BGE_M3_MODEL_ID,
            "provider": "bge-m3",
            "operation": "dense_cosine",
            "dim": 1024,
        },
        "dataset": {
            "path": str(DATASET_PATH.relative_to(REPO_ROOT)),
            "sha256": _sha256(DATASET_PATH),
            "dataset_id": dataset.get("dataset_id"),
            "schema_version": dataset.get("schema_version"),
            "n_pairs": dataset["statistics"]["total_pairs"],
            "n_positives": dataset["statistics"]["total_positives"],
            "n_negatives": dataset["statistics"]["total_negatives"],
            "n_measurable": dataset["statistics"]["similarity_measurement_pairs"],
        },
        "sweep_source": {
            "path": str(SWEEP_PATH.relative_to(REPO_ROOT)),
            "sha256": _sha256(SWEEP_PATH),
            "sweep_status": sweep.get("overall_status"),
        },
        "metrics_table": metrics_table,
        "recommendation_rule": sweep.get("recommendation_rule", ""),
        "safety_rationale": _safety_rationale(sweep, recommended),
        "rollback_rule": _rollback_rule(recommended),
        "owner_approval": {
            "status": "PENDING_APPROVAL",
            "approver": None,
            "approved_utc": None,
            "approval_evidence_ref": None,
        },
        "implementation_status": "PROPOSED_NOT_APPLIED",
        "config_binding": {
            "target_key": "agentic_core.L4_state.utils.memory.semantic_cache_manager._TIER_THRESHOLD_DEFAULTS.dynamic",
            "current_value": OLD_THRESHOLD,
            "proposed_value": recommended,
            "applied": False,
            "apply_procedure": (
                "This ADR is not automatically applied. To apply (after "
                "approval), modify _TIER_THRESHOLD_DEFAULTS in "
                "agentic_core/L4_state/utils/memory/semantic_cache_manager.py "
                "and ship the change via the normal PR/review flow. Do NOT "
                "apply via environment variable — that triggers "
                "OVERRIDE_PRESENT in the threshold probe."
            ),
        },
        "anti_cheat_invariants": {
            "rule_1_no_silent_threshold_lowering": True,
            "rule_7_adr_gate": True,
            "generator_never_auto_approves": True,
            "generator_never_sets_applied_true": True,
            "generator_emits_pending_approval_only": True,
        },
    }


def _compose_adr_md(adr: dict) -> str:
    """Produce the human-readable ADR with values pulled from adr dict."""
    recommended = adr["recommended_threshold"]
    rec_str = f"{recommended}" if recommended is not None else "**NONE (no safe threshold found)**"
    metrics_rows = "\n".join(
        f"| {m['threshold']:.2f} | {m['tp']} | {m['fn']} | {m['tn']} | {m['fp']} | "
        f"{m['precision']:.3f} | {m['recall']:.3f} | {m['fpr']:.3f} | {m['fnr']:.3f} | "
        f"{m['unsafe_fp_count']} | {str(m['policy_freshness_preserved']).lower()} | "
        f"{str(m['lexical_overlap_preserved']).lower()} |"
        for m in adr["metrics_table"]
    )
    return f"""# ADR {adr['adr_id']} — Semantic Cache Threshold Recalibration

**Status**: PROPOSED_NOT_APPLIED  
**Owner approval**: PENDING_APPROVAL  
**ADR version**: {adr['adr_version']}  
**Created**: {adr['created_utc']}  
**Generator**: `{adr['generator']}`

## Context

The semantic cache currently uses a dense-cosine similarity threshold of
**{adr['old_threshold']}** (dynamic tier). W1 phase 3 calibration evidence
(commit `f676009c16`) flagged this threshold as producing false negatives
on legitimate paraphrase queries (low recall) while also potentially
admitting false positives on adversarial near-miss pairs (safety risk).

W1 phase 4 ran an expanded calibration sweep across six candidate
thresholds on a dataset of **{adr['dataset']['n_pairs']} pairs**
({adr['dataset']['n_positives']} positives / {adr['dataset']['n_negatives']} negatives) using the live
**{adr['model']['identifier']}** embedding model ({adr['model']['operation']},
{adr['model']['dim']}-dim).

## Decision

**Recommended threshold**: {rec_str}

**Sweep status**: `{adr['recommendation_status']}`

{adr['safety_rationale']}

## Recommendation Rule

```
{adr['recommendation_rule']}
```

## Metrics Table

| Threshold | TP | FN | TN | FP | Precision | Recall | FPR | FNR | Unsafe FP | Policy Preserved | Lexical-Overlap Preserved |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
{metrics_rows}

## Dataset Provenance

- Path: `{adr['dataset']['path']}`
- SHA-256: `{adr['dataset']['sha256']}`
- Dataset ID: `{adr['dataset']['dataset_id']}`
- Schema version: `{adr['dataset']['schema_version']}`

## Consequences

### If approved and applied at threshold {rec_str}

(If `recommended_threshold` is NONE, this section is a placeholder. No
config change is authorized until a future sweep — on an enlarged
dataset or with an upgraded model — surfaces a safe threshold.)

- Positive queries that score in [{rec_str}, 0.95) would start cache-hitting.
- Safety invariants (FP=0, unsafe_FP=0, policy/freshness preserved,
  lexical-overlap preserved) MUST be re-measured post-deployment via
  UWG receipt telemetry within 7 days.

### If not approved

- R1B_PRODUCTION_THRESHOLD_PROOF stays at `CALIBRATION_GAP`.
- R1B_DENSE_SIMILARITY_COMPOSITION_PROOF stays at `PARTIAL` (Rule 5).
- RTC-REQ-055 stays at `PARTIAL` until either the threshold is
  approved+applied OR the calibration is redone on a tightened dataset.

## Rollback Rule

{adr['rollback_rule']}

## Apply Procedure

{adr['config_binding']['apply_procedure']}

## Owner Approval

| Field | Value |
|---|---|
| Status | PENDING_APPROVAL |
| Approver | _(pending)_ |
| Approved UTC | _(pending)_ |
| Approval evidence ref | _(pending)_ |

An approver must:

1. Review the metrics table and confirm the recommendation rule output.
2. Edit `artifacts/certification/semantic_cache_threshold_adr.json` and set
   `owner_approval.status = APPROVED`, `owner_approval.approver = <name>`,
   `owner_approval.approved_utc = <ISO-8601>`.
3. Ship the config change (see Apply Procedure) in a separate PR that sets
   `config_binding.applied = true` AFTER the config file change lands.
4. Re-run `python scripts/compose_semantic_cache_subclaims.py` and observe
   the upgraded subclaim verdict.

## Anti-Cheat Invariants Honored

- Rule 1: no silent threshold lowering (this ADR is PROPOSED_NOT_APPLIED)
- Rule 7: ADR gate (composer refuses PASS without APPROVED + APPLIED + FP=0)
- Generator never auto-approves
- Generator never sets `applied = true`

## References

- Sweep evidence: `{adr['sweep_source']['path']}` (SHA-256: `{adr['sweep_source']['sha256']}`)
- W1p3 plan: `.codex/plans/rtc-w1-phase3-blockers-close-d7a2f1.md`
- W1p4 plan: `.codex/plans/rtc-w1-phase4-threshold-adr-b4c9e1.md`
- Composer: `scripts/compose_semantic_cache_subclaims.py`
- Threshold SSOT: `agentic_core/L4_state/utils/memory/semantic_cache_manager.py`
"""


def main() -> int:
    sweep, err = _load_sweep()
    if err:
        print(f"[generate_adr] FAIL: {err}", file=sys.stderr)
        print("[generate_adr] Run first: python tools/certification/evidence/probe_threshold_sweep.py", file=sys.stderr)
        return 2
    assert sweep is not None

    if sweep.get("overall_status") not in ("SWEEP_COMPLETE", "NO_SAFE_THRESHOLD_FOUND"):
        print(
            f"[generate_adr] FAIL: sweep status = {sweep.get('overall_status')}. "
            f"ADR generation requires SWEEP_COMPLETE or NO_SAFE_THRESHOLD_FOUND.",
            file=sys.stderr,
        )
        return 2

    adr_json = _compose_adr_json(sweep)
    adr_md = _compose_adr_md(adr_json)

    # Write both atomically
    ADR_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    ADR_MD_PATH.parent.mkdir(parents=True, exist_ok=True)
    ADR_JSON_PATH.write_text(json.dumps(adr_json, indent=2, sort_keys=True), encoding="utf-8")
    ADR_MD_PATH.write_text(adr_md, encoding="utf-8")

    # Enforce invariants in final output
    assert adr_json["owner_approval"]["status"] == "PENDING_APPROVAL"
    assert adr_json["implementation_status"] == "PROPOSED_NOT_APPLIED"
    assert adr_json["config_binding"]["applied"] is False

    print(f"[generate_adr] wrote: {ADR_JSON_PATH.relative_to(REPO_ROOT)}")
    print(f"[generate_adr] wrote: {ADR_MD_PATH.relative_to(REPO_ROOT)}")
    print(f"[generate_adr] recommended_threshold = {adr_json['recommended_threshold']}")
    print(f"[generate_adr] owner_approval.status = PENDING_APPROVAL (unchanged)")
    print(f"[generate_adr] implementation_status = PROPOSED_NOT_APPLIED (unchanged)")
    print(f"[generate_adr] config_binding.applied = False (unchanged)")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"[generate_adr] HARNESS_ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(3)
