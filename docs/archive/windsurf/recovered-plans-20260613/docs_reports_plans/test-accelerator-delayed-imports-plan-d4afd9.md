# Zero Signal Loss: ADG-Backed Collection Safety + Delayed Import Enforcement

Extend the existing ADG infrastructure with a `collection-safety` subcommand and a delayed-import converter — no new SSOT, no parallel scanners — so every test file collects and executes without fatal early exit, with zero signal loss.

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Current State

| Metric | Value |
|--------|-------|
| Total test files | 885 |
| Reconstructed (placeholder stubs) | 205 (23.2%) |
| Collection-fatal (PATH A) | Unknown — never measured statically |
| Delayed-import compliant (PATH B) | Unknown — never audited |

**Root problem**: Previous batches used runtime `pytest` to validate. Runtime cannot detect the _full set_ of broken imports because one bad file crashes collection and hides the rest. The ADG already extracts the full import graph (G1 `imports` edges) statically — we just need to **query** it for collection safety.

---

## Architecture: Extend ADG, Don't Duplicate It

### What Already Exists (Single SSOT)

| Component | Location | Capability |
|-----------|----------|------------|
| **`ADGStaticScanner`** | `agentic_core/adg/extraction/static_scanner.py` | AST-based edge extraction: G1 `imports`, `dead_imports`, `in_cycle` edges. `include_tests=True` already scans test files. |
| **`ADGIndex`** | `tools/adg_test_accelerator.py` | Builds `self.imports` dict (module→imports), `self.imported_by` (reverse), `transitive_importers()`, `tests_for_changed()`. |
| **`ScanResult`** | `static_scanner.py:878` | Contains all edges, modules list, `syntax_errors` list, `ScanManifest` with cycle/dead-import counts. |
| **`adg_test_accelerator.py`** | `tools/` | CLI with `gap`, `scope`, `groups`, `report` subcommands. Already uses `ADGStaticScanner(include_tests=True)` + `ADGIndex`. |
| **`adg_test_selector.py`** | `tools/adg/` | Redis-backed test selection via `covers` edges. |
| **`ast_test_collector.py`** | `tools/` | AST-based test function collection, skip detection, logic-vs-placeholder classification. |
| **`adg_test_classifier.py`** | `tools/` | Classifies tests as UNIT_STRICT / DEGRADED_PATH / INTEGRATION_INFRA via ADG import graph walk. |

### What's New (Extensions, Not New Tools)

**Extension 1: `cmd_collection_safety` subcommand** added to `adg_test_accelerator.py`

Reuses `ADGIndex.imports` dict to classify each test file's import chain:
```
For each test file T in ADGIndex:
  For each module M that T imports (from ADGIndex.imports[T]):
    If M not in result.modules → MISSING
    If M appears in result.syntax_errors → SYNTAX_ERROR
    If M has in_cycle edge → CIRCULAR
    If M exists on disk but ADG path ≠ filesystem path → STALE_PATH
    Otherwise → RESOLVABLE
  
  T is collection_safe if ALL its imports are RESOLVABLE
```

Maps directly to PyTest Lifecycle triage:
- Check 1.1: MISSING → `production_bug_fix` (module should exist)
- Check 1.2: STALE_PATH → `stale_reference_fix` (wrong import path)
- Neither: ANTI_PATTERN → BLOCKED

**Extension 2: `tools/convert_delayed_imports.py`** (genuinely new — no existing tool does this)

Mechanically converts test files from PATH A → PATH B per PyTest Lifecycle document:
```
BEFORE (PATH A — Fatal Early Exit):
    from agentic_core.L0_routing.enforcement import ExecutionGatewayError
    class TestGateway:
        def test_init(self):
            obj = ExecutionGatewayError("msg")

AFTER (PATH B — Delayed Import):
    class TestGateway:
        def test_init(self):
            from agentic_core.L0_routing.enforcement import ExecutionGatewayError
            obj = ExecutionGatewayError("msg")
```

---

## Phased Execution Plan (200K Context-Friendly)

### Phase 0: Measure via ADG (Wave 0) — 1 session, <50K context
> _"You can't fix what you can't see. The ADG already sees — query it."_

| Step | Action | Exit Gate | Context Size |
|------|--------|-----------|-------------|
| 0.1 | Add `collection-safety` subcommand to `adg_test_accelerator.py` | Subcommand runs | ~5K |
| 0.2 | Run: `python tools/adg_test_accelerator.py collection-safety --json artifacts/collection_safety.json` | JSON artifact produced | ~10K |
| 0.3 | Review collection-safety.json for triage categories | Zero unknowns | ~5K |
| 0.4 | Commit extension | Pushed to main | ~5K |

**Implementation**: 1 subcommand added, queries existing `ADGIndex.imports` — no new AST parsing.

**Output**: `artifacts/collection_safety.json` (ADG-sourced, <5K)

---

### Phase 1: Convert to Delayed Imports (Waves 1-3) — 3 sessions, <150K total

#### Wave 1: Build converter + convert L0 (~75 files) — <50K context
| Step | Action | Exit Gate | Context |
|------|--------|-----------|--------|
| 1.1 | Build `tools/convert_delayed_imports.py` (AST rewriter) | Tool runs on sample | ~15K |
| 1.2 | Convert L0 routing tests to delayed imports | AST parse passes | ~20K |
| 1.3 | `pytest --collect-only tests/unit/agentic_core/L0_routing/` | Zero collection errors | ~10K |
| 1.4 | Commit + push | L0 collection-safe | ~5K |

#### Wave 2: Convert L2 + L5 (~250 files) — <50K context
| Step | Action | Exit Gate | Context |
|------|--------|-----------|--------|
| 2.1 | Convert L2 execution + L5 safety tests | Collection-safe | ~25K |
| 2.2 | `pytest --collect-only` on both layers | Zero collection errors | ~15K |
| 2.3 | Commit + push | L2+L5 collection-safe | ~10K |

#### Wave 3: Convert remaining layers (~560 files) — <50K context
| Step | Action | Exit Gate | Context |
|------|--------|-----------|--------|
| 3.1 | Convert governance, ADG, apps, system_learning, tools | All converted | ~30K |
| 3.2 | `pytest --collect-only tests/` (full suite) | **Zero collection errors** | ~15K |
| 3.3 | Commit + push | Full repo collection-safe | ~5K |

**Phase 1 Exit Gate**: `pytest --collect-only tests/` = 0 errors. **Zero signal loss.**

---

### Phase 2: Fix Missing Dependencies (Waves 4-6) — 3 sessions, <150K total

#### Wave 4: High-blast-radius dependencies — <50K context
| Step | Action | Exit Gate | Context |
|------|--------|-----------|--------|
| 4.1 | Query ADG: sort MISSING modules by fan-in | Priority list | ~10K |
| 4.2 | Fix top-10 missing modules | Modules importable | ~25K |
| 4.3 | Re-run collection-safety | MISSING count ↓ 50%+ | ~10K |
| 4.4 | Commit + push | Top-10 resolved | ~5K |

#### Wave 5: Stale path corrections — <50K context
| Step | Action | Exit Gate | Context |
|------|--------|-----------|--------|
| 5.1 | Fix STALE_PATH imports using ADG suggestions | Paths corrected | ~20K |
| 5.2 | Re-run collection-safety | STALE_PATH → 0 | ~15K |
| 5.3 | Commit + push | All paths correct | ~15K |

#### Wave 6: Anti-pattern and circular resolution — <50K context
| Step | Action | Exit Gate | Context |
|------|--------|-----------|--------|
| 6.1 | Query ADG `in_cycle` edges — break cycles | CIRCULAR → 0 | ~15K |
| 6.2 | Triage ANTI_PATTERN files | Each classified | ~20K |
| 6.3 | Re-run collection-safety: full green | All RESOLVABLE | ~10K |
| 6.4 | Commit + push | 100% resolvable | ~5K |

**Phase 2 Exit Gate**: Collection-safety shows 0 MISSING, 0 STALE_PATH, 0 CIRCULAR.

---

### Phase 3: Test Execution Convergence (Waves 7-9) — 3 sessions, <150K total

#### Wave 7: L0 + L2 execution pass — <50K context
| Step | Action | Exit Gate | Context |
|------|--------|-----------|--------|
| 7.1 | `pytest tests/unit/agentic_core/L0_routing/ -x --tb=short` | Identify failures | ~15K |
| 7.2 | Fix CAT 2 errors per PyTest Lifecycle triage | Tests pass | ~25K |
| 7.3 | Same for L2 execution | Tests pass | ~10K |
| 7.4 | Commit + push | L0+L2 green | ~5K |

#### Wave 8: L5 + governance + ADG execution pass — <50K context
| Step | Action | Exit Gate | Context |
|------|--------|-----------|--------|
| 8.1 | Run pytest on remaining layers | Identify failures | ~20K |
| 8.2 | Fix CAT 2 errors | Tests pass | ~20K |
| 8.3 | Commit + push | L5+gov+ADG green | ~10K |

#### Wave 9: Full suite convergence — <50K context
| Step | Action | Exit Gate | Context |
|------|--------|-----------|--------|
| 9.1 | `pytest tests/ --tb=short -q` (full suite) | Measure pass/fail/skip | ~15K |
| 9.2 | Use `adg_test_accelerator.py scope` for targeted re-runs | Iterate efficiently | ~20K |
| 9.3 | Final: `pytest tests/ -q` | **≥85% pass, 0 collection errors, 0 skips** | ~10K |
| 9.4 | Commit + push | Suite converged | ~5K |

---

## Tool Specifications

### Extension: `cmd_collection_safety` in `adg_test_accelerator.py`

```
CLI (added to existing subcommand parser):
  python tools/adg_test_accelerator.py collection-safety              # Summary
  python tools/adg_test_accelerator.py collection-safety --layer L0   # Single layer
  python tools/adg_test_accelerator.py collection-safety --json <out> # Full JSON

Implementation:
  - Reuses ADGIndex.imports, ADGIndex.imported_by (already built)
  - Queries ScanResult.syntax_errors for SYNTAX_ERROR classification
  - Queries in_cycle edges for CIRCULAR classification
  - Resolves module paths against ScanResult.modules for MISSING/STALE
  - Maps to PyTest Lifecycle Check 1.1 / 1.2 triage categories
  - NO new AST parsing — pure read over existing ADG data
```

### New Tool: `tools/convert_delayed_imports.py`

```
CLI:
  python tools/convert_delayed_imports.py                     # Full conversion
  python tools/convert_delayed_imports.py --layer L0          # Single layer
  python tools/convert_delayed_imports.py --file <path>       # Single file
  python tools/convert_delayed_imports.py --dry-run           # Preview only
  python tools/convert_delayed_imports.py --validate          # Check compliance

Algorithm:
  1. ast.parse() the test file
  2. Classify top-level imports:
     KEEP_TOP  — pytest, unittest, stdlib, typing, __future__
     DELAY     — agentic_core.*, apps_*, system_learning.*
  3. For each DELAY import, find test functions referencing its symbols
  4. Insert import as first statement in each function body
  5. Remove from top level
  6. Validate: ast.parse(new_source) succeeds
```

---

## SSOT Compliance Map

| Concern | SSOT Owner | This Plan Uses |
|---------|-----------|----------------|
| Import graph (G1 edges) | `static_scanner.py` | ✅ Same — via `ADGIndex.imports` |
| Cycle detection | `static_scanner.py` (`in_cycle` edges) | ✅ Same — query existing edges |
| Dead import detection | `static_scanner.py` (`dead_imports` edges) | ✅ Same |
| Test coverage mapping | `ADGIndex.prod_to_tests` | ✅ Same |
| Test classification | `adg_test_classifier.py` | ✅ Same |
| Test selection | `adg_test_selector.py` / `adg_test_accelerator.py scope` | ✅ Same |
| Test function collection | `ast_test_collector.py` | ✅ Same |
| Collection safety triage | **NEW subcommand** in `adg_test_accelerator.py` | Extension, not duplication |
| Delayed import conversion | **NEW tool** `convert_delayed_imports.py` | Genuinely new capability |

**Nothing is duplicated. Two additions: one subcommand extension, one new converter tool.**

---

## Relationship to Existing Tools

| Existing Tool | Role | Change |
|---------------|------|--------|
| `adg_test_accelerator.py` | **Primary orchestrator** | +1 subcommand: `collection-safety` |
| `static_scanner.py` | SSOT for import graph | **No changes** — read-only consumer |
| `ast_test_collector.py` | Test function enumeration | **No changes** — used in Phase 0 |
| `adg_test_classifier.py` | Infra-seam classification | **No changes** — used in Phase 3 |
| `adg/adg_test_selector.py` | Scoped test selection | **No changes** — used in Phase 3 |
| `guard_all_test_imports.py` | try/except guards | **Retired** — replaced by converter |
| `enhance_import_only_tests.py` | Stub enhancement | **No changes** — used in Phase 3 |

---

## Success Metrics

| Metric | Current | Phase 0 | Phase 1 | Phase 2 | Phase 3 |
|--------|---------|---------|---------|---------|---------|
| ADG scans test files | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| Collection-safe (PATH B) | Unknown | Measured | **885** | 885 | 885 |
| Imports resolvable | Unknown | Measured | Same | **885** | 885 |
| Tests passing | ~50 | ~50 | ~50 | ~200 | **750+** |
| Signal loss | HIGH | **ZERO** | ZERO | ZERO | ZERO |
| New SSOTs created | — | **0** | **0** | **0** | **0** |

---

## Critical Path

```
Phase 0 (ADG query) ──► Phase 1 (delayed imports) ──► Phase 2 (fix deps) ──► Phase 3 (pass tests)
     │                         │                            │
     │                         │                            └─ Uses ADG scope for targeted runs
     │                         └─ HARD GATE: collection 100% safe before fixing deps
     └─ HARD GATE: ADG collection-safety report before any conversion
```

**Hard gates** prevent wasted work. All queries flow through existing ADG — single source of truth, zero duplication.

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

