# ADR-034: Wiring-CI Gate Plane and UWG Writer Allowlist

**Date:** 2026-04-23
**Status:** Accepted
**Deciders:** SVP Engineering (Constitutional Rule #11)
**Related:** Constitutional §22 (graph layer primary), §5-§7 (gravity + exception discipline), ADG Canonical Invariants §1-§4
**Supersedes:** none
**Superseded by:** none

## Context

The C0 Context Engine pipeline — declared in `docs/reference/03_L0_Routing/C0 - Retrieval/C0 Context Engine.md` as the 5-stage retrieval engine (Plan → Fetch → Graph → Shape → Contract) — had **zero wiring in the production call graph** as of adg snapshot `adg_indexed_04222026_2106.sqlite`. The file `agentic_core/L1_cognition/utils/c0_context_retriever.py` was trace-theater (73/78 imports = 0.94 ratio targeting `lifecycle_trace_contract._emit_*`), and a matching seam test asserted three `getattr(agentic_core, ...)` attributes that do not exist on the `agentic_core` package at all.

`pytest.importorskip(...)` fixtures masked the missing exports, letting the seam test file pass by skipping. The failure mode was entirely silent to existing CI.

Investigation through the ADG revealed that the same pattern (documented pipeline + no production caller + trace ritual + seam-test theater) was NOT unique to C0:

- 1,780 production modules have zero inter-module `imports` fan-in (orphan plane)
- 2,389 `writes_to` edges originate from modules that are not on the Unified Write Gateway (UWG) approved-writer path
- 1,759 `antipattern.global_state_mutation` edges in production layers
- 13 module-level directed import cycles (including cross-layer: L0↔L2, L5 safety self-cycles)
- 5 seam test files use the same `importorskip → getattr → NameError` pattern that masked C0

Existing CI gates (`infra_wiring_scan.py`, `executor_theater_gate.py`, etc.) did not catch any of this because they operate on different signal dimensions (raw infra imports, fake parallelism) than graph-shape wiring.

## Decision

Introduce a **15-gate Wiring-CI plane** anchored on the ADG SQLite snapshot and a small number of on-disk configs, organized into three tiers:

### Tier B (Blocking)

| Gate | Purpose |
|---|---|
| `J1_canonical_pipeline_wiring` | Every `active` stage in `config/canonical_pipelines.yaml` must have ≥1 production-layer caller matching its ingress layer |
| `A6_import_cycle` | No directed SCC of size > 1 in the module-level projection of `imports` edges |
| `G2_seam_test_export_coherence` | Every `getattr(pkg, "name")` in `tests/**/seams/*.py` must resolve to a real export in `pkg/__init__.py` |
| `W5_waiver_expiry` | Every entry in `config/wiring_gate_waivers.yaml` must have a future `expires_on` |

### Tier R (Ratchet — locked at today's count, regressions fail CI)

| Gate | Baseline |
|---|--:|
| `A1_orphan_module_ratchet` | 1,780 |
| `A3_dead_public_symbol_ratchet` | 0 |
| `E1_trace_stub_module` | 1,263 |
| `L1_layer_gravity` | 100 |
| `L2_lpg_drift_ratchet` | 14 |
| `M1_module_loc_ratchet` | 323 |
| `S1_global_state_mutation_ratchet` | 1,759 |
| `S2_uwg_bypass_ratchet` | 2,389 |
| `S3_exception_swallow_ratchet` | 1,593 |
| `S4_unused_imports_ratchet` | 5,780 |

### Tier W (Warn — diagnostic only, never blocks)

| Gate | Purpose |
|---|---|
| `D1_layer_doc_binding` | Every `docs/reference/NN_L*/` folder should map to a pipeline in the canonical manifest |

### UWG Writer Allowlist (binding contract)

The `S2_uwg_bypass_ratchet` gate references a frozen, in-code allowlist of modules permitted to issue `writes_to` edges without routing through the Unified Write Gateway:

```python
UWG_APPROVED_WRITERS = frozenset({
    "agentic_core/L2_execution/utils/write_gateway.py",
    "agentic_core/L4_state/enforcement/promotion_write_gateway.py",
    "agentic_core/L5_safety/validators/static_checks/write_gateway_enforcer.py",
    "agentic_core/interfaces/write_gateway.py",
    "agentic_core/interfaces/write_gateway_shim.py",
})
```

These five modules — the gateway itself, its L4 promotion-path sibling, the L5 static enforcer, and two L_SHARED interface declarations — are the ONLY production modules permitted to originate `writes_to` semantic edges. Any addition to this set requires:

1. A new ADR documenting the justification.
2. Citation of the ADR in a code comment above the allowlist entry.
3. Explicit reviewer sign-off on the ADR, not on the PR.

Ratchet semantics ensure that the 2,389 pre-existing bypasses are frozen (cleanup proceeds asynchronously) while no new bypass above baseline can land without either (a) routing through the gateway or (b) the allowlist ADR path above.

## Rationale

**Why ratchet not block for 10 of 15 gates.** The codebase has substantial accumulated architectural debt (15,001 pre-existing instances across the 10 ratchet gates). Blocking on absolute zero would freeze the repository. Ratcheting freezes the ceiling at today's state and inverts the economics: every new PR is cheaper to clean up than the equivalent pre-existing line, so new code cannot add to the backlog.

**Why graph-layer analysis instead of grep.** Each gate is backed by structural semantics (fan-in, fan-out, SCC membership, semantic-edge relation type) that grep cannot replicate without false positives and false negatives. See Constitutional §22 and the graph-analysis skill's tool-routing tree.

**Why the allowlist is frozen in code, not configurable.** Writes are the most destructive surface in the ADG Canonical Invariants §3 (Execution / Write / Security / State / Observability). A config file makes exemptions cheap to add; keeping the set in code and gated by ADR makes each exemption a deliberate, auditable decision. This mirrors the treatment of guardian exemptions per Constitutional §8.

**Why three tiers.** Blocking everything (B) would stall the codebase. Warning on everything (W) would be ignored. The B/R/W split gives each gate a behavior that matches its signal density: sharp-threshold rules like "no cycles" block outright; ratchets give operational forgiveness while preventing regression; diagnostic rules stay out of the way.

## Consequences

### Positive

- C0 wiring failures are caught at PR time rather than in production incidents.
- The 15,001 pre-existing issues are measured, named, and ratcheted — inventory exists where none did before.
- The UWG enforcement perimeter is real: new code either routes through the gateway or fails CI.
- The seam-test `importorskip`-then-`getattr` anti-pattern is blocked across all 5 existing seam test files and any new ones.
- The wiring trend reporter (`tools/reports/wiring_ci_trend.py`) makes regression and cleanup visible over time.

### Negative / Costs

- 15 extra checks in `run_contract_gates.py`; full fleet runs in ~20-30s against a 250 MB snapshot (acceptable).
- The UWG allowlist is stable enough to live in code but adds PR friction when a legitimate new sanctioned-writer module is introduced (requires ADR).
- Baselines must be periodically re-seeded in the opposite direction (ratchet-down) when cleanup lands — cleanup that is not baselined back down loses its CI ratchet protection on the next regression.

### Neutral

- The `span_end_line` column on ADG symbol nodes is not populated in the current snapshot; `M1_module_loc_ratchet` therefore reads files from disk. When `span_end_line` is populated in a future ADG generator change, switch M1 back to pure-ADG.

## Alternatives Considered

1. **Keep the existing `infra_wiring_scan.py` as the only wiring CI.** Rejected: it catches raw infra imports only, not graph-shape wiring. It would not have caught C0.

2. **Add a single monolithic "wiring health" gate.** Rejected: a single gate collapses dozens of orthogonal signals into one pass/fail, loses per-category ratchet ability, and produces unactionable failure reports.

3. **Require every writer to route through UWG with no allowlist at all.** Rejected: 2,389 pre-existing sites make this infeasible; would block every commit. The allowlist + ratchet provides the asymptotic discipline while allowing incremental cleanup.

4. **Put wiring gates in pre-commit only.** Rejected: pre-commit is staged-file-only by design (per existing `.pre-commit-config.yaml` principle). Wiring gates are whole-repo ADG queries. They live in `run_contract_gates.py` (CI) plus two file-triggered fast gates (`wiring-waiver-expiry`, `wiring-canonical-pipelines`) and two manual-stage dispatchers for local devs.

## Implementation

### Files created

```
ops_scripts/ci/
  _adg_wiring_gate_base.py                # shared harness: WiringGate ABC + tiers + sink
  check_canonical_pipeline_wiring.py      # J1
  check_orphan_module_ratchet.py          # A1
  check_dead_symbols_ratchet.py           # A3
  check_import_cycles.py                  # A6 (iterative Tarjan SCC)
  check_trace_stub_modules.py             # E1
  check_seam_test_export_coherence.py     # G2 (AST-only, no ADG)
  check_layer_gravity.py                  # L1
  check_lpg_drift_ratchet.py              # L2
  check_module_loc_ratchet.py             # M1 (disk-read)
  check_layer_doc_binding.py              # D1 (warn)
  check_global_state_mutation_ratchet.py  # S1
  check_uwg_bypass_ratchet.py             # S2 — allowlist lives here
  check_exception_swallow_ratchet.py      # S3
  check_unused_imports_ratchet.py         # S4
  check_waiver_expiry.py                  # W5
  baselines/wiring_*.json                 # 10 baseline files

config/
  canonical_pipelines.yaml                # C0 manifest
  schemas/canonical_pipeline.schema.json  # JSON Schema
  wiring_gate_waivers.yaml                # empty by default

tools/reports/
  wiring_ci_trend.py                      # trend markdown generator

docs/reports/wiring-ci/                   # output directory for trend reports
artifacts/windsurf/wiring_gate_violations.jsonl  # append-only sink
```

### CI integration

All 15 gates wired into `ops_scripts/ci/run_contract_gates.py` under the `[WIRING-CI GATE PLANE]` section. Pre-commit config (`.pre-commit-config.yaml`) adds:

- `T7l: wiring-waiver-expiry` — fast, triggered on `config/wiring_gate_waivers.yaml` edits
- `T7m: wiring-canonical-pipelines` — triggered on `config/canonical_pipelines.yaml` edits
- `wiring-ci-full` — manual stage, runs the full fleet
- `wiring-ci-trend` — manual stage, regenerates the trend report

### Current CI state (2026-04-23)

```
3 gates RED:   J1 (6), A6 (13), G2 (15) — reflect real architectural debt
10 ratchets:   locked at baseline, 15,001 issues frozen
1 warn:        D1 (3 unbound layer-doc folders)
1 green:       W5 (no waivers)
```

## Waivers

Waivers live in `config/wiring_gate_waivers.yaml`. Every waiver entry MUST specify `gate`, `scope`, `reason`, `owner`, and `expires_on`. `W5_waiver_expiry` blocks CI when any waiver is past its expiry date, forcing periodic human review. Waivers are never silently applied — each one is exercised against every gate run through `_waiver_matches()` in the harness.

## References

- Plan: `.windsurf/plans/adg-wiring-ci-hardening-7a5d84.md`
- Plan: `.windsurf/plans/c0-context-engine-wiring-fix-9e42a1.md`
- Constitutional rule: §22 (ADG graph layer primary)
- ADG Canonical Invariants: §1-§4 (SSOT hierarchy, ADG wins conflicts, surfaces, deadly catch-site antipatterns)
- Doctrine: `docs/reference/AST Dependency Graphs (ADG)/ADG - SQLite vs. Redis.md`
