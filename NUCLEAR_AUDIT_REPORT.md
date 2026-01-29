# NUCLEAR AUDIT REPORT: Agent Technical Status
Generated: 2026-01-29T16:03:46.271370
Total Agents Analyzed: 7

## Summary Statistics
- Broken Inheritance: 7 agents
- Missing heal() Method: 7 agents
- Invalid Namespace: 7 agents
- Stub/Incomplete Agents: 0 agents

## Detailed Technical Status

| Agent | Layer | File | Inheritance | heal() | Namespace | Type | Complexity | Issues |
|-------|-------|------|-------------|--------|-----------|------|------------|--------|
| RootCustomsAgent | L0 | agentic_core\L0_maintenance\logs\RoutingDecisionAgent.py | [BROKEN] - Missing SovereignBaseAgent inheritance | [MISSING] - No heal() method | [INVALID] | Concrete | 66.0 | ISSUES 4 |
| RootCustomsAgent | L0 | agentic_core\L0_maintenance\scripts\RoutingDecisionAgent.py | [BROKEN] - Missing SovereignBaseAgent inheritance | [MISSING] - No heal() method | [INVALID] | Concrete | 126.0 | ISSUES 4 |
| SubAtomicAgent | L2 | agentic_core\L2_execution\tool_registry\BaseToolAgent.py | [BROKEN] - Missing SovereignBaseAgent inheritance | [MISSING] - No heal() method | [INVALID] | Concrete | 14.5 | ISSUES 4 |
| BaseAgent | L2 | agentic_core\L2_execution\tool_registry\BaseToolAgent.py | [BROKEN] - Missing SovereignBaseAgent inheritance | [MISSING] - No heal() method | [INVALID] | Concrete | 15.5 | ISSUES 4 |
| BaseAgent | L3 | agentic_core\L3_orchestration\workflow_engines\DomainPlannerAgent.py | [BROKEN] - Missing SovereignBaseAgent inheritance | [MISSING] - No heal() method | [INVALID] | Concrete | 45.5 | ISSUES 3 |
| DiscoveredAgent | Unknown | agentic_core\DiscoveredAgent.py | [BROKEN] - Missing SovereignBaseAgent inheritance | [MISSING] - No heal() method | [INVALID] | Concrete | 27.0 | ISSUES 3 |
| BiasAuditorAgent | Unknown | agentic_core\runtime\shared_runtime\BiasTypeAgent.py | [BROKEN] - Missing SovereignBaseAgent inheritance | [MISSING] - No heal() method | [INVALID] | Concrete | 10.0 | ISSUES 3 |

## Critical Issues Requiring Immediate Attention

### CRITICAL: RootCustomsAgent (L0)
**File:** `agentic_core\L0_maintenance\logs\RoutingDecisionAgent.py`
**Issues:** Missing SovereignBaseAgent inheritance, Missing heal() method, Invalid namespace/location, Broken import dependencies
**Recommendations:** Add SovereignBaseAgent to class inheritance, Implement heal(self, violation: dict) -> dict method, Move agent to proper directory per structure blueprint, Fix import statements and dependencies

### CRITICAL: RootCustomsAgent (L0)
**File:** `agentic_core\L0_maintenance\scripts\RoutingDecisionAgent.py`
**Issues:** Missing SovereignBaseAgent inheritance, Missing heal() method, Invalid namespace/location, Broken import dependencies
**Recommendations:** Add SovereignBaseAgent to class inheritance, Implement heal(self, violation: dict) -> dict method, Move agent to proper directory per structure blueprint, Fix import statements and dependencies

### CRITICAL: SubAtomicAgent (L2)
**File:** `agentic_core\L2_execution\tool_registry\BaseToolAgent.py`
**Issues:** Missing SovereignBaseAgent inheritance, Missing heal() method, Invalid namespace/location, Broken import dependencies
**Recommendations:** Add SovereignBaseAgent to class inheritance, Implement heal(self, violation: dict) -> dict method, Move agent to proper directory per structure blueprint, Fix import statements and dependencies

### CRITICAL: BaseAgent (L2)
**File:** `agentic_core\L2_execution\tool_registry\BaseToolAgent.py`
**Issues:** Missing SovereignBaseAgent inheritance, Missing heal() method, Invalid namespace/location, Broken import dependencies
**Recommendations:** Add SovereignBaseAgent to class inheritance, Implement heal(self, violation: dict) -> dict method, Move agent to proper directory per structure blueprint, Fix import statements and dependencies

### CRITICAL: BaseAgent (L3)
**File:** `agentic_core\L3_orchestration\workflow_engines\DomainPlannerAgent.py`
**Issues:** Missing SovereignBaseAgent inheritance, Missing heal() method, Invalid namespace/location
**Recommendations:** Add SovereignBaseAgent to class inheritance, Implement heal(self, violation: dict) -> dict method, Move agent to proper directory per structure blueprint

### CRITICAL: DiscoveredAgent (Unknown)
**File:** `agentic_core\DiscoveredAgent.py`
**Issues:** Missing SovereignBaseAgent inheritance, Missing heal() method, Invalid namespace/location
**Recommendations:** Add SovereignBaseAgent to class inheritance, Implement heal(self, violation: dict) -> dict method, Move agent to proper directory per structure blueprint

### CRITICAL: BiasAuditorAgent (Unknown)
**File:** `agentic_core\runtime\shared_runtime\BiasTypeAgent.py`
**Issues:** Missing SovereignBaseAgent inheritance, Missing heal() method, Invalid namespace/location
**Recommendations:** Add SovereignBaseAgent to class inheritance, Implement heal(self, violation: dict) -> dict method, Move agent to proper directory per structure blueprint
