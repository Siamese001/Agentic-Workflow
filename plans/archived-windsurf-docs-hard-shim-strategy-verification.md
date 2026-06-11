---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\hard-shim-strategy-verification.md'
original_relative_path: 'hard-shim-strategy-verification.md'
source_sha256: 6d32181e33414dd2763d932782f36b51f458e5410ca196944edc9bb8654d40bd
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-08'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Hard Shim Strategy — Verification Report

**Date:** 2026-02-08
**Branch:** `v5.1-agentic-core-heal-complete`
**Scope:** `agentic_core/L5_safety/config/structure_blueprint/` package + `structure_blueprint_config.py` shim

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


## 1. Import Cycle Detection

**Method:** AST-based static analysis of all `.py` files in the package. Edges extracted from `ast.ImportFrom` nodes where `node.module` starts with the package prefix. DFS coloring algorithm (white/gray/black) detects back-edges.

**Dependency Graph:**

```text
__init__       -> ssot, territories
_constants     -> (none)                    ← LEAF NODE
artifacts      -> (none)
classification -> (none)
derived        -> _constants
governance     -> (none)
semantics      -> (none)
ssot           -> _constants, derived
territories    -> _constants
```

**Result:** PASS — zero import cycles detected.

**Note:** The `ssot -> __init__ -> ssot` cycle that existed prior to this fix (caused by `from package import derived` inside `lru_cache` functions) was eliminated by changing to `from package.derived import X` (direct module import, bypasses `__init__`).

---

## 2. API Surface

| Metric | Value |
|---|---|
| Package `__all__` | **163 names** |
| Shim `__all__` | **163 names** |
| Symmetric diff | **0** (exact match) |
| All `__all__` names resolve from package | Yes |
| All `__all__` names resolve from shim | Yes |

**Result:** PASS — exact match, all names resolve.

---

## 3. Deep Immutability + Identity (Phase 3)

| Object | Type | Len | Immutable | Identity |
| --- | --- | --- | --- | --- |
| `ROOT_WHITELIST` | `frozenset` | 13 | Yes (frozenset) | `_constants is ssot`: True |
| `SOVEREIGN_TERRITORIES` | `MappingProxyType` | 13 | Yes (deep) | `_constants is territories`: True, `_constants is ssot`: True |

**Deep Immutability Guarantees (Phase 3):**

- `ROOT_WHITELIST` is `frozenset` — no mutation possible.
- `SOVEREIGN_TERRITORIES` is `MappingProxyType` — top-level mutation blocked (`TypeError` on `__setitem__`).
- All nested dicts are recursively wrapped in `MappingProxyType`.
- All nested lists are converted to `tuple`.
- All nested sets are converted to `frozenset`.
- Implemented via `_deep_freeze()` in `_constants.py`, applied once at materialization time.
- Recursive depth check in verifier walks entire tree — any mutable container at any depth = FAIL.
- Identity preserved: same object in `_constants`, `ssot`, `territories`, and shim.

**Result:** PASS — deep immutable, identity preserved.

---

## 4. Backward Compatibility (18 excluded names)

These names were removed from `__all__` (not part of the 163-name public API) but remain importable via explicit import from both the package and the shim:

| Name | Category | Importable from package | Importable from shim |
|---|---|---|---|
| `SubfolderDefinition` | TypedDict | Yes (via `__getattr__` → territories) | Yes (explicit re-export) |
| `TerritoryDefinition` | TypedDict | Yes | Yes |
| `build_sovereign_territories` | Builder | Yes | Yes |
| `LAYER_OVERRIDES` | Static data | Yes | Yes |
| `get_sovereign_territories` | Lazy getter | Yes (eager in ssot) | Yes |
| `get_core_subfolder_map` | Lazy getter | Yes | Yes |
| `get_subfolder_metadata` | Lazy getter | Yes | Yes |
| `get_apps_lic_subfolder_map` | Lazy getter | Yes | Yes |
| `get_apps_rg_subfolder_map` | Lazy getter | Yes | Yes |
| `get_apps_shared_subfolder_map` | Lazy getter | Yes | Yes |
| `agentic_core_registry` | Derived | Yes (via `__getattr__` → derived) | Yes |
| `verify_derived_registries` | Derived | Yes | Yes |
| `L4_SUBFOLDER_MAP` | Derived | Yes | Yes |
| `L4_APPROVED_FOLDERS` | Derived | Yes | Yes |
| `SCRIPTS_PLACEMENT_RULES` | Derived | Yes | Yes |
| `get_app_specific_patterns_compiled` | Compiled regex | Yes (via `__getattr__` → artifacts) | Yes |
| `get_classification_suffix_patterns_compiled` | Compiled regex | Yes (via `__getattr__` → classification) | Yes |
| `get_compound_suffix_patterns_compiled` | Compiled regex | Yes | Yes |

**Leaked into `__all__`:** 0 (correct — these are not in the public API)

**Result:** PASS — 18/18 importable from both entry points, 0 leaked into `__all__`.

---

## 5. Import Linter + Phantom Baseline Lock (Phase 3)

**Method:** AST-based scan of all 246 `.py` files. Errors bucketed into:

- **Phantom names** — references to names that never existed (baseline noise)
- **Policy violations** — short-path imports bypassing the two-tier contract

| Metric | Phase 2 | Phase 3 |
| --- | --- | --- |
| Files checked | 246 | 246 |
| Total errors | 31 | 29 |
| Phantom names | 31 | 29 |
| Policy violations | 0 | 0 |

**Phase 3: Phantom Baseline Lock**

The 29 phantom names are now serialized to `docs/reports/plans/phantom_baseline.json` as a machine-enforced baseline. The verifier compares the current phantom set against the saved baseline:

- **If identical** → PASS (LOCKED)
- **If reduced** → PASS but prints improvement, requires `--update-baseline` flag to persist
- **If new phantoms appear** → FAIL (no silent regressions)

Baseline is never auto-updated. Explicit `--update-baseline` flag required.

**Result:** PASS — 0 policy violations, phantom baseline LOCKED (29 entries).

---

## 6. Shim Structural Hard Lock (Phase 3)

**Method:** AST inspection of `structure_blueprint_config.py`. Enforces:

- **Allowed:** `Import`/`ImportFrom`, exactly one `Assign` to `__all__`, module docstring `Expr`
- **Forbidden:** `FunctionDef`, `AsyncFunctionDef`, `ClassDef`, top-level `Call` expressions, control flow (`If`, `For`, `While`, `Try`, `With`), `Dict`/`List` literal assignments, any assignment except `__all__`

Phase 3 strengthening over Phase 2:

- Counts `__all__` assignments (must be exactly 1)
- Explicitly forbids control flow nodes
- Explicitly forbids top-level `Call` expressions
- Any non-whitelisted AST node type = FAIL

**Result:** PASS — `__all__` assignments: 1, FunctionDef/ClassDef/Call/ControlFlow: 0.

---

## 7. `_constants.py` Stdlib Allowlist (Phase 3)

**Method:** AST inspection of `_constants.py` against a strict import allowlist.

**Allowlist:**

```python
ALLOWED_MODULES = {
    "__future__", "typing", "types", "collections",
    "functools", "itertools", "dataclasses",
}
```

**Rules:**

- Any `Import`/`ImportFrom` with a top-level module not in allowlist = FAIL
- No relative imports allowed
- No dynamic imports (`__import__`, `importlib.import_module`) = FAIL
- Forbidden calls: `os.getenv`, `os.environ`, `os.getcwd`, `open`, `Path.read_text`, `Path.cwd`, `time.time`, `datetime.now`, `random.*`

Phase 3 strengthening over Phase 2: replaces ad-hoc forbidden-module list with a strict positive allowlist. Only the 7 modules above are permitted.

**Result:** PASS — no forbidden imports, no relative imports, no dynamic imports.

---

## 8. Compat Name Consumer Report

**Posture: INTERNAL FOREVER (not deprecated)**

These 18 names are part of the build/derivation machinery. They are importable via explicit import but excluded from `__all__` to prevent downstream coupling to internal structure.

| Name | Consumers | Status |
| --- | --- | --- |
| `SubfolderDefinition` | 0 | UNUSED |
| `TerritoryDefinition` | 0 | UNUSED |
| `build_sovereign_territories` | 0 | UNUSED |
| `LAYER_OVERRIDES` | 0 | UNUSED |
| `get_sovereign_territories` | 0 | UNUSED |
| `get_core_subfolder_map` | 0 | UNUSED |
| `get_subfolder_metadata` | 0 | UNUSED |
| `get_apps_lic_subfolder_map` | 0 | UNUSED |
| `get_apps_rg_subfolder_map` | 0 | UNUSED |
| `get_apps_shared_subfolder_map` | 0 | UNUSED |
| `agentic_core_registry` | 0 | UNUSED |
| `get_app_specific_patterns_compiled` | 0 | UNUSED |
| `get_classification_suffix_patterns_compiled` | 0 | UNUSED |
| `get_compound_suffix_patterns_compiled` | 0 | UNUSED |
| `verify_derived_registries` | 2 | ACTIVE |
| `L4_SUBFOLDER_MAP` | 1 | ACTIVE |
| `L4_APPROVED_FOLDERS` | 5 | ACTIVE |
| `SCRIPTS_PLACEMENT_RULES` | 1 | ACTIVE |

**Summary:** 14 of 18 compat names have zero external consumers. The 4 active names (`verify_derived_registries`, `L4_SUBFOLDER_MAP`, `L4_APPROVED_FOLDERS`, `SCRIPTS_PLACEMENT_RULES`) have legitimate consumers in validators, tests, and enforcement modules. No deprecation planned — these are stable internal API.

---

## Import-Path Policy

| Entry Point | Audience | Surface |
| --- | --- | --- |
| `from agentic_core.L5_safety.config.structure_blueprint import X` | Package internals, new code | `__all__` (163 names) via `import *`; all 181 names via explicit import |
| `from agentic_core.L5_safety.config.structure_blueprint_config import X` | External consumers (backward compat) | `__all__` (163 names) via `import *`; 181 names via explicit import |

The shim is a **backward-compatible re-export façade**:

- `__all__` mirrors the package exactly (163 names, auto-synced via `_pkg_all`)
- 18 additional internal names are explicitly re-exported for backward compatibility
- The shim contains NO data definitions and NO domain logic (verified by AST invariant check)
- The only structural "logic" is: `from package import *`, explicit re-imports, and `__all__ = list(_pkg_all)`

**Forbidden:** Short-path imports (`from structure_blueprint import ...`) are a policy violation. The verifier flags them as FAIL.

---

## Verification Script

Runnable verification (8-section test suite):

```bash
python -m agentic_core.L5_safety.config.structure_blueprint._verify
```

---

## Files Modified

| File | Change |
| --- | --- |
| `_constants.py` | Leaf-node module. `ROOT_WHITELIST` is `frozenset`. `SOVEREIGN_TERRITORIES` deep-frozen via `_deep_freeze()` → `MappingProxyType`. Imports restricted to stdlib allowlist. |
| `territories.py` | Thin re-export shim from `_constants.py` |
| `ssot.py` | Module-level imports from `_constants`+`derived`. Inline imports eliminated. |
| `derived.py` | Module-level import from `_constants`. Inline imports eliminated. |
| `__init__.py` | `ROOT_WHITELIST` eagerly imported. `__all__` curated to 163. |
| `structure_blueprint_config.py` | Backward-compat re-export shim. Structural hard lock enforced (no logic, no data, no control flow). |
| `_verify.py` | Phase 3 hardened: 8-section verifier with deep immutability test, stdlib allowlist, phantom baseline lock, shim structural hard lock. |
| `routing_decision.py` | Removed `sys.path.append` hacks, fully-qualified imports. |
| `phantom_baseline.json` | NEW: Machine-enforced phantom import baseline (29 entries). |

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

