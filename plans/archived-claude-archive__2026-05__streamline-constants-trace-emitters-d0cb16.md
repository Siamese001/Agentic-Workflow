---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\streamline-constants-trace-emitters-d0cb16.md'
original_relative_path: '_archive\\2026-05\\streamline-constants-trace-emitters-d0cb16.md'
source_sha256: 2527fb8bcaf956e236fa7fb6239397142426183c848c8df64135f313df37ddce
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Streamline Constants & Trace Emitters — Repository-Wide Cleanup

Aggressively consolidate duplicated constants, eliminate trace emitter pollution, and remove legacy shims across the codebase (excluding `_constants.py` which is handled separately).

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| Wave 1 | T1-T3 | Trace emitter consolidation — remove repetitive `_emit_*` calls from 276 L0_routing files | 45,000 🟢 | ADG ingest after each batch; stop if edge count drops >5% | PENDING | ≤100 emitters remain in L0_routing (was 21,947) |
| Wave 2 | C1-C3 | Duplicated constants consolidation — unify MAX_RETRIES, DEFAULT_SLEEP, etc. across 417 files into single SSOT | 35,000 🟢 | No circular imports created; backward compat via re-export only | PENDING | 1 canonical constants location; 0 duplication |
| Wave 3 | S1-S2 | Shim/Proxy file cleanup — remove trace emitters from structure_blueprint_config.py, ssot_tier_constants.py, etc. | 25,000 🟢 | Keep import paths functional; remove runtime side effects | PENDING | All shims are pure re-exports; no _emit_* calls |
| Wave 4 | V1-V2 | ADG regeneration + verification — full scan, coverage validation, downstream consumer tests | 20,000 🟢 | Redis hot cache refresh; MCP config sync | PENDING | ADG edge count stable; downstream tests pass |

**Total: 125,000 tokens across 4 waves, all GREEN** (well below 197,000 warning threshold)

---

## Gap Register

**GAP-1: Trace Emitter Proliferation**
- 21,947+ `_emit_*` matches across agentic_core (mostly L0_routing)
- Pattern: Every file has 80-200+ repetitive lifecycle trace calls
- Files like `config_store.py` have 126 identical `_emit_reads_through` calls at module level
- Impact: Module import side effects, noise, maintenance burden, import-time overhead

**GAP-2: Constants Duplication**
- 417 files contain identical copies of 8 constants (MAX_RETRIES, DEFAULT_SLEEP, THRESHOLD, BUFFER_SIZE, BATCH_SIZE, MAX_DEPTH, MAX_FILES, DEFAULT_TIMEOUT)
- No canonical SSOT — changes require 417-file edits
- Impact: Inconsistency risk, maintenance nightmare, drift between modules

**GAP-3: Shim/Proxy File Pollution**
- `structure_blueprint_config.py`: 119 lines of `_emit_*` calls for simple re-exports
- `ssot_tier_constants.py`: 81 lines of `_emit_*` calls for 5 re-exported constants
- `path_constants.py`: 204 `_emit_*` calls mixed with actual definitions
- Impact: Shim files have runtime side effects, violating "pure re-export" contract

**GAP-4: Builder Function Complexity**
- `_builders.py`: `_deep_freeze`, `_build_lcd_subfolders_template`, `_build_layer_definition` still used but could be simplified
- `config_store.py`: Complex caching with trace pollution
- Impact: Over-engineered for current needs, hard to reason about

---

## Execution Plan

### Phase T1 — Trace Emitter Inventory & Categorization
**Scope**: Enumerate all `_emit_*` calls across agentic_core; categorize by file, layer, emitter type

**Commands**:
```bash
# Inventory all trace emitters by layer
python -c "
import subprocess
layers = ['L0_routing', 'L1_cognition', 'L2_execution', 'L3_orchestration', 'L4_state', 'L5_safety', 'L6_observability']
for layer in layers:
    result = subprocess.run(['rg', '-c', '_emit_\\w+\\(', f'agentic_core/{layer}'], capture_output=True, text=True)
    print(f'{layer}: {result.stdout.strip() if result.stdout else 0} matches')
"

# Top files by emitter count
rg '_emit_\w+\(' agentic_core/L0_routing --stats | head -50
```

**Acceptance**: 
- [ ] Complete inventory written to `artifacts/trace_emitter_inventory.json`
- [ ] Files ranked by emitter count (priority for cleanup)
- [ ] Categorization: P0/P1/P2/P3/P4 lifecycle phases identified

---

### Phase T2 — L0_routing Trace Emitter Cleanup
**Scope**: Remove ~21,000 repetitive `_emit_*` calls from L0_routing (276 files); retain only meaningful semantic trace points

**Commands**:
```bash
# Dry run: identify auto-removable patterns
python tools/cleanup_trace_emitters.py --layer L0_routing --dry-run --output artifacts/l0_emitter_cleanup_plan.json

# Execute cleanup (batch of 50 files at a time)
python tools/cleanup_trace_emitters.py --layer L0_routing --batch-size 50 --checkpoint every-batch

# Verify after each batch
python tools/generate/generate_full_adg.py --quick
pytest tests/unit/agentic_core/L0_routing/ -x --tb=short
```

**Acceptance**:
- [ ] ≤100 `_emit_*` calls remain in L0_routing (was 21,947)
- [ ] Remaining calls are meaningful (not repetitive module-level spam)
- [ ] All L0_routing tests pass
- [ ] ADG edge count change <5%

---

### Phase T3 — Cross-Layer Trace Emitter Cleanup
**Scope**: Apply same cleanup to L1-L6 layers; consolidate to single trace entry points per module

**Commands**:
```bash
# Cleanup remaining layers
for layer in L1_cognition L2_execution L3_orchestration L4_state L5_safety L6_observability; do
    python tools/cleanup_trace_emitters.py --layer $layer --batch-size 30
done

# Full regeneration and verification
python tools/adg/generate_full_adg.py
python tools/adg/adg_redis_ingest.py --force
pytest tests/unit/agentic_core/ -x --tb=short
```

**Acceptance**:
- [ ] All layers: ≤20 `_emit_*` calls per layer (consolidated to entry points)
- [ ] No module-level repetitive emitters remain
- [ ] Full test suite passes (19/19 scanner tests, all unit tests)
- [ ] ADG edge count stable (±2%)

---

### Phase C1 — Canonical Constants SSOT Creation
**Scope**: Create single canonical location for numeric constants; eliminate 417-file duplication

**Commands**:
```bash
# Create canonical constants module (already partially exists, expand it)
# SSOT: agentic_core/config/core/constants_config.py

# Audit all duplications
python tools/find_duplicated_constants.py --constants "MAX_RETRIES,DEFAULT_SLEEP,THRESHOLD,BUFFER_SIZE,BATCH_SIZE,MAX_DEPTH,MAX_FILES,DEFAULT_TIMEOUT" --output artifacts/duplicated_constants_inventory.json

# Generate migration script
python tools/generate_constants_migration.py --canonical agentic_core/config/core/constants_config.py --output tools/migrate_to_canonical_constants.py
```

**Acceptance**:
- [ ] Single SSOT module: `agentic_core/config/core/constants_config.py` with all 8 canonical constants
- [ ] Complete inventory of 417 files with duplications
- [ ] Migration script generated and tested on 10 sample files

---

### Phase C2 — Downstream Constants Migration
**Scope**: Execute migration across 417 files; replace inline constants with canonical imports

**Commands**:
```bash
# Phase 1: agentic_core internal (200 files)
python tools/migrate_to_canonical_constants.py --scope agentic_core --batch-size 40 --checkpoint every-batch

# Phase 2: apps_* packages (150 files)
python tools/migrate_to_canonical_constants.py --scope apps --batch-size 30 --checkpoint every-batch

# Phase 3: tests (67 files)
python tools/migrate_to_canonical_constants.py --scope tests --batch-size 20 --checkpoint every-batch

# Verification
rg "^MAX_RETRIES = 3$" --type py | wc -l  # Should be 0 (or 1 in canonical)
rg "^DEFAULT_SLEEP = 1.0$" --type py | wc -l  # Should be 0 (or 1 in canonical)
```

**Acceptance**:
- [ ] 0 inline constant definitions outside canonical module
- [ ] All imports use: `from agentic_core.config.core.constants_config import MAX_RETRIES, ...`
- [ ] No circular imports introduced
- [ ] All tests pass

---

### Phase C3 — Re-export Shim Cleanup
**Scope**: Remove shim-level trace emitters; make re-exports pure

**Commands**:
```bash
# Clean structure_blueprint_config.py
python tools/cleanup_shim_emitters.py --file agentic_core/L5_safety/config/structure_blueprint_config.py --dry-run
python tools/cleanup_shim_emitters.py --file agentic_core/L5_safety/config/structure_blueprint_config.py

# Clean ssot_tier_constants.py
python tools/cleanup_shim_emitters.py --file agentic_core/L0_routing/config/ssot_tier_constants.py

# Clean interfaces/path_constants.py
python tools/cleanup_shim_emitters.py --file agentic_core/interfaces/path_constants.py

# Verify shims are pure
python -c "
from agentic_core.L5_safety.config import structure_blueprint_config
# Should have no side effects on import
print('Import successful, no side effects')
"
```

**Acceptance**:
- [ ] All shim files: 0 `_emit_*` calls
- [ ] Shims are pure re-exports (no runtime side effects)
- [ ] Import timing unchanged (no import-time overhead)

---

### Phase S1 — Legacy Builder Function Audit
**Scope**: Review `_builders.py`, `config_store.py` for simplification opportunities

**Commands**:
```bash
# ADG analysis: which builder functions are actually called
python tools/adg/analyze_symbol_usage.py --symbols "_deep_freeze,_build_lcd_subfolders_template,_build_layer_definition" --output artifacts/builder_usage_analysis.json

# Review config_store complexity
python tools/adg/analyze_symbol_usage.py --symbols "_capture_start_of_run_state,_START_OF_RUN_CACHE,_IN_WRITE_CONTEXT" --output artifacts/config_store_usage.json
```

**Acceptance**:
- [ ] Usage analysis for all builder symbols
- [ ] Dead code identified for removal
- [ ] Simplification plan for complex functions

---

### Phase S2 — Simplification Execution
**Scope**: Remove dead code; simplify over-engineered functions

**Commands**:
```bash
# Remove unused builder functions (if analysis shows unused)
python tools/remove_dead_code.py --scope agentic_core/L5_safety/config/structure_blueprint --analysis artifacts/builder_usage_analysis.json

# Simplify config_store (remove repetitive trace calls)
python tools/simplify_config_store.py --file agentic_core/L0_routing/meta_control/config_store.py --remove-emitters

# Verify
pytest tests/unit/agentic_core/L5_safety/config/structure_blueprint/ -x
pytest tests/unit/agentic_core/L0_routing/meta_control/ -x
```

**Acceptance**:
- [ ] Dead builder functions removed (if confirmed unused)
- [ ] config_store.py simplified (≤50% size reduction)
- [ ] All tests pass

---

### Phase V1 — Full ADG Regeneration
**Scope**: Complete ADG rebuild with cleaned codebase

**Commands**:
```bash
# Full ADG generation
python tools/generate/generate_full_adg.py --output artifacts/adg/adg_indexed_$(date +%Y%m%d_%H%M).sqlite

# Redis hot cache refresh
python tools/adg/adg_redis_ingest.py --force

# Stats comparison
python tools/adg/compare_adg_stats.py --before artifacts/adg/adg_pre_cleanup.sqlite --after artifacts/adg/adg_post_cleanup.sqlite
```

**Acceptance**:
- [ ] Fresh ADG generated successfully
- [ ] Redis hot cache populated
- [ ] Edge count: within ±5% of pre-cleanup (major variance indicates issues)

---

### Phase V2 — Downstream Verification
**Scope**: Verify all downstream consumers work correctly

**Commands**:
```bash
# Full test collection
python -m pytest tests/ --collect-only -q 2>&1 | tail -5

# Critical path tests
pytest tests/unit/agentic_core/L0_routing/ -x --tb=short
pytest tests/unit/agentic_core/L5_safety/config/ -x --tb=short
pytest tests/apps_*/ -x --ignore-glob="*_adg.py" --tb=short

# Integration tests
pytest tests/integration/ -x -k "config or structure or blueprint" --tb=short

# Final verification
python tools/adg/verify_adg_consistency.py
```

**Acceptance**:
- [ ] Test collection: 0 errors
- [ ] L0_routing tests: 100% pass
- [ ] L5_safety/config tests: 100% pass
- [ ] apps_* tests: no regressions
- [ ] ADG consistency: PASS

---

## Rules

1. **Aggressive cleanup**: Remove repetitive trace emitters entirely (don't just consolidate)
2. **Single SSOT**: Only `agentic_core/config/core/constants_config.py` defines canonical constants
3. **Pure shims**: Re-export files must have zero side effects (no _emit_* calls)
4. **Batch execution**: Process files in batches of 20-50 with checkpoints
5. **ADG validation**: Regenerate ADG and verify edge counts after each wave
6. **Test gating**: All tests must pass before proceeding to next phase
7. **No circular imports**: Constants module must be importable from any layer without upward deps

---

## Success Criteria

- [ ] **Trace Emitters**: ≤500 total `_emit_*` calls across entire agentic_core (was 21,947+)
- [ ] **Constants Duplication**: 0 duplicated constants outside canonical module (was 417 files)
- [ ] **Shim Purity**: 100% of shim files have zero side effects
- [ ] **Test Pass Rate**: 100% (no regressions)
- [ ] **ADG Stability**: Edge count within ±5% of baseline
- [ ] **Import Time**: No measurable import-time regression

---

## Implementation Commands

```bash
# Full execution sequence
python tools/cleanup_trace_emitters.py --all-layers --batch-size 50
python tools/migrate_to_canonical_constants.py --all-scopes
python tools/cleanup_shim_emitters.py --all-shims
python tools/generate/generate_full_adg.py
python tools/adg/adg_redis_ingest.py --force
pytest tests/ -x --tb=short
```

---

## Rollback Strategy

If things go wrong:
1. **Git revert**: `git revert HEAD~N` (commits are per-wave)
2. **ADG restore**: Use backup from `artifacts/adg/backups/`
3. **Redis restore**: Re-ingest from known-good SQLite file
4. **Constants fallback**: Restore inline constants temporarily if canonical import fails

---

## Acceptance Criteria Summary

| Metric | Target | Verification |
|---|---|---|
| Trace emitter count | ≤500 | `rg '_emit_\w+\(' agentic_core --count` |
| Constants duplication | 0 files | `rg "^MAX_RETRIES = 3$" agentic_core --type py \| wc -l` = 1 |
| Shim side effects | 0 | Import shims in isolation, verify no logging |
| Test pass rate | 100% | `pytest tests/ --tb=no -q` shows 0 failures |
| ADG edge drift | ±5% | Compare pre/post edge counts |
| Import time | ≤baseline | `time python -c "from agentic_core.L0_routing.config.path_constants import *"` |
