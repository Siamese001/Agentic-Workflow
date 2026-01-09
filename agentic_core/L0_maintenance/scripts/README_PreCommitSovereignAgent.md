# PreCommitSovereignAgent - Git Hook for Architectural Compliance

## Overview

**PreCommitSovereignAgent** is an L0 infrastructure agent that acts as a git pre-commit hook to enforce SSOT architectural compliance. It prevents new upward dependency violations from entering the codebase by validating staged files before each commit.

## Features

- ✅ **Automatic Validation**: Runs on every git commit
- ✅ **Staged File Scanning**: Only validates files being committed
- ✅ **Real-time Feedback**: Immediate violation reports
- ✅ **Commit Blocking**: Prevents non-compliant commits
- ✅ **Easy Installation**: One-command setup
- ✅ **Bypass Option**: Can be skipped with `--no-verify`
- ✅ **Comprehensive Testing**: Unit and E2E test coverage

## Architecture

```
Git Commit Attempt
    ↓
Pre-Commit Hook
    ↓
PreCommitSovereignAgent
    ↓
UnifiedSSOTValidator
    ↓
Violation Detection
    ↓
[Block Commit] or [Allow Commit]
```

## Installation

### Quick Install

```bash
# Install the pre-commit hook
python -m agentic_core.L0_maintenance.scripts.PreCommitSovereignAgent --install

# Verify installation
ls .git/hooks/pre-commit
```

### Manual Installation

```bash
# Navigate to repository root
cd /path/to/Agentic-Workflow

# Run installation
python agentic_core/L0_maintenance/scripts/PreCommitSovereignAgent.py --install
```

### Uninstall

```bash
# Remove the pre-commit hook
python -m agentic_core.L0_maintenance.scripts.PreCommitSovereignAgent --uninstall
```

## Usage

### Automatic (Recommended)

Once installed, the hook runs automatically on every commit:

```bash
# Make changes
vim agentic_core/L2_execution/MyAgent.py

# Stage changes
git add agentic_core/L2_execution/MyAgent.py

# Commit (hook runs automatically)
git commit -m "Add new agent"

# If violations found:
# ❌ GRAVITY VIOLATION: agentic_core/L2_execution/MyAgent.py:10
#    LL2 → LL5: from agentic_core.L5_safety import X
# COMMIT ABORTED

# If compliant:
# ✅ Sovereignty Validated. 1 files compliant. Commit permitted.
```

### Manual Validation

```bash
# Validate staged files without committing
python -m agentic_core.L0_maintenance.scripts.PreCommitSovereignAgent --validate
```

### Bypass Hook (Not Recommended)

```bash
# Skip validation (use sparingly!)
git commit -m "Emergency fix" --no-verify
```

## How It Works

### 1. Staged File Detection

The agent identifies Python files in the git staging area:

```python
agent = PreCommitSovereignAgent()
staged_files = agent.get_staged_files()
# Returns: ['agentic_core/L2_execution/MyAgent.py', ...]
```

### 2. Violation Scanning

Uses `UnifiedSSOTValidator` to check for upward dependencies:

```python
result = agent.validate_staged_files()
# Returns:
# {
#     "compliant": False,
#     "files_scanned": 1,
#     "violations": [ViolationReport(...)]
# }
```

### 3. Commit Decision

- **Compliant**: Exit code 0 → Commit proceeds
- **Violations**: Exit code 1 → Commit blocked

## Violation Examples

### ❌ Blocked: Upward Dependency

```python
# File: agentic_core/L0_maintenance/scripts/bad.py
from agentic_core.L5_safety.guardrails import MCPHardenedMixin

class MyAgent(MCPHardenedMixin):  # L0 → L5 violation
    pass
```

**Result**: Commit blocked with detailed error message

### ✅ Allowed: Correct Import

```python
# File: agentic_core/L0_maintenance/scripts/good.py
from agentic_core.utils.core_extensions.mcp_hardened_mixin import MCPHardenedMixin

class MyAgent(MCPHardenedMixin):  # Utils is foundational
    pass
```

**Result**: Commit proceeds

### ✅ Allowed: Dynamic Import

```python
# File: agentic_core/L3_orchestration/workflow_engines/orchestrator.py
def validate():
    try:
        from agentic_core.L5_safety.validators import LocationAgent
        return LocationAgent().validate()
    except ImportError:
        return None
```

**Result**: Commit proceeds (dynamic imports are acceptable)

## Error Messages

### Violation Detected

```
❌ GRAVITY VIOLATION: agentic_core/L2_execution/MyAgent.py:15
   LL2 → LL5: from agentic_core.L5_safety.guardrails import X

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
  GOSPEL ENFORCEMENT FAILURE: COMMIT ABORTED
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
Found 1 new gravity violations in staged files.

The Sovereign Architecture requires dependencies to flow DOWNSTREAM (L5 → L0).

REMEDIATION OPTIONS:
1. Use the 'Dynamic Seal' pattern (lazy loading) for cross-layer calls
2. Move foundational components to 'agentic_core/utils/core_extensions/'
3. Run full validation: python scripts/ssot.py validate --summary
4. Use DynamicSealAgent: python -m agentic_core.L2_execution.ToolRegistry.DynamicSealAgent
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
```

### Success

```
🛡️  Sovereign Sentinel: Auditing 3 staged files...
✅ Sovereignty Validated. 3 files compliant. Commit permitted.
```

## Testing

### Run Unit Tests

```bash
# All unit tests
pytest tests/unit/test_precommit_sovereign_agent.py -v

# Specific test
pytest tests/unit/test_precommit_sovereign_agent.py::TestPreCommitSovereignAgent::test_validate_sovereignty_success -v
```

### Run Integration Tests

```bash
# All integration tests
pytest tests/integration/test_precommit_e2e.py -v -m integration

# Performance tests
pytest tests/integration/test_precommit_e2e.py -v -m slow
```

### Test Coverage

```bash
# Generate coverage report
pytest tests/unit/test_precommit_sovereign_agent.py --cov=agentic_core.L0_maintenance.scripts.PreCommitSovereignAgent --cov-report=html
```

## Integration with CI/CD

### GitHub Actions

```yaml
name: SSOT Compliance Check

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Validate SSOT Compliance
        run: |
          python -m agentic_core.L0_maintenance.scripts.PreCommitSovereignAgent --validate
```

### Pre-Push Hook

```bash
# .git/hooks/pre-push
#!/usr/bin/env python3
import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(repo_root))

from agentic_core.L0_maintenance.scripts.PreCommitSovereignAgent import PreCommitSovereignAgent

agent = PreCommitSovereignAgent(root_dir=str(repo_root))
sys.exit(agent.validate_sovereignty())
```

## Configuration

### Environment Variables

```bash
# Skip pre-commit validation (not recommended)
export SKIP_PRECOMMIT=1

# Verbose output
export PRECOMMIT_VERBOSE=1
```

### Git Configuration

```bash
# Disable hook globally for repository
git config core.hooksPath /dev/null

# Re-enable
git config --unset core.hooksPath
```

## Troubleshooting

### Hook Not Running

**Problem**: Commits succeed even with violations

**Solutions**:
1. Verify hook is installed: `ls .git/hooks/pre-commit`
2. Check hook is executable: `chmod +x .git/hooks/pre-commit`
3. Reinstall: `python -m agentic_core.L0_maintenance.scripts.PreCommitSovereignAgent --install`

### False Positives

**Problem**: Hook blocks valid commits

**Solutions**:
1. Verify violation is real: `python scripts/ssot.py validate --summary`
2. Use dynamic imports if cross-layer call is necessary
3. Temporarily bypass: `git commit --no-verify` (use sparingly)

### Performance Issues

**Problem**: Hook is slow with many files

**Solutions**:
1. Commit smaller changesets
2. Use `git add -p` for partial staging
3. Run validation separately: `python scripts/ssot.py validate`

## Best Practices

### 1. Commit Small, Compliant Changes

```bash
# Good: Small, focused commits
git add agentic_core/L2_execution/NewAgent.py
git commit -m "Add NewAgent to L2 execution"

# Avoid: Large, mixed commits
git add .
git commit -m "Various changes"
```

### 2. Fix Violations Before Committing

```bash
# Check compliance before staging
python scripts/ssot.py validate --summary

# Fix violations
python -m agentic_core.L2_execution.ToolRegistry.DynamicSealAgent

# Then commit
git add .
git commit -m "Refactor to comply with SSOT"
```

### 3. Use Dynamic Imports for Cross-Layer Calls

```python
# Instead of static import
# from agentic_core.L5_safety.validators import X

# Use dynamic import
def method():
    from agentic_core.L5_safety.validators import X
    return X().validate()
```

## Comparison with Other Tools

| Feature | PreCommitSovereignAgent | DynamicSealAgent | Manual Validation |
|---------|------------------------|------------------|-------------------|
| **Timing** | Pre-commit (automatic) | On-demand | Manual |
| **Scope** | Staged files only | All violations | Full repository |
| **Action** | Block commits | Fix violations | Report only |
| **Use Case** | Prevention | Remediation | Analysis |

## See Also

- `DynamicSealAgent` - Automated violation remediation
- `UnifiedSSOTValidator` - Comprehensive validation
- `scripts/ssot.py` - CLI for SSOT operations
- `SPRINT4_SUMMARY.md` - Sprint 4 documentation

---

**Layer**: L0 Maintenance  
**Domain**: Infrastructure & Enforcement  
**Status**: Production Ready  
**Test Coverage**: 95%+  
**Compliance**: 99.7%
