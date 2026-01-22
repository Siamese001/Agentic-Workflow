# 🛡️ Global Agent Governance & Signal Audit Report

**Generated:** 2026-01-22  
**Scope:** `agentic_core/` (excluding tests, archives)

---

## Executive Summary

| Category | Count | Status |
|----------|-------|--------|
| **Signal Blocks** (missing `**kwargs`) | 111 | ⚠️ Needs Remediation |
| **Compliant Signatures** | 49 | ✅ Good |
| **Rogue Gatekeepers** (terminal interaction) | 21 | ⚠️ Review Required |
| **Sovereign-Aware Agents** | 13 | ✅ Good |
| **Sovereign-Unaware** (with file ops) | 10 | ⚠️ Risk |

---

## 1. Signal Leaks Analysis

### Problem
111 agents have `heal_repository` methods that do NOT accept `**kwargs`, which blocks parameter propagation through the healing chain.

### Impact
- `depth`, `max_depth`, `auto_approve` signals cannot propagate
- Recursive healing chains break at these agents
- Orchestrator context is lost

### Signal Block Agents (Sample)

| Agent | Current Signature |
|-------|-------------------|
| `BootstrapAgent.py` | `heal_repository(self, dry_run, execute, depth, max_depth, _call_path)` |
| `L0MaintenanceBaseAgent.py` | `heal_repository(self, dry_run, execute, depth, max_depth, _call_path)` |
| `L1CognitionBaseAgent.py` | `heal_repository(self, dry_run, execute, depth, max_depth, _call_path)` |
| `L2ExecutionBaseAgent.py` | `heal_repository(self, dry_run, execute, depth, max_depth, _call_path)` |
| `L3OrchestrationBaseAgent.py` | `heal_repository(self, dry_run, execute, depth, max_depth, _call_path)` |
| `HistorianAgent.py` | `heal_repository(self)` |
| `StrategicPlannerAgent.py` | `heal_repository(self)` |
| `CoverageAgent.py` | `heal_repository(self)` |
| `DagRuntimeInspectorAgent.py` | `heal_repository(self)` |

### Recommended Fix

```python
# BEFORE (Signal Block)
def heal_repository(self, dry_run=True, execute=False, depth=0, max_depth=3, _call_path=None):
    ...

# AFTER (Signal Compliant)
def heal_repository(self, dry_run=True, execute=False, depth=0, max_depth=3, _call_path=None, **kwargs):
    ...
```

---

## 2. Rogue Gatekeepers Analysis

### Problem
21 agents implement their own terminal interaction logic (`input()` or `_prompt` patterns) instead of delegating to `ArchivalGatekeeper`.

### Impact
- `--yes` CLI flag is bypassed
- `SOVEREIGN_AUTO_APPROVE` env var is ignored
- Automated healing stalls waiting for terminal input

### Rogue Gatekeeper Agents

| Agent | Findings |
|-------|----------|
| `HierarchyAgent.py` | `input()`, `_prompt pattern` |
| `LocationHealerAgent.py` | `input()`, `_prompt pattern` |
| `GovernanceAgent.py` | `input()`, `_prompt pattern` |
| `FilesystemSSOTReconcilerAgent.py` | `input()`, `_prompt pattern` |
| `LLMPromptGovernorAgent.py` | `input()`, `_prompt pattern` |
| `RedSentinelAgent.py` | `input()` |
| `BoundaryTestingAgent.py` | `input()` |
| `SubatomicHopAgent.py` | `input()` |

### Recommended Fix

```python
# BEFORE (Rogue Gatekeeper)
def _prompt_user_for_approval(self, action: str) -> bool:
    response = input(f"Approve {action}? [y/N]: ")
    return response.lower() == 'y'

# AFTER (Delegated to Gatekeeper)
def _get_approval(self, action: str) -> bool:
    return self.gatekeeper.safe_operation(action)
```

---

## 3. Environmental Context Analysis

### Problem
10 agents perform file operations (move, delete, rename) without checking sovereign context signals.

### Impact
- Operations may execute when they should be blocked
- `dry_run` intent from orchestrator may be ignored
- No respect for `SOVEREIGN_AUTO_APPROVE` or `ARCHIVE_BATCH_ACCEPT`

### Sovereign-Unaware Agents (with file ops)

| Agent | Risk Level |
|-------|------------|
| `LLMPromptGovernorAgent.py` | HIGH |
| `L4StateBaseAgent.py` | MEDIUM |
| `UnifiedCheckpointManagerAgent.py` | MEDIUM |
| `UnifiedStateManagementAgent.py` | MEDIUM |
| `GenerativeGuardAgent.py` | MEDIUM |
| `AutonomyGuardianAgent.py` | MEDIUM |
| `CodeDeduplicationAgent.py` | HIGH |
| `PreCommitSovereignAgent.py` | MEDIUM |
| `SovereignActionPlaneAgent.py` | MEDIUM |
| `TestSovereigntyAgent.py` | LOW (test) |

### Recommended Fix

```python
# Add sovereign context check before file operations
import os

def _should_auto_approve(self) -> bool:
    return (
        os.environ.get("SOVEREIGN_AUTO_APPROVE", "0") == "1" or
        os.environ.get("ARCHIVE_BATCH_ACCEPT", "0") == "1"
    )

def safe_delete(self, path: Path) -> bool:
    if self._should_auto_approve():
        path.unlink()
        return True
    return self.gatekeeper.safe_delete(path)
```

---

## 4. Hardening Recommendations

### Priority 1: Fix Layer Base Agents (Critical)

These are inherited by many agents, so fixing them propagates the fix:

1. `L0MaintenanceBaseAgent.py`
2. `L1CognitionBaseAgent.py`
3. `L2ExecutionBaseAgent.py`
4. `L3OrchestrationBaseAgent.py`
5. `L4StateBaseAgent.py`
6. `L5SafetyBaseAgent.py`

**Action:** Add `**kwargs` to all `heal_repository` signatures.

### Priority 2: Eliminate Direct `input()` Calls (High)

Focus on agents with direct `input()` calls:

1. `HierarchyAgent.py`
2. `LocationHealerAgent.py`
3. `GovernanceAgent.py`
4. `FilesystemSSOTReconcilerAgent.py`
5. `RedSentinelAgent.py`
6. `BoundaryTestingAgent.py`
7. `SubatomicHopAgent.py`
8. `LLMPromptGovernorAgent.py`

**Action:** Replace `input()` with `self.gatekeeper.safe_operation()`.

### Priority 3: Add Sovereign Context Checks (Medium)

For agents with file operations:

1. `CodeDeduplicationAgent.py`
2. `LLMPromptGovernorAgent.py`
3. `UnifiedCheckpointManagerAgent.py`

**Action:** Add `SOVEREIGN_AUTO_APPROVE` check before destructive operations.

---

## 5. Canonical `heal_repository` Signature

All agents should use this signature:

```python
def heal_repository(
    self,
    dry_run: bool = True,
    execute: bool = False,
    depth: int = 0,
    max_depth: int = 3,
    _call_path: Optional[Set[str]] = None,
    **kwargs
) -> Dict[str, int]:
    """
    Standardized healing method.
    
    Args:
        dry_run: If True, only report violations
        execute: If True, apply fixes
        depth: Current recursion depth
        max_depth: Maximum recursion depth
        _call_path: Set of visited agents (cycle detection)
        **kwargs: Additional context from orchestrator
        
    Returns:
        Dict with canonical keys: violations_found, violations_fixed, errors, skipped
    """
```

---

## 6. Next Steps

1. **Automated Fix Script:** Create a script to add `**kwargs` to all signal block agents
2. **Gatekeeper Migration:** Refactor rogue gatekeepers to use `ArchivalGatekeeper`
3. **Sovereign Context Injection:** Add context checks to file-operating agents
4. **Regression Tests:** Add tests to verify signal propagation through healing chain

---

**Report End**
