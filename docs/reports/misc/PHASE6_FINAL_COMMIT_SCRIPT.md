# Phase 6 Final Commit Script

## Issue
Pre-commit hooks are failing on files we didn't modify (apps_lic files with pre-existing errors).

## Solution
Commit ONLY the Phase 6 files we actually fixed.

## Files to Commit (Phase 6 Only)

### Core Import Fixes
```bash
git add apps_rg/domain/__init__.py
git add apps_rg/domain/config/__init__.py
git add apps_rg/shared/reasoning/__init__.py
git add apps_rg/shared/mixins.py
git add apps_rg/shared/core/StateTransaction.py
git add apps_rg/shared/core/mixins.py
git add apps_rg/shared/core/TraceRegistry.py
git add apps_rg/logic_nodes/__init__.py
git add apps_rg/logic_nodes/RGFlowRouter.py
```

### Engine Files (Import + Linting Fixes)
```bash
git add apps_rg/engines/__init__.py
git add apps_rg/engines/AgentExecutor.py
git add apps_rg/engines/AllProvidersDownError.py
git add apps_rg/engines/ATSCompatibilityAgent.py
git add apps_rg/engines/BrandComplianceAgent.py
git add apps_rg/engines/CampaignPlannerAgent.py
git add apps_rg/engines/ContentQualityAgent.py
git add apps_rg/engines/ContentStrategyAgent.py
git add apps_rg/engines/ExecutiveSummaryOutputAgent.py
git add apps_rg/engines/FactCheckAgent.py
git add apps_rg/engines/HeadlineOutputAgent.py
git add apps_rg/engines/ProactiveAgent.py
git add apps_rg/engines/RgHealingOrchestratorAgent.py
git add apps_rg/engines/RgReflectionAgent.py
git add apps_rg/engines/RgResumeOrchestratorAgent.py
git add apps_rg/engines/RgStrategicPlannerAgent.py
git add apps_rg/engines/RgTemplateOptimizerAgent.py
git add apps_rg/engines/SectionBalanceAgent.py
git add apps_rg/engines/base/BaseRGEngine.py
```

### Base Agents
```bash
git add agentic_core/base_agents/TokenLimitError.py
```

### Tests
```bash
git add tests/e2e/ops_scripts/test_lic_rg_parity.py
```

### Documentation
```bash
git add docs/reports/PHASE6_IMPORT_ANALYSIS.md
git add docs/reports/PHASE6_PROGRESS_SUMMARY.md
```

## Commit Command
```bash
git commit -m "Phase 6: Fix import issues and linting errors

Fixed 30 files with proper architecture:
- Module name mismatches resolved
- Circular dependency broken with apps_rg/shared/mixins.py
- MRO conflicts fixed
- All linting errors resolved in modified files

Test results: 2/6 passing in test_lic_rg_parity.py"
```
