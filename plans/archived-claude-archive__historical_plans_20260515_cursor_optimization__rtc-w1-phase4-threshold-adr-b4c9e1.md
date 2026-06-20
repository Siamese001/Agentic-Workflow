---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\rtc-w1-phase4-threshold-adr-b4c9e1.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\rtc-w1-phase4-threshold-adr-b4c9e1.md'
source_sha256: 830dfb85be45edd7f1507e779c7b582cfd9c4fe1613124d898183b73faf6485e
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# W1 Phase 4 — Threshold ADR & Calibration Decision

Plan ID: `rtc-w1-phase4-threshold-adr-b4c9e1`
Status: APPROVED — execution in progress
Parent: `rtc-w1-phase3-blockers-close-d7a2f1.md` (commit `f676009c16`)
User approval: 2026-04-30 18:51Z

## Goal

Resolve `R1B_PRODUCTION_THRESHOLD_PROOF` without weakening safety. Produce an
ADR artifact that is PROPOSED_NOT_APPLIED — do not apply the threshold.

## Non-Goals (user-confirmed)

- No W2 integrated runtime.
- No W3 OTEL/replay.
- No W4 final certification / Merkle.
- No SemanticCacheManager threshold mutation.
- No config/YAML default mutation.
- No threshold override env changes.
- No forced green (R1B_PRODUCTION_THRESHOLD_PROOF stays CALIBRATION_GAP/PARTIAL).

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|---|---|---|---:|---|---|
| A | A.1 | Expand dataset to ~100 pairs across 6 classes | 8k | todo | test_calibration_dataset_expanded 16+ tests pass |
| B | B.1 | Threshold sweep probe (6 thresholds) | 10k | todo | threshold_sweep_results.json emitted with metrics table |
| C | C.1, C.2 | ADR generator + JSON + MD | 8k | todo | Both artifacts land with PROPOSED_NOT_APPLIED |
| D | D.1, D.2, D.3, D.4 | Composer gate + model-scope + tests + CI | 14k | todo | 212+70 tests pass; RTC-REQ-055 stays PARTIAL |

## Phase-Level Summary

| Phase ID | Title | Scope | Pain Points | Est. Tokens | Status |
|---|---|---|---|---:|---|
| A.1 | Dataset expansion | `data/certification/calibration_pairs.json` v2; rename `reference_contract_negative` → `policy_tenant_freshness_reuse_negative` and `lexical_overlap_negative` → `lexical_overlap_different_meaning_negative`; add 2 new positive classes; grow to 100 pairs | Schema-bump back-compat; keep existing pair ids stable | 8k | todo |
| B.1 | Threshold sweep probe | `tools/certification/evidence/probe_threshold_sweep.py`; sweep [0.95, 0.92, 0.90, 0.88, 0.85, 0.80]; emit per-threshold TP/FN/TN/FP/precision/recall/FPR/FNR + unsafe_fp_count + policy_preserved + lexical_preserved; recommend highest safe threshold | Needs BGE-M3 live (local only — CI continue-on-error) | 10k | todo |
| C.1 | ADR JSON | `artifacts/certification/semantic_cache_threshold_adr.json` with `owner_approval.status=PENDING_APPROVAL`, `implementation_status=PROPOSED_NOT_APPLIED`, `config_binding.applied=false` | Fail-closed on schema errors; deterministic from sweep evidence | 4k | todo |
| C.2 | ADR MD | `docs/adr/semantic_cache_threshold_recalibration.md` — human-readable, pulls values from JSON | JSON↔MD stay in sync; sign-off row blank | 4k | todo |
| D.1 | Composer ADR gate | Extend `scripts/compose_semantic_cache_subclaims.py` to read ADR; PASS only when APPROVED + APPLIED + threshold match + sweep FP=0 | `DRIFT_DETECTED` status not in `ALLOWED_STATUSES` — use PARTIAL + drift flag in notes | 4k | todo |
| D.2 | Model-scope field | Add `certification_scope` block to `semantic_cache_model_proof.json` (local_model_operational / ci_model_operational / final_model_certification_scope = LOCAL_ONLY\|CI_READY\|PRODUCTION_READY) | CI sentinel reads from `CI=true` env; new field must not break existing model-proof tests | 3k | todo |
| D.3 | Tests | 6 new test files (~70 tests): calibration_dataset_expanded, threshold_sweep_probe, threshold_adr_artifact, composer_adr_gate, model_scope_field, w1_phase4_invariants | Must preserve all 212 existing tests | 5k | todo |
| D.4 | CI wiring + final verification | Add W1.2i/j to workflow; bump timeout 180→300s; add 6 tests; upload new artifacts; run full chain | Workflow scope-clean — no unrelated edits | 2k | todo |

## Dataset Class Counts (Phase A target)

| Class | Target | Type | Expected label |
|---|---:|---|---|
| `paraphrase_positive` | 25 | measurable | POSITIVE |
| `abbreviation_definition_positive` | 15 | measurable | POSITIVE |
| `short_form_reminder_positive` | 10 | measurable | POSITIVE |
| `near_miss_negative` | 20 | measurable | NEGATIVE (unsafe_if_hit) |
| `lexical_overlap_different_meaning_negative` | 20 | measurable | NEGATIVE (efficiency_only; high overlap; unsafe_if_hit for some) |
| `policy_tenant_freshness_reuse_negative` | 10 | NOT measurable (contract anchor) | CONTRACT_NEGATIVE |
| **Total** | **100** | — | **50 pos / 50 neg** |

Safety-critical classes (FP must be 0): `near_miss_negative`, all `policy_tenant_freshness_reuse_negative`, and `lexical_overlap_different_meaning_negative` where overlap could produce a semantically dangerous hit.

## Threshold Sweep Values (Phase B)

`[0.95, 0.92, 0.90, 0.88, 0.85, 0.80]` — user-approved.

## Recommendation Rule (Phase B — user-approved)

```
recommended = max(t in sweep where
    fp == 0                              # no false positives at all
    AND unsafe_fp_count == 0             # no safety-critical FPs
    AND policy_freshness_preserved       # policy anchors stay MISS
    AND lexical_overlap_preserved        # lexical-overlap negatives stay MISS
    AND recall >= recall_at_0.95         # never regress positive recall
)
```

Tie-break: higher precision, then higher threshold. If no threshold satisfies
all four constraints → `recommended_threshold = null`, `status = NO_SAFE_THRESHOLD_FOUND`.

## ADR Schema (Phase C — user-approved fields)

```json
{
  "adr_id": "SEMCACHE-THRESH-001",
  "adr_version": "1.0",
  "created_utc": "...",
  "created_by": "w1_phase_4_threshold_calibration",
  "old_threshold": 0.95,
  "recommended_threshold": null | <float>,
  "model": {"identifier": "BAAI/bge-m3", "operation": "dense_cosine", "dim": 1024},
  "dataset": {"path": "data/certification/calibration_pairs.json", "sha256": "...", "n_pairs": 100, "n_positives": 50, "n_negatives": 50},
  "metrics_table": [ {threshold, tp, fn, tn, fp, precision, recall, fpr, fnr, f1, accuracy, unsafe_fp_count, policy_freshness_preserved, lexical_overlap_preserved} * 6 ],
  "safety_rationale": "...",
  "rollback_rule": "...",
  "owner_approval": {"status": "PENDING_APPROVAL", "approver": null, "approved_utc": null, "approval_evidence_ref": null},
  "implementation_status": "PROPOSED_NOT_APPLIED",
  "config_binding": {"target_key": "semantic_cache.similarity_threshold", "current_value": 0.95, "proposed_value": <float>, "applied": false}
}
```

## Composer ADR Gate (Phase D.1)

Status mapping for `R1B_PRODUCTION_THRESHOLD_PROOF`:

| ADR state | Configured threshold | Sweep FP at configured | Verdict |
|---|---|---|---|
| absent | — | — | CALIBRATION_GAP (legacy W1p3) |
| present, status=PENDING_APPROVAL | — | — | CALIBRATION_GAP |
| APPROVED, PROPOSED_NOT_APPLIED | — | — | PARTIAL (approved, not applied) |
| APPROVED, APPLIED, threshold != approved | any | any | PARTIAL (drift; note-flagged) |
| APPROVED, APPLIED, threshold == approved | — | FP>0 | PARTIAL (drift from sweep) |
| APPROVED, APPLIED, threshold == approved | — | FP=0 | PASS |

`ALLOWED_STATUSES` does not include `DRIFT_DETECTED`; drift surfaces as
PARTIAL with `notes` carrying the DRIFT flag.

## Model Scope Gate (Phase D.2)

New field in `semantic_cache_model_proof.json`:

```json
"certification_scope": {
  "local_model_operational": bool,      // from bge_m3_operational_proof.json
  "ci_model_operational": bool | "UNKNOWN",  // from env CI=true + probe result
  "final_model_certification_scope": "LOCAL_ONLY" | "CI_READY" | "PRODUCTION_READY" | "INSUFFICIENT"
}
```

Composer invariant: `R1B_APPROVED_MODEL_PROOF` cannot be PASS when
`final_model_certification_scope == LOCAL_ONLY`. Today this would pull
RTC-REQ-055 back from ACCEPTED even if threshold passes — but since
threshold stays PARTIAL/CALIBRATION_GAP regardless, RTC-REQ-055 stays
PARTIAL. The scope field is honest paper trail.

Wait: the user's condition says "Final acceptance cannot pass while
final_model_certification_scope = LOCAL_ONLY" — this is about the row
outcome, not the subclaim. We'll surface the scope in the overrides
caveat (not in the subclaim verdict itself) so `R1B_APPROVED_MODEL_PROOF`
stays PASS locally (reflecting that the model actually works), but the
final row-outcome reason-code includes the LOCAL_ONLY scope as a
blocker-adjacent note. Composer path: include scope in sidecar's
`notes` field for `R1B_APPROVED_MODEL_PROOF`, and the verifier already
reads `notes` for the caveat.

## Expected Final State After W1p4

| Artifact | Before | After |
|---|---|---|
| `R1B_APPROVED_MODEL_PROOF` | PASS | PASS (with scope=LOCAL_ONLY in notes) |
| `R1B_PRODUCTION_THRESHOLD_PROOF` | CALIBRATION_GAP | CALIBRATION_GAP (ADR pending approval) |
| `R1B_DENSE_SIMILARITY_COMPOSITION_PROOF` | PARTIAL | PARTIAL (unchanged) |
| RTC-REQ-055 row | PARTIAL | PARTIAL (unchanged — honest) |
| `semantic_cache_threshold_adr.json` | absent | present, PROPOSED_NOT_APPLIED |
| `docs/adr/semantic_cache_threshold_recalibration.md` | absent | present, sign-off row blank |
| Calibration dataset | 24 pairs | ~100 pairs |
| `threshold_sweep_results.json` | absent | present with 6 threshold rows |

## Anti-Cheat Invariants (all 5 preserved + 2 new W1p4)

1. No silent threshold lowering — ADR `applied=false`, no SSOT mutation
2. No silent fallback PASS — W1p2 preserved
3. No integrated-runtime claim — hardcoded NOT_APPLICABLE
4. UWG receipt when available — W1p2 preserved
5. Fixture/production distinction — W1p2 preserved
6. NEW — ADR gate: PASS only with APPROVED+APPLIED+threshold-match+FP=0
7. NEW — CI/local scope honesty: `final_model_certification_scope` surfaced

## Files Touched

**New (14)**:
- `.windsurf/plans/rtc-w1-phase4-threshold-adr-b4c9e1.md` (this file)
- `tools/certification/evidence/probe_threshold_sweep.py`
- `scripts/generate_threshold_adr.py`
- `artifacts/certification/threshold_sweep_results.json`
- `artifacts/certification/semantic_cache_threshold_adr.json`
- `docs/adr/semantic_cache_threshold_recalibration.md`
- `tests/runtime/test_calibration_dataset_expanded.py`
- `tests/runtime/test_threshold_sweep_probe.py`
- `tests/runtime/test_threshold_adr_artifact.py`
- `tests/runtime/test_composer_adr_gate.py`
- `tests/runtime/test_model_scope_field.py`
- `tests/runtime/test_w1_phase4_invariants.py`

**Modified (6)**:
- `data/certification/calibration_pairs.json` (v1 → v2, 100 pairs)
- `tools/certification/evidence/probe_threshold_calibration.py` (accept renamed skip class)
- `tools/certification/evidence/probe_semantic_cache_model.py` (add certification_scope)
- `tools/certification/evidence/probe_semantic_cache_threshold.py` (consume ADR)
- `scripts/compose_semantic_cache_subclaims.py` (ADR gate logic)
- `.github/workflows/runtime-certification.yml` (W1.2i/j + tests + artifacts)

## Execution Order

1. Plan file (this) ✓
2. Phase A — dataset v2 + compat update
3. Phase B — sweep probe + run locally
4. Phase C — ADR generator + both artifacts
5. Phase D.1 — composer gate
6. Phase D.2 — model-scope field
7. Phase D.3 — tests
8. Phase D.4 — CI wiring
9. Full verification chain
10. Commit + push (scope-clean)

## Lessons Borrowed From W1p3

- Bump test timeout for probes that embed many texts
- Mark CI steps `continue-on-error` when BGE-M3 absent in CI is expected
- Consume optional evidence defensively; composer tolerates absence
- Reference hashes change across regenerations — test via structural assertions, not content hashes
