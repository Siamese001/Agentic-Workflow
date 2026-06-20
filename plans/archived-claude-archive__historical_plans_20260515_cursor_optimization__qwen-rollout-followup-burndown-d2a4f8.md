---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\qwen-rollout-followup-burndown-d2a4f8.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\qwen-rollout-followup-burndown-d2a4f8.md'
source_sha256: 7c64c2740110480820f3934c8077d0be4e0fd31135120ad0448751d28120d7cf
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Qwen-Rollout Follow-Up Burndown — d2a4f8

> Successor plan to `apps-eval-qwen32b-rollout-b7c4d9` (Completed 2026-05-02).
> Captures every deferred / open-scope item from the predecessor plan's
> "Deferred + Open Scope Register" and routes each to the correct disposition:
> burnable-now, data-gated (4-6 wks), trigger-conditioned, or external CI.

## Status

- **Plan**: `qwen-rollout-followup-burndown-d2a4f8`
- **Created**: 2026-05-02
- **Owner**: Cascade
- **Predecessor**: `apps-eval-qwen32b-rollout-b7c4d9`
- **Status**: Completed (2026-05-03)

## Supersedes / Related

- Inherits the Deferred + Open Scope Register from
  `.windsurf/plans/apps-eval-qwen32b-rollout-b7c4d9.md`
  (also captured in the Notion plan page body of the predecessor).

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | P1.1 | **Burnable now → DONE** — `apps_lic.engines.generation_engine.GenerationEngine.execute()` (the actual production HOP5 substrate entry point — legacy `HOP5GenerationAgent` is no longer in the runtime path) wired Qwen-first via sync `openai.OpenAI` cascade, falls through to original deterministic scaffold on any failure | ~2k | QwenLLMClient adapter live (verified W4 P4.1 of predecessor); `apps_lic` composition root identified as `generation_engine.py` not the legacy reasoning-folder agent | done | Live: real Qwen-32B produced "I noticed your recent achievements in scaling your fintech operations..." for a B2B outreach prompt; `generator=qwen_local` confirmed; deterministic scaffold fallback preserved on any cascade failure; W1 determinism floor 5/5 still green (5 passed, 0.36s) |
| W2 | P2.1–P2.6 | **Data-gated (passive)** — six items waiting on ≥30 paired runs per app from `judge_calibration.py` weekly Markdown reports | ~0 | Production traffic accumulating; harness running weekly | passive | First per-app eligibility report at ~4-6 wks post-rollout; until then, this wave's success is "harness keeps generating reports without watchdog firing" |
| W3 | P3.1–P3.2 | **Trigger-conditioned (passive)** — frontier second-judge pairing at HOP6 + HOP3b/HOP3c reopen if proposal sections grow free-text | ~0 | Wilson-CI agreement metric tracked weekly; section taxonomy stable | passive | No premature firing; if either trigger fires, this wave reopens as a new T2/T3 plan |
| W4 | P4.1 | **Config-only deferral** — `apps_rg` ensemble N=3 → N=5 — single PR after W2 latency data shows p95 fits SLO at N=5 | ~0.5k | Predecessor W5 P5.2 finding | gated on W2 | Single config-line edit in `apps_rg/config/agent_specs.json` + smoke test; no behavioral change beyond candidate count |
| W5 | P5.1 | **Out-of-scope (separate plan)** — apps_underwriting_ai activation | ~0 | App is genuinely a stub | deferred | When activated, spawn a NEW plan with the W4-apps_lic pattern as anchor (preconditions captured in predecessor §"Wave 8 findings") |
| W6 | P6.1 | **External CI** — RTC-REQ / mutation-rejection / OTel coverage gates | ~0 | Next CI run | external | Verified by next CI pipeline run; no rollout-side action |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| P1.1 | HOP5 composition-root wiring | `apps_lic/engines/generation_engine.py` (substrate-pipeline entry point per `apps_lic/config/hop_pipeline.py:_STAGE_SPECS[4]`); legacy `HOP5GenerationAgent` in reasoning folder is NOT in runtime path | Identification: substrate uses `GenerationEngine`, not the legacy agent. Sync wiring chosen over async-bridging to match W2/W3/W5 cascade pattern (sync `openai.OpenAI` against `VLLM_BASE_URL`). | 2k | done |
| P2.1 | apps_research 50-run agreement test (W3 P3.4 of predecessor) | none — passive monitoring of `docs/reports/calibration/judge/<YYYY-Www>.md` | Eligibility ~4-6 wks; cannot fire prematurely | 0 | passive |
| P2.2 | apps_lic ≥30-row promotion gate for HOP6 (W4 P4.5) | passive | Wilson-CI thresholds: wilson_lower≥0.60, z≥1.96, uplift>0, n_each_arm≥30 | 0 | passive |
| P2.3 | apps_rg 100-resume regression composite ≥0.85 (W5 P5.6) | passive | ATS unchanged + runtime ±20% baseline checks bundle in same row | 0 | passive |
| P2.4 | apps_rg latency p50/p95 vs cloud Anthropic baseline (W5 P5.5) | passive | Captured by harness's per-app latency stats | 0 | passive |
| P2.5 | apps_rfp section-classification audit + cost-per-proposal (W6 P6.4) | passive | Reopens P3.2 if sections grow free-text | 0 | passive |
| P2.6 | Six-site §29 paired-emission promotion verdicts (W9 P9.4) | passive | Per-app `promote/hold` cannot fire until n≥30 paired runs | 0 | passive |
| P3.1 | Frontier-API second-judge pairing at HOP6 (W4 P4.4) | passive trigger | Trigger: Wilson-CI on per-archetype agreement Qwen-vs-human < 0.85 over 4-week rolling window | 0 | passive |
| P3.2 | apps_rfp HOP3b/HOP3c reopen on free-text sections (W6 P6.2/P6.3) | passive trigger | Trigger: any `SectionType` value graduates from templated assembly to generated narrative | 0 | passive |
| P4.1 | apps_rg ensemble N=3 → N=5 (W5 P5.2) | `apps_rg/config/agent_specs.json` + `_ensemble_runner` defaults | Gated on W2 latency data (p95 fits SLO at N=5) | 0.5k | gated |
| P5.1 | apps_underwriting_ai activation (W8 P8.2/P8.3) | none in this plan; spawns separate plan | Out-of-scope by design; preconditions in predecessor §"Wave 8 findings" | 0 | deferred |
| P6.1 | RTC-REQ / mutation-rejection / OTel coverage (W10 P10.4) | none — external CI | Next CI run | 0 | external |

## ADG_HOTSPOT_REPORT

This plan's only burnable item (P1.1) is a single composition-root edit. ADG hotspot analysis is not required at the plan level — the change touches at most 1-2 files and stays within the apps_lic boundary.

## ADG_GRAPH_LAYER_EVIDENCE

For P1.1 the relevant graph fact is the existing edge: `apps_lic.HOP5GenerationAgent` consumes whatever `llm_client` it receives at construction. The composition root is the only place where the dependency injection happens. No layer crossings, no new fan-in/fan-out — purely substituting a `None` (today's deterministic-stub-only path) with a real `QwenLLMClient()` instance.

## Decision Log

- **2026-05-02 17:55 UTC** — Plan created on completion of predecessor `apps-eval-qwen32b-rollout-b7c4d9`. Six buckets identified. Only P1.1 is burnable now; everything else is data-gated, trigger-conditioned, out-of-scope, or external CI. Waves W2/W3/W5/W6 marked `passive` or `deferred` rather than `pending` — they have no current work item.
- **2026-05-02 18:08 UTC** — P1.1 done. Anchor turned out to be `apps_lic/engines/generation_engine.py:GenerationEngine.execute()`, NOT the legacy `apps_lic/engines/HOP5GenerationAgent.py` referenced by the W4 P4.1 docstring. The substrate-based pipeline (`apps_lic/config/hop_pipeline.py:_STAGE_SPECS[4]` — stage_id=5 — points to `GenerationEngine`) is the production HOP5 entry point; the legacy agent class is hollow per `ops_scripts/ci/hollow_file_baseline.json` and is referenced only by tests. `QwenLLMClient` (the async adapter from W4 P4.1) is now effectively a tested-and-documented spare; the production wiring uses the same sync `openai.OpenAI` pattern as W2/W3/W5 to avoid asyncio bridging in the substrate's sync `execute()` method. Live evidence: real Qwen-32B output for a B2B outreach prompt; `generator=qwen_local` set on the returned dict. Fallback chain preserved: any failure (preflight / SDK / model_registry / client_init / gateway / empty) returns "" and `execute()` falls through to the original deterministic template scaffold.

## Burndown Order

1. **P1.1** (immediate, this session) — wire HOP5 composition root.
2. **P2.x** — passive observation; no scheduled response from Cascade until calibration weekly Markdown surfaces eligibility.
3. **P4.1** — fires conditionally on P2.4 producing latency p95-under-SLO evidence.
4. **P3.x** — fires conditionally on agreement-drift or section-taxonomy-change triggers.
5. **P5.1, P6.1** — out-of-scope / external; not Cascade work items.

## Closeout — 2026-05-03

### ADG-revalidated final dispositions

| Phase | Final disposition | Owner after closeout |
|-------|-------------------|----------------------|
| **P1.1** | ✅ Shipped — ADG-verified imports of `openai`, `is_qwen_available`, `QWEN_LOCAL_MODEL_ID`, `VLLM_BASE_URL` in `apps_lic/engines/generation_engine.py`; substrate pipeline `_STAGE_SPECS[4]` (stage_id=5) routes HOP5 to `GenerationEngine`; legacy `HOP5GenerationAgent` has 0 production fan-in. | None — code-resident |
| **P2.1–P2.6** | Transferred to `ops_scripts/calibration/judge_calibration.py` weekly emitter. Eligibility (≥30 paired runs, Wilson-CI thresholds) is detected by the harness, not by this plan. | `judge_calibration.py` + capture queue at `artifacts/capture/markers.jsonl` |
| **P3.1** | Trigger-conditioned `NEXT_STEP:` emitted (frontier second-judge pairing if Wilson-CI agreement < 0.85 over 4-week rolling window). | Backlog — spawns new T2/T3 plan on trigger |
| **P3.2** | Trigger-conditioned `NEXT_STEP:` emitted (apps_rfp HOP3b/HOP3c reopen if any `SectionType` graduates from templated to free-text). | Backlog — spawns new T2/T3 plan on trigger |
| **P4.1** | Gated `NEXT_STEP:` emitted (apps_rg `n_candidates: 3 → 5` — single-line edit in `apps_rg/config/rg_agent_specs.json:36`, fires only when P2.4 latency data shows p95 under SLO at N=5). NOT shipped here — would risk SLO without the gating evidence. | Backlog — micro-plan on trigger |
| **P5.1** | Already non-goal — `apps_underwriting_ai` activation will spawn its own plan when preconditions hold (predecessor §"Wave 8 findings"). | Separate future plan |
| **P6.1** | External CI — RTC-REQ / mutation-rejection / OTel coverage gates fire on next pipeline run independently of plan state. | CI |

### Why closing now is safe

- Every "passive" item is owned by an autonomous system (`judge_calibration.py`) that does not reference this plan's slug. ADG fan-in confirms zero structural coupling between the plan and the data pipeline.
- Every "trigger-conditioned" item now has a durable `NEXT_STEP:` marker — the trigger surface (Wilson-CI watchdog, section-taxonomy diff) is in code, not in plan prose.
- P4.1's gate condition (latency p95 fits SLO at N=5) is unmet today; shipping it now would violate the plan's own success criteria.

### Author-Gate

No Author-Gate fired for closeout: dispositions are deterministic (data-gated → harness; trigger-conditioned → NEXT_STEP; gated config → NEXT_STEP; out-of-scope → already non-goal; external → CI). No competing options.
