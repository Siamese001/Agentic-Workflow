---
name: layer-boundary-guard
description: Prevents layer gravity violations before any import is added or file created in agentic_core. Use before adding any import statement crossing layer boundaries, before creating files in any L0-L6 layer directory, or when reviewing diffs for layer inversion. Enforces gravity rules where LN can only import from L0..LN.
enforcement_layer: pre-commit
enforcement_timing: after_work
enforcement_type: structural
---

# Layer Boundary Guard Skill

Enforces constitutional layer gravity rules before any import or file creation introduces a boundary violation.

## Files

- **`gravity_rules.md`** — Canonical layer hierarchy and gravity rule table. Defines which layers may import from which. MANDATORY reference before adding any cross-layer import.

- **`pre_import_checklist.md`** — Step-by-step checklist to run before adding any import statement. Identifies source layer, target layer, validates gravity compliance, and blocks violation before it enters the codebase.

## When to use

- Before adding ANY `import` or `from ... import` statement in `agentic_core/L*_*/`
- Before creating a new file in any layer directory
- When reviewing a diff that touches imports across layer directories
- When a module needs to call something in a higher-numbered layer (automatic STOP)

## Gravity Rules Summary

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

## Constitutional Requirements Enforced

- **§3.4:** AST dependency graphs PRIMARY for boundary validation
- **§4.3:** Boundary enforcement MUST use AST dependency graph
- **§4.4:** Before any code edit, MUST determine graph-backed impact analysis
