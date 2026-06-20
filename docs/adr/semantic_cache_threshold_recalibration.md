# ADR SEMCACHE-THRESH-001 — Semantic Cache Threshold Recalibration

**Status**: PROPOSED_NOT_APPLIED  
**Owner approval**: PENDING_APPROVAL  
**ADR version**: 1.0  
**Created**: 2026-05-01T18:04:12.067466Z  
**Generator**: `ops_scripts/ci/generate_threshold_adr.py`

**Current-state note (2026-06-15):** This remains intentionally not applied. The sweep found no safe threshold, and the pending approval state is part of the enforcement contract that prevents silent threshold lowering.

## Context

The semantic cache currently uses a dense-cosine similarity threshold of
**0.95** (dynamic tier). W1 phase 3 calibration evidence
(commit `f676009c16`) flagged this threshold as producing false negatives
on legitimate paraphrase queries (low recall) while also potentially
admitting false positives on adversarial near-miss pairs (safety risk).

W1 phase 4 ran an expanded calibration sweep across six candidate
thresholds on a dataset of **100 pairs**
(50 positives / 50 negatives) using the live
**BAAI/bge-m3** embedding model (dense_cosine,
1024-dim).

## Decision

**Recommended threshold**: **NONE (no safe threshold found)**

**Sweep status**: `NO_SAFE_THRESHOLD_FOUND`

NO_SAFE_THRESHOLD_FOUND. At every candidate threshold in the sweep, at least one of the four safety conditions was violated: (fp=0 AND unsafe_fp=0 AND policy/freshness preserved AND lexical-overlap preserved AND recall >= recall_at_0.95). The honest finding is that this dataset contains adversarial lexical-overlap pairs (e.g. 'cancel order' vs 'place order', 'enable 2FA' vs 'disable 2FA') where dense cosine similarity cannot discriminate semantically opposite intents. Deploying any of the candidate thresholds would admit at least one safety-critical false positive. Per Rule 1 (no silent threshold lowering), this ADR records the finding and does NOT recommend any change. Remediation paths documented in the recommendation section.

## Recommendation Rule

```
max(t in sweep where fp=0 AND unsafe_fp=0 AND policy_preserved AND lexical_overlap_preserved AND recall >= recall_at_0.95)
```

## Metrics Table

| Threshold | TP | FN | TN | FP | Precision | Recall | FPR | FNR | Unsafe FP | Policy Preserved | Lexical-Overlap Preserved |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| 0.95 | 6 | 44 | 38 | 2 | 0.750 | 0.120 | 0.050 | 0.880 | 2 | true | false |
| 0.92 | 10 | 40 | 38 | 2 | 0.833 | 0.200 | 0.050 | 0.800 | 2 | true | false |
| 0.90 | 15 | 35 | 37 | 3 | 0.833 | 0.300 | 0.075 | 0.700 | 3 | true | false |
| 0.88 | 23 | 27 | 35 | 5 | 0.821 | 0.460 | 0.125 | 0.540 | 5 | true | false |
| 0.85 | 28 | 22 | 34 | 6 | 0.824 | 0.560 | 0.150 | 0.440 | 6 | true | false |
| 0.80 | 33 | 17 | 23 | 17 | 0.660 | 0.660 | 0.425 | 0.340 | 17 | true | false |

## Dataset Provenance

- Path: `data\certification\calibration_pairs.json`
- SHA-256: `9acb8dc88fbd89fd9ff0db079c43e09bbfeeb6f704ee7905fe160c083f7d4fb4`
- Dataset ID: `rtc-req-055-calibration-v2`
- Schema version: `2`

## Consequences

### If approved and applied at threshold **NONE (no safe threshold found)**

(If `recommended_threshold` is NONE, this section is a placeholder. No
config change is authorized until a future sweep — on an enlarged
dataset or with an upgraded model — surfaces a safe threshold.)

- Positive queries that score in [**NONE (no safe threshold found)**, 0.95) would start cache-hitting.
- Safety invariants (FP=0, unsafe_FP=0, policy/freshness preserved,
  lexical-overlap preserved) MUST be re-measured post-deployment via
  UWG receipt telemetry within 7 days.

### If not approved

- R1B_PRODUCTION_THRESHOLD_PROOF stays at `CALIBRATION_GAP`.
- R1B_DENSE_SIMILARITY_COMPOSITION_PROOF stays at `PARTIAL` (Rule 5).
- RTC-REQ-055 stays at `PARTIAL` until either the threshold is
  approved+applied OR the calibration is redone on a tightened dataset.

## Rollback Rule

Not applicable — no threshold change is recommended. If the dataset is expanded or the model is upgraded such that a safe threshold emerges, regenerate the ADR via `python ops_scripts/ci/generate_threshold_adr.py`.

## Apply Procedure

This ADR is not automatically applied. To apply (after approval), modify _TIER_THRESHOLD_DEFAULTS in agentic_core/L4_state/utils/memory/semantic_cache_manager.py and ship the change via the normal PR/review flow. Do NOT apply via environment variable — that triggers OVERRIDE_PRESENT in the threshold probe.

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

- Sweep evidence: `artifacts\certification\threshold_sweep_results.json` (SHA-256: `cdac96f24ae01100e0c5d3eb0a581d42be5399a55f2febd834e875215256223b`)
- W1p3 plan: `.codex/plans/rtc-w1-phase3-blockers-close-d7a2f1.md`
- W1p4 plan: `.codex/plans/rtc-w1-phase4-threshold-adr-b4c9e1.md`
- Composer: `scripts/compose_semantic_cache_subclaims.py`
- Threshold SSOT: `agentic_core/L4_state/utils/memory/semantic_cache_manager.py`
