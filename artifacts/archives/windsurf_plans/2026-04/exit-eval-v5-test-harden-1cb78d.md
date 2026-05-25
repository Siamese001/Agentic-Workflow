# Plan: Exit-Eval v5 — Finish Open Scope + Test Hardening

- **Plan ID**: `exit-eval-v5-test-harden-1cb78d`
- **Parent**: `.windsurf/plans/exit-eval-v5-gap-c0aa47.md` (commit `171ad27e8d`)
- **Tier**: T2 (L3 factory + tests only)
- **ADG snapshot**: `artifacts/adg/adg_indexed_04252026_0843.sqlite`
- **Status**: Active

## SR_INTAKE

Parent plan closed gaps 1–5 and landed X1G's rubric file + store-level wiring. Three follow-ups remain:

1. **Factory X1G gap** — `factory.build_pipeline(["X1A","X1G"])` raises `KeyError: unknown gate 'X1G'` because `_build_graders_for_gate` has no X1G branch (X1G is pipeline-level, not gate-level). Callers who pass `"X1G"` in `gate_ids` get a confusing error. Resolution: treat `"X1G"` as a *pipeline-policy enable* flag that requires `consistency_store` + `consistency_policy` to be supplied; do not build a Gate for it.
2. **`bucket_key_from_context` is not exercised by existing tests** — harden.
3. **Break-glass envelope** does not explicitly include v5 reason codes when mandatory-deny fires — harden with a parity test.

## Verified surface

- `@c:/Git/Agentic-Workflow/agentic_core/L3_orchestration/exit_eval/consistency.py:47-56` — `BucketKey` already keys by `trajectory_class` (v5 §X1G satisfied at store level).
- `@c:/Git/Agentic-Workflow/agentic_core/L3_orchestration/exit_eval/factory.py:215-224` — factory loop unconditionally calls `_build_graders_for_gate` for every id → X1G gap.
- `@c:/Git/Agentic-Workflow/agentic_core/L3_orchestration/exit_eval/pipeline.py` — consistency already consulted only when `consistency_store` supplied and `commit_candidate=True`.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|---|---|---|---|---|---|
| F1 | F1.1 | Factory X1G handling | ~1500 | Todo | `build_pipeline(["X1A","X1G"], consistency_store=s, consistency_policy=p)` returns bundle with 1 Gate + consistency wired; missing store raises clear error |
| F2 | F2.1 F2.2 F2.3 | Hardening tests | ~3000 | Todo | ≥7 new tests; all pass |
| F3 | F3.1 | Commit + push | ~500 | Todo | Pushed to origin/main |

## Phase-Level Summary

| Phase ID | Title | Scope | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| F1.1 | X1G enable-flag semantics in build_pipeline | `agentic_core/L3_orchestration/exit_eval/factory.py` | Must preserve back-compat: `X1A..X1F` still work exactly as before | 1500 | Todo |
| F2.1 | Factory X1G tests | `tests/agentic_core/L3_orchestration/exit_eval/test_factory_x1g.py` (new) | Stub BusEmitter + PassKStore | 1000 | Todo |
| F2.2 | bucket_key_from_context tests | `tests/agentic_core/L3_orchestration/exit_eval/test_consistency.py` (extend or new file) | None | 800 | Todo |
| F2.3 | Break-glass v5 reason-code tests | extend `tests/.../exit_eval/test_v5_parity.py` | Uses existing pipeline fixtures | 1200 | Todo |
| F3.1 | Commit + push | git | None | 500 | Todo |

## Out of Scope (remaining next-steps)

- BUS T golden-set promotion pipeline
- Judge calibration cadence automation (covered by `judge-calibration-cadence.md` rule)
- Sandbox capability-token rotation policy

## ADG_HOTSPOT_REPORT

| Rank | File | Layer | Archetype | Surface | Fan-in | Impact | Wave |
|---|---|---|---|---|---|---|---|
| 1 | `factory.py` | L3 | CENTRAL_DEPENDENCY | Execution | medium | 0.7 | F1 |
| 2 | `consistency.py` | L3 | STATE_NODE | State | medium | 0.5 | F2 |

## ADG_GRAPH_LAYER_EVIDENCE

- `mv_exit_disposition_coverage` — X3B/INSUFFICIENT_HISTORY path coverage unchanged.
- `mv_eval_coverage_by_path` — factory.py currently well-tested; new X1G branch must not reduce line coverage.
- `mv_hitl_reclearance_gaps` — unaffected.
- Semantic edges: `flows_to` from `build_pipeline` → `EvaluationPipeline`; new branch must preserve the edge direction.
- P-views: no new `v_p0_*`/`v_p1_*` matches expected.
