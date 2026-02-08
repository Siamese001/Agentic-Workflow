# Final Legacy Migration Disposition Report

## 1. Disposition Overview

The legacy_archive has been decommissioned. Rescued agents are now live in the apps_lic/engines SSOT.

| Legacy File | Pattern Identified | Target SSOT Agent | Disposition |
| :--- | :--- | :--- | :--- |
| `legacy_market_intel.py` | BioTech/AgriTech Competitors | N/A | **DELETED** |
| `old_stack_analyzer.py` | Mainframe/COBOL Regex | N/A | **DELETED** |
| `CompetitorReconAgent.py` | Rescued & Enriched | `apps_lic/engines/` | **MOVED** |
| `StackModernizationAgent.py` | Rescued & Enriched | `apps_lic/engines/` | **MOVED** |
| `v1_onboarding.py` | Superseded | N/A | **DELETED** |
| `deprecated_orch.py` | Superseded | N/A | **DELETED** |

## 2. Structural Readiness (Gravity Check)

* **DomainPlannerAgent**: STUB removed. Inherits from `BaseAgent`.
* **Post-Purge State**: `legacy_archive` directory removed.
