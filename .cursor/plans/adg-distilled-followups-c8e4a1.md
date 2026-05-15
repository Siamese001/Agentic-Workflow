# ADG Distilled Follow-ups — Gate Aggregation + Wiring Gap Detection

**Slug:** `adg-distilled-followups-c8e4a1`
**Status:** Completed (W1 + W2 done 2026-05-06)
**Authored:** 2026-05-06
**Tier:** T2 (cross-file, additive tooling, no production code mutation)
**Supersedes:** `adg-enforcement-hardening-p1-p8-7e9c4a`, `adg-mcp-reopen-hardening-e8f9a0`, `adg-fail-aggregating-gate-chain-9d4e1f`, `adg-repair-orchestrator-enhancement-02c1fc` (all archived 2026-05-06 with pointer to this plan)

---

## 1. Why This Plan Exists

The four predecessor plans were drafted in 2026-04 against an ADG state that has since shifted:

- **ADG is now structurally clean** (snapshot `adg_indexed_05052026_0722.sqlite`): 0 P0 issues, 0 layer violations, 0 circular imports.
- **51 P0 Phase-B violations that motivated `adg-deferred-investigations` are gone** (verified 2026-05-06; that plan was archived).
- **No recent MCP reopen incidents** observed in session logs — `adg-mcp-reopen-hardening` premise is speculative.
- **Most "50 antipattern violations" are detector false-positives on constants** (`OSError`, `REPO_ROOT`, `SOFT_CAP`) — chasing them is busy work.

Two concerns survive ruthless filtering:

1. **Gate chain fails-fast** — a bad run reports the first failure and hides everything downstream. CI debugging is N round-trips when it could be one.
2. **No detection for runtime-import bugs** — dead imports, unresolved imports, port-adapter gaps compile fine but fail at runtime. With 140K nodes / 863K edges, this is a real risk surface that no current gate checks.

These are the only two follow-ups worth scoping. Everything else from the predecessor plans is dropped.

---

## 2. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---:|---|---|---|
| W1 | P1, P2 | Fail-aggregating gate chain in `generate_full_adg.py` + consolidated report | ~6,000 | `_fail_closed_gate` + `record_or_exit` infrastructure already exists | ✅ DONE (verified 2026-05-07 — all violation paths already route through `record_or_exit`; drain + summary table already in `main()`) | Single run surfaces ALL gate violations; final summary table prints regardless of individual gate outcomes |
| W2 | P3, P4 | New detection tool `tools/adg/adg_wiring_gap_check.py` + tests | ~5,000 | ADG SQLite snapshot exposes `instantiates`, `imports`, `dead_import`, `unresolved` edge kinds | ✅ DONE — `tools/adg/adg_wiring_gap_check.py` (4 modes, `--gate`/`ADG_WIRING_GAP_GATE=1`), 21 tests, registered as WG1 in `run_contract_gates.py` | 4 detection modes (registry-gaps, instantiation-orphans, port-adapter-gaps, dead-imports); `--gate` flag exits non-zero on critical findings |

---

## 3. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---:|---|---|
| P1 | Wire defer infrastructure into all 13 gate violation paths in `generate_full_adg.py` | `tools/generate_full_adg.py`, `tools/generate/validation/gates.py` | Defer currently only triggers on infrastructure exceptions, not on `if violations > 0:` paths. Need to route the latter through `record_or_exit` too. | 3,500 | ✅ DONE — all violation paths verified to call `record_or_exit`; 3 remaining `sys.exit` calls are intentional integrity-boundary hard-fails (documented in gate comments) |
| P2 | Final aggregated summary table at end of `generate_full_adg.py main()` | `tools/generate_full_adg.py` (drain block ~line 1747) | Need to consolidate per-gate violation counts + top-N offenders into one printed table; preserve existing per-gate logs | 2,500 | ✅ DONE — drain block at lines 1976-1995 prints inline summary + calls `format_summary_table()` rendering full markdown table |
| P3 | New `tools/adg/adg_wiring_gap_check.py` with 4 detection modes | `tools/adg/adg_wiring_gap_check.py` (new), `tests/unit/tools/adg/test_adg_wiring_gap_check.py` (new) | Same archetypal shape as existing `adg_fanin_isolation_check.py`; queries `nodes`/`edges` directly; no MV dependency | 3,000 | ✅ DONE — 4 modes implemented; CRITICAL severity on dead-imports; WARN on orphans/adapter-gaps/registry-gaps; schema-guard for stub snapshots |
| P4 | `--gate` mode + CI registration | Above file + `ops_scripts/ci/run_contract_gates.py` registration | Decide which findings are "critical" (exit 1) vs advisory (WARN). Initial recommendation: unresolved imports = critical; dead imports / orphan instantiations = WARN | 2,000 | ✅ DONE — `--gate` flag + `ADG_WIRING_GAP_GATE=1` env var; registered as WG1 advisory entry in `wiring_gates` list |

---

## 4. Out Of Scope (explicitly dropped from predecessor plans)

- ❌ **Plan-evidence stop-equivalent hook** (Plan 1 P2) — speculative, no demonstrated need.
- ❌ **Pre-prompt grep-for-deps warning** (Plan 1 P4) — already covered by §28 ADG-first rule + audit hook.
- ❌ **Hook chain latency telemetry** (Plan 1 P5) — premature optimization.
- ❌ **PEP/PDP scaffold** (Plan 1 P6) — premature abstraction.
- ❌ **MCP reopen hardening** (Plan 2 W1-W4) — no recent incident; defer to actual failure.
- ❌ **P2 ratchet recalibration** (Plan 3 I1) — orthogonal; handled separately if/when ratchet trips.
- ❌ **`--continue-on-p0` rename** (Plan 3 I5) — cosmetic.
- ❌ **Notion P-bands rescore** (Plan 3 I8) — orthogonal to gate chain.
- ❌ **SQLite analyzer query repair** (Plan 4 W1-W2) — premise was P0 violations existed; they don't.
- ❌ **P1/P2 repair rules** (Plan 4 W3) — auto-fix infrastructure for problems that don't currently exist.
- ❌ **`auto_fix_p1_p2.py` archival** (Plan 4 W4) — bundled with W3.

---

## 5. Phase Detail

### P1 — Defer infrastructure on violation paths

**Current state** (`tools/generate/validation/gates.py:53-65`):
```python
def _fail_closed_gate(...):
    try:
        result = gate_fn(...)
        if violations > 0:
            sys.exit(1)   # <-- fail-fast, blocks downstream gates
    except (sqlite3.Error, OSError, json.JSONDecodeError, ValueError) as e:
        record_or_exit(...)   # <-- defer only on exceptions
```

**Target state**:
```python
def _fail_closed_gate(...):
    try:
        result = gate_fn(...)
        if violations > 0:
            record_or_exit(gate_name, violation_summary, exit_code=1)   # always defer
    except (sqlite3.Error, OSError, json.JSONDecodeError, ValueError) as e:
        record_or_exit(...)
```

**Acceptance**: a run with multiple known violations produces records for ALL of them in `_shared_deferred_exit_code`'s drain, not just the first.

### P2 — Consolidated final report

After the existing drain block (`generate_full_adg.py:1747-1772`), append:

```
================================================================
  ADG GATE CHAIN — RUN SUMMARY
================================================================
  Snapshot: adg_indexed_<ts>.sqlite (<n> nodes, <m> edges)
  Total gates run: 13
  Gates passed: <p>
  Gates with violations: <v>
  Gates with infra errors: <e>

  Top violations by severity:
    [P0] <gate_name>: <count> — <top_offender>
    [P1] <gate_name>: <count> — <top_offender>
    ...

  Final exit code: <rc>
================================================================
```

**Acceptance**: summary prints unconditionally at end of run; cite gate names + counts + first offender per gate.

### P3 — `tools/adg/adg_wiring_gap_check.py` with 4 modes

Same shape as `tools/adg/adg_fanin_isolation_check.py`. Modes:

- `--registry-gaps` — Agent/Provider/Strategy classes with no registry importer (SQL: classes whose path matches `*Agent.py`/`*Provider.py`/`*Strategy.py` but no edge from any `*registry*.py` file)
- `--instantiation-orphans` — production classes with zero `instantiates` edges from production code
- `--port-adapter-gaps` — files in `*/ports/*` with no `*/adapters/*` importer + adapters with zero production fan-in
- `--dead-imports` — `edge_kind = 'dead_import'` and `edge_kind = 'unresolved'` in production paths

CLI:
```
python tools/adg/adg_wiring_gap_check.py --all
python tools/adg/adg_wiring_gap_check.py --port-adapter-gaps --json > gaps.json
python tools/adg/adg_wiring_gap_check.py --gate     # CI mode
```

### P4 — `--gate` mode + CI registration

Critical (exit 1):
- Any `unresolved` edge in production code (real `ImportError` risk)
- Any port in `*/ports/*` with literally zero adapter importer

Advisory (WARN, exit 0):
- Dead imports
- Instantiation orphans (many false positives — abstract bases, dataclasses)
- Registry gaps (some classes are intentionally not registered)

Register in `ops_scripts/ci/run_contract_gates.py` as advisory gate `WIRING-GAPS`.

---

## 6. ADG_HOTSPOT_REPORT

| File | Archetype | Layer | Fan-in | Surface | Rationale |
|---|---|---|---:|---|---|
| `tools/generate_full_adg.py` | ORCHESTRATOR | L_TOOLS | 0 (CLI entry) | Observability Surface | Coordinates 13 gates; current fail-fast hides downstream signal |
| `tools/generate/validation/gates.py` | SAFETY_GATEKEEPER | L_TOOLS | high (every gate calls `_fail_closed_gate`) | Observability Surface | Gate-chain control point; `record_or_exit` already exists, needs broader application |
| `tools/adg/adg_wiring_gap_check.py` (new) | SAFETY_GATEKEEPER | L_TOOLS | 0 (new CLI entry) | Security/Observability Surface | New runtime-import-bug detector; complements `adg_fanin_isolation_check.py` |

---

## 7. ADG_GRAPH_LAYER_EVIDENCE

This plan ships tooling/CI hardening (no production code mutation), so constitutional §22 evidence is grounded in the MVs and edges the new tool consumes:

- **`mv_dependency_cone_risk`** — wiring gap check builds on the same dependency-cone semantics; ports without adapters are high-risk cones.
- **`mv_replay_surface_gaps`** — fail-aggregating chain plugs an observability gap (today only the first failure is replayable).
- **`mv_chokepoint_bridges`** — adapter modules acting as chokepoints between port and consumer; gaps here are exactly what P3 surfaces.

Semantic edges consulted by the new tool:
- `imports` (registry membership, port-adapter linkage)
- `instantiates` (orphan detection)
- `dead_import` / `unresolved` edge_kind values (already populated by ADG generator)

P-views not directly applicable — this is `L_TOOLS` infrastructure, not production code under classification.

**ADG Provenance**: backend=sqlite, snapshot=adg_indexed_05052026_0722.sqlite, node_count=140743, edge_count=863353

---

## 8. Success Criteria

- [ ] `python tools/generate_full_adg.py --continue-on-p0` runs end-to-end and prints aggregated final summary even when ≥2 gates fail
- [ ] All 13 gate violation paths route through `record_or_exit` (not just exception paths)
- [ ] `tools/adg/adg_wiring_gap_check.py --all` runs against current snapshot without error
- [ ] `--registry-gaps` surfaces ≥1 known unregistered Agent/Provider class (or proves none exist)
- [ ] `--port-adapter-gaps` reports `system_learning/ports/` ↔ `system_learning/adapters/` linkage status
- [ ] `--dead-imports` surfaces production-only dead/unresolved imports
- [ ] `--gate` mode exits 1 on any unresolved import in production
- [ ] Tests for both phases pass (`tests/unit/tools/generate/test_gate_aggregation.py`, `tests/unit/tools/adg/test_adg_wiring_gap_check.py`)
- [ ] No production code (`agentic_core/`, `apps_*/`) modified

---

## 9. Rollback Strategy

- **P1**: revert `gates.py` change with `git checkout`. Existing tests cover the exception-path `record_or_exit` invocation; new violation-path invocations are additive.
- **P2**: summary print is purely additive — remove the block to revert.
- **P3**: new file — `git rm` to revert with zero codebase impact.
- **P4**: gate registration in `run_contract_gates.py` is a single-line add — revert with `git checkout`.

---

## 10. Predecessor Plans Archived

The following 4 plans are archived 2026-05-06 with this plan as the consolidated successor. Disk: `git mv` to `.cursor/plans/_archive/2026-orphaned/`. Notion: Status → `Archived`, AI Summary updated to point here.

| Predecessor Slug | Reason for Archive | What Survived (in this plan) |
|---|---|---|
| `adg-enforcement-hardening-p1-p8-7e9c4a` | 7 of 8 phases speculative or done; remaining work mostly chasing antipattern false-positives | Nothing — antipattern detector noise is a separate fix |
| `adg-mcp-reopen-hardening-e8f9a0` | No demonstrated reopen failure; speculative reliability work | Nothing — defer to actual incident |
| `adg-fail-aggregating-gate-chain-9d4e1f` | 9 issues, 6 cosmetic/orthogonal; 3 substantive issues distilled here | I3 (fail-fast endemic) + I4 (defer half-wired) + I6 (no aggregated report) → P1 + P2 |
| `adg-repair-orchestrator-enhancement-02c1fc` | W1-W4 solve auto-fix problems for ADG state that's currently clean | W5 (wiring gap checks) → P3 + P4 |

---

## 11. References

- Constitutional §22 (graph-layer primary driver), §28 (ADG-first), §29 (fail-aggregating doctrine)
- `.cursor/rules/adg-graph-layer-enforcement.md`
- `.cursor/rules/adg-canonical-invariants.md`
- Predecessor plans (archived): see §10
- Companion tool template: `tools/adg/adg_fanin_isolation_check.py`

---

**Author-Gate posture**: open scope; do not implement until user explicitly approves W1 or W2.
