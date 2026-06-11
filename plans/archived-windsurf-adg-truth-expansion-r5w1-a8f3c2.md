---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\adg-truth-expansion-r5w1-a8f3c2.md'
original_relative_path: 'adg-truth-expansion-r5w1-a8f3c2.md'
source_sha256: 154cf9b822ada7fd259f988004b7a9664ef6a39e03281a58d80f0ed7c74feffc
recovered_status: SURVIVED_IN_CURRENT
last_commit: '153652b9eb3'
last_commit_date: '2026-06-07 06:37:48 -0400'
created_date: '2026-04-25'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: adg-truth-expansion-r5w1-a8f3c2
plan_type: infra    # New visitors + precision tables + P-view + CI gate — no production code refactor
---

# ADG Truth Expansion — R5 Wave 1 (A8 + A6 + A12)

Upgrade ADG from "knows syntax and patterns" to "knows truth": hidden write paths, entrypoint reachability, and gate self-consistency.

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| `agentic_core/adg/extraction/visitors/runtime_semantic.py` | Existing `_ExecutionSemanticVisitor` — A8 extends its side-effect detection | ✅ READ |
| `agentic_core/adg/extraction/visitors/__init__.py` | Visitor registry + base classes — A6/A8 add new visitors | ✅ READ |
| `agentic_core/adg/artifact/multi_writer.py` | DDL for `precision_side_effects` table — A8 populates it | ✅ READ |
| `tools/generate/infra_wiring_views.py` | Existing `v_p0_write_bypass_uwg` — A8 creates v2 with behavior-based detection | ✅ READ |
| `tools/generate/materialized_views/` | 42 existing MVs — A6/A8 add new MVs | ✅ READ |
| `.windsurf/hooks.json` | Hook entrypoints — A6 scans for `entrypoint_kind=hook` | ✅ READ |
| `ops_scripts/ci/check_*.py` (61 files) | A12 scans docstring vs actual enforcement | ✅ READ |
| ADG snapshot 04252026_0521 | Baseline — 82835 nodes, 581345 edges | ✅ VERIFIED |

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Checkpoint | Status |
|------|-----------|-------|-------------|------------|--------|
| W1 | 1.1–1.3 | A8 hidden_write_path visitor + precision table + P-view v2 | ~8K | A | 🟢 |
| W1 | 2.1–2.3 | A6 entrypoint_kind visitor + MV + reachability view | ~6K | B | 🟢 |
| W1 | 3.1–3.2 | A12 gate_self_test detector + CI gate | ~4K | C | 🟢 |
| W1 | 4.1 | ADG regeneration + validation + Redis ingest | ~2K | D | 🟢 |

**Total: ~20K tokens across 4 checkpoints, all GREEN**

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| 1.1 | A8: _HiddenWritePathVisitor | `visitors/runtime_semantic.py` (new visitor class) | PP-1: existing visitor only flags `emits_side_effect` edges, not `writes_to_external` with UWG-bypass classification | ~3K | 🔲 TODO |
| 1.2 | A8: populate `precision_side_effects` with write-path metadata | `agentic_core/adg/artifact/multi_writer.py` (add columns) | PP-2: table exists but `effect_type` is generic; need `write_channel`, `uwg_bypass` columns | ~2K | 🔲 TODO |
| 1.3 | A8: `v_p0_write_bypass_uwg_v2` P-view | `tools/generate/infra_wiring_views.py` | PP-3: existing view is import-only; v2 joins behavior edges | ~3K | 🔲 TODO |
| 2.1 | A6: _EntrypointKindVisitor | `visitors/misc.py` (new visitor) + `static_scanner.py` (registration) | PP-4: no visitor emits `entrypoint_kind` on nodes | ~2K | 🔲 TODO |
| 2.2 | A6: Entrypoint scanner (non-AST sources) | New `tools/generate/entrypoint_scanner.py` | PP-5: hooks.json, mcp_config.json, pre-commit, GH workflows not in AST | ~2K | 🔲 TODO |
| 2.3 | A6: `v_reachability_v2` MV + `entrypoint_kind` column on nodes | `multi_writer.py` (DDL), `materialized_views/phase_a_path_authority.py` | PP-6: fan-in=0 treated as dead, but hook/CI entrypoints invisible | ~2K | 🔲 TODO |
| 3.1 | A12: gate_self_test scanner | New `tools/analysis/gate_self_test_scanner.py` | PP-7: no tool compares gate docstring claims vs actual SQL/regex | ~2K | 🔲 TODO |
| 3.2 | A12: `check_gate_doc_vs_query_consistency.py` CI gate | New `ops_scripts/ci/check_gate_doc_vs_query_consistency.py` | PP-8: no CI gate exists for this class | ~2K | 🔲 TODO |
| 4.1 | ADG regeneration + validation | `tools/generate_full_adg.py` | PP-9: must verify new visitors produce edges without breaking existing scan | ~2K | 🔲 TODO |

---

## Gap Register

**GAP-1: `precision_side_effects` table schema is too narrow**
- Current: `effect_type TEXT, target TEXT, confidence REAL`
- Needed: add `write_channel TEXT` (fs|db|cache|http_mutation|metric), `uwg_bypass BOOLEAN`, `source_line INTEGER`
- Impact: A8 cannot store write-path classification without schema extension

**GAP-2: nodes table has no `entrypoint_kind` column**
- Current: no column for how a module is reached (imported vs CLI vs hook vs CI vs MCP)
- Needed: add `entrypoint_kind TEXT DEFAULT 'imported'` column
- Impact: A6 cannot annotate reachability without DDL change

**GAP-3: Existing `_ExecutionSemanticVisitor` emits `emits_side_effect` edges but does not classify write channels**
- Current: `_SIDE_EFFECT_PREFIXES` catches `open`, `redis.`, `sqlite3.`, `requests.` but lumps them as `io` or `mutation`
- Needed: finer classification — `filesystem_write`, `db_write`, `cache_write`, `http_mutation`, `metric_emit`
- Impact: A8 needs this classification to distinguish UWG-bypass from benign IO

---

## Execution Plan

### Phase 1.1 — A8: `_HiddenWritePathVisitor`

**Scope**: New visitor class in `visitors/runtime_semantic.py` that detects write-path calls outside UWG.

**Design**:
```python
@register_visitor("hidden_write_path")
class _HiddenWritePathVisitor(BaseRuntimeVisitor):
    """Detect write operations that bypass the Universal Write Gateway.
    
    Emits edges with relation_type='writes_to_external' and semantic_type
    classifying the write channel:
      - filesystem_write: open(_, 'w'|'a'|'x'), Path.write_text/write_bytes/mkdir
      - db_write: .execute(INSERT|UPDATE|DELETE|UPSERT|CREATE|ALTER|DROP)
      - cache_write: .set/.hset/.lpush/.sadd/.zadd (Redis), .put (cache)
      - http_mutation: requests.post/put/patch/delete, httpx.* mutating verbs
      - metric_emit: .increment/.gauge/.histogram (OTEL/Prometheus)
      - governance_assertion: record_compliance, assert_layer, register_*, declare_*, mark_*
    
    Each edge carries metadata:
      - dynamic_resolution: 'uwg_bypass=true' if the module does NOT import
        from agentic_core.L4_state or write_gateway
      - confidence: 0.9 for direct calls, 0.7 for attribute dispatch
    """
```

**Write-channel classification heuristics** (AST-recognizable):

| Channel | AST Pattern | Example |
|---------|-------------|---------|
| filesystem_write | `open(_, 'w'/'a'/'x')`, `Path.write_text/write_bytes`, `shutil.copy/move` | `open("out.json", "w")` |
| db_write | `.execute("INSERT/UPDATE/DELETE")`, `.executemany`, cursor mutation | `cur.execute("INSERT INTO ...")` |
| cache_write | `redis.set/hset/lpush/sadd/zadd`, `cache.put/set` | `r.set("key", "val")` |
| http_mutation | `requests.post/put/patch/delete`, `httpx.AsyncClient.post/...` | `requests.post(url, data=...)` |
| metric_emit | `.increment/.gauge/.histogram/.counter` | `meter.counter("x").add(1)` |
| governance_assertion | `record_compliance/assert_layer/register_*/declare_*/mark_*` | `record_compliance(...)` |

**UWG-bypass detection**: After emitting `writes_to_external` edge, check if the source module imports from `agentic_core.L4_state` or contains `write_gateway`/`uwg` in its import edges. If not, set `dynamic_resolution='uwg_bypass=true'`.

**Acceptance**: Visitor registered, `py_compile` passes, produces `writes_to_external` edges on a test file.

---

### Phase 1.2 — A8: Extend `precision_side_effects` table

**Scope**: Add columns to `precision_side_effects` DDL in `multi_writer.py`.

**DDL change**:
```sql
-- Existing columns: id, node_id, effect_type, target, confidence
ALTER TABLE precision_side_effects ADD COLUMN write_channel TEXT DEFAULT '';
ALTER TABLE precision_side_effects ADD COLUMN uwg_bypass BOOLEAN DEFAULT FALSE;
ALTER TABLE precision_side_effects ADD COLUMN source_line INTEGER DEFAULT 0;
```

Since SQLite `ALTER TABLE ADD COLUMN` is safe (existing rows get defaults), this is non-breaking. The multi_writer DDL template should use `CREATE TABLE IF NOT EXISTS` with the new columns included.

**Population**: The `_HiddenWritePathVisitor` edges get persisted into `precision_side_effects` during the existing precision-stage write in `multi_writer.py`. Add a mapping from `writes_to_external` edges → `precision_side_effects` rows with `write_channel`, `uwg_bypass`, and `source_line` populated.

**Acceptance**: DDL applies cleanly on existing DB, new columns default correctly.

---

### Phase 1.3 — A8: `v_p0_write_bypass_uwg_v2` P-view

**Scope**: New P-view in `infra_wiring_views.py` that joins behavior-detected write paths (not just import-detected).

**View SQL** (conceptual):
```sql
CREATE VIEW IF NOT EXISTS v_p0_write_bypass_uwg_v2 AS
-- Layer 1: existing import-based detection (preserved)
SELECT * FROM v_p0_write_bypass_uwg
UNION ALL
-- Layer 2: behavior-based detection from writes_to_external edges
SELECT
    e.id AS violation_edge_id,
    n_src.id AS writer_id,
    n_src.resolved_path AS writer_file,
    n_src.layer AS writer_layer,
    e.symbol AS write_symbol,
    e.line_no AS write_line,
    'P0: behavior-detected write bypass outside UWG (' || e.semantic_type || ')' AS violation_type
FROM edges e
JOIN nodes n_src ON e.src_id = n_src.id
WHERE e.relation_type = 'writes_to_external'
  AND e.dynamic_resolution = 'uwg_bypass=true'
  AND n_src.resolved_path NOT LIKE '%UniversalWrite%'
  AND n_src.resolved_path NOT LIKE '%write_gateway%'
  AND n_src.resolved_path NOT LIKE '%uwg%'
  AND n_src.resolved_path NOT LIKE '%mutation_prohibition%'
  AND n_src.resolved_path NOT LIKE 'tools/%'
  AND n_src.resolved_path NOT LIKE 'tests/%'
  AND n_src.resolved_path NOT LIKE 'ops_scripts/%'
  AND n_src.resolved_path NOT LIKE 'infrastructure/%'
  AND n_src.layer IN ('L0', 'L1', 'L3', 'L_APP')
;
```

**Also**: Add `v_p0_write_bypass_uwg_v2` to the `_ALL_VIEW_NAMES` tuple and the PVIEW_SPECS in `adg/mv_projection.py`.

**Acceptance**: View returns rows for files that write to external resources without UWG import, including cases the import-only view misses.

---

### Phase 2.1 — A6: `_EntrypointKindVisitor` (AST sources)

**Scope**: New visitor in `visitors/misc.py` that detects `if __name__ == "__main__"` blocks and marks the module as `entrypoint_kind=cli`.

**Design**:
```python
@register_visitor("entrypoint_kind")
class _EntrypointKindVisitor(BaseADGVisitor):
    """Detect entrypoint kind for modules.
    
    AST-detectable kinds:
      - cli: module has `if __name__ == "__main__"` block
      - test: module path matches tests/ pattern
    
    Non-AST kinds (populated by entrypoint_scanner.py):
      - hook: referenced in .windsurf/hooks.json
      - ci: referenced in .github/workflows/*.yml or .pre-commit-config.yaml
      - mcp: referenced in .windsurf/mcp_config.json
    
    Emits `entrypoint_kind` edges from module to a synthetic ADG::Entrypoint node.
    """
```

**Edge emission**: For each detected entrypoint, emit an edge:
```
from_name=<module_adg>, relation_type='entrypoint_kind', to_name='ADG::Entrypoint::<kind>'
```
This allows downstream MVs to join on `relation_type='entrypoint_kind'` to compute reachability.

**Acceptance**: Visitor detects `if __name__ == "__main__"` blocks in `tools/mcp/*.py`, `ops_scripts/*.py`, etc.

---

### Phase 2.2 — A6: Entrypoint scanner (non-AST sources)

**Scope**: New `tools/generate/entrypoint_scanner.py` that parses config files and emits entrypoint edges.

**Sources**:

| Source File | Field | entrypoint_kind |
|-------------|-------|-----------------|
| `.windsurf/hooks.json` | `hooks.*.[].command` | `hook` |
| `.windsurf/mcp_config.json` | `mcpServers.*.command` + `mcpServers.*.args[]` | `mcp` |
| `.pre-commit-config.yaml` | `repos.*.hooks[].entry` | `hook` |
| `.github/workflows/*.yml` | `jobs.*.steps[].run` (python invocations) | `ci` |
| `pyproject.toml` | `[project.scripts]` | `cli` |

**Implementation**: Parse each source, extract Python file references, resolve to repo-relative paths, emit `entrypoint_kind` edges into the edge list (appended before SQLite write).

**Acceptance**: Scanner identifies all 15+ Windsurf hook scripts, all 12 MCP server scripts, and all CI-invoked Python files.

---

### Phase 2.3 — A6: `entrypoint_kind` column + `v_reachability_v2` MV

**Scope**: Add `entrypoint_kind` column to `nodes` DDL and create a reachability view.

**DDL change**:
```sql
ALTER TABLE nodes ADD COLUMN entrypoint_kind TEXT DEFAULT 'imported';
-- Values: imported | cli | hook | ci | mcp | test | scheduled
```

**Population**: After edge scan, update `nodes.entrypoint_kind` based on `entrypoint_kind` edges. If a node has multiple entrypoint edges, use the most-specific kind (mcp > hook > ci > cli > imported).

**View**:
```sql
CREATE VIEW IF NOT EXISTS v_reachability_v2 AS
SELECT
    n.id AS node_id,
    n.resolved_path AS file_path,
    n.layer AS layer,
    n.entrypoint_kind AS entrypoint_kind,
    COALESCE(fanin.import_count, 0) AS import_fan_in,
    CASE
        WHEN n.entrypoint_kind != 'imported' THEN 'reachable'
        WHEN fanin.import_count > 0 THEN 'reachable'
        ELSE 'orphaned'
    END AS reachability_status
FROM nodes n
LEFT JOIN (
    SELECT dst_id, COUNT(*) AS import_count
    FROM edges WHERE relation_type = 'imports'
    GROUP BY dst_id
) fanin ON fanin.dst_id = n.id
WHERE n.entity_type = 'Module'
  AND n.resolved_path NOT LIKE 'tests/%'
  AND n.resolved_path NOT LIKE 'archives/%'
;
```

**Acceptance**: View correctly classifies `ops_scripts/` and `tools/mcp/` modules as `reachable` via `hook`/`mcp`/`ci` entrypoints even when import fan-in is 0.

---

### Phase 3.1 — A12: `gate_self_test_scanner.py`

**Scope**: New analysis tool that compares gate docstring claims vs actual enforcement logic.

**Design**:
```python
"""Scan CI gate files for docstring-vs-enforcement drift.

For each ops_scripts/ci/check_*.py file:
1. Extract module docstring + first comment block (claimed invariant)
2. Extract all SQL queries, regex patterns, path checks (actual enforcement)
3. Compare: does the claim match what's actually checked?

Output: JSON report with entries:
  {
    "file": "check_exception_contract.py",
    "claimed": "No bare except Exception without guardian comment",
    "enforced_patterns": ["except Exception", "guardian"],
    "claim_matches_enforcement": true,
    "gaps": []
  }
"""
```

**Claim extraction**: Parse module docstring, look for keywords like "ensures", "checks", "no ", "forbids", "requires", "must".

**Enforcement extraction**: Walk AST for:
- String literals in `re.compile()`, `re.search()`, `re.match()` → regex patterns
- SQL strings in `cursor.execute()` → SQL queries
- Path references in `Path()`, `glob()` → file checks
- Function calls to `sys.exit()` → fail conditions

**Comparison heuristic**: For each claimed keyword (e.g., "bare except"), check if any enforcement pattern contains the keyword or a synonym. Flag if claim mentions a concept with zero enforcement evidence.

**Acceptance**: Scanner runs on all 61 `check_*.py` files and produces a JSON report.

---

### Phase 3.2 — A12: `check_gate_doc_vs_query_consistency.py` CI gate

**Scope**: CI gate that fails if any gate file has a docstring claim with no matching enforcement.

**Implementation**:
```python
"""CI gate: gate docstring claims must match actual enforcement.

Runs gate_self_test_scanner.py and fails if any entry has
claim_matches_enforcement=False with a non-empty claimed field.

Exit codes:
  0 — all claims match enforcement
  1 — one or more gates have drifted claims
  2 — scanner error (fail-open: log warning, exit 0)
"""
```

**Integration**: Add to `.pre-commit-config.yaml` and `ops_scripts/ci/run_contract_gates.py`.

**Acceptance**: Gate runs, exits 0 on current codebase (or surfaces legitimate drift for triage).

---

### Phase 4.1 — ADG Regeneration + Validation

**Scope**: Run full ADG generation with new visitors, verify edge counts, validate SQLite integrity.

**Commands**:
```bash
# Regenerate ADG with new visitors
python tools/generate_full_adg.py

# Verify new edge types exist
sqlite3 artifacts/adg/adg_indexed_<ts>.sqlite "SELECT relation_type, COUNT(*) FROM edges WHERE relation_type IN ('writes_to_external', 'entrypoint_kind') GROUP BY relation_type"

# Verify v_p0_write_bypass_uwg_v2 returns rows
sqlite3 artifacts/adg/adg_indexed_<ts>.sqlite "SELECT COUNT(*) FROM v_p0_write_bypass_uwg_v2"

# Verify v_reachability_v2 classifies entrypoint modules
sqlite3 artifacts/adg/adg_indexed_<ts>.sqlite "SELECT entrypoint_kind, COUNT(*) FROM v_reachability_v2 GROUP BY entrypoint_kind"

# Run gate self-test
python tools/analysis/gate_self_test_scanner.py

# Ingest to Redis
python tools/adg/adg_redis_ingest.py
```

**Acceptance**: ADG generation succeeds, new edge types appear, new views return data, Redis ingest completes.

---

## ADG_HOTSPOT_REPORT

| File | Layer | Fan-In | Violation Count | Impact | Archetype | Surface |
|------|-------|--------|-----------------|--------|-----------|---------|
| `agentic_core/adg/extraction/visitors/runtime_semantic.py` | L1 | 3 | 0 (new code) | N/A | — | — |
| `agentic_core/adg/artifact/multi_writer.py` | L4 | 8 | 0 (schema extension) | N/A | — | — |
| `tools/generate/infra_wiring_views.py` | L_TOOLS | 5 | 0 (new view) | N/A | — | — |
| `ops_scripts/ci/check_*.py` (61 files) | L_OPS | 0 | ~5 expected drift | ~5 | ORCHESTRATOR | Observability |

Note: This is an infrastructure extension plan (new visitors + tables + views), not a refactoring plan. No existing violations are being remediated; the plan *creates new detection capability*.

---

## ADG_GRAPH_LAYER_EVIDENCE

| Primitive | Usage | Evidence |
|-----------|-------|----------|
| `mv_graph_chokepoint_bridges` | A8: join with `writes_to_external` edges to find writes that bypass chokepoints | Will identify write-path chokepoint bypasses not visible today |
| `v_p0_write_bypass_uwg` | A8: existing import-only view, preserved as layer 1 of v2 | Baseline: currently catches import-based bypasses only |
| `emits_side_effect` semantic edge | A8: existing edge type from `_ExecutionSemanticVisitor`, extended with finer classification | Currently lumps all IO as `io` or `mutation`; A8 adds `write_channel` taxonomy |
| `precision_side_effects` table | A8: populated with write-channel metadata from new visitor | Currently sparse; A8 fills it with structured write-path data |
| `imports` edge | A6: used in `v_reachability_v2` to compute import fan-in | Baseline: fan-in=0 currently treated as dead code |

Semantic edges used: `writes_to_external` (NEW), `entrypoint_kind` (NEW), `emits_side_effect` (EXTENDED), `imports` (EXISTING).

P-view cross-references: `v_p0_write_bypass_uwg_v2` (NEW), `v_reachability_v2` (NEW).

---

## Rules

- New visitors must use `@register_visitor()` decorator and inherit from appropriate base class
- DDL changes must be `ALTER TABLE ADD COLUMN` (non-breaking) or `CREATE TABLE IF NOT EXISTS` / `CREATE VIEW IF NOT EXISTS`
- No changes to production code outside `agentic_core/adg/`, `tools/generate/`, `tools/analysis/`, `ops_scripts/ci/`
- All new Python files must pass `py_compile`
- ADG regeneration must complete with exit code 0 (SC-1 structural conformance may still fail — that's pre-existing)

---

## Success Criteria

- [ ] `_HiddenWritePathVisitor` produces `writes_to_external` edges with `write_channel` classification
- [ ] `precision_side_effects` table has new columns `write_channel`, `uwg_bypass`, `source_line`
- [ ] `v_p0_write_bypass_uwg_v2` returns rows not caught by v1 (behavior-detected bypasses)
- [ ] `_EntrypointKindVisitor` detects `if __name__ == "__main__"` blocks
- [ ] `entrypoint_scanner.py` identifies all hook/MCP/CI entrypoints from config files
- [ ] `nodes.entrypoint_kind` column populated with non-`imported` values for entrypoint modules
- [ ] `v_reachability_v2` classifies `ops_scripts/` and `tools/mcp/` as `reachable` (not `orphaned`)
- [ ] `gate_self_test_scanner.py` produces JSON report on all 61 CI gates
- [ ] `check_gate_doc_vs_query_consistency.py` CI gate runs and exits cleanly
- [ ] Full ADG regeneration succeeds with new visitors active

---

## Implementation Commands

```bash
# Phase 1.1-1.3: A8 hidden write path
python -m py_compile agentic_core/adg/extraction/visitors/runtime_semantic.py
python -m py_compile agentic_core/adg/artifact/multi_writer.py
python -m py_compile tools/generate/infra_wiring_views.py

# Phase 2.1-2.3: A6 entrypoint kind
python -m py_compile agentic_core/adg/extraction/visitors/misc.py
python -m py_compile tools/generate/entrypoint_scanner.py
python -m py_compile agentic_core/adg/artifact/multi_writer.py

# Phase 3.1-3.2: A12 gate self-test
python -m py_compile tools/analysis/gate_self_test_scanner.py
python -m py_compile ops_scripts/ci/check_gate_doc_vs_query_consistency.py

# Phase 4.1: Full validation
python tools/generate_full_adg.py
python tools/adg/adg_redis_ingest.py
python tools/analysis/gate_self_test_scanner.py
python ops_scripts/ci/check_gate_doc_vs_query_consistency.py
```

---

## Rollback Strategy

1. New visitors are additive — disabling them requires only removing from the visitor list in `static_scanner.py`
2. New DDL columns have defaults — existing code ignores them harmlessly
3. New P-views can be `DROP VIEW`'d without affecting existing views
4. New CI gate can be removed from `.pre-commit-config.yaml`
5. If ADG regeneration fails, the previous snapshot remains valid in `artifacts/adg/`

---

## Acceptance Criteria

| Metric | Target | Verification |
|--------|--------|--------------|
| `writes_to_external` edge count | >0 (at least some hidden writes detected) | `SELECT COUNT(*) FROM edges WHERE relation_type='writes_to_external'` |
| `v_p0_write_bypass_uwg_v2` row count | ≥ v1 count (v1 is subset) | `SELECT COUNT(*) FROM v_p0_write_bypass_uwg_v2` |
| `entrypoint_kind != 'imported'` node count | >10 (hook/MCP/CI/CLI modules) | `SELECT COUNT(*) FROM nodes WHERE entrypoint_kind != 'imported'` |
| `v_reachability_v2.orphaned` count | < current fan-in=0 count | Compare before/after |
| Gate self-test drift count | Finite (triage-able) | JSON report output |
| ADG generation exit code | 0 | Process exit code |
