---
name: boundary-enforcement
description: Consolidated layer boundary and import hygiene enforcement. Replaces layer-boundary-guard, import-hygiene, and shim-discipline. Enforces layer gravity rules, import hygiene, and backward compatibility discipline.
metadata:
  enforcement_layer: pre-commit
  enforcement_timing: after_work
  enforcement_type: structural
---

# Boundary Enforcement Skill (Consolidated)

Consolidated skill that merges `layer-boundary-guard`, `import-hygiene`, and `shim-discipline` into unified boundary and import enforcement.

## Files

- **`gravity_rules.md`** — Canonical layer hierarchy and gravity rule table with violation examples
- **`import_validation_checklist.md`** — Five-point pre-import checklist covering usage, duplication, canonical paths, forbidden patterns, and layer compliance
- **`forbidden_imports_registry.md`** — Authoritative list of forbidden import patterns and their canonical alternatives
- **`shim_discipline_protocol.md`** — Backward compatibility requirements for symbol relocation and deprecation
- **`boundary_violation_examples.md`** — Common violation patterns and their correct alternatives

## When to use

- Before adding ANY `import` or `from ... import` statement in `agentic_core/L*_*/`
- Before creating a new file in any layer directory
- When reviewing a diff that touches imports across layer directories
- When a module needs to call something in a higher-numbered layer (automatic STOP)
- Before committing any file where imports were modified
- When relocating or renaming symbols between modules
- During any refactor that moves symbols between layers

## Layer Gravity Rules

```
L0 → can import: L0 only
L1 → can import: L0, L1
L2 → can import: L0, L1, L2
L3 → can import: L0, L1, L2, L3
L4 → can import: L0, L1, L2, L3, L4
L5 → can import: L0, L1, L2, L3, L4, L5
L6 → can import: L0, L1, L2, L3, L4, L5, L6
apps_* → can import: agentic_core (any layer), apps_shared
```

**VIOLATION:** Any import where source layer N imports from layer M where M > N.

## Import Hygiene Protocol

**Pre-Import Checklist (MANDATORY):**

1. **Usage Check**: Symbol is actually used in the file body
2. **Duplication Check**: Not already imported in scope
3. **Canonical Path Check**: Import path is canonical (not a shim unless intentional)
4. **Forbidden Pattern Check**: Not on the forbidden import list
5. **Layer Gravity Check**: Layer gravity not violated

**Forbidden Imports:**
- `structure_blueprint.ssot` (use constants instead)
- `base_agents.timeout_decorator` (use `L0_routing.utils.timeout_decorator`)
- Runtime imports (`import X` inside a function) for structural/config logic

**Hard Failures:**
- ❌ Importing a symbol and never using it
- ❌ Importing the same symbol twice in one file
- ❌ Importing from a forbidden module path
- ❌ Runtime imports for structural logic
- ❌ Importing from a shim when the canonical path is available

## Shim Discipline Protocol

**When relocating any Python module or changing canonical import paths:**

1. **Create Backward Compatibility**: Create `_shim.py` or `_compat.py` with redirection
2. **Document Deprecation**: Add deprecation warnings with 90-day minimum timeline
3. **Update References**: Coordinate changes across all dependent files
4. **Test Compatibility**: Verify both old and new import paths work during transition

**Shim Requirements:**
- Must import from canonical location and re-export
- Must include `DeprecationWarning` with timeline
- Must document canonical alternative in docstring
- Must be removed after deprecation period

**FORBIDDEN:**
- Moving or renaming symbols without shim discipline
- Creating undocumented shims
- Silent breaking changes
- Permanent shims (must have removal plan)

## Boundary Validation Process

**Before adding any import:**

1. **Identify Source Layer**: Determine which layer the importing file belongs to
2. **Identify Target Layer**: Determine which layer the imported module belongs to
3. **Check Gravity**: Verify source layer N can import from target layer M (M ≤ N)
4. **Validate Path**: Ensure import path is canonical and not a shim
5. **Check Usage**: Verify symbol will actually be used

**If gravity violation detected → STOP. Do not add import.**

## Pre-Commit Import Verification

Run before every commit touching Python files:

```python
# Verify no dead imports (F401)
python -m ruff check --select F401 <changed_files>

# Verify no forbidden imports
python -m ruff check --select E402 <changed_files>

# Verify import ordering
python -m ruff check --select I <changed_files>
```

If `ruff` unavailable, manually verify each added import against the checklist.

## Common Violation Patterns

### Layer Gravity Violations
```python
# ❌ FORBIDDEN: L3 importing from L5
from agentic_core.L5_safety.config import some_config

# ✅ CORRECT: Move import to lower layer or use dependency injection
from agentic_core.L3_orchestration.config import some_config  # If it exists here
```

### Dead Import Violations
```python
# ❌ FORBIDDEN: Import never used
import os  # Never used in file

# ✅ CORRECT: Remove unused import
```

### Shim Violations
```python
# ❌ FORBIDDEN: Import from old location without shim
from old_module import SomeClass

# ✅ CORRECT: Use canonical path
from new_location.canonical_module import SomeClass
# Or during transition: from old_module.shim import SomeClass
```

## Constitutional Requirements Enforced

- **§3.4:** AST dependency graphs PRIMARY for boundary validation
- **§4.3:** Boundary enforcement MUST use AST dependency graph
- **§4.4:** Before any code edit, MUST determine graph-backed impact analysis
- **§8.2:** Layer inversion detection MUST be AST-based
- **§8.3:** Tooling/runtime boundary enforcement

## Enforcement Scripts

| Requirement | Enforcement Script(s) |
|-------------|---------------------|
| Import hygiene | `python -m ruff check --select F401,E402,I` |
| Layer boundary | Custom boundary validation script |
| Shim discipline | Deprecation warning verification |

**Single entrypoint:** `python ops_scripts/ci/run_contract_gates.py`

## Evidence Requirements

When boundary violations are detected and must be documented:
```
## BOUNDARY_VIOLATION
**Import**: from L5_module import X
**Source Layer**: L3
**Target Layer**: L5
**Gravity Rule**: L3 cannot import from L5 (M > N)
**Resolution**: Move to L3 or use dependency injection
```

## Forbidden Patterns

- ❌ Importing from higher-numbered layers
- ❌ Importing unused symbols
- ❌ Importing from forbidden modules
- ❌ Runtime imports for structural logic
- ❌ Moving symbols without shim discipline
- ❌ Creating permanent shims without removal plan
- ❌ Importing duplicates in same file
- ❌ Using non-canonical import paths when canonical exists
