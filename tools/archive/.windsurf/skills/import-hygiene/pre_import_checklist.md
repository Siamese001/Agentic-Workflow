# Pre-Import Checklist

Run BEFORE adding any import statement to any Python file.
ALL five points must be satisfied before the import is added.

---

## Point 1 — Symbol Is Actually Used

Confirm the imported symbol appears in the file body at least once (not just imported):

```python
# Quick check: does <SymbolName> appear in the file outside the import line?
python -c "
import pathlib, re
text = pathlib.Path('<file_path>').read_text(encoding='utf-8', errors='replace')
lines = text.splitlines()
uses = [
    (i+1, l.strip()) for i, l in enumerate(lines)
    if '<SymbolName>' in l and not l.strip().startswith(('import ', 'from '))
]
print(f'Uses of <SymbolName>: {len(uses)}')
for lineno, line in uses:
    print(f'  {lineno}: {line}')
"
```

If zero uses found → **do NOT add this import** (dead import).

---

## Point 2 — Not Already Imported in This File

Confirm the symbol is not already imported under the same or an aliased name:

```python
python -c "
import ast, pathlib
tree = ast.parse(pathlib.Path('<file_path>').read_text(encoding='utf-8', errors='replace'))
for node in ast.walk(tree):
    if isinstance(node, ast.ImportFrom):
        for alias in node.names:
            name = alias.asname or alias.name
            if '<SymbolName>' in name:
                print(f'Already imported at line {node.lineno}: {ast.unparse(node)}')
"
```

If already imported → **do NOT add duplicate**.

---

## Point 3 — Import Path Is Canonical

Prefer the canonical path over shim paths:

```
Proposed import: from <module_path> import <Symbol>

Is this a shim path (ends in _util, _shim, _compat, _legacy)?
  YES → Check if canonical path exists. If so, use canonical instead.
  NO  → Proceed.

Is this the most direct path to the symbol?
  If symbol is re-exported through multiple layers → use the most direct one.
```

---

## Point 4 — Not a Forbidden Import

Check against `forbidden_imports_registry.md`:

| Forbidden Pattern | Use Instead |
|---|---|
| `from agentic_core.base_agents.timeout_decorator import timeout` | `from agentic_core.L0_routing.utils.timeout_decorator import timeout` |
| `from agentic_core.L5_safety.config.structure_blueprint.ssot import *` | Use specific constants from `structure_blueprint_config.py` |
| Any `import *` (wildcard) in production code | Explicit named imports only |
| Runtime `import X` inside function body for structural/config logic | Module-level import |

---

## Point 5 — Layer Gravity Not Violated

For files in `agentic_core/L*_*/`: run the `layer-boundary-guard` skill `pre_import_checklist.md`.

Quick check:
```
Source file layer: L<N>
Import target layer: L<M>
Rule: M must be <= N
```

If M > N → **GRAVITY VIOLATION** — do not add this import.

---

## Verification Command (run before commit)

```python
import subprocess, sys

files = sys.argv[1:]  # pass changed .py files as arguments

# F401: unused imports
result = subprocess.run(
    ["python", "-m", "ruff", "check", "--select", "F401,E401,I001"] + files,
    capture_output=True, text=True
)
if result.returncode != 0:
    print("IMPORT HYGIENE VIOLATIONS:")
    print(result.stdout)
    sys.exit(1)
print("Import hygiene: PASS")
```
