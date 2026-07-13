---
name: boundary-enforcement
description: Use this skill when adding or changing imports, moving Python symbols between L0-L6 layers, introducing compatibility shims, or reviewing a refactor for layer-gravity and canonical-import violations.
metadata:
  owner: platform-team
  version: "2.0"
---

# Boundary enforcement

Use graph evidence and repository gates to preserve layer gravity, canonical imports, and temporary
compatibility shims. This skill supplies the review procedure; CI remains the enforcement authority.

## Workflow

1. Use `graph-analysis` to identify the importing module, imported symbol, fan-in, and fan-out.
2. Read [gravity_rules.md](gravity_rules.md) and classify source and target layers.
3. Run the five checks in
   [import_validation_checklist.md](import_validation_checklist.md): usage, duplication, canonical
   path, forbidden pattern, and layer gravity.
4. Consult [forbidden_imports_registry.md](forbidden_imports_registry.md) before adding a new
   cross-package or cross-layer dependency.
5. When relocating a public symbol, follow
   [shim_discipline_protocol.md](shim_discipline_protocol.md) and give the shim an owner and removal
   condition.
6. Run focused lint/tests, then the repository boundary gates. Review the diff for undeclared imports.

## Layer rule

A core layer may depend only on itself and lower-numbered layers. Application packages may depend on
`agentic_core` and approved shared application surfaces; core must not depend on an application.
When a lower layer needs higher-layer behavior, use dependency injection, a callback, or a lower-level
contract instead of reversing the dependency.

## Linting

```bash
python -m ruff check --select F401,I <changed-python-files>
```

`F401` checks unused imports and `I` checks import sorting. Ruff `E402` only detects module imports that
are not at the top of a file; it does **not** enforce the repository's forbidden-import registry or
layer gravity. Use the repository boundary gate for those policies.

## Shim rules

- Re-export from the canonical location; do not duplicate implementation.
- Emit a targeted `DeprecationWarning` when compatibility requires it.
- Document the canonical import and removal condition.
- Test both the canonical path and the compatibility path during the transition.
- Remove the shim when the declared condition is met; do not create permanent compatibility layers.

## Validation

```bash
python -m ruff check --select F401,I <changed-python-files>
python ops_scripts/ci/run_contract_gates.py
```

Read [boundary_violation_examples.md](boundary_violation_examples.md) only when classifying a
non-obvious violation.
