# Autonomy Compliance Report

**Generated:** January 03, 2026  
**Source:** `agent_discovery_full.json` (canonical AST scan)

## 🎯 Executive Summary

**System Health:** 29.6/100 | **Risk Level:** HIGH | **Criticality:** 100/100

### Key Metrics
- **Total Agents:** 435
- **Compliant:** 177 (40.7%) ❌
- **Healing Capabilities:** 278 (63.9%) ⚠️
- **Healing Invocation:** 63 (14.5%) ❌
- **With Tests:** 171 (39.3%) ❌
- **Avg Complexity:** 42.9 ❌

## 📊 Territory Analysis

**Note:** Table data available in CSV format for better readability in spreadsheet tools.

### High Priority Territories (Criticality > 70)

### High Priority Territories

- 🔥 **L5 Safety/Validators**: 12/19 compliant | Health: 52.6% | Risk: HIGH | Heal Gap: 52.6%
- 🔥 **L1 Cognition/Intent Analysis**: 9/50 compliant | Health: 31.3% | Risk: HIGH | Heal Gap: 66.0%
- 🔥 **L1 Cognition/Thought Engine**: 9/50 compliant | Health: 31.3% | Risk: HIGH | Heal Gap: 66.0%
- 🔥 **L0 Maintenance**: 5/24 compliant | Health: 38.9% | Risk: HIGH | Heal Gap: 87.5%
- 🔥 **L2 Execution/Action Handlers**: 27/83 compliant | Health: 42.2% | Risk: HIGH | Heal Gap: 61.4%
- 🔥 **L2 Execution/Mcp**: 27/83 compliant | Health: 42.2% | Risk: HIGH | Heal Gap: 61.4%
- 🔥 **L5 Safety/Guardrails**: 28/37 compliant | Health: 34.2% | Risk: HIGH | Heal Gap: 67.6%

### Medium Priority Territories

- 🔥 **Apps Lic/Domain**: 11/47 compliant | Health: 29.1% | Risk: HIGH | Heal Gap: 57.5%
- 🔥 **Apps Lic/Engines**: 11/47 compliant | Health: 29.1% | Risk: HIGH | Heal Gap: 57.5%
- 🔥 **Apps Lic/Core**: 11/47 compliant | Health: 29.1% | Risk: HIGH | Heal Gap: 57.5%
- 🔥 **Apps Rg/Domain**: 5/40 compliant | Health: 45.0% | Risk: HIGH | Heal Gap: 42.5%
- 🔥 **Apps Rg/Engines**: 5/40 compliant | Health: 45.0% | Risk: HIGH | Heal Gap: 42.5%
- 🔥 **Apps Shared**: 0/4 compliant | Health: 16.7% | Risk: HIGH | Heal Gap: 100.0%
- 🔥 **L3 Orchestration/Workflow Engines**: 30/62 compliant | Health: 54.3% | Risk: HIGH | Heal Gap: 62.9%
- 🔥 **L3 Orchestration/Meta Learning**: 30/62 compliant | Health: 54.3% | Risk: HIGH | Heal Gap: 62.9%
- ⚠️ **L5 Safety/Gravity**: 2/2 compliant | Health: 50.0% | Risk: MED | Heal Gap: 50.0%
- 🔥 **L5 Safety/Red Teaming**: 1/1 compliant | Health: 66.7% | Risk: HIGH
- 🔥 **L4 State/Validationcontext**: 10/21 compliant | Health: 50.8% | Risk: HIGH | Heal Gap: 61.9%
- 🔥 **L4 State/Validation Context**: 10/21 compliant | Health: 50.8% | Risk: HIGH | Heal Gap: 61.9%

### Low Priority Territories

- 🔥 **Tests**: 0/19 compliant | Health: 49.1% | Risk: HIGH | Heal Gap: 36.8%
- 🔥 **Utils/Core Extensions**: 0/7 compliant | Health: 33.3% | Risk: HIGH | Heal Gap: 42.9%
- 🔥 **Utils/General Helpers**: 0/7 compliant | Health: 33.3% | Risk: HIGH | Heal Gap: 42.9%

### Unclassified Agents

- ❓ **Unclassified**: 24/90 compliant | Health: 38.9% | Risk: HIGH | Heal Gap: 51.1%


## 📈 Recommendations

### Immediate Actions (High Risk)
- **L5 Safety/Validators**: Focus on complexity reduction (CC=40.1) and test coverage
- **L5 Safety/Guardrails**: Focus on complexity reduction (CC=40.1) and test coverage
- **L2 Execution/Action Handlers**: Focus on complexity reduction (CC=40.1) and test coverage
- **L2 Execution/Mcp**: Focus on complexity reduction (CC=40.1) and test coverage
- **L1 Cognition/Intent Analysis**: Focus on complexity reduction (CC=40.1) and test coverage
- **L1 Cognition/Thought Engine**: Focus on complexity reduction (CC=40.1) and test coverage
- **L0 Maintenance**: Focus on complexity reduction (CC=40.1) and test coverage
- **L5 Safety/Red Teaming**: Focus on complexity reduction (CC=40.1) and test coverage
- **L4 State/Validationcontext**: Focus on complexity reduction (CC=40.1) and test coverage
- **L4 State/Validation Context**: Focus on complexity reduction (CC=40.1) and test coverage
- **L3 Orchestration/Workflow Engines**: Focus on complexity reduction (CC=40.1) and test coverage
- **L3 Orchestration/Meta Learning**: Focus on complexity reduction (CC=40.1) and test coverage
- **Apps Lic/Domain**: Focus on complexity reduction (CC=40.1) and test coverage
- **Apps Lic/Engines**: Focus on complexity reduction (CC=40.1) and test coverage
- **Apps Lic/Core**: Focus on complexity reduction (CC=40.1) and test coverage
- **Apps Rg/Domain**: Focus on complexity reduction (CC=40.1) and test coverage
- **Apps Rg/Engines**: Focus on complexity reduction (CC=40.1) and test coverage
- **Apps Shared**: Focus on complexity reduction (CC=40.1) and test coverage

### Healing Gap Closure
- **Apps Shared**: Add heal_repository() methods (Gap: 100.0%)
- **L0 Maintenance**: Add heal_repository() methods (Gap: 87.5%)
- **L5 Safety/Guardrails**: Add heal_repository() methods (Gap: 67.6%)
- **L1 Cognition/Intent Analysis**: Add heal_repository() methods (Gap: 66.0%)
- **L1 Cognition/Thought Engine**: Add heal_repository() methods (Gap: 66.0%)
- **L3 Orchestration/Workflow Engines**: Add heal_repository() methods (Gap: 62.9%)
- **L3 Orchestration/Meta Learning**: Add heal_repository() methods (Gap: 62.9%)
- **L4 State/Validationcontext**: Add heal_repository() methods (Gap: 61.9%)
- **L4 State/Validation Context**: Add heal_repository() methods (Gap: 61.9%)
- **L2 Execution/Action Handlers**: Add heal_repository() methods (Gap: 61.4%)
- **L2 Execution/Mcp**: Add heal_repository() methods (Gap: 61.4%)
- **Apps Lic/Domain**: Add heal_repository() methods (Gap: 57.5%)
- **Apps Lic/Engines**: Add heal_repository() methods (Gap: 57.5%)
- **Apps Lic/Core**: Add heal_repository() methods (Gap: 57.5%)
- **L5 Safety/Validators**: Add heal_repository() methods (Gap: 52.6%)
- **L5 Safety/Gravity**: Add heal_repository() methods (Gap: 50.0%)
- **Apps Rg/Domain**: Add heal_repository() methods (Gap: 42.5%)
- **Apps Rg/Engines**: Add heal_repository() methods (Gap: 42.5%)


## 📊 Data Files

- **Detailed CSV**: `reports/autonomy_compliance_data.csv` (open in Excel/Sheets)
- **Summary Report**: This markdown file

---
*Report generated by AutonomyGuardianAgent | January 03, 2026*
