# ADG Repair Orchestrator Enhancement + Novel Wiring Gap Checks

Fixes broken SQLite analyzer queries, wires it into the orchestrator, adds P1/P2 repair rules, absorbs `auto_fix_p1_p2.py`, and adds a comprehensive `adg_wiring_gap_check.py` to catch partial-wiring issues (registry gaps, instantiation orphans, port-adapter gaps, dead imports).

---

## Wave Structure

| Wave | Phase | Focus | Est. Tokens | Status |
|------|-------|-------|-------------|--------|
| 1 | Fix `sqlite_analyzer.py` | Correct broken queries + add P1/P2 detection | ~3K | 🟢 |
| 2 | Wire into `repair_orchestrator.py` | Add `_extract_sqlite_deficiencies()` call path | ~2K | 🟢 |
| 3 | New repair rules: P1 + P2 | `fix_p1_layer_violation.py` + `fix_p2_antipatterns.py` | ~4K | 🟢 |
| 4 | Absorb `auto_fix_p1_p2.py` + tests | Archive standalone, update `generate_full_adg.py`, add tests | ~4K | 🟢 |
| 5 | Novel wiring gap checks | `adg_wiring_gap_check.py` — registry, instantiation, port-adapter, dead-import | ~5K | 🟢 |

**Total: ~18K tokens across 5 waves, all GREEN**

---

## Gap Register

**GAP-1: `sqlite_analyzer.py` has broken queries**
- `get_modules_missing_governance_edges()` uses `n.label` — column doesn't exist (actual: `n.resolved_path`)
- `get_layer_violations()` uses string comparison `src.layer > dst.layer` — fails for "L0"–"L6" (should use `relation_type='violates'`)
- `get_deficiencies_as_dicts()` builds `file_path` from `violation["src_id"]` (integer node ID, not a path)
- No P2 exception antipattern query exists
- Impact: orchestrator silently finds zero SQLite deficiencies on every run

**GAP-2: `repair_orchestrator.py` never calls `SQLiteAnalyzer`**
- `detect_deficiencies()` only parses JSON reports — SQLite path never received
- `__init__` has no `sqlite_path` parameter
- Impact: P1/P2 violations invisible to orchestrator despite schema having them

**GAP-3: No P1/P2 repair rules in `tools/adg/repair/rules/`**
- No rule for `issue_type='layer_violation'` (P1)
- No rule for `issue_type IN ('silent_exception_swallow', 'broad_exception_catch', ...)` (P2)
- Impact: orchestrator can detect deficiencies but has no rules to act on them

**GAP-4: `auto_fix_p1_p2.py` is a duplicate fast-path outside the orchestrator**
- Queries latest SQLite from `artifacts/adg/` — wrong DB during gate check (temp DB is current)
- Duplicates detection logic that should live in `SQLiteAnalyzer`
- Impact: redundant infrastructure, two codepaths for same problem

**GAP-5: No tool to detect partial-wiring issues before they reach production**
- Classes matching `*Agent`, `*Provider`, `*Strategy` exist but are never imported by a registry
- Classes defined but never instantiated = infrastructure that can't actually be used
- `system_learning/ports/` interfaces with no wired `adapters/` implementation = silent dead abstract layer
- `dead_import` / `unresolved` edges flag broken import chains that compile fine but silently fail at runtime
- Impact: developer sets up infrastructure, runs code, hits `KeyError: agent not found` or `NotImplementedError` instead of a build-time signal

---

## Execution Plan

### Wave 1 — Fix `sqlite_analyzer.py`

**Scope**: Repair all broken queries; add P2 antipattern query; fix `get_deficiencies_as_dicts()`.

**Changes to `tools/adg/repair/sqlite_analyzer.py`**:
1. `get_modules_missing_governance_edges()` — replace `n.label` with `n.resolved_path`
2. `get_layer_violations()` — replace string comparison with `WHERE relation_type = 'violates'`; join `source_file` from edges
3. Add `get_p2_antipatterns()` — queries `edge_kind IN ('silent_exception_swallow', 'broad_exception_catch', 'log_and_swallow', 'return_none_swallow')` with `source_file` and `line_no`
4. Fix `get_deficiencies_as_dicts()` — use `resolved_path` not `src_id` for `file_path`; emit P2 deficiencies with `FixCategory.SUGGEST_FIX` (classify, no auto-code-change)

**Acceptance**: `python -c "from tools.adg.repair.sqlite_analyzer import SQLiteAnalyzer; ..."` runs without OperationalError.

---

### Wave 2 — Wire SQLiteAnalyzer into `repair_orchestrator.py`

**Scope**: Add `sqlite_path` parameter; call analyzer in `detect_deficiencies()`; log results.

**Changes to `tools/adg/repair/repair_orchestrator.py`**:
1. Add `sqlite_path: Path | None = None` to `__init__`
2. Add `_extract_sqlite_deficiencies()` method — constructs `SQLiteAnalyzer`, calls `get_deficiencies_as_dicts()`, converts to `Deficiency` objects, appends to `self.deficiencies`
3. Call `_extract_sqlite_deficiencies()` from `detect_deficiencies()` when `sqlite_path` is not None

**Changes to `tools/adg/adg_repair.py`** (CLI entry point):
- Pass SQLite path to orchestrator (auto-detect latest from `artifacts/adg/` when `--latest`)

**Acceptance**: `python tools/adg/adg_repair.py --latest --dry-run` reports P1/P2 deficiency counts > 0.

---

### Wave 3 — New Repair Rules

**Scope**: Two new rules following `BaseRepairRule` interface.

#### `tools/adg/repair/rules/fix_p1_layer_violation.py`

```
@repair_rule("fix_p1_layer_violation", priority=5)
```
- `match()`: `issue_type == 'layer_violation'`
- `can_fix()`: returns `(True, "")` only for entries in `KNOWN_SAFE_VIOLATIONS` dict; else `(False, "requires human refactoring")`
- `apply_fix()`: adds `# guardian: allow-layer-violation -- <specific justification>` before the import line
- `verify_fix()`: re-reads file, confirms guardian comment present
- Category: `AUTO_FIX` for known-safe, `BLOCK_FIX` for all others

**KNOWN_SAFE_VIOLATIONS** initial set:
```python
{
    "ops_scripts/dev_tools/l0_scripts/start_runtime_api_util.py":
        "runtime API utility script requires L6 observability layer for server startup diagnostics"
}
```

#### `tools/adg/repair/rules/fix_p2_antipatterns.py`

```
@repair_rule("fix_p2_antipatterns", priority=15)
```
- `match()`: `issue_type IN ('silent_exception_swallow', 'broad_exception_catch', 'log_and_swallow', 'return_none_swallow')`
- `can_fix()`: **always returns `(False, "P2 requires human classification")`** — this is a pure classifier
- `apply_fix()`: returns `FixResult(success=False, error_message="P2 antipatterns require human review")`
- `verify_fix()`: returns `True` (no-op verifier)
- Category: always `BLOCK_FIX`
- Produces structured output: file, line, antipattern type, suggested remediation hint

**SVP rationale**: 3,924 locations — no bulk auto-fix. Classification gives actionable inventory; Author-Gate signs off tier by tier.

---

### Wave 4 — Absorb `auto_fix_p1_p2.py` + Tests

**Scope**: Archive standalone script; update gate call in `generate_full_adg.py`; write tests.

**Step 1 — Archive `auto_fix_p1_p2.py`**:
- Move to `tools/archive/auto_fix_p1_p2_archived_20260406.py`
- Add deprecation header

**Step 2 — Update `generate_full_adg.py`**:
- Remove `_run_p1_p2_auto_fix()` function
- In P1/P2 gate error paths: replace subprocess call with direct orchestrator invocation
  ```python
  from tools.adg.repair.repair_orchestrator import ADGRepairOrchestrator
  orch = ADGRepairOrchestrator(adg_dir=adg_artifacts_dir, timestamp=ts, sqlite_path=sqlite_path)
  result = orch.run(dry_run=False)
  print(f"[Auto-repair] {result.fixes_applied} fix(es) applied, {result.fixes_blocked} blocked")
  ```

**Step 3 — Tests** (`tools/generate/test_generate_full_adg_failfast.py` + new file):
- `test_sqlite_analyzer_layer_violations()` — mock DB with `violates` edge, assert detection
- `test_sqlite_analyzer_p2_antipatterns()` — mock DB with `silent_exception_swallow` edge, assert detection
- `test_p1_rule_known_safe_auto_fix()` — assert guardian comment added for known-safe violation
- `test_p1_rule_unknown_returns_block_fix()` — assert BLOCK_FIX for unknown violation
- `test_p2_rule_always_block_fix()` — assert P2 rule never auto-applies code changes
- `test_orchestrator_receives_sqlite_deficiencies()` — integration test with temp DB

**Acceptance**:
```
python -m pytest tools/generate/test_generate_full_adg_failfast.py -q --tb=short
python tools/adg/adg_repair.py --latest --dry-run
```

---

### Wave 5 — Novel Wiring Gap Checks

**Scope**: New standalone tool `tools/adg/adg_wiring_gap_check.py` (same pattern as `adg_fanin_isolation_check.py`) with 4 independent check modes. No code modification — detection and classification only.

---

#### Check A: Registry Membership Gap (`--registry-gaps`)

**The question**: "Is this class visible to the registry that's supposed to manage it?"

**SQL pattern**:
```sql
-- Find Agent/Provider/Strategy classes with zero imports from any *registry* file
SELECT n.resolved_path, n.layer
FROM nodes n
WHERE (n.resolved_path LIKE '%Agent.py' OR n.resolved_path LIKE '%Provider.py'
       OR n.resolved_path LIKE '%Strategy.py' OR n.resolved_path LIKE '%Handler.py')
  AND n.entity_type = 'module'
  AND n.resolved_path NOT LIKE '%test%'
  AND n.id NOT IN (
      SELECT e.dst_id FROM edges e
      JOIN nodes src ON src.id = e.src_id
      WHERE e.relation_type = 'imports'
        AND src.resolved_path LIKE '%registry%'
  );
```

**Output**: list of classes by layer + their naming pattern; flag those where a sibling registry exists but the class isn't in it.

**Known targets**:
- `AGENT_REGISTRY` dict in `agentic_core/agents/types/agent_registry.py`
- `capability_registry.py` in `agentic_core/L3_orchestration/utils/registry/`
- `mcp_registry.py` in `agentic_core/L2_execution/config/`

---

#### Check B: Instantiation Orphan (`--instantiation-orphans`)

**The question**: "Does production code ever actually create an instance of this class?"

**SQL pattern**:
```sql
-- Classes with zero production instantiations
SELECT n.resolved_path, n.layer
FROM nodes n
WHERE n.entity_type IN ('class', 'module')
  AND n.resolved_path NOT LIKE '%test%'
  AND n.resolved_path NOT LIKE '%ops_scripts%'
  AND n.resolved_path NOT LIKE '%tools/%'
  AND n.resolved_path NOT LIKE '%__init__%'
  AND n.id NOT IN (
      SELECT e.dst_id FROM edges e
      JOIN nodes src ON src.id = e.src_id
      WHERE e.relation_type = 'instantiates'
        AND src.resolved_path NOT LIKE '%test%'
        AND src.resolved_path NOT LIKE '%ops_scripts%'
  );
```

**Output**: classes with zero production instantiations, grouped by layer. Entrypoints and abstract bases are expected here — flag those that look like concrete implementations (not ABC, not dataclass-only).

---

#### Check C: Port-Adapter Gap (`--port-adapter-gaps`)

**The question**: "Every port has a matching adapter that production code actually uses."

**SQL pattern**:
```sql
-- Ports with no production adapter importer
SELECT port.resolved_path AS port_path
FROM nodes port
WHERE port.resolved_path LIKE '%/ports/%'
  AND port.entity_type = 'module'
  AND port.id NOT IN (
      SELECT e.dst_id FROM edges e
      JOIN nodes adapter ON adapter.id = e.src_id
      WHERE e.relation_type = 'imports'
        AND adapter.resolved_path LIKE '%/adapters/%'
  );
```

**Also checks** (second query): adapter nodes that exist in `adapters/` but have zero production fan-in themselves (adapter wired to port but nothing instantiates the adapter).

**Known targets**: `system_learning/ports/` ↔ `system_learning/adapters/`

---

#### Check D: Dead Import + Unresolved Import (`--dead-imports`)

**The question**: "Are there broken import chains that compile fine but will fail at runtime?"

**SQL pattern**:
```sql
-- Dead imports in production code (imported but never used)
SELECT source_file, symbol, line_no
FROM edges
WHERE edge_kind = 'dead_import'
  AND source_file NOT LIKE '%test%'
  AND source_file NOT LIKE '%ops_scripts%'
  AND source_file NOT LIKE '%tools/%'
ORDER BY source_file;

-- Unresolved imports (import target can't be resolved to any known node)
SELECT source_file, symbol, line_no
FROM edges
WHERE edge_kind = 'unresolved'
  AND source_file NOT LIKE '%test%'
  AND source_file NOT LIKE '%ops_scripts%'
ORDER BY source_file;
```

**Output**: two tables — dead imports (symbol present but unused) and unresolved imports (symbol references a non-existent module). Unresolved = higher severity (will raise `ImportError` at runtime).

---

#### CLI Interface

```
python tools/adg/adg_wiring_gap_check.py --all
python tools/adg/adg_wiring_gap_check.py --registry-gaps --gate
python tools/adg/adg_wiring_gap_check.py --port-adapter-gaps
python tools/adg/adg_wiring_gap_check.py --dead-imports
python tools/adg/adg_wiring_gap_check.py --instantiation-orphans --json > gaps.json
```

`--gate` flag: exits `1` if any critical wiring gap is found (zero-importer registry candidates, unresolved imports in production, port with no adapter). Suitable for CI pre-commit hook.

---

#### Tests (`tests/unit/tools/adg/test_adg_wiring_gap_check.py`)

- `test_registry_gap_detects_unregistered_class()` — mock DB, class with no registry importer
- `test_registry_gap_passes_when_registered()` — mock DB, class with registry importer → no gap
- `test_instantiation_orphan_flags_uninstantiated_class()` — no `instantiates` edge → flagged
- `test_port_adapter_gap_detects_missing_adapter()` — port exists, no adapter importer → flagged
- `test_port_adapter_gap_passes_with_wired_adapter()` — adapter imports port → pass
- `test_dead_imports_query_production_only()` — confirms `ops_scripts/` excluded
- `test_unresolved_imports_higher_severity()` — unresolved yields exit code 1 in gate mode

---

## Rules

- No bulk guardian exemptions — each exemption needs specific, non-generic justification
- P2 rule MUST NOT write code — classify only, BLOCK_FIX always
- `auto_fix_p1_p2.py` archived to `tools/archive/`, not deleted (§9 archival discipline)
- All `BaseRepairRule` subclasses must implement all 4 abstract methods
- `sqlite_analyzer.py` fixes must use `resolved_path` not `label`/`adg_name`
- `adg_wiring_gap_check.py` is detection-only — no file modifications, never writes code

---

## Success Criteria

- [ ] `sqlite_analyzer.py` queries execute without `OperationalError` against real ADG DB
- [ ] `repair_orchestrator.py` reports P1 count ≥ 1 and P2 count ≥ 1 when given SQLite path
- [ ] P1 rule adds guardian exemption for `start_runtime_api_util.py` (AUTO_FIX)
- [ ] P1 rule returns BLOCK_FIX for any file not in `KNOWN_SAFE_VIOLATIONS`
- [ ] P2 rule classifies all 4 antipattern types without modifying any file
- [ ] `generate_full_adg.py` P1/P2 gates call orchestrator directly (no subprocess)
- [ ] `auto_fix_p1_p2.py` archived under `tools/archive/`
- [ ] `adg_wiring_gap_check.py --registry-gaps` runs against live DB without error
- [ ] `adg_wiring_gap_check.py --dead-imports` surfaces at least the `gptcache_client` dead-import pattern
- [ ] `adg_wiring_gap_check.py --port-adapter-gaps` reports `system_learning/ports/` gaps
- [ ] `adg_wiring_gap_check.py --gate` exits `1` on unresolved imports, `0` on clean DB
- [ ] All new tests pass

---

## Rollback Strategy

1. `auto_fix_p1_p2.py` is archived — restore from `tools/archive/` if needed
2. `generate_full_adg.py` gate call is a localized change — revert with `git checkout`
3. New rules are additive — removing them from `rules/__init__.py` disables them with no other impact
4. `adg_wiring_gap_check.py` is read-only detection — can be deleted with zero codebase impact
