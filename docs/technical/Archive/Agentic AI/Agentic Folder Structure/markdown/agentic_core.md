agentic_core/
├── l1_planning/
│   ├── strategy_planning/
│   │   ├── blueprint/
│   │   │   ├── goals/
│   │   │   │   ├── goal_definitions.py
│   │   │   │   ├── goal_constraints.py
│   │   │   │   └── goal_templates.yaml
│   │   │   ├── signals/
│   │   │   │   ├── signal_types.py
│   │   │   │   ├── signal_extractors.py
│   │   │   │   └── signal_weights.yaml
│   │   │   └── orchestration/
│   │   │       ├── plan_schema.py
│   │   │       ├── plan_optimizer.py
│   │   │       └── plan_safety_checks.py
│   │   ├── decomposition/
│   │   │   ├── task_segmentation.py
│   │   │   ├── task_graph_builder.py
│   │   │   └── task_normalization.py
│   │   └── refinement/
│   │       ├── validator.py
│   │       ├── redundancy_pruning.py
│   │       └── scoring.py
│   │
│   ├── qa_planning/
│   │   ├── question_understanding/
│   │   │   ├── classification.py
│   │   │   ├── intent_extraction.py
│   │   │   └── disambiguation.py
│   │   ├── retrieval_plans/
│   │   │   ├── rag_blueprints.py
│   │   │   ├── ranking_strategies.py
│   │   │   └── fallback_routes.yaml
│   │   └── answer_blueprints/
│   │       ├── format_constraints.py
│   │       ├── answer_templates.yaml
│   │       └── verification_rules.py
│   │
│   ├── rag_planning/
│   │   ├── query_generation/
│   │   │   ├── expansion_hyde.py
│   │   │   ├── query_rewriting.py
│   │   │   └── signal_weighting.py
│   │   ├── fusion/
│   │   │   ├── rrf.py
│   │   │   ├── hybrid_fuser.py
│   │   │   └── scoring_models.py
│   │   └── routing/
│   │       ├── vector_db_selection.py
│   │       ├── cross_db_balancing.py
│   │       └── retrieval_budgeting.py
│   │
│   ├── safety_planning/
│   │   ├── detectors/
│   │   │   ├── pii.py
│   │   │   ├── toxicity.py
│   │   │   └── jailbreak_patterns.yaml
│   │   ├── policies/
│   │   │   ├── rule_engine.py
│   │   │   ├── policy_map.yaml
│   │   │   └── severity_levels.yaml
│   │   └── mitigation/
│   │       ├── redact.py
│   │       ├── rephrase.py
│   │       └── block.py
│   │
│   └── utils/
│       ├── schema_helpers.py
│       ├── context_pruning.py
│       └── scoring_utils.py
│
├── l2_execution/
│   ├── tools/
│   │   ├── browser/
│   │   │   ├── run_search.py
│   │   │   ├── scrape.py
│   │   │   └── extraction_utils.py
│   │   ├── file_ops/
│   │   │   ├── load_file.py
│   │   │   ├── find_in_file.py
│   │   │   └── summarization_utils.py
│   │   └── api/
│   │       ├── openai_client.py
│   │       ├── anthropic_client.py
│   │       └── retry_backoff.py
│   │
│   ├── execution_engines/
│   │   ├── tool_invocation.py
│   │   ├── validation.py
│   │   └── error_handling.py
│   │
│   └── utils/
│       ├── parsing.py
│       ├── serialization.py
│       └── io_limits.py
│
├── l3_orchestration/
│   ├── dag/
│   │   ├── node_types/
│   │   │   ├── plan_node.py
│   │   │   ├── act_node.py
│   │   │   └── observe_node.py
│   │   ├── graph_builder.py
│   │   ├── graph_optimizer.py
│   │   └── graph_validator.py
│   │
│   ├── react/
│   │   ├── think_step.py
│   │   ├── act_step.py
│   │   └── observe_step.py
│   │
│   └── controllers/
│       ├── loop_controller.py
│       ├── retry_controller.py
│       └── escalate_controller.py
│
├── l4_memory/
│   ├── short_term/
│   │   ├── buffer.py
│   │   ├── summarizer.py
│   │   └── eviction_policy.py
│   ├── long_term/
│   │   ├── embeddings_store.py
│   │   ├── document_index.py
│   │   └── versioning.py
│   └── state/
│       ├── execution_context.py
│       ├── thread_state.py
│       └── persistence.py
│
└── l5_safety/
    ├── filters/
    │   ├── pii_filter.py
    │   ├── violence_filter.py
    │   └── policy_classifier.py
    ├── guardrails/
    │   ├── enforcement_engine.py
    │   ├── safety_events.py
    │   └── runtime_blocks.py
    └── audit/
        ├── logging.py
        ├── trace_capture.py
        └── safety_reports.py


### Directory Structure

```plaintext
├── agentic_core.md
├── apps.md
├── config.md
├── data.md
├── observability.md
├── prompt_governance.md
├── runtime.md
├── schemas.md
├── scripts.md
├── tests.md
└── update_markdown_trees.py
```
