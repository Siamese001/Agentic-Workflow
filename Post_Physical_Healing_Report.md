# SSOT Sovereign Health Report

**Compliance Score**: 88.7%
**Total Violations**: 137
**Scan Duration**: 29.66s

## ⚠️ Status: NON-COMPLIANT

Found 137 violations requiring attention.

---

## 1. Gravity Violations (Physical Location)

✅ **No violations** - All agents in correct layers

## 2. Import Violations (Upward Dependencies)

**Count**: 130

| File | Line | Source → Target | Import |
|------|------|-----------------|--------|
| `agentic_core\L0_maintenance\scripts\auditors_guard_ddd_alignment.py` | 9 | LL0 → LL1 | `from agentic_core.L1_cognition.P2_domain.sovereign...` |
| `agentic_core\L0_maintenance\scripts\BootstrapAgent.py` | 128 | LL0 → LL2 | `from agentic_core.L2_execution.ToolRegistry.Toolsm...` |
| `agentic_core\L0_maintenance\scripts\filesystem_mcp_client.py` | 33 | LL0 → LL3 | `from agentic_core.L3_orchestration.workflow_engine...` |
| `agentic_core\L0_maintenance\scripts\gitkraken_mcp_client.py` | 31 | LL0 → LL3 | `from agentic_core.L3_orchestration.workflow_engine...` |
| `agentic_core\L0_maintenance\scripts\GuardianOrchestratorAgent.py` | 19 | LL0 → LL5 | `from agentic_core.L5_safety.guardrails.mcp_hardene...` |
| `agentic_core\L0_maintenance\scripts\HealingOrchestratorAgent.py` | 21 | LL0 → LL5 | `from agentic_core.L5_safety.guardrails.mcp_hardene...` |
| `agentic_core\L0_maintenance\scripts\healing_vector_healing_strategy.py` | 11 | LL0 → LL4 | `from agentic_core.L4_state.semantic_memory.pinecon...` |
| `agentic_core\L0_maintenance\scripts\L0Agent.py` | 16 | LL0 → LL5 | `from agentic_core.L5_safety.guardrails.mcp_hardene...` |
| `agentic_core\L0_maintenance\scripts\l0_delegation_testing_mixin.py` | 93 | LL0 → LL5 | `from agentic_core.L5_safety.gravity import Gravity...` |
| `agentic_core\L0_maintenance\scripts\l1_health_benchmark.py` | 18 | LL0 → LL1 | `from agentic_core.L1_cognition.cognitive_node.Cogn...` |
| ... and 120 more | | | |

## 3. Hierarchy Violations (Depth Limits)

**Count**: 6

| Folder | Actual Depth | Max Depth | Root |
|--------|--------------|-----------|------|
| `apps_rg\engines\resume_engine\autonomous` | 3 | 2 | apps_rg |
| `apps_rg\engines\resume_engine\autonomous\tests` | 4 | 2 | apps_rg |
| `apps_lic\engines\outreach_engine\autonomous` | 3 | 2 | apps_lic |
| `apps_lic\engines\outreach_engine\hop_agents` | 3 | 2 | apps_lic |
| `apps_lic\engines\outreach_engine\tools` | 3 | 2 | apps_lic |
| `apps_lic\engines\outreach_engine\autonomous\tests` | 4 | 2 | apps_lic |

## 4. Drift Violations (Filesystem vs Blueprint)

**Count**: 1

| Folder | Type | Parent |
|--------|------|--------|
| `agentic_core\L0_maintenance\mixins` | orphaned | L0_maintenance |

---

## Summary Statistics

- **Total Agents**: 304
- **Files Scanned**: 3037
- **Gravity Violations**: 0
- **Import Violations**: 130
- **Hierarchy Violations**: 6
- **Drift Violations**: 1
- **Compliance Score**: 88.7%