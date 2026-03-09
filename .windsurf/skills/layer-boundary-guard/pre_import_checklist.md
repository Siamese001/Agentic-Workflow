# Pre-Import Checklist

Run BEFORE adding any import statement to a file in `agentic_core/L*_*/` or `apps_*/`.

## Step 1 — Identify Source Layer

Determine the layer of the FILE receiving the import:

```
File path: agentic_core/L?_*/...
Extract layer number N from path segment "L?_"
Source layer rank = N
```

If file is in `apps_rg/`, `apps_lic/`, or `apps_shared/` → apply apps_* rules from `gravity_rules.md`.

## Step 2 — Identify Target Layer

Determine the layer of the MODULE being imported:

```
Import: from agentic_core.L?_* import ...
Extract layer number M from module path segment "L?_"
Target layer rank = M
```

If target is NOT in `agentic_core` (e.g., stdlib, third-party, `apps_shared`) → skip gravity check, proceed to Step 4.

## Step 3 — Gravity Check

```
IF target_rank (M) > source_rank (N):
    → GRAVITY VIOLATION
    → STOP — do NOT add this import
    → Document violation in evidence
    → Propose alternative: restructure to push logic DOWN to LN or lower
ELSE:
    → Gravity OK, proceed
```

## Step 4 — Forbidden Module Check

Check against `forbidden_imports_registry.md` (import-hygiene skill):
- Is the import path on the forbidden list? → BLOCK
- Is this importing from a shim when canonical path is available? → Use canonical

## Step 5 — Usage Check

Confirm the imported symbol is USED in the file body:
- Search the file for references to the imported name
- If zero uses found → dead import → do NOT add

## Step 6 — Document in Evidence

Record in phase evidence:
```
IMPORT ADDED:
  File: <source_file>  (Layer L<N>)
  Import: from <module> import <symbol>  (Layer L<M>)
  Gravity check: M=<M> <= N=<N> → PASS
  Usage count: <N> references in file
  Forbidden check: PASS
```

## STOP Conditions

| Condition | Action |
|-----------|--------|
| M > N (gravity violation) | STOP — restructure, do not add import |
| Symbol on forbidden list | STOP — use approved alternative |
| Symbol never used | STOP — do not add dead import |
| Shim available but canonical preferred | Use canonical path |
