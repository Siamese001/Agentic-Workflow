# Orphan Agent Assessment Report

**Generated:** 2026-02-02  
**Total Agents:** 171  
**Orphan Agents:** 11  
**Orphan Rate:** 6.4%

---

## Executive Summary

This report identifies **11 orphan agents** that have no production references in the codebase. These agents exist but are only referenced in test files, scripts, or their own definition files.

### Disposition Summary

| Disposition | Count | Description |
|-------------|-------|-------------|
| ARCHIVE | 7 | Complex agents with healing - move to legacy_archive |
| DEPRECATE | 2 | No clear usage - mark for deprecation review |
| MERGE | 1 | Small agent - consolidate with another |
| KEEP | 1 | HOP pipeline agent - may be used dynamically |

---

## Detailed Orphan Agent Analysis

### 1. HOP9IntegrationAgent

**Disposition:** `KEEP`  
**Path:** `apps_lic/engines/HOP9IntegrationAgent.py`  
**Layer:** Apps  
**Territory:** Apps Lic/HOP  
**LOC:** 68  
**Cyclomatic Complexity:** 10

**Reason:** HOP pipeline agent - may be used dynamically

**Analysis:** This agent is part of the HOP (Hop-based Orchestration Pipeline) and may be invoked dynamically at runtime. Recommend keeping but adding explicit registration.

**Recommended Action:** No action required - verify dynamic usage patterns.

---

### 2. HistorianAgent

**Disposition:** `DEPRECATE`  
**Path:** `agentic_core/L2_execution/tool_registry/HistorianAgent.py`  
**Layer:** L2  
**Territory:** L2 Execution/Runners  
**LOC:** 72  
**Cyclomatic Complexity:** 7

**Reason:** No clear usage pattern - mark for deprecation review

**Analysis:** Small agent with low complexity. Has healing capabilities but no production consumers.

**Recommended Action:** 
1. Add `@deprecated` decorator
2. Schedule for removal in next major version
3. Migrate any useful functionality to `SubAtomicRegistryAgent`

**File Diff (Deprecation):**
```python
# Add at top of file after imports
import warnings
from typing import deprecated  # Python 3.13+ or use typing_extensions

@deprecated("HistorianAgent is deprecated and will be removed in v2.0. Use SubAtomicRegistryAgent instead.")
class HistorianAgent:
    ...
```

---

### 3. DecompositionOrchestratorAgent

**Disposition:** `ARCHIVE`  
**Path:** `agentic_core/L3_orchestration/workflow_engines/DecompositionOrchestratorAgent.py`  
**Layer:** L3  
**Territory:** L3 Orchestration/DAG  
**LOC:** 235  
**Cyclomatic Complexity:** 52

**Reason:** Complex agent with healing - archive for potential future use

**Analysis:** High complexity orchestrator with DAG decomposition logic. May have been superseded by `NervousSystemAgent` or `DomainPlannerAgent`.

**Recommended Action:**
1. Move to `agentic_core/L3_orchestration/legacy_archive/`
2. Update imports in any test files
3. Document reason for archival

**File Diff (Archive Move):**
```bash
# Move command
git mv agentic_core/L3_orchestration/workflow_engines/DecompositionOrchestratorAgent.py \
       agentic_core/L3_orchestration/legacy_archive/DecompositionOrchestratorAgent.py
```

---

### 4. AdversarialProbeAgent

**Disposition:** `ARCHIVE`  
**Path:** `agentic_core/L5_safety/red_teaming/AdversarialProbeAgent.py`  
**Layer:** L5  
**Territory:** L5 Safety/Red Teaming  
**LOC:** 160  
**Cyclomatic Complexity:** 24

**Reason:** Complex agent with healing - archive for potential future use

**Analysis:** Red teaming agent for adversarial testing. Valuable for security testing but not integrated into CI/CD pipeline.

**Recommended Action:**
1. Keep in place but mark as "experimental"
2. Create integration plan for security testing pipeline
3. Add to pre-release validation workflow

**File Diff (Mark Experimental):**
```python
# Add to class docstring
"""
AdversarialProbeAgent - Red Team Security Testing

STATUS: EXPERIMENTAL - Not integrated into production pipeline
TODO: Integrate into pre-release security validation workflow

This agent probes for adversarial vulnerabilities...
"""
```

---

### 5. BoundaryTestingAgent

**Disposition:** `ARCHIVE`  
**Path:** `agentic_core/L5_safety/red_teaming/BoundaryTestingAgent.py`  
**Layer:** L5  
**Territory:** L5 Safety/Red Teaming  
**LOC:** 176  
**Cyclomatic Complexity:** 26

**Reason:** Complex agent with healing - archive for potential future use

**Analysis:** Tests boundary conditions and edge cases. Similar to AdversarialProbeAgent - part of red teaming suite.

**Recommended Action:** Same as AdversarialProbeAgent - mark experimental, plan integration.

---

### 6. ChaosEngineeringAgent

**Disposition:** `ARCHIVE`  
**Path:** `agentic_core/L5_safety/red_teaming/ChaosEngineeringAgent.py`  
**Layer:** L5  
**Territory:** L5 Safety/Red Teaming  
**LOC:** 152  
**Cyclomatic Complexity:** 24

**Reason:** Complex agent with healing - archive for potential future use

**Analysis:** Chaos engineering for resilience testing. Valuable but requires controlled environment.

**Recommended Action:**
1. Keep in red_teaming folder
2. Add safety guards for production environments
3. Create dedicated chaos testing workflow

---

### 7. CostGovernorAgent

**Disposition:** `MERGE`  
**Path:** `agentic_core/L5_safety/guardrails/CostGovernorAgent.py`  
**Layer:** L5  
**Territory:** L5 Safety/Guardrails/Core  
**LOC:** 48  
**Cyclomatic Complexity:** 7  
**Merge Target:** `CodeDetectorAgent`

**Reason:** Small agent, consider merging into CodeDetectorAgent

**Analysis:** Small cost governance agent. Functionality could be absorbed into a broader guardrails agent.

**Recommended Action:**
1. Extract core cost governance logic
2. Merge into `BudgetGuardrailAgent` or create unified `ResourceGovernorAgent`
3. Delete original file after merge

**File Diff (Merge):**
```python
# In target agent (e.g., BudgetGuardrailAgent), add:

class BudgetGuardrailAgent(L5SafetyBase):
    """
    Unified resource and cost governance.
    
    Merged from:
    - CostGovernorAgent (deprecated)
    - BudgetGuardrailAgent (original)
    """
    
    def check_cost_limits(self, operation: str, estimated_cost: float) -> bool:
        """Migrated from CostGovernorAgent."""
        # ... cost governance logic from CostGovernorAgent
        pass
```

---

### 8. DependencyPruningAgent

**Disposition:** `ARCHIVE`  
**Path:** `agentic_core/L5_safety/guardrails/DependencyPruningAgent.py`  
**Layer:** L5  
**Territory:** L5 Safety/Guardrails/Hygiene  
**LOC:** 98  
**Cyclomatic Complexity:** 23

**Reason:** Complex agent with healing - archive for potential future use

**Analysis:** Prunes unused dependencies. Useful for maintenance but not actively used.

**Recommended Action:**
1. Integrate into maintenance scripts
2. Add to periodic cleanup workflow
3. Keep in guardrails but mark as "maintenance-only"

---

### 9. PreCommitSovereignAgent

**Disposition:** `ARCHIVE`  
**Path:** `agentic_core/L5_safety/validators/PreCommitSovereignAgent.py`  
**Layer:** L5  
**Territory:** L5 Safety/Validators/Structure  
**LOC:** 208  
**Cyclomatic Complexity:** 38

**Reason:** Complex agent with healing - archive for potential future use

**Analysis:** Pre-commit validation agent. May have been superseded by `.pre-commit-config.yaml` hooks.

**Recommended Action:**
1. Review overlap with existing pre-commit hooks
2. If redundant, archive to legacy_archive
3. If unique functionality exists, integrate into pre-commit workflow

**File Diff (Integration Check):**
```python
# Add integration marker
"""
PreCommitSovereignAgent - Sovereign Pre-Commit Validation

INTEGRATION STATUS: Review required
- Check overlap with .pre-commit-config.yaml
- Unique features: [list unique features]
- Redundant features: [list redundant features]
"""
```

---

### 10. PromptInjectionAgent

**Disposition:** `ARCHIVE`  
**Path:** `agentic_core/L5_safety/red_teaming/PromptInjectionAgent.py`  
**Layer:** L5  
**Territory:** L5 Safety/Red Teaming  
**LOC:** 147  
**Cyclomatic Complexity:** 22

**Reason:** Complex agent with healing - archive for potential future use

**Analysis:** Tests for prompt injection vulnerabilities. Critical for LLM security but not integrated.

**Recommended Action:**
1. HIGH PRIORITY - Integrate into security testing
2. Add to CI/CD security validation
3. Create prompt injection test suite

---

### 11. SemanticDebuggerAgent

**Disposition:** `DEPRECATE`  
**Path:** `agentic_core/L5_safety/validators/SemanticDebuggerAgent.py`  
**Layer:** L5  
**Territory:** L5 Safety/Validators/Content  
**LOC:** 61  
**Cyclomatic Complexity:** 9

**Reason:** No clear usage pattern - mark for deprecation review

**Analysis:** Small semantic debugging agent. May be superseded by other validation agents.

**Recommended Action:**
1. Review functionality overlap with other validators
2. If unique, integrate into validation pipeline
3. If redundant, deprecate and schedule removal

---

## Test Cases for Orphan Agent Refactoring

### Test Case 1: Verify Orphan Detection Accuracy

```python
# tests/guardian/test_orphan_agent_detection.py

def test_orphan_detection_excludes_production_agents():
    """Verify that actively used agents are NOT flagged as orphans."""
    detector = OrphanAgentDetector(PROJECT_ROOT)
    detector.load_agent_discovery()
    detector.scan_references()
    orphans = detector.identify_orphans()
    
    # These agents should NOT be orphans
    active_agents = {
        "LocationAgent",
        "HierarchyAgent", 
        "GovernanceAgent",
        "NervousSystemAgent",
    }
    
    orphan_names = {o.class_name for o in orphans}
    assert not active_agents.intersection(orphan_names), \
        f"Active agents incorrectly flagged as orphans: {active_agents.intersection(orphan_names)}"
```

### Test Case 2: Verify Deprecation Markers

```python
def test_deprecated_agents_have_markers():
    """Verify deprecated agents have proper deprecation markers."""
    deprecated_agents = [
        "HistorianAgent",
        "SemanticDebuggerAgent",
    ]
    
    for agent_name in deprecated_agents:
        agent_path = find_agent_path(agent_name)
        content = Path(agent_path).read_text()
        
        assert "deprecated" in content.lower() or "DEPRECATED" in content, \
            f"{agent_name} missing deprecation marker"
```

### Test Case 3: Verify Archive Moves

```python
def test_archived_agents_in_correct_location():
    """Verify archived agents are moved to legacy_archive."""
    archived_agents = [
        "DecompositionOrchestratorAgent",
        # Add others after archival
    ]
    
    for agent_name in archived_agents:
        # Should be in legacy_archive
        legacy_path = PROJECT_ROOT / "agentic_core" / "legacy_archive" / f"{agent_name}.py"
        original_path = find_original_agent_path(agent_name)
        
        assert legacy_path.exists() or not original_path.exists(), \
            f"{agent_name} not properly archived"
```

### Test Case 4: Verify Merge Completeness

```python
def test_merged_agent_functionality_preserved():
    """Verify merged agent functionality is preserved in target."""
    merges = {
        "CostGovernorAgent": "BudgetGuardrailAgent",
    }
    
    for source, target in merges.items():
        target_path = find_agent_path(target)
        content = Path(target_path).read_text()
        
        # Check for migration marker
        assert f"Merged from: {source}" in content or \
               f"migrated from {source}" in content.lower(), \
            f"Merge of {source} into {target} not documented"
```

---

## Implementation Checklist

### Phase 1: Immediate Actions (This Sprint)

- [ ] Add deprecation markers to `HistorianAgent` and `SemanticDebuggerAgent`
- [ ] Merge `CostGovernorAgent` into appropriate target
- [ ] Mark red teaming agents as "experimental"

### Phase 2: Integration (Next Sprint)

- [ ] Integrate `PromptInjectionAgent` into security testing pipeline
- [ ] Create chaos testing workflow for `ChaosEngineeringAgent`
- [ ] Review `PreCommitSovereignAgent` overlap with pre-commit hooks

### Phase 3: Cleanup (Following Sprint)

- [ ] Archive `DecompositionOrchestratorAgent` if confirmed unused
- [ ] Remove deprecated agents after deprecation period
- [ ] Update agent discovery to exclude archived agents

---

## Appendix: File Locations

| Agent | Current Path | Recommended Path |
|-------|--------------|------------------|
| HOP9IntegrationAgent | apps_lic/engines/ | *Keep* |
| HistorianAgent | agentic_core/L2_execution/tool_registry/ | *Deprecate in place* |
| DecompositionOrchestratorAgent | agentic_core/L3_orchestration/workflow_engines/ | legacy_archive/ |
| AdversarialProbeAgent | agentic_core/L5_safety/red_teaming/ | *Keep, mark experimental* |
| BoundaryTestingAgent | agentic_core/L5_safety/red_teaming/ | *Keep, mark experimental* |
| ChaosEngineeringAgent | agentic_core/L5_safety/red_teaming/ | *Keep, mark experimental* |
| CostGovernorAgent | agentic_core/L5_safety/guardrails/ | *Merge & delete* |
| DependencyPruningAgent | agentic_core/L5_safety/guardrails/ | *Keep, maintenance-only* |
| PreCommitSovereignAgent | agentic_core/L5_safety/validators/ | *Review for integration* |
| PromptInjectionAgent | agentic_core/L5_safety/red_teaming/ | *HIGH PRIORITY integration* |
| SemanticDebuggerAgent | agentic_core/L5_safety/validators/ | *Deprecate in place* |

---

## Conclusion

The 6.4% orphan rate is within acceptable limits. Most orphan agents are in the L5 Safety layer, particularly in the red_teaming subfolder. These agents have value for security testing but lack production integration.

**Priority Actions:**
1. **HIGH:** Integrate `PromptInjectionAgent` into security pipeline
2. **MEDIUM:** Merge `CostGovernorAgent` to reduce agent count
3. **LOW:** Archive `DecompositionOrchestratorAgent` after review

The guardian test `test_orphan_agent_detection.py` will continuously monitor for new orphan agents and prevent orphan rate from exceeding 30%.
