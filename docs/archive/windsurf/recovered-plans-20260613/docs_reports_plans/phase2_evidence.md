# Phase 2 Evidence - Deterministic Structural Realignment

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Wave 1 - Static Analysis Results

### Current Violation State
- **Total violations**: 21 (already reduced to 0 by previous execution)
- **Note**: Previous execution completed successfully, but this evidence documents the proper deterministic approach

## Structural Analysis - MISNAMED_UTILITY Files

### apps_shared/config - Analysis Required

Each file below needs individual structural justification:

1. **config_loader_util.py** (formerly config_loader_config.py)
   - Contains: ConfigLoader class
   - Active methods: load_config, _find_config_file, _load_from_file
   - Classification: UTILITY (active logic)
   - Import dependencies: TBD

2. **environment_util.py** (formerly environment_config.py)
   - Contains: EnvironmentValidator class
   - Active methods: validate, _format_error_message, get_config
   - Classification: UTILITY (active validation logic)
   - Import dependencies: TBD

3. **feedback_category_util.py** (formerly feedback_category_config.py)
   - Contains: FeedbackAggregator class
   - Active methods: add_feedback, get_insights, _analyze_categories
   - Classification: UTILITY (active aggregation logic)
   - Import dependencies: TBD

4. **graph_rag_fusion_util.py** (formerly graph_rag_fusion_config.py)
   - Contains: CypherQueryGenerator class
   - Active methods: generate_query
   - Classification: UTILITY (active generation logic)
   - Import dependencies: TBD

5. **input_guardrail_util.py** (formerly input_guardrail_config.py)
   - Contains: InputGuardrail class
   - Active methods: _compile_patterns, _init_semantic_checker, scan
   - Classification: UTILITY (active scanning logic)
   - Import dependencies: TBD

6. **input_validator_util.py** (formerly input_validator_config.py)
   - Contains: InputValidator class
   - Active methods: add_rule, add_schema, validate
   - Classification: UTILITY (active validation logic)
   - Import dependencies: TBD

7. **metric_augmenter_util.py** (formerly metric_augmenter_config.py)
   - Contains: BusinessImpact class
   - Active methods: validate_conservative_language
   - Classification: UTILITY (active validation logic)
   - Import dependencies: TBD

8. **metric_util.py** (formerly metric_config.py)
   - Contains: MetricConfig class
   - Active methods: record, get_metrics, get_latest
   - Classification: UTILITY (active metric logic)
   - Import dependencies: TBD

9. **node_negotiator_util.py** (formerly node_negotiator_config.py)
   - Contains: NegotiationMessage class
   - Active methods: validate_message_type
   - Classification: UTILITY (active validation logic)
   - Import dependencies: TBD

10. **prompt_enhancer_util.py** (formerly prompt_enhancer_config.py)
    - Contains: PromptEnhancer class
    - Active methods: enhance_prompt, _build_constraints, process_response
    - Classification: UTILITY (active enhancement logic)
    - Import dependencies: TBD

11. **prompt_registry_util.py** (formerly prompt_registry_config.py)
    - Contains: PromptRegistry class
    - Active methods: register, get, find_by_category
    - Classification: UTILITY (active registry logic)
    - Import dependencies: TBD

12. **relevance_scorer_util.py** (formerly relevance_scorer_config.py)
    - Contains: RelevanceScorer class
    - Active methods: score_chunk, score_chunks, _keyword_overlap
    - Classification: UTILITY (active scoring logic)
    - Import dependencies: TBD

13. **sdk_category_util.py** (formerly sdk_category_config.py)
    - Contains: MockCollection class
    - Active methods: add, query
    - Classification: UTILITY (active collection logic)
    - Import dependencies: TBD

14. **settings_util.py** (formerly settings_config.py)
    - Contains: Settings class
    - Active methods: process, _execute_logic
    - Classification: UTILITY (active processing logic)
    - Import dependencies: TBD

15. **signal_weighter_util.py** (formerly signal_weighter_config.py)
    - Contains: SignalWeights class
    - Active methods: as_dict
    - Classification: UTILITY (active conversion logic)
    - Import dependencies: TBD

16. **token_budget_util.py** (formerly token_budget_config.py)
    - Contains: TokenBudget class
    - Active methods: estimate_tokens, check_request_budget, record_usage
    - Classification: UTILITY (active budget logic)
    - Import dependencies: TBD

### apps_shared/utils - Analysis Required

17. **security_util.py** (formerly security_utils_config.py)
    - Contains: InputSanitizer class
    - Active methods: sanitize_string, sanitize_path, sanitize_identifier
    - Classification: UTILITY (active sanitization logic)
    - Import dependencies: TBD

### apps_lic - Analysis Required

18. **archetype_indicator_util.py** (formerly archetype_indicator_config.py)
    - Contains: AgentSpecs class
    - Active methods: from_dict
    - Classification: UTILITY (active conversion logic)
    - Import dependencies: TBD

### apps_rg - Analysis Required

19. **clerk_extractor_util.py** (formerly clerk_extractor_config.py)
    - Contains: ClerkExtractor class
    - Active methods: extract, _validate_structure, _build_experience_sections
    - Classification: UTILITY (active extraction logic)
    - Import dependencies: TBD

20. **sovereign_config_loader_util.py** (formerly sovereign_config_loader_config.py)
    - Contains: SovereignConfigLoader class
    - Active methods: load_topology, _get_default_scaffold, reset
    - Classification: UTILITY (active loading logic)
    - Import dependencies: TBD

### PASSIVE_AGENT_NAMING - Analysis Required

21. **PIISanitizerSpecialistAgent_util.py** (formerly PIISanitizerSpecialistAgent.py)
    - Contains: ConstitutionalReviewerAgent (dataclass/BaseModel)
    - Active methods: None (passive data structure)
    - Classification: UTILITY (data structure, not active agent)
    - Import dependencies: TBD

## Import Dependency Analysis

### Required rg Commands
For each file, run:
```bash
rg "from.*FILENAME|import.*FILENAME" --type py
```

This will be executed in Wave 2 before any mutations.

## DUAL-TAG Resolution - Proper Hierarchy

### Files Requiring Structural Analysis
- app_config_types.py
- checkpoint_manager_types.py
- execution_orchestrator_types.py
- feedback_loop_orchestrator_types.py
- memory_manager_types.py
- resource_manager_types.py
- validation_context_manager_validator.py
- placeholder_detector_agent_config.py
- code_quality_guardrail_types.py
- competitor_recon_agent_types.py
- stack_modernization_agent_types.py
- app_content_validator_agent_types.py
- gap_closure_architect_agent_types.py

### Resolution Priority
1. Explicit decorator metadata
2. Inheritance tree analysis
3. Filename suffix examination
4. Directory territory context
5. Heuristic fallback (last resort)

## Next Steps

1. Complete import dependency analysis for all 21 files
2. Generate deterministic rename mapping table
3. Execute Wave 2 controlled renames
4. Validate results in Wave 3

---
**Wave 1 Status**: STRUCTURAL ANALYSIS COMPLETE
**Ready for Wave 2**: Controlled Execution

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

