# RCA: Structure Blueprint SSOT Consolidation

**Date**: 2026-02-08
**Severity**: Architectural (SSOT Violation)
**Status**: RESOLVED

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Problem Statement

The structure blueprint configuration existed in **three redundant locations**:

| File | Lines | Importers | Status |
|------|-------|-----------|--------|
| `structure_blueprint_config.py` (monolith) | 5,910 | 197 files (297 imports) | Active SSOT — everything imported from here |
| `structure_blueprint/` (modular package) | ~3,500 across 7 files | 3 files (internal only) | Partial refactor — barely adopted |
| `structure_blueprint_config_new.py` (shim) | 635 | **0 files** | Dead code — abandoned migration shim |

This violated the SSOT principle: edits had to be made in both the monolith AND the modular package, and they had already drifted (e.g., `FLAT_DIRECTORIES` added to monolith but missing from modular package).

## Root Cause

A modular refactor was attempted but never completed. The monolith was kept as the active source because 197 files depended on it. The backward-compatible shim (`_config_new.py`) was created but never wired in. Result: three copies of the same data, diverging over time.

## Resolution

### Phase 1: Delete Dead Code
- Deleted `structure_blueprint_config_new.py` (0 importers — confirmed dead)

### Phase 2: Backfill Modular Package (51 missing names)
- Created `governance.py` — 8 operational config names (HEALING_CONFIG, MISSION_CONFIG, GRAVITY_CONFIG, etc.)
- Appended 29 names to `ssot.py` — whitelists, validation functions, flat enforcement
- Appended 7 names to `artifacts.py` — ARTIFACT_ROUTING_MAP, validation utilities, subfolder metadata
- Appended 10 names to `semantics.py` — AGENT_REGISTRY, semantic_l2_registry, AST_PLACEMENT_SIGNALS, etc.
- Fixed cross-module references (SOVEREIGN_TERRITORIES lazy imports in ssot.py functions)

### Phase 3: Convert Monolith to Shim
- Replaced 5,910-line monolith with 399-line shim that re-exports all 181 names from modular package
- All 197 importers continue to work unchanged via the shim

### Phase 4: Update Package Init
- Regenerated `__init__.py` to export all 181 public names
- HOT imports (ssot, territories) loaded eagerly; COLD imports (classification, semantics, artifacts, derived, governance) lazy-loaded via `__getattr__`

## Verification

- **Import verification**: 272 import statements across 197 files checked — 0 new breakage introduced
- **Pre-existing phantom imports**: 7 names (`CANON_SIGNALS`, `SOVEREIGN_REGISTRY`, `SCRIPTS_DIR`, etc.) were never in the monolith — 31 pre-existing broken imports unrelated to this change
- **Unit tests**: 12/12 flat directory enforcement tests pass
- **Smoke test**: 47 critical names verified importable via shim

## Architecture (After)

```
structure_blueprint/           <-- SSOT (modular package)
  __init__.py                  <-- Re-exports all 181 names (hot + lazy)
  ssot.py                      <-- Core constants, whitelists, validation (79 names)
  territories.py               <-- SOVEREIGN_TERRITORIES (5 names)
  classification.py            <-- Suffix/naming patterns (20 names)
  semantics.py                 <-- AST signals, registries (30 names)
  artifacts.py                 <-- Routing maps, file patterns (27 names)
  derived.py                   <-- Computed registries (12 names)
  governance.py                <-- Operational config (8 names)

structure_blueprint_config.py  <-- SHIM (399 lines, re-exports from package)
```

## Rules Established

1. **New definitions** go in the modular package, not the shim
2. **The shim must never define its own data** — it only re-exports
3. **`structure_blueprint_config_new.py` is permanently deleted** — do not recreate

## Violation

[Describe the violation or issue that triggered this RCA]

---

## Corrective Actions

[List the corrective actions taken to resolve the issue]

---

