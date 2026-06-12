---
plan_type: platform_core_change
slug: graph-source-ey-insurtech-bullets-c5f2a9
status: In Progress
ai_summary: "Promote EY+InsurTech bullets from base-resume Engine-B to graph-sourced 2-SC + Gemini judge."
dod_exempt: false
supersedes: []
---

# Graph-Source EY + InsurTech Bullets (2-SC + real Gemini judge + lean gates)

## Supersedes
| Predecessor slug | Reason |
|---|---|
| _None — net-new plan._ | |

## Context (SCQA)

- **Situation.** EY and InsurTech bullets run the generic **Engine B** (`role_episode_lane.py`):
  source = base-résumé structured facts (NOT graph), generation = 1 call (no SC, no selector),
  judge = deterministic X2-mirror (no real LLM call), ~6 thin gates. Unify/IBM run **Engine A**
  (graph-anchored bundles → 4-SC pool → Claude per-slot selector → real Gemini judge).
- **Complication.** This makes EY/InsurTech second-class: ungrounded in the skills graph (so the
  epoch-ordinal contamination model can't police them), no independent semantic judge, and not
  best-of-N. Phase-2 (EY) now has **4** graph skills and Phase-3 (InsurTech) has **10** (epoch
  wiring `e3284e5447`), so graph-anchoring is now feasible.
- **Question.** Bring EY/InsurTech to parity with Unify/IBM — graph-sourced, multi-draft,
  real-judged — without the full 45-gate Unify weight, and without over-tailoring two older roles?
- **Answer (user-directed).** Graph-source both lanes via new role-episode bundles; generate with
  **2 SC paths × 3 bullets** (Claude per-slot selector); add **1 real Gemini-Pro judge**; and define
  a **lean graph-bullet gate set** (grounding + shape + epoch-scope) rather than inheriting the
  Unify/IBM style/metric gates.

## Status Tables

### Wave Progress
| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| W1 | P1 | Author graph-anchored bundles: `ey_role_episode_bundles.json` (3) + `insurtech_role_episode_bundles.json` (3) | ~60k | Phase-2/3 skills suffice (4/10) | ⬜ Not Started | Each of 3 bullets anchored to ≥1 graph skill + linked source fact; metric_outcome_ids declared |
| W2 | P2 | Lean graph-bullet gate set for EY/InsurTech (consolidate role_episode gates + add graph-binding) | ~40k | role_episode `_x2_gates` is the base | ⬜ Not Started | ~10 gates: grounding + count + graph_skill_node_ids_required + epoch-scope; no Unify-specific gates |
| W3 | P3 | Rewire EY/InsurTech generation: Engine-B → `generate_bullet_lane_with_sc_and_claude` with **sc_paths=2** | ~90k | employment_bullet_pool supports per-lane SC count | ⬜ Not Started | 2 SC drafts → Claude per-slot selector → 3 bullets; regen safety net intact |
| W4 | P4 | Real **Gemini-Pro** judge: `run_ey_bullets_judges` / `run_insurtech_bullets_judges` (replace mirror) | ~40k | section_judge_policy proof roster | ⬜ Not Started | Real gemini_pro call grades the 3 bullets; X3 blocks on judge fail |
| W5 | P5 | Wire-up + tests + smoke (negative/positive + lane run) | ~70k | — | ⬜ Not Started | Tests green; lane smoke runs; demoted gates honored; grounding still fail-closed |

### Phase-Level Summary
| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| P1 | Bundles | `fact_inventory/{ey,insurtech}_role_episode_bundles.json` | accurate skill mapping + metric provenance (defines résumé claims) | ~60k | ⬜ |
| P2 | Lean gates | new `validators/role_episode_graph_x2.py` or extend role_episode `_x2_gates` | grounding + graph-binding without Unify weight | ~40k | ⬜ |
| P3 | 2-SC engine | `employment_bullet_pool.py`, `bullet_lane_generation.py`, lane dispatch | rewire from role_episode → SC pool; SC=2 | ~90k | ⬜ |
| P4 | Gemini judge | `judges/{ey,insurtech}_bullets_x1d.py`, `section_judge_policy.py` | proof roster + rubric | ~40k | ⬜ |
| P5 | Tests/smoke | `tests/unit/apps_rg/**` | negative/positive proofs; no-regression | ~70k | ⬜ |

## Architecture

- **Source (W1).** New bundle files mirroring `unify_role_episode_bundles.json`: per bundle —
  `role_episode_bundle_id, employer, title, time_window, employer_node_id, bundle_theme,
  scope_signals, graph_skill_node_ids (Phase-2/3), linked_source_fact_ids (bul_ey_*/bul_insurtech_*),
  linked_metric_outcome_ids, bullet_intent`, with top-level `invariants`
  (`base_resume_hydration_excluded: true`). Source content = the base-résumé EY/InsurTech bullets,
  re-expressed as graph-anchored facts.
- **Engine (W3).** Route `ey_bullets`/`insurtech_bullets` to `generate_bullet_lane_with_sc_and_claude`
  (the Unify/IBM engine) with `SC_PATH_COUNT_BY_LANE[...] = 2`. 2 full-3-bullet drafts → Claude
  per-slot selector picks best per bullet → regen safety net. Replaces the single role_episode call.
- **Judge (W4).** `run_ey_bullets_judges`/`run_insurtech_bullets_judges` → `run_policy_section_judges`
  with `judge_keys=["gemini_pro"]` (real call, GRADE-ONLY), replacing the deterministic `_judge_rows`
  mirror. `section_judge_policy` proof roster for these lanes → `("gemini_pro",)`.
- **Gates (W2).** Lean set: `allowed_fact_ids_non_empty`, `source_fact_ids_supported`,
  `claim_ledger_claim_text_non_empty`, `runtime_real_llm`, `bullet_count_3`, `no_embedded_newline`,
  **+ new** `graph_skill_node_ids_required` (parity with unify), `no_cross_employer_leakage`,
  epoch-scope (`phase ≤ max_phase`). Drop nothing from the existing 6 (all correctness); add the
  graph-binding + leakage + epoch gates. ~10 total — far below Unify's ~45.

## Definition of Done
| # | Criterion | Verification |
|---|---|---|
| 1 | EY + InsurTech bundles exist, each bullet graph-skill-anchored + source-fact-linked | bundle files + schema check |
| 2 | EY/InsurTech generate via 2 SC drafts + Claude per-slot selector | gen_meta shows 2 paths + selection_mode |
| 3 | A real Gemini-Pro judge grades the 3 bullets (not a mirror) | x1d output shows MODEL_BACKED gemini_pro call |
| 4 | Lean ~10-gate graph-bullet set; grounding + graph-binding + leakage present | gate inventory |
| 5 | **Negative:** ungrounded/leaked/wrong-count bullet still BLOCKS | weak-payload test |
| 6 | **Positive:** clean graph-sourced 3 bullets pass; no base-résumé hydration | lane test + grounding gate |
| 7 | Lane smoke: `python -m apps_rg --section ey_bullets ...` runs (or same disposition as baseline) | live run |

## Safety / Invariants
- Bundle content defines résumé CLAIMS → author from real base-résumé accomplishments only; no fabrication.
- `base_resume_hydration_excluded: true` — bundles re-anchor facts to the graph, not the résumé prose.
- Grounding stays fail-closed (`source_fact_ids ⊆ allowed`), no weakening.
- 2 SC (not 4) is deliberate: EY/InsurTech are Phase-2/3 (older) — enough for per-slot mixing, less spend.

## Open question for operator
- The base-résumé EY/InsurTech bullets carry metrics ($15M, 40%, 99.99%, Solvency II). These must map
  to **approved `metric_outcome_id`s** in the bundles (IBM-style) so the metric-fidelity gate can bind
  them. Confirm the metrics are approved-for-claim, or mark conditional.
