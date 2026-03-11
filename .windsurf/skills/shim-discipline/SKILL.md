---
name: shim-discipline
description: Enforces consistent shim and backward-compatibility stub discipline when moving or renaming canonical modules. Use when relocating any Python module, when creating files ending in _util.py/_shim.py/_compat.py, or when a canonical symbol's import path changes. Prevents undocumented shims and shimless moves that break consumers.
enforcement_layer: both
enforcement_timing: before_work
enforcement_type: behavioural_primary_structural_secondary
---

# Shim Discipline Skill

Enforces a consistent protocol for backward-compatibility shims whenever canonical module locations change.

## Files

- **`shim_decision_tree.md`** — Four-branch decision tree: (1) move canonical → create shim, (2) shim exists → update it, (3) rename only → update shim docstring, (4) no consumers → skip shim with documented justification.

- **`shim_contract_template.md`** — Template for a compliant shim file. Includes mandatory `# DEPRECATED` docstring, canonical import, re-export, and expiry annotation. Every shim MUST match this template.

## When to use

- Before moving or renaming any Python module in `agentic_core/` or `apps_*/`
- When creating any file ending in `_util.py`, `_shim.py`, `_compat.py`, or `_legacy.py`
- When an import path changes and downstream consumers exist
- When reviewing a diff that relocates files without adding a shim

## Shim Requirements (ALL mandatory)

1. **Deprecation docstring** — First line: `# DEPRECATED: Use <canonical.import.path> instead`
2. **Canonical import** — Import from the new canonical location only
3. **Re-export** — `__all__` must re-export the same public symbols
4. **Test** — A test file MUST assert the shim re-exports the canonical symbol
5. **Expiry** — Comment with planned removal milestone: `# SHIM EXPIRY: after all consumers migrated`

## Constitutional Requirements Enforced

- **§1.1:** Every changed surface (including shims) MUST have tests
- **§1.2:** Shim tests MUST exist before the canonical move is committed
- **§3.1:** Scope declaration MUST include both canonical file AND shim file
