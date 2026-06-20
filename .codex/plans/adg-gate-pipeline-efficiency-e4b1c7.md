---
plan_id: adg-gate-pipeline-efficiency-e4b1c7
plan_type: refactor
touches_agentic_core: false
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# ADG Generator — Gate Efficiency + Coverage Hardening

Make the ADG generation pipeline run every CI gate, materialized-view (MV) phase, and graph-DB-lite projection **provably and efficiently** — pin the dispatcher to the current run's snapshot, collapse redundant SQLite connections, parallelize the gate fleet, and de-duplicate the inline/dispatcher witness check — without breaking the 16-gate manifest contract.

> **plan_id discipline**: marker lines use `plan=adg-gate-pipeline-efficiency-e4b1c7`.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: COMPLETE
CURRENT_WAVE: DONE
LAST_COMPLETED_WAVE: W4
LAST_UPDATED: 2026-06-07

## Finalization (2026-06-07)

Delivered + committed (`08453ed391`, 9 files): **W1.1** dispatcher snapshot pin,
**W1.2** MV fail-fast guard + MV-present probe, **W1.3** MV progress bar, **W2.1**
single shared WAL connection across MV phases A–F. Verified: 191 unit tests pass,
manifest 16-gate contract intact, `materialize_all_views` produced all 52 MV
tables on the live snapshot.

**Deferred / reverted with evidence** — `W2.2` (P0-check conn coalesce: not worth
rewriting a safety-gate's fail-closed flow for 2 opens/run); `W3.1` (dispatcher
threading: **REVERTED**, warm parallel ~50s vs serial ~42.5s, GIL-bound gates —
determinism passed but no speedup); `W3.2` (witness de-dup: coverage-only
follow-up, not started per user "finalize now").

**Corrected finding:** total ADG run is dominated by MV materialization (~530s
sequential `CREATE TABLE AS SELECT`); the dispatcher (~45s) is a small slice and
not profitably threadable. The pipeline was already well-optimized for
throughput; the available wins were correctness/coverage, now delivered.

PLAN_COMPLETE: plan=adg-gate-pipeline-efficiency-e4b1c7 note="W1+W2.1 delivered+committed; W2.2/W3.2 deferred, W3.1 reverted (measured slower); ADG perf is MV-dominated"

---

## Context (SCQA)

- **Situation** — `tools/generate/generate_full_adg.py` (2,493 lines; the path the user referenced, `tools/adg/generate_full_adg.py`, is a deprecation shim) drives ADG generation. ADG CI gates run in three places: (1) **inline** Tier-1/Tier-2 validations via `run_recorded_validation`; (2) a **subprocess dispatcher** `python -m ops_scripts.ci.adg_gates.run` running 51 gates (12 CANONICAL + 39 WIRING) in-process **serially**; (3) a **parallel post-ADG chain** in `main()`. MVs (`_materialize_adg_views`, Phase A–F = 42 tables) and graph-DB-lite (P6 `adg_graph_<ts>.sqlite` + P6b NetworkX) materialize **before** the dispatcher — ordering is correct.
- **Complication** — Five concrete inefficiencies / coverage gaps: **(a)** the dispatcher re-resolves "latest snapshot" by glob/mtime instead of using the just-built `prod_sqlite_path` — a redundant glob and a race risk; **(b)** `_materialize_adg_views(paths.sqlite)` at line 1093 is **unguarded** — if MVs fail, a committed snapshot is left with no MVs and every MV-dependent gate then errors, with no skip-ledger trail; **(c)** the inline `_check_witness_tier_gates` queries the **exact same 6 `mv_*` views** as the dispatcher's `gate_p1_architecture_witness` (100% duplicate, plus drift risk); **(d)** MV refresh opens **6 separate SQLite connections** (one per phase) and emits **no progress bar** despite being a >5 s step (§16); **(e)** inline `_check_p0_violations` opens **3 connections**. The dispatcher's 51-gate fleet runs **serially** even though each gate uses an isolated read-only/immutable connection.
- **Question** — How do we guarantee all gates + MVs + graph-DB-lite run on the current snapshot, while cutting wall-clock, **without** violating the gate-invocation manifest contract (16 `REQUIRED_GATES`) that CI certification depends on?
- **Answer** — Stage the work by risk: (W1) correctness/coverage guards that are nearly free; (W2) connection consolidation; (W3) the two higher-leverage but contract-sensitive changes (dispatcher fleet parallelization + witness de-dup) behind Author-Gate decisions; (W4) measured verification against the manifest contract and test suite.

---

## Status Tables

### Wave Progress

| Wave | Focus | Status | Tests Added | Files Changed |
|------|-------|--------|-------------|---------------|
| W1 | Correctness & coverage (snapshot pin, MV guard, MV progress bar) | ✅ DONE | 0 (191 existing pass) | 2 |
| W2 | SQLite connection consolidation (MV single-conn ✅; inline P0 coalesce ⏸ deferred) | ✅ DONE | 0 | 7 |
| W3 | Throughput & de-dup — W3.1 ❌ REVERTED (measured slower); W3.2 ⏳ pending decision | 🔄 IN PROGRESS | 0 | 0 |
| W4 | Verification & evidence (manifest contract ✅, 191 tests ✅, live MV run ✅; full cert regen deferred — parallel tree work) | ✅ DONE | 0 | 0 |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W1.1 | Pin `ADG_SNAPSHOT` + `--output-dir` for the dispatcher subprocess | ✅ DONE |
| W1.2 | Guard MV materialization + skip-ledger; fail-fast MV-present check before dispatcher | ✅ DONE |
| W1.3 | Progress bar on MV refresh (orchestrator §16) | ✅ DONE |
| W2.1 | Thread one SQLite connection through MV phases A–F | ✅ DONE |
| W2.2 | Coalesce inline `_check_p0_violations` 3→1 connection | ⏸ DEFERRED (see note) |
| W3.1 | **Author-Gate**: dispatcher fleet parallelization (ThreadPoolExecutor) | ❌ REVERTED — warm parallel ~50s vs serial ~42.5s (GIL-bound gates); determinism passed but no speedup |
| W3.2 | **Author-Gate**: witness-tier inline/dispatcher de-dup (manifest-preserving) | 🔲 TODO |
| W4.1 | Timed certification smoke run + manifest 16-gate contract check | 🔲 TODO |
| W4.2 | Test suite (audit wrapper, manifest recorder, MV) + memory writeback | 🔲 TODO |

---

## Out Of Scope

- **Removing inline `_check_structural_conformance` (SC-1..SC-8) / `_check_agentic_antipatterns` (AP-1..AP-18)** despite overlap with dispatcher gates. These **INSERT into the `violations` table** (`class='structural_conformance'` / `'agentic_antipattern'`) — a side effect consumed downstream by P-views and the burndown report. Removing them changes data semantics, not just timing. **Audit-only here** (Gap Register GAP-3); any change is a separate plan.
- Changing the `REQUIRED_GATES` registry, manifest JSON schemas, or `adg_gate_results_<ts>.json` schema.
- Touching `agentic_core/**` (this plan is `L_TOOLS` / `L_OPS` only).
- The three-bucket / OTel runtime path (`ADG_THREE_BUCKET`).

---

## Wave 1 — Correctness & Coverage

WAVE_ID: W1
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

**Authorization**: NOT_REQUIRED — additive guards + env pinning; no manifest contract change, no gate removal.

**Phases**:
- **W1.1** — Pin `ADG_SNAPSHOT`+`--output-dir` for dispatcher | ~4K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W1.2** — Guard MV refresh + fail-fast MV-present check | ~6K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W1.3** — MV refresh progress bar | ~3K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- Dispatcher provably loads the exact `adg_indexed_<ts>.sqlite` built this run (logged + asserted), not a glob result.
- An MV materialization failure produces a recorded `adg_pipeline_skips_<ts>.jsonl` entry **and** a fail-fast before the dispatcher runs (no silent stranded snapshot).
- MV refresh shows a §16-compliant progress bar.

---

## Wave 2 — SQLite Connection Consolidation

WAVE_ID: W2
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: B

**Authorization**: NOT_REQUIRED — internal connection plumbing; identical SQL/semantics, identical outputs.

**Phases**:
- **W2.1** — Single connection threaded through MV phases A–F | ~10K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W2.2** — Coalesce inline P0 violation checks 3→1 connection | ~5K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- MV materialization opens **1** connection (was 6); `materialize_all_views` row-count dict byte-identical to baseline on the same snapshot.
- `_check_p0_violations` opens **1** connection (was 3); identical pass/fail verdict and violation counts.

---

## Wave 3 — Throughput & De-duplication (Author-Gate)

WAVE_ID: W3
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: REQUIRED
CHECKPOINT: C

**Authorization**: REQUIRED — both phases are `architecture_choice` decisions with reversibility/blast-radius trade-offs against the manifest contract. **Both Author-Gates resolved 2026-06-07** (see Decisions Captured below); execution still pending overall plan approval.

AG_QUEUE_SEED: plan=adg-gate-pipeline-efficiency-e4b1c7 id=ag_w3_1_dispatcher_parallel depends_on= title=dispatcher-fleet-parallelization
AG_QUEUE_SEED: plan=adg-gate-pipeline-efficiency-e4b1c7 id=ag_w3_2_witness_dedup depends_on=ag_w3_1_dispatcher_parallel title=witness-tier-inline-dispatcher-dedup

**Decisions Captured**:
- **W3.1** → `ThreadPoolExecutor` fan-out (confidence 0.85). Rationale: reuse the in-production `_run_post_adg_gates_parallel` pattern; gates use isolated read-only/immutable connections; SQLite frees the GIL on queries. Mitigations mandatory: importlib `_MODULE_CACHE` pre-warm (single-threaded) before fan-out + result re-sort by fleet index so classification, ordering, and `overall_exit_code` are byte-identical to serial.
- **W3.2** → **Verify-then-collapse** (confidence 0.78). Rationale: never trade coverage for a small perf win. Step 1 PROVES inline `_check_witness_tier_gates` ≡ dispatcher `gate_p1_architecture_witness` (Class A/B + schema-regression). If equivalent → inline reads dispatcher `adg_gate_results` row + still records the `witness_tier_gates` manifest gate. If NOT equivalent → fall back to "keep both" + document (no collapse). Coverage is never reduced.
- `DECISION_CAPTURED:` markers emitted in chat 2026-06-07; ledger precedent was `none` (COLD_CORPUS).

**Phases**:
- **W3.1** — Parallelize the 51-gate dispatcher fleet | ~12K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W3.2** — Witness-tier inline/dispatcher de-dup | ~10K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- W3.1: fleet wall-clock drops materially (target ≥40% on the 51-gate loop); **result ordering, classification, and `overall_exit_code` are byte-identical** to the serial run on a fixed snapshot; gate isolation preserved (each gate keeps its own read-only/immutable connection).
- W3.2: `witness_tier_gates` still appears in the manifest with correct phase/kind/status; the same Class A/B conditions are still enforced; one implementation of the check, not two divergent ones.

---

## Wave 4 — Verification & Evidence

WAVE_ID: W4
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: D

**Phases**:
- **W4.1** — Timed certification smoke run + 16-gate manifest contract check | ~6K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W4.2** — Targeted test suite + memory writeback | ~5K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- `python tools/adg/run_full_adg_audit.py --mode certification --format both` exits per pre-change baseline; manifest contains all 16 `REQUIRED_GATES`.
- Before/after wall-clock recorded; net improvement reported with the breakdown per wave.
- Named test files all pass, 0 regressions.

---

## Execution Details

### W1.1 — Pin `ADG_SNAPSHOT` + `--output-dir` for the dispatcher subprocess
**Scope**: `tools/generate/generate_full_adg.py` ~L1159–1173 (the `_sp.run([... "ops_scripts.ci.adg_gates.run", "--json-only"])` call).
- Pass `env={**os.environ, "ADG_SNAPSHOT": str(prod_sqlite_path)}` and `"--output-dir", str(adg_artifacts_dir)` to the subprocess.
- `ADG_SNAPSHOT` is already honored by `latest_snapshot()` (`ops_scripts/ci/_adg_wiring_gate_base.py:95–100`) — no dispatcher CLI change needed for the pin. Add one assertion log line confirming the dispatcher's resolved snapshot == `prod_sqlite_path` (parse from `adg_gate_results_<ts>.json` or log).
- **Risk**: minimal — env-only; falls back to glob if unset.

### W1.2 — Guard MV materialization + fail-fast MV-present check
**Scope**: `tools/generate/generate_full_adg.py` ~L1093.
- Wrap `_materialize_adg_views(paths.sqlite)` so a failure is recorded via `_record_pipeline_skip(..., layer="MV", name="materialize_all_views", ...)` AND then fails fast (MVs are a hard dependency for the dispatcher; unlike P4/P5 this is **not** non-blocking). Keep the snapshot committed but exit non-zero with a clear MV-missing message rather than letting 12 P0 gates error opaquely downstream.
- Add a lightweight `mv_*` presence probe (e.g. `mv_handoff_witness_tiers`, `mv_write_sovereignty_paths`) immediately before the dispatcher invocation; if absent, fail with a pointed message referencing `check_snapshot_has_mvs.py` (§22).

### W1.3 — MV refresh progress bar
**Scope**: `tools/generate/materialized_views/orchestrator.py` `materialize_all_views`.
- Wrap the 6 phase calls in a `tqdm` bar (`desc="ADG-MV phases", unit="phase", total=6`). No semantic change.

### W2.1 — Single connection through MV phases A–F
**Scope**: `tools/generate/materialized_views/{orchestrator.py, sqlite_helpers.py, phase_a..f_*.py}`.
- Add `connect_sqlite_for_mv` once in the orchestrator; pass the open `conn` into each `materialize_phase_*` (add an optional `conn` param; phases open their own only when `conn is None`, preserving standalone `python -m` usage). Phases already run serially in dependency order, so a single connection is safe.
- Keep `commit()` cadence between phases (later phases read earlier phases' tables).

### W2.2 — Coalesce inline P0 violation checks 3→1  ⏸ DEFERRED (2026-06-07)
**Scope**: `tools/generate/validation/gates.py` `_check_p0_violations` (~L68–187).
- Original intent: open one read-only connection; run the violates / in_cycle / dynamic_exec queries against it instead of three separate `sqlite3.connect()` calls.
- **DEFERRED — engineering judgment.** Coalescing requires deep re-nesting of the guardian-filter loop inside the fail-closed control flow of a **P0 SAFETY_GATEKEEPER gate**, for a saving of **2 connection-opens on a gate that runs once per ADG generation**. Per constitutional "do not weaken a gate" + scope-containment "no gold-plating", the risk (subtly altering P0 fail-closed semantics) outweighs the microsecond reward. The 3 `with sqlite3.connect()` blocks are read-only and already correct. Revisit only if profiling shows connection-open cost is material (it is not). User may override.

### W3.1 — Dispatcher fleet parallelization (Author-Gate)
**Scope**: `ops_scripts/ci/adg_gates/run.py` main fleet loop (~L527–537).
- Replace the serial `for spec in tqdm(fleet)` with a bounded `ThreadPoolExecutor` (mirrors the existing `_run_post_adg_gates_parallel` pattern). Each gate already opens its **own** `?mode=ro&immutable=1` connection with `PRAGMA query_only=ON` (`gate_base.py:175–180`) / `?mode=ro` (`_adg_wiring_gate_base.py:156–159`), so per-gate isolation holds across threads; SQLite releases the GIL during queries.
- Preserve deterministic output: collect results, re-sort by fleet index before classification/printing; `overall_exit_code` computed from the collected rows exactly as today.
- Guard `_MODULE_CACHE` (importlib module cache) for thread-safe population (pre-warm class loads single-threaded, or lock).
- **Decision LOCKED (Author-Gate 2026-06-07): ThreadPoolExecutor.** Determinism + module-cache pre-warm mitigations above are mandatory acceptance criteria, not options.

### W3.2 — Witness-tier inline/dispatcher de-dup (Author-Gate)
**Scope**: `tools/generate/validation/gates.py` `_check_witness_tier_gates` (~L1666) + call site in `generate_full_adg.py` (~L1292).
- The dispatcher (which includes `11_architecture_witness`) runs **before** the inline witness check, so the inline check can read the dispatcher's `adg_gate_results_<ts>.json` for that gate's verdict instead of re-querying the 6 views — **while still emitting the `witness_tier_gates` manifest record** (preserving the `REQUIRED_GATES` contract) and preserving the schema-regression / missing-table fail-fast.
- **Decision LOCKED (Author-Gate 2026-06-07): verify-then-collapse.** Hard pre-condition: a parity check (new test) must prove inline ≡ dispatcher witness semantics (Class A/B + schema-regression + missing-table fail-fast) BEFORE the inline body is replaced with a dispatcher-result reader. If parity fails, emit `DISCOVERED_SCOPE` + keep both implementations and document the divergence — do NOT collapse.

### W4.1 — Timed certification smoke run + manifest contract check
**Commands**:
```bash
# Baseline timing BEFORE any edit (capture once at W1 start), then re-run after each wave:
python tools/adg/run_full_adg_audit.py --mode certification --format both
# Inspect manifest contains all 16 REQUIRED_GATES:
python -c "import json,glob; ... assert REQUIRED ⊆ recorded"   # scripted check, not -c quote hazard: use a temp .py
```

### W4.2 — Targeted tests + writeback
**Commands**:
```bash
python -m pytest tests/unit/tools_adg/test_run_full_adg_audit.py \
  tests/unit/tools/generate/test_gate_manifest_validation_recording.py \
  tests/unit/tools/generate/test_generate_full_adg_failfast.py \
  tests/unit/ops_scripts/ci/adg_gates/ -q
```

---

## ADG_HOTSPOT_REPORT

Snapshot: adg_indexed_05272026_1632.sqlite (node_count=180,057, edge_count=1,068,351; graph projection fresh).

| rank | file | layer | role | archetype | surfaces | note |
|------|------|-------|------|-----------|----------|------|
| 1 | tools/generate/generate_full_adg.py | L_TOOLS | pipeline orchestrator | ORCHESTRATOR | Observability | 22 ADG nodes (module + symbols); governs gate dispatch + MV/graph-lite sequencing |
| 2 | ops_scripts/ci/adg_gates/run.py | L_OPS | gate fleet dispatcher | ORCHESTRATOR | Observability | 1 module node; runs 51 gates |
| 3 | tools/generate/materialized_views/*.py | L_TOOLS | MV builders | STATE_NODE | State | 6 phases, 42 tables |
| 4 | tools/generate/validation/gates.py | L_TOOLS | inline validations | SAFETY_GATEKEEPER | Security/State | houses witness/SC/AP/P0 checks |

**Layer note**: All touched files are `L_TOOLS` / `L_OPS` (ADG governance tooling), **not** the L0–L6 runtime spine. The L0/L5 ×2.0 layer multipliers do not apply; the real blast-radius control for this change is the **gate-invocation manifest contract** (16 `REQUIRED_GATES`), tabulated below, plus the `adg_gate_results_<ts>.json` schema. No `agentic_core/**` node is in scope, so no Core-Addition Author-Gate / migration receipt is required.

## ADG_GRAPH_LAYER_EVIDENCE

### Materialized Views consulted (the subject matter of this plan)
- **mv_handoff_witness_tiers / mv_cross_cutting_witness_tiers** — consumed by BOTH inline `_check_witness_tier_gates` and dispatcher `gate_p1_architecture_witness` → the duplication this plan targets (W3.2).
- **mv_write_sovereignty_paths, mv_digest_reconciliation, mv_local_heal_first_breaches, mv_observability_interference_breaches** — the other 4 views queried by both surfaces.
- **mv_critical_path_segments / mv_authority_boundary_breaches / mv_capability_and_egress_gaps / …** — required-present-before-dispatcher set (W1.2 fail-fast probe targets a representative subset).

### Semantic / structural edges used
- `latest_snapshot()` resolves the dispatcher's snapshot by filesystem glob + mtime (NOT an ADG edge) — W1.1 replaces this implicit resolution with an explicit `ADG_SNAPSHOT` pin.
- Gate→MV dependency mapping (51 gates) sourced from `unified_registry.WIRING_GATES`/`CANONICAL_GATES` + each gate's `source_views`.

### Manifest contract (blast-radius control — do not break)
`REQUIRED_GATES` (16): `mcp_config_drift`, `wal_checkpoint`, `locked_files`, `wiring`, `config-ref`, `lifecycle`, `except-contract`, `test-coverage`, `p0_violations`, `p1_ratchet`, `p2_ratchet`, `dead_production_imports`, `structural_conformance`, `agentic_antipatterns`, `witness_tier_gates`, `three_bucket_manifest_quick`, `adg_gate_dispatcher`. (Source: `tools/generate/_required_gates.py`.) Every wave must leave all of these present in the gate-invocation manifest with their existing phase/kind/blocking_mode.

### ADG Provenance
ADG Provenance: backend=sqlite, snapshot=adg_indexed_05272026_1632.sqlite

---

## Gap Register

**GAP-1: Dispatcher snapshot is glob-resolved, not pinned**
- `latest_snapshot()` globs `artifacts/adg/adg_indexed_*.sqlite` by mtime; a concurrent touch on an older snapshot could mis-resolve. Addressed by W1.1 (`ADG_SNAPSHOT` pin).

**GAP-2: MV materialization is unguarded**
- `_materialize_adg_views` failure leaves a committed snapshot with no MVs and no skip-ledger entry; the 12 MV-dependent P0/P1 gates then error opaquely. Addressed by W1.2.

**GAP-3: SC/AP inline checks overlap dispatcher gates BUT write `violations` rows (NOT removable here)**
- `_check_structural_conformance` (SC-1 gravity, SC-5 spine, SC-8 trace) and `_check_agentic_antipatterns` (AP-1 text-to-action, AP-3 provider bypass) overlap dispatcher gates, but INSERT into `violations` (consumed by P-views/burndown). **Audit-only**; removal deferred to a separate plan with downstream-consumer analysis.

**GAP-4: Witness-tier check exists in two divergent implementations**
- Drift risk between inline and dispatcher implementations of the same 6-view check. Addressed by W3.2 (single source of truth, manifest preserved).

---

## Definition of Done

DoD-1: Dispatcher provably runs on the current run's snapshot
- Evidence: log line + assertion that dispatcher-resolved snapshot == `prod_sqlite_path`; `adg_gate_results_<ts>.json` references the current `<ts>`.
- Status: TODO

DoD-2: Smoke run (executable surface touched) exits 0 and produces artifacts
- Evidence: `python tools/adg/run_full_adg_audit.py --mode certification --format both` exits per baseline; `artifacts/adg/adg_gate_invocation_manifest_<ts>.json` + `adg_gate_results_<ts>.json` produced.
- Status: TODO

DoD-3: Test suite green, zero regressions
- Evidence: `pytest tests/unit/tools_adg/test_run_full_adg_audit.py tests/unit/tools/generate/test_gate_manifest_validation_recording.py tests/unit/ops_scripts/ci/adg_gates/ -q` → all pass, 0 fail.
- Status: TODO

DoD-4: Manifest 16-gate contract intact + no new ADG violations
- Evidence: scripted check asserts `required_gate_names()` ⊆ manifest gate names; `python ops_scripts/ci/run_contract_gates.py` exits 0.
- Status: TODO

DoD-5: Measured speedup + memory/ADR writeback
- Evidence: before/after wall-clock table (MV refresh, dispatcher fleet, full run); `mem:` ProceduralPattern updated; sibling note in `.codex/rules` if gate behavior changed.
- Status: TODO

DoD-6: Connection-count reduction verified
- Evidence: MV path opens 1 SQLite connection (was 6); inline P0 opens 1 (was 3) — confirmed by instrumented count or code review diff.
- Status: TODO

---

## Scope Expansion Authorization

```
DISCOVERED_SCOPE: plan=adg-gate-pipeline-efficiency-e4b1c7 wave=<N> phase=<M> gap="<what>" impact="<severity>"
AUTHORIZATION_DECISION: plan=adg-gate-pipeline-efficiency-e4b1c7 decision=<ACCEPTED|DEFERRED|SPLIT_TO_NEW_PLAN|REJECTED> authorized_by=<user|author_gate|self> decisive_reason="<why>"
SCOPE_EXPANSION: plan=adg-gate-pipeline-efficiency-e4b1c7 reason="<summary>" added="<waves/phases>" authorized="yes"
```

> **Documentation ≠ Authorization.** SC/AP removal (GAP-3) and any `REQUIRED_GATES` change require SPLIT_TO_NEW_PLAN.

---

## Marker Quick Reference

```
WAVE_START: plan=adg-gate-pipeline-efficiency-e4b1c7 wave=<N>
WAVE_COMPLETE: plan=adg-gate-pipeline-efficiency-e4b1c7 wave=<N> note="+N tests, N files, scope=<summary>"
PHASE_COMPLETE: plan=adg-gate-pipeline-efficiency-e4b1c7 phase=<W1.1>
PLAN_COMPLETE: plan=adg-gate-pipeline-efficiency-e4b1c7 note="<final outcome>"
```
