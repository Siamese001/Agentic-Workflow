---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-orphaned\\adg-fail-aggregating-gate-chain-9d4e1f.md'
original_relative_path: '_archive\\2026-orphaned\\adg-fail-aggregating-gate-chain-9d4e1f.md'
source_sha256: 383b23eaa50f3987190beb4bf5f7e702319b21cd67b67c45a9d13b0dba5482b1
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# ADG Gate Chain — Fail-Aggregating Refactor + Backlog Cleanup

**Slug:** `adg-fail-aggregating-gate-chain-9d4e1f`
**Status:** Draft (awaiting approval)
**Authored:** 2026-04-28
**Tier:** T3 (cross-layer, 13+ gate sites, alters CI semantics)
**Author:** Cascade (per session 2026-04-28 06:30–06:44 UTC)

---

## 1. Problem Summary

Today's `python tools/generate_full_adg.py` run revealed multiple compounding issues
in the ADG gate chain. They surfaced while verifying the Notion top-5 critical
backlog items, but they have repo-wide impact on debugging speed, snapshot
freshness, and CI signal completeness.

### Issues identified (this session)

| # | Issue | Severity | Evidence |
|---|---|:---:|---|
| **I1** | **P2 ratchet hard-fail in production** — `current=8 > ceiling=2` (6 new MEDIUM antipatterns since 04-25) | P1 | `[ERROR] P2 ratchet: MEDIUM antipattern regression detected` in `_last_full_run.log` |
| **I2** | **Stale snapshot — 3 days old** (`adg_indexed_04252026_0843.sqlite`); current run never produced fresh `.sqlite` because Stage 1 short-circuited | P1 | `ls artifacts/adg/adg_indexed_*.sqlite` shows latest is 04-25 |
| **I3** | **Fail-fast endemic across 13 gate functions** — every gate calls `sys.exit(1)` or `raise` on first violation, hiding all downstream gate signal | P1 | Audit: 11/11 gate fns use sys.exit; 0/11 use deferred registry on violation path |
| **I4** | **Defer infrastructure exists but is half-wired** — `_fail_closed_gate` only delegates to `record_or_exit` on infrastructure errors (sqlite/OSError/JSON/ValueError), NOT on actual violation findings | P1 | `validation/gates.py:53-65` — only `except` blocks call defer; `if p0_count > 0:` paths still `sys.exit(1)` |
| **I5** | **Flag is misleadingly named** — `--continue-on-p0` / `ADG_CONTINUE_ON_P0=1` is documented as governing all gates but its name implies P0-only | P2 | `deferred_failures.py:_DEFER_ENV_VAR` + docstring caveat |
| **I6** | **No aggregated final report** — even when defer is active, `main()`'s drain prints `gate_name(rc=N)` but no consolidated summary table of all violations across all gates in one run | P2 | `_shared_deferred_exit_code` drain block in `generate_full_adg.py:1747-1772` |
| **I7** | **`generate_full_adg.py` ≠ full contract-gate suite** — broader gates in `ops_scripts/ci/run_contract_gates.py` (config schema, graph-layer evidence, deferred-scope markers, MCP sync, AGENTS coverage, query progress bar, router calibration) are NOT invoked by ADG generation; user expectation mismatch | P2 | Constitutional §4 documents `run_contract_gates.py` as the canonical full runner |
| **I8** | **Notion P-bands are stale** — Last Scored=2026-04-24 across the top-5; impact scores haven't been recomputed against current snapshot | P3 | Today's Notion query showed `Last Scored: 2026-04-24` on all 5 rows |
| **I9** | **Inconsistent execution model between Stage 1 and Stage 2** — Stage 2 (post-ADG gates) already runs in parallel via `_run_post_adg_gates_parallel`, but Stage 1 is sequential + fail-fast. Same gates, two different philosophies. | P3 | `generate_full_adg.py:1648-1733` |

### Root cause

Gates were originally written individually with hard-exit semantics. Plan
`adg-cascading-ratchet-defer-exit-a41828` (Wave B) introduced the deferred
registry but only retrofitted the infrastructure-error paths via
`_fail_closed_gate`. The violation-finding paths were never converted.

---

## 2. Goal

A single `python tools/generate_full_adg.py` run produces:

- A fresh ADG snapshot on disk **even when gates fail**
- Every gate's pass/fail/error signal in a single aggregated report
- A non-zero exit code if any gate failed (CI still blocks merge)
- An optional strict mode (`ADG_STRICT_FAIL_FAST=1`) that preserves today's behavior for emergency use

---

## 3. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---:|---|---|---|
| **W0** | W0.1 | Baseline + reproduce | 2k | Current `gates.py` / `integrity.py` / `deferred_failures.py` are SSOT; no concurrent W2 plans modify them | Todo | Audit log + reproducer captured under `docs/reports/plans/adg-fail-aggregating-gate-chain-9d4e1f/W0_baseline.md` |
| **W1** | W1.1, W1.2 | Clear current P2 regression so the rest of the chain can run today | 5k | The 6 new MEDIUM antipatterns are real (not false positives); guardian exemptions are inappropriate | Todo | `python tools/generate_full_adg.py` exits 0 with all gates run OR explicit ratchet bump with ADR |
| **W2** | W2.1, W2.2, W2.3, W2.4 | Wire violation paths to deferred registry across all 13 gate sites | ~12k | `record_or_exit` semantics are correct as-is; no API change needed in `deferred_failures.py` | Done | All 13 sites converted; 11 aggregation tests + 186 failfast-mode tests all green (`test_deferred_failures_aggregation.py`, `test_generate_full_adg_failfast.py`) |
| **W3** | W3.1, W3.2 | Aggregated final report + flag rename/alias | 4k | Operators want one summary table at run-end; back-compat alias acceptable | Done | `format_summary_table()` in `deferred_failures.py` wired into drain (`generate_full_adg.py:1772`); `ADG_CONTINUE_ON_GATE_FAILURE` alias landed alongside legacy `ADG_CONTINUE_ON_P0` |
| **W4** | W4.1 | Stage 1 ↔ Stage 2 unification (partial) | ~6k | ThreadPoolExecutor parallelism for Stage 1 ratchets is safe (each reads SQLite read-only) | Partial | Stage-2 post-ADG parallel-gate failures now route through `record_or_exit` so the drain table covers them too (`generate_full_adg.py:1932-1939`); full Stage-1 parallelization deferred |
| **W5** | W5.1, W5.2 | Refresh Notion P-bands + close the loop on top-5 critical | 3k | Snapshot renderer regenerates without errors after W2 changes | Todo | Top-5 backlog items re-scored; snapshot page regenerated; aged "UNSCORED" rows reduced |

**Total est. tokens:** ~32k

---

## 4. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---:|---|
| **W0.1** | Capture baseline + reproducer | (none — read-only) | Confirm current behavior, log all 13 fail-fast sites | 2k | Todo |
| **W1.1** | Investigate the 6 new MEDIUM antipatterns | `artifacts/adg/p2_ratchet.json`, ADG SQLite query | Identify which files/edges crossed the line; classify regression vs accepted change | 2k | Todo |
| **W1.2** | Remediate or bump ceiling with ADR | `<implicated files>`, `artifacts/adg/p2_ratchet.json`, `docs/architecture/adr/ADR-NNN-*.md` | Either narrow exception handlers OR justify ceiling bump | 3k | Todo |
| **W2.1** | Convert P0/P1/P2/P3 ratchet violation paths to `record_or_exit` | `tools/generate/validation/gates.py` (lines 117, 129, 142, 157, P1/P2/P3 ratchet fns) | Preserve message format; preserve plan_path argument; ensure SystemExit re-raise unchanged | 4k | Todo |
| **W2.2** | Convert structural-conformance + agentic-antipattern + witness-tier paths | `tools/generate/validation/gates.py` (`_check_structural_conformance`, `_check_agentic_antipatterns`, `_check_witness_tier_gates`) | Same conversion pattern as W2.1 | 3k | Todo |
| **W2.3** | Convert integrity gates + dead-prod-imports + locked-files + p0_runner | `tools/generate/validation/integrity.py`, `tools/generate/utils/file_utils.py`, `tools/generate/integration/p0_runner.py`, `tools/generate/integration/mcp_drift.py` | locked-files MUST stay fail-fast (snapshot would corrupt); rest defers | 3k | Todo |
| **W2.4** | Unit tests — fail-fast vs defer for each gate | `tests/unit/tools/generate/test_gate_defer_semantics.py` (new) | Cover env-var off (legacy), env-var on (defer), strict mode env override | 2k | Todo |
| **W3.1** | Aggregated final report block | `tools/generate/generate_full_adg.py` (drain block ~line 1747-1772), `tools/generate/integration/deferred_failures.py` (add `format_summary_table()`) | Markdown table sorted by severity, copy-pasteable | 2k | Todo |
| **W3.2** | Flag rename/alias + docs | `tools/generate/integration/deferred_failures.py`, `docs/architecture/adr/ADR-NNN-fail-aggregating-gates.md`, AGENTS.md | Add `ADG_CONTINUE_ON_GATE_FAILURE=1` reading the same gate; preserve `ADG_CONTINUE_ON_P0=1` with deprecation note | 2k | Todo |
| **W4.1** | Parallelize independent Stage 1 ratchets | `tools/generate/generate_full_adg.py` (refactor `main()` ratchet calls into a gate-spec list and reuse `_run_post_adg_gates_parallel`) | Each gate must be SQLite-read-only; serialization preserved for snapshot-build dependencies | 6k | Todo |
| **W5.1** | Regenerate snapshot + run scorer | `python tools/generate_full_adg.py`, `python tools/notion/snapshot_renderer.py --regenerate` | Requires W2+W3 complete; will auto-rescore top-5 | 1k | Todo |
| **W5.2** | Cross-check top-5 critical backlog ranking | Notion Wave/Phase Convergence DB | Confirm/refute today's session ranking against fresh impact scores | 2k | Todo |

---

## 5. Out of Scope (NEXT_STEP candidates)

- Replacing `generate_full_adg.py` with `run_contract_gates.py` as canonical full-suite runner (documentation/wiring task; not a code refactor)
- Migrating Stage 2 gates from subprocess to in-process (W3 ADR notes this is a future option)
- Cleaning up the 60 UNSCORED Notion rows (separate scorer-cadence work)

---

## 6. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Defer mode masks ordering-dependent failures (e.g. snapshot build) | Keep `_check_locked_files`, snapshot-build, and `_check_mcp_config_drift` as fail-fast; document why in code comments |
| CI exit code regressions if `record_or_exit` returns instead of exiting | W2.4 unit tests + W5.1 end-to-end run in both legacy and aggregating modes |
| Aggregated report grows unbounded in large failures | Cap details at top-N per gate; full list spilled to `artifacts/adg/gate_failures_<ts>.json` |
| Flag rename breaks downstream scripts | Preserve old flag with deprecation log; remove no earlier than 90 days |

---

## 7. Acceptance Criteria

- [ ] `python tools/generate_full_adg.py` produces a fresh `adg_indexed_<ts>.sqlite` snapshot **even when gates fail**
- [ ] All 13 gate sites converted to defer-aware violation paths (W2 audit script returns 0 fail-fast-on-violation hits)
- [ ] Default behavior remains fail-fast (env var off → identical exit-code semantics to today, except snapshot is now written before exit)
- [ ] `ADG_CONTINUE_ON_GATE_FAILURE=1` produces aggregated report with all gate outcomes in a single markdown table
- [ ] `ADG_STRICT_FAIL_FAST=1` reproduces today's behavior exactly (escape hatch)
- [ ] ADR-NNN-fail-aggregating-gates.md committed and posted to ADR Registry
- [ ] AGENTS.md MCP Quick Reference + global_rules.md updated with new flag
- [ ] Notion top-5 critical re-verified against fresh snapshot

---

## ADG_HOTSPOT_REPORT

(Required per constitutional §22 / §23. Computed before W2 execution.)

To be populated in W0.1 from the fresh ADG snapshot. Expected hotspots based
on import topology:

| Rank | File | Layer | Fan-In | Surface | Archetype | Impact (est.) |
|---:|---|:---:|---:|---|---|---:|
| 1 | `tools/generate/validation/gates.py` | L_TOOLS | TBD | Observability Surface | CENTRAL_DEPENDENCY | TBD |
| 2 | `tools/generate/integration/deferred_failures.py` | L_TOOLS | TBD | Observability Surface | STATE_NODE | TBD |
| 3 | `tools/generate/generate_full_adg.py` | L_TOOLS | TBD | Execution Surface | ORCHESTRATOR | TBD |

(Will be filled in by W0.1 from `mcp1_adg_edge_fanin` queries.)

---

## ADG_GRAPH_LAYER_EVIDENCE

(Required per constitutional §22. ≥3 materialized views, ≥1 semantic edge.)

- **`mv_hotspot_centrality`** — confirm `gates.py` is high-fan-in within `L_TOOLS`
- **`mv_dependency_cone_risk`** — show blast radius if `gates.py` API changes
- **`mv_path_criticality_rollup`** — confirm gate-chain is on critical path

Semantic edges: **`flows_to`** (from gates → `main()` drain), **`controls_flow`**
(gate exit code → process termination).

P-views: `v_p2_*` not expected to match (this is L_TOOLS, not production).

---

## 10. References

- Plan **adg-cascading-ratchet-defer-exit-a41828** (W8/Wave B — introduced `_fail_closed_gate` + `deferred_failures.py`; this plan completes the conversion)
- Constitutional **§4** — `run_contract_gates.py` is the canonical full-suite runner
- Constitutional **§22, §23** — ADG graph-layer + canonical invariants
- Source files (audit results from session 2026-04-28):
  - `tools/generate/validation/gates.py` (8 fail-fast sites)
  - `tools/generate/validation/integrity.py` (3 fail-fast sites)
  - `tools/generate/integration/p0_runner.py`, `mcp_drift.py` (2 sites)
  - `tools/generate/utils/file_utils.py` (1 site — KEEP fail-fast)
  - `tools/generate/integration/deferred_failures.py` (defer infrastructure)
  - `tools/generate/generate_full_adg.py` (`main()` drain block, Stage 2 parallel runner)
- Audit scripts (this session):
  - `artifacts/adg/_gate_audit.py` — gate fn → behavior table
  - `artifacts/adg/_gate_audit2.py` — ratchet + drift detail
  - `artifacts/adg/_last_full_run.log` — reproducer for I1+I2+I3
