# Agent Discovery Inconsistency Report

**Date:** January 12, 2026  
**Scope:** Full codebase analysis (284 agents discovered)  
**Status:** 🔴 **8 Critical Inconsistency Categories Identified**  
**Related:** L6ObservabilityBaseAgent fix revealed similar patterns

---

## Executive Summary

Comprehensive analysis of `agent_discovery_full.json` reveals **8 categories of systemic inconsistencies** affecting **241+ agents** across the codebase. These issues mirror the L6ObservabilityBaseAgent problem that was just resolved (ABC inheritance exclusion).

**Key Findings:**
- **196 agents** missing expected layer base inheritance (69% of agents)
- **12 duplicate agent names** across different locations
- **6 base agents** in wrong territories
- **4 agents** in "Unknown" territories
- **2 L5 agents** not MCP hardened (security violation)
- **2 SovereignBaseAgent duplicates** in different directories

---

## **Category 1: Base Agents in Wrong Territories** 🔴 **CRITICAL**

**Issue:** 6 base agents are NOT in "Base Class" territories, violating dashboard organizational structure.

### **Affected Agents:**

| Agent Name | Layer | Current Territory | Expected Territory | Priority |
|------------|-------|-------------------|-------------------|----------|
| `L2Agent` | L2 | `L2 Execution/Core` | `L2 Execution/Base Class` | HIGH |
| `L3Agent` | L3 | `L3 Orchestration/Core` | `L3 Orchestration/Base Class` | HIGH |
| `L4Agent` | L4 | `L4 State/Core` | `L4 State/Base Class` | HIGH |
| `L5Agent` | L5 | `L5 Safety/Validators` | `L5 Safety/Base Class` | HIGH |
| `SovereignBaseAgent` | Unknown | `Unknown` | Should be categorized | CRITICAL |
| `SovereignBaseAgent` | utils | `utils` | Duplicate - needs resolution | CRITICAL |

### **Root Cause:**
The discovery script's `is_base_class` check at line 1297-1301 only includes:
```python
is_base_class = (
    node.name.endswith('BaseAgent') or 
    node.name in {'L0MaintenanceBaseAgent', 'L1CognitionBaseAgent', 'L6Agent', 'L6ObservabilityBaseAgent'} or
    'BaseAgent' in node.name
)
```

**Missing:** L2Agent, L3Agent, L4Agent, L5Agent are NOT in the explicit list.

### **Recommended Fix:**
Update `scripts/full_agent_discovery.py` line 1299:
```python
is_base_class = (
    node.name.endswith('BaseAgent') or 
    node.name in {'L0MaintenanceBaseAgent', 'L1CognitionBaseAgent', 'L2Agent', 'L3Agent', 'L4Agent', 'L5Agent', 'L6Agent', 'L6ObservabilityBaseAgent'} or
    'BaseAgent' in node.name
)
```

### **Impact:**
- Dashboard shows base agents mixed with concrete agents
- Breaks layer-by-layer base class visualization
- Inconsistent with L0, L1, L6 which ARE in Base Class territories

---

## **Category 2: Agents Inheriting from ABC** ⚠️ **POTENTIAL EXCLUSION RISK**

**Issue:** 2 agents inherit from `ABC` (Abstract Base Class), which almost caused L6ObservabilityBaseAgent to be excluded.

### **Affected Agents:**

| Agent Name | Layer | Territory | Inheritance | Risk Level |
|------------|-------|-----------|-------------|------------|
| `L6ObservabilityBaseAgent` | L6 | `L6_Observability/Base Class` | ABC, SovereignBaseAgent | ✅ FIXED |
| `SovereignBaseAgent` | utils | `utils` | ABC, HealerMixin | 🔴 AT RISK |

### **Root Cause:**
Before the fix, the discovery script excluded agents inheriting from ABC at Layer 1 (line 820):
```python
if bases & non_agent_bases:
    log.debug(f"EXCLUDED {name}: inherits from non-agent base {bases & non_agent_bases}")
    return False
```

This was fixed for base agents, but `SovereignBaseAgent` in utils may still be vulnerable.

### **Verification Needed:**
Check if `SovereignBaseAgent` (utils) is:
1. A duplicate of `agentic_core/base_agents/SovereignBaseAgent.py`
2. Should be excluded as deprecated
3. Needs the same ABC exception applied

### **Recommended Action:**
1. Investigate if utils/SovereignBaseAgent is a stale duplicate
2. If duplicate, remove the utils version
3. If legitimate, ensure ABC exception applies

---

## **Category 3: Orphaned Agents (No Inheritance)** ⚠️ **MEDIUM PRIORITY**

**Issue:** 31 agents have NO inheritance, indicating they don't follow the agent hierarchy.

### **Sample Affected Agents:**
1. `ContentCleanlinessValidatorAgent` (Apps)
2. `ConvergenceDetectorAgent` (Apps)
3. `InternalAgent` (Apps)
4. `MessageDiversityValidatorAgent` (Apps)
5. `PlaceholderDetectorAgent` (Apps)
6. `StrictDocEnforcerAgent` (Apps)
7. `TestContentQualityAgent` (Apps)
8. `TestLeadQualityAgent` (Apps)
9. `TestOutreachProactiveAgent` (Apps)
10. `TestProactiveAgent` (Apps)
... and 21 more

### **Root Cause:**
These agents either:
1. Don't inherit from any base class
2. Are test harnesses that shouldn't be discovered
3. Are utilities misclassified as agents

### **Impact:**
- No access to healing capabilities (HealerMixin)
- No standardized agent lifecycle
- May indicate test harnesses leaking into production agent count

### **Recommended Fix:**
1. Review each agent to determine if it's a real agent or test fixture
2. If real agent: Add proper base class inheritance
3. If test fixture: Add to skip list in discovery script
4. If utility: Rename to not end with "Agent"

---

## **Category 4: Missing Expected Layer Base Inheritance** 🔴 **CRITICAL - 196 AGENTS**

**Issue:** 196 agents (69% of total) are missing expected layer-specific base class inheritance.

### **Expected Inheritance by Layer:**

| Layer | Expected Base Classes | Agents Missing | Example Agents |
|-------|----------------------|----------------|----------------|
| L0 | `L0MaintenanceBaseAgent` | ~10 | BootstrapAgent, FilesystemSSOTReconcilerAgent |
| L1 | `L1CognitionBaseAgent`, `L1CognitionBaseAgent` | ~25 | Various cognition agents |
| L2 | `L2Agent`, `L2ExecutionBaseAgent` | ~40 | Various execution agents |
| L3 | `L3Agent`, `L3OrchestrationBaseAgent` | ~50 | Various orchestration agents |
| L4 | `L4Agent`, `L4StateBaseAgent` | ~12 | Various state agents |
| L5 | `L5Agent`, `L5SafetyBaseAgent` | ~55 | Various safety agents |
| L6 | `L6Agent`, `L6ObservabilityBaseAgent` | 0 (all correct now) | ✅ Fixed |

### **Sample L0 Agents Missing Base Inheritance:**
- BootstrapAgent
- FilesystemSSOTReconcilerAgent
- GapClosureArchitectAgent
- GospelSyncAgent
- GuardianOrchestratorAgent
- HealingOrchestratorAgent
- MetricsWitnessAgent
- PreCommitSovereignAgent
- ScriptToAgentClassifierAgent
- ScriptsPlanningOrchestratorAgent

### **Root Cause:**
Agents were created without proper inheritance from layer base classes, likely due to:
1. Copy-paste from different layers
2. Evolution of codebase before base class standardization
3. Direct inheritance from SovereignBaseAgent instead of layer bases

### **Impact:**
- Agents lack layer-specific capabilities
- Breaks architectural layering
- Inconsistent agent behavior across layers
- Dashboard categorization may be unreliable

### **Recommended Fix:**
**Phased approach:**
1. **Phase 1 (Quick Win):** Update L0 agents (10 agents) to inherit from L0MaintenanceBaseAgent
2. **Phase 2:** Update L1-L2 agents (~65 agents)
3. **Phase 3:** Update L3-L5 agents (~117 agents)
4. **Phase 4:** Validate all agents have proper inheritance chain

**Example Fix for BootstrapAgent:**
```python
# Before
class BootstrapAgent(SovereignBaseAgent):
    ...

# After
class BootstrapAgent(L0MaintenanceBaseAgent):
    ...
```

---

## **Category 5: MCP Hardening Inconsistencies** 🔴 **SECURITY VIOLATION**

**Issue:** 2 out of 57 L5 Safety agents are NOT MCP hardened, violating the security mandate.

### **Affected Agents:**

| Agent Name | Territory | MCP Hardened | Risk Level |
|------------|-----------|--------------|------------|
| `CompositeGuardrailAgent` | L5 Safety/Guardrails | ❌ NO | HIGH |
| `L5SafetyExerciserAgent` | L5 Safety/Guardrails | ❌ NO | HIGH |

### **Root Cause:**
L5 Safety agents are required to inherit from `MCPHardenedMixin` for external resource protection, but these 2 agents are missing it.

### **Impact:**
- Potential security vulnerability
- Unprotected external resource access
- Non-compliance with L5 safety requirements

### **Recommended Fix:**
Update both agents to include MCPHardenedMixin:
```python
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin

class CompositeGuardrailAgent(L5SafetyBaseAgent, MCPHardenedMixin):
    ...
```

### **Verification:**
Run E2E test 11 to confirm MCP hardening after fix.

---

## **Category 6: Duplicate Agent Names** 🔴 **CRITICAL - 12 DUPLICATES**

**Issue:** 12 agent names exist in multiple locations, causing ambiguity and potential runtime conflicts.

### **All Duplicates:**

| Agent Name | Instance 1 | Instance 2 | Conflict Type |
|------------|-----------|-----------|---------------|
| `CognitiveContractValidatorAgent` | `L1_cognition/thought_engine` | `schemas/models` | Cross-module |
| `HealingOrchestratorAgent` | `apps_rg/engines/resume_engine` | `L0_maintenance/scripts` | App vs Core |
| `InternalAgent` | `apps_lic/engines/outreach_engine` | `L2_execution/ToolRegistry` | App vs Core |
| `OrganizationAgent` | `apps_lic/engines/outreach_engine` | `L2_execution/ToolRegistry` | App vs Core |
| `RecipientAgent` | `apps_lic/engines/outreach_engine` | `L2_execution/ToolRegistry` | App vs Core |
| `ReflectionAgent` | `apps_rg/engines/resume_engine` | `L1_cognition/thought_engine` | App vs Core |
| `ResumeOrchestratorAgent` | `apps_rg/engines/resume_engine` | `L3_orchestration/workflow_engines` | App vs Core |
| `S2_SupervisorAgent` | `apps_lic/engines/outreach_engine` | `L2_execution/ToolRegistry` | App vs Core |
| `SovereignBaseAgent` | `base_agents` | `utils/core_extensions` | **BASE CLASS DUPLICATE** |
| `StrategicPlannerAgent` | `apps_rg/engines/resume_engine` | `L2_execution/ToolRegistry` | App vs Core |
| `TemplateOptimizerAgent` | `apps_lic/engines/outreach_engine` | `apps_rg/engines/resume_engine` | App vs App |
| `WorkflowOrchestratorAgent` | `apps_lic/engines/outreach_engine` | `L0_maintenance/scripts` | App vs Core |

### **Most Critical: SovereignBaseAgent Duplicate**

**Instance 1:** `agentic_core/base_agents/SovereignBaseAgent.py`
- Simple implementation, inherits from MCPHardenedMixin
- Used by most agents

**Instance 2:** `agentic_core/utils/core_extensions/SovereignBaseAgent.py`
- Complex implementation with @dataclass, inherits from ABC
- Has HealerMixin, RedisCacheMixin, PineconeVectorMixin
- Likely a legacy/experimental version

### **Root Cause:**
1. Code evolution without cleanup
2. App-specific agents copied to core
3. Refactoring incomplete

### **Impact:**
- Import ambiguity
- Different agents with same name may have different capabilities
- Runtime conflicts if both are imported
- Dashboard confusion

### **Recommended Fix:**

**For SovereignBaseAgent:**
1. Determine which version is canonical
2. Rename or remove the non-canonical version
3. Update all imports to use canonical version

**For App/Core Duplicates:**
1. Rename app-specific agents with prefix (e.g., `LicInternalAgent`, `RgReflectionAgent`)
2. Or consolidate if functionality is identical
3. Update imports across codebase

---

## **Category 7: Agents in 'Unknown' Territories** ⚠️ **MEDIUM PRIORITY**

**Issue:** 4 agents are categorized as "Unknown" or "utils", indicating discovery script couldn't determine their layer.

### **Affected Agents:**

| Agent Name | Layer | Territory | Path |
|------------|-------|-----------|------|
| `CognitiveContractValidatorAgent` | Unknown | Unknown | `schemas/models` |
| `PromptRegistryAgent` | Unknown | Unknown | `prompt_governance` |
| `SovereignBaseAgent` | Unknown | Unknown | `base_agents` |
| `SovereignBaseAgent` | utils | utils | `utils/core_extensions` |

### **Root Cause:**
Discovery script uses path-based layer detection which fails for:
1. Agents in non-standard directories (`schemas`, `prompt_governance`, `base_agents`, `utils`)
2. Base agents that don't follow standard layer structure

### **Impact:**
- Agents not visible in dashboard layer breakdown
- May be excluded from layer-specific validations
- Dashboard "Unknown" category is confusing

### **Recommended Fix:**

**Option 1: Add explicit layer mappings**
```python
# In full_agent_discovery.py
SPECIAL_LAYER_MAPPINGS = {
    'schemas': 'L1',  # Validation schemas are cognition-related
    'prompt_governance': 'L1',  # Prompt management is cognition
    'base_agents': 'Base',  # Special category for base agents
    'utils': 'Utils',  # Utility category
}
```

**Option 2: Create dedicated territories**
- `Base Agents/Core` for SovereignBaseAgent
- `Governance/Prompts` for PromptRegistryAgent
- `Validation/Schemas` for CognitiveContractValidatorAgent

---

## **Category 8: Dataclass Agents** ℹ️ **INFORMATIONAL**

**Issue:** Some agents use `@dataclass` decorator, which almost caused L6ObservabilityBaseAgent to be excluded.

### **Known Dataclass Agents:**
1. `L6ObservabilityBaseAgent` (✅ Fixed - ABC exclusion bypass added)
2. `SovereignBaseAgent` (utils version - also inherits from ABC)

### **Root Cause:**
Discovery script has logic at line 926 that excludes dataclasses without strong signals:
```python
if any(d in {'dataclass', 'attrs', 'attr.s'} for d in decorators) and not has_strong_positive_signal and not is_base_agent:
    return False
```

The fix we applied ensures `is_base_agent` protects dataclass base agents.

### **Verification Needed:**
Search codebase for other agents using `@dataclass` that might be at risk:
```bash
grep -r "@dataclass" agentic_core --include="*Agent.py"
```

### **Recommended Action:**
1. Audit all agents using `@dataclass`
2. Ensure they have proper inheritance signals
3. Add to `is_base_agent` check if they're base classes

---

## **Summary & Priority Matrix**

| Category | Agents Affected | Priority | Effort | Impact |
|----------|----------------|----------|--------|--------|
| 1. Base Agents in Wrong Territories | 6 | 🔴 HIGH | LOW | Medium |
| 2. ABC Inheritance Risk | 2 | ⚠️ MEDIUM | LOW | Medium |
| 3. Orphaned Agents | 31 | ⚠️ MEDIUM | HIGH | Medium |
| 4. Missing Layer Base Inheritance | 196 | 🔴 CRITICAL | HIGH | HIGH |
| 5. MCP Hardening | 2 | 🔴 CRITICAL | LOW | HIGH (Security) |
| 6. Duplicate Names | 12 | 🔴 HIGH | MEDIUM | High |
| 7. Unknown Territories | 4 | ⚠️ MEDIUM | LOW | Low |
| 8. Dataclass Agents | 2+ | ℹ️ INFO | LOW | Low |

### **Total Impact:** 241+ agents affected

---

## **Recommended Action Plan**

### **Phase 1: Critical Fixes (Week 1)**
1. ✅ **L6ObservabilityBaseAgent ABC inheritance** - COMPLETE
2. 🔴 **Fix MCP hardening** for 2 L5 agents (SECURITY)
3. 🔴 **Resolve SovereignBaseAgent duplicate** (BASE CLASS)
4. 🔴 **Add L2Agent-L5Agent to base class check** (6 agents)

### **Phase 2: High Priority (Week 2)**
5. 🔴 **Rename/consolidate 12 duplicate agents**
6. 🔴 **Fix top 20 agents missing layer base inheritance**

### **Phase 3: Medium Priority (Week 3-4)**
7. ⚠️ **Categorize 4 Unknown territory agents**
8. ⚠️ **Review 31 orphaned agents** (determine if test fixtures or real agents)
9. ⚠️ **Continue fixing missing layer base inheritance** (remaining 176 agents)

### **Phase 4: Comprehensive Audit (Week 5+)**
10. ℹ️ **Audit all @dataclass agents**
11. ℹ️ **Standardize agent naming conventions**
12. ℹ️ **Create comprehensive agent inheritance map**

---

## **Files Modified for Analysis**

1. **`agent_discovery_full.json`** - Source data for analysis
2. **`analyze_inconsistencies.py`** - Analysis script (temporary)
3. **This report** - Complete findings

---

## **Related Documents**

- `L6_BASE_AGENT_FIX_COMPLETE.md` - L6ObservabilityBaseAgent fix documentation
- `L6_BASE_AGENT_RCA_FINAL.md` - Root cause analysis for L6 base agent
- `MISTAKENLY_DEPRECATED_AGENTS_REPORT.md` - Archived agents analysis
- `scripts/full_agent_discovery.py` - Discovery script requiring updates
- `scripts/test_dashboard_end_to_end.py` - E2E tests showing failures

---

**Report Generated:** January 12, 2026  
**Next Review:** After Phase 1 fixes complete  
**Owner:** Development Team
