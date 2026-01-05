# Autonomy Compliance Report

**Generated:** January 05, 2026  
**Source:** `agent_discovery_full.json` (canonical AST scan)

## 🎯 Executive Summary

**System Health:** 71.1/100 | **Risk Level:** HIGH | **Criticality:** 100/100

### Key Metrics
- **Total Agents:** 313
- **Compliant:** 161 (51.4%) ❌
- **Healing Capabilities:** 300 (95.8%) ✅
- **Healing Invocation:** 155 (49.5%) ❌
- **With Tests:** 295 (94.2%) ✅
- **Avg Complexity:** 59.0 ❌

## 📊 Territory Analysis

**Note:** Table data available in CSV format for better readability in spreadsheet tools.

### High Priority Territories (Criticality > 70)

### High Priority Territories

- 🔥 **L2 Execution/Core**: 26/69 compliant | Health: 76.3% | Risk: HIGH | Heal Gap: 58.0%
- 🔥 **L1 Cognition/Core**: 3/14 compliant | Health: 73.8% | Risk: HIGH | Heal Gap: 78.6%
- 🔥 **Apps Rg**: 3/24 compliant | Health: 62.5% | Risk: HIGH | Heal Gap: 87.5%
- 🔥 **Apps Lic**: 10/33 compliant | Health: 48.5% | Risk: HIGH | Heal Gap: 69.7%

### Medium Priority Territories

- ⚠️ **L5 Safety/Validators**: 16/20 compliant | Health: 95.0% | Risk: MED
- ⚠️ **L5 Safety/Guardrails**: 26/30 compliant | Health: 94.4% | Risk: MED
- 🔥 **L0 Maintenance/Infrastructure**: 0/3 compliant | Health: 55.6% | Risk: HIGH | Heal Gap: 66.7%
- 🔥 **L3 Orchestration/Specialized**: 0/5 compliant | Health: 80.0% | Risk: HIGH
- 🔥 **L1 Cognition/Specialized**: 0/3 compliant | Health: 55.6% | Risk: HIGH | Heal Gap: 33.3%
- 🔥 **Observability/Metrics**: 2/12 compliant | Health: 80.6% | Risk: HIGH | Heal Gap: 33.3%
- ⚠️ **L5 Safety/Red Teaming**: 6/6 compliant | Health: 100.0% | Risk: MED
- 🔥 **L3 Orchestration/Core**: 22/40 compliant | Health: 81.7% | Risk: HIGH | Heal Gap: 35.0%
- ⚠️ **L5 Safety/Gravity**: 2/2 compliant | Health: 100.0% | Risk: MED
- 🔥 **L2 Execution/Specialized**: 2/4 compliant | Health: 83.3% | Risk: HIGH | Heal Gap: 50.0%
- 🔥 **L4 State/Core**: 5/12 compliant | Health: 66.7% | Risk: HIGH | Heal Gap: 50.0%
- 🔥 **L4 State/Infrastructure**: 1/3 compliant | Health: 77.8% | Risk: HIGH | Heal Gap: 33.3%
- ⚠️ **L1 Cognition/Base Class**: 1/1 compliant | Health: 66.7% | Risk: MED | Heal Gap: 100.0%
- 🔥 **Apps Shared**: 0/2 compliant | Health: 50.0% | Risk: HIGH | Heal Gap: 50.0%
- ⚠️ **L2 Execution/Base Class**: 1/1 compliant | Health: 100.0% | Risk: MED
- 🔥 **L0 Maintenance/Core**: 0/6 compliant | Health: 66.7% | Risk: HIGH | Heal Gap: 100.0%
- 🔥 **L4 State/Specialized**: 3/5 compliant | Health: 80.0% | Risk: HIGH | Heal Gap: 20.0%
- ⚠️ **L3 Orchestration/Infrastructure**: 2/2 compliant | Health: 83.3% | Risk: MED
- ⚠️ **Observability/Telemetry**: 1/1 compliant | Health: 100.0% | Risk: MED
- ⚠️ **Observability/Tracing**: 1/1 compliant | Health: 100.0% | Risk: MED
- ⚠️ **Observability/Compliance**: 1/1 compliant | Health: 100.0% | Risk: MED

### Low Priority Territories

- 🔥 **L1 Cognition/Infrastructure**: 0/8 compliant | Health: 33.3% | Risk: HIGH | Heal Gap: 100.0%
- 🔥 **L2 Execution/Infrastructure**: 0/2 compliant | Health: 33.3% | Risk: HIGH | Heal Gap: 100.0%
- 🔥 **Tests**: 0/3 compliant | Health: 66.7% | Risk: HIGH


## 📈 Recommendations

### Immediate Actions (High Risk)
- **L2 Execution/Core**: Focus on complexity reduction (CC=31.0) and test coverage
- **L1 Cognition/Core**: Focus on complexity reduction (CC=31.0) and test coverage
- **Apps Lic**: Focus on complexity reduction (CC=31.0) and test coverage
- **Apps Rg**: Focus on complexity reduction (CC=31.0) and test coverage
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
- **L1 Cognition/Base Class**: Add heal_repository() methods (Gap: 100.0%)
- **L0 Maintenance/Core**: Add heal_repository() methods (Gap: 100.0%)
- **Apps Rg**: Add heal_repository() methods (Gap: 87.5%)
- **L1 Cognition/Core**: Add heal_repository() methods (Gap: 78.6%)
- **Apps Lic**: Add heal_repository() methods (Gap: 69.7%)
- **L0 Maintenance/Infrastructure**: Add heal_repository() methods (Gap: 66.7%)
- **L2 Execution/Core**: Add heal_repository() methods (Gap: 58.0%)
- **L4 State/Core**: Add heal_repository() methods (Gap: 50.0%)
- **L2 Execution/Specialized**: Add heal_repository() methods (Gap: 50.0%)
- **Apps Shared**: Add heal_repository() methods (Gap: 50.0%)
- **L3 Orchestration/Core**: Add heal_repository() methods (Gap: 35.0%)
- **L4 State/Infrastructure**: Add heal_repository() methods (Gap: 33.3%)
- **L1 Cognition/Specialized**: Add heal_repository() methods (Gap: 33.3%)
- **Observability/Metrics**: Add heal_repository() methods (Gap: 33.3%)
- **L4 State/Specialized**: Add heal_repository() methods (Gap: 20.0%)


## 📊 Data Files

- **Detailed CSV**: `reports/autonomy_compliance_data.csv` (open in Excel/Sheets)
- **Summary Report**: This markdown file

---
*Report generated by AutonomyGuardianAgent | January 05, 2026*
