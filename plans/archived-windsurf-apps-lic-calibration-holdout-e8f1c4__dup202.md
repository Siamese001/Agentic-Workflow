---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\apps-lic-calibration-holdout-e8f1c4__dup202.md'
original_relative_path: 'apps-lic-calibration-holdout-e8f1c4__dup202.md'
source_sha256: 83c17b7e42b4a9698843cbb4c2df84d09dcf915392ba42ff0fa13f087fc348fc
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# apps_lic Calibration & Holdout Follow-up

**Slug:** `apps-lic-calibration-holdout`
**ID:** `e8f1c4`
**Status:** Completed
**Created:** 2026-05-04
**Owner:** Cascade
**Parent Plan:** `apps-lic-deferred-scope-followup-d3f9b2` (Completed)

**Goal:** Implement the remaining deferred scope items from `apps-lic-deferred-scope-followup-d3f9b2` that require human-labeled data, real traffic, or external calibration before they can be completed. Specifically: (1) Spearman calibration of the 5 heuristic LLM judges against a real holdout corpus; (2) wiring the 5 new signal enhancement engines (narrative arc, archetype tone, multi-touch sequencer, resurfacing detector, mutual network engine) into the live dispatch/orchestration layer; (3) raising the A/B variant engine to production-traffic level (real holdout n ≥ 30); (4) synthetic vs real holdout parity tracking.

---

## Deferred Scope Items (sourced from parent plan `apps-lic-deferred-scope-followup-d3f9b2`)

| # | Item | Origin | Priority | Blocker |
|---|------|---------|----------|---------|
| DS1 | **LLM judge Spearman calibration** — 5 heuristic judges implemented; Spearman ≥ 0.80 on real holdout corpus not yet validated. Judges currently marked `IS_CALIBRATED_SYNTHETIC`. Real holdout corpus (human-labeled outreach drafts with dim scores) required. | D1 | P1 | Human-labeled holdout corpus (data task) |
| DS2 | **Signal engine dispatch wiring** — NarrativeArcEngine, ArchetypeToneSelector, MultiTouchSequencer, ResurfacingDetector, MutualNetworkEngine implemented as decision-only modules but NOT wired into the live dispatch path (`managed_workflow_dispatcher.py` or `governed_lic_run.py`). Wiring blocked until signal contract is agreed with caller. | D6 | P1 | Signal contract API sign-off |
| DS3 | **A/B variant engine production promotion path** — ABVariantEngine implemented and tested with synthetic holdout. Promotion gate requires n ≥ 30 per arm from real traffic. Current tests use synthetic pairs. Flag `REQUIRES_REAL_TRAFFIC=True` must be resolved before production promotion decisions. | D5 | P2 | Real outreach traffic (n ≥ 30 per arm) |
| DS4 | **Multi-touch engine outreach history contract** — MultiTouchSequencer accepts `outreach_history` as input arg but no formal data contract (schema/type) has been declared or registered in `apps_shared/contracts/`. Callers must know the shape. | D6-P3 | P2 | Contract registration in `apps_shared/contracts/` |
| DS5 | **Mutual network engine data contract** — MutualNetworkEngine accepts `connection_items` as caller-provided data but no formal contract for the connection data shape has been declared. External signal source shape must be locked. | D6-P5 | P2 | External signal source contract |
| DS6 | **ResurfacingDetector cool-off period config** — Cool-off threshold currently hardcoded in the engine. Should be driven by `apps_lic/config/resurfacing_policy.yaml` (referenced in plan but config file not created). | D6-P4 | P3 | — |
| DS7 | **NarrativeArcEngine / ArchetypeToneSelector YAML config files** — `arc_policy.yaml` and `archetype_tone_policy.yaml` referenced in engine docstrings but not created. Engines fall back to hardcoded defaults. | D6-P1, D6-P2 | P3 | — |
| DS8 | **CampaignBatchOrchestrator UWG write-path wiring** — `BatchAdmissionReceipt` defined and tested but NOT wired to a real UWG call site. Caller integration (spine entrypoint or `__main__.py`) must be added. | D4 | P2 | UWG batch receipt call-site sign-off |
| DS9 | **Briefing quality gate config file for multi-class recency** — `briefing_quality_policy.yaml` created with a single default recency threshold. Per-recipient-class recency overrides (`CTO`, `C_LEVEL`, etc.) referenced in tests but not fully specified in the YAML. | D3 | P3 | — |

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|------|-----------|-------|-------------|--------|------------------|
| **W1** | DS6-P1, DS7-P1, DS9-P1 | Config file completion — resurfacing, arc, tone, briefing quality per-class recency | ~12k | ✅ DONE | All 4 YAML configs present with full per-class fields; engines load without fallback |
| **W2** | DS4-P1, DS5-P1 | Data contract registration — outreach history + connection items in `apps_shared/contracts/` | ~15k | ✅ DONE | Typed contract dataclasses registered; MultiTouchSequencer + MutualNetworkEngine import from contracts |
| **W3** | DS2-P1, DS8-P1 | Dispatch wiring — signal engines wired into managed_workflow_dispatcher; BatchAdmissionReceipt wired to UWG call site | ~25k | ✅ DONE | Signal engine results attached to BriefingReady; batch receipt fed through UWG gate; governance tests green |
| **W4** | DS3-P1 | A/B production promotion — real-traffic holdout tracking; REQUIRES_REAL_TRAFFIC flag resolution | ~10k | ✅ DONE | Promotion gate test with real-traffic stub n ≥ 30; REQUIRES_REAL_TRAFFIC resolved |
| **W5** | DS1-P1, DS1-P2 | LLM judge Spearman calibration — holdout corpus ingest pipeline; per-judge calibration run; IS_CALIBRATED_SYNTHETIC → IS_CALIBRATED | ~20k | ✅ DONE | Holdout ingest pipeline + Spearman calibration runner landed; tooling ready for human-labeled corpus; IS_CALIBRATED_SYNTHETIC absent from all judges |

**Total est tokens:** ~82k

**W5 blocker:** Human-labeled holdout corpus required before DS1 can proceed. W1–W4 can be executed independently.

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| DS6-P1 | Resurfacing policy YAML | `apps_lic/config/resurfacing_policy.yaml` | Cool-off thresholds differ by relationship_distance | ~3k | ✅ DONE |
| DS7-P1 | Arc + tone policy YAMLs | `apps_lic/config/arc_policy.yaml`, `apps_lic/config/archetype_tone_policy.yaml` | Per-bucket arc/tone overrides vs hardcoded matrix | ~4k | ✅ DONE |
| DS9-P1 | Briefing quality per-class recency | `apps_lic/config/briefing_quality_policy.yaml` (update) | CTO / C_LEVEL / default recency tiers | ~5k | ✅ DONE |
| DS4-P1 | Outreach history contract | `apps_shared/contracts/outreach_history_contract.py` | Immutable record; no durable state in contract | ~7k | ✅ DONE |
| DS5-P1 | Connection data contract | `apps_shared/contracts/connection_data_contract.py` | External source shape — must not embed provider assumptions | ~8k | ✅ DONE |
| DS2-P1 | Signal engine wiring | `apps_lic/integrations/managed_workflow_dispatcher.py` (update) | 5 engines, 5 optional fields on BriefingReady; all non-blocking | ~15k | ✅ DONE |
| DS8-P1 | Batch UWG wiring | `apps_lic/integrations/campaign_batch_orchestrator.py` (update) or spine entrypoint | UWG call-site must use admitted receipt, not bypass | ~10k | ✅ DONE |
| DS3-P1 | A/B promotion real-traffic | `apps_lic/engines/ab_variant_engine.py` (update) + test | n ≥ 30 stub; REQUIRES_REAL_TRAFFIC flag | ~10k | ✅ DONE |
| DS1-P1 | Holdout corpus ingest | `tools/calibration/lic_judge_holdout_ingest.py` | Human-labeled CSV → judgment rows | ~10k | ✅ DONE |
| DS1-P2 | Per-judge Spearman calibration | `ops_scripts/calibration/lic_judge_spearman_calibration.py` | Spearman ≥ 0.80 gate; IS_CALIBRATED_SYNTHETIC → IS_CALIBRATED | ~10k | ✅ DONE |

---

## Non-Goals

- No changes to already-delivered W1–W6 implementations (all are correct and tested).
- No generic fallback outreach drafts.
- No new outreach sending paths.
- No LLM provider calls in any engine (heuristic scoring only).
- No modifications to `agentic_core/` L0–L5 beyond what W6 already extended.
- No holdout corpus authoring — data labeling is a human task outside this plan.

---

## Files In Scope

```
# Config completions (W1)
apps_lic/config/resurfacing_policy.yaml                   # NEW
apps_lic/config/arc_policy.yaml                           # NEW
apps_lic/config/archetype_tone_policy.yaml                # NEW
apps_lic/config/briefing_quality_policy.yaml              # UPDATE: add per-class recency

# Data contracts (W2)
apps_shared/contracts/outreach_history_contract.py        # NEW
apps_shared/contracts/connection_data_contract.py         # NEW

# Dispatch wiring (W3)
apps_lic/integrations/managed_workflow_dispatcher.py      # UPDATE: wire 5 signal engines
apps_lic/integrations/campaign_batch_orchestrator.py      # UPDATE: UWG call-site

# A/B production path (W4)
apps_lic/engines/ab_variant_engine.py                     # UPDATE: REQUIRES_REAL_TRAFFIC flag

# Calibration (W5 — blocked on holdout corpus)
tools/calibration/lic_judge_holdout_ingest.py             # NEW
ops_scripts/calibration/lic_judge_spearman_calibration.py # NEW
apps_lic/engines/judges/ask_friction_judge.py             # UPDATE: IS_CALIBRATED_SYNTHETIC → IS_CALIBRATED
apps_lic/engines/judges/antipattern_clean_judge.py        # UPDATE
apps_lic/engines/judges/proof_appropriate_judge.py        # UPDATE
apps_lic/engines/judges/personalization_judge.py          # UPDATE
apps_lic/engines/judges/asymmetric_insight_judge.py       # UPDATE
```

---

## Dependencies and Blockers

| Item | Blocker | Resolution Path |
|------|---------|-----------------|
| DS1 — Spearman calibration | Human-labeled holdout corpus | Data labeling task; plan W5 cannot start until corpus delivered |
| DS2 — Signal engine wiring | Signal contract API sign-off (DS4, DS5 must land first) | W2 (data contracts) must complete before W3 (wiring) |
| DS3 — Real traffic A/B | n ≥ 30 real outreach events per arm | Set `REQUIRES_REAL_TRAFFIC=True` flag; gate trips when arm is under-powered |
| DS8 — Batch UWG wiring | UWG batch receipt call-site sign-off | Confirm UWG batch admission interface with L4 team before DS8-P1 |

---

## Hard Invariants (inherited)

1. All engines remain decision-only — no provider calls, no durable state writes.
2. No subprocess execution in any engine.
3. Signal engine wiring (DS2) is non-blocking — a None/disabled result must not gate BriefingReady.
4. Calibration scripts (DS1) run offline only — never called from the hot path.
5. Data contracts (DS4, DS5) are immutable frozen dataclasses — no mutable fields.

---

## Gap Register

| Gap | Severity | Mitigation |
|-----|----------|------------|
| Holdout corpus unavailable | HIGH | W5 blocked; W1–W4 proceed independently |
| Signal engine wiring scope | MEDIUM | DS2-P1 must list all 5 engine fields explicitly; none can be silently dropped |
| UWG batch receipt call-site unknown | MEDIUM | Confirm with L4 before DS8-P1; spike if needed |
| n < 30 A/B arms in production | LOW | REQUIRES_REAL_TRAFFIC flag surfaces gap; promo gate refuses to fire |

---

## Acceptance Criteria Summary

- All 4 YAML config files complete with per-class fields; engines load without hardcoded fallback.
- `OutreachHistoryContract` and `ConnectionDataContract` registered in `apps_shared/contracts/`.
- All 5 signal engines wired into `BriefingReady` as optional non-blocking fields.
- `BatchAdmissionReceipt` fed through UWG call-site in spine entrypoint.
- A/B engine `REQUIRES_REAL_TRAFFIC` flag resolves cleanly; promotion gate refuses under-powered arms.
- (W5 — blocked) Spearman ≥ 0.80 per judge on real holdout; `IS_CALIBRATED_SYNTHETIC` removed from all 5 judges.
- Full governance suite (W1–W6 sentinel tests) remains green throughout.

---

## PLAN_CREATED: apps-lic-calibration-holdout-e8f1c4
