---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\residual-gap-fix-wave-plan.md'
original_relative_path: 'residual-gap-fix-wave-plan.md'
source_sha256: 0c7bb8d32fc7001234d74fda650814475dcd9906f8dc3b1f5857143109708054
recovered_status: LOST_RECOVERED
last_commit: '6477883502e'
last_commit_date: '2026-04-27 08:55:24 -0400'
created_date: '2026-04-06'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Wave Plan: Residual Gap Fixes - AST-Based Import Parsing

## Overview

This plan addresses the remaining design gaps in the dead import removal tools that require AST-based parsing instead of naive string matching.

## Gaps Addressed

- **G7**: strip_dead_reexports.py - Naive string matching "from " and "import " could match comments or strings
- **G8**: strip_dead_reexports.py - Naive substring match could match partial symbol names (e.g., "MAX" matches "MAX_RETRIES")

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | W1-A | AST-based import detection in strip_dead_reexports.py | 5000 | Python AST module available | COMPLETED | Imports correctly identified even in comments/strings |
| W2 | W2-A | Exact symbol matching (word boundaries) in strip_dead_reexports.py | 3000 | No assumptions | SUPERSEDED | AST approach provides exact matching natively |

## Per-Wave Token Budgets

| Wave | Budget | Status |
|------|--------|--------|
| W1 | GREEN 🟢 5000 tokens | COMPLETED |
| W2 | GREEN 🟢 3000 tokens | SUPERSEDED (by W1-A) |

---

## WAVE 1 — AST-Based Import Detection

### W1-A — Replace naive string matching with AST parsing

**File**: `tools/fix/strip_dead_reexports.py`

**Current Issue**:
```python
# Line 47 - naive matching
if "from " in line and "import " in line:
```
This matches comments like `# from X import Y` and strings like `"from X import Y"`.

**Fix Strategy**:
1. Parse the file with `ast.parse()`
2. Traverse AST to find `ast.ImportFrom` nodes
3. Extract exact line numbers and symbol names
4. Only process actual import statements, not comments/strings

**Commands**:
```bash
# Test AST-based detection
python -c "
import ast
code = '''
# from fake import comment
from real import symbol
\"\"\"from fake import string\"\"\"
'''
tree = ast.parse(code)
for node in ast.walk(tree):
    if isinstance(node, ast.ImportFrom):
        print(f'Line {node.lineno}: from {node.module} import {[n.name for n in node.names]}')
"
```

**Acceptance**:
- AST correctly identifies only real import statements
- Comments and strings are ignored
- Line numbers match actual imports
- Tests pass with the new logic

---

## WAVE 2 — Exact Symbol Matching

### W2-A — Replace substring match with word boundary matching

**File**: `tools/fix/strip_dead_reexports.py`

**Current Issue**:
```python
# Line 49 - naive substring match
has_dead = any(dead in line for dead in dead_imports)
```
This matches "MAX" in "MAX_RETRIES" when only "MAX" should be removed.

**Fix Strategy**:
1. Use regex with word boundaries: `r'\b' + re.escape(symbol) + r'\b'`
2. Or extract exact symbol names from AST `ast.alias` nodes
3. Match only complete symbol names, not substrings

**Commands**:
```bash
# Test word boundary matching
python -c "
import re
line = 'MAX_RETRIES, MAX_DEPTH, TIMEOUT'
dead = {'MAX'}
# Naive - wrong
print('Naive:', any(d in line for d in dead))
# Word boundary - correct
pattern = r'\b' + re.escape('MAX') + r'\b'
print('Word boundary:', bool(re.search(pattern, line)))
"
```

**Acceptance**:
- "MAX" does NOT match "MAX_RETRIES"
- "MAX_RETRIES" matches "MAX_RETRIES" exactly
- No false positives from partial matches
- Tests pass with the new logic

---

## Rollback Strategy

Each wave will be committed separately. If a wave causes issues:
```bash
git revert <commit-hash>
```

---

## Dependencies

- W2-A depends on W1-A (AST parsing provides exact symbol names)
- No external dependencies beyond Python stdlib

---

## Success Metrics

- All imports correctly identified (no comments/strings)
- No partial symbol matches
- Zero false positives/negatives
- All existing tests pass
