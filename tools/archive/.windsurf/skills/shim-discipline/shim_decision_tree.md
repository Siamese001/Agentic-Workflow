# Shim Decision Tree

When a canonical module is moved, renamed, or consolidated, follow this decision tree.
STOP at the first matching branch.

---

## Decision Flow

```
Canonical module location is changing?
│
├─► 1. Are there known consumers of the OLD import path?
│       YES → Create a shim at the old path.
│             Follow shim_contract_template.md EXACTLY.
│             Write a test asserting re-export works.
│             DONE.
│
├─► 2. A shim already exists at the old path?
│       YES → Update the shim's internal import to point to the new canonical.
│             Update the DEPRECATED docstring with the new canonical path.
│             Re-run the existing shim test.
│             DONE.
│
├─► 3. Only the docstring / file-level comment changed (no path change)?
│       YES → Update the shim's DEPRECATED docstring only.
│             No new shim needed.
│             DONE.
│
└─► 4. No known consumers AND no existing shim?
        → Skip shim creation.
          MANDATORY: Document justification in evidence:
            "No shim created: zero consumers confirmed via AST search on <date>"
          DONE.
```

---

## Hard Rules

- Branches 1–3 are the ONLY valid paths when consumers exist.
- Branch 4 requires documented AST-backed proof of zero consumers.
- A canonical move WITHOUT a shim (when consumers exist) = CONSTITUTIONAL VIOLATION.
- Shims are NEVER the long-term solution — every shim needs an expiry annotation.

## Consumer Discovery (required for Branch 4)

Before skipping shim creation, run:

```python
# Find all imports of the old module path
python -m ruff check --select F401 .
# AND
python -c "
import ast, pathlib
old_path = 'agentic_core.old.module.path'
for f in pathlib.Path('.').rglob('*.py'):
    try:
        tree = ast.parse(f.read_text(encoding='utf-8', errors='replace'))
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                src = getattr(node, 'module', '') or ''
                if old_path in src:
                    print(f'{f}:{node.lineno}')
    except: pass
"
```

Zero results from both commands = Branch 4 justified.
