# Misnamed Agent Scan - Findings & Recommendations Report

**Date:** January 22, 2026
**Scan Scope:** `agentic_core/**/*Agent.py`
**Total Files Scanned:** 182 (was 185)
**Issues Found:** 35
**Clean Files:** 147 (80.8%)
**Files Deleted:** 3 legacy layer base duplicates

---

## Executive Summary

This scan identified 35 files with naming inconsistencies across three severity levels:

- **HIGH Priority (7 issues):** Utility/Handler classes incorrectly named with "Agent" suffix
- **MEDIUM Priority (24 issues):** Agent classes missing SovereignBaseAgent inheritance
- **LOW Priority (4 issues):** Class name doesn't match filename

**Recent Action:** Deleted 3 legacy duplicate layer base agents (`L2Agent.py`, `L3Agent.py`, `L5Agent.py`) from `L5_safety/validators/` that were redundant with canonical layer bases in their proper locations.

**Impact:** Naming inconsistencies create confusion about which classes are true agents with L0 DNA vs. utility classes. This affects maintainability, discoverability, and architectural clarity.

---

## 🚨 HIGH PRIORITY - 7 Issues

These are **utility/handler/manager classes** incorrectly named with "Agent" suffix in the filename.

### Issue Pattern
- File ends with `Agent.py`
- Class inside is a Handler/Manager/Utility (not a true agent)
- Should be renamed to remove misleading "Agent" suffix

### Findings

| File | Class Name | Issue | Recommendation |
|------|------------|-------|----------------|
| `SovereignRAGManagerAgent.py` | `SovereignRAGManager` | Manager class, not agent | Rename to `SovereignRAGManager.py` |
| `SpiffeManagerAgent.py` | `SpiffeManager` | Manager class, not agent | Rename to `SpiffeManager.py` |
| `FirecrackerManagerAgent.py` | `FirecrackerManager` | Manager class, not agent | Rename to `FirecrackerManager.py` |
| `DagManagerAgent.py` | `DAGManager` | Manager class, not agent | Rename to `DAGManager.py` |

### Recommended Actions

```bash
# Rename utility/manager classes
git mv agentic_core/knowledge/document_loaders/SovereignRAGManagerAgent.py \
      agentic_core/knowledge/document_loaders/SovereignRAGManager.py

git mv agentic_core/L1_cognition/thought_engine/SpiffeManagerAgent.py \
      agentic_core/L1_cognition/thought_engine/SpiffeManager.py

git mv agentic_core/L2_execution/ToolRegistry/FirecrackerManagerAgent.py \
      agentic_core/L2_execution/ToolRegistry/FirecrackerManager.py

git mv agentic_core/L3_orchestration/workflow_engines/DagManagerAgent.py \
      agentic_core/L3_orchestration/workflow_engines/DAGManager.py
```

**Impact:** These renames eliminate architectural confusion and make it clear which files contain true agents vs. utility classes.

---

## ⚠️ MEDIUM PRIORITY - 24 Issues

These are **true agent classes** that are missing SovereignBaseAgent inheritance (L0 DNA).

### Issue Pattern
- File ends with `Agent.py`
- Class name ends with `Agent`
- But doesn't inherit from `SovereignBaseAgent` or layer base agents

### Findings by Category

#### **L5 Safety Validators (12 agents)**

| Agent | Status |
|-------|--------|
| `CodeDetectorAgent` | Missing L0 DNA |
| `CodeEnforcerAgent` | Missing L0 DNA |
| `ResourceManagerAgent` | Missing L0 DNA |
| `SafetyDetectorAgent` | Missing L0 DNA |
| `SecurityManagerAgent` | Missing L0 DNA |
| `DDDAlignmentAgent` | Missing L0 DNA |
| `FilesystemSSOTReconcilerAgent` | Missing L0 DNA |
| `GapClosureArchitectAgent` | Missing L0 DNA |
| `GospelSyncAgent` | Missing L0 DNA |
| `MetricsWitnessAgent` | Missing L0 DNA |
| `ReportingAgent` | Missing L0 DNA |
| `TerritoryChangeHandlerAgent` | Missing L0 DNA |

#### **L6 Observability (1 agent)**

| Agent | Status |
|-------|--------|
| `SovereignObservabilityAgent` | Missing L0 DNA |

#### **Other Layers (11 agents)**

| Agent | Layer | Status |
|-------|-------|--------|
| `AutonomousPromptEvolutionAgent` | L1 Cognition | Missing L0 DNA |
| `UnifiedModelRouterAgent` | L2 Execution | Missing L0 DNA |
| `UnifiedOrchestratorAgent` | L3 Orchestration | Missing L0 DNA |
| `CognitiveDispositionAgent` | L5 Safety | Missing L0 DNA |
| `LocationValidatorAgent` | L5 Safety | Missing L0 DNA |
| `SSOTFolderCleanupAgent` | L5 Safety | Missing L0 DNA |
| `UnifiedCodeDetectorAgent` | L5 Safety | Missing L0 DNA |
| `UnifiedCodeEnforcerAgent` | L5 Safety | Missing L0 DNA |
| `UnifiedResourceManagerAgent` | L5 Safety | Missing L0 DNA |
| `UnifiedSafetyDetectorAgent` | L5 Safety | Missing L0 DNA |
| `UnifiedSecurityManagerAgent` | L5 Safety | Missing L0 DNA |

### Recommended Actions

**Option 1: Bulk Migration (Recommended)**

Run the existing migration script to add SovereignBaseAgent inheritance:

```bash
python migrate_plain_classes.py
```

**Option 2: Manual Migration**

For each agent, add:

```python
from agentic_core.observability.SovereignBaseAgent import SovereignBaseAgent

class MyAgent(SovereignBaseAgent):
    def __init__(self, **kwargs):
        super().__init__()
        # ... rest of init
```

**Impact:** Adding L0 DNA ensures all agents have:
- Autonomous Repair Capability (`heal_repository`)
- MCP hardening
- Self-testing capability
- Prompt injection protection

---

## ℹ️ LOW PRIORITY - 4 Issues

These are **naming mismatches** where the class name doesn't match the filename.

### Findings

| File | Class Name | Issue |
|------|------------|-------|
| `StrategicPlannerAgent.py` | `RgStrategicPlannerAgent` | Prefix mismatch |
| `ReflectionAgent.py` | `RgReflectionAgent` | Prefix mismatch |
| `S2_SupervisorAgent.py` | `LicS2SupervisorAgent` | Prefix mismatch |

### Recommended Actions

**Option 1:** Rename files to match class names

```bash
git mv agentic_core/L2_execution/ToolRegistry/StrategicPlannerAgent.py \
      agentic_core/L2_execution/ToolRegistry/RgStrategicPlannerAgent.py

git mv agentic_core/L5_safety/validators/ReflectionAgent.py \
      agentic_core/L5_safety/validators/RgReflectionAgent.py

git mv agentic_core/L5_safety/validators/S2_SupervisorAgent.py \
      agentic_core/L5_safety/validators/LicS2SupervisorAgent.py
```

**Option 2:** Rename classes to match filenames (if prefixes are legacy)

**Impact:** Low - these are cosmetic inconsistencies but should be resolved for consistency.

---

## Special Case: CanonDependencySentinelAgent

**File:** `CanonDependencySentinelAgent.py`
**Classes:** `CodeJanitor`, `DependencySentinelAgent`, `NestingVisitor`
**Issue:** File contains multiple classes, primary class is `CodeJanitor` (not agent)

**Recommendation:**
- Extract `CodeJanitor` to separate file `CodeJanitor.py`
- Keep `DependencySentinelAgent` in current file
- Or rename file to match primary class usage

---

## ✅ Recently Resolved: Legacy Layer Base Duplicates

### **Deleted Files (3)**

These legacy duplicates were removed as they conflicted with canonical layer base agents:

| Deleted File | Canonical Replacement | Location |
|--------------|----------------------|----------|
| `L5_safety/validators/L2Agent.py` | `L2ExecutionBaseAgent` | `L2_execution/ToolRegistry/` |
| `L5_safety/validators/L3Agent.py` | `L3OrchestrationBaseAgent` | `L3_orchestration/workflow_engines/` |
| `L5_safety/validators/L5Agent.py` | `L5SafetyBaseAgent` | `L5_safety/validators/` |

**Why Deleted:**
- **Zero imports** - No files referenced them
- **Canonical versions exist** - Proper layer base agents are in correct locations
- **Architectural clarity** - Removes confusion about which base to use
- **SSOT compliance** - Layer bases should live in their layer directories, not duplicated

**Impact:** Eliminates 3 sources of confusion and ensures developers use the correct, feature-complete layer base agents.

---

## Implementation Priority

### Phase 1: HIGH Priority (Immediate)

1. Rename 4 utility/handler files to remove "Agent" suffix
2. Update all imports referencing these files
3. Run tests to verify no breakage

### Phase 2: MEDIUM Priority (This Sprint)

1. Run bulk migration script for 24 agents missing L0 DNA
2. Verify each agent compiles after migration
3. Run `canon_validator_agentic_v2_thin.py --full` to confirm 100% DNA compliance

### Phase 3: LOW Priority (Next Sprint)

1. Resolve 4 filename/classname mismatches
2. Update documentation to reflect new naming conventions

---

## Naming Convention Enforcement

### Going Forward

**Rule 1:** Files ending in `Agent.py` MUST contain a class ending in `Agent`
**Rule 2:** Classes ending in `Agent` MUST inherit from `SovereignBaseAgent` or layer base
**Rule 3:** Utility/Handler/Manager classes MUST NOT use "Agent" suffix
**Rule 4:** Layer base agents MUST live in their respective layer directories (no duplicates)

### Enforcement Mechanisms

1. **Pre-commit Hook:** Add check for Agent naming conventions
2. **CI/CD Gate:** Run `scan_misnamed_agents.py` in CI pipeline
3. **Code Review:** Flag any new Agent files without proper inheritance
4. **Duplicate Detection:** Scan for duplicate layer base agents

---

## Conclusion

**Current State:**
- 182 Agent files scanned (down from 185)
- 147 (80.8%) are correctly named and structured
- 35 (19.2%) have naming or inheritance issues
- 3 legacy duplicates eliminated

**Target State:**
- 100% of Agent files contain true agents with L0 DNA
- 0% utility classes masquerading as agents
- 100% filename/classname consistency
- 0% duplicate layer base agents

**Estimated Effort:**
- HIGH priority: 2-3 hours (rename + update imports)
- MEDIUM priority: 4-6 hours (bulk migration + verification)
- LOW priority: 1-2 hours (cosmetic fixes)
- **Total:** ~8-11 hours

**Risk:** Low - Changes are surgical and can be validated with existing test suite.

---

**Generated by:** `scan_misnamed_agents.py`
**Report Date:** January 22, 2026
**Last Updated:** After deleting 3 legacy layer base duplicates
