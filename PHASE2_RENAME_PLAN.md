# Phase 2 Duplicate Resolution Plan

## 11 Duplicate Agent Names Identified

### Apps_RG Agents (Need Rg Prefix):
1. **ResumeOrchestratorAgent** → **RgResumeOrchestratorAgent**
   - File: `apps_rg/engines/resume_engine/ResumeOrchestratorAgent.py`
   
2. **HealingOrchestratorAgent** → **RgHealingOrchestratorAgent**
   - File: `apps_rg/engines/resume_engine/HealingOrchestratorAgent.py`

### Apps_LIC Agents (Need Lic Prefix):
1. **InternalAgent** → **LicInternalAgent**
   - File: `apps_lic/engines/outreach_engine/InternalAgent.py`

2. **OrganizationAgent** → **LicOrganizationAgent**
   - File: `apps_lic/engines/outreach_engine/OrganizationAgent.py`

3. **RecipientAgent** → **LicRecipientAgent**
   - File: `apps_lic/engines/outreach_engine/RecipientAgent.py`

4. **ReflectionAgent** → **LicReflectionAgent**
   - File: `apps_lic/engines/outreach_engine/OutreachReflectionAgent.py` (already has Outreach prefix)

5. **S2_SupervisorAgent** → **LicS2SupervisorAgent**
   - File: `apps_lic/engines/outreach_engine/S2_SupervisorAgent.py`

6. **StrategicPlannerAgent** → **LicStrategicPlannerAgent**
   - File: `apps_lic/engines/outreach_engine/` (need to find exact file)

7. **TemplateOptimizerAgent** → **LicTemplateOptimizerAgent**
   - File: `apps_lic/engines/outreach_engine/TemplateOptimizerAgent.py`

8. **WorkflowOrchestratorAgent** → **LicWorkflowOrchestratorAgent**
   - File: `apps_lic/engines/outreach_engine/WorkflowOrchestratorAgent.py`

9. **HealingOrchestratorAgent** → **LicHealingOrchestratorAgent**
   - File: `apps_lic/engines/outreach_engine/OutreachHealingOrchestratorAgent.py`

10. **CognitiveContractValidatorAgent** → Need to verify location

## Renaming Strategy
1. Rename class definition
2. Rename file
3. Update all imports in apps_rg/ and apps_lic/
4. Leave core agents unchanged (they are the canonical versions)

## L0 Agents Needing L0Agent Inheritance
Based on grep results, these L0 agents currently inherit from other bases:
1. BootstrapAgent - currently inherits from HealerMixin, L0DelegationTestingMixin, MCPHardenedMixin
2. MaintenanceBaseAgent - currently inherits from SovereignBaseAgent
3. (Need to identify remaining 8 from L0_maintenance directory)
