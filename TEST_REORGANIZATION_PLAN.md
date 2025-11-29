# Test Folder Reorganization Plan

## Current State Analysis
✅ **COMPLIANT:**
- Unified `/tests/` directory exists
- L1-L5 layer structure in place
- No tests in forbidden locations (apps/, engine/)

⚠️ **NEEDS REORGANIZATION:**
- Tests nested in subdirectories instead of layer-level files
- Missing engine-specific naming convention
- Structure doesn't match Windsurf Rules.md illustrated examples

## Target Structure (from Windsurf Rules.md)

```
/tests
├── L1_planning/
│   ├── test_resume_planner.py
│   ├── test_resume_refinement_planner.py
│   ├── test_outreach_planner.py
│   ├── test_outreach_archetype_planner.py
│   └── test_outreach_research_planner.py
├── L2_execution/
│   ├── test_resume_rag_executor.py
│   ├── test_resume_company_research_executor.py
│   ├── test_resume_skill_extraction_executor.py
│   ├── test_outreach_company_research_executor.py
│   ├── test_outreach_contact_research_executor.py
│   └── test_outreach_message_generation_executor.py
├── L3_orchestration/
│   ├── test_resume_orchestrator.py
│   ├── test_resume_workflow_graph.py
│   ├── test_outreach_orchestrator.py
│   └── test_outreach_workflow_graph.py
├── L4_state/
│   ├── test_resume_state_manager.py
│   ├── test_outreach_state_manager.py
│   ├── test_temporal_agent.py
│   ├── test_temporal_kg.py
│   ├── test_entity_resolution.py
│   └── test_rag_memory_providers.py
├── L5_safety/
│   ├── test_resume_safety_validator.py
│   ├── test_outreach_safety_validator.py
│   ├── test_policy_engine.py
│   └── test_guardrails.py
└── [existing integration/, e2e/, unit/, etc.]
```

## Reorganization Steps

### Phase 1: Move Tests to Layer Level
1. Move tests from `L1_planning/unit/` to `L1_planning/`
2. Move tests from `L2_execution/unit/` to `L2_execution/`
3. Move tests from `L3_orchestration/unit/` to `L3_orchestration/`
4. Move tests from `L4_state/unit/` to `L4_state/`
5. Move tests from `L5_safety/unit/` to `L5_safety/`

### Phase 2: Rename for Engine-Specific Convention
1. Identify resume vs outreach test files
2. Rename following the pattern:
   - `test_archetype_planner_outputs.py` → `test_outreach_archetype_planner.py`
   - `test_company_research_executor.py` → `test_outreach_company_research_executor.py`
   - etc.

### Phase 3: Create Missing Test Files
1. Create placeholder files for missing tests in target structure
2. Add basic test structure with TODO comments

### Phase 4: Update Imports and References
1. Update any import statements that reference old test locations
2. Update pytest configuration if needed
3. Update documentation

## Validation Checklist
- [ ] All tests at layer level (no nested unit/integration subdirs in L1-L5)
- [ ] Engine-specific naming convention applied
- [ ] No tests in forbidden locations
- [ ] All existing test categories preserved
- [ ] Test collection still works
- [ ] No broken imports
