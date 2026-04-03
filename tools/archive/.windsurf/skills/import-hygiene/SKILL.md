---
name: import-hygiene
description: Prevents dead imports, forbidden imports, and duplicate imports before they enter the codebase. Use before adding any import statement, during any refactor touching imports, and before committing any file with import changes. Enforces ruff F401 compliance and blocks forbidden import patterns defined in windsurfrules.
enforcement_layer: both
enforcement_timing: after_work
enforcement_type: structural
---

# Import Hygiene Skill

Enforces clean import discipline before any import change reaches a commit.

## Files

- **`pre_import_checklist.md`** — Five-point checklist before adding any import: (1) symbol is actually used, (2) not already imported in scope, (3) import path is canonical (not a shim unless intentional), (4) not a forbidden module, (5) layer gravity not violated.

- **`forbidden_imports_registry.md`** — Authoritative list of forbidden import patterns for this repository. Includes: `structure_blueprint.ssot` (use constants instead), `base_agents.timeout_decorator` (use `L0_routing.utils.timeout_decorator`), runtime imports inside function bodies for structural logic.

## When to use

- Before adding any `import` or `from ... import` to any file
- During any refactor that moves symbols between modules
- Before committing any file where imports were modified
- When `ruff` or `flake8` is not available and manual checking is required

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

If `ruff` unavailable, manually verify each added import is:
- Used at least once in the file body
- Not duplicated elsewhere in the same file
- Not on the forbidden list (`forbidden_imports_registry.md`)
- Not violating layer gravity (`layer-boundary-guard` skill)

## Hard Failures

- ❌ Importing a symbol and never using it
- ❌ Importing the same symbol twice in one file
- ❌ Importing from a forbidden module path
- ❌ Runtime imports (`import X` inside a function) for structural/config logic
- ❌ Importing from a shim when the canonical path is available

## Constitutional Requirements Enforced

- **§3.3:** Code analysis MUST use AST — dead import detection is AST-based
- **§3.5:** Grep FORBIDDEN as primary — use ruff/AST not grep to find imports
- **§1.1:** Every changed import surface MUST have a test verifying the symbol resolves
