# L5 Canon Validator Safety Protocol

## Critical Incident: 2025-12-14

### What Happened
The `ArchitecturalRefactorAgent` attempted to modify **686 files** in a single execution, causing widespread syntax corruption across the codebase. The agent was executing a `MISSION_ENCAPSULATE_GLOBALS` that rewrote global variables but generated invalid Python code (bad indentation, missing commas, broken strings).

### Recovery Actions Taken
1. ✅ Executed `git reset --hard HEAD` to revert 182 corrupted files
2. ✅ Disabled `ArchitecturalRefactorAgent` in main execution loop (line 3224)
3. ✅ Added `MAX_FILES_PER_RUN = 5` safety constraint to agent class
4. ✅ Implemented enforcement in `_execute_encapsulate_globals` method

### L5 Safety Protocol (Permanent)

**The Subatomic Rule:** *An agent may never modify more than 5 files in a single execution.*

#### Implementation Details

**Class-Level Constraint:**
```python
class ArchitecturalRefactorAgent(SubAtomicAgent):
    # L5 SAFETY CONSTRAINT: Never modify more than 5 files in a single execution
    MAX_FILES_PER_RUN = 5
```

**Enforcement in Execution:**
```python
if len(files_with_globals) > self.MAX_FILES_PER_RUN:
    logger.warning(f"⚠️ SAFETY LIMIT: Truncating targets from {len(files_with_globals)} to {self.MAX_FILES_PER_RUN} files")
    files_with_globals = files_with_globals[:self.MAX_FILES_PER_RUN]
```

### Safe Agents (Always Enabled)
- ✅ `WhitespaceMechanic` - Only fixes whitespace
- ✅ `SecurityEnforcer` - Read-only security checks
- ✅ `CodeQualityAuditor` - AST-based fixes (empty except blocks)
- ✅ `StructuralLinter` - Calls autopep8 (safe formatter)
- ✅ `DependencySentinel` - Calls autoflake/isort (safe tools)
- ✅ `BudgetAgent` - Read-only complexity checks
- ✅ `StatePersistenceAgent` - Only persists state, no code changes

### Dangerous Agents (Disabled by Default)
- ⛔ `ArchitecturalRefactorAgent` - Can modify hundreds of files
  - **Status:** Commented out in main loop (line 3224)
  - **Re-enable only if:** MAX_FILES_PER_RUN constraint is verified working
  - **Test first:** Run on isolated test directory with max 5 files

### Testing Protocol Before Re-enabling

1. **Syntax Baseline Check:**
   ```bash
   ruff check . --select E9,F63,F7,F82 --output-format=concise
   ```

2. **Isolated Test:**
   - Create test directory with 10 files containing globals
   - Enable ArchitecturalRefactorAgent
   - Verify only 5 files are modified
   - Verify generated code has valid syntax

3. **Rollback Plan:**
   - Always commit before running ArchitecturalRefactorAgent
   - Keep `git reset --hard HEAD` ready
   - Monitor logs for "SAFETY LIMIT" warnings

### Lessons Learned

1. **Never trust bulk refactoring agents** without file count limits
2. **Always test AST transformations** on small samples first
3. **Commit frequently** when running experimental agents
4. **Syntax validation** must run before and after agent execution
5. **False positives** in validation scores indicate unparseable code

### Current Status
- ✅ Codebase reverted to safe state
- ✅ ArchitecturalRefactorAgent disabled
- ✅ Safety constraints implemented
- ✅ Documentation complete
- ⏳ Awaiting approval to re-enable with constraints

---
**Last Updated:** 2025-12-14
**Incident Severity:** CRITICAL
**Resolution Status:** RESOLVED with permanent safeguards
