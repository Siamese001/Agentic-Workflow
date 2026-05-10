---
status: decided
type: author-gate-decisions-record
created: 2026-05-10
session: apps_rg-restoration-author-gate-walkthrough
related:
  - docs/architecture/apps-rg-pre-consolidation-functionality-gap.md
  - docs/architecture/apps-rg-restoration-author-gates.md
  - .windsurf/state/refactor_decisions/refactor_decision_ledger.sqlite
---

# apps_rg Restoration — Author-Gate Decisions (2026-05-10)

All 15 AG decisions settled in one walkthrough session. AG-1 through AG-7 surfaced interactively; AG-8 through AG-15 batch-accepted at the recommended option per user directive.

## Decisions

| AG | Domain | Selected | Confidence | Gap | Principle | Precedent |
|---|---|---|---|---|---|---|
| **AG-1** | payload extension shape | `d_manifest_bundled` | 0.88 | +0.23 | AG-RGGOV-6 declarative-ingress preserved via digest-bound manifest | none |
| **AG-2** | config loading authority | `b_apps_rg_eager_manifest` | 0.90 | +0.40 | apps_rg owns domain config loading | AG-1.d |
| **AG-3** | prompt mode selection | `a_explicit_user_choice` | 0.86 | +0.31 | domain intent is user authority | none |
| **AG-4** | multi-provider reconciliation | `b_capability_requirement_clause` | 0.87 | +0.27 | apps_rg declares semantic needs; core decides provider | none (ADR required) |
| **AG-5** | provider_util canonical | `a_utils_canonical` | 0.90 | +0.35 | real impl wins over stub | none |
| **AG-6** | env consumption point | `c_model_registry_at_l0` | 0.88 | +0.38 | L0 owns provider routing | AG-4.b |
| **AG-7** | X1A-X1J invocation | `c_exit_review_packet_builder_stage` | 0.88 | +0.23 | single responsibility per stage | none |
| **AG-8** | 29-gate mesh phasing | `c_rolling_restoration` | 0.87 | +0.17 | incremental validation per wave | AG-7.c |
| **AG-9** | apps gate placement | `b_exit_stage_callbacks_registry` | 0.87 | +0.37 | apps_rg owns domain logic; core mediates | AG-7.c |
| **AG-10** | HOP pipeline restoration | `a_l3_reads_hop_from_apps_rg` | 0.85 | +0.30 | domain owns stages; core owns orchestration | AG-1.d + AG-2.b |
| **AG-11** | two-phase generation | `a_pa_template_chaining` | 0.86 | +0.26 | PA owns prompt composition | AG-3.a + AG-10.a |
| **AG-12** | healing cycle | `b_exit_x3b_redispatch_via_l3` | 0.85 | +0.25 | canonical X3 flow drives retry | AG-7.c + AG-10.a |
| **AG-13** | HITL bridge | `b_apps_rg_hitl_emitter_core_registry` | 0.87 | +0.32 | consistent registry pattern | AG-9.b |
| **AG-14** | output enrichment + DOCX + spine handoff | `a_apps_rg_exit_stage_callbacks_registry` | 0.86 | +0.41 | third registry pattern instance | AG-9.b + AG-13.b |
| **AG-15** | strategic meta (restore/phasing/backcompat) | `recommended_per_category_rolling_feature_flag` | 0.88 | +0.33 | incremental delivery + explicit cutover | AG-8.c |

## Architectural Emergent Pattern

Three decisions collapse to **one consistent registry pattern**:
- **AG-9** gate registry
- **AG-13** HITL registry
- **AG-14** output callback registry

Implementation consolidation: shared base `agentic_core/runtime/registries/_base.py` with three concrete registries. Mirrors the existing `apps_rg.cert.fec_producer` pattern.

## The 6 Implementation Waves

Per AG-15 phasing:

| Wave | Scope | Dependencies |
|---|---|---|
| **W1 — Multi-provider LLM** | AG-4 + AG-5 + AG-6 (+ ADR for AG-4 capability clause) | none |
| **W2 — Safety mesh (first batch)** | AG-7 (ExitReviewPacket builder) + AG-8 (G09+G21+G22) + AG-9 (gate registry) | W1 telemetry |
| **W3 — HOP pipeline** | AG-10 (L3 reads HOP) + AG-11 (two-phase via PA chaining) | W2 |
| **W4 — HITL + healing** | AG-12 (X3B re-dispatch) + AG-13 (HITL registry) | W2 |
| **W5 — Enrichment** | AG-14 (DOCX + RunReport + spine handoff) | W4 |
| **W6 — Polish + cutover** | P3 categories + flip `APPS_RG_RESTORATION_MODE` default from v1→v2 | W1-W5 |

## Foundational Decisions (Phase A) — Cross-Wave

AG-1, AG-2, AG-3 — land in W1 as prerequisite infrastructure:
- AG-1.d: extend `AppsRgIngressPayload` with `profile_manifest` field + `capability_requirements` field (AG-4.b)
- AG-2.b: apps_rg `__main__` pre-pass loads `AppsRgProfileManifest`
- AG-3.a: `--mode` CLI flag + wizard branch + `AppsRgIngressPayload.generation_mode`

## Feature Flag Control

Per AG-15.3:
- `APPS_RG_RESTORATION_MODE=v2` — new path active
- `APPS_RG_RESTORATION_MODE=v1` (default until W6 verified) — current path
- Cutover after W6 smoke tests + X1A-X1J all green on sample runs

## Ledger Row Records

All 15 decisions written to `@.windsurf/state/refactor_decisions/refactor_decision_ledger.sqlite` via `DECISION_CAPTURED:` markers. Each marker contains `type`, `repo_area`, `selected`, `outcome=executed`, `confidence`, `gap`, `override=false`, `principle`, `precedent`, `exit_criteria`. Capture pipeline: marker → `markers.jsonl` → `queue_to_ledger.py` → SQLite → Notion mirror via `tools/notion/sync_decision_ledger.py`.

## Meta-Learning Notes

- **Dominance fired on every AG** — confidence gaps ranged +0.17 to +0.41. No low-confidence decisions required extra deliberation.
- **Three AGs cite prior AGs as precedent** (AG-10 cites AG-1+AG-2; AG-11 cites AG-3+AG-10; AG-14 cites AG-9+AG-13) — dependency graph holds.
- **One AG requires a constitutional change** (AG-4 capability-requirement clause added to AG-RGGOV-6) — ADR sequencing gates W1.
- **One emergent consolidation** — three registries (gate, HITL, output) share a base pattern. Plan author should factor out `_base.py` once to avoid triplicating the pattern.

## Next Actions (NOT done in this session)

- Draft ADR: "AG-RGGOV-6 capability-requirement clause addition"
- Author W1 plan: `apps-rg-w1-multi-provider-<6hex>.md`
- Emit `PLAN_CREATED:` marker + register Plans DB row per §36

## Session Pipeline Confirmation

- **Walkthrough complete**: 15/15 AGs decided
- **Ledger state**: 16 prior rows + 15 pending from this session (processed post-response by capture hook)
- **Durable record**: this file (survives hook failure)
- **Dependency graph**: intact, validated
- **No code changes**: decisions are design choices, not implementation
