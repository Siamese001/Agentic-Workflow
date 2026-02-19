# Canonical Invocation Policy

## Rule

When executing any Python module or agent, use ONLY the canonical entrypoint.
Do NOT create new scripts to invoke existing scripts or modules.

## Allowed Invocation Patterns

```powershell
# Pattern 1: Direct file invocation
python path/to/existing_file.py [args]

# Pattern 2: Module invocation (-m)
python -m existing.module.path [args]
```

## Prohibited Patterns (BLOCKING VIOLATIONS)

- Creating any new `.py`, `.sh`, `.ps1`, or `.bat` file whose primary purpose
  is to invoke an existing script or module.
- Files named `run_*`, `*_runner`, `tmp_*`, `scratch_*`, `invoke_*`, `launch_*`.
- Any file that imports a canonical module and re-exposes its logic without
  adding new business logic.
- Wrapping a direct invocation in a new file to "make it easier to run."

## If No `__main__` Exists

If the target file has no `if __name__ == "__main__":` block and cannot be
invoked directly:

1. Add `main()` function + `if __name__ == "__main__": main()` to the SAME
   canonical file.
2. Do NOT create a new runner file.
3. The addition must be minimal — only wiring, no new business logic.

## Evidence Requirement

When any agent or module is invoked during a phase:
- Record the exact invocation command in the evidence file.
- Confirm no new runner files were created via `git diff --name-only HEAD`.
