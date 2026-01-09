# SSOT Sovereign Health Report

**Compliance Score**: 94.9%
**Total Violations**: 62
**Scan Duration**: 32.47s

## ⚠️ Status: NON-COMPLIANT

Found 62 violations requiring attention.

---

## 1. Gravity Violations (Physical Location)

✅ **No violations** - All agents in correct layers

## 2. Import Violations (Upward Dependencies)

**Count**: 59

| File | Line | Source → Target | Import |
|------|------|-----------------|--------|
| `agentic_core\L1_cognition\thought_engine\query_planner.py` | 10 | LL1 → LL4 | `from agentic_core.L4_state.validation_context.sema...` |
| `agentic_core\L1_cognition\thought_engine\query_planner.py` | 11 | LL1 → LL5 | `from agentic_core.L5_safety.guardrails.subatomic_e...` |
| `agentic_core\L1_cognition\thought_engine\ReasoningMemory.py` | 246 | LL1 → LL4 | `from agentic_core.L4_state.ledger import Ledger...` |
| `agentic_core\L1_cognition\thought_engine\ReasoningMemory.py` | 258 | LL1 → LL4 | `from agentic_core.L4_state.ledger import Ledger...` |
| `agentic_core\L1_cognition\thought_engine\reasoning_memory.py` | 16 | LL1 → LL5 | `from agentic_core.L5_safety.guardrails.mcp_soverei...` |
| `agentic_core\L1_cognition\thought_engine\_LegacyNamingAgent.py` | 11 | LL1 → LL5 | `from agentic_core.L5_safety.guardrails.mcp_hardene...` |
| `agentic_core\L2_execution\ToolRegistry\deepwiki_client_sovereign.py` | 13 | LL2 → LL3 | `from agentic_core.L3_orchestration.workflow_engine...` |
| `agentic_core\L2_execution\ToolRegistry\ExecutionCanonBaseAgent.py` | 550 | LL2 → LL5 | `from agentic_core.L5_safety.validators.TestSoverei...` |
| `agentic_core\L2_execution\ToolRegistry\fetch_client_sovereign.py` | 11 | LL2 → LL4 | `from agentic_core.L4_state.semantic.semantic_cache...` |
| `agentic_core\L2_execution\ToolRegistry\fetch_client_sovereign.py` | 12 | LL2 → LL5 | `from agentic_core.L5_safety.guardrails.mcp_soverei...` |
| ... and 49 more | | | |

## 3. Hierarchy Violations (Depth Limits)

**Count**: 2

| Folder | Actual Depth | Max Depth | Root |
|--------|--------------|-----------|------|
| `apps_rg\engines\resume_engine\autonomous\tests` | 4 | 3 | apps_rg |
| `apps_lic\engines\outreach_engine\autonomous\tests` | 4 | 3 | apps_lic |

## 4. Drift Violations (Filesystem vs Blueprint)

**Count**: 1

| Folder | Type | Parent |
|--------|------|--------|
| `agentic_core\L0_maintenance\mixins` | orphaned | L0_maintenance |

---

## Summary Statistics

- **Total Agents**: 302
- **Files Scanned**: 3047
- **Gravity Violations**: 0
- **Import Violations**: 59
- **Hierarchy Violations**: 2
- **Drift Violations**: 1
- **Compliance Score**: 94.9%