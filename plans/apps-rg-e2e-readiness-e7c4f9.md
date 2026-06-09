---
plan_type: platform_core_change
slug: apps-rg-e2e-readiness-e7c4f9
status: In Progress
ai_summary: "Sequence the 4 prerequisites the operator requires before the full AIG E2E."
dod_exempt: false
supersedes: []
---

# apps_rg Full-E2E Readiness — Operator-Gated Sequence

## Supersedes
| Predecessor slug | Reason |
|---|---|
| _None — net-new sequencing plan._ | |

## Context (SCQA)
- **Situation.** The AIG full-resume E2E reaches REAL_LLM on every generating lane (C0.2 fixed); ey_bullets
  ALLOWs. Remaining blockers are grounding/coverage + lane-parity, not infrastructure.
- **Complication.** The operator does NOT want the full E2E run until four readiness conditions hold.
- **Question.** What is the ordered set of changes, and what's already done?
- **Answer.** Graph *skills* for all epochs (incl. EY Phase-2 / InsurTech Phase-3) are already in the ledger
  (`graph-skills-three-phase-jd-b3e5f2`, `resume-graph-skills-remediation-a7f2c3`,
  `graph-skills-quality-enhancement-c4e8a1`). unify_bullets / competencies / executive_summary generation is
  already graph-sourced (`unify-bullets-graph-compose-a3f7e2`, `competencies-graph-10x6-gemini-924516`,
  `c03-skills-graph-exec-summary-f9a2c4`). The remaining work is the 4 operator gates below.

## Operator E2E gates (must all be done before the full E2E)
| # | Gate | Status | Notes |
|---|---|---|---|
| G1 | **InsurTech & EY bullets leverage C0.3, generated same way as Unify/IBM** (graph-anchored bundles → SC pool → Claude per-slot selector → Claude-selector X1D judge) | 🟢 Code done — EY proven; InsurTech blocked upstream (C0) | Lean upgrade of `role_episode_lane` bullet path (no per-lane file clones). **EY ALLOWs** (REAL_LLM, X3_ALLOW, graph gate PASS). **InsurTech** = REQUIRED_PROOF_ABSENT at C0 proof loading (pre-existing grounding gap, plan `apps-rg-fec-grounding-blocker-d9a4b7` / G22 BM25) — upstream of the rewire. Judge = Claude pool selector (operator decision, Unify/IBM parity — NOT gemini-pro). SC = 2 for insurtech/ey; Unify/IBM left at 4 (uniform 2-SC reverted — Unify selector `fallback_empty` is count-independent + pre-existing; see Evidence). |
| G2 | **Narratives — all four use the hybrid design** (derive from finalized bullets + role-episode `bundle_theme`/`scope_signals`, not the static base `role_narrative`); change EY/InsurTech **after** their bullets (G1) | ⬜ Not Started | Unify/IBM narratives switch now; InsurTech/EY after G1. Retires ibm_narrative's hardcoded metric-strip. |
| G3 | **Finalize executive_summary + headline approach** (currently TBD) | ⬜ Not Started | exec_summary already C0.3-graph-sourced (f9a2c4) — confirm/adjust; headline approach to be decided (review pending). |
| G4 | **Full AIG E2E** | ⬜ Blocked on G1–G3 | bank all changes; per-lane disposition; iterate to generated_resume.json. |

## Wave Progress
| Wave | Gate | Focus | Est. Tokens | Status | Success Criteria |
|---|---|---|---|---|---|
| W1 | G1 | EY+InsurTech graph-sourced bullets (bundles + Engine A + 2-SC + Claude-selector judge) | ~260k | 🟢 EY done; InsurTech C0-blocked | EY: graph bundles, SC pool, per-slot selector, Claude-selector judge, graph gate PASS, X3_ALLOW ✓. InsurTech: rewired (same path) but REQUIRED_PROOF_ABSENT upstream at C0 (d9a4b7). |
| W2 | G2 | Narrative hybrid: Unify/IBM now; EY/InsurTech after W1 | ~150k | ⬜ | all 4 narratives derive from bullets + bundle theme; anti-duplication kept; real judge (incl. EY/InsurTech post-W1) |
| W3 | G3 | Finalize exec_summary + headline approach | ~120k | ⬜ | documented approach + any needed change; both lanes' gates reviewed |
| W4 | G4 | Full AIG E2E | ~90k | ⬜ | run completes; per-lane chain; ≥ baseline lanes ALLOW; iterate |

## Phase-Level Summary
| Phase | Title | Scope | Status |
|---|---|---|---|
| P1 | EY/InsurTech bullets graph-sourced | `fact_inventory/{ey,insurtech}_role_episode_bundles.json`, employment_bullet_pool, lane dispatch, judges, lean gates | ⬜ |
| P2 | Narrative hybrid (bullet+theme derived) | unify/ibm narrative lanes (now); role_episode narrative (after P1); anti-duplication gates | ⬜ |
| P3 | Exec_summary + headline finalize | exec_summary (confirm f9a2c4 approach); headline (decide approach) | ⬜ |
| P4 | Full E2E | doctor + bootstrap + full AIG run | ⬜ |

## Already-done (Notion-verified, do NOT redo)
- Graph skills incl. EY Phase-2 (4) + InsurTech Phase-3 (10): `graph-skills-three-phase-jd-b3e5f2` (Completed).
- unify_bullets graph-compose: `unify-bullets-graph-compose-a3f7e2` (Completed).
- competencies graph pool + gemini judge: `competencies-graph-10x6-gemini-924516` (Completed).
- executive_summary C0.3 graph: `c03-skills-graph-exec-summary-f9a2c4` (Completed).

## G1 Evidence (2026-06-09)
**Approach (lean):** upgraded the shared `role_episode_lane` bullet path in place — no per-lane file
clones. Bullets now load graph role-episode bundles → frame the prompt around them → generate via the
shared SC-pool engine (`generate_bullet_lane_with_sc_and_claude`) → Claude per-slot selector picks →
Claude-selector X1D judge (`employment_pool_x1d_judge_rows`). Files: `role_episode_lane.py` (bundle
loader + graph prompt + generation/judge swap + graph gate), `employment_bullet_pool.py` (per-lane SC),
+ `fact_inventory/{ey,insurtech}_role_episode_bundles.json`.

**EY (`ey_bullets`) — PROVEN:** `RUNTIME_GENERATION_STATUS=REAL_LLM`, `PRODUCT_STATUS=X3_ALLOW`,
`PRODUCT_QUALITY_STATUS=PASS`. `generation_mode=qwen_employment_pool_claude_top_n_regen`,
`total_paths_executed=2`, `claude_selection_count=3` (scores 0.82/0.79/0.80). X1D judge
`provider_key=anthropic_claude`, `judge_role=employment_bullet_pool_selector`, pass=0.79. All X2 gates
pass incl. new `x2_ey_bullets_graph_role_episode_bundle_consumed`. Bullets graph-anchored: $15M
regulatory analytics modernization, 40% remediation reduction, 12% Solvency II/AG43.

**InsurTech (`insurtech_bullets`) — BLOCKED upstream:** `REQUIRED_PROOF_ABSENT` at C0 proof loading
(`x2_insurtech_bullets_required_proof_present=False`) — fails closed *before* the rewire runs. Same C0
grounding gap as plan `apps-rg-fec-grounding-blocker-d9a4b7` (G22 BM25/sparse). Rewire is correct; lane
needs a grounded C0 proof pool to exercise it.

**Judge decision (operator, AskUserQuestion 2026-06-09):** Claude pool selector IS the X1D judge
(Unify/IBM parity) — not a separate gemini-pro call. The selector scores each candidate against the
employment rubric (MODEL_BACKED, real Claude) and picks; that scoring is the judge.

**Uniform 2-SC reverted for Unify/IBM:** set `SC_PATH_COUNT_BY_LANE` per-lane (insurtech/ey=2,
unify/ibm=4=original). Empirically, `unify_bullets` selector returns `selection_mode=fallback_empty`
(`claude_selection_count=0`) at **both** SC=2 (regen→5 paths) and SC=4 (regen→7 paths) — count-independent.
SC paths generate valid bullets; the selector fails on the wider 6-slot candidate set (EY's 3-slot path
selects fine). This is **pre-existing on the branch, not a G1 regression** — `unify_bullets_lane` is
untouched. Captured as a separate background task (selector fix); blocks unify/ibm in the full E2E (G4).


- `apps-rg-fec-grounding-blocker-d9a4b7`: R3/G23 ✓, R1 FEC ✓, R2 competencies term-count (deterministic top-up
  pending). These improve E2E pass-rate but are tracked under that plan; the operator's 4 gates above are the
  E2E trigger.

## Dependency graph
```
  G1 (EY/InsurTech bullets) ──┬──▶ G2 (EY/InsurTech narrative hybrid)
                              │
  G2 (Unify/IBM narrative) ───┘   (can start now, independent of G1)
  G3 (exec_summary + headline) ── independent, can run in parallel
  G1 + G2 + G3 ───────────────▶ G4 (full E2E)
```

## Definition of Done
| # | Criterion | Verification |
|---|---|---|
| 1 | insurtech/ey bullets graph-sourced (bundles + Engine A + real Gemini judge) | lane run shows SC paths + selector + gemini judge; no REQUIRED_PROOF_ABSENT |
| 2 | all 4 narratives derive from bullets + bundle theme (anti-duplication intact) | narrative lane shows bullet-derived source; n-gram gate green |
| 3 | exec_summary + headline approach documented + any change landed | plan note + lane tests |
| 4 | full AIG E2E run completes with per-lane chain | live run artifacts |
