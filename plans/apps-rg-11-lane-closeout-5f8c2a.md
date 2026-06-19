---
plan_id: apps-rg-11-lane-closeout-5f8c2a
plan_format: v2
plan_type: closeout
touches_agentic_core: false
touches_governance_ci: false
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
supersedes: ["typed-edge-role-facet-guardrails-a6f3d2"]
---

# apps_rg 11-Lane Closeout

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: IN_PROGRESS
CURRENT_WAVE: B-SHIP
LAST_COMPLETED_WAVE: NONE
LAST_UPDATED: 2026-06-16

## Decision

This plan replaces the active execution path in
`plans/typed-edge-role-facet-guardrails-a6f3d2.md`.

The old plan remains historical design context for role facets, typed edges,
sliding-scale composition, and waterfall proof. It is no longer the live
execution checklist. The live objective is smaller:

1. Get current `main` to one durable Anthropic `11/11 X3_ALLOW` run.
2. Assemble `final_resume.json` and DOCX from that run.
3. Prove GraphDB is the skills and metrics SSOT with focused static/runtime tests.
4. Keep graph-skill waterfall analysis as cheap diagnostics, not as a blocker for
   the first finished resume.

## Current Main Baseline

Verified on `main` at `b5e619d29dc35fdbf856d264d283616c4471b8b3`:

- `main` is clean and synced to `origin/main`.
- `apps_rg/fact_inventory/augmented_skills_graph.py` exposes graph-authority
  projection fields including `source_resume_files`, `activation_status`, and
  `support_level`.
- `tests/_apps_contract/test_apps_rg_c0_ownership_split.py` blocks apps_rg graph
  skill authority from leaking into `agentic_core`.
- `tests/unit/apps_rg/fact_inventory/test_augmented_skills_graph_sqlite.py`
  proves C0.3 resolves resume-backed graph skills.
- `tools/apps_rg/graph_skill_utilization_report.py` exists and remains
  report-only; it requires `final_resume_assembly/final_resume.json`.
- No current full apps_rg E2E artifact exists after `b5e619d29d`; the next
  live run is the source of truth for the current lane board.

Recent verification:

```powershell
python -m pytest tests\_apps_contract\test_apps_rg_c0_ownership_split.py `
  tests\unit\apps_rg\fact_inventory\test_augmented_skills_graph_sqlite.py `
  tests\unit\apps_rg\test_graph_skill_utilization_report.py -q
```

Result: `37 passed, 1 skipped`.

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| B-SHIP | B1, B2, B3 | First durable Anthropic 11/11 run | ~12K | Current `main` can run Anthropic apps_rg E2E from a clean checkout | IN_PROGRESS | 11 lanes reach `X3_ALLOW`; final JSON and DOCX exist; run summary rendered |
| G-SSOT | G1, G2 | GraphDB skills and metrics authority | ~6K | GraphDB-backed selectors remain the only skills/metrics authority | TODO | Static/runtime tests prove JD, briefing, fact ledger, and proof-pool cannot mint authority |
| W-DIAG | W1, W2 | Waterfall diagnostic, not ship blocker | ~5K | Selection diagnostics can run without provider calls | TODO | Assembly report exists after B-SHIP; five-target diagnostic emits causal deltas |
| S-PCT | S1, S2 | Sliding-scale percent policy | ~7K | Active enforcement waits until dry-run diagnostics are stable | TODO | Dry-run diagnostics are emitted; active enforcement only starts after proof |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| B1 | Preflight | TODO |
| B2 | Full Anthropic E2E | TODO |
| B3 | Single-lane iterate if needed | TODO |
| G1 | GraphDB skills authority tests | TODO |
| G2 | GraphDB metrics authority tests | TODO |
| W1 | Assembly-based utilization after successful run | TODO |
| W2 | Provider-free selection diagnostic | TODO |
| S1 | Sliding-scale dry-run diagnostics | TODO |
| S2 | Sliding-scale active enforcement | TODO |

## Non-Goals

- Do not implement role facets, typed edges, or active sliding-scale enforcement
  before the first durable `11/11` Anthropic run.
- Do not run multi-target live matrices before the single-resume ship gate passes.
- Do not treat `fact_ledger`, proof-pool rows, JD, briefing, or prior generated
  text as skills or metrics authority.
- Do not let JD or briefing text mint skill eligibility, metric eligibility, or
  proof authority. JD and briefing can express target demand only; eligible
  skills and metrics must resolve to GraphDB-backed IDs before selection,
  weighting, prompting, diagnostics, or enforcement.
- Do not make prompt-only fixes count as W3/W4/W5 architectural closure.
- Do not revive Notion as plan SSOT; Notion is a manual tracking mirror only.

## Wave B-SHIP: First Durable 11/11

Goal: one current-main Anthropic full run reaches all 11 generated lanes
`X3_ALLOW`, assembles final artifacts, and renders DOCX.

### B1. Preflight

Commands:

```powershell
python scripts/governance/codex_readiness.py --json --require-clean-worktree --fail-duplicate-processes
python scripts/governance/check_windows_path_budget.py --out-dir artifacts/rg_b --suite apps_rg.dev.resume_generation
python ops_scripts\ci\check_apps_rg_fact_vectors_readiness.py
```

Acceptance:

- Main checkout clean.
- No duplicate apps_rg provider runs.
- Chroma dense and sparse fact vectors ready.
- Output root passes Windows path budget.

### B2. Full Anthropic E2E

Run current-main apps_rg for:

- target company: `Anthropic`
- target role: `Manager of Applied AI Architecture, Partnerships`
- JD: `apps_rg/config/targeting/anthropic_manager_applied_ai_architecture_partnerships_jd.txt`
- briefing: `apps_rg/config/targeting/anthropic_manager_applied_ai_architecture_partnerships_briefing.md`
- artifact root: short path such as `artifacts/rg_b`

Required after every run:

```powershell
python tools/apps_rg/render_run_summary.py artifacts/rg_b
```

Acceptance:

- 11 lanes executed and finalized.
- 11 lanes `X3_ALLOW`.
- No mocked generation or mocked judge certification.
- `final_resume_assembly/final_resume.json` exists.
- DOCX artifact exists.
- Run summary rendered before claiming success.

### B3. Single-Lane Iterate If Needed

If the full run blocks:

1. Inspect the failed lane's X2/X3 receipts.
2. Patch only the failed lane or shared gate that directly caused the failure.
3. Add a focused regression test for the exact failure shape.
4. Run focused tests.
5. Re-run the failed lane or a patch-run if the runner supports it.
6. Re-run full `artifacts/rg_b` confirmation when all lanes are locally green.

Do not open W3/W4/W5 scope while B-SHIP is blocked.

## Wave G-SSOT: GraphDB Skills And Metrics Authority

Goal: close the active SSOT proof with tests, not another broad migration.

The authority rule is explicit:

- GraphDB is the SSOT for selectable skills.
- GraphDB is the SSOT for metric outcomes and metric weights.
- JD and briefing inputs are targeting demand signals only. They may request or
  emphasize skills, but they cannot create skill IDs, metric IDs, eligibility,
  weights, proof, or traversal authority.
- Prompt assembly, proof-pool lookup, graph utilization reporting, waterfall
  diagnostics, and sliding-scale policy must consume GraphDB-approved skill and
  metric IDs, not raw JD phrases.

Acceptance tests must prove:

- Skills authority resolves through `augmented_skills_graph`.
- Metrics authority resolves through first-class `metric_outcome` rows.
- `fact_ledger` cannot provide skill eligibility, metric eligibility, weighting,
  proof, or traversal authority.
- Proof-pool is transport/cache for GraphDB-approved IDs only.
- JD and briefing terms remain targeting-only.
- JD-specified skills align to GraphDB skill IDs through a traceable resolver;
  unmatched JD skill demand fails closed or is reported as unresolved demand.
- Unresolved graph skill or metric IDs fail closed.
- apps_rg graph-skill authority does not move into `agentic_core`.

Suggested checks:

```powershell
python -m pytest tests\_apps_contract\test_apps_rg_c0_ownership_split.py `
  tests\_apps_contract\test_apps_rg_augmented_skills_graph_dual_source_all_sections.py `
  tests\unit\apps_rg\fact_inventory\test_augmented_skills_graph_sqlite.py `
  tests\unit\apps_rg\fact_inventory\test_metric_outcome_materializer.py -q
```

Known hygiene item:

- Deduplicate the duplicate `TestAgenticCoreGraphSkillBoundary` class in
  `tests/_apps_contract/test_apps_rg_c0_ownership_split.py`.

## Wave W-DIAG: Waterfall Diagnostic, Not Ship Blocker

Goal: keep graph-skill allocation analysis, but make it cheap and causal.

Keep:

- target x lane graph-skill allocation percentages.
- role family, role facet, pillar, source-fact family, employer scope, metric type.
- deltas versus prior stage and immutable Stage A.
- expected/unexpected variance labels for material changes.
- held-out cold targets for generalization.

Drop as a ship blocker:

- full live E2E at every conceptual stage.
- assembly-based utilization before `final_resume.json` exists.
- W3/W4/W5 waterfall requirements before the first `11/11` resume.

Required implementation shape:

- `tools/apps_rg/selection_diagnostic.py` or equivalent CLI emits selection-based
  graph-skill allocation without LLM generation.
- `tools/apps_rg/graph_skill_utilization_report.py` remains authoritative
  assembly-based reporting only after a successful final assembly.

Acceptance:

- Anthropic Stage B has an assembly-based graph utilization report.
- Five-target selection diagnostic can run without provider calls.
- Waterfall report labels material deltas as expected or unexpected.

## Wave S-PCT: Sliding-Scale Percent Policy

Goal: use sliding scale as a JD-aligned graph-skill composition control after
B-SHIP.

Sliding-scale percentages are not generic aesthetic balance. They must be
computed against JD-derived skill demand after that demand has been resolved to
GraphDB skill IDs:

1. Extract JD skill demand by lane and role family.
2. Resolve each demanded skill or skill family to GraphDB skill IDs.
3. Compute selected-skill percentage, source concentration, metric
   concentration, role-facet balance, and pillar balance against those resolved
   IDs.
4. Treat unresolved JD skill demand as a diagnostic failure until GraphDB
   coverage is expanded or the demand is explicitly out of scope.
5. Never let JD-only phrases bypass GraphDB eligibility.

### S1. Dry-Run Diagnostics

Compute, but do not enforce:

- JD-demand coverage percentage by lane.
- selected GraphDB skill percentage against JD-resolved demand.
- source concentration.
- metric concentration.
- role-facet and pillar balance.
- repeated concept family penalties.
- core-candidate preservation.

Acceptance:

- Diagnostics emitted per lane.
- Diagnostics identify JD-demanded GraphDB skills selected, missing, demoted, or
  blocked, with percentages based on GraphDB IDs rather than raw phrase counts.
- No selected skill IDs, selected metric IDs, ranking order, prompt inputs, lane
  status, generated text, or artifact hashes change because of dry-run diagnostics.

### S2. Active Enforcement

Only after S1 is stable:

- block or rebalance over-concentrated pools before prompt assembly when
  GraphDB-approved selections overfit one source, metric family, pillar, or role
  facet relative to JD-resolved skill demand.
- emit `REBALANCE_REQUIRED` when active policy intervenes.
- prove JD/briefing cannot create proof eligibility.

Acceptance:

- Anthropic and Brown & Brown full E2E pass under active enforcement.
- Sliding-scale interventions are visible in receipts and explainable in the
  waterfall report.
- Enforcement receipts show the JD-demand percentages, resolved GraphDB skill
  IDs, intervention reason, and unchanged rule that JD-only terms cannot create
  proof eligibility.

## Definition Of Done

The plan is complete when:

- `main` has a current Anthropic `11/11 X3_ALLOW` apps_rg run.
- Final resume JSON and DOCX exist for the run.
- `tools/apps_rg/render_run_summary.py` has rendered the successful run.
- GraphDB skills/metrics SSOT tests pass.
- A graph-skill utilization report exists for the successful run.
- Sliding-scale diagnostics are either explicitly deferred or proven dry-run with
  JD-demand percentages aligned to GraphDB skill IDs.
- The old `typed-edge-role-facet-guardrails-a6f3d2` plan is treated as historical
  context, not active execution status.

## Execution Markers

```text
WAVE_START: plan=apps-rg-11-lane-closeout-5f8c2a wave=<wave>
PHASE_COMPLETE: plan=apps-rg-11-lane-closeout-5f8c2a phase=<phase>
WAVE_COMPLETE: plan=apps-rg-11-lane-closeout-5f8c2a wave=<wave> note="<evidence>"
PLAN_COMPLETE: plan=apps-rg-11-lane-closeout-5f8c2a note="<final run + artifacts>"
```
