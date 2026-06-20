# Import Validation Checklist

Run before adding any `import` or `from ... import` statement.

## Five-Point Checklist

1. **Usage** — symbol is actually used in the file body (no dead imports)
2. **Duplication** — not already imported in the same file scope
3. **Canonical path** — import path is the canonical location, not a shim
4. **Forbidden patterns** — not on the forbidden imports registry (see `forbidden_imports_registry.md`)
5. **Layer gravity** — source layer N does not import from layer M where M > N

## Hard Failures (STOP immediately)

- Importing a symbol and never using it
- Importing the same symbol twice in one file
- Importing from a forbidden module path
- Runtime imports (`import X` inside a function) for structural/config logic
- Importing from a shim when the canonical path exists

## Verification Commands

```bash
# Dead imports
python -m ruff check --select F401 <changed_files>

# Forbidden imports / ordering
python -m ruff check --select E402,I <changed_files>

# Layer gravity
python ops_scripts/ci/validate_import_dependencies.py
```
