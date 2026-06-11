---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\l0-prompt-retrieval-deferred-triage-d3e8f1.md'
original_relative_path: 'l0-prompt-retrieval-deferred-triage-d3e8f1.md'
source_sha256: 191da493fa7e3504709637dbd2d71316494c898bb883a44e4655dd4ec282c402
recovered_status: LOST_RECOVERED
last_commit: '6477883502e'
last_commit_date: '2026-04-27 08:55:24 -0400'
created_date: '2026-04-22'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_type: tracker
---

# L0 Prompt Retrieval — Deferred Triage

**Parent plan:** `l0-context-prompt-retrieval-review-b7c4a2.md` (W1+W2+W3 DONE)
**Status:** Todo — awaiting prioritization slot
**Tier:** T1 per item (single-file exception-handler fix) / T2 aggregate
**ADG Provenance:** backend=sqlite, snapshot=adg_indexed_04222026_1508.sqlite

---

## Scope

Parent plan surfaced 3 HIGH-severity antipatterns and 2 stale tests that were out-of-scope for the C0/prompt-retrieval wiring fix. This plan tracks their triage independently so the parent plan can close.

None were caused by W1/W2 of the parent. The 3 antipatterns were exposed by intervening commit `0de154c7e6` (`adg-ci Wave C — exception-contract caller resolution`) which tightened caller resolution and re-classified these pre-existing catches as HIGH.

---

## Wave Structure

| Wave | Phase IDs | Focus | Priority | Est. Tokens | Status | Success Criteria |
|---:|---|---|:-:|---:|---|---|
| W1 | P1.1 | Triage `execution_orchestrator.py` HIGH catches (ImportError + RuntimeError) — L0, 2 violations, × 2.0 layer multiplier | **P0** | ~4k | Todo | Each catch either narrowed to specific recovery or gains `guardian: allow-<type> -- <justification>` per approval-exception-policy |
| W2 | P2.1 | Triage `gptcache_client.py:130` HIGH catch (`_NotFoundError`) — L4, 1 violation, × 1.75 layer multiplier | **P1** | ~2k | Todo | Catch is legitimate cache-miss sentinel → guardian exemption; OR narrowed to explicit miss return path |
| W3 | P3.1 | Fix 2 stale prompt-lifecycle tests referencing non-existent `agentic_core.L0_routing.engines` (real path is `reasoning`) | **P2** | ~1k | Todo | `test_build_mixins_sorted` and `test_build_from_packet_with_real_store` pass without `--deselect` |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---:|---|
| P1.1 | Narrow or exempt `ImportError` catch at line 303 and `RuntimeError` catch at line 328 in `execution_orchestrator.py` | `agentic_core/L0_routing/reasoning/execution_orchestrator.py` | L0 orchestrator is a hot path; any change needs behavioral review — both catches may be legitimate boundary guards (import-time fallback, subprocess failure containment). Most likely outcome: guardian exemptions with specific justifications. | ~4k | Todo |
| P2.1 | Triage `_NotFoundError` catch at line 130 in `gptcache_client.py` | `agentic_core/L4_state/cache/gptcache_client.py` | Cache-miss is semantically a non-error in client logic; the catch likely translates the library's NotFound to a return-None. Either convert to explicit return path or add guardian exemption. | ~2k | Todo |
| P3.1 | Update stale test imports: `agentic_core.L0_routing.engines.prompt_bom_builder` → `agentic_core.L0_routing.reasoning.prompt_bom_builder` | `tests/integration/apps_exec/test_prompt_lifecycle_pipeline.py` | Two tests (`test_build_mixins_sorted`, `test_build_from_packet_with_real_store`) import from a module path that no longer exists. Likely a rename artifact never backfilled. | ~1k | Todo |

## ADG_HOTSPOT_REPORT

| File | Violations | Fan-in (imports) | Layer | Layer Mult | Impact | Archetype | Surfaces |
|---|---:|---:|:-:|:-:|---:|---|---|
| `agentic_core/L0_routing/reasoning/execution_orchestrator.py` | 2 HIGH (lines 303, 328) | — | L0 | 2.0 | **P0** | ORCHESTRATOR | Execution, Observability |
| `agentic_core/L4_state/cache/gptcache_client.py` | 1 HIGH (line 130) | — | L4 | 1.75 | **P1** | STATE_NODE | State |
| `tests/integration/apps_exec/test_prompt_lifecycle_pipeline.py` | — stale imports | — | tests | 1.0 | **P2** | — | — |

Priority rationale: L0 orchestrator × 2.0 × 2 violations = highest impact. L4 cache × 1.75 × 1 violation = medium. Test hygiene = lowest.

## ADG_GRAPH_LAYER_EVIDENCE

1. **P0 wave plan** — `adg_p0_wave_plan` currently reports 0 P0 items (the ratchet blocks at P1-HIGH, not P0).
2. **`v_p1_mis_layered_infra`** — none of these three files appear; they are behavioral antipatterns, not layering violations.
3. **`mv_hotspot_centrality`** — `execution_orchestrator.py` is centrality-high in L0 (orchestrator archetype), which is why 2 HIGH catches there dominate W1 priority.
4. **Semantic edges** — the catches emit no `flows_to` (error path dropped), no `emits_side_effect` (no log/audit), confirming they are silent swallows rather than narrowed handlers.

## Non-Goals

- Rewriting any of these modules. Each fix is a targeted exception-handler change or a guardian exemption.
- Modifying the P1 ratchet ceiling. The ratchet correctly flagged pre-existing debt that now needs remediation.

## Rollback

Each phase touches exactly one file. `git revert` per phase.
