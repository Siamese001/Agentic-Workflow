# App File Relocation Plan (SSOT-Aligned)

**Generated:** 2026-01-20
**Status:** Ready for implementation
**SSOT Compliance:** ✅ Verified against `structure_blueprint.py`

---

## Executive Summary

**312 files** in `agentic_core/` are actually app-specific and belong in `apps_rg/`, `apps_lic/`, or `apps_shared/`.

| Category | Files | Destination |
|----------|-------|-------------|
| Resume Engine (apps_rg) | 179 | `apps_rg/engines/` |
| Outreach Engine (apps_lic) | 58 | `apps_lic/engines/` |
| Shared (both apps) | 75 | `apps_shared/` |
| **TOTAL MISPLACED** | **312** | - |

---

## SSOT-Approved Target Structure

### apps_rg (Resume Engine)

```
apps_rg/                        (depth: 2)
├── logic_nodes/
│   ├── node_definitions/
│   └── node_helpers/
├── asset_library/
│   ├── asset_definitions/
│   └── asset_helpers/
├── system_flow/
│   ├── flow_definitions/
│   └── flow_helpers/
├── engines/                    ← PRIMARY TARGET
│   ├── resume_engine/          ← Existing (16 agents)
│   │   ├── ResumeAgent.py
│   │   ├── ATSCompatibilityAgent.py
│   │   ├── ContentQualityAgent.py
│   │   └── ...
│   └── utils/                  ← NEW - thought_engine utilities
│       ├── parse_job_description.py
│       ├── build_skill_query.py
│       ├── calibrate_fit_score.py
│       └── ...
├── templates/
│   ├── template_definitions/
│   └── template_helpers/
└── domain/
```

### apps_lic (Outreach Engine)

```
apps_lic/                       (depth: 2)
├── logic_nodes/
│   ├── node_definitions/
│   └── node_helpers/
├── asset_library/
│   ├── asset_definitions/
│   └── asset_helpers/
├── system_flow/
│   ├── flow_definitions/
│   └── flow_helpers/
├── engines/                    ← PRIMARY TARGET
│   ├── outreach_engine/        ← Existing
│   │   ├── HOP1ProfileAnalysisAgent.py
│   │   ├── HOP2ResearchAgent.py
│   │   ├── CampaignPlannerAgent.py
│   │   └── ...
│   └── utils/                  ← NEW - thought_engine utilities
│       ├── build_message_filters.py
│       ├── calibrate_engagement_score.py
│       ├── optimize_message_structure.py
│       └── ...
├── templates/
│   ├── template_definitions/
│   └── template_helpers/
├── domain/
│   ├── validators/
│   └── models/
└── core/
```

### apps_shared (Shared Utilities)

```
apps_shared/                    (depth: 3)
├── base_definitions/
├── common_utils/               ← Error handling, retries, fallbacks
│   ├── handle_api_timeouts.py
│   ├── handle_service_errors.py
│   ├── implement_fallback_strategy.py
│   ├── retry_generation_failures.py
│   └── ...
├── core_components/            ← LLM, embedding, caching
│   ├── embed_job_description.py
│   ├── embed_message.py
│   ├── embed_recipient_profile.py
│   ├── llm_engine.py
│   └── ...
├── base_agents/                ← Shared agent bases
│   ├── BudgetAgent.py
│   ├── LLMPromptGovernorAgent.py
│   └── ...
├── models/
│   ├── model_definitions/
│   └── model_helpers/
├── utils/                      ← Formatting, serialization
│   ├── format_data.py
│   ├── format_metadata.py
│   ├── serialize_generation_context.py
│   └── ...
└── mixins/
```

---

## Detailed File Mapping

### Phase 1: L1_cognition/thought_engine (80 files)

#### Resume Engine → `apps_rg/engines/utils/` (29 files)

```
agentic_core/L1_cognition/thought_engine/adjust_section_weights.py
agentic_core/L1_cognition/thought_engine/assess_cognition_relevance.py
agentic_core/L1_cognition/thought_engine/build_search_filters.py
agentic_core/L1_cognition/thought_engine/build_skill_query.py
agentic_core/L1_cognition/thought_engine/calibrate_fit_score.py
agentic_core/L1_cognition/thought_engine/compute_skill_similarity.py
agentic_core/L1_cognition/thought_engine/diagnose_generation_issues.py
agentic_core/L1_cognition/thought_engine/evaluate_writing_quality.py
agentic_core/L1_cognition/thought_engine/fetch_user_preferences.py
agentic_core/L1_cognition/thought_engine/normalize_skill_scores.py
agentic_core/L1_cognition/thought_engine/optimization_strategies.py
agentic_core/L1_cognition/thought_engine/optimize_content_order.py
agentic_core/L1_cognition/thought_engine/order_skills_by_relevance.py
agentic_core/L1_cognition/thought_engine/parse_job_description.py
agentic_core/L1_cognition/thought_engine/weight_experience_match.py
... (and 14 more)
```

#### Outreach Engine → `apps_lic/engines/utils/` (43 files)

```
agentic_core/L1_cognition/thought_engine/adjust_tone_weights.py
agentic_core/L1_cognition/thought_engine/aggregate_campaign_state.py
agentic_core/L1_cognition/thought_engine/assess_content_risk.py
agentic_core/L1_cognition/thought_engine/assess_message_relevance.py
agentic_core/L1_cognition/thought_engine/build_message_filters.py
agentic_core/L1_cognition/thought_engine/build_personalization_query.py
agentic_core/L1_cognition/thought_engine/calibrate_engagement_score.py
agentic_core/L1_cognition/thought_engine/compute_personalization_match.py
agentic_core/L1_cognition/thought_engine/diagnose_personalization_issues.py
agentic_core/L1_cognition/thought_engine/evaluate_engagement_potential.py
agentic_core/L1_cognition/thought_engine/evaluate_personalization_quality.py
agentic_core/L1_cognition/thought_engine/fetch_recipient_interactions.py
agentic_core/L1_cognition/thought_engine/inspect_message_quality.py
agentic_core/L1_cognition/thought_engine/log_campaign_metrics.py
agentic_core/L1_cognition/thought_engine/optimize_message_structure.py
... (and 28 more)
```

#### Shared → `apps_shared/common_utils/` (21 files)

```
agentic_core/L1_cognition/thought_engine/handle_api_timeouts.py
agentic_core/L1_cognition/thought_engine/handle_service_errors.py
agentic_core/L1_cognition/thought_engine/implement_fallback_strategy.py
agentic_core/L1_cognition/thought_engine/implement_fallbacks.py
agentic_core/L1_cognition/thought_engine/retry_generation_failures.py
agentic_core/L1_cognition/thought_engine/retry_task_implement_fallbacks.py
agentic_core/L1_cognition/thought_engine/task_handle_service_errors.py
agentic_core/L1_cognition/thought_engine/task_implement_fallback_strategy.py
agentic_core/L1_cognition/thought_engine/task_retry_generation_failures.py
agentic_core/L1_cognition/thought_engine/embed_job_description.py
agentic_core/L1_cognition/thought_engine/embed_message.py
agentic_core/L1_cognition/thought_engine/embed_recipient_profile.py
agentic_core/L1_cognition/thought_engine/format_data.py
agentic_core/L1_cognition/thought_engine/format_metadata.py
agentic_core/L1_cognition/thought_engine/serialize_generation_context.py
... (and 6 more)
```

### Phase 2: L2_execution/ToolRegistry (30 files)

#### Resume Engine → `apps_rg/engines/utils/` (21 files)

```
agentic_core/L2_execution/ToolRegistry/achv_models.py
agentic_core/L2_execution/ToolRegistry/apply_clerk_extraction.py
agentic_core/L2_execution/ToolRegistry/apply_data_enrichment.py
agentic_core/L2_execution/ToolRegistry/compute_word_count.py
agentic_core/L2_execution/ToolRegistry/create_experience_bullets.py
agentic_core/L2_execution/ToolRegistry/diff_generator.py
... (and 15 more)
```

#### Outreach Engine → `apps_lic/engines/utils/` (9 files)

```
agentic_core/L2_execution/ToolRegistry/action_call_generator.py
agentic_core/L2_execution/ToolRegistry/create_message_body.py
agentic_core/L2_execution/ToolRegistry/format_personalization_prompt.py
agentic_core/L2_execution/ToolRegistry/generate_subject_line.py
agentic_core/L2_execution/ToolRegistry/order_call_to_actions.py
agentic_core/L2_execution/ToolRegistry/prepare_message_payload.py
agentic_core/L2_execution/ToolRegistry/serialize_data.py
... (and 2 more)
```

### Phase 3: L5_safety/validators (49 files)

#### Resume Engine → `apps_rg/engines/` (42 files)

```
agentic_core/L5_safety/validators/DispatchResumeToolsAgent.py
... (and 41 more - many are dashboard/test files, review individually)
```

#### Outreach Engine → `apps_lic/engines/` (7 files)

```
agentic_core/L5_safety/validators/DispatchOutreachToolsAgent.py
agentic_core/L5_safety/validators/enforce_tone_guidelines.py
agentic_core/L5_safety/validators/OrganizationAgent.py
agentic_core/L5_safety/validators/RecipientAgent.py
agentic_core/L5_safety/validators/safety_validate_ethical_standards.py
... (and 2 more)
```

---

## Implementation Steps

### Step 1: Create Target Folders

```bash
# Resume Engine
mkdir -p apps_rg/engines/utils

# Outreach Engine
mkdir -p apps_lic/engines/utils

# Shared
mkdir -p apps_shared/common_utils
mkdir -p apps_shared/core_components
mkdir -p apps_shared/base_agents
```

### Step 2: Move Files (Gradual Migration)

**Phase 1: thought_engine utilities (80 files)**

```bash
# Resume utils
git mv agentic_core/L1_cognition/thought_engine/parse_job_description.py apps_rg/engines/utils/
git mv agentic_core/L1_cognition/thought_engine/build_skill_query.py apps_rg/engines/utils/
# ... (repeat for all 29 resume files)

# Outreach utils
git mv agentic_core/L1_cognition/thought_engine/build_message_filters.py apps_lic/engines/utils/
git mv agentic_core/L1_cognition/thought_engine/calibrate_engagement_score.py apps_lic/engines/utils/
# ... (repeat for all 43 outreach files)

# Shared utils
git mv agentic_core/L1_cognition/thought_engine/handle_api_timeouts.py apps_shared/common_utils/
git mv agentic_core/L1_cognition/thought_engine/implement_fallback_strategy.py apps_shared/common_utils/
# ... (repeat for all 21 shared files)
```

### Step 3: Update Imports

Run automated import updater:

```bash
python scripts/update_app_imports.py --dry-run
python scripts/update_app_imports.py --execute
```

### Step 4: Verify

```bash
# Agent discovery should remain stable
python scripts/full_agent_discovery.py --force

# Test imports
python -c "import apps_rg; import apps_lic; import apps_shared"

# Run tests
pytest tests/ -v
```

---

## SSOT Compliance Verification

✅ **APPS_RG_SUBFOLDER_MAP updated:**
```python
'engines': ['resume_engine', 'utils']
```

✅ **APPS_LIC_SUBFOLDER_MAP updated:**
```python
'engines': ['outreach_engine', 'utils']
```

✅ **APPS_SHARED_SUBFOLDER_MAP verified:**
```python
'common_utils': ['utility_helpers', 'utility_types']
'core_components': ['component_definitions', 'component_helpers']
'base_agents': ['agent_definitions', 'agent_helpers']
```

✅ **APP_SPECIFIC_TARGET_SUBFOLDER = "engines"** - All app files go to engines/

---

## Expected Results

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| agentic_core files | 1,317 | ~1,005 | -312 files |
| apps_rg files | ~30 | ~209 | +179 files |
| apps_lic files | ~30 | ~88 | +58 files |
| apps_shared files | ~10 | ~85 | +75 files |

**Agent count:** Should remain stable at 201 agents

---

## Risk Mitigation

1. **Git tags before each phase** - `git tag pre-phase1-migration`
2. **Gradual migration** - One phase at a time
3. **Import compatibility** - Old paths work during transition
4. **Automated testing** - Run full test suite after each phase

---

## Next Steps

1. ✅ SSOT updated in `structure_blueprint.py`
2. Create target folders
3. Start Phase 1: thought_engine migration (80 files)
4. Update imports
5. Verify and test
6. Proceed to Phase 2 and 3

---

## Appendix: Classification Methodology

Files classified using keyword analysis:

- **Resume keywords:** `resume`, `cv`, `ats`, `job description`, `skill`, `experience`, `bullet`, `section`
- **Outreach keywords:** `outreach`, `linkedin`, `recipient`, `campaign`, `personalization`, `sender`, `message`
- **Shared signals:** `fallback`, `retry`, `timeout`, `error`, `api`, `cache`, `embed`, `format`, `llm`

Run `python scripts/analyze_app_files.py` for updated analysis.
