# SSOT Sovereign Health Report

**Compliance Score**: 90.4%
**Total Violations**: 116
**Scan Duration**: 35.69s

## ⚠️ Status: NON-COMPLIANT

Found 116 violations requiring attention.

---

## 1. Gravity Violations (Physical Location)

✅ **No violations** - All agents in correct layers

## 2. Import Violations (Upward Dependencies)

**Count**: 109

| File | Line | Source → Target | Import |
|------|------|-----------------|--------|
| `agentic_core\L1_cognition\thought_engine\query_planner.py` | 10 | LL1 → LL4 | `from agentic_core.L4_state.validation_context.sema...` |
| `agentic_core\L1_cognition\thought_engine\query_planner.py` | 11 | LL1 → LL5 | `from agentic_core.L5_safety.guardrails.subatomic_e...` |
| `agentic_core\L1_cognition\thought_engine\ReasoningMemory.py` | 246 | LL1 → LL4 | `from agentic_core.L4_state.ledger import Ledger...` |
| `agentic_core\L1_cognition\thought_engine\ReasoningMemory.py` | 258 | LL1 → LL4 | `from agentic_core.L4_state.ledger import Ledger...` |
| `agentic_core\L1_cognition\thought_engine\reasoning_memory.py` | 16 | LL1 → LL5 | `from agentic_core.L5_safety.guardrails.mcp_soverei...` |
| `agentic_core\L1_cognition\thought_engine\_LegacyNamingAgent.py` | 11 | LL1 → LL5 | `from agentic_core.L5_safety.guardrails.mcp_hardene...` |
| `agentic_core\L2_execution\ToolRegistry\CartographerAgent.py` | 16 | LL2 → LL5 | `from agentic_core.L5_safety.guardrails.mcp_hardene...` |
| `agentic_core\L2_execution\ToolRegistry\CodeDeduplicationAgent.py` | 65 | LL2 → LL5 | `from agentic_core.L5_safety.guardrails.mcp_hardene...` |
| `agentic_core\L2_execution\ToolRegistry\CodeJanitorAgent.py` | 31 | LL2 → LL5 | `from agentic_core.L5_safety.guardrails.mcp_hardene...` |
| `agentic_core\L2_execution\ToolRegistry\deepwiki_client_sovereign.py` | 13 | LL2 → LL3 | `from agentic_core.L3_orchestration.workflow_engine...` |
| ... and 99 more | | | |

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

- **Total Agents**: 302
- **Files Scanned**: 3042
- **Gravity Violations**: 0
- **Import Violations**: 109
- **Hierarchy Violations**: 6
- **Drift Violations**: 1
- **Compliance Score**: 90.4%