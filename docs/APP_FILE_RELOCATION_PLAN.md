# App File Relocation Plan

## Problem Statement

Many files in `agentic_core/` are actually app-specific and belong in `apps_rg/` (Resume Generator) or `apps_lic/` (LinkedIn Canonical). This creates:
- **False bloat perception** - files appear as core bloat but are legitimate app code
- **Unclear ownership** - hard to know which app owns which functionality
- **Import complexity** - apps importing from core when they should be self-contained

## Analysis Results

| Category | Files | Action |
|----------|-------|--------|
| Resume-related (apps_rg) | 222 files | Relocate to apps_rg |
| Outreach-related (apps_lic) | 72 files | Relocate to apps_lic |
| Generic (keep in agentic_core) | 660 files | No action |

**Total potential relocation: 294 files**

---

## Classification Methodology

Files were classified using keyword analysis:

### Resume Generator (apps_rg) Keywords
- `resume`, `cv `, `ats`, `job description`, `bullet point`, `work experience`, `resume generator`, `resume_engine`

### LinkedIn Outreach (apps_lic) Keywords
- `outreach`, `linkedin`, `recipient`, `campaign`, `personalization`, `sender`, `inmail`, `message generation`, `outreach_engine`

### Classification Rules
1. **Explicit app reference** - Files containing `apps_rg` or `apps_lic` imports → that app
2. **Single domain** - Files with only resume OR outreach keywords → that domain
3. **Keyword frequency** - Files with both → higher frequency wins (threshold: 5+)
4. **Generic** - Files with neither or low frequency → keep in agentic_core

---

## Detailed Relocation Plan

### Phase 1: L1_cognition/thought_engine (80 files)

This folder contains the most app-specific code disguised as core cognition.

#### To apps_rg/engines/thought_engine/ (35 files)

```
agentic_core/L1_cognition/thought_engine/adjust_section_weights.py
agentic_core/L1_cognition/thought_engine/assess_cognition_relevance.py
agentic_core/L1_cognition/thought_engine/build_search_filters.py
agentic_core/L1_cognition/thought_engine/build_skill_query.py
agentic_core/L1_cognition/thought_engine/calibrate_fit_score.py
agentic_core/L1_cognition/thought_engine/CognitiveNode.py
agentic_core/L1_cognition/thought_engine/CognitiveNodeRefactored.py
agentic_core/L1_cognition/thought_engine/compute_skill_similarity.py
agentic_core/L1_cognition/thought_engine/diagnose_generation_issues.py
agentic_core/L1_cognition/thought_engine/evaluate_writing_quality.py
agentic_core/L1_cognition/thought_engine/fetch_user_preferences.py
agentic_core/L1_cognition/thought_engine/handle_api_timeouts.py
agentic_core/L1_cognition/thought_engine/implement_fallback_strategy.py
agentic_core/L1_cognition/thought_engine/llm_engine.py
agentic_core/L1_cognition/thought_engine/load_rag_config.py
agentic_core/L1_cognition/thought_engine/normalize_skill_scores.py
agentic_core/L1_cognition/thought_engine/optimization_strategies.py
agentic_core/L1_cognition/thought_engine/optimize_content_order.py
agentic_core/L1_cognition/thought_engine/order_skills_by_relevance.py
agentic_core/L1_cognition/thought_engine/parse_job_description.py
agentic_core/L1_cognition/thought_engine/rank_content_relevance.py
agentic_core/L1_cognition/thought_engine/SemanticMemory.py
agentic_core/L1_cognition/thought_engine/weight_experience_match.py
... (and more)
```

#### To apps_lic/engines/thought_engine/ (45 files)

```
agentic_core/L1_cognition/thought_engine/adjust_tone_weights.py
agentic_core/L1_cognition/thought_engine/aggregate_campaign_state.py
agentic_core/L1_cognition/thought_engine/assess_content_risk.py
agentic_core/L1_cognition/thought_engine/assess_message_relevance.py
agentic_core/L1_cognition/thought_engine/build_message_filters.py
agentic_core/L1_cognition/thought_engine/build_personalization_query.py
agentic_core/L1_cognition/thought_engine/calibrate_engagement_score.py
agentic_core/L1_cognition/thought_engine/cognitive_node.py
agentic_core/L1_cognition/thought_engine/compute_personalization_match.py
agentic_core/L1_cognition/thought_engine/consensus_engine.py
agentic_core/L1_cognition/thought_engine/diagnose_personalization_issues.py
agentic_core/L1_cognition/thought_engine/embed_message.py
agentic_core/L1_cognition/thought_engine/embed_recipient_profile.py
agentic_core/L1_cognition/thought_engine/evaluate_engagement_potential.py
agentic_core/L1_cognition/thought_engine/evaluate_personalization_quality.py
agentic_core/L1_cognition/thought_engine/fetch_recipient_interactions.py
agentic_core/L1_cognition/thought_engine/inspect_message_quality.py
agentic_core/L1_cognition/thought_engine/log_campaign_metrics.py
agentic_core/L1_cognition/thought_engine/match_recipient_patterns.py
agentic_core/L1_cognition/thought_engine/meaning_search_similar_messages.py
agentic_core/L1_cognition/thought_engine/optimize_message_structure.py
agentic_core/L1_cognition/thought_engine/persona_planner.py
agentic_core/L1_cognition/thought_engine/query_past_campaigns.py
agentic_core/L1_cognition/thought_engine/rank_message_variants.py
agentic_core/L1_cognition/thought_engine/refine_message_ranking.py
agentic_core/L1_cognition/thought_engine/snapshot_campaign_state.py
agentic_core/L1_cognition/thought_engine/update_recipient_profiles.py
agentic_core/L1_cognition/thought_engine/weight_personalization_factors.py
... (and more)
```

### Phase 2: L2_execution/ToolRegistry (30 files)

#### To apps_rg/engines/tools/ (21 files)

```
agentic_core/L2_execution/ToolRegistry/achv_models.py
agentic_core/L2_execution/ToolRegistry/apply_clerk_extraction.py
agentic_core/L2_execution/ToolRegistry/apply_data_enrichment.py
agentic_core/L2_execution/ToolRegistry/compute_word_count.py
agentic_core/L2_execution/ToolRegistry/create_experience_bullets.py
agentic_core/L2_execution/ToolRegistry/diff_generator.py
... (and more)
```

#### To apps_lic/engines/tools/ (9 files)

```
agentic_core/L2_execution/ToolRegistry/action_call_generator.py
agentic_core/L2_execution/ToolRegistry/create_message_body.py
agentic_core/L2_execution/ToolRegistry/format_personalization_prompt.py
agentic_core/L2_execution/ToolRegistry/generate_subject_line.py
agentic_core/L2_execution/ToolRegistry/order_call_to_actions.py
agentic_core/L2_execution/ToolRegistry/prepare_message_payload.py
agentic_core/L2_execution/ToolRegistry/serialize_data.py
... (and more)
```

### Phase 3: L5_safety/validators (49 files)

#### To apps_rg/engines/validators/ (42 files)

```
agentic_core/L5_safety/validators/DispatchResumeToolsAgent.py
agentic_core/L5_safety/validators/check_output_quality.py
agentic_core/L5_safety/validators/dashboard_e2e_pipeline.py
... (and more - many are dashboard/test files, review individually)
```

#### To apps_lic/engines/validators/ (7 files)

```
agentic_core/L5_safety/validators/DispatchOutreachToolsAgent.py
agentic_core/L5_safety/validators/enforce_tone_guidelines.py
agentic_core/L5_safety/validators/OrganizationAgent.py
agentic_core/L5_safety/validators/RecipientAgent.py
agentic_core/L5_safety/validators/safety_validate_ethical_standards.py
... (and more)
```

---

## Implementation Strategy

### Option A: Gradual Migration (Recommended)

**Pros:** Low risk, easy rollback, maintains compatibility
**Cons:** Slower, temporary import complexity

1. **Create target folders**
   ```bash
   mkdir -p apps_rg/engines/thought_engine
   mkdir -p apps_rg/engines/tools
   mkdir -p apps_rg/engines/validators
   mkdir -p apps_lic/engines/thought_engine
   mkdir -p apps_lic/engines/tools
   mkdir -p apps_lic/engines/validators
   ```

2. **Add compatibility imports** in agentic_core
   - Keep original files as re-exports
   - Update to import from new locations
   - Deprecation warnings for direct imports

3. **Move files in batches**
   - Phase 1: L1_cognition/thought_engine (highest value)
   - Phase 2: L2_execution/ToolRegistry
   - Phase 3: L5_safety/validators
   - Phase 4: Remaining scattered files

4. **Update imports** across codebase
   - Use automated script to update import paths
   - Run tests after each batch

5. **Remove compatibility shims** after verification

### Option B: Big Bang Migration

**Pros:** Clean, one-time effort
**Cons:** Higher risk, harder to debug issues

1. Move all files at once
2. Update all imports in single pass
3. Run full test suite
4. Fix any breakages

---

## Recommended Approach

### Best Practice: Domain-Driven Design

The cleanest solution is to restructure apps to be self-contained:

```
apps_rg/
├── engines/
│   ├── resume_engine/          # Existing
│   ├── thought_engine/         # NEW - from L1_cognition
│   ├── tools/                  # NEW - from L2_execution
│   └── validators/             # NEW - from L5_safety
├── domain/
│   └── models/
└── shared/                     # Shared with apps_lic

apps_lic/
├── engines/
│   ├── outreach_engine/        # Existing
│   ├── thought_engine/         # NEW - from L1_cognition
│   ├── tools/                  # NEW - from L2_execution
│   └── validators/             # NEW - from L5_safety
├── domain/
│   └── models/
└── shared/                     # Shared with apps_rg

apps_shared/                    # Truly shared code between apps
├── cognition/
├── tools/
└── validators/
```

### Files to Keep in agentic_core

These are truly generic and should NOT be moved:

- Base agents (L0-L6 base classes)
- Structure blueprint and SSOT
- MCP infrastructure
- Generic validators (syntax, AST, etc.)
- Observability infrastructure
- Generic orchestration patterns

---

## Verification Checklist

After each phase:

- [ ] Run `python scripts/full_agent_discovery.py --force`
- [ ] Verify agent count stable (201 agents)
- [ ] Run `pytest tests/ -v`
- [ ] Check no circular imports: `python -c "import apps_rg; import apps_lic"`
- [ ] Verify dashboard still works

---

## Risk Mitigation

1. **Git tags before each phase** - Easy rollback
2. **Compatibility imports** - Old paths still work during transition
3. **Incremental batches** - Catch issues early
4. **Automated import updates** - Reduce human error

---

## Timeline Estimate

| Phase | Files | Effort | Risk |
|-------|-------|--------|------|
| Phase 1: thought_engine | 80 | 2-3 hours | Medium |
| Phase 2: ToolRegistry | 30 | 1-2 hours | Low |
| Phase 3: validators | 49 | 2-3 hours | Medium |
| Phase 4: scattered | 135 | 4-6 hours | High |
| **Total** | **294** | **10-14 hours** | - |

---

## Next Steps

1. **Review this plan** - Confirm classification accuracy
2. **Decide on approach** - Gradual vs Big Bang
3. **Create backup** - Git tag current state
4. **Start Phase 1** - L1_cognition/thought_engine migration
5. **Iterate** - Adjust based on findings

---

## Appendix: Full File Lists

Run `python scripts/analyze_app_files.py` for complete categorized file lists.
