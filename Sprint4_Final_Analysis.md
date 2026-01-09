# SSOT Sovereign Health Report

**Compliance Score**: 99.4%
**Total Violations**: 7
**Scan Duration**: 32.42s

## ⚠️ Status: NON-COMPLIANT

Found 7 violations requiring attention.

---

## 1. Gravity Violations (Physical Location)

✅ **No violations** - All agents in correct layers

## 2. Import Violations (Upward Dependencies)

**Count**: 4

| File | Line | Source → Target | Import |
|------|------|-----------------|--------|
| `agentic_core\L3_orchestration\workflow_engines\NervousSystemAgent.py` | 75 | LL3 → LL5 | `from agentic_core.L5_safety.validators.LocationAge...` |
| `agentic_core\L3_orchestration\workflow_engines\NervousSystemAgent.py` | 80 | LL3 → LL5 | `from agentic_core.L5_safety.guardrails.HierarchyAg...` |
| `agentic_core\L3_orchestration\workflow_engines\NervousSystemAgent.py` | 85 | LL3 → LL5 | `from agentic_core.L5_safety.gravity.ImportAgent im...` |
| `agentic_core\L3_orchestration\workflow_engines\OrchestrationBaseAgent.py` | 312 | LL3 → LL5 | `from agentic_core.L5_safety.validators.TestSoverei...` |

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

- **Total Agents**: 299
- **Files Scanned**: 3050
- **Gravity Violations**: 0
- **Import Violations**: 4
- **Hierarchy Violations**: 2
- **Drift Violations**: 1
- **Compliance Score**: 99.4%