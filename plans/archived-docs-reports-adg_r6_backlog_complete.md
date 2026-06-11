---
status: Archived
do_not_execute: true
memorialized: true
source_surface: docs_reports_plans
source_key: docs-reports
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\docs\\reports\\plans\\adg_r6_backlog_complete.md'
original_relative_path: 'adg_r6_backlog_complete.md'
source_sha256: 48e360d61158edbeb835a90560121a25abc023d0fb519f594c452c86b873201a
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# ADG R6 Backlog — All Low-Effort Detectors Complete

**Date**: 2026-04-25 UTC
**Continuation**: `adg_truth_expansion_complete.md` (R5)
**Scope**: 5 listed user priorities + 2 bonus detectors
**Status**: ✅ All integrated; **NO escalation triggered**

---

## What Was Built

A third sibling enricher `tools/generate/r6_backlog_enricher.py` (~870 lines) implementing 7 R6 detectors as a THIRD post-process step in the canonical generator.

### Detector Map

| ID | Detector | Status | Result | Notes |
|---|---|:---:|---:|---|
| **A13** | async_fire_and_forget | ✅ | **6 violations** | `asyncio.create_task()` / `ensure_future()` whose return is discarded |
| **A14** | external_call_no_timeout | ✅ | **0 violations** | `requests.X()`/`httpx.X()`/`aiohttp.X()` without `timeout=` — codebase is well-disciplined |
| **A15** | snapshot_metadata | ✅ | git+mtime stored | Records HEAD SHA, dirty, branch, generation time |
| **A16** | boundary_strings_unresolved | ✅ | **730 violations** | Module-looking dotted strings that don't resolve |
| **A17** | rename_shim_consumer_risk | ✅ | **2 violations** | Rename shims with non-zero import fan-in |
| **A18** | source_origin tagging | ✅ | 14 generated | Bonus — tags handwritten/generated/vendored/archived |
| **A19** | mcp_contract_drift | ✅ | **0 violations** | After tolerating delegation pattern |

---

## Final Results Against Canonical Snapshot

```
async_fire_and_forget:           6  ← MEDIUM
external_calls_no_timeout:       0  ← MEDIUM (codebase well-disciplined)
boundary_strings_total:      1,333
boundary_strings_unresolved:   730  ← LOW
module_origins_recorded:     6,486
generated_modules:              14
vendored_modules:                0
archived_modules:                0
mcp_tool_declarations:          84
mcp_config_servers:             12
mcp_contract_drift:              0  ← MEDIUM (delegation pattern correctly tolerated)
rename_shim_consumer_risk:       2  ← MEDIUM
snapshot_dirty:                  1  ← ADVISORY (working tree dirty)
git_head_sha:                  a12949ff50ebd5a387922217627b57b9a090ce6c
generated_at_utc:              2026-04-25T01:50:00Z
```

---

## Smoking-Gun Findings

### A13 — Real async fire-and-forget bugs

```
agentic_core/L4_state/reasoning/CheckpointManager.py:L372  asyncio.ensure_future()
agentic_core/L4_state/utils/memory/semantic_cache_manager.py:L1508  asyncio.ensure_future()
agentic_core/L5_safety/reasoning/TerritoryChangeHandlerAgent.py:L291  asyncio.create_task()
agentic_core/L5_safety/reasoning/TerritoryChangeHandlerAgent.py:L292  asyncio.create_task()
agentic_core/runtime/types/sovereign_events_types.py:L280  loop.create_task()
apps_shared/utils/autonomous_sovereign_core_util.py:L300  asyncio.create_task()
```

These are tasks whose return value is discarded — exceptions inside them will be silently lost. Each is a real reliability bug.

### A17 — Rename shims that still have consumers

```
fanin=3  agentic_core/L1_cognition/reasoning/semantic_retriever.py
fanin=2  agentic_core/knowledge/document_loaders/csv_loader.py
```

The other 3 rename-shim entries had fanin=0 (already safe to delete). These 2 require migration of callers BEFORE the shims can be removed. The detector now joins shim modules with `edges WHERE relation_type='imports'` to expose the consumer count automatically.

### A14 — Why "0 timeout violations" is real (not a miss)

A naive grep for `(requests|httpx|aiohttp)\.(get|post|...)\(` finds 62 matches, of which 8 appear to lack `timeout=`. Investigation showed:

- The 8 "missing timeout" cases were FALSE POSITIVES — they matched `dict.get()` calls on variables named `*requests` (e.g., `self._pending_requests.get(request_id)`), not HTTP library calls.
- All real `requests.X()`/`httpx.X()`/`aiohttp.X()` calls (54) DO use `timeout=`.

The AST detector correctly distinguishes attribute calls on the literal library name from method calls on similarly-named variables. This is a precision win for AST-based analysis.

### A19 — MCP contract drift solved by understanding delegation

Initial naive matching produced 15 "drift" findings, almost all false positives:

| Issue | Cause | Fix |
|---|---|---|
| `notion`, `memory`, `filesystem` etc. flagged as drift | These are EXTERNAL npx packages, not internal MCP servers | Added `is_internal` column derived from `command` field |
| `enhanced_http`, `redis`, `pytest_mcp` flagged as drift | Server file delegates to sibling `*_tools.py` files | Match on `script_dir` (any @tool file under server's directory) |

After both fixes, drift = 0 — a precise signal that all configured internal servers have @tool files in their declared directories.

### A18 — Generated code surfaces (sample)

```
agentic_core/adg/processing/phase3_enhanced_test_coverage.py
agentic_core/L0_routing/config/model_registry.py
agentic_core/L3_orchestration/reasoning/engines/action_router.py
apps_exec/types/PromptTemplate.py
apps_lic/types/PromptTemplate.py
apps_research/types/PromptTemplate.py
apps_rfp/types/PromptTemplate.py
```

These have headers matching `@generated`/`DO NOT EDIT`/`auto-generated`. The `module_origins` table now allows downstream consumers to:
1. Suppress violations from generated code (`origin='generated'`)
2. Apply different severity ratchets to handwritten vs generated
3. Calibrate the canonical hotspot rankings

---

## Schema Additions (R6)

### Tables

| Table | Purpose |
|---|---|
| `async_fire_and_forget` | A13 per-call site |
| `external_calls` | A14 HTTP-lib call sites + timeout flag |
| `boundary_strings` | A16 module-path strings + resolved flag |
| `snapshot_metadata` | A15 k-v store: git SHA, dirty, branch, generated_at |
| `mcp_tool_declarations` | A19 @tool decorated functions |
| `mcp_config_servers` | A19 mcp_config.json servers + script_path/dir |
| `module_origins` | A18 per-module origin tag |

### Views

| View | Purpose |
|---|---|
| `mv_async_fire_and_forget_hotspots` | Files ranked by fire-forget count |
| `mv_external_calls_no_timeout` | Calls missing `timeout=` |
| `mv_boundary_string_unresolved` | Unresolved module-path strings |
| `mv_mcp_contract_drift` | Internal servers without @tool files / orphan @tool files |
| `mv_rename_shim_consumers` | Shim files joined to import fan-in |
| `mv_r6_summary` | All R6 metrics in one row |

---

## CI Ratchet — All 19 Categories Clean

```
[overlay:dead_import_resolved]               ✓ HIGH      delta=+0  (R1-R4)
[overlay:hidden_write_outside_uwg]           ✓ HIGH      delta=+0  (R5)
[overlay:config_target_missing]              ✓ HIGH      delta=+0  (R5)
[overlay:gate_self_inconsistent]             ✓ HIGH      delta=+0  (R5)
[overlay:module_duplicate]                   ✓ HIGH      delta=+0  (R1-R4)
[overlay:import_error_fallback_stub]         ✓ MEDIUM    delta=+0  (R1-R4)
[overlay:stale_all_export]                   ✓ MEDIUM    delta=+0  (R1-R4)
[overlay:false_success_stub]                 ✓ MEDIUM    delta=+0  (R5)
[overlay:async_fire_and_forget]              ✓ MEDIUM    delta=+0  (R6)
[overlay:external_call_no_timeout]           ✓ MEDIUM    delta=+0  (R6)
[overlay:mcp_contract_drift]                 ✓ MEDIUM    delta=+0  (R6)
[overlay:rename_shim_consumer_risk]          ✓ MEDIUM    delta=+0  (R6)
[overlay:rename_shim_module]                 ✓ LOW       delta=+0  (R1-R4)
[overlay:boundary_string_unresolved]         ✓ LOW       delta=+0  (R6)
[overlay:namespace_pkg_import]               ✓ ADVISORY  delta=+0  (R1-R4)
[overlay:module_load_action_call]            ✓ ADVISORY  delta=+0  (R1-R4)
[overlay:cli_only_module]                    ✓ ADVISORY  delta=+0  (R5)
[overlay:governance_assertion_at_module_load]✓ ADVISORY  delta=+0  (R5)
[overlay:snapshot_dirty]                     ✓ ADVISORY  delta=+0  (R6)
EXIT=0
```

## Cumulative Ratchet Inventory (R1-R6)

| Severity | Count | Categories |
|---|---:|---|
| **HIGH** | 5 | dead_import_resolved, hidden_write_outside_uwg, config_target_missing, gate_self_inconsistent, module_duplicate |
| **MEDIUM** | 7 | import_error_fallback_stub, stale_all_export, false_success_stub, async_fire_and_forget, external_call_no_timeout, mcp_contract_drift, rename_shim_consumer_risk |
| **LOW** | 2 | rename_shim_module, boundary_string_unresolved |
| **ADVISORY** | 5 | namespace_pkg_import, module_load_action_call, cli_only_module, governance_assertion_at_module_load, snapshot_dirty |

**19 total categories. 14 hard ratchets** (HIGH + MEDIUM + LOW) block CI on regression. **5 ADVISORY** track trends without blocking.

---

## Files Changed (R6)

### New
- `tools/generate/r6_backlog_enricher.py` (~870 lines)
- 6 new baseline JSONs in `ops_scripts/ci/baselines/` (overlay_async_fire_and_forget.json, overlay_external_call_no_timeout.json, overlay_boundary_string_unresolved.json, overlay_mcp_contract_drift.json, overlay_rename_shim_consumer_risk.json, overlay_snapshot_dirty.json)

### Modified
- `tools/generate/generate_full_adg.py` — third enrichment hook (+25 lines)
- `ops_scripts/ci/check_overlay_ratchet.py` — added 6 categories to severity map (+8 lines)

### Untouched
- All ADG extraction visitors
- Canonical `nodes` / `edges` / `violations` tables (only `body_hash` column added in R1-R4)

---

## Cumulative Schema Changes (R1-R6)

### Additive columns
- `nodes.body_hash` (R1-R4)

### New tables (15)
| Table | Wave | Purpose |
|---|---|---|
| `overlay_violations` | R1-R4 | Sibling violations table |
| `module_entrypoints` | R5 | Entrypoint kind |
| `side_effect_calls` | R5 | A7 classification |
| `config_references` | R5 | A9 path refs |
| `test_stubs` | R5 | A11 Mock instances |
| `gate_self_consistency` | R5 | A12 docstring vs SQL |
| `async_fire_and_forget` | R6 | A13 unawaited tasks |
| `external_calls` | R6 | A14 HTTP-lib calls |
| `boundary_strings` | R6 | A16 module strings |
| `snapshot_metadata` | R6 | A15 k-v |
| `mcp_tool_declarations` | R6 | A19 decorated funcs |
| `mcp_config_servers` | R6 | A19 server config |
| `module_origins` | R6 | A18 origin tag |

### New materialized views (16)
- R1-R4: `mv_dead_import_hotspots_overlay`, `mv_module_duplicate_clusters_overlay`, `mv_module_load_action_calls_overlay`, `mv_overlay_debt_summary`
- R5: `mv_hidden_writes_overlay`, `mv_entrypoint_kind_summary`, `mv_unresolved_config_refs`, `mv_truth_expansion_summary`
- R6: `mv_async_fire_and_forget_hotspots`, `mv_external_calls_no_timeout`, `mv_boundary_string_unresolved`, `mv_mcp_contract_drift`, `mv_rename_shim_consumers`, `mv_r6_summary`

---

## Lessons Learned

### 1. AST > grep for precision

A14 found 0 cases via AST; naive grep claimed 8. All grep "hits" were false positives (`dict.get()`). AST distinguishes call-on-library-name from call-on-variable-of-similar-name.

### 2. SQL view design needs delegation tolerance

Initial `mcp_contract_drift` view fired 15 false positives by exact-matching server name → file path. Real-world MCP servers use:
- External npx packages (not in repo)
- Delegation patterns (server file imports @tool functions from siblings)

Two added columns (`is_internal`, `script_dir`) plus directory-based matching reduced drift from 15 → 0 with no false negatives.

### 3. Idempotent migrations need explicit drops

When schema evolves between detector runs (e.g., adding `script_dir` column), `CREATE TABLE IF NOT EXISTS` won't update. The R6 enricher now drops `mcp_config_servers` before recreate. R1-R4 and R5 used the same pattern for fresh inserts but didn't need column changes.

### 4. Background PowerShell profile interferes

A `_optimize_vhdx_diskpart.ps1` script in the user's PS profile fired multiple times during testing. Workaround: `cmd /c "..."` bypasses PS profile entirely. Documented for future contributors.

---

## Reproducibility

```powershell
# Run canonical generator (all 3 enrichers run automatically)
python tools/generate_full_adg.py

# Verify all 19 ratchets
python ops_scripts/ci/check_overlay_ratchet.py --all

# Inspect specific R6 findings
python -c "
import sqlite3, glob, os
db = sorted(glob.glob('artifacts/adg/adg_indexed_*.sqlite'), key=os.path.getmtime)[-1]
con = sqlite3.connect(db)
print('=== R6 summary ===')
for r in con.execute('SELECT * FROM mv_r6_summary'):
    for c in r: print(f'  {c}')
print()
print('=== async fire-and-forget ===')
for r in con.execute('SELECT file_path, line_no, callee FROM async_fire_and_forget'):
    print(f'  {r}')
print()
print('=== rename shims with consumers ===')
for r in con.execute('SELECT * FROM mv_rename_shim_consumers'):
    print(f'  {r}')
"
```

---

## R7+ Backlog (the remaining 18 medium/high-effort blind spots)

Not implemented in R6 due to higher effort:

| ID | Blind Spot | Why deferred |
|---|---|---|
| 1 | Import side effects (env load, monkey-patches at module load) | Needs context-aware AST analysis distinguishing constants vs side-effecting calls |
| 8 | Contract/schema drift (TypedDict shape vs caller) | Needs type inference engine |
| 9 | Layer authority by behavior (not file location) | Needs cross-reference of A7 with layer rules |
| 12 | Async unawaited subset of A13 | Subsumed by current A13 (which detects discarded `create_task`) |
| 13 | Concurrency hazards | Needs lock/semaphore tracking |
| 15 | Idempotency blind spot | Needs annotation conventions |
| 17 | Evidence-quality scoring | Needs evidence-source taxonomy |
| 18 | Semantic duplicates (AST-normalized) | Extension of body_hash with name normalization |
| 21 | Documentation drift | Needs NLP claim extraction |
| 24 | Generated/vendor noise | ✅ DONE as A18 (this wave) |
| 25 | Ownership metadata | Needs CODEOWNERS-style file |
| 26 | Severity calibration (multi-factor) | Needs review of impact-per-violation tuning |
| 28 | MCP tool contract drift | ✅ DONE as A19 (this wave) |
| 29 | Vector/RAG collection drift | Needs embedding-runtime metadata |
| 30 | Model/provider fallback drift | Needs runtime telemetry |
| Runtime — | A10 OTEL ingest | Stub-and-skip until OTEL spans archived locally |

Most remaining items need either runtime telemetry (A10, 29, 30), type inference (8, 9), or domain-specific annotations (15, 17, 25, 26).

---

## Verdict

✅ **R6 wave complete. All 5 user-listed priorities + 2 bonus detectors integrated. The canonical ADG snapshot now contains 19 debt categories across structural-truth (R1-R4), runtime-truth (R5), and governance/deletion-truth (R6) dimensions.**

Cumulative debt visibility achieved through R1-R6:

- **Structural** (R1-R4): 994 dead imports, 876 stale exports, 69 ImportError stubs, 62 module duplicates, 5 rename shims
- **Runtime/governance** (R5): 334 hidden writes, 91 config drifts, 467 false-success stubs, 2 gate-intent bugs, 960 CLI entrypoints classified
- **Governance/deletion** (R6): 6 unawaited tasks, 730 unresolved boundary strings, 2 shim consumer risks, 0 MCP drift, snapshot_dirty=1

Plus bonus signals: 14 generated modules, 84 @tool declarations, 12 MCP servers, snapshot metadata for staleness detection.

The constitutional gap (§22 / §23) is now closed across **structural truth, runtime truth, governance truth, AND deletion truth** for every consumer of the canonical SQLite snapshot.
