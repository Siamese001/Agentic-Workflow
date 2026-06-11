---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\apps-lic-holdout-realtraffic-followup-b2d9f3__dup210.md'
original_relative_path: 'apps-lic-holdout-realtraffic-followup-b2d9f3__dup210.md'
source_sha256: c42b8472aec319b4b32eb6ee3d83f313969fe09c82cd9d50b3809de082ef444d
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# apps_lic Holdout & Real-Traffic Follow-up

**Slug:** `apps-lic-holdout-realtraffic-followup`
**ID:** `b2d9f3`
**Status:** Not Started
**Created:** 2026-05-04
**Owner:** Cascade
**Parent Plan:** `apps-lic-calibration-holdout-e8f1c4` (Completed)

**Goal:** Resolve the three remaining open items from `apps-lic-calibration-holdout-e8f1c4` that are blocked on external inputs (human-labeled holdout corpus, real outreach traffic, UWG spine sign-off). The tooling is already in place; this plan wires it to real data once blockers are lifted.

---

## Deferred Scope Items (sourced from parent plan `apps-lic-calibration-holdout-e8f1c4`)

| # | Item | Blocker | Priority | Notes |
|---|------|---------|----------|-------|
| RD1 | **Spearman calibration run against real holdout corpus** — `tools/calibration/lic_judge_holdout_ingest.py` and `ops_scripts/calibration/lic_judge_spearman_calibration.py` are complete. Calibration has not been run because no human-labeled holdout CSV exists yet. When corpus is available: ingest → run → confirm ρ ≥ 0.80 per judge → update `IS_CALIBRATED` docstring comments. | Human-labeled holdout CSV (data labeling task) | P1 | Tooling complete; unblocked the moment corpus lands |
| RD2 | **A/B variant engine real-traffic promotion** — `ABPromotionGate` and `REQUIRES_REAL_TRAFFIC=True` are in place. The gate correctly refuses to promote when any arm has n < 30. Needs real outreach traffic (n ≥ 30 per arm) flowing through `ABTrafficAccumulator` before a production promotion decision can be made. | Real outreach events per arm (traffic ramp) | P2 | Gate already enforces the constraint; no code change needed once traffic arrives |
| RD3 | **UWG real call-site spine integration for `BatchAdmissionReceipt`** — `CampaignBatchOrchestrator` accepts an optional `uwg_submit` callable injection (W3). The injection is not wired because `UnifiedWriteGateway` **does not exist anywhere in this codebase** (confirmed 2026-05-04 by full repo search). The L4 team must either provide the module location (external repo/branch) or define the interface so a local stub/implementation can be created. Injection shape is locked: `uwg_submit(receipt: BatchAdmissionReceipt) -> Any`. | `UnifiedWriteGateway` module missing — L4 team must provide location or define interface | P2 | Constructor injection point is ready; UWG itself is the blocker |

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|------|-----------|-------|-------------|--------|------------------|
| **W1** | RD1-P1 | Run Spearman calibration against real holdout corpus; confirm ρ ≥ 0.80 per judge | ~5k | Not Started — **BLOCKED: holdout corpus** | All 7 judges pass ρ ≥ 0.80; calibration report at `artifacts/calibration/lic_holdout_spearman_<date>.json` |
| **W2** | RD2-P1 | Validate A/B promotion gate with real traffic accumulator snapshot; emit first real `VERDICT_PROMOTE` or `VERDICT_UNDERPOWERED` decision | ~5k | Not Started — **BLOCKED: n ≥ 30 per arm** | Gate produces a real decision from live `ABTrafficAccumulator` data; result logged |
| **W3** | RD3-P1 | Wire `uwg_submit` at spine entrypoint; bind `CampaignBatchOrchestrator` to real `UnifiedWriteGateway.submit_batch_receipt()` | ~10k | Not Started — **BLOCKED: `UnifiedWriteGateway` not in codebase** | Spine integration test green; `BatchAdmissionReceipt` flows through UWG; governance tests pass |

**Total est tokens:** ~20k

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| RD1-P1 | Spearman calibration run | `tools/calibration/lic_judge_holdout_ingest.py` (run), `ops_scripts/calibration/lic_judge_spearman_calibration.py` (run), `artifacts/calibration/` (output) | Corpus format must match `REQUIRED_COLUMNS`; any judge below ρ 0.80 triggers a follow-up scoring audit | ~5k | Not Started |
| RD2-P1 | A/B real-traffic gate validation | `apps_lic/engines/ab_variant_engine.py` (no edit needed), `ABTrafficAccumulator` populated from live events | Traffic ramp timeline unknown; gate must remain in `VERDICT_UNDERPOWERED` until threshold reached | ~5k | Not Started |
| RD3-P1 | UWG spine wiring | `apps_lic/integrations/governed_lic_run.py` or `apps_lic/__main__.py` (UPDATE) | Must use constructor injection, not bypass; fail-soft on UWG exception must be preserved | ~10k | Not Started |

---

## Non-Goals

- No changes to judge scoring logic (heuristics are final for this plan).
- No changes to `ABTrafficAccumulator` or `ABPromotionGate` logic — gate is correct as-is.
- No new signal engines.
- No modifications to `agentic_core/` L0–L5.
- No holdout corpus authoring — data labeling is a human task.
- No provider API calls in any path.

---

## Files In Scope

```
# W1 — calibration run (offline scripts, no source edits)
tools/calibration/lic_judge_holdout_ingest.py          # RUN (no edit)
ops_scripts/calibration/lic_judge_spearman_calibration.py  # RUN (no edit)
artifacts/calibration/lic_holdout_corpus.jsonl         # OUTPUT: ingest
artifacts/calibration/lic_holdout_spearman_<date>.json # OUTPUT: calibration report

# W2 — A/B gate validation (no source edits; driven by live data)
apps_lic/engines/ab_variant_engine.py                  # NO EDIT — gate is ready

# W3 — UWG spine wiring
apps_lic/integrations/governed_lic_run.py              # UPDATE: inject uwg_submit
# OR
apps_lic/__main__.py                                   # UPDATE: inject uwg_submit
```

---

## Dependencies and Blockers

| Item | Blocker | Resolution Path |
|------|---------|-----------------|
| RD1 — Spearman calibration run | Human-labeled holdout CSV not yet available | Data labeling task; unblocked immediately on corpus delivery |
| RD2 — A/B real traffic | No real outreach traffic flowing through accumulator yet | Deploy with REQUIRES_REAL_TRAFFIC=True; gate surfaces gap automatically |
| RD3 — UWG spine wiring | `UnifiedWriteGateway` module absent from codebase (confirmed 2026-05-04) | L4 team must provide module location (external repo/branch) OR define interface for local implementation; injection shape locked: `uwg_submit(receipt: BatchAdmissionReceipt) -> Any` |

---

## Hard Invariants (inherited)

1. All engines remain decision-only — no provider calls, no durable state writes.
2. Signal engine wiring (DS2/W3) is non-blocking — a None/disabled result must not gate BriefingReady.
3. Calibration scripts (RD1) run offline only — never called from the hot path.
4. `uwg_submit` injection (RD3) must remain fail-soft — exception must not abort batch dispatch.
5. `ABPromotionGate` verdict is advisory — it never blocks `ABVariantEngine.assign()`.

---

## Gap Register

| Gap | Severity | Mitigation |
|-----|----------|------------|
| Holdout corpus delivery date unknown | HIGH | W1 blocked indefinitely until corpus delivered; no code change needed |
| Traffic ramp timeline for n ≥ 30 arms unknown | MEDIUM | REQUIRES_REAL_TRAFFIC flag surfaces gap; promotion gate refuses silently |
| UWG batch interface not yet signed off | MEDIUM | Confirm with L4 before W3; spike test interface before committing |

---

## Acceptance Criteria Summary

- `lic_judge_spearman_calibration.py` exits 0 with all 7 judges at ρ ≥ 0.80 on real corpus.
- `ABPromotionGate` emits `VERDICT_PROMOTE` for at least one experiment with real-traffic n ≥ 30 per arm.
- `CampaignBatchOrchestrator` `uwg_submit` injection is wired at the spine entrypoint; `BatchAdmissionReceipt` flows through a real `UnifiedWriteGateway` call.
- Full governance suite (W1–W5 sentinel tests, 184 tests) remains green throughout.

---

## PLAN_CREATED: apps-lic-holdout-realtraffic-followup-b2d9f3
