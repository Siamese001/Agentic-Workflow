# Pre-Creation Checklist

Run BEFORE creating any new agent, mixin, utility function, or constant.
All four searches MUST return zero matches before creation proceeds.

---

## Step 1 — AST Symbol Search

Search the entire codebase for classes/functions with equivalent signatures:

```python
python -c "
import ast, pathlib

TARGET_STEM = '<new_symbol_name_stem>'  # e.g. 'complexity_analyzer', 'layer_gravity'

for f in pathlib.Path('.').rglob('*.py'):
    if '__pycache__' in str(f): continue
    try:
        tree = ast.parse(f.read_text(encoding='utf-8', errors='replace'))
        for node in ast.walk(tree):
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                if TARGET_STEM.lower() in node.name.lower():
                    print(f'{f}:{node.lineno} {type(node).__name__} {node.name}')
    except: pass
"
```

Record ALL matches. If ANY match found → go to `dedup_decision_tree.md` branch 1 or 2.

---

## Step 2 — Name Pattern Search

Find all symbols with overlapping name stems using ruff/grep as secondary:

```python
python -c "
import pathlib, re

PATTERN = re.compile(r'(class|def)\s+\w*TARGET_STEM\w*', re.IGNORECASE)
PATTERN_STR = PATTERN.pattern.replace('TARGET_STEM', '<stem>')

for f in pathlib.Path('.').rglob('*.py'):
    if '__pycache__' in str(f): continue
    try:
        text = f.read_text(encoding='utf-8', errors='replace')
        for i, line in enumerate(text.splitlines(), 1):
            if re.search(PATTERN_STR, line):
                print(f'{f}:{i} {line.strip()}')
    except: pass
"
```

---

## Step 3 — Behavioral / Data Search

Find all symbols that read/write the same data or call the same APIs:

For **constants**: Search for the constant value (not just name):
```python
python -c "
import pathlib
VALUE = '<constant_value>'
for f in pathlib.Path('.').rglob('*.py'):
    if '__pycache__' in str(f): continue
    try:
        if VALUE in f.read_text(encoding='utf-8', errors='replace'):
            print(f)
    except: pass
"
```

For **agents/mixins**: Search for the same base class or mixin combination.

---

## Step 4 — Registry Check

For agents: Verify symbol is NOT already in agent registry:
```
artifacts/consolidation/active_set_snapshot.json
artifacts/discovery/agent_discovery_full.json
```

For constants: Verify NOT already in:
```
agentic_core/L0_routing/config/path_constants.py
agentic_core/L5_safety/config/structure_blueprint_config.py
```

---

## Step 5 — Decision

| Search Result | Action |
|---|---|
| Exact match found (same name + behavior) | Branch 1: Reuse existing |
| Near-match found (similar behavior, different name) | Branch 2: Extend existing |
| No matches in all 4 searches | Branch 3: Create new with justification |

---

## Step 6 — Justification (Required for Branch 3)

Document in evidence before creating:

```
DEDUP SEARCH COMPLETED:
  New symbol: <SymbolName>
  AST search: 0 matches
  Name pattern search: 0 matches
  Behavioral search: 0 matches
  Registry check: not present
  Justification for creation: <why this cannot reuse/extend existing>
  Creation approved: YES
```
