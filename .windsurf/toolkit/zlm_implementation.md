# Zero Loss Merge (ZLM) Implementation Protocol

**Purpose:** Ensure zero regressions during any code modification.

---

## Protocol Steps

### 1. List Target Files

Before any modification, explicitly list every file that will be touched:

```text
TARGET FILES:
- path/to/file1.py (modify)
- path/to/file2.py (modify)
- path/to/new_file.py (create)
```

### 2. Shadow Implementation

Create `.zlm.tmp` shadow versions of files before modification:

```bash
cp target_file.py target_file.py.zlm.tmp
```

Implement minimal changes in the shadow file first. This allows:
- Easy rollback via `mv target_file.py.zlm.tmp target_file.py`
- Side-by-side diff comparison
- Safe experimentation

### 3. Regression Tests

For every fix, add exactly 3 focused tests:

| Test Type | Purpose | Example |
|-----------|---------|---------|
| **Failure Case** | Verify the bug existed | Assert old behavior fails |
| **Happy Path** | Verify the fix works | Assert new behavior succeeds |
| **Edge Case** | Verify boundary handling | Assert edge conditions work |

Test naming convention: `test_zlm_<audit_id>_<type>`

```python
def test_zlm_audit001_failure():
    """Regression test: verify the original bug behavior."""
    pass

def test_zlm_audit001_happy_path():
    """Verify the fix works for the primary use case."""
    pass

def test_zlm_audit001_edge_case():
    """Verify boundary conditions are handled."""
    pass
```

### 4. Verification

Run full test suite before finalizing:

```bash
pytest tests/ -v
```

**If tests fail:**

```text
REVERT: [specific reason for failure]
```

Stop immediately. Do not proceed with broken tests.

### 5. Final Output

Produce ultra-detailed unified diff(s) only:

```diff
--- a/path/to/file.py
+++ b/path/to/file.py
@@ -10,7 +10,7 @@
 context line
-old line
+new line
 context line
```

---

## Strict Rules

1. **Preserve ALL existing behavior** - No unrelated modifications
2. **Use full canonical paths** - Always use absolute paths in diff headers
3. **Minimal changes only** - Smallest possible fix for the issue
4. **No side effects** - Changes must not affect unrelated functionality
5. **Document everything** - Every change needs justification

---

## Rollback Procedure

If anything goes wrong:

```bash
# Restore from shadow file
mv target_file.py.zlm.tmp target_file.py

# Or restore from git
git checkout -- target_file.py
```

---

## Checklist

Before committing any ZLM fix:

- [ ] Target files explicitly listed
- [ ] Shadow files created
- [ ] 3 regression tests added
- [ ] Full test suite passes
- [ ] Diff is minimal and focused
- [ ] No unrelated changes included
- [ ] Rollback procedure tested
