# Graph Skills SQLite Runtime Redesign

Plan ID: `graph-skills-sqlite-runtime-redesign-a4c9e2`
Status: Implemented
Created: 2026-06-25
Owner: Codex

## Objective

Move apps_rg C0.3 graph-skills selection from Python-side JSON/context binding toward deterministic SQLite-backed traversal, reverse lookup, ranking, metric diversity, and rejected-sibling receipts while keeping `apps_rg/fact_inventory/master_skills_arsenal_ledger.json` as the reviewable canonical graph source.

## Constraints

- Do not make the generated `.sqlite` binary the canonical source of truth.
- Keep graph rows as routing/context support, not claim proof.
- Preserve `master_skills_arsenal_ledger.json` as canonical source and `augmented_skills_graph.sqlite` as deterministic runtime projection.
- Do not introduce a parallel C0 engine or broad GraphRAG rewrite.
- Do not alter unrelated C0.2 vector-readiness work.
- Fail closed on unresolved role-family projection, missing graph DB, unresolved metric outcome rows, or stale/invalid materialization.
- Preserve original C0.2 atoms unchanged; C0.3 may bind, rank, reject, and receipt but must not mint facts.

## Status Tables

### Wave Progress

| Wave | Scope | Status | Exit Evidence |
|---|---|---|---|
| W0 | Evidence, ADG scope, and plan approval | DONE | Plan approved by user |
| W1 | SQLite projection schema and deterministic query surface | DONE | Materialization tests pass |
| W2 | Runtime C0.3 selection/ranking integration | DONE | C0.3 runtime tests pass |
| W3 | Receipts, guardrails, and verification | DONE | Focused pytest + validation scripts pass |

### Phase Progress

| Phase | Task | Status |
|---|---|---|
| W0.1 | Restore/prove MCP transports | DONE |
| W0.2 | Confirm ADG scope and consumers | DONE |
| W0.3 | Present plan for approval | DONE |
| W1.1 | Add SQLite projection rows/table for skill selection features | DONE |
| W1.2 | Add SQLite indexes/validation for reverse fact/skill/metric lookup | DONE |
| W1.3 | Test deterministic materialization and source-review boundary | DONE |
| W2.1 | Add C0.3 SQLite query/ranking module | DONE |
| W2.2 | Wire `expand_c03_graph_bindings` to SQLite-ranked candidates | DONE |
| W2.3 | Emit selected and rejected sibling/metric receipts | DONE |
| W3.1 | Add runtime tests for ranking, penalties, and receipts | DONE |
| W3.2 | Run focused pytest and graph hardening validation | DONE |
| W3.3 | Record closeout receipt if implementation succeeds | DONE |

## Dependency Graph

ADG Provenance: backend_used=sqlite, query_count=12, cache_hits=0, snapshot=`adg_indexed_06242026_2303.sqlite`.

Graph roots:

- `apps_rg/fact_inventory/augmented_skills_graph_sqlite.py`
- `apps_rg/runtime/c0/c03_graph_expansion.py`
- `apps_rg/runtime/c03_graph_sqlite_context.py`
- `apps_rg/runtime/c0/c03_graph_ref_policy.py`
- `apps_rg/fact_inventory/metric_outcome_materializer.py`

Impacted consumers:

- `apps_rg/runtime/c0/evidence_room.py`
- `tests/_apps_contract/test_apps_rg_c0_ownership_split.py`
- `tests/unit/apps_rg/runtime/c0/test_exec_summary_graph_shaping.py`
- `tests/unit/apps_rg/fact_inventory/test_augmented_skills_graph_sqlite.py`
- `tests/unit/apps_rg/fact_inventory/test_metric_outcome_materializer.py`
- `tools/apps_rg/c03_partner_ade_calibration.py`
- `tools/apps_rg/c0_evidence_room_stress.py`

Boundary findings:

- Existing C0.3 entrypoint is `expand_c03_graph_bindings`, not a new generic C0 engine.
- Existing SQLite context is already routing/context support and not claim proof.
- Existing runtime path still performs material binding in Python after querying a broad SQLite context bundle; W2 should move selection and rejection decisions into a deterministic SQLite-backed query/ranking layer.
- `master_skills_arsenal_ledger.json` already contains C0.3 hardening rows for metric heterogeneity, reverse traversal, and sibling rejection receipts. The redesign should consume that signal in the runtime query layer rather than appending duplicate concepts.

## Scope Declaration

Files expected to modify:

1. `apps_rg/fact_inventory/augmented_skills_graph_sqlite.py` - add deterministic projection support for runtime selection features and validation.
2. `apps_rg/runtime/c03_graph_sqlite_context.py` - expose a tighter SQLite context/query surface for selected facts, metric buckets, and rejected siblings.
3. `apps_rg/runtime/c0/c03_graph_expansion.py` - consume SQLite-ranked graph candidates while preserving the existing public entrypoint.
4. `apps_rg/runtime/c0/c03_sqlite_graph_selection.py` - new focused runtime query/ranking helper, if no existing helper can absorb the logic cleanly.
5. `tests/unit/apps_rg/fact_inventory/test_augmented_skills_graph_sqlite.py` - materialization/schema/query tests.
6. `tests/unit/apps_rg/runtime/c0/test_c03_sqlite_graph_selection.py` - new ranking, diversity, reverse traversal, and receipt tests.
7. `tests/unit/apps_rg/runtime/c0/test_exec_summary_graph_shaping.py` - regression coverage for the public C0.3 entrypoint.

Baseline: GitKraken and `git status --short --branch` initially reported a clean working tree on `codex/publish-c0-authority-profile-20260625`.

Closeout note: post-implementation status also includes unrelated headline/X2/prompt working-tree edits outside this plan scope. They were not changed by the graph-skills SQLite redesign.

## Pre Code Gate

Changed surfaces:

- `materialize_augmented_skills_graph_sqlite`
- `validate_materialized_sqlite`
- `assemble_c03_graph_sqlite_context`
- `expand_c03_graph_bindings`
- new SQLite ranking/query helper

Existing coverage:

- `tests/unit/apps_rg/fact_inventory/test_augmented_skills_graph_sqlite.py`
- `tests/unit/apps_rg/fact_inventory/test_metric_outcome_materializer.py`
- `tests/unit/apps_rg/runtime/c0/test_exec_summary_graph_shaping.py`
- `tests/unit/apps_rg/test_c03_graph_skills_mvp.py`

Required new tests:

- SQLite projection exposes skill selection features without making SQLite canonical.
- Reverse lookup ranks `skill -> fact` and `fact -> skill` candidates deterministically.
- Repeated metric bucket/fact/skill-family penalties change ranking predictably.
- Rejected siblings are retained with reason codes.
- Public `expand_c03_graph_bindings` preserves original atoms and emits graph metrics/receipts.
- Materialization remains idempotent and source-reviewable from JSON.

## Implementation Plan

### W1 - SQLite Projection

1. Add a compact projection table or view for skill selection features, sourced from canonical skill rows and existing graph rows.
2. Include enough columns for ranking: `skill_id`, `pillar`, `metric_bucket`, `confidence`, `external_eligible`, `support_level`, and source authority.
3. Add indexes for reverse lookup by fact, skill, section, metric bucket, and role-family/pillar where available.
4. Extend validation so projection rows reconcile with graph node/skill fact link counts and fail closed on orphaned rows.

### W2 - Runtime Query And Ranking

1. Add a focused SQLite query helper for C0.3 selection.
2. Query candidates through SQLite joins across `skill_fact_links`, `graph_nodes`, `section_eligibility`, `role_family_projection`, and metric-outcome rows where applicable.
3. Rank with deterministic components: direct fact support, claim eligibility, pillar/role-family fit, proof strength, metric novelty, section fit, and penalties for repeated fact/metric/skill family.
4. Return selected candidates plus rejected sibling candidates with reason codes.
5. Wire `expand_c03_graph_bindings` to the helper while keeping the existing function signature backward compatible.

### W3 - Receipts And Verification

1. Emit selection metrics in the C0.3 output: selected skill count, rejected sibling count, metric bucket counts, repeated penalties applied, and SQLite graph version/hash.
2. Preserve `graph_context_ref`, `new_atoms_created=0`, and existing section-local proof classification.
3. Run focused tests and `apps_rg/fact_inventory/validate_c03_graph_hardening.py`.
4. If successful, write a closeout receipt under `docs/reports/apps_rg/`.

## Verification Commands

```powershell
python apps_rg/fact_inventory/validate_c03_graph_hardening.py
python -m pytest tests/unit/apps_rg/fact_inventory/test_augmented_skills_graph_sqlite.py tests/unit/apps_rg/fact_inventory/test_metric_outcome_materializer.py tests/unit/apps_rg/runtime/c0/test_exec_summary_graph_shaping.py tests/unit/apps_rg/runtime/c0/test_c03_sqlite_graph_selection.py tests/unit/apps_rg/test_c03_graph_skills_mvp.py -q
python scripts/governance/codex_readiness.py --json
```

## Closeout Evidence

Closeout receipt: `docs/reports/apps_rg/graph_skills_sqlite_runtime_redesign_a4c9e2_receipt.json`

Focused verification:

- `python -m pytest tests/unit/apps_rg/fact_inventory/test_augmented_skills_graph_sqlite.py tests/unit/apps_rg/runtime/c0/test_c03_sqlite_graph_selection.py -q` -> `20 passed, 1 warning`
- `python -m pytest tests/unit/apps_rg/fact_inventory/test_augmented_skills_graph_sqlite.py tests/unit/apps_rg/fact_inventory/test_metric_outcome_materializer.py tests/unit/apps_rg/runtime/c0/test_exec_summary_graph_shaping.py tests/unit/apps_rg/runtime/c0/test_c03_sqlite_graph_selection.py tests/unit/apps_rg/test_c03_graph_skills_mvp.py -q` -> `43 passed, 1 warning`
- `python apps_rg/fact_inventory/validate_c03_graph_hardening.py` -> PASS, `distinct_metric_buckets=11`, `max_same_metric_bucket_share=0.3151`
- `git diff --check -- <graph-skill changed files>` -> no whitespace errors; Git reported CRLF conversion notices only
- `python scripts/governance/codex_readiness.py --json` -> WARN only: dirty working tree advisory, duplicate MCP cohort advisory, and major exposure audit yellow

Broader generated-lane E2E probe:

- `python -m pytest tests/unit/apps_rg/fact_inventory/test_metric_outcome_materializer.py tests/unit/apps_rg/runtime/c0/test_exec_summary_graph_shaping.py tests/unit/apps_rg/test_c03_graph_skills_mvp.py tests/unit/apps_rg/test_c0_evidence_room.py tests/_apps_contract/test_c0_evidence_room_generated_lanes_e2e.py -q` -> 60 passed, 2 failed. The failures occur before C0.3 graph expansion in proof-pool depth checks for `executive_summary` and `headline`, so they are tracked as unrelated baseline/generated-lane evidence depth failures.

## Definition Of Done

| Requirement | Done When |
|---|---|
| SQLite is runtime query layer | C0.3 selection/ranking uses SQLite-backed query helper |
| JSON remains canonical | Materialization and receipts state JSON ledger is source and SQLite is generated |
| Reverse traversal works | Tests prove fact/skill reverse lookup and rejected sibling receipts |
| Metric repetition reduced | Tests prove metric bucket/fact/skill repeat penalties are deterministic |
| No new facts minted | C0.3 output preserves original atoms and reports `new_atoms_created=0` |
| Tests pass | Focused pytest and graph hardening validation pass |

## Risks And Stop Conditions

- Stop if implementation would require broad C0/C0.4/L2 API changes.
- Stop if existing materialization has drifted from the current canonical JSON.
- Stop if ranking needs runtime history not available in C0.3 input; add optional history input only if backward compatible.
- Stop if tests reveal existing unrelated failures outside the declared scope.

## Approval Gate

Implementation must not start until this plan is approved in the Codex thread.
