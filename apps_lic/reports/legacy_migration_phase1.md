# Legacy Archive Disposition Report (Phase 1)

## 1. Disposition Overview

The following files in `C:\Git\Agentic-Workflow\apps_lic\legacy_archive` have been analyzed for logic extraction and disposition.

| Legacy File | Pattern Identified | Target SSOT Agent | Disposition |
| :--- | :--- | :--- | :--- |
| `legacy_market_intel.py` | Logic Extracted to CompetitorRecon | `legacy_archive` | **READY FOR DELETION** |
| `old_stack_analyzer.py` | Logic Extracted to StackModernization | `legacy_archive` | **READY FOR DELETION** |
| `CompetitorReconAgent.py` | Rescued & Enriched | `apps_lic/agents/` | **MOVED** |
| `StackModernizationAgent.py` | Rescued & Enriched | `apps_lic/agents/` | **MOVED** |
| `v1_onboarding.py` | Outdated 30-60-90 logic | `OnboardingPlannerAgent.py` | **Delete** (Superseded) |
| `deprecated_orch.py` | Linear loops | `HOPOrchestratorAgent.py` | **Delete** (Superseded) |

## 2. Structural Readiness (Gravity Check)

* **DomainPlannerAgent**: STUB removed. Ready for logic injection.
* **CompetitorReconAgent**: Requires extraction of `MockIntelProvider` to support legacy data injection.
* **StackModernizationAgent**: Ready for regex pattern expansion.

## 3. Migration Logic (Phase 2 Preview)

* **Extraction**: We will parse `legacy_market_intel.py` to extract the `biotech` and `agritech` competitor dictionaries.
* **Extraction**: We will parse `old_stack_analyzer.py` to extract `cobol` and `db2` detection patterns.

## 4. Testing Strategy

All merges must pass the `tests/migration_integrity_test.py` suite (created in Phase 1) before deletion is authorized.
