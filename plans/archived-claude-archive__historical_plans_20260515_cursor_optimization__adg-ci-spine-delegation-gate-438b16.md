---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\adg-ci-spine-delegation-gate-438b16.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\adg-ci-spine-delegation-gate-438b16.md'
source_sha256: 519b06abbd5477a3d5dd39253f03a39782035d8b9513617b6dd0356b46ae030e
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# ADG CI Gate — apps_* → agentic_core Spine Delegation

**Plan ID**: `adg-ci-spine-delegation-gate-438b16`
**Status**: **Superseded by `adg-three-bucket-unified-c4f8e2`** (2026-04-30) — folded into unified W3 (advisory) + W5 (strict flip)
**Tier**: T2
**Owner**: Cascade (proposes); operator (approves)
**Created**: 2026-04-30

## Problem

Constitutional architecture states two valid runtime modes:

- **Mode A (core-only)**: `user → agentic_core spine → output`
- **Mode B (app overlay)**: `user → apps_* enrichment → agentic_core spine → output`

The forbidden mode is: `user → apps_* standalone mini-runtime → output` — i.e.,
an `apps_*` package that reimplements intake/route/execute logic instead of
delegating to `agentic_core/L0_routing`, `L1_cognition`, `L2_execution`.

This invariant is **not** mechanically detectable at author time (a hook on
file write cannot tell legitimate enrichment from forbidden re-implementation).
It **is** detectable at commit/CI time as a structural ADG property: every
`apps_*/` package MUST have at least one import edge into the spine layers,
AND MUST NOT define its own intake-router-executor triple.

No current gate enforces this. The `core-vs-apps-routing` advisory rule (to be
added separately) is the prompt-tier mechanism; this plan is the deterministic
fail-closed mechanism.

## Goal

Ship `ops_scripts/ci/check_apps_spine_delegation.py` as a pre-commit + CI
gate that, for every `apps_*/` top-level package, asserts spine delegation via
ADG queries — fail-closed when an app contains modules with no edges into
`agentic_core.L[0-2]_*` and locally defines orchestrator-shaped classes.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | 1.1, 1.2 | Spec + ADG query design | ~4000 | ADG snapshot has `nodes`, `edges`, materialized views populated | Todo | Query returns deterministic result on current snapshot; expected pass on all current `apps_*/` |
| W2 | 2.1, 2.2, 2.3 | Implement gate + tests | ~9000 | `ops_scripts/ci/` is canonical SSOT folder per constitutional §31 | Todo | Gate exits 0 on clean tree, exits 2 on synthetic violation fixture; ≥15 unit tests pass |
| W3 | 3.1, 3.2 | Wire into pre-commit + run_contract_gates | ~3000 | `.pre-commit-config.yaml` schema unchanged | Todo | New hook fires on staged `apps_*/**.py`; `run_contract_gates.py` includes the gate |
| W4 | 4.1 | Notion + memory writeback | ~1500 | MCP Registry + ADR Registry reachable | Todo | ADR row posted; Memory `ProceduralPattern:AppsSpineDelegationGate` written |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| 1.1 | Spec the invariant | `docs/architecture/adr/ADR-NNN-apps-spine-delegation.md` (NEW) | Distinguishing "no spine import" (forbidden) from "imports infrastructure only" (allowed shared utils) | ~2000 | Todo |
| 1.2 | Design ADG query | (design only — written into ADR) | False-positive risk on legitimate utility-only modules inside apps_*; need allowlist for pure config/schema files | ~2000 | Todo |
| 2.1 | Implement gate logic | `ops_scripts/ci/check_apps_spine_delegation.py` (NEW) | Direct SQLite per constitutional §28 (build/CI has no MCP); reuse `find_latest_snapshot` pattern from `apps_qna/integrations/architecture_synth.py` | ~5000 | Todo |
| 2.2 | Synthetic-violation fixtures | `tests/unit/ops_scripts/ci/fixtures/apps_violator/` (NEW) | Need a minimal apps_* shape that exercises (a) clean delegation, (b) zero spine imports, (c) local orchestrator-shaped class with no spine edge | ~2000 | Todo |
| 2.3 | Unit tests | `tests/unit/ops_scripts/ci/test_check_apps_spine_delegation.py` (NEW) | Cover: snapshot-missing fallback, no-violations path, single-violation path, multi-app path, allowlist mechanism, bypass env var | ~2000 | Todo |
| 3.1 | Pre-commit wiring | `.pre-commit-config.yaml` (modify) | Hook id naming + tier (T7-class structural gate); ensure pass-filenames so it only runs on `apps_*/**.py` changes | ~1500 | Todo |
| 3.2 | Contract-gates wiring | `ops_scripts/ci/run_contract_gates.py` (modify) | Add to gate registry; ensure non-zero exit propagates to GH Actions | ~1500 | Todo |
| 4.1 | Writeback | Notion ADR Registry, MCP Registry note (if behavior overlaps), Memory `ProceduralPattern:AppsSpineDelegationGate` | Per `memory-notion-writeback.md`; the ADR is the searchable artifact, the gate file is the SSOT | ~1500 | Todo |

## Gap Register

| Gap | Resolution Plan |
|-----|-----------------|
| What counts as a "spine import edge"? | ADR §3 enumerates: any edge `apps_X/**` → `agentic_core.L0_routing.*` ∨ `agentic_core.L1_cognition.*` ∨ `agentic_core.L2_execution.*`. Excludes `agentic_core.L4_state.*`, `L5_safety.*`, `L6_observability.*` (those are infrastructure, not spine). |
| What counts as "orchestrator-shaped"? | ADR §4: classes whose name matches `*Engine`, `*Router`, `*Orchestrator`, `*Executor`, `*Runner` AND whose module imports nothing from `agentic_core.L[0-2]_*`. Two-condition AND keeps false-positive rate low. |
| Allowlist for legitimate utility-only modules? | YAML at `config/apps_spine_delegation_allowlist.yaml` — explicit per-file opt-out with justification field. CI reads it; gate prints allowlist usage to stderr for visibility. |
| Bypass mechanism? | `APPS_SPINE_DELEGATION_BYPASS=1` env var. Logs WARNING; durable via existing pre-commit logging. |
| Direct-SQLite path? | Per constitutional §28, MCP-unavailable contexts (CI, pre-commit) MUST use direct `sqlite3` against `artifacts/adg/adg_indexed_<ts>.sqlite`. Reuse `find_latest_snapshot` pattern with the ≥1MB stub-filter from `apps_qna/integrations/architecture_synth.py:find_latest_snapshot`. |
| Snapshot-missing behavior? | Exit 0 with WARNING ("ADG snapshot unavailable; spine delegation check skipped — re-run after `python tools/generate_full_adg.py`"). Fail-soft consistent with other ADG-dependent gates. |

## ADG_HOTSPOT_REPORT

The gate itself is not refactoring existing code, so a hotspot report is not
applicable. The gate's *targets* are the `apps_*/` packages, and the ADR
section §5 will enumerate current-state spine-delegation status per app:

| App | Mode (current) | Spine import edge count | Risk |
|-----|----------------|-------------------------|------|
| apps_qna | Mode B | TBD via ADG query at W1.2 | Low (recent integration; verified manually 2026-04-30) |
| apps_eval | Mode B | TBD | Low |
| apps_exec | Mode B | TBD | Low |
| apps_lic | Mode B | TBD | Medium (large surface; needs verification) |
| apps_research | Mode B | TBD | Low |
| apps_rfp | Mode B | TBD | Low |
| apps_rg | Mode B | TBD | Medium (large surface; multiple engines) |
| apps_underwriting_ai | Mode B | TBD | Medium |
| apps_shared | (utility) | exempt | n/a — apps_shared is shared utility, not an app |

W1.2 produces the actual numbers and confirms zero false-positives before the gate goes strict.

## ADG_GRAPH_LAYER_EVIDENCE

Mandatory per constitutional §22. The gate uses the following ADG primitives:

1. **`mv_graph_reverse_dependency_hotspots`** — used by ADR §5 to confirm that
   spine modules (`agentic_core/L[0-2]_*/`) appear as high-fanin targets of
   `apps_*/` callers (i.e., the canonical Mode-B pattern is observable in the
   current graph as a baseline).
2. **`mv_hotspot_centrality`** — used to rank spine entrypoints; the gate's
   "spine edge" definition is anchored to the top-N centrality nodes within
   `agentic_core.L[0-2]_*`, not arbitrary symbols.
3. **`mv_path_criticality_rollup`** — used by W1.2 design phase to verify
   the gate's allowlist does not exempt files on critical execution paths.
4. **Semantic edges** — `imports` is the primary edge for delegation
   detection. `flows_to` is consulted as secondary evidence: an apps_* module
   with `flows_to` edges into spine but no `imports` edge is suspicious
   (likely indirect-import smell — flagged but not blocked in v1).
5. **P-views** — `v_p1_mis_layered_infra` and `v_p1_zero_caller_infra` are
   cross-checked: any module the gate flags should also appear here OR have a
   recorded allowlist entry — otherwise the violation is novel and warrants
   ADR-level attention before the gate flips to strict.

ADG provenance line for evidence in W1.2: `backend=sqlite, snapshot=adg_indexed_<latest>.sqlite`.

## Forbidden Patterns

- ❌ Implementing the gate as a Windsurf hook (`pre_write_gate.py`) — wrong tier; the invariant is structural, not authoring-time. See user request 2026-04-30 13:14 UTC-04:00 recommendation.
- ❌ Using `grep_search` to find spine imports — constitutional §28 forbids grep for dependency analysis; direct SQLite is the canonical fallback when MCP is unavailable.
- ❌ Hard-coding the apps_* list — discover from filesystem (`apps_*` glob) at gate-run time so new apps are auto-covered.
- ❌ Strict mode at v1 — start advisory (exit 0 + report) for one calibration cycle, then flip to fail-closed via `APPS_SPINE_DELEGATION_GATE_MODE=strict` once the W1.2 baseline confirms zero false positives on current tree.

## Operational Gates

- **Entry to W2**: ADR merged + W1.2 baseline shows zero false positives across all 9 apps_* packages.
- **Entry to W3**: gate passes on clean tree; gate fails on synthetic-violation fixture; ≥15 unit tests green.
- **Entry to W4**: pre-commit + run_contract_gates wiring smoke-tested locally; one full `pre-commit run --all-files` passes.
- **Exit (plan complete)**: ADR row in Notion ADR Registry; Wave/Phase row marked Done; Memory `ProceduralPattern:AppsSpineDelegationGate` written; gate active in `.pre-commit-config.yaml` and `run_contract_gates.py`; `APPS_SPINE_DELEGATION_GATE_MODE` defaults to `strict`.

## Dependencies

- Pairs with new conditional rule `core-vs-apps-routing.md` (separate plan) — the advisory tier informing Cascade where new modules should live; this plan is the deterministic tier catching violators.
- Constitutional §22 (graph-layer primary driver), §28 (SQLite-first fallback), §31 (SSOT folder routing — gate file lands in `ops_scripts/ci/`).

## Success Criteria (plan-level)

1. ADR-NNN-apps-spine-delegation.md merged.
2. `ops_scripts/ci/check_apps_spine_delegation.py` exists, ≥15 unit tests, runs in <2s on current snapshot.
3. Pre-commit hook `apps-spine-delegation` registered; runs on `apps_*/**.py` changes only.
4. `run_contract_gates.py` invokes the gate; non-zero exit propagates to CI.
5. One full `pre-commit run --all-files` passes on current main.
6. Synthetic violation fixture demonstrably fails the gate.
7. Notion ADR Registry row + Memory writeback complete.
