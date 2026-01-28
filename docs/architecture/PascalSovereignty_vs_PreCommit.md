# PascalSovereigntyFixer vs Pre-Commit Hook: Architectural Distinction

## Question
> "Why is dry run mode for sovereignty needed? Isn't that duplicative with PascalSovFixer?"

## Answer: Different Execution Contexts

### 1. **PascalSovereigntyFixer.py** (Standalone Tool)
**Purpose**: Proactive batch remediation of naming violations

**Execution Context**:
- Run manually by developers: `python agentic_core/L0_maintenance/scripts/PascalSovereigntyFixer.py`
- Run in CI/CD pipelines for full repository scans
- Run during migration/refactoring operations

**Modes**:
- `--dry-run`: Preview violations without making changes (safe exploration)
- `--execute`: Apply renames and fix imports (destructive)

**Use Cases**:
- Developer wants to see what violations exist before committing
- CI/CD wants to audit the entire codebase
- Migration scripts need to verify compliance before proceeding

### 2. **Pre-Commit Hook** (Git Integration)
**Purpose**: Reactive commit-time enforcement

**Execution Context**:
- Triggered automatically by `git commit`
- Blocks commits that introduce new violations
- Cannot be manually invoked outside of git workflow

**Mode**:
- Always runs in **dry-run** mode (read-only)
- Never modifies files (git pre-commit hooks should not mutate working tree)
- Returns exit code 0 (pass) or 1 (block)

**Use Cases**:
- Prevent developers from accidentally committing violations
- Enforce sovereignty at the git boundary
- Provide immediate feedback during commit workflow

## Why Both Are Needed

### Scenario 1: Developer Workflow
```bash
# Step 1: Developer makes changes
vim agentic_core/domain/entities.py  # Creates a class

# Step 2: Developer runs standalone tool to preview
python agentic_core/L0_maintenance/scripts/PascalSovereigntyFixer.py
# Output: [DETECT] entities.py (CLASS) -> BaseEntity.py

# Step 3: Developer decides to fix it
python agentic_core/L0_maintenance/scripts/PascalSovereigntyFixer.py --execute
# Output: Files Renamed: 1, Imports Fixed: 12

# Step 4: Developer commits
git commit -m "feat: Add BaseEntity"
# Pre-commit hook runs in dry-run mode, sees no violations, allows commit
```

### Scenario 2: CI/CD Pipeline
```yaml
# .github/workflows/sovereignty-audit.yml
- name: Full Repository Sovereignty Audit
  run: python agentic_core/L0_maintenance/scripts/PascalSovereigntyFixer.py --dry-run
  # Scans entire repo, reports violations, fails CI if any found
```

### Scenario 3: Emergency Override
```bash
# Developer needs to commit urgently (e.g., hotfix)
git commit --no-verify -m "hotfix: Critical production bug"
# Pre-commit hook bypassed, but CI/CD will catch violations later
```

## Key Differences

| Aspect | PascalSovereigntyFixer | Pre-Commit Hook |
|--------|------------------------|-----------------|
| **Invocation** | Manual or CI/CD | Automatic (git commit) |
| **Scope** | Entire repository | Staged files only |
| **Mutation** | Can modify files (--execute) | Read-only (always dry-run) |
| **Bypass** | N/A | `--no-verify` flag |
| **Purpose** | Remediation tool | Enforcement gate |
| **Timing** | Anytime | Commit-time only |

## Why Pre-Commit Uses Dry-Run

**Git Best Practice**: Pre-commit hooks should **never** modify the working tree because:

1. **User Expectation**: Developers expect `git commit` to commit what they staged, not surprise them with automatic renames
2. **Atomicity**: If the hook fails mid-rename, the repository is left in an inconsistent state
3. **Transparency**: Developers should explicitly run the fixer tool to see what will change
4. **Rollback Safety**: If a rename breaks something, developers can easily revert before committing

## Recommended Workflow

```bash
# 1. Make changes
vim agentic_core/L5_safety/validators/my_validator.py

# 2. Preview violations (optional but recommended)
python agentic_core/L0_maintenance/scripts/PascalSovereigntyFixer.py

# 3. Fix violations
python agentic_core/L0_maintenance/scripts/PascalSovereigntyFixer.py --execute

# 4. Commit (pre-commit hook validates)
git add .
git commit -m "feat: Add MyValidator"
# Hook runs in dry-run, sees compliance, allows commit
```

## Conclusion

The "duplication" is intentional architectural separation:
- **PascalSovereigntyFixer**: Swiss Army knife (scan, preview, fix)
- **Pre-Commit Hook**: Gatekeeper (block violations at commit boundary)

Both use the same core logic but serve different roles in the sovereignty enforcement pipeline.
