# SSOT Sovereign Health Report

**Compliance Score**: 87.7%
**Total Violations**: 151
**Scan Duration**: 31.86s

## ⚠️ Status: NON-COMPLIANT

Found 151 violations requiring attention.

---

## 1. Gravity Violations (Physical Location)

✅ **No violations** - All agents in correct layers

## 2. Import Violations (Upward Dependencies)

**Count**: 131

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
| ... and 121 more | | | |

## 3. Hierarchy Violations (Depth Limits)

**Count**: 12

| Folder | Actual Depth | Max Depth | Root |
|--------|--------------|-----------|------|
| `agentic_core\L0_maintenance\scripts\.github\workflows` | 4 | 3 | agentic_core |
| `agentic_core\L0_maintenance\scripts\runtime\core` | 4 | 3 | agentic_core |
| `agentic_core\L0_maintenance\scripts\schemas\data_assets` | 4 | 3 | agentic_core |
| `agentic_core\L0_maintenance\scripts\schemas\evaluation` | 4 | 3 | agentic_core |
| `apps_rg\engines\resume_engine\autonomous` | 3 | 2 | apps_rg |
| `apps_rg\engines\resume_engine\autonomous\tests` | 4 | 2 | apps_rg |
| `apps_lic\engines\outreach_engine\autonomous` | 3 | 2 | apps_lic |
| `apps_lic\engines\outreach_engine\hop_agents` | 3 | 2 | apps_lic |
| `apps_lic\engines\outreach_engine\planners` | 3 | 2 | apps_lic |
| `apps_lic\engines\outreach_engine\rag` | 3 | 2 | apps_lic |
| ... and 2 more | | | |

## 4. Drift Violations (Filesystem vs Blueprint)

**Count**: 8

| Folder | Type | Parent |
|--------|------|--------|
| `agentic_core\config\validators` | orphaned | config |
| `agentic_core\L0_maintenance\mixins` | orphaned | L0_maintenance |
| `agentic_core\L1_cognition\learning` | orphaned | L1_cognition |
| `agentic_core\L3_orchestration\coordinators` | orphaned | L3_orchestration |
| `agentic_core\L3_orchestration\interfaces` | orphaned | L3_orchestration |
| `agentic_core\L3_orchestration\strategic_recommendation` | orphaned | L3_orchestration |
| `agentic_core\L6_observability` | orphaned | agentic_core |
| `agentic_core\observability\alerting` | orphaned | observability |

---

## Summary Statistics

- **Total Agents**: 307
- **Files Scanned**: 3034
- **Gravity Violations**: 0
- **Import Violations**: 131
- **Hierarchy Violations**: 12
- **Drift Violations**: 8
- **Compliance Score**: 87.7%