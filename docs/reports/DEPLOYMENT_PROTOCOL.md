# Pascal Sovereignty Deployment Protocol

## Overview

The Pascal Sovereignty Fixer enforces strict file naming conventions across the codebase:
- **Agents** → `PascalCaseAgent.py`
- **Classes** → `PascalCase.py`
- **Utilities** → `snake_case.py`

**Current Status:** 640 violations detected across 1,610 files (40% non-compliance)

## ⚠️ CRITICAL WARNINGS

### 1. Magnitude of Change
This is **NOT a refactor** - it is a **migration**. The operation will:
- Rename ~640 files
- Update import paths across the entire codebase
- Modify hundreds of dependent files

### 2. Git Conflict Risk
- **Probability of conflicts with active branches: 100%**
- **MUST be executed on a clean, dedicated branch**
- **MUST be merged immediately after execution**
- **MUST NOT have uncommitted changes**

### 3. Windows-Specific Risks

#### Path Length Limits
- Deep file paths may trigger Windows 260-character limit
- Ensure `LongPathsEnabled` registry key is set
- Most common in `apps_rg` deep nesting

#### File Lock Issues
- Files open in IDEs (VS Code, PyCharm) will cause `PermissionError`
- Running Python processes holding file handles will block renames
- **Failure mid-execution leaves repo in "torn state"**

#### Case Sensitivity
- Windows filesystem is case-insensitive but case-preserving
- Three-step rename (src → temp → dest) handles this safely
- Collision detection prevents overwrites

## Pre-Execution Checklist

### Required Actions
- [ ] **Close ALL IDE instances** (VS Code, PyCharm, etc.)
- [ ] **Close ALL terminal windows** except deployment terminal
- [ ] **Stop ALL running Python processes**
- [ ] **Commit or stash ALL changes** (`git status` must be clean)
- [ ] **Create dedicated branch** (`git checkout -b pascal-sovereignty-migration`)
- [ ] **Verify registry setting** (Windows only):
  ```batch
  reg query HKLM\SYSTEM\CurrentControlSet\Control\FileSystem /v LongPathsEnabled
  ```
  Should return `0x1`. If not, run as Admin:
  ```batch
  reg add HKLM\SYSTEM\CurrentControlSet\Control\FileSystem /v LongPathsEnabled /t REG_DWORD /d 1 /f
  ```

### Recommended Actions
- [ ] **Backup current state** (`git branch backup-pre-sovereignty`)
- [ ] **Run full test suite** to establish baseline
- [ ] **Review dry-run report** thoroughly
- [ ] **Notify team members** to avoid concurrent work
- [ ] **Schedule deployment** during low-activity period

## Deployment Pipeline

The `execute_sovereignty.bat` script enforces a mandatory 3-stage pipeline:

### Stage 1: Safety Tests (Automated)
```batch
python tests/test_pascal_sovereignty.py
```
- Validates all 26 logic tests pass
- Verifies AST classification, import regex, rename safety
- **Blocks deployment if ANY test fails**

### Stage 2: Impact Report (Automated)
```batch
python PascalSovereigntyFixer.py --dry-run > sovereignty_impact_report.txt
```
- Generates detailed report of all planned changes
- Lists every file to be renamed
- Shows violation counts by type
- **Review this file before proceeding**

### Stage 3: User Confirmation (Manual Gate)
```
Type 'YES' to execute the Pascal Sovereignty enforcement:
```
- **The Gatekeeper** - requires explicit user acknowledgment
- Typing anything other than `YES` aborts deployment
- Final opportunity to cancel before execution

### Stage 4: Execution (Automated)
```batch
python PascalSovereigntyFixer.py
```
- Performs actual file renames
- Updates all import references
- Reports success/failure statistics

## Execution

### Standard Deployment
```batch
execute_sovereignty.bat
```

### Manual Deployment (Advanced)
If you need more control:

```batch
# 1. Run tests
python tests/test_pascal_sovereignty.py

# 2. Generate report
python PascalSovereigntyFixer.py --dry-run > report.txt

# 3. Review report
type report.txt

# 4. Execute (if satisfied)
python PascalSovereigntyFixer.py
```

### Validation Only (No Changes)
```batch
python PascalSovereigntyFixer.py --validate
```

## Post-Execution Validation

### Immediate Checks
```batch
# 1. Verify git status
git status

# 2. Check for orphaned imports
python -m pytest tests/ -v

# 3. Run integration tests
python scripts/test_all_agents.py

# 4. Verify no syntax errors
python -m py_compile **/*.py
```

### Expected Git Changes
- ~640 file renames (deletions + additions)
- ~1000+ import statement updates
- No content changes (only paths/names)

### Rollback Procedure
If issues are detected:

```batch
# Immediate rollback
git reset --hard HEAD

# Or restore from backup branch
git checkout backup-pre-sovereignty
git branch -D pascal-sovereignty-migration
```

## Failure Recovery

### Partial Execution Failure
If the script fails mid-execution (e.g., file lock):

1. **DO NOT PANIC** - the script is idempotent
2. **Identify the locked file** from error message
3. **Close the application** holding the file
4. **Re-run the script** - it will skip already-renamed files
5. **Verify completion** with `--validate` flag

### Import Resolution Failures
If imports break after execution:

1. **Check `sovereignty_impact_report.txt`** for expected changes
2. **Search for old import paths** manually:
   ```batch
   findstr /s /i "old_module_name" *.py
   ```
3. **Update manually** if regex missed edge cases
4. **Report issue** to improve regex pattern

## Testing Strategy

### Pre-Deployment Tests
```batch
# Deployment readiness
python tests/test_deployment_readiness.py

# Logic verification
python tests/test_pascal_sovereignty.py
```

### Post-Deployment Tests
```batch
# Full test suite
python -m pytest tests/ -v --tb=short

# Import validation
python -c "import agentic_core; print('OK')"

# Agent discovery
python scripts/discover_agents.py
```

## Known Limitations

### Files NOT Renamed
- `__init__.py` - Always ignored
- `__main__.py` - Treated as utility
- Empty files - Ignored
- Syntax error files - Ignored
- Files outside `agentic_core/`, `apps_*/` - Ignored

### Import Patterns NOT Updated
- Dynamic imports: `importlib.import_module(variable)`
- String-based imports: `__import__('module')`
- Comments containing old names
- Documentation/README references

### Edge Cases
- **Multiple classes per file**: Uses heuristic (matches filename or longest)
- **Utility files**: Currently NOT renamed (conservative approach)
- **Circular imports**: May surface after rename (pre-existing issue)

## Performance

- **Analysis time**: ~5 seconds for 1,610 files
- **Execution time**: ~30-60 seconds for 640 renames + import updates
- **Memory usage**: <100MB peak

## Support

### Troubleshooting
1. Review `sovereignty_impact_report.txt`
2. Check error messages for specific file paths
3. Verify file permissions and locks
4. Ensure running from repo root

### Reporting Issues
Include:
- Full error message
- `git status` output
- `sovereignty_impact_report.txt`
- Python version and OS

## Success Criteria

✅ All 26 logic tests pass
✅ All 4 deployment readiness tests pass
✅ Dry-run report reviewed and approved
✅ Git status clean before execution
✅ All files renamed successfully
✅ All imports updated successfully
✅ Post-execution tests pass
✅ No syntax errors in codebase
✅ Agent discovery runs successfully

---

**Last Updated:** January 25, 2026
**Script Version:** Phase 2 (Class-Based Architecture)
**Test Coverage:** 26 logic tests + 4 deployment tests = 30 total
