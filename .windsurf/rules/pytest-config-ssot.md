---
trigger:
  - file_change
---
# Pytest Configuration SSOT Enforcement

**Status**: ACTIVE  
**Rule ID**: RULE-PYTEST-SSOT-001  
**Enforcement**: CI Gate + Pre-commit Hook  
**Scope**: `pytest.ini` ↔ `pyproject.toml` consistency

---

## SSOT Hierarchy

| Priority | File | Purpose |
|----------|------|---------|
| **PRIMARY** | `pytest.ini` | Runtime configuration (Windsurf IDE reads this) |
| **REFERENCE** | `pyproject.toml` | Build/package metadata + fallback defaults |

### Key Constraint
`pytest.ini` values **MUST** be equal or stricter than `pyproject.toml` values.  
`pyproject.toml` can have broader defaults; `pytest.ini` provides IDE-optimized runtime values.

---

## Critical Config Fields (Must Match)

### 1. Parallel Execution (xdist)
```ini
# pytest.ini MUST have:
-n auto --dist=loadfile --timeout=180
```
```toml
# pyproject.toml MUST have equivalent:
-n auto --dist=loadfile --timeout=180
```

### 2. Test Discovery Paths
```ini
# pytest.ini
testpaths = tests
python_files = test_*.py *_test.py
```
```toml
# pyproject.toml
testpaths = ["tests"]
python_files = ["test_*.py"]
```

### 3. Required Markers (Must be superset)
`pytest.ini` markers must include all `pyproject.toml` markers.

---

## Prohibited Config Drift Patterns

| Violation | Severity | Auto-Fix |
|-----------|----------|----------|
| `pytest.ini` missing `-n auto` | **CRITICAL** | Yes |
| `pytest.ini` timeout < `pyproject.toml` timeout | **HIGH** | Yes |
| `pytest.ini` missing `serial` marker | **HIGH** | Yes |
| `addopts` conflicts (same option, different values) | **CRITICAL** | Manual |
| `testpaths` mismatch | **MEDIUM** | No |

---

## CI Gate Enforcement

### Command
```bash
python ops_scripts/ci/_validate_pytest_config.py
```

### Exit Codes
- `0`: Configs synchronized
- `1`: Critical drift detected (blocks CI)
- `2`: Warning drift (logs, allows CI)

### CI Integration
```yaml
# .github/workflows/pytest-config-sync.yml
- name: Validate Pytest Config SSOT
  run: python ops_scripts/ci/_validate_pytest_config.py --strict
```

---

## Windsurf IDE Behavior

Windsurf reads pytest configuration in this order:
1. `pytest.ini` (if exists) — **USED**
2. `pyproject.toml` [tool.pytest.ini_options] — **FALLBACK**
3. `setup.cfg` — **NOT USED**
4. `tox.ini` — **NOT USED**

**Critical**: Since `pytest.ini` exists, Windsurf **ignores** `pyproject.toml` pytest settings entirely.

---

## Manual Sync Procedure

When updating pytest configuration:

1. **Edit `pytest.ini` first** (this is the runtime SSOT)
2. **Run validation**: `python ops_scripts/ci/_validate_pytest_config.py`
3. **Commit both files together** (atomic config change)
4. **Verify in Windsurf**: Run `pytest --collect-only -q`

---

## Pre-commit Hook

```yaml
# .pre-commit-config.yaml
- repo: local
  hooks:
    - id: pytest-config-sync
      name: Pytest Config SSOT Check
      entry: python ops_scripts/ci/_validate_pytest_config.py
      language: system
      files: ^(pytest\.ini|pyproject\.toml)$
      pass_filenames: false
```

---

## RCA Template for Config Drift

If drift is detected:

```markdown
## RCA: Pytest Config Drift (RESOLVED)

**Violation**: pytest.ini/pyproject.toml addopts mismatch
**Impact**: Windsurf runs with different settings than CI
**Fix Applied**: Synced -n auto --dist=loadfile to both files
**Prevention**: Pre-commit hook now blocks mismatched configs
**Status**: ✅ RESOLVED
```

---

## Related Rules

- `.windsurf/rules/mcp-config-ssot.md` — Similar pattern for MCP config
- `.windsurf/rules/plan_ci_enforcement.md` — CI gate standards
