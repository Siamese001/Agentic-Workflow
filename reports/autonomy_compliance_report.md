# Autonomy Compliance Report

**Generated:** January 05, 2026  
**Source:** `agent_discovery_full.json` (canonical AST scan)

## 🎯 Executive Summary

**System Health:** 46.2/100 | **Risk Level:** MED | **Criticality:** 100/100

### Key Metrics
- **Total Agents:** 318
- **Compliant:** 285 (89.6%) ✅
- **Healing Capabilities:** 285 (89.6%) ✅
- **Healing Invocation:** 142 (44.7%) ❌
- **With Tests:** 296 (93.1%) ✅
- **Avg Complexity:** 35.1 ❌

## 📊 Territory Analysis

**Note:** Table data available in CSV format for better readability in spreadsheet tools.

### High Priority Territories (Criticality > 70)

### High Priority Territories

- 🔥 **L2 Execution/Core**: 27/69 compliant | Health: 76.8% | Risk: HIGH | Heal Gap: 56.5%
- 🔥 **L1 Cognition/Core**: 3/14 compliant | Health: 73.8% | Risk: HIGH | Heal Gap: 71.5%
- 🔥 **Apps Rg**: 3/24 compliant | Health: 62.5% | Risk: HIGH | Heal Gap: 87.5%
- ⚠️ **L5 Safety/Guardrails**: 27/31 compliant | Health: 91.4% | Risk: MED
- 🔥 **Apps Lic**: 10/33 compliant | Health: 48.5% | Risk: HIGH | Heal Gap: 69.7%

### Medium Priority Territories

- 🔥 **L5 Safety/Validators**: 15/19 compliant | Health: 91.2% | Risk: HIGH | Heal Gap: 15.8%
- 🔥 **L0 Maintenance/Infrastructure**: 0/3 compliant | Health: 55.6% | Risk: HIGH | Heal Gap: 66.7%
- 🔥 **L3 Orchestration/Specialized**: 0/5 compliant | Health: 66.7% | Risk: HIGH | Heal Gap: 40.0%
- 🔥 **L1 Cognition/Specialized**: 0/3 compliant | Health: 55.6% | Risk: HIGH | Heal Gap: 33.3%
- 🔥 **Observability/Metrics**: 2/12 compliant | Health: 72.2% | Risk: HIGH | Heal Gap: 50.0%
- ⚠️ **L5 Safety/Red Teaming**: 6/6 compliant | Health: 100.0% | Risk: MED
- ⚠️ **L5 Safety/Base Class**: 2/2 compliant | Health: 83.3% | Risk: MED
- ⚠️ **L5 Safety/Gravity**: 2/2 compliant | Health: 100.0% | Risk: MED
- 🔥 **L3 Orchestration/Core**: 22/41 compliant | Health: 74.8% | Risk: HIGH | Heal Gap: 53.7%
- 🔥 **L2 Execution/Specialized**: 2/4 compliant | Health: 83.3% | Risk: HIGH | Heal Gap: 50.0%
- 🔥 **L4 State/Core**: 5/12 compliant | Health: 63.9% | Risk: HIGH | Heal Gap: 58.3%
- 🔥 **L4 State/Infrastructure**: 1/3 compliant | Health: 77.8% | Risk: HIGH | Heal Gap: 33.3%
- ⚠️ **L1 Cognition/Base Class**: 1/1 compliant | Health: 100.0% | Risk: MED
- 🔥 **Apps Shared**: 0/2 compliant | Health: 33.3% | Risk: HIGH | Heal Gap: 100.0%
- ⚠️ **L2 Execution/Base Class**: 1/1 compliant | Health: 100.0% | Risk: MED
- 🔥 **L0 Maintenance/Core**: 0/6 compliant | Health: 66.7% | Risk: HIGH | Heal Gap: 100.0%
- 🔥 **L4 State/Specialized**: 3/5 compliant | Health: 80.0% | Risk: HIGH | Heal Gap: 20.0%
- ⚠️ **L3 Orchestration/Infrastructure**: 2/2 compliant | Health: 83.3% | Risk: MED
- ⚠️ **L3 Orchestration/Base Class**: 1/1 compliant | Health: 100.0% | Risk: MED
- ⚠️ **Observability/Telemetry**: 1/1 compliant | Health: 100.0% | Risk: MED
- ⚠️ **Observability/Tracing**: 1/1 compliant | Health: 100.0% | Risk: MED
- ⚠️ **Observability/Compliance**: 1/1 compliant | Health: 100.0% | Risk: MED

### Low Priority Territories

- ⚠️ **L4 State/Base Class**: 1/1 compliant | Health: 100.0% | Risk: MED
- 🔥 **L1 Cognition/Infrastructure**: 0/8 compliant | Health: 33.3% | Risk: HIGH | Heal Gap: 100.0%
- 🔥 **L2 Execution/Infrastructure**: 0/2 compliant | Health: 33.3% | Risk: HIGH | Heal Gap: 100.0%
- 🔥 **Tests**: 0/3 compliant | Health: 66.7% | Risk: HIGH


## 📈 Recommendations

### Immediate Actions (High Risk)
- **L2 Execution/Core**: Focus on complexity reduction (CC=31.0) and test coverage
- **L1 Cognition/Core**: Focus on complexity reduction (CC=31.0) and test coverage
- **Apps Lic**: Focus on complexity reduction (CC=31.0) and test coverage
- **Apps Rg**: Focus on complexity reduction (CC=31.0) and test coverage
- **L5 Safety/Validators**: Focus on complexity reduction (CC=31.0) and test coverage
- **L4 State/Core**: Focus on complexity reduction (CC=31.0) and test coverage
- **L4 State/Infrastructure**: Focus on complexity reduction (CC=31.0) and test coverage
- **L4 State/Specialized**: Focus on complexity reduction (CC=31.0) and test coverage
- **L3 Orchestration/Core**: Focus on complexity reduction (CC=31.0) and test coverage
- **L3 Orchestration/Specialized**: Focus on complexity reduction (CC=31.0) and test coverage
- **L2 Execution/Specialized**: Focus on complexity reduction (CC=31.0) and test coverage
- **L1 Cognition/Specialized**: Focus on complexity reduction (CC=31.0) and test coverage
- **L0 Maintenance/Core**: Focus on complexity reduction (CC=31.0) and test coverage
- **L0 Maintenance/Infrastructure**: Focus on complexity reduction (CC=31.0) and test coverage
- **Observability/Metrics**: Focus on complexity reduction (CC=31.0) and test coverage
- **Apps Shared**: Focus on complexity reduction (CC=31.0) and test coverage

### Healing Gap Closure
- **L0 Maintenance/Core**: Add heal_repository() methods (Gap: 100.0%)
- **Apps Shared**: Add heal_repository() methods (Gap: 100.0%)
- **Apps Rg**: Add heal_repository() methods (Gap: 87.5%)
- **L1 Cognition/Core**: Add heal_repository() methods (Gap: 71.5%)
- **Apps Lic**: Add heal_repository() methods (Gap: 69.7%)
- **L0 Maintenance/Infrastructure**: Add heal_repository() methods (Gap: 66.7%)
- **L4 State/Core**: Add heal_repository() methods (Gap: 58.3%)
- **L2 Execution/Core**: Add heal_repository() methods (Gap: 56.5%)
- **L3 Orchestration/Core**: Add heal_repository() methods (Gap: 53.7%)
- **L2 Execution/Specialized**: Add heal_repository() methods (Gap: 50.0%)
- **Observability/Metrics**: Add heal_repository() methods (Gap: 50.0%)
- **L3 Orchestration/Specialized**: Add heal_repository() methods (Gap: 40.0%)
- **L4 State/Infrastructure**: Add heal_repository() methods (Gap: 33.3%)
- **L1 Cognition/Specialized**: Add heal_repository() methods (Gap: 33.3%)
- **L4 State/Specialized**: Add heal_repository() methods (Gap: 20.0%)
- **L5 Safety/Validators**: Add heal_repository() methods (Gap: 15.8%)


## 📊 Data Files

- **Detailed CSV**: `reports/autonomy_compliance_data.csv` (open in Excel/Sheets)
- **Summary Report**: This markdown file

---
*Report generated by AutonomyGuardianAgent | January 05, 2026*
