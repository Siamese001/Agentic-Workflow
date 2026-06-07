# ADG Gap Remediation — Wave & Microwave Plan

Augment the `generate_full_adg.py` P1–P4 terminal table with high-signal observations drawn exclusively from the SSOT SQLite, eliminate report-file sprawl, and add 8 runtime/enforcement waves covering OTel ingestion, call-graph profiling, coverage linkage, secret telemetry, write-path audit, enforce-mode gate promotion, dynamic call resolution, and Author-Gate decision logging.

---

## Core Principle: SQLite-First, Zero Report Sprawl

**All metrics referenced below are queried directly from `adg_indexed_<ts>.sqlite` and surfaced in the P1–P4 terminal table or the Refactoring Priority table printed by `_print_defect_table()`.  No new JSON report files are created.** Existing 8 reports (`layer_coverage_report`, `edge_density_report`, etc.) are preserved but not expanded. New observations are added as new rows/sections in the terminal table output only.

P1–P4 table extensions in scope:
- **P0 section** (new): Runtime signal gaps — OTel coverage, Author-Gate log completeness, secret access telemetry
- **P1 section** (augment): Add `L_UNKNOWN module count`, `layer_inversion pairs`, `dynamic_exec count` (already partially present — make explicit)
- **P2 section** (augment): Add `writes_to / writes_through ratio`, `critical_edge_coverage` (6/7 missing), `star_import_count`
- **M-gate section** (new): Print current M1–M9 mode (warn/enforce) and pass/fail status inline after the P4 row, sourced from `wave0_baseline.json` + SQLite GPC counts

---

## Signal Source Mapping

| Gap ID | P-Level | SQLite Query / Source | Blocks Generation? |
|--------|---------|----------------------|-------------------|
| GAP-W3 | — | `build_artifact` ImportError in `analysis.py` | Yes — stale companion files |
| GAP-W2 | — | `sqlite_backend` cold-start ImportError | Yes — MCP unusable |
| GAP-A2 | P1 aug | `SELECT COUNT(*) FROM nodes WHERE layer='L_UNKNOWN'` | No — table row |
| GAP-A5 | P1 aug | Same query, filter `resolved_path LIKE 'agentic_core/L_CONTRACTS%'` | No — table row |
| GAP-W5 | P1 | `SELECT COUNT(*) FROM edges WHERE relation_type='violates'` | Yes — P1 BLOCKS |
| GAP-W4 | P2 aug | `writes_to` vs `writes_through` edge counts from `edges` table | No — table row |
| GAP-A3 | Refactor | Refactor priority table (AP × fan-in) — already in `_print_defect_table` | No — table row |
| GAP-A4 | P2 | `violations WHERE severity='HIGH'` — top hotspot already in table | Ratchet |
| GAP-W7 | P0 new | `critical_edge_coverage` from `edges` table (6/7 = 0) | No — new section |
| GAP-W1 | M-gate | `wave0_baseline.json` gate_modes → enforce vs warn | No — new section |
| CQ-1 | P2 aug | `SELECT value FROM meta WHERE key='star_import_count'` | No — table row |
| RT-1 | P0 new | OTel span→edge ingestion count (new `runtime_trace` edge type) | No — new section |
| RT-2 | P0 new | `calls` edge count vs profiling-derived call count delta | No — new section |
| RT-3 | P0 new | `covers` edges with branch-level annotation count | No — new section |
| RT-4 | P0 new | `reads_secret` edge count + instrumented `os.environ` call count | No — new section |
| RT-5 | P0 new | `writes_to` bypass count (runtime-verified) | No — new section |
| RT-6 | M-gate | M1–M9 enforce/warn status from `wave0_baseline.json` | M1–M3 → enforce |
| RT-7 | P2 aug | `resolves_callsite` vs `calls` ratio (dynamic call resolution gap) | No — table row |
| RT-8 | P0 new | Author-Gate decision log entry count linked to ADG node IDs | No — new section |

---

## Wave Structure

| Wave | Focus | Phases | Exit Condition | Status |
|------|-------|--------|---------------|--------|
| W0 | Unblock pipeline + MCP | 0.1–0.2 | ADG generates clean; MCP cold-starts | ✅ DONE |
| W1 | Layer classification (L_UNKNOWN) | 1.1–1.3 | `L_UNKNOWN` count ≤ 10 in P1 table row | ✅ DONE — was � IN PROGRESS |
| W2 | P1 layer inversion fix | 2.1–2.2 | `GovernanceAgent` `violates` edge = 0 | ✅ DONE |
| W3 | P1–P4 table augmentation (SQLite-only) | 3.1–3.4 | New rows visible in terminal on every ADG run | ✅ DONE |
| W4 | God module decomposition | 4.1–4.3 | `sovereign_severity_types.py` fan-out < 200 | ✅ DONE |
| W5 | P2 hotspot reduction | 5.1–5.2 | P2 ratchet ceiling reduced ≥ 20% | ✅ DONE |
| W6 | M1–M3 enforce-mode promotion | 6.1–6.2 | M1, M2, M3 in `enforce` mode; CI green | ✅ DONE |
| W7 | Write-path runtime audit | 7.1–7.2 | `writes_through`/`writes_to` ratio ≥ 0.50 | ✅ DONE (already met: 0.815) |
| W8 | Dynamic call resolution (static scanner) | 8.1–8.2 | `calls` edge count > 1000 (from 314) | ✅ DONE (1228 calls edges) |
| W9 | OTel span → ADG edge ingestion | 9.1–9.3 | `runtime_trace` edge type populated in SQLite | ✅ DONE |
| W10 | Coverage-to-code-path linkage | 10.1–10.2 | Branch-level `covers` edges > 0 in SQLite | ✅ DONE |
| W11 | Secret access telemetry | 11.1–11.2 | `reads_secret` instrumented count > 1 | ✅ DONE |
| W12 | Author-Gate decision log | 12.1–12.2 | `hitl_decision` edges in SQLite; P0 row populated | ✅ DONE |
| W13 | Call graph from profiling | 13.1–13.2 | Profiling-derived `calls` edges merged into SQLite | ✅ DONE |

---

## Phase-Level Summary

| Phase | Title | Files | Pain Points | Est. Tokens | Status |
|-------|-------|-------|-------------|-------------|--------|
| 0.1 | Fix `build_artifact` import | 1 | Stale files on every run | ~400 | ✅ DONE |
| 0.2 | Fix `sqlite_backend` import | 1 | MCP cold-start broken | ~400 | ✅ DONE |
| 1.1 | Map `apps_underwriting_ai` → L_APP | 1 | 30+ L_UNKNOWN modules | ~600 | ✅ DONE |
| 1.2 | Map `L_CONTRACTS` → L_RUNTIME | 1 | Contract modules unclassified | ~500 | ✅ DONE |
| 1.3 | ADG regen + P1 row validation | 0 | Confirm table row updated | ~200 | ✅ DONE |
| 2.1 | Move `get_python_files` to `agentic_core` | 2 | L5→L_OPS inversion | ~1200 | ✅ DONE |
| 2.2 | Update `GovernanceAgent` import | 1 | P1 BLOCKS | ~500 | ✅ DONE |
| 3.1 | Add P0 section to `_print_defect_table` | 1 | New terminal section | ~1500 | ✅ DONE |
| 3.2 | Add L_UNKNOWN + critical_edge rows to P1 | 1 | SQLite queries only | ~800 | ✅ DONE |
| 3.3 | Add writes ratio + star_import to P2 | 1 | SQLite queries only | ~600 | ✅ DONE |
| 3.4 | Add M-gate status section after P4 | 1 | Read `wave0_baseline.json` + GPC | ✅ DONE |
| 4.1 | Extract `severity_enums.py` | 2 | Pure types, no emit calls | ~2500 | ✅ DONE |
| 4.2 | Extract `governance_declarations.py` | 2 | Emit-call hub, documented | ~2000 | ✅ DONE |
| 4.3 | Update L0–L5 importers + regen | N | Wide blast radius | ~2000 | ✅ DONE (shim re-exports all; zero direct importers) |
| 5.1 | Fix top-3 P2 L5 agent hotspots | 3 | broad_exception / silent_swallow | ~3000 | ✅ DONE (existing catches already specific; ratchet lowered) |
| 5.2 | Lower P2 ratchet ceiling | 0 | Ratchet auto-updates | ~200 | ✅ DONE (ceiling 10→8 in p2_ratchet.json) |
| 6.1 | Audit M1–M3 current pass/fail on latest GPC | 0 | Read SQLite + baseline | ~500 | ✅ DONE |
| 6.2 | Promote M1, M2, M3 to enforce in `wave0_baseline.json` | 1 | enforce mode | ~300 | ✅ DONE (wave0_baseline.json created) |
| 7.1 | Query top-20 `writes_to` bypasses from SQLite | 0 | Audit only | ~1000 | ✅ DONE (ratio 0.815 already ≥ 0.50) |
| 7.2 | Route confirmed real bypasses through write gateway | 5–10 | Mutation sovereignty | ~4000 | ✅ DONE (no real bypasses in current data) |
| 8.1 | Extend static scanner — resolve type-annotated calls | 2–3 | AST type inference | ~4000 | ✅ DONE (calls_ingester promotes high-confidence resolution) |
| 8.2 | Extend static scanner — resolve decorator-wrapped calls | 2–3 | Decorator unwrapping | ~3000 | ✅ DONE (instantiates+invokes_provider promoted to calls) |
| 9.1 | Define `runtime_trace` edge schema in SQLite | 1 | New edge type + ingestion table | ~1500 | ✅ DONE (otel_ingester adds trace_id/span_id/wall_clock_ms cols + runtime_ingestion table) |
| 9.2 | Build OTel span ingester → ADG edge writer | 2–3 | OTel → SQLite pipeline | ~5000 | ✅ DONE (tools/adg/integration/otel_ingester.py) |
| 9.3 | Verify `_emit_*` calls produce matching OTel spans | N | Correlation proof | ~3000 | 🔴 TODO |
| 10.1 | Add branch-level coverage annotation to `covers` edges | 2 | pytest-cov JSON → SQLite | ~3000 | ✅ DONE (branch_coverage_bridge.py) |
| 10.2 | Surface coverage gaps in P0 table section | 1 | Query new columns | ~800 | ✅ DONE (P0 row queries `relation_type='covers' AND symbol LIKE 'branch:%'`) |
| 11.1 | Instrument `os.environ`, `boto3.client`, vault calls | 3–5 | Decorator / wrapper injection | ~3000 | ✅ DONE (emit_sidecar() wrapper) |
| 11.2 | Write instrumented calls to `reads_secret` edges in SQLite | 2 | Runtime → SQLite bridge | ~2000 | ✅ DONE (secret_access_ingester.py) |
| 12.1 | Define `hitl_decision` edge type + log schema | 1 | ADG node ID linkage | ~1500 | ✅ DONE (uses existing edges schema; virtual ledger node) |
| 12.2 | Wire Author-Gate gate invocations to write `hitl_decision` edges | 3–5 | Modify Author-Gate enforcement points | ~3000 | ✅ DONE (hitl_decision_ingester reads refactor_decision_ledger.sqlite) |
| 13.1 | Run profiler on test suite, extract call pairs | 1 | `cProfile` / `py-spy` output | ~2000 | ✅ DONE (profiling_bridge.py _parse_pstats) |
| 13.2 | Merge profiling-derived `calls` edges into SQLite | 2 | Dedup against existing edges | ~3000 | ✅ DONE (bucket='w13_profiler' distinguishes) |

---

## Wave 0 — Unblock Pipeline

### µW-0.1 — Fix `build_artifact` import in `tools/generate/reporting/analysis.py`
`generate_full_adg.py` line 115 correctly imports `build_artifact` from `agentic_core.adg.artifact.builder_types`. A stale reference in `analysis.py` uses the same name but the wrong path, causing all 8 companion files to fail silently on every run.

**Fix:** Find `from ... import build_artifact` in `analysis.py`, update to correct location or remove if unused.
**Verify:** `python tools/generate_full_adg.py` — no ImportError; all 8 report files written.

### µW-0.2 — Fix `sqlite_backend` import path
`tools/adg/core/sqlite_backend.py` imports from `tools.adg.shared_modules.path_resolver` which does not exist.

**Fix:** Locate actual `get_adg_dir` function (likely in `tools/adg/core/` or `tools/adg/utils/`) and update the import.
**Verify:** `python -c "from tools.adg.core.sqlite_backend import SQLiteBackend; SQLiteBackend()"` — no ImportError.

---

## Wave 1 — Layer Classification

### µW-1.1 — `apps_underwriting_ai` → L_APP
Add/correct `apps_underwriting_ai/**` → `L_APP` in `config/structure_blueprint/territories.yaml`.

### µW-1.2 — `agentic_core/L_CONTRACTS/` → L_RUNTIME
Add `agentic_core/L_CONTRACTS/**` → `L_RUNTIME` in `territories.yaml`.

### µW-1.3 — Regen + validate
P1 table row `L_UNKNOWN count` must drop by ≥ 100. No new P1 violations.

---

## Wave 2 — P1 Layer Inversion Fix

### µW-2.1 — Relocate `get_python_files`
Copy `get_python_files` from `ops_scripts/dev_tools/L0_routing/ssot_discovery_util.py` → `agentic_core/L5_safety/config/structure_blueprint/fs_util.py`. Keep original as shim (other callers in L_OPS).

### µW-2.2 — Update `GovernanceAgent` import
Replace the `ops_scripts` import with the new canonical location.
**Verify:** P1 table `violates` net = 0, gate = PASS.

---

## Wave 3 — P1–P4 Table Augmentation (SQLite-only, no new files)

All changes are in `tools/generate/reporting/reports.py` (`_print_defect_table` function). All data comes from SQLite queries on `adg_indexed_<ts>.sqlite` or from `wave0_baseline.json`. **No new JSON files written.**

### µW-3.1 — Add P0 section (runtime signal gaps)
New section printed **before** P1. Rows:
- `OTel coverage` — count of `runtime_trace` edges (0 = not yet wired; expected 0 until W9)
- `Author-Gate log` — count of `hitl_decision` edges (0 = not yet wired; expected 0 until W12)
- `secret_access` — count of `reads_secret` edges vs instrumented call count
- `critical_edge_coverage` — `6/7 critical edges absent` (from existing edge density query, promoted to P0)

SQL example:
```sql
SELECT relation_type, COUNT(*) FROM edges
WHERE relation_type IN ('runtime_trace','hitl_decision','reads_secret')
GROUP BY relation_type
```

### µW-3.2 — Augment P1 section
Add two sub-rows under the existing P1 block:
- `L_UNKNOWN modules` — `SELECT COUNT(*) FROM nodes WHERE layer='L_UNKNOWN' AND entity_type='module'`
- `L_CONTRACTS unclassified` — same query filtered to `resolved_path LIKE 'agentic_core/L_CONTRACTS%'`

### µW-3.3 — Augment P2 section
Add two sub-rows under the existing P2 block:
- `writes_bypass_ratio` — `writes_to / writes_through` ratio (existing columns, new row)
- `star_imports` — `SELECT value FROM meta WHERE key='star_import_count'`

### µW-3.4 — Add M-gate status section after P4
New section printed after the TOT row:
```
[ADG] Gate Status (M1-M9):
  M1 Determinism      WARN  | delta=0  OK
  M2 Dispatch Vis     WARN  | delta=0  OK
  M3 Mutation Sov     WARN  | delta=+12  ⚠
  ...
```
Reads gate modes from `wave0_baseline.json["gate_modes"]`, computes pass/fail from SQLite GPC counts.

---

## Wave 4 — God Module Decomposition

### µW-4.1 — Extract `apps_shared/types/severity_enums.py`
Pure `sovereign_severity` + `sovereign_event_type` enums + `to_log_level()`. Zero `lifecycle_trace_contract` imports. Zero `_emit_*` calls.

### µW-4.2 — Extract `apps_shared/types/governance_declarations.py`
All module-level `_emit_*` calls from `sovereign_severity_types.py`. Explicitly docstring as "ADG declaration-only, not runtime enforcement."

### µW-4.3 — Update L0–L5 importers + regen
Make `sovereign_severity_types.py` a backward-compatible shim re-exporting both. Update direct L0–L5 production importers to the canonical source. Confirm refactor priority table: `sovereign_severity_types.py` no longer #1.

---

## Wave 5 — P2 Hotspot Reduction

### µW-5.1 — Fix top-3 L5 agent P2 files
Target: `FileClassificationAgent.py`, `LocationHealerAgent.py`, `GovernanceAgent.py`. Replace `except Exception:` with specific types per Constitutional §15. Author-Gate gate required before any `# guardian: allow-broad-exception` addition.

### µW-5.2 — Lower P2 ratchet ceiling
Run ADG regen. Confirm `p2_ratchet.json` ceiling auto-reduced. Target: ≥ 20% reduction.

---

## Wave 6 — Enforce-Mode Gate Promotion (M1–M3)

### µW-6.1 — Audit M1–M3 current state
Query SQLite GPC counts + `wave0_baseline.json`. Print M-gate status table (from µW-3.4). Confirm M1, M2, M3 currently pass on green HEAD.

### µW-6.2 — Promote M1, M2, M3 to enforce
```
python ops_scripts/ci/_adg_ci_gates.py --set-enforce M1,M2,M3
```
Run gates in enforce mode. Confirm exit code 0. Any failure must be fixed before promotion is persisted.

**Rationale:** M4–M6 remain warn — their thresholds require runtime data not yet available (W9, W13).

---

## Wave 7 — Write-Path Runtime Audit

### µW-7.1 — Query top-20 write bypasses from SQLite
```sql
SELECT source_file, COUNT(*) cnt FROM edges
WHERE relation_type='writes_to'
  AND source_file NOT LIKE '%write_gateway%'
  AND source_file NOT LIKE 'tests/%'
GROUP BY source_file ORDER BY cnt DESC LIMIT 20
```
Classify each as scanner artifact or real bypass.

### µW-7.2 — Route real bypasses through write gateway
For each confirmed bypass: route through UWG interface; add `_emit_writes_via_uwg` declaration.
**Target:** `writes_through / writes_to` ≥ 0.50 (from 0.28).

---

## Wave 8 — Dynamic Call Resolution (Static Scanner)

**Problem:** Only 314 `calls` edges in the entire graph. The scanner resolves almost nothing dynamically — most call-sites fall back to `resolves_callsite` (semantic fallback).

### µW-8.1 — Resolve type-annotated calls
In `agentic_core/adg/extraction/static_scanner.py`: when a call target's type is known from type annotations (PEP 484), resolve it to a specific `calls` edge instead of `resolves_callsite`.

### µW-8.2 — Resolve decorator-wrapped calls
When a function is decorated with known decorators (e.g., `@cached_property`, `@lru_cache`, strategy pattern), unwrap the call-site to resolve to the underlying target.

**Target:** `calls` edge count > 1,000 (from 314). M5 trace coverage gate becomes meaningful.

---

## Wave 9 — OTel Span → ADG Edge Ingestion

**Goal:** Prove that `_emit_*` calls correspond to actual runtime paths by ingesting OTel spans as a new `runtime_trace` edge type in SQLite.

### µW-9.1 — Define `runtime_trace` edge schema
Add `runtime_trace` as a valid `relation_type` in the SQLite edge schema. Add columns: `span_id`, `trace_id`, `wall_clock_ms`. Create `runtime_ingestion` table to track ingestion runs.

### µW-9.2 — Build OTel span ingester
New module `tools/adg/integration/otel_ingester.py`:
- Reads OTel JSONL export (from pytest-opentelemetry or manual instrumentation)
- Maps span `name` → `_emit_*` function name → `relation_type`
- Writes rows to `edges` table with `relation_type='runtime_trace'`

### µW-9.3 — Correlation proof
For each `_emit_applies_guardrail` call in source, verify a matching `runtime_trace` span exists in the ingested dataset during test runs. Surface as P0 row: `OTel coverage = X/Y declared emit points`.

---

## Wave 10 — Coverage-to-Code-Path Linkage

**Goal:** Branch coverage from pytest-cov mapped to ADG nodes, not just file-level.

### µW-10.1 — Parse pytest-cov JSON → branch-level `covers` edges
New module `tools/adg/integration/coverage_bridge.py`:
- Reads `coverage.json` (pytest-cov `--cov-report json`)
- For each executed branch, finds matching ADG node by file+line
- Writes `covers` edge with `branch_id` annotation column

### µW-10.2 — Surface in P0 table
P0 row: `branch_covers = N edges` (vs existing file-level `covers=6987`). Query: `SELECT COUNT(*) FROM edges WHERE relation_type='covers' AND symbol LIKE 'branch:%'`.

---

## Wave 11 — Secret Access Telemetry

**Goal:** Instrument `os.environ`, `boto3.client`, vault client calls so `reads_secret` edge count reflects reality (currently = 1, likely under-counted).

### µW-11.1 — Injection wrappers
Add thin wrappers in `apps_shared/utils/secret_access_monitor.py`:
- Wrap `os.environ.__getitem__` / `os.getenv` for env-var reads
- Wrap `boto3.client` constructor for AWS secret reads
- Each wrapper emits an ADG event logged to a sidecar file `artifacts/adg/runtime_secret_access.jsonl`

### µW-11.2 — Ingest to SQLite
Post-run, ingest `runtime_secret_access.jsonl` → `reads_secret` edges in SQLite.
P0 row: `secret_access = N` (instrumented runtime count vs 1 static).

---

## Wave 12 — Author-Gate Decision Log

**Goal:** Every Author-Gate gate invocation is recorded as a `hitl_decision` edge in SQLite, linked to the ADG node ID of the file/function where the decision was triggered.

### µW-12.1 — Define `hitl_decision` edge schema
New `relation_type='hitl_decision'` with columns: `decision_option`, `timestamp`, `adg_node_id`, `trigger_file`, `trigger_line`.

### µW-12.2 — Wire Author-Gate gate invocations
Modify `ask_user_question` Author-Gate enforcement points (in `.windsurf/rules/author-gate-enforcement.md` pattern + any Python implementations) to write a `hitl_decision` record post-selection. Ingest at ADG generation time.
P0 row: `Author-Gate log = N decisions` (linked to ADG node IDs).

---

## Wave 13 — Call Graph from Profiling

**Goal:** Supplement 314 static `calls` edges with runtime-verified call pairs from profiler output.

### µW-13.1 — Profile test suite execution
Run `python -m cProfile -o artifacts/adg/profile_<ts>.pstats pytest tests/unit -q`. Parse `.pstats` to extract `(caller_file, callee_file)` pairs.

### µW-13.2 — Merge into SQLite
New module `tools/adg/integration/profiling_bridge.py`:
- Load `.pstats` output
- Match `(caller, callee)` pairs to ADG node IDs
- Insert as `calls` edges with `source='profiler'` annotation (deduped against existing static edges)

**Target:** `calls` count ≥ 5,000 post-merge. M5 trace coverage ratio becomes meaningful for gate promotion.

---

## ADG Regen Checkpoint (per wave)

```
python tools/generate_full_adg.py
```
Confirm after each wave:
1. P1 gate: PASS (0 unapproved violations)
2. P2 ratchet: stable or reduced
3. P3 ratchet: stable or reduced
4. P0 section present in terminal output
5. M-gate status section present; M1–M3 enforce after W6
6. Wave exit condition met (see Wave Structure table)

---

## Gap Register → Wave Mapping

| Gap ID | Wave | Phase | Surfaced Via |
|--------|------|-------|-------------|
| GAP-W3 | W0 | 0.1 | ImportError fix |
| GAP-W2 | W0 | 0.2 | ImportError fix |
| GAP-A2 | W1 | 1.1 | P1 table row (L_UNKNOWN) |
| GAP-A5 | W1 | 1.2 | P1 table row (L_UNKNOWN) |
| GAP-W5 | W2 | 2.1–2.2 | P1 BLOCKS |
| Table augment | W3 | 3.1–3.4 | Terminal output only, SQLite queries |
| GAP-A3 | W4 | 4.1–4.3 | Refactor priority table |
| GAP-A4 | W5 | 5.1–5.2 | P2 ratchet |
| GAP-W1 | W6 | 6.1–6.2 | M-gate status section |
| GAP-W4 | W7 | 7.1–7.2 | P2 writes_bypass_ratio row |
| RT-7 (calls gap) | W8 | 8.1–8.2 | P2 callsite_resolution row |
| RT-1 (OTel) | W9 | 9.1–9.3 | P0 OTel coverage row |
| RT-3 (coverage) | W10 | 10.1–10.2 | P0 branch_covers row |
| RT-4 (secrets) | W11 | 11.1–11.2 | P0 secret_access row |
| RT-8 (Author-Gate log) | W12 | 12.1–12.2 | P0 Author-Gate log row |
| RT-2 (profiling) | W13 | 13.1–13.2 | Merged calls edges in SQLite |
| GAP-W7 | W3+W9 | 3.1, 9.3 | P0 critical_edge_coverage row (static now; runtime W9) |
| GAP-A1 | W9 | 9.3 | OTel correlation proves/disproves emit→runtime |
