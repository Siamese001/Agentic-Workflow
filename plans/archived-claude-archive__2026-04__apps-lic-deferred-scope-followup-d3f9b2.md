---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-04\\apps-lic-deferred-scope-followup-d3f9b2.md'
original_relative_path: '_archive\\2026-04\\apps-lic-deferred-scope-followup-d3f9b2.md'
source_sha256: 4ea4abeb72fc2b6e29015113640fa08a6a7a0b07951fc4cf22686fb6519d1fdd
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# apps_lic Deferred Scope Follow-up

**Slug:** `apps-lic-deferred-scope-followup`
**ID:** `d3f9b2`
**Status:** Not Started
**Created:** 2026-05-04
**Owner:** Cascade
**Parent Plan:** `apps-lic-canonical-spine-wireup-e7c2a5` (Completed)

**Goal:** Implement the six deferred scope items captured during the `apps-lic-canonical-spine-wireup` plan (W1–W8). Each item was descoped to maintain a bounded delivery of the canonical spine wireup. This plan delivers the remaining enhancements — HITL freeze/review, production quality gating, multi-recipient batching, A/B variant testing, P2+P3 signal enhancements, and real LLM-judge implementations.

---

## Deferred Scope Items (sourced from parent plan `## Deferred Scope`)

| # | Item | Origin | Priority | Dependency |
|---|------|---------|----------|------------|
| D1 | **Real LLM-judge implementations** for Exit rubric dims (`ask_friction_score`, `antipattern_clean`, `proof_appropriate_for_recipient`, `personalization_mode_appropriate`, `asymmetric_insight_present`) — stubs exist per `apps-eval-harness-deferred-e4a1b7` | W8 | P1 | Human-labeled holdout corpus required |
| D2 | **HITL freeze/review/re-clearance mechanism** — design approved in W8 (exit rubric references HITL path); implementation deferred | W8 | P1 | ADR-023 HITL contract; compliance review |
| D3 | **Production apps_research briefing quality validation** — research quality gates (coverage, recency, source diversity) out of scope for spine wireup | W3 | P2 | apps_research public API extension |
| D4 | **Multi-recipient campaign batching** — single-recipient only in parent plan; batch orchestration, deduplication, rate control all deferred | W2 | P2 | L3 campaign orchestrator; UWG batch admission |
| D5 | **A/B test framework for message variants** — L6 shadow eval scaffolding; holdout assignment; variant scoring; promotion gate | W8 | P3 | L6 regret accounting; promotion gate (ADR-050) |
| D6 | **P2+P3 signal enhancements** (narrative arc, archetype tone, multi-touch sequencing, resurfacing logic, mutual network signals) — tracked in `apps-lic-signal-enhancements-p2p3-f4b8d1` | W6–W7 | P2 | Sender credibility engine (W7 complete); asymmetric insight engine (W7 complete) |

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|------|-----------|-------|-------------|--------|------------------|
| **W1** | D2-P1, D2-P2 | HITL freeze/review/re-clearance mechanism — design + implementation | ~25k | Not Started | `HITLFreezePolicy` evaluates exit rubric low-confidence dims; re-clearance path emits new X3 disposition; tests cover freeze/approve/reject/return-to-L1 |
| **W2** | D1-P1, D1-P2, D1-P3, D1-P4, D1-P5 | Real LLM-judge implementations for 5 Exit rubric dims | ~35k | Not Started | Each dim judge: Spearman ≥ 0.80 on holdout; IS_STUB removed; grade() returns float 0–1; NO_UNIMPL_JUDGES gate green |
| **W3** | D3-P1, D3-P2 | Production briefing quality validation gates | ~20k | Not Started | `BriefingQualityGate` checks coverage / recency / source diversity; low-quality briefing → R5 `APPS_RESEARCH_WEAK_SUPPORT` or `APPS_RESEARCH_STALE` |
| **W4** | D6-P1, D6-P2, D6-P3, D6-P4, D6-P5 | P2+P3 signal enhancements | ~30k | Not Started | Narrative arc engine; archetype tone selector; multi-touch sequencer; resurfacing detector; mutual network signal extractor — all decision-only, config-gated |
| **W5** | D4-P1, D4-P2, D4-P3 | Multi-recipient campaign batching | ~25k | Not Started | `CampaignBatchOrchestrator` dispatches N single-recipient runs; deduplication via manifest_hash; rate control config; UWG batch admission receipt |
| **W6** | D5-P1, D5-P2, D5-P3 | A/B test framework for message variants | ~20k | Not Started | Holdout assignment in L6; variant scoring via shadow eval; promotion gate (Wilson CI ≥ 0.60, n ≥ 30); regret ledger records per-variant |

**Total est tokens:** ~155k

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| D2-P1 | HITL policy design | `apps_lic/integrations/hitl_freeze_policy.py`, `apps_lic/config/hitl_policy.yaml` | ADR-023 boundary — HITL admission vs compliance review | ~12k | Not Started |
| D2-P2 | HITL re-clearance path | `apps_lic/integrations/governed_lic_run.py`, `tests/governance/test_apps_lic_hitl_freeze.py` | Re-clearance must emit new X3; must not mutate current-run state | ~13k | Not Started |
| D1-P1 | `ask_friction_score` judge | `apps_lic/engines/judges/ask_friction_judge.py` | Holdout corpus needed; score band calibration | ~7k | Not Started |
| D1-P2 | `antipattern_clean` judge | `apps_lic/engines/judges/antipattern_clean_judge.py` | LLM judge vs rule-based overlap — avoid double-counting | ~7k | Not Started |
| D1-P3 | `proof_appropriate_for_recipient` judge | `apps_lic/engines/judges/proof_appropriate_judge.py` | Contextual — recipient_class must be passed to judge | ~7k | Not Started |
| D1-P4 | `personalization_mode_appropriate` judge | `apps_lic/engines/judges/personalization_judge.py` | Cold vs warm calibration differs significantly | ~7k | Not Started |
| D1-P5 | `asymmetric_insight_present` judge | `apps_lic/engines/judges/asymmetric_insight_judge.py` | Config-gated — must honor outreach_mode bypass | ~7k | Not Started |
| D3-P1 | Briefing quality gate design | `apps_lic/integrations/briefing_quality_gate.py`, schema extension | apps_research API may not expose all quality signals | ~10k | Not Started |
| D3-P2 | Briefing quality gate wiring | `apps_lic/integrations/managed_workflow_dispatcher.py` (update) | Must not block R4 when quality is marginal — policy-gated | ~10k | Not Started |
| D6-P1 | Narrative arc engine | `apps_lic/engines/narrative_arc_engine.py` | Recipient class + relationship distance drive arc selection | ~6k | Not Started |
| D6-P2 | Archetype tone selector | `apps_lic/engines/archetype_tone_selector.py` | Overlap with personalization_mode — must be additive not replacing | ~6k | Not Started |
| D6-P3 | Multi-touch sequencer | `apps_lic/engines/multi_touch_sequencer.py` | Requires prior outreach history reference; no durable state reads in engine | ~6k | Not Started |
| D6-P4 | Resurfacing detector | `apps_lic/engines/resurfacing_detector.py` | Cold vs warm re-engagement signals differ | ~6k | Not Started |
| D6-P5 | Mutual network signal extractor | `apps_lic/engines/mutual_network_engine.py` | External signal source — data contract must be declared, not embedded | ~6k | Not Started |
| D4-P1 | Campaign batch orchestrator | `apps_lic/integrations/campaign_batch_orchestrator.py` | Rate control config; deduplication by manifest_hash | ~8k | Not Started |
| D4-P2 | UWG batch admission | `apps_lic/integrations/campaign_batch_orchestrator.py` (write path) | UWG batch receipt shape; partial-failure handling | ~8k | Not Started |
| D4-P3 | Batch governance tests | `tests/governance/test_apps_lic_campaign_batch.py` | Deduplication + rate control + partial-fail sentinel tests | ~9k | Not Started |
| D5-P1 | Holdout assignment + variant scoring | `apps_lic/engines/ab_variant_engine.py` | L6 shadow eval integration — non-blocking | ~7k | Not Started |
| D5-P2 | Promotion gate wiring | `agentic_core/L6_observability/promotion_gates.py` (extension) | Wilson CI n ≥ 30 requirement — may need synthetic holdout for tests | ~6k | Not Started |
| D5-P3 | Regret ledger per-variant recording | `agentic_core/L6_observability/regret_accounting.py` (extension) | Per-variant reward attribution; `by_layer_json` non-empty requirement | ~7k | Not Started |

---

## Non-Goals

- No changes to the canonical spine wireup (W1–W8) already delivered in parent plan.
- No changes to `apps_research/` internals — integrate only via public API.
- No message sending. `apps_lic` generates drafts or send-ready candidates only.
- No generic fallback outreach draft in any new path.
- No real holdout corpus authoring — that is a data task, not a code task.
- No changes to `agentic_core/` L0–L5 internals beyond the bounded extensions named above.

---

## Files In Scope

```
# HITL freeze/review/re-clearance (D2)
apps_lic/integrations/hitl_freeze_policy.py              # NEW
apps_lic/config/hitl_policy.yaml                         # NEW
apps_lic/integrations/governed_lic_run.py                # UPDATE: wire HITL re-clearance path
tests/governance/test_apps_lic_hitl_freeze.py            # NEW

# Real LLM-judge implementations (D1)
apps_lic/engines/judges/ask_friction_judge.py            # UPDATE: remove IS_STUB
apps_lic/engines/judges/antipattern_clean_judge.py       # UPDATE: remove IS_STUB
apps_lic/engines/judges/proof_appropriate_judge.py       # UPDATE: remove IS_STUB
apps_lic/engines/judges/personalization_judge.py         # UPDATE: remove IS_STUB
apps_lic/engines/judges/asymmetric_insight_judge.py      # UPDATE: remove IS_STUB

# Briefing quality validation (D3)
apps_lic/integrations/briefing_quality_gate.py           # NEW
apps_lic/integrations/managed_workflow_dispatcher.py     # UPDATE: wire quality gate

# P2+P3 signal enhancements (D6)
apps_lic/engines/narrative_arc_engine.py                 # NEW
apps_lic/engines/archetype_tone_selector.py              # NEW
apps_lic/engines/multi_touch_sequencer.py                # NEW
apps_lic/engines/resurfacing_detector.py                 # NEW
apps_lic/engines/mutual_network_engine.py                # NEW

# Multi-recipient batching (D4)
apps_lic/integrations/campaign_batch_orchestrator.py     # NEW
tests/governance/test_apps_lic_campaign_batch.py         # NEW

# A/B test framework (D5)
apps_lic/engines/ab_variant_engine.py                    # NEW
agentic_core/L6_observability/promotion_gates.py         # UPDATE: apps_lic variant gate
agentic_core/L6_observability/regret_accounting.py       # UPDATE: per-variant recording
```

---

## Dependencies and Blockers

| Item | Blocker | Resolution Path |
|------|---------|-----------------|
| D1 — Real LLM judges | Human-labeled holdout corpus for Spearman calibration | Data task; use synthetic holdout for initial gate, upgrade when real data available |
| D2 — HITL freeze | ADR-023 compliance review | Read ADR-023 + `.windsurf/reminders/2026-04-28-adr-023-acceptance.md` before W1 |
| D3 — Quality gate | apps_research API must expose quality signals | Discovery phase at D3-P1 start; extend API if missing as bounded public contract |
| D4 — Batch | UWG batch receipt shape | Check `agentic_core/L4_state/` UWG contract before D4-P2 |
| D5 — A/B | `by_layer_json` non-empty invariant in regret ledger | Confirmed by `closed-loop-router-enforcement.md` §L6/regret |
| D6 — Multi-touch | Prior outreach history reference | Engine reads a declared data contract reference only — no durable state reads |

---

## Hard Invariants (inherited from parent plan)

1. All new engines are decision-only, compose-only — no provider calls, no durable state writes.
2. No subprocess execution in any engine.
3. `send_now` / `auto_send` / `connector_send` remain blocked at schema and Exit.
4. COMMIT_REQUEST never for raw outreach drafts.
5. Durable writes only through `Exit → UWG → L4`.
6. L6 shadow eval (D5) is non-blocking — never gates the current run.

---

## Gap Register

| Gap | Severity | Mitigation |
|-----|----------|------------|
| LLM judge calibration without holdout corpus | HIGH | Synthetic holdout with known scores for initial Spearman gate; flag as `IS_CALIBRATED_SYNTHETIC=True` |
| HITL re-clearance state machine complexity | MEDIUM | Strict state machine: `frozen → under_review → cleared / rejected / returned_to_l1`; no free-form transitions |
| Multi-touch engine needs prior outreach history | MEDIUM | Declare data contract reference; engine receives history as input arg — never queries state directly |
| A/B promotion gate needs n ≥ 30 | LOW | Synthetic variant pairs sufficient for gate tests; flag production path as `REQUIRES_REAL_TRAFFIC=True` |

---

## Acceptance Criteria Summary

- All 5 LLM-judge stubs replaced with real implementations (`IS_STUB` removed); `NO_UNIMPL_JUDGES` gate green.
- HITL freeze policy evaluates exit rubric dims; re-clearance path emits new X3 disposition.
- Briefing quality gate fires on low-coverage / stale briefings; routes to correct R5 code.
- P2+P3 signal engines all decision-only, config-gated, no provider calls.
- Campaign batch orchestrator dispatches N single-recipient runs with deduplication and rate control.
- A/B variant engine assigns holdout; promotion gate uses Wilson CI; regret ledger records per-variant.
- Full governance suite (W1–W8 sentinel tests) remains green throughout.
- No regressions in `tests/governance/test_apps_lic_w1_*` through `test_apps_lic_w8_*`.

---

## PLAN_CREATED: apps-lic-deferred-scope-followup-d3f9b2
