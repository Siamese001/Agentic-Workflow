---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\apps-rg-l7-auditability-wireup-b3c7e1.md'
original_relative_path: '_archive\\2026-05\\apps-rg-l7-auditability-wireup-b3c7e1.md'
source_sha256: 5052bf106abcb0118808398cce0862e89580d04cdd8e8085b29f741fd7fc6391
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# apps_rg L7 Auditability Wire-up

**Slug**: `apps-rg-l7-auditability-wireup-b3c7e1`
**Tier**: T2 (single-file edit in shared L4 entrypoint; behavior change propagates to every consumer of `run_integrated_r4_deterministic_pipeline`)
**Status**: Not Started
**Created**: 2026-05-06
**Authors**: Cursor Agent

PLAN_CREATED: slug=apps-rg-l7-auditability-wireup-b3c7e1 path=.cursor/plans/apps-rg-l7-auditability-wireup-b3c7e1.md tier=T2

## 1. Problem Statement

`apps_rg` runs (e.g. `artifacts/apps_rg/runs/20260506_125845/`) terminate without emitting any L7_AUDITABILITY plane artifacts. Specifically missing from every R4 run:

- `agentic_core_how_trace.json`
- `agentic_core_l7_route_family_coverage.json`
- `agentic_core_spine_proof.json`
- `integrated_runtime_artifact_manifest.json`
- `fortknox_l7_evidence/` directory (RTC-REQ-130..139 wrappers)

Per `agentic_core/L7_auditability/__init__.py:14`: *"The evidence plane is mandatory for every governed runtime run."* — this invariant is currently violated for the entire R4 chain family.

## 2. Root Cause

L7 emission is wired into TWO L4 entrypoints:

| Entrypoint | L7 emit site | Chain kinds covered |
|---|---|---|
| `agentic_core/runtime/entrypoints/integrated_managed_workflow_run.py` | lines 606–630 | `MANAGED_WORKFLOW`, `MANAGED_WORKFLOW_REAL_EXECUTION` |
| `agentic_core/runtime/entrypoints/integrated_safe_reuse_run.py` | lines 1184–1219 | `R1B`, `R1A_EXACT_CACHE`, `R5_FALLBACK`, `UWG_BLOCK_PATH`, `UWG_COMMIT_PATH`, `R3_GROUNDED_READ`, `R4_SINGLE_ACTION` |

A THIRD entrypoint exists that omits the L7 emit block:

- `agentic_core/runtime/entrypoints/integrated_r4_deterministic_pipeline_run.py` (declares `CHAIN_KIND = "R4_SINGLE_ACTION"` at line 92, never imports `build_how_trace`)

`apps_rg/__main__.py:349` is the only known caller of this third entrypoint. Result: every apps_rg run silently bypasses the auditability plane.

`build_how_trace` already accepts `R4_SINGLE_ACTION` in `_R1B_FAMILY` (`agentic_core/L7_auditability/how_trace/how_trace_builder.py:138-149`) — no builder change needed.

## 3. Goal & Non-Goals

**Goal**: Make L7 emission mandatory for every governed apps_rg run by adding the canonical emit block to `integrated_r4_deterministic_pipeline_run.py`. After this plan, an `apps_rg` run produces the four canonical L7 artifacts plus the Fort Knox L7 evidence wrapper directory.

**Non-Goals**:
- Migrate apps_rg from R4 deterministic pipeline to safe-reuse entrypoint (out-of-scope refactor).
- Promote runs to `SPINE_COMPLETE_CERTIFIED` end-to-end — that is the apps-e2e certification track, separate plan family (`apps_shared.spine_emission`).
- Add new L7 stages or modify `HowTrace` schema.
- Change `_R1B_FAMILY` membership in `how_trace_builder.py` (R4_SINGLE_ACTION already a member).
- Change apps_rg's call site in `apps_rg/__main__.py` — the entrypoint is the seam.
- Touch `integrated_managed_workflow_run.py` or `integrated_safe_reuse_run.py` — already wired correctly.
- Run Fort Knox certification compile against the new artifacts (separate downstream plan).

## 4. Scope (Files In Scope)

| File | Change Type | Justification |
|---|---|---|
| `agentic_core/runtime/entrypoints/integrated_r4_deterministic_pipeline_run.py` | EDIT | Add L7 emit block (HOW trace + coverage matrix + manifest cross-ref). |
| `tests/unit/agentic_core/runtime/entrypoints/test_integrated_r4_l7_emit.py` | NEW | Regression test that an R4 run produces all 4 L7 artifacts. |

Out of scope (read-only context): `agentic_core/L7_auditability/**`, `apps_rg/__main__.py`, `agentic_core/runtime/entrypoints/integrated_managed_workflow_run.py`, `agentic_core/runtime/entrypoints/integrated_safe_reuse_run.py`.

## 5. ADG_HOTSPOT_REPORT

| Node | Layer | Archetype | Fan-in | Fan-out | Surface | Justification |
|---|---|---|---|---|---|---|
| `integrated_r4_deterministic_pipeline_run` | L4 (state) | ORCHESTRATOR | apps_rg (1 known); other apps may follow | calls L0/L1/L2/L3 emitters, writes artifact dir | Observability + Write | Fan-in expected to grow as additional apps adopt R4 single-action chain. Missing L7 emit silently breaks downstream Fort Knox proofs (RTC-REQ-130..139). Layer multiplier ×1.75 (L4 state). Impact = 1 violation × (1 + log10(2)) × 1.75 ≈ 2.3 — modest, but the Observability surface intersection raises the priority because silent skip of the evidence plane is by definition unobservable from runtime telemetry. |

Hotspot is the entrypoint itself. The fix removes one P-class concern (`mandatory L7 emit absent`) from one node.

## 6. ADG_GRAPH_LAYER_EVIDENCE

Querying ADG MCP at plan-write time (snapshot `artifacts/adg/adg_indexed_<latest>.sqlite`):

- `mv_graph_chokepoint_bridges` — `integrated_r4_deterministic_pipeline_run` is the bridge between apps_rg's transport layer and the L0–L3 governed substrate. Adding L7 emit at the bridge propagates to every consumer without per-app code change.
- `mv_dependency_cone_risk` — apps_rg is the documented consumer; ADG shows zero downstream Fort Knox bindings for this entrypoint, confirming the gap.
- `mv_hotspot_centrality` — degree centrality of the three R4 entrypoints is comparable; the two safe-reuse and managed-workflow entrypoints show edges to `agentic_core.L7_auditability.how_trace.how_trace_builder.build_how_trace`; the deterministic-pipeline entrypoint does not.
- Semantic edges (`emits_side_effect`): the two wired entrypoints have `emits_side_effect → agentic_core_how_trace.json`; the deterministic-pipeline entrypoint has none.
- `v_p1_evidence_plane_gaps` (P1 view) — confirms `integrated_r4_deterministic_pipeline_run` as the only L4 entrypoint missing the canonical L7 emit pair.

ADG Provenance: backend=sqlite, snapshot=adg_indexed_<latest>.sqlite. Live ADG queries to be re-confirmed at execution time before edits.

## 7. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| W1 | P1.1, P1.2, P1.3 | L7 emit block added to R4 entrypoint; unit test added; one live apps_rg run validates artifacts on disk | ~6k | `build_how_trace(chain_kind="R4_SINGLE_ACTION")` works as-is; `_emit` helper exists in R4 entrypoint with same signature as in the two siblings; artifact_dir is the same shape | Not Started | All 4 L7 artifacts present in next apps_rg run; unit test green; no regression in any existing apps_rg test |

Single-wave plan — scope is one targeted edit plus a regression test plus one live verification run.

## 8. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| P1.1 | Add L7 emit block to R4 entrypoint | `agentic_core/runtime/entrypoints/integrated_r4_deterministic_pipeline_run.py` | (a) Locate the existing `_emit(...)` helper and the post-chain seal point; (b) replicate the 30-line block from `integrated_safe_reuse_run.py:1184-1219` verbatim with `chain_kind="R4_SINGLE_ACTION"`; (c) ensure the block runs AFTER all chain artifacts are written (HOW trace is a projection over them); (d) preserve fail-loud semantics — if `build_how_trace` raises `ValueError("required artifacts missing")`, surface it, do not swallow. | ~3k | Not Started |
| P1.2 | Regression test | `tests/unit/agentic_core/runtime/entrypoints/test_integrated_r4_l7_emit.py` (new) | Build a minimal fake artifact_dir with the chain artifacts `build_how_trace` requires (identity, route, manifest), invoke the R4 entrypoint or just the L7 emit branch in isolation, assert `agentic_core_how_trace.json` and the three siblings exist with non-empty JSON. Mirror the test pattern in `tests/unit/agentic_core/runtime/entrypoints/test_integrated_safe_reuse_l7_emit.py` if it exists; otherwise mirror the assertion shape used by `ops_scripts/ci/verify_agentic_core_how_trace.py`. | ~2k | Not Started |
| P1.3 | Live verification | `python -m apps_rg --target-company <test> --target-role <test> --jd <fixture> --manual-brief <fixture>` | Re-run apps_rg end-to-end against a fixture brief/JD; confirm new run dir contains the 4 canonical L7 artifacts; spot-check `agentic_core_how_trace.json` payload shape against `agentic_core/L7_auditability/contracts/how_trace.py`. | ~1k | Not Started |

## 9. Verification

After P1.3:

```powershell
$run = (Get-ChildItem artifacts\apps_rg\runs | Sort-Object Name -Descending | Select-Object -First 1).FullName
Get-ChildItem $run -Filter "agentic_core_*.json"
Get-ChildItem $run -Filter "integrated_runtime_artifact_manifest.json"
Test-Path "$run\fortknox_l7_evidence"
```

Expected: `agentic_core_how_trace.json`, `agentic_core_l7_route_family_coverage.json`, `agentic_core_spine_proof.json`, `integrated_runtime_artifact_manifest.json` all present.

CI gates that should now pass for the run:

- `ops_scripts/ci/verify_agentic_core_how_trace.py`
- `ops_scripts/ci/verify_agentic_core_l7_route_family_coverage.py`
- `ops_scripts/ci/verify_l7_fortknox_evidence.py` (after Fort Knox emitter is run, optional — not in this plan's scope)

## 10. Risk & Rollback

**Risk**: Low. The change is additive — a new emit block at the end of an existing entrypoint. If `build_how_trace` raises on a malformed chain (legitimately broken upstream artifacts), the run will fail loudly instead of silently completing without L7 evidence. This is the desired fail-closed semantic per `L7_auditability/__init__.py:14`.

**Rollback**: Revert the single-file edit. No schema migrations, no Notion-stateful changes, no hash-bound artifacts mutated.

## 11. Author-Gate Decisions Foreseen

None expected — the fix is mechanical replication of an established pattern. Should an Author-Gate emerge during P1.1 (e.g. divergent `_emit` signature in R4 entrypoint), it will be surfaced before code change.

## 12. References

- `agentic_core/L7_auditability/__init__.py` — plane invariant
- `agentic_core/L7_auditability/how_trace/how_trace_builder.py:114-149` — accepted chain kinds
- `agentic_core/runtime/entrypoints/integrated_safe_reuse_run.py:1184-1219` — reference implementation
- `agentic_core/runtime/entrypoints/integrated_managed_workflow_run.py:606-630` — second reference
- `apps_rg/__main__.py:66-68, 349-352` — current call site
- `tools/cert/emit_l7_plane_evidence.py` — RTC-REQ-130..139 binder (downstream consumer)
- ADR-080 (Phase D auditability) — design anchor
- ADR-050 (intelligence-ledger-family) — cross-cutting evidence plane discipline
- Constitutional §32 (Fort Knox certification integrity)

## 13. Non-Implementation Notice

**This plan is registered with Notion but NOT yet executed.** Wave execution requires a separate explicit user authorization. Per constitutional §36, no `wave_execution_state.py start` will be called until the user approves W1 to begin.
