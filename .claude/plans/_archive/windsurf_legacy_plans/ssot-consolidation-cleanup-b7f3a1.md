# SSOT Consolidation: Eliminate Triple-Redundancy in Structure Blueprint

Eliminate the triple-redundancy between `_constants.py` (1,978 lines), `territories.yaml` (791 lines), and `build_sovereign_territories()` (1,400 lines of dead code) by collapsing to a two-file architecture: YAML for structure, Python for routing rules and operational configs.

---

## Context & Web Research Findings

### Industry Best Practices (2025–2026)

**From "Structuring Your Codebase for AI Tools" (Propel, 2025):**
- AI tools perform best with **predictable, conventional directory structures** — not deeply nested programmatic declarations
- **Context engineering > prompt engineering** — systems that automatically gather relevant context outperform hand-curated ones
- **Preventing context rot**: automated freshness checks, documentation drift detection, CI/CD validation
- Single `AGENTS.md` + convention-based structure is the modern standard

**From "Repository Intelligence in AI Coding Tools" (BuildMVPFast, 2026):**
- **Code graphs >> flat file declarations** — Augment Code's knowledge graph showed 80% quality improvement via MCP
- **AST-based structural chunking** (tree-sitter) improves RAG by 5.5 points over naive approaches
- Context architecture matters **as much or more than model choice**
- A weaker model with good context outperforms a stronger model with poor context

### How This Applies to Agentic-Workflow

This codebase already has the RIGHT tools:
- **ADG** = code knowledge graph (69,739 nodes, 534,867 edges) — superior to any static Python dict
- **territories.yaml** = conventional, AI-readable structure definition
- **MCP servers** = live context retrieval (ADG SQLite, Redis cache, memory graph)

What's WRONG is the **triple-redundancy** maintaining the same directory tree in 3 places:
1. `territories.yaml` (YAML SSOT — correct)
2. `LAYER_OVERRIDES` in `_constants.py` (subfolder trees — redundant)
3. `build_sovereign_territories()` in `_constants.py` (1,400 lines of dead code building a 4th copy)

This causes **phantom drift** (the Cat 4 cleanup problem), **maintenance tax** (updating 2+ files per directory change), and **context rot** (stale Python dicts confusing both humans and AI tools).

---

## ADG Fan-in Analysis (Blast Radius)

| Symbol | ADG Node | Consumers | Impact |
|--------|----------|-----------|--------|
| `build_sovereign_territories()` | 17022 | 2 test files only | **DEAD** — safe to remove |
| `LAYER_OVERRIDES` | 17016 | `__init__.py` (1 consumer) | Internal — refactor |
| `HEALING_CONFIG` | 17015 | `__init__.py`, `governance.py`, shim (3) | **ALIVE** — keep |
| `GRAVITY_CONFIG` | 17013 | Same 3 consumers | **ALIVE** — keep |
| `MCP_CAPABILITIES` | 17017 | Same 3 consumers | **ALIVE** — keep |
| `SubfolderDefinition` | 17019 | `__init__.py`, `territories.py`, shim (3) | **ALIVE** — keep type |
| `TerritoryDefinition` | 17020 | Same pattern | **ALIVE** — keep type |
| `SOVEREIGN_TERRITORIES` | (commented out L1768) | N/A | **DEAD** — already removed |

---

## Wave Structure

| Wave | Metric | Scope | Checkpoint | Tokens |
|------|--------|-------|------------|--------|
| Wave 1 | Dead code removal | `_constants.py` lines 584–1907 | A: tests pass | ~8K 🟢 |
| Wave 2 | LAYER_OVERRIDES slim | `_constants.py` lines 112–512 | B: routing rules preserved | ~6K 🟢 |
| Wave 3 | Shim + package cleanup | `structure_blueprint_config.py`, `__init__.py` | C: imports stable | ~4K 🟢 |
| Wave 4 | Verification + ADG regen | ADG, tests, pre-commit | D: green CI | ~3K 🟢 |

**Total: ~21K tokens across 4 waves, all GREEN**

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| 1.1 | Delete `build_sovereign_territories()` + all private helpers | `_constants.py` (delete lines 515–1746) | PP-1: 1,400 lines of dead code | ~4K | 🔲 TODO |
| 1.2 | Delete lifecycle trace emit block | `_constants.py` (delete lines 1782–1907) | PP-2: 126 lines of import-time side effects in a constants file | ~2K | 🔲 TODO |
| 1.3 | Update 2 test files consuming `build_sovereign_territories` | `test_leaf_domain_contract.py` (×2) | PP-3: tests call deprecated function | ~2K | 🔲 TODO |
| 2.1 | Remove all `*_subfolders` keys from `LAYER_OVERRIDES` | `_constants.py` L0–L6 overrides | PP-4: subfolder trees duplicated in territories.yaml | ~3K | 🔲 TODO |
| 2.2 | Remove LCD subfolder builder `_build_lcd_subfolders_template` + `_build_layer_definition` | `_constants.py` (delete lines 80–581) | PP-5: builder pipeline for dead dict | ~3K | 🔲 TODO |
| 3.1 | Clean `structure_blueprint_config.py` shim | `structure_blueprint_config.py` | PP-6: references deleted symbols | ~2K | 🔲 TODO |
| 3.2 | Clean `__init__.py` re-exports | `structure_blueprint/__init__.py` | PP-7: re-exports of removed symbols | ~2K | 🔲 TODO |
| 4.1 | Run tests, pre-commit, regen ADG | Full verification | PP-8: ensure zero regression | ~3K | 🔲 TODO |

---

## Gap Register

**GAP-1: Routing rules not in territories.yaml**
- `routing_rules` and `*_suffixes` patterns per layer exist only in `_constants.py`
- These are NOT duplicated — they are unique enforcement data
- **Decision**: Keep in `_constants.py` as the slimmed LAYER_OVERRIDES (routing-only)
- **Future**: Consider `config/structure_blueprint/routing_rules.yaml` if maintenance burden grows

**GAP-2: AST signals defined inline in `build_sovereign_territories()`**
- Lines 874–953 define AST signal patterns per directory
- These are unique data not duplicated elsewhere
- **Decision**: Move to `config/structure_blueprint/ast_signals.yaml` (file already exists)
- Verify current `ast_signals.yaml` content and merge if needed

**GAP-3: Lifecycle trace emit block in constants file**
- Lines 1782–1907: 126 lines of `_emit_*` calls at import time
- These execute as side effects when importing a "constants" module
- **Decision**: Remove — a constants leaf node should have zero side effects

---

## Execution Plan

### Phase 1.1 — Delete `build_sovereign_territories()` + helpers

**Scope**: Remove the 1,400-line deprecated function, all private builders (`_build_layer_definition`, `_deep_freeze`), and the commented-out SOVEREIGN_TERRITORIES materialization.

**What survives**: Lines 1–111 (module docstring, imports, TypedDicts, LCD template) and lines 112–512 (LAYER_OVERRIDES) and lines 1929–1977 (governance configs).

**Acceptance**: `_constants.py` < 600 lines. No import errors in package.

### Phase 1.2 — Delete lifecycle trace emit block

**Scope**: Remove lines 1782–1907 (import-time `_emit_*` calls and their massive import block).

**Acceptance**: `_constants.py` has zero side effects at import time.

### Phase 1.3 — Update test consumers

**Scope**: Update `test_leaf_domain_contract.py` (2 copies) to use `get_all_territories()` from `territories.py` instead of `build_sovereign_territories()`.

**Acceptance**: Both tests pass.

### Phase 2.1 — Slim LAYER_OVERRIDES to routing-only

**Scope**: Remove all `extra_subfolders`, `reasoning_subfolders`, `enforcement_subfolders`, `utils_subfolders`, `validators_subfolders`, `config_subfolders` from every layer entry. Keep: `purpose`, `notes`, `routing_rules`, `*_suffixes`, `forbidden_capabilities`.

**Acceptance**: LAYER_OVERRIDES is ~200 lines, contains only routing/suffix/purpose data.

### Phase 2.2 — Remove builder pipeline

**Scope**: Delete `_build_lcd_subfolders_template()` and `_build_layer_definition()` — no longer needed once subfolder trees are removed.

**Acceptance**: `_constants.py` < 400 lines total.

### Phase 3.1 — Clean shim

**Scope**: Remove references to deleted symbols from `structure_blueprint_config.py`.

**Acceptance**: Shim imports cleanly, no warnings.

### Phase 3.2 — Clean package `__init__.py`

**Scope**: Remove re-exports of deleted symbols from `structure_blueprint/__init__.py`.

**Acceptance**: `from agentic_core.L5_safety.config.structure_blueprint import *` works.

### Phase 4.1 — Full verification

**Scope**: Run tests, pre-commit gates, regenerate ADG.

**Acceptance**: All tests pass, ADG regenerates cleanly, pre-commit green.

---

## Target Architecture (Post-Cleanup)

```
config/structure_blueprint/
  territories.yaml        ← SSOT: what directories exist, their purposes
  ast_signals.yaml        ← SSOT: AST classification patterns (already exists)
  layers.yaml             ← SSOT: layer ordering and relationships (already exists)

agentic_core/L5_safety/config/
  structure_blueprint/
    _constants.py          ← ~300 lines: TypedDicts, routing_rules, suffix patterns, governance configs
    __init__.py            ← Package API (slimmed)
    territories.py         ← Python API for territories.yaml
    territories_loader.py  ← YAML loader
    yaml_loader.py         ← YAML loader for layer overrides
    ssot.py                ← SSOT query functions
    derived.py             ← Derived registries
    governance.py           ← Governance config consumers
    ...
  structure_blueprint_config.py  ← Backward-compat shim (slimmed)
```

**Separation of concerns:**
- **What directories exist** → `territories.yaml` (SSOT, AI-readable, conventional)
- **What files go where** → `_constants.py` routing_rules + suffix patterns (enforcement)
- **Runtime governance** → `_constants.py` HEALING/GRAVITY/MCP/MISSION configs
- **Structural truth** → ADG (69K nodes, 534K edges — the real enforcement engine)

---

## Rules

- No editing without reading the file first
- ADG fan-in/fan-out for all dependency analysis (NEVER grep for deps)
- Commit after each wave with descriptive message
- Zero test deletion — update tests to use new API, not skip
- Preserve all backward-compat imports through the shim

---

## Success Criteria

- [ ] `_constants.py` reduced from 1,978 → < 400 lines
- [ ] `build_sovereign_territories()` and all 1,400 lines of territory builders deleted
- [ ] Import-time side effects removed from constants module
- [ ] 2 test files updated to use `get_all_territories()`
- [ ] LAYER_OVERRIDES contains only routing rules, suffixes, purposes (no subfolder trees)
- [ ] All tests pass
- [ ] Pre-commit gates green
- [ ] ADG regenerates cleanly
- [ ] Zero import breakage via shim backward compatibility

---

## Rollback Strategy

1. `git stash` before each wave
2. If wave fails: `git stash pop` to restore
3. If post-commit regression: `git revert HEAD` per wave commit
4. ADG snapshot preserved at `artifacts/adg/adg_indexed_04102026_1052.sqlite`

---

## Acceptance Criteria

| Metric | Target | Verification |
|--------|--------|-------------|
| `_constants.py` line count | < 400 | `wc -l` |
| Dead code removed | ~1,600 lines | Diff stat |
| Test pass rate | 100% | `python -m pytest tests/ -x` |
| Import stability | 0 breakage | `python -c "from agentic_core.L5_safety.config.structure_blueprint_config import *"` |
| ADG health | green | `mcp1_adg_health` |
