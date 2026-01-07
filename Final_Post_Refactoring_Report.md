# SSOT Sovereign Health Report

**Compliance Score**: 89.6%
**Total Violations**: 126
**Scan Duration**: 43.99s

## ⚠️ Status: NON-COMPLIANT

Found 126 violations requiring attention.

---

## 1. Gravity Violations (Physical Location)

✅ **No violations** - All agents in correct layers

## 2. Import Violations (Upward Dependencies)

**Count**: 119

| File | Line | Source → Target | Import |
|------|------|-----------------|--------|
| `agentic_core\L0_maintenance\scripts\l0_delegation_testing_mixin.py` | 93 | LL0 → LL5 | `from agentic_core.L5_safety.gravity import Gravity...` |
| `agentic_core\L0_maintenance\scripts\MaintenanceBaseAgent.py` | 118 | LL0 → LL5 | `from agentic_core.L5_safety.validators.TestSoverei...` |
| `agentic_core\L0_maintenance\scripts\MaintenanceBaseAgent.py` | 138 | LL0 → LL5 | `from agentic_core.L5_safety.validators.TestSoverei...` |
| `agentic_core\L0_maintenance\scripts\sovereign_rescue_review.py` | 11 | LL0 → LL4 | `from agentic_core.L4_state.vector.PineconeSovereig...` |
| `agentic_core\L0_maintenance\scripts\sovereign_rescue_review.py` | 12 | LL0 → LL4 | `from agentic_core.L4_state.cache.redis_sovereign_a...` |
| `agentic_core\L0_maintenance\scripts\sovereign_rescue_review.py` | 13 | LL0 → LL4 | `from agentic_core.L4_state.vector.PineconeSovereig...` |
| `agentic_core\L1_cognition\thought_engine\CognitiveContractValidatorAgent.py` | 17 | LL1 → LL5 | `from agentic_core.L5_safety.guardrails.mcp_hardene...` |
| `agentic_core\L1_cognition\thought_engine\L1Agent.py` | 16 | LL1 → LL5 | `from agentic_core.L5_safety.guardrails.mcp_hardene...` |
| `agentic_core\L1_cognition\thought_engine\PrintStatementValidatorAgent.py` | 10 | LL1 → LL5 | `from agentic_core.L5_safety.guardrails.mcp_hardene...` |
| `agentic_core\L1_cognition\thought_engine\query_planner.py` | 10 | LL1 → LL4 | `from agentic_core.L4_state.validation_context.sema...` |
| ... and 109 more | | | |

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

- **Total Agents**: 303
- **Files Scanned**: 3040
- **Gravity Violations**: 0
- **Import Violations**: 119
- **Hierarchy Violations**: 6
- **Drift Violations**: 1
- **Compliance Score**: 89.6%