---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\apps-l7-coverage-spine-wide-c5e8d2.md'
original_relative_path: 'apps-l7-coverage-spine-wide-c5e8d2.md'
source_sha256: 7ddd5d7359feda92a0487a96bb86543ffe5a9fdb9c302f0bea74347598ca46b5
recovered_status: SURVIVED_IN_CURRENT
last_commit: '153652b9eb3'
last_commit_date: '2026-06-07 06:37:48 -0400'
created_date: '2026-05-06'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Apps L7 Auditability Coverage — Spine-Wide Umbrella

**Slug**: `apps-l7-coverage-spine-wide-c5e8d2`
**Tier**: T3 (cross-cutting; touches 3 L4 entrypoints + 1 shared spine emitter; affects 7 production apps)
**Status**: Not Started
**Created**: 2026-05-06
**Authors**: Cursor Agent
**Supersedes**: `apps-rg-l7-auditability-wireup-b3c7e1` (absorbed as W1)

PLAN_CREATED: slug=apps-l7-coverage-spine-wide-c5e8d2 path=.windsurf/plans/apps-l7-coverage-spine-wide-c5e8d2.md tier=T3

## 1. Problem Statement

L7_AUDITABILITY (`agentic_core/L7_auditability/__init__.py:14`) declares itself "mandatory for every governed runtime run". Currently emitted by 3 of 11 L4 entrypoints, and 0 of 8 production apps_* runs produce any L7 artifacts on their primary code path.

| Path | L7 today | Affected apps |
|---|:---:|---|
| `integrated_safe_reuse_run` (R1B family + R4 + R3 + UWG_*) | yes | (probes / cert harness only) |
| `integrated_managed_workflow_run` | yes | (probes / cert harness only) |
| `integrated_grounded_read_run` | yes | (probes only) |
| `integrated_single_action_spine_run` | NO | `apps_rg` |
| `integrated_r4_lic_pipeline_run` | NO | `apps_lic` (direct path) |
| `apps_shared.spine_emission.governed_run` | NO | `apps_qna`, `apps_research`, `apps_rfp`, `apps_underwriting_ai`, `apps_lic` (governed path) |
| (no spine wrapping at all) | NO | `apps_eval`, `apps_repo_brief` |

This plan closes the gap for the 7 spined production apps. The 2 unspined apps are deferred via DEFERRED_SCOPE markers (see Section 13).

## 2. Architectural Choice (Author-Gate decision 2026-05-06)

Two parallel artifact-emission tracks exist:

- **Track 1** — `apps_shared.spine_emission.governed_run` emits 10 canonical receipts under `artifacts/<app>/runs/<ts>/`. Consumed by `apps_e2e` proof producers for `SPINE_COMPLETE_CERTIFIED`.
- **Track 2** — `integrated_safe_reuse_run` / `integrated_managed_workflow_run` emit 17+ chain artifacts under `artifacts/certification/integrated_runtime/<chain>/`. Consumed by Fort Knox runtime certification (RTC-REQ-130..139).

`build_how_trace` reads Track-2 filenames (`runtime_identity_envelope.json`, `compiled_prompt_artifact.json`, `l2_sealed_artifact.json`, `runtime_trace_snapshot.json`). Track-1 emits different filenames (`u0_intake_envelope.json`, `prompt_assembly_manifest.json`, `l2_execution_receipt.json`, `otel_runtime_trace.json`).

**Chosen approach (Option A — alias-and-emit)**: at the end of `GovernedRun.emit_post_execution_contracts`, write canonical Track-2 filename aliases as content-identical sibling files, then invoke `build_how_trace` with `chain_kind="R4_SINGLE_ACTION"`. CI verifier asserts alias and source remain byte-identical (no drift).

Rejected:
- **Option B** (separate builder): doctrinal split + maintenance cost
- **Option C** (extend builder with auto-detect): bloats the L7 SSOT
- **Option D** (declare governed_run out-of-scope, ADR amends "mandatory"): doctrinal regression

## 3. Goal & Non-Goals

**Goal**: every governed `apps_*` run going through `governed_run`, `integrated_single_action_spine_run`, or `integrated_r4_lic_pipeline_run` emits the four canonical L7 artifacts: `agentic_core_how_trace.json`, `agentic_core_l7_route_family_coverage.json`, `agentic_core_spine_proof.json`, `integrated_runtime_artifact_manifest.json`. The constitutional invariant becomes true for 7 of 8 production apps.

**Non-Goals**:
- Wire `apps_eval` and `apps_repo_brief` into governed_run (deferred — see Section 13).
- Run Fort Knox certification compile against the new artifacts (downstream plan).
- Modify `build_how_trace` input contract — Option C explicitly rejected.
- Modify `integrated_safe_reuse_run`, `integrated_managed_workflow_run`, or `integrated_grounded_read_run` — already wired.
- Migrate `apps_rg` from R4 deterministic pipeline to safe-reuse entrypoint.
- Add new L7 stages or modify HowTrace schema.
- Promote any run to `SPINE_COMPLETE_CERTIFIED` end-to-end.

## 4. Scope — Files In Scope

### Wave 1 — apps_rg (R4 deterministic pipeline)
- `agentic_core/runtime/entrypoints/integrated_single_action_spine_run.py` — EDIT
- `tests/unit/agentic_core/runtime/entrypoints/test_integrated_r4_l7_emit.py` — NEW

### Wave 2 — apps_lic direct (R4 lic pipeline)
- `agentic_core/runtime/entrypoints/integrated_r4_lic_pipeline_run.py` — EDIT
- `tests/unit/agentic_core/runtime/entrypoints/test_integrated_r4_lic_l7_emit.py` — NEW

### Wave 3 — governed_run alias-and-emit
- `apps_shared/spine_emission/context.py` — EDIT (`GovernedRun.emit_post_execution_contracts`)
- `apps_shared/spine_emission/_l7_alias_map.py` — NEW (Track-1 to Track-2 filename map; pure helper)
- `tests/unit/apps_shared/spine_emission/test_governed_run_l7_emit.py` — NEW
- `tests/unit/apps_shared/spine_emission/test_l7_alias_map_integrity.py` — NEW (byte-identical assertion)
- `ops_scripts/ci/check_governed_run_l7_alias_drift.py` — NEW (advisory CI gate; bypass `GOVERNED_RUN_L7_ALIAS_BYPASS=1`)

Out of scope (read-only context): `agentic_core/L7_auditability/**`, `apps_*/**`, the three L7-wired entrypoints, `tools/cert/emit_l7_plane_evidence.py`, `apps_e2e/**`.

## 5. ADG_HOTSPOT_REPORT

| Node | Layer | Archetype | Fan-in | Fan-out | Surface | Justification |
|---|---|---|---|---|---|---|
| `apps_shared.spine_emission.context.GovernedRun.emit_post_execution_contracts` | L4 (state) | CENTRAL_DEPENDENCY | 5+ apps via `governed_run` ctx mgr (apps_qna, apps_research, apps_rfp, apps_underwriting_ai, apps_lic) | writes 10 canonical receipts | Write + Observability + State | Highest-fan-in node. Single edit covers 5 apps. Multiplier x1.75 (L4). Impact = 1 * (1 + log10(6)) * 1.75 ~= 3.1 |
| `integrated_single_action_spine_run` | L4 (state) | ORCHESTRATOR | apps_rg (1 known) | L0/L1/L2/L3 emitters | Observability + Write | Direct entrypoint; missing emit silently violates `__init__.py:14` |
| `integrated_r4_lic_pipeline_run` | L4 (state) | ORCHESTRATOR | apps_lic (1 known) | similar | Observability + Write | Verbatim fix shape mirrors W1 |

5-Surfaces: all three intersect **Observability** (silent evidence-plane drop is unobservable from runtime telemetry) and **Write** (artifact emission). The governed_run hotspot additionally intersects **State** (owns run-dir state machine).

## 6. ADG_GRAPH_LAYER_EVIDENCE

ADG queries against `artifacts/adg/adg_indexed_<latest>.sqlite` (provenance to be re-confirmed at execution time before edits):

- `mv_graph_chokepoint_bridges` — `GovernedRun.emit_post_execution_contracts` is the bridge between every spined app and the canonical receipt set. Fix at bridge propagates without per-app changes.
- `mv_graph_reverse_dependency_hotspots` — `governed_run` ranks high; the 5 apps using it represent the largest cohort of production runs.
- `mv_dependency_cone_risk` — apps_rg + apps_lic + governed_run cone shows zero downstream `build_how_trace` edges, confirming the gap.
- `mv_hotspot_centrality` — degree centrality of the three R4-class entrypoints (`safe_reuse`, `managed_workflow`, `r4_deterministic_pipeline`, `r4_lic_pipeline`) is comparable; only the first two have edges to `agentic_core.L7_auditability.how_trace.how_trace_builder.build_how_trace`.
- Semantic edges (`emits_side_effect`): the two L7-wired entrypoints have `emits_side_effect -> agentic_core_how_trace.json`; the two R4 entrypoints and `governed_run` have none.
- `v_p1_evidence_plane_gaps` — confirms the four target nodes as the only L4 governed-run-shaped surfaces missing the canonical L7 emit pair.

ADG Provenance: backend=sqlite, snapshot=adg_indexed_<latest>.sqlite. Live ADG queries to be re-confirmed at execution time.

## 7. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| W1 | P1.1, P1.2, P1.3 | apps_rg L7 wireup via R4 deterministic pipeline entrypoint | ~6k | `build_how_trace(chain_kind="R4_SINGLE_ACTION")` works as-is; `_emit` helper exists in R4 entrypoint with same signature as siblings | Not Started | All 4 L7 artifacts present in next apps_rg run; new unit test green; zero apps_rg regression |
| W2 | P2.1, P2.2, P2.3 | apps_lic L7 wireup via R4 lic pipeline entrypoint | ~5k | R4 lic entrypoint has matching `_emit` shape; chain_kind="R4_SINGLE_ACTION" valid for lic chain | Not Started | All 4 L7 artifacts present in next apps_lic direct-path run; new unit test green; zero apps_lic regression |
| W3 | P3.1, P3.2, P3.3, P3.4 | governed_run alias-and-emit (covers 5 apps) | ~12k | Track-1 receipts content-equivalent to Track-2 expectations after alias map; build_how_trace tolerates the aliased shape | Not Started | All 5 governed apps emit 4 L7 artifacts on next run; alias-drift CI gate passes; integrity test asserts byte-identical alias-source pairs; smoke test on each of the 5 apps green |

3 sequential waves. W1 must land first to validate the verbatim-replication pattern before W2 mirrors it. W3 is the larger architectural change and benefits from W1+W2 establishing the reference implementation.

## 8. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| P1.1 | Add L7 emit block to R4 deterministic entrypoint | `integrated_single_action_spine_run.py` | Locate the existing `_emit(...)` helper and the post-chain seal point; replicate the 30-line block from `integrated_safe_reuse_run.py:1184-1219` verbatim with `chain_kind="R4_SINGLE_ACTION"`; ensure block runs AFTER all chain artifacts are written; preserve fail-loud semantics. | ~3k | Not Started |
| P1.2 | Regression test for W1 | `tests/unit/agentic_core/runtime/entrypoints/test_integrated_r4_l7_emit.py` (new) | Build minimal fake artifact_dir with chain artifacts `build_how_trace` requires (identity, route, manifest); invoke entrypoint or L7 branch in isolation; assert all 4 L7 artifacts exist with non-empty JSON. | ~2k | Not Started |
| P1.3 | Live verification W1 | `python -m apps_rg --target-company <test> --target-role <test> --jd <fixture> --manual-brief <fixture>` | Re-run apps_rg; confirm new run dir contains 4 L7 artifacts; spot-check `agentic_core_how_trace.json` against `agentic_core/L7_auditability/contracts/how_trace.py`. | ~1k | Not Started |
| P2.1 | Add L7 emit block to R4 lic entrypoint | `integrated_r4_lic_pipeline_run.py` | Same shape as P1.1; verify R4 lic uses identical `_emit` signature; if it does not, surface as Author-Gate before proceeding. | ~2k | Not Started |
| P2.2 | Regression test for W2 | `tests/unit/agentic_core/runtime/entrypoints/test_integrated_r4_lic_l7_emit.py` (new) | Mirror P1.2 for lic chain. | ~2k | Not Started |
| P2.3 | Live verification W2 | `python -m apps_lic --apps-e2e-live <args>` | Re-run apps_lic direct-path; confirm 4 L7 artifacts. | ~1k | Not Started |
| P3.1 | Author alias map module | `apps_shared/spine_emission/_l7_alias_map.py` (new) | Pure helper exporting `TRACK1_TO_TRACK2_FILENAMES` dict and a `write_aliases(run_dir)` function that copies bytes from each Track-1 source to its Track-2 alias name; explicit, no symlinks. Failure to find a Track-1 source raises ValueError (fail-loud). | ~2k | Not Started |
| P3.2 | Wire alias write + L7 emit into governed_run | `apps_shared/spine_emission/context.py` (`emit_post_execution_contracts`) | After all 10 canonical receipts written and BEFORE the method returns, call `write_aliases(run_dir)` then `build_how_trace(run_dir, chain_kind="R4_SINGLE_ACTION")`, then write the 4 L7 artifacts. Wrap in try/except ValueError to surface fail-loud diagnostics; do NOT swallow. | ~4k | Not Started |
| P3.3 | Tests + CI gate | `test_governed_run_l7_emit.py`, `test_l7_alias_map_integrity.py`, `check_governed_run_l7_alias_drift.py` | (a) Unit test the alias map function. (b) Integration test invoking `governed_run` via a fixture and asserting 4 L7 artifacts. (c) Byte-identical assertion: alias-source SHA256 pairs match. (d) CI gate scans last N apps_* runs under `artifacts/<app>/runs/` for missing aliases or drift; advisory by default; fail-closed via env var. | ~4k | Not Started |
| P3.4 | Live verification W3 | One smoke run per affected app: apps_qna, apps_research, apps_rfp, apps_underwriting_ai, apps_lic (governed path) | Each smoke run must produce all 4 L7 artifacts under its run_dir; spot-check no Track-1 receipts mutated. | ~2k | Not Started |

## 9. Verification

After each wave, the following must hold for a fresh run of the affected app:

```powershell
$run = (Get-ChildItem artifacts\<app>\runs | Sort-Object Name -Descending | Select-Object -First 1).FullName
foreach ($f in @("agentic_core_how_trace.json","agentic_core_l7_route_family_coverage.json","agentic_core_spine_proof.json","integrated_runtime_artifact_manifest.json")) {
  if (-not (Test-Path "$run\$f")) { Write-Error "MISSING $f in $run"; exit 1 }
}
```

CI gates that should pass after this plan:

- `ops_scripts/ci/verify_agentic_core_how_trace.py` (existing — should now apply to apps_* runs too)
- `ops_scripts/ci/verify_agentic_core_l7_route_family_coverage.py` (existing)
- `ops_scripts/ci/check_governed_run_l7_alias_drift.py` (new, W3)

## 10. Risk & Rollback

**W1, W2 risk**: Low. Additive emit blocks at end of existing entrypoints. If `build_how_trace` raises on malformed chain, runs fail loudly — desired fail-closed semantic.

**W3 risk**: Medium. Alias copy operation introduces filesystem write at end of `emit_post_execution_contracts`. Disk-full or permission errors could now break runs that previously succeeded silently. Mitigation: P3.3 CI gate is advisory-by-default; integrity test catches drift before CI escalates.

**Rollback**: per-wave revert. Each wave is one or two file edits plus its tests; no schema migrations; no hash-bound artifacts mutated; alias files are content-identical copies (deletable).

## 11. Author-Gate Decisions Foreseen

The architectural choice (Option A vs B/C/D) was already resolved 2026-05-06. Three further Author-Gate decisions may surface during execution:

AG_QUEUE_SEED: plan=apps-l7-coverage-spine-wide-c5e8d2 id=ag1-r4-lic-emit-shape title=R4_lic_emit_shape_divergence depends_on=
AG_QUEUE_SEED: plan=apps-l7-coverage-spine-wide-c5e8d2 id=ag2-alias-map-source title=Track1_to_Track2_alias_map_source_decisions depends_on=ag1-r4-lic-emit-shape
AG_QUEUE_SEED: plan=apps-l7-coverage-spine-wide-c5e8d2 id=ag3-alias-drift-fail-mode title=Alias_drift_CI_gate_advisory_or_fail_closed depends_on=ag2-alias-map-source

Triggers:
- AG-1 fires if `_emit` signature in R4 lic differs from R4 deterministic in W2.P2.1
- AG-2 fires when authoring the alias map in W3.P3.1 — choice of which Track-1 file maps to each Track-2 expected filename, especially for `runtime_identity_envelope.json` which has no exact Track-1 sibling and may need synthesis
- AG-3 fires when promoting the alias-drift CI gate from advisory to fail-closed; depends on shadow-mode FP rate evidence

## 12. References

- `agentic_core/L7_auditability/__init__.py:14` — plane invariant
- `agentic_core/L7_auditability/how_trace/how_trace_builder.py:114-175` — build_how_trace contract and required filenames
- `agentic_core/runtime/entrypoints/integrated_safe_reuse_run.py:1184-1219` — reference L7 emit implementation
- `agentic_core/runtime/entrypoints/integrated_managed_workflow_run.py:606-630` — second reference
- `apps_shared/spine_emission/context.py:408-493` — current `emit_post_execution_contracts`
- `apps_rg/__main__.py:66-68, 349-352` — apps_rg call site (W1)
- `apps_lic/__main__.py` — apps_lic dual-path (W2 + W3)
- `tools/cert/emit_l7_plane_evidence.py` — RTC-REQ-130..139 binder (downstream)
- ADR-080 (Phase D auditability) — design anchor
- ADR-050 (intelligence-ledger-family) — cross-cutting evidence plane discipline
- Constitutional sections 5, 22, 32, 36

## 13. Deferred Scope

DEFERRED_SCOPE: apps_eval has no spine wrapping; runs as a direct __main__ shim that delegates to L1/L2/L0 without governed_run or any L7-emitting entrypoint. Wiring apps_eval into governed_run is an architectural change (~10k tokens) beyond this plan's boundary. Tracked as a sibling plan to be authored after W3 lands.

DEFERRED_SCOPE: apps_repo_brief invokes its own integrations runner directly without governed_run. Same shape as apps_eval gap. Tracked as a sibling plan.

DEFERRED_SCOPE: Fort Knox certification compile (`tools/cert/emit_l7_plane_evidence.py`, `tools/certification/generate_100pct_runtime_proof.py`) does not currently include apps_* runtime evidence in its RTC-REQ-130..139 chain enumeration. After this plan lands, a follow-up plan extends Fort Knox to bind apps_* L7 artifacts to the certification universe.

DEFERRED_SCOPE: The 5 currently-unused legacy entrypoints (`integrated_exact_cache_run.py`, `integrated_fallback_run.py`, `integrated_managed_workflow_real_run.py`, `integrated_single_action_run.py`, `integrated_uwg_block_run.py`, `integrated_uwg_commit_run.py`) also lack L7 emit but have no current production callers. Either wire them or retire them — separate plan.

NEXT_STEP: After W3 lands, audit apps_e2e proof producers to confirm they accept the new L7 artifacts as additional evidence without breaking SPINE_COMPLETE_CERTIFIED.

NEXT_STEP: After W3 lands, run `ops_scripts/ci/check_governed_run_l7_alias_drift.py` in shadow for >= 7 days, then gate AG-3 to flip from advisory to fail-closed.

## 14. Non-Implementation Notice

This plan is registered in Notion but NOT yet executed. Wave execution requires explicit user authorization. Per constitutional section 36, no `wave_execution_state.py start` will be called until the user approves W1 to begin.

The superseded plan `apps-rg-l7-auditability-wireup-b3c7e1` is being marked Retired in Notion concurrent with this plan's registration; its file is preserved on disk for traceability and absorbed verbatim as W1 of this umbrella.
