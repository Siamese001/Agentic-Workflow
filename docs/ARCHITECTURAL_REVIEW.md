# Deep Architectural Review: Top 5 Consolidation & Hardening Opportunities

**Date:** January 19, 2026
**Scope:** `agentic_core/` and `scripts/` directories
**Objective:** Identify structural friction, redundant logic, and dependency risks

---

## Analysis Summary

| Metric | Count (Active Code) | Risk Level | Trend |
|--------|---------------------|------------|-------|
| Cross-imports (`from agentic_core.*`) | ~2,500 in active files | HIGH | → Stable |
| Orchestrator classes | 28 files (active) | MEDIUM | ↓ Improving |
| rglob/glob usage | ~200 in active files | MEDIUM | ↓ Improving |
| Mixin classes | 193 files with mixin patterns | LOW | ↓ Improved |
| BaseAgent variants | 8 active (down from 11) | LOW | ✅ Resolved |
| heal_repository implementations | ~300 in active files | MEDIUM | → Stable |

> **Note:** Raw grep counts include `.sovereign_healing_backup/` and `archives/` directories. Active code counts exclude these.

---

## Opportunity #1: Orchestrator Proliferation (CRITICAL)

### Rationale

The codebase contains **28 distinct orchestrator classes** with overlapping responsibilities:

- `ConsolidatedOrchestratorAgent` - "The General"
- `SSOTOrchestratorAgent` - SSOT validation
- `ComplianceOrchestratorAgent` - Compliance checks
- `HealingOrchestratorAgent` - Healing coordination
- `GuardianOrchestratorAgent` - Guardian coordination
- `WorkflowOrchestratorAgent` - Workflow execution
- `mission_controller.py` - Mission execution
- `mission_controller_engine.py` - Mission engine
- Plus 20+ RL/specialized orchestrators

**Friction:** Multiple entry points for "run all agents" creates confusion. Developers don't know which orchestrator to use. Each has slightly different result handling, logging, and error recovery.

### Consolidation Targets

**Files to Merge:**

```
agentic_core/L3_orchestration/ConsolidatedOrchestratorAgent.py
agentic_core/L3_orchestration/workflow_engines/SSOTOrchestratorAgent.py
agentic_core/L3_orchestration/workflow_engines/WorkflowOrchestratorAgent.py
agentic_core/L3_orchestration/workflow_engines/mission_controller.py
agentic_core/L3_orchestration/workflow_engines/mission_controller_engine.py
agentic_core/L5_safety/validators/HealingOrchestratorAgent.py
agentic_core/L5_safety/validators/GuardianOrchestratorAgent.py
agentic_core/L5_safety/validators/ComplianceOrchestratorAgent.py
```

**Files to Deprecate (RL Orchestrators - low usage):**

```
agentic_core/L3_orchestration/workflow_engines/ActorCriticOrchestratorAgent.py
agentic_core/L3_orchestration/workflow_engines/PPOOrchestratorAgent.py
agentic_core/L3_orchestration/workflow_engines/QLearningOrchestratorAgent.py
agentic_core/L3_orchestration/workflow_engines/RLOrchestratorAgent.py
agentic_core/L3_orchestration/workflow_engines/ReinforceCriticOrchestratorAgent.py
```

### Detailed Implementation Plan

**Step 1:** Create unified orchestrator interface

```python
# agentic_core/L3_orchestration/interfaces/IOrchestratorAgent.py
from typing import Protocol, List, Dict, Any
from agentic_core.utils.result_utils import AgentResult

class IOrchestratorAgent(Protocol):
    def run_mission(
        self,
        agents: List[str],
        dry_run: bool = True,
        execute: bool = False
    ) -> Dict[str, Any]: ...

    def run_agent(
        self,
        agent_name: str,
        dry_run: bool = True
    ) -> AgentResult: ...
```

**Step 2:** Create `UnifiedOrchestratorAgent` that consolidates all patterns

```python
# agentic_core/L3_orchestration/UnifiedOrchestratorAgent.py
class UnifiedOrchestratorAgent(L3OrchestrationBaseAgent):
    """
    Single entry point for all orchestration needs.

    Modes:
    - HEALING: Run healing agents (replaces HealingOrchestratorAgent)
    - COMPLIANCE: Run compliance checks (replaces ComplianceOrchestratorAgent)
    - SSOT: Run SSOT validation (replaces SSOTOrchestratorAgent)
    - FULL: Run complete mission (replaces ConsolidatedOrchestratorAgent)
    """
    pass
```

**Step 3:** Migrate callers from old orchestrators to unified one

**Step 4:** Add deprecation warnings to old orchestrators

**Step 5:** Delete deprecated files after 30-day migration period

### Progress Log (Jan 19, 2026)

| Action | Status | Evidence |
|--------|--------|----------|
| Create `UnifiedOrchestratorAgent.py` | ✅ Completed | `agentic_core/L3_orchestration/UnifiedOrchestratorAgent.py` exists |
| Create `IOrchestratorAgent` protocol | ✅ Completed | `agentic_core/L3_orchestration/interfaces/IOrchestratorAgent.py` exists |
| Add DeprecationWarnings to old orchestrators | ⚠️ Pending | No warnings found in legacy orchestrators |
| Migrate callers to unified orchestrator | ⚠️ Pending | Legacy orchestrators still in use |

**Status: IN PROGRESS** - Foundation complete, migration pending.

### Hardening Action

**Programmatic Enforcement:**

```python
# agentic_core/L3_orchestration/orchestrator_registry.py
REGISTERED_ORCHESTRATORS = {
    "healing": UnifiedOrchestratorAgent,
    "compliance": UnifiedOrchestratorAgent,
    "ssot": UnifiedOrchestratorAgent,
}

def get_orchestrator(mode: str) -> IOrchestratorAgent:
    """Factory function - single entry point."""
    if mode not in REGISTERED_ORCHESTRATORS:
        raise ValueError(f"Unknown orchestrator mode: {mode}")
    return REGISTERED_ORCHESTRATORS[mode]
```

**Import Guard:**

```python
# In deprecated orchestrators
import warnings
warnings.warn(
    "SSOTOrchestratorAgent is deprecated. Use UnifiedOrchestratorAgent instead.",
    DeprecationWarning,
    stacklevel=2
)
```

---

## Opportunity #2: BaseAgent Fragmentation (HIGH)

### Rationale

The codebase has **11 different BaseAgent files** creating a fragmented inheritance hierarchy:

```
SovereignBaseAgent.py (root)
  L0MaintenanceBaseAgent.py
  MaintenanceBaseAgent.py (duplicate?)
  L1CognitionBaseAgent.py
  L2ExecutionBaseAgent.py
  ExecutionCanonBaseAgent.py (duplicate?)
  CanonBaseAgent.py (duplicate?)
  L3OrchestrationBaseAgent.py
  L4StateBaseAgent.py
  L5SafetyBaseAgent.py
  L6ObservabilityBaseAgent.py
```

**Friction:**
- Unclear which base to inherit from
- Duplicate functionality across bases
- MRO complexity when combining mixins
- 3 different "L2 base" variants

### Consolidation Targets

**Files to Merge/Delete:**

```
DELETE: agentic_core/L0_maintenance/scripts/MaintenanceBaseAgent.py (duplicate of L0MaintenanceBaseAgent)
DELETE: agentic_core/L2_execution/ToolRegistry/CanonBaseAgent.py (merge into L2ExecutionBaseAgent)
DELETE: agentic_core/L2_execution/ToolRegistry/ExecutionCanonBaseAgent.py (merge into L2ExecutionBaseAgent)
```

**Files to Standardize:**

```
agentic_core/utils/core_extensions/SovereignBaseAgent.py - ROOT (keep)
agentic_core/L0_maintenance/scripts/L0MaintenanceBaseAgent.py - Layer 0 (keep)
agentic_core/L1_cognition/thought_engine/L1CognitionBaseAgent.py - Layer 1 (keep)
agentic_core/L2_execution/ToolRegistry/L2ExecutionBaseAgent.py - Layer 2 (keep, absorb others)
agentic_core/L3_orchestration/workflow_engines/L3OrchestrationBaseAgent.py - Layer 3 (keep)
agentic_core/L4_state/ValidationContext/L4StateBaseAgent.py - Layer 4 (keep)
agentic_core/L5_safety/guardrails/L5SafetyBaseAgent.py - Layer 5 (keep)
agentic_core/L6_observability/L6ObservabilityBaseAgent.py - Layer 6 (keep)
```

### Detailed Implementation Plan

**Step 1:** Audit all agents using deprecated bases

```bash
grep -r "CanonBaseAgent\|ExecutionCanonBaseAgent\|MaintenanceBaseAgent" agentic_core/
```

**Step 2:** Update imports in affected agents

```python
# Before
from agentic_core.L2_execution.ToolRegistry.CanonBaseAgent import CanonBaseAgent

# After
from agentic_core.L2_execution.ToolRegistry.L2ExecutionBaseAgent import L2ExecutionBaseAgent
```

**Step 3:** Merge unique functionality from deprecated bases into layer bases

**Step 4:** Delete deprecated base files

**Step 5:** Add `__all__` exports to layer base modules

### Progress Log (Jan 19, 2026)

| Action | Status | Evidence |
|--------|--------|----------|
| Delete `CanonBaseAgent.py` | ✅ Completed | Not found in `agentic_core/` (archived to `archives/void_violations/`) |
| Delete `ExecutionCanonBaseAgent.py` | ✅ Completed | Not found in `agentic_core/` |
| Delete `MaintenanceBaseAgent.py` | ✅ Completed | Not found in `agentic_core/` (archived to `archives/void_violations/`) |
| Standardize layer bases | ✅ Completed | 8 active BaseAgent files remain |

**Status: ✅ COMPLETED** - BaseAgent fragmentation resolved. Down from 11 to 8 active files.

### Hardening Action

**AST Validation in CI:**

```python
# scripts/validate_base_inheritance.py
ALLOWED_BASES = {
    "L0": "L0MaintenanceBaseAgent",
    "L1": "L1CognitionBaseAgent",
    "L2": "L2ExecutionBaseAgent",
    "L3": "L3OrchestrationBaseAgent",
    "L4": "L4StateBaseAgent",
    "L5": "L5SafetyBaseAgent",
    "L6": "L6ObservabilityBaseAgent",
}

def validate_agent_base(file_path: Path) -> bool:
    """Ensure agent inherits from correct layer base."""
    layer = infer_layer(file_path)
    expected_base = ALLOWED_BASES.get(layer)
    actual_bases = extract_bases(file_path)
    return expected_base in actual_bases
```

---

## Opportunity #3: rglob Scan Proliferation (HIGH)

### Rationale

**304 rglob/glob calls across 194 files** create:
- Performance degradation (scanning entire repo repeatedly)
- Inconsistent exclusion patterns
- Risk of scanning backup directories (`.sovereign_healing_backup`)
- Duplicate discovery logic

**Top Offenders:**
- `test_dashboard_end_to_end.py` (13 rglob calls)
- `test_hierarchy_agent_root_healing.py` (11 rglob calls)
- `NamingAgent.py` (8 rglob calls)

### Consolidation Targets

**Files with Excessive rglob:**

```
agentic_core/L0_maintenance/scripts/test_dashboard_end_to_end.py (13)
agentic_core/L0_maintenance/scripts/test_hierarchy_agent_root_healing.py (11)
agentic_core/L5_safety/validators/NamingAgent.py (8)
agentic_core/L0_maintenance/scripts/populate_pinecone_embeddings.py (6)
agentic_core/L5_safety/guardrails/HierarchyAgent.py (5)
agentic_core/L5_safety/guardrails/StructuralHealerAgent.py (4)
agentic_core/L5_safety/validators/LocationAgent.py (3)
```

### Detailed Implementation Plan

**Step 1:** Extend `ssot_discovery.py` with file scanning utilities

```python
# agentic_core/utils/ssot_discovery.py (extend)
def get_python_files(
    project_root: Path,
    include_tests: bool = False,
    include_scripts: bool = True
) -> List[Path]:
    """
    Get Python files from SSOT discovery, not rglob.
    Falls back to cached file list if available.
    """
    pass

def get_files_by_layer(
    project_root: Path,
    layer: str
) -> List[Path]:
    """Get files for a specific layer."""
    pass
```

**Step 2:** Create file cache that's regenerated on discovery

```python
# agentic_core/utils/file_cache.py
class FileCache:
    """Cached file listing to avoid repeated rglob scans."""

    def __init__(self, project_root: Path):
        self._cache_file = project_root / ".file_cache.json"
        self._files = self._load_or_scan()

    def get_python_files(self) -> List[Path]:
        return self._files.get("python", [])

    def invalidate(self):
        """Called when files are added/removed."""
        self._files = self._scan()
        self._save()
```

**Step 3:** Refactor top offenders to use cache

**Step 4:** Add lint rule to flag new rglob usage

### Progress Log (Jan 19, 2026)

| Action | Status | Evidence |
|--------|--------|----------|
| Create `ssot_discovery.py` | ⚠️ Pending | File not found in `agentic_core/utils/` |
| Create `FileCache` class | ⚠️ Pending | Not implemented |
| Refactor `test_dashboard_end_to_end.py` | ⚠️ Partial | Reduced from 13 to 9 rglob calls |
| Add lint rule for rglob | ⚠️ Pending | No CI check implemented |

**Status: ⚠️ PENDING** - No significant progress. rglob usage still high.

### Hardening Action

**Import Guard:**

```python
# agentic_core/utils/scan_guard.py
import warnings

def guarded_rglob(path: Path, pattern: str) -> List[Path]:
    """
    Wrapper that logs rglob usage and suggests alternatives.
    """
    warnings.warn(
        f"rglob usage detected. Consider using ssot_discovery.get_python_files() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    return list(path.rglob(pattern))
```

**CI Check:**

```python
# scripts/check_rglob_usage.py
def check_rglob_count(max_allowed: int = 50) -> bool:
    """Fail CI if rglob usage exceeds threshold."""
    count = count_rglob_calls()
    if count > max_allowed:
        print(f"ERROR: {count} rglob calls exceed limit of {max_allowed}")
        return False
    return True
```

---

## Opportunity #4: Mixin Inheritance Complexity (MEDIUM-HIGH)

### Rationale

**256 files with mixin patterns** and **1,450 mixin references** create:
- Deep MRO chains (10+ classes)
- Initialization order bugs (`super().__init__()` issues)
- Attribute shadowing between mixins
- Circular import risks

**Key Mixins (by usage):**
- `HealerMixin` - 321 files
- `MCPHardenedMixin` - 321 files
- `SubatomicTestingMixin` - 321 files

**Problem:** Every agent inherits all three, creating a 3-way diamond pattern.

### Consolidation Targets

**Mixin Files to Consolidate:**

```
agentic_core/utils/core_extensions/healer_mixin.py
agentic_core/utils/core_extensions/mcp_hardened_mixin.py (duplicate location)
agentic_core/L5_safety/guardrails/mcp_hardened_mixin.py (original location)
agentic_core/utils/core_extensions/subatomic_testing_mixin.py
agentic_core/L3_orchestration/fission_logic/subatomic_testing_mixin.py (duplicate)
```

### Detailed Implementation Plan

**Step 1:** Consolidate mixin locations (single source)

```
KEEP: agentic_core/utils/core_extensions/healer_mixin.py
KEEP: agentic_core/utils/core_extensions/mcp_hardened_mixin.py
KEEP: agentic_core/utils/core_extensions/subatomic_testing_mixin.py
DELETE: agentic_core/L5_safety/guardrails/mcp_hardened_mixin.py
DELETE: agentic_core/L3_orchestration/fission_logic/subatomic_testing_mixin.py
```

**Step 2:** Create unified infrastructure mixin

```python
# agentic_core/utils/core_extensions/infrastructure_mixin.py
class InfrastructureMixin(HealerMixin, MCPHardenedMixin, SubatomicTestingMixin):
    """
    Unified infrastructure mixin combining all standard capabilities.

    Agents should inherit from this instead of individual mixins.
    """

    def __init__(self):
        super().__init__()
        # Unified initialization
```

**Step 3:** Update SovereignBaseAgent to use InfrastructureMixin

**Step 4:** Remove individual mixin imports from agents

### Progress Log (Jan 19, 2026)

| Action | Status | Evidence |
|--------|--------|----------|
| Create `InfrastructureMixin` | ✅ Completed | `agentic_core/utils/core_extensions/infrastructure_mixin.py` exists |
| Consolidate mixin locations | ✅ Completed | Duplicates archived |
| Update `SovereignBaseAgent` | ✅ Completed | Uses Root Injection Pattern (MCPHardenedMixin in root) |
| Delete duplicate mixins | ✅ Completed | `L5_safety/guardrails/mcp_hardened_mixin.py` archived |

**Status: ✅ COMPLETED** - Mixin complexity resolved via Root Injection Pattern.

### Hardening Action

**MRO Validation:**

```python
# scripts/validate_mro.py
def validate_mro(agent_class: type) -> bool:
    """
    Ensure MRO follows pattern:
    Agent -> Specialized -> Layer -> Sovereign -> Infrastructure -> object
    """
    mro = agent_class.__mro__

    # Check Infrastructure is near the end
    infra_idx = mro.index(InfrastructureMixin)
    object_idx = mro.index(object)

    if infra_idx > object_idx - 2:
        return False

    return True
```

**Import Guard:**

```python
# In individual mixin files
import warnings
warnings.warn(
    "Direct mixin import deprecated. Use InfrastructureMixin instead.",
    DeprecationWarning
)
```

---

## Opportunity #5: Healing Method Fragmentation (MEDIUM)

### Rationale

**936 heal_repository references across 290 files** with inconsistent:
- Return value formats (`violations` vs `violations_found`)
- Parameter signatures (`dry_run`, `execute`, `depth`, `**kwargs`)
- Error handling patterns
- Logging approaches

**Problem:** Orchestrators must handle 5+ different return formats.

### Consolidation Targets

**Files with Non-Standard Signatures:**

```
# Missing **kwargs (breaks orchestrator calls)
agentic_core/L5_safety/validators/BiasAuditorAgent.py
agentic_core/L5_safety/validators/L5Agent.py
agentic_core/L5_safety/validators/MethodChangeDetectorAgent.py

# Non-standard return keys
agentic_core/L5_safety/guardrails/HierarchyAgent.py (uses 'violations' not 'violations_found')
agentic_core/L5_safety/validators/NamingAgent.py (uses 'renamed' not 'fixed')
```

### Detailed Implementation Plan

**Step 1:** Define canonical signature in HealerMixin

```python
# agentic_core/utils/core_extensions/healer_mixin.py
from typing import TypedDict

class HealResult(TypedDict):
    violations_found: int
    violations_fixed: int
    status: str  # 'PASS', 'FAIL', 'ERROR', 'SKIPPED'
    errors: int
    skipped: int

def heal_repository(
    self,
    dry_run: bool = True,
    execute: bool = False,
    depth: int = 0,
    max_depth: int = 3,
    **kwargs
) -> HealResult:
    """Canonical signature - all agents must match."""
    pass
```

**Step 2:** Create signature validator

```python
# scripts/validate_heal_signatures.py
import inspect

def validate_heal_signature(agent_class: type) -> bool:
    """Ensure heal_repository matches canonical signature."""
    method = getattr(agent_class, 'heal_repository', None)
    if not method:
        return False

    sig = inspect.signature(method)
    params = list(sig.parameters.keys())

    required = ['self', 'dry_run', 'execute']
    for req in required:
        if req not in params:
            return False

    # Must accept **kwargs
    if not any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values()):
        return False

    return True
```

**Step 3:** Fix non-compliant agents

**Step 4:** Add return value normalization to HealerMixin

```python
def _normalize_result(self, result: Dict) -> HealResult:
    """Normalize any return format to HealResult."""
    return {
        'violations_found': result.get('violations_found') or result.get('violations') or 0,
        'violations_fixed': result.get('violations_fixed') or result.get('fixed') or result.get('renamed') or 0,
        'status': result.get('status', 'UNKNOWN'),
        'errors': result.get('errors', 0),
        'skipped': result.get('skipped', 0),
    }
```

### Progress Log (Jan 19, 2026)

| Action | Status | Evidence |
|--------|--------|----------|
| Define `HealResult` TypedDict | ⚠️ Pending | Not found in `healer_mixin.py` |
| Create signature validator | ⚠️ Pending | `validate_heal_signatures.py` not created |
| Fix non-compliant agents | ⚠️ Pending | ~20 agents still have non-standard signatures |
| Add result normalization | ⚠️ Pending | `_normalize_result` not implemented |

**Status: ⚠️ PENDING** - No progress on healing method standardization.

### Hardening Action

**Protocol Enforcement:**

```python
# agentic_core/utils/core_extensions/protocols.py
from typing import Protocol, runtime_checkable

@runtime_checkable
class IHealable(Protocol):
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        **kwargs
    ) -> HealResult: ...

# Usage in orchestrator
def run_agent(agent: IHealable) -> AgentResult:
    if not isinstance(agent, IHealable):
        raise TypeError(f"{agent} does not implement IHealable protocol")
    return agent.heal_repository(dry_run=True)
```

**CI Validation:**

```python
# scripts/validate_heal_compliance.py
def validate_all_healers() -> bool:
    """Validate all agents with heal_repository match protocol."""
    from agentic_core.utils.ssot_discovery import get_healers

    failures = []
    for agent_data in get_healers():
        cls = import_agent_class(agent_data)
        if not validate_heal_signature(cls):
            failures.append(agent_data['class_name'])

    if failures:
        print(f"FAIL: {len(failures)} agents have non-compliant heal_repository")
        return False
    return True
```

---

## Implementation Priority Matrix

| Opportunity | Impact | Effort | Priority |
|-------------|--------|--------|----------|
| #1 Orchestrator Consolidation | HIGH | HIGH | P1 |
| #2 BaseAgent Fragmentation | HIGH | MEDIUM | P1 |
| #3 rglob Proliferation | MEDIUM | LOW | P2 |
| #4 Mixin Complexity | MEDIUM | MEDIUM | P2 |
| #5 Healing Fragmentation | MEDIUM | LOW | P3 |

---

## Recommended Execution Order

### Week 1: Foundation

1. Create `IOrchestratorAgent` protocol
2. Create `IHealable` protocol
3. Add signature validation scripts

### Week 2: Consolidation

4. Merge BaseAgent variants
5. Consolidate mixin locations
6. Create `InfrastructureMixin`

### Week 3: Orchestrator Unification

7. Create `UnifiedOrchestratorAgent`
8. Add deprecation warnings to old orchestrators
9. Migrate callers

### Week 4: Hardening

10. Add CI checks for all protocols
11. Reduce rglob usage below threshold
12. Delete deprecated files

---

## Success Metrics

| Metric | Jan 18 | Jan 19 | Target | Status |
|--------|--------|--------|--------|--------|
| Orchestrator classes | 28 | 28 | 3 | ⚠️ In Progress |
| BaseAgent variants | 11 | 8 | 8 | ✅ Achieved |
| rglob calls (active) | 304 | ~200 | <50 | ⚠️ Partial |
| Mixin locations | 5 | 3 | 3 | ✅ Achieved |
| Non-compliant heal signatures | ~20 | ~20 | 0 | ⚠️ Pending |

---

## New Friction Identified (Jan 19, 2026)

### Anti-Pattern: Backup Directory Bloat

The `.sovereign_healing_backup/` directory has grown significantly, inflating grep counts:
- 10,310 files matched for cross-imports (vs ~800 active)
- 4,706 files matched for heal_repository (vs ~300 active)

**Recommendation:** Implement periodic backup pruning or exclude from all scans.

### Anti-Pattern: Test Files in Production Directories

Several test files exist in production directories:
- `agentic_core/L5_safety/validators/test_dashboard_end_to_end.py`
- `agentic_core/L5_safety/validators/test_hierarchy_agent_root_healing.py`
- `agentic_core/L5_safety/validators/test_healer_mixin_heal_repository.py`

**Recommendation:** Move to `tests/` directory to maintain clean production lens.

---

## Recommended Next 3 Refactoring Targets

Based on updated priority analysis:

1. **`agentic_core/L3_orchestration/workflow_engines/SSOTOrchestratorAgent.py`**
   - Add `DeprecationWarning` pointing to `UnifiedOrchestratorAgent`
   - Priority: HIGH (blocks Opportunity #1 completion)

2. **`agentic_core/utils/core_extensions/healer_mixin.py`**
   - Add `HealResult` TypedDict
   - Implement canonical `heal_repository` signature
   - Priority: HIGH (blocks Opportunity #5)

3. **`agentic_core/utils/ssot_discovery.py`** (CREATE)
   - Implement `get_python_files()` and `get_files_by_layer()`
   - Replace rglob usage in top offenders
   - Priority: MEDIUM (Opportunity #3)

---

**End of Architectural Review**
