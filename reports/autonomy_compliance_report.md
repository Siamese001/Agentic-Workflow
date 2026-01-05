# Autonomy Compliance Report

**Generated:** January 05, 2026  
**Source:** `agent_discovery_full.json` (canonical AST scan)

## 🎯 Executive Summary

**System Health:** 74.0/100 | **Risk Level:** HIGH | **Criticality:** 100/100

### Key Metrics
- **Total Agents:** 252
- **Compliant:** 115 (45.6%) ❌
- **Healing Capabilities:** 190 (75.4%) ⚠️
- **Healing Invocation:** 109 (43.3%) ❌
- **With Tests:** 252 (100.0%) ✅
- **Avg Complexity:** 53.3 ❌

## 📊 Territory Analysis

**Note:** Table data available in CSV format for better readability in spreadsheet tools.

### High Priority Territories (Criticality > 70)

### High Priority Territories

- 🔥 **L0 Maintenance/Infrastructure**: 0/1 compliant | Health: 66.7% | Risk: HIGH
- 🔥 **L2 Execution/Core**: 27/72 compliant | Health: 79.6% | Risk: HIGH | Heal Gap: 54.2%
- 🔥 **L1 Cognition/Core**: 4/16 compliant | Health: 75.0% | Risk: HIGH | Heal Gap: 75.0%
- ⚠️ **L2 Execution/Infrastructure**: 0/1 compliant | Health: 66.7% | Risk: MED | Heal Gap: 100.0%

### Medium Priority Territories

- ⚠️ **L5 Safety/Guardrails**: 21/24 compliant | Health: 98.6% | Risk: MED
- ⚠️ **L5 Safety/Validators**: 13/16 compliant | Health: 97.9% | Risk: MED
- 🔥 **L3 Orchestration/Specialized**: 0/5 compliant | Health: 73.3% | Risk: HIGH | Heal Gap: 20.0%
- ⚠️ **L5 Safety/Red Teaming**: 7/7 compliant | Health: 100.0% | Risk: MED
- 🔥 **Apps Rg**: 4/15 compliant | Health: 66.7% | Risk: HIGH | Heal Gap: 73.3%
- 🔥 **L1 Cognition/Specialized**: 0/7 compliant | Health: 61.9% | Risk: HIGH | Heal Gap: 71.4%
- 🔥 **L2 Execution/Specialized**: 3/7 compliant | Health: 76.2% | Risk: HIGH | Heal Gap: 57.1%
- 🔥 **L0 Maintenance/Core**: 0/4 compliant | Health: 66.7% | Risk: HIGH | Heal Gap: 100.0%
- 🔥 **L4 State/Infrastructure**: 0/4 compliant | Health: 66.7% | Risk: HIGH | Heal Gap: 75.0%
- ⚠️ **L5 Safety/Gravity**: 2/2 compliant | Health: 100.0% | Risk: MED
- 🔥 **Observability/Metrics**: 2/9 compliant | Health: 81.5% | Risk: HIGH | Heal Gap: 22.3%
- 🔥 **Apps Lic**: 10/20 compliant | Health: 78.3% | Risk: HIGH | Heal Gap: 50.0%
- 🔥 **L4 State/Core**: 2/6 compliant | Health: 77.8% | Risk: HIGH | Heal Gap: 50.0%
- 🔥 **L4 State/Specialized**: 2/5 compliant | Health: 80.0% | Risk: HIGH | Heal Gap: 40.0%
- 🔥 **L3 Orchestration/Core**: 10/22 compliant | Health: 81.8% | Risk: HIGH | Heal Gap: 45.4%
- ⚠️ **L1 Cognition/Base Class**: 1/1 compliant | Health: 66.7% | Risk: MED | Heal Gap: 100.0%
- 🔥 **Apps Shared**: 0/2 compliant | Health: 50.0% | Risk: HIGH | Heal Gap: 50.0%
- ⚠️ **Observability/Telemetry**: 1/1 compliant | Health: 100.0% | Risk: MED
- ⚠️ **Observability/Tracing**: 1/1 compliant | Health: 100.0% | Risk: MED
- ⚠️ **Observability/Compliance**: 1/1 compliant | Health: 100.0% | Risk: MED

### Low Priority Territories

- 🔥 **Tests**: 0/3 compliant | Health: 66.7% | Risk: HIGH


## 📈 Recommendations

### Immediate Actions (High Risk)
- **L2 Execution/Core**: Focus on complexity reduction (CC=31.0) and test coverage
- **L1 Cognition/Core**: Focus on complexity reduction (CC=31.0) and test coverage
- **L0 Maintenance/Infrastructure**: Focus on complexity reduction (CC=31.0) and test coverage
- **L4 State/Core**: Focus on complexity reduction (CC=31.0) and test coverage
- **L4 State/Infrastructure**: Focus on complexity reduction (CC=31.0) and test coverage
- **L4 State/Specialized**: Focus on complexity reduction (CC=31.0) and test coverage
- **L3 Orchestration/Core**: Focus on complexity reduction (CC=31.0) and test coverage
- **L3 Orchestration/Specialized**: Focus on complexity reduction (CC=31.0) and test coverage
- **L2 Execution/Specialized**: Focus on complexity reduction (CC=31.0) and test coverage
- **L1 Cognition/Specialized**: Focus on complexity reduction (CC=31.0) and test coverage
- **L0 Maintenance/Core**: Focus on complexity reduction (CC=31.0) and test coverage
- **Observability/Metrics**: Focus on complexity reduction (CC=31.0) and test coverage
- **Apps Lic**: Focus on complexity reduction (CC=31.0) and test coverage
- **Apps Rg**: Focus on complexity reduction (CC=31.0) and test coverage
- **Apps Shared**: Focus on complexity reduction (CC=31.0) and test coverage

### Healing Gap Closure
- **L2 Execution/Infrastructure**: Add heal_repository() methods (Gap: 100.0%)
- **L1 Cognition/Base Class**: Add heal_repository() methods (Gap: 100.0%)
- **L0 Maintenance/Core**: Add heal_repository() methods (Gap: 100.0%)
- **L1 Cognition/Core**: Add heal_repository() methods (Gap: 75.0%)
- **L4 State/Infrastructure**: Add heal_repository() methods (Gap: 75.0%)
- **Apps Rg**: Add heal_repository() methods (Gap: 73.3%)
- **L1 Cognition/Specialized**: Add heal_repository() methods (Gap: 71.4%)
- **L2 Execution/Specialized**: Add heal_repository() methods (Gap: 57.1%)
- **L2 Execution/Core**: Add heal_repository() methods (Gap: 54.2%)
- **L4 State/Core**: Add heal_repository() methods (Gap: 50.0%)
- **Apps Lic**: Add heal_repository() methods (Gap: 50.0%)
- **Apps Shared**: Add heal_repository() methods (Gap: 50.0%)
- **L3 Orchestration/Core**: Add heal_repository() methods (Gap: 45.4%)
- **L4 State/Specialized**: Add heal_repository() methods (Gap: 40.0%)
- **Observability/Metrics**: Add heal_repository() methods (Gap: 22.3%)
- **L3 Orchestration/Specialized**: Add heal_repository() methods (Gap: 20.0%)


## 📊 Data Files

- **Detailed CSV**: `reports/autonomy_compliance_data.csv` (open in Excel/Sheets)
- **Summary Report**: This markdown file

---
*Report generated by AutonomyGuardianAgent | January 05, 2026*
