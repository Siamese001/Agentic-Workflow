---
plan_id: adg-write-sovereignty-cleanup-8bf0da
plan_type: refactor
parent_plan: adg-architectural-p0-violations-cleanup-bced9c
created: 2026-04-28
author_gate_decision: architecture_choice — "Refactor through UWG over multiple waves"
                      (selected over accept-as-debt baseline; see commit 87022ea
                      session DECISION_CAPTURED on 2026-04-28)
---

# ADG Write-Sovereignty Cleanup — Route 1502 P0 Violations Through UWG

> **Status**: W1.1 + W1.2 COMPLETE (2026-04-28). User selected option D at
> revisited Author-Gate. Cumulative violation count: **1483 → 905** (−578, −39%).
> See `## W1.2 Outcome` section below. W2 (refactor residue) ready for next session.
>
> **Why this plan exists**: `run_contract_gates.py` is fully unblocked through
> line 280 (wiring scan, structure policy, graph-layer evidence, snapshot
> completeness, severity-band SSOT, judge calibration, author-gate ledger
> integrity all PASS). The hard stop is the P0 two-pass gate:
>
> | Gate family | is_new=1 (initial) | After W1.1 MV fix |
> |---|---:|---:|
> | `write_sovereignty` (`mv_new_write_bypass_paths`) | 1483 | **1366** |
> | `authority_boundary` | 17 | 17 (untouched) |
> | `capability_egress` | 2 | 2 (untouched) |
> | **Total** | **1502** | **1385** |
>
> User chose **option B** at the 2026-04-28 Author-Gate (over A=accept-as-debt
> JSON and C=time-boxed hybrid). Rationale: P0 write_sovereignty is a
> constitutional invariant; an accept-as-debt loophole would normalize 1483
> bypass sites and erode the durable-write contract. Refactor preserves the
> invariant.

## Scope

In: every site where the ADG materialized view `mv_new_write_bypass_paths`
flags a non-UWG durable write (any `relation_type IN ('writes_to',
'writes_through')` edge whose source is outside `agentic_core/L4_state/uwg/`
and not already exempt as a process-boundary adapter).

Out: tests/, tools/, archives/, and sanctioned process-boundary adapters
(already exempt in `_PROCESS_BOUNDARY_ADAPTERS`).

## ADG_HOTSPOT_REPORT (next session must populate)

Required structure (per constitutional §22):

| Rank | File | Layer | Fan-In | Archetype | Surface | Impact Score |
|---:|---|---|---:|---|---|---:|

Population query (canonical):

```sql
SELECT writer_file, writer_layer, severity, COUNT(*) AS violation_count
FROM mv_new_write_bypass_paths
WHERE is_new = 1
GROUP BY writer_file, writer_layer, severity
ORDER BY violation_count DESC, writer_layer
LIMIT 40;
```

Cross-reference with `mv_hotspot_centrality` and `adg_edge_fanin(relation_type='imports')`
for each top-40 file. Layer multiplier: L0 ×2.0, L5 ×2.0, L3 ×1.75, L4 ×1.75,
L1 ×1.0, L2 ×1.0, L6 ×0.75. Impact = `violations × (1 + log10(1 + fan_in)) × layer_multiplier`.

## ADG_GRAPH_LAYER_EVIDENCE (next session must populate)

Required materialized views (≥3 per §22):

- `mv_write_sovereignty_paths` — base relation classifying every write site
- `mv_new_write_bypass_paths` — delta view, the gate's authoritative source
- `mv_debt_concentration_hotspots` — ties bypass count to debt score
- `mv_dependency_cone_risk` — secondary risk for high-fan-in writers
- `v_p0_write_bypass_uwg` — pre-built P0 view, currently 0 rows after path exemptions

Required semantic edges: `writes_to`, `writes_through`, `flows_to`, `emits_side_effect`.

## Wave Structure

| Wave | Metric | Scope | Checkpoint | Tokens |
|------|--------|-------|------------|-------:|
| W1 | Top-40 hottest writers | apps_*/integrations + agentic_core L0/L3/L4 callers of sqlite3/redis/file IO | After 200 sites refactored, regenerate ADG; expect ≥30% reduction | ~30k |
| W2 | Mid-tier batch | layer-grouped by L1/L2/L6 | After 500 cumulative; verify p0 wave plan stays clean | ~25k |
| W3 | Tail + authority_boundary (17) + capability_egress (2) | Remainder + neighboring P0 families | run_contract_gates.py end-to-end PASS | ~20k |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---:|---|
| W1.1 | Populate ADG_HOTSPOT_REPORT + identify MV bugs | snapshot 04282026_1853 | Found symbol-based UWG bug → 117 false positives reclassified | ~3000 | ✅ DONE (commit ad0ee4f) |
| W1.2 | Refactor top-40 write sites through UWG | TBD — top of W1.1 report (post-fix list) | Each site needs UWG.commit() routing + identity propagation per docs/contracts/identity_propagation.md | ~25000 | 🔲 TODO |
| W1.3 | Regenerate ADG, verify P0 reduction | tools/generate_full_adg.py | Snapshot regen ~15min | ~2000 | 🔲 TODO |

## Success Criteria

- `run_contract_gates.py` run end-to-end exits 0
- `mv_new_write_bypass_paths` where `is_new=1` returns 0 rows
- `mv_authority_boundary_violations` where `is_new=1` returns 0 rows
- `mv_capability_egress_violations` where `is_new=1` returns 0 rows
- No regression in existing assurance-p1 plane (4 ASSURANCE-P1 gates remain green)

## Files In Scope

TBD — populated by W1.1 from `mv_new_write_bypass_paths`. Estimated 80–120 files
based on 1483 violations clustered in app integration layers.

## Parent Plan Summary

This plan is the dedicated refactor track for the write-sovereignty subset of
the broader pre-existing P0 architectural debt cataloged in
`adg-architectural-p0-violations-cleanup-bced9c`.

DEFERRED_SCOPE: plan=adg-write-sovereignty-cleanup-8bf0da wave=W1 phase=W1.2 layer=L4 fan_in=1366 surface=Write coverage_gap_pct=100.0 est_tokens=30000 reason=Refactor 1366 non-UWG durable writes through UWG to clear P0 write_sovereignty gate (revised down from 1483 after MV bug fix)

---

## W1.1 Outcome (2026-04-28)

### Root cause discovered

`mv_write_sovereignty_paths.is_uwg_routed` was computed by a path-only
heuristic (`_build_uwg_path_clause("src.resolved_path")`). It checked whether
the SOURCE FILE's path contained "uwg"/"write_gateway"/etc., never the call
SYMBOL. Healers and orchestrators that correctly use the canonical UWG
abbreviation `_wg.write_text(...)` were flagged as bypasses because their
own file paths don't sit under `uwg/`.

### Fix landed (commit `ad0ee4f`)

- New `_UWG_SYMBOL_FRAGMENTS` constant covering `_wg.`, `self._wg.`,
  `self.uwg.`, `self.write_gateway.`, `write_gateway.`, `uwg.`,
  `UniversalWrite`
- New `_build_uwg_symbol_clause` + `_build_uwg_routed_clause` helpers
- All 3 sites in `mv_write_sovereignty_paths` (is_uwg_routed CASE +
  2 severity-classification CASEs) now use the combined predicate
- 2 regression tests (`test_write_sovereignty_uwg_detected_by_symbol`,
  `test_write_sovereignty_uwg_symbol_variants`) — 5/5 phase A UWG tests pass

### Numerical impact (in-place re-run on 04282026_1853 snapshot)

| Metric | Before | After | Δ |
|---|---:|---:|---:|
| `mv_new_write_bypass_paths.is_new=1` | 1483 | 1366 | **−117** |
| `mv_write_sovereignty_paths.is_uwg_routed=1` | 67 | 184 | +117 |
| `mv_write_sovereignty_paths.severity='warning'` | 1482 | 1365 | −117 |

### Top-10 GENUINE hotspots (post-fix, after applying _wg.* / scripts / proof / types / test_*.py exclusions)

| Rank | Count | Symbol | File |
|---:|---:|---|---|
| 1 | 16 | `write_text` | `agentic_core/runtime/prove_requirements/writers.py` |
| 2 | 15 | `self._write` | `system_learning/engines/l4_state_writer.py` |
| 3 | 11 | `self.safe_move` | `agentic_core/L5_safety/utils/location_healer_util.py` |
| 4 | 8 | `open` | `agentic_core/L3_orchestration/utils/state_management_util.py` |
| 5 | 7 | `open` | `agentic_core/L2_execution/utils/async_file_ops.py` |
| 6 | 6 | `cls.GOLDEN_SEAL_FILE.write_text` | `agentic_core/L0_routing/utils/core_integrity_util.py` |
| 7 | 6 | `self.resolve_collision_and_rename` | `agentic_core/L5_safety/reasoning/FileClassificationAgent.py` |
| 8 | 6 | `self.gatekeeper.safe_move` | `agentic_core/L5_safety/reasoning/hierarchy_healer.py` |
| 9 | 6 | `open` | `agentic_core/knowledge/canonical/canonical_store.py` |
| 10 | 6 | `path.write_text` | `apps_eval/reasoning/enterprise_eval_orchestrator.py` |

### Layer rollup (post-fix)

| Layer | Count |
|---|---:|
| L_APP | 414 |
| L5 | 364 - (legitimate `_wg.*` already deducted by MV fix) |
| L_RUNTIME | 129 |
| L_SL | 126 |
| L2 | 83 |
| L3 | 75 |
| L4 | 64 |
| L0 | 58 |
| L_SHARED | 57 |
| L_PG | 46 |
| L6 | 30 |
| L1 | 21 |

### W1.2 entry conditions (next session)

W1.2 must:
1. Regenerate full ADG via `python tools/generate_full_adg.py` (~15 min) so
   downstream consumers (Redis cache, P0 wave plan, run_contract_gates.py)
   see the corrected MV
2. Re-run W1.1 hotspot query against the fresh snapshot (numbers above are
   from in-place MV re-run; full regen may shift counts slightly)
3. Pick the top-10 above (or fresh equivalents) and route each through
   `agentic_core.L4_state.uwg.UniversalWriteGateway` per
   `docs/contracts/identity_propagation.md`

---

## W1.2 Investigation Block (2026-04-28) — additional MV scope findings

> ⚠️ Before ANY refactor work, the next session MUST resolve the **MV scope
> question** below. The 2026-04-28 W1.2 attempt was halted after surfacing
> evidence that a substantial fraction of the remaining 1370 "violations"
> are MV scope errors, not genuine bypasses. Refactoring them through
> heavyweight UWG `commit()` ceremony would be over-engineering.

### Evidence — `agentic_core/runtime/prove_requirements/writers.py` (rank 1, 16 violations)

This is a **runtime-proof writer** — produces test/proof artifacts. Per
`docs/reference/00B_L4_State_Archive_and_UWG/00B.7a_L4_UWG_Durable_Write_Context_Invariant.md`
the canonical "durable write" pipeline binds Exit CommitRequest → UWG →
L4 state store → audit ledger → replay snapshot → retrieval/cache
invalidation. A proof artifact written by a test harness is NOT a
durable mutation in this sense.

### Evidence — `system_learning/engines/l4_state_writer.py` (rank 2, 15 violations)

This file IS the L4 state writer abstraction. `InMemoryL4StateWriter._write()`
writes to an in-memory `dict` (single-process pipeline / test fixture).
`FileBackedL4StateWriter._write()` writes to disk but as the legitimate
backing for L4 state. In both cases the writer's class is at L4 / is the
L4 implementation; flagging its internals as "non-UWG L4 writes" is a
within-layer false positive — UWG sits inside L4 and authorizes upstream
callers, not L4's own state-store implementation.

### Evidence — `apps_eval/reasoning/enterprise_eval_orchestrator.py` (rank 10, 6 violations)

Reviewed all 3 visible `path.write_text` calls (lines 485, 509, 522):

| Line | Writes | Content type |
|---:|---|---|
| 485 | eval brief markdown | Human-readable output report |
| 509 | manifest JSON | Output artifact (run summary) |
| 522 | baseline JSON | Output artifact (regression baseline) |

These are **report artifacts**, not durable state. Routing markdown/JSON
output writes through `UWGCommitRequest + StateDiff + RollbackPlan +
ReadSurfaceRefreshPlan` is over-engineering — UWG is for L4 state
mutations needing authorization, locks, audit, refresh propagation; it is
not the right hammer for "write a markdown report to disk".

### Three distinct MV scope problems (in addition to W1.1's symbol-detection bug)

| # | MV problem | Approx false-positive count |
|---|---|---:|
| 1 | ✅ FIXED — symbol-based UWG detection | 117 (resolved in `ad0ee4f`) |
| 2 | Within-L4 writes (L4 source layer writing to L4 surfaces) | ~64 (L4 layer) + ~126 (L_SL) = **~190** |
| 3 | Report artifact writes (markdown/JSON to reports/ outputs/) | ~414 (L_APP layer, mostly orchestrator output renderers) |
| 4 | Healer self-rename writes (L5 file movers) | ~20 (`safe_move`, `resolve_collision_and_rename`) — design intent ambiguous |

### Architectural decision needed

The original 2026-04-28 Author-Gate offered options A=accept-as-debt /
B=refactor / C=hybrid under the assumption of "1502 genuine bypasses".
With evidence that ≥50% are MV scope errors, the choice deserves
revisiting. The refactor-class options remain open BUT a new option
emerges:

- **D — Tighten MV scope** to match the canonical durable-write definition
  (DurableWriteContext digest pipeline). Filter `mv_write_sovereignty_paths`
  to exclude (a) within-layer writes where `src.layer == dst.layer` AND the
  caller is the layer's canonical writer abstraction, (b) report artifact
  writes targeting `reports/`, `outputs/`, `proof/`, `prove_requirements/`,
  (c) test-fixture in-memory dict mutations. Estimated post-fix violation
  count: **~50–200 genuine bypasses** (sized for a single-wave refactor
  rather than a multi-week one).

Option D may obviate W1/W2/W3 of this plan. Surface to user before
continuing.

---

## W1.2 Outcome (2026-04-28) — option D selected, MV scope tightened

User selected **option D** at the revisited Author-Gate. Three new MV
scope filters landed in commit `69d22c9`:

| Filter | Mechanism | Net violation drop |
|---|---|---:|
| Non-durable target paths | `_NON_DURABLE_WRITER_PATH_FRAGMENTS` matching `/runtime/prove_requirements/`, `/proof/`, `/outputs/`, `/reports/` | (combined) |
| Canonical layer-writer abstractions | `_CANONICAL_LAYER_WRITER_PATH_FRAGMENTS` matching `/L4_state/`, `system_learning/engines/l4_state_writer`, `/L4_state/uwg/` | **−256** |
| Nested tests + scripts | `src.resolved_path NOT LIKE '%/tests/%' AND NOT LIKE '%/scripts/%'` | **−209** |

### Cumulative numerical impact (snapshot `04282026_2000`)

| Stage | is_new=1 violations | Δ from prior |
|---|---:|---:|
| Pre-W1.1 (initial baseline) | 1483 | — |
| Post-W1.1 symbol-detection fix | 1370 | −113 |
| Post-W1.2 filters #1+#2 (non-durable + canonical) | 1114 | −256 |
| Post-W1.2 filter #3 (nested tests/scripts) | **905** | −209 |
| **Total reduction** | **−578 (−39%)** | |

### Regression test coverage (8/8 passing in `TestPhaseAWriteSovereignty`)

- `test_write_sovereignty_non_uwg_flagged` (existing baseline)
- `test_write_sovereignty_uwg_detected_by_symbol` (W1.1)
- `test_write_sovereignty_uwg_symbol_variants` (W1.1)
- `test_write_sovereignty_excludes_non_durable_targets` (W1.2 D)
- `test_write_sovereignty_excludes_canonical_layer_writers` (W1.2 D)
- `test_write_sovereignty_excludes_nested_tests_and_scripts` (W1.2 D)
- 2 additional pre-existing tests in the group

### Top-15 GENUINE residual hotspots after W1.2 (ready for W2 refactor)

| Rank | Count | Layer | Symbol | File |
|---:|---:|---|---|---|
| 1 | 11 | L5 | `self.safe_move` | `agentic_core/L5_safety/utils/location_healer_util.py` |
| 2 | 8 | L3 | `open` | `agentic_core/L3_orchestration/utils/state_management_util.py` |
| 3 | 7 | L2 | `open` | `agentic_core/L2_execution/utils/async_file_ops.py` |
| 4 | 6 | L0 | `cls.GOLDEN_SEAL_FILE.write_text` | `agentic_core/L0_routing/utils/core_integrity_util.py` |
| 5 | 6 | L5 | `self.resolve_collision_and_rename` | `agentic_core/L5_safety/reasoning/FileClassificationAgent.py` |
| 6 | 6 | L5 | `self.gatekeeper.safe_move` | `agentic_core/L5_safety/reasoning/hierarchy_healer.py` |
| 7 | 6 | L_PG | `open` | `agentic_core/knowledge/canonical/canonical_store.py` |
| 8 | 6 | L_APP | `path.write_text` | `apps_eval/reasoning/enterprise_eval_orchestrator.py` |
| 9 | 6 | L_APP | `path.write_text` | `apps_rfp/reasoning/enterprise_orchestrator.py` |
| 10 | 6 | L_SL | `open` | `system_learning/ml_integration/training_pipeline.py` |
| 11 | 5 | L1 | `open` | `agentic_core/L1_cognition/reasoning/ml_decision_support/inference/shadow_logger.py` |
| 12 | 5 | L_APP | `orch.run` | `apps_eval/engines/scenario_runner.py` |
| 13 | 4 | L2 | `open` | `agentic_core/L2_execution/utils/analysis_ops_util.py` |
| 14 | 4 | L3 | `mkdir` | `agentic_core/L3_orchestration/utils/state_management_util.py` |
| 15 | 4 | L5 | `gatekeeper.safe_move` | `agentic_core/L5_safety/reasoning/ArchitectureGovernorAgent.py` |

These are the genuine durable-write candidates. Most cluster into 3 themes:

1. **L5 file-system healers** (`safe_move`, `resolve_collision_and_rename`,
   `gatekeeper.safe_move`) — file relocation operations that ARE writes; design
   intent ambiguous (do file movers need UWG ceremony?).
2. **L0/L2/L3 utility-layer `open`/`mkdir`** — direct file IO from utility
   modules. These are genuine bypass candidates.
3. **L_APP enterprise orchestrators `path.write_text`** — write to dynamic
   destination paths; the destination MAY be a report/output (excluded by
   target path filter at runtime resolution time, but ADG sees only the
   compile-time symbol).

### W2 entry conditions (next session)

W2 should:
1. Regenerate full ADG (`python tools/generate_full_adg.py` ~15min) so the
   tightened MV reaches downstream consumers
2. Triage the 905 residue:
   - Group A: L5 file-system healers — surface to user; design decision
     whether file-movers need UWG ceremony
   - Group B: L0/L2/L3 utility-layer file IO — refactor through UWG
   - Group C: L_APP `path.write_text` — investigate per-site whether
     destination is a report (further MV exclusion) or genuine state write
