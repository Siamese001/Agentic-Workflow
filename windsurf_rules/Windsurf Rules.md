````markdown
==================================================================================================
WINDSURF GLOBAL RULES — MODE-B VERSION  
FINAL COMPREHENSIVE + ZERO-LOSS + OPENAI-ALIGNED AGENTIC RULESET
==================================================================================================

Windsurf MUST load and enforce ALL rules in this file.  
These rules override all other instructions and govern every Phase (PATCH + VALIDATION).

Windsurf MUST operate ONLY in Mode-B:
- PATCH Phase → `apply_patch` + `write_to_file` ONLY  
- VALIDATION Phase → TRUE/FALSE matrix + completion line ONLY  
- No narrative, no explanations, no shell commands, no reasoning text.


==================================================================================================
0 — EXECUTION MODEL
==================================================================================================

Windsurf MUST:
- modify ANY file as needed  
- ALWAYS self-correct violations of these rules  
- NEVER ask questions  
- NEVER stop early  
- continue patching until ALL validations pass  

Modes:
- PATCH_LOOP → `apply_patch` + `write_to_file` ONLY  
- VALIDATION_LOOP → TRUE/FALSE matrix + completion line ONLY  


==================================================================================================
1 — FILE OPERATIONS
==================================================================================================

Rules:
- Existing files → `apply_patch`  
- New files → `write_to_file`  
- Directories → created implicitly  
- No placeholders, no partial diffs  
- All ambiguity MUST resolve toward rule compliance + zero-loss continuity  


==================================================================================================
1.1 — CACHE HANDLING RULES
==================================================================================================

ALL caches / venvs / Python artifacts MUST be relocated to:

```text
/agentic_workflow_10_11/runtime/cache/
````

MANDATORY mappings:

```text
__pycache__      → /agentic_workflow_10_11/runtime/cache/__pycache__/
.venv            → /agentic_workflow_10_11/runtime/cache/venv/
.mypy_cache      → /agentic_workflow_10_11/runtime/cache/mypy/
.pytest_cache    → /agentic_workflow_10_11/runtime/cache/pytest/
.ruff_cache      → /agentic_workflow_10_11/runtime/cache/ruff/
.cache, cache    → /agentic_workflow_10_11/runtime/cache/tmp/
tmp, temp        → /agentic_workflow_10_11/runtime/cache/tmp/
scratch          → /agentic_workflow_10_11/runtime/cache/tmp/
```

Constraints:

* These folders MUST NOT appear anywhere else in the repo.
* Windsurf MUST ensure `/agentic_workflow_10_11/runtime/cache/` is `.gitignore`-protected.
* Any newly discovered cache-like folders MUST be migrated into this tree.

==================================================================================================
2 — ZERO-LOSS CONTINUITY
========================

* Windsurf MUST preserve ALL existing capabilities.
* No regressions.
* No deletions of behavior.
* Duplicate / conflicting logic MUST be merged into a single correct version.
* When in doubt, preserve BOTH behaviors and add tests to disambiguate.

==================================================================================================
3 — CANONICAL REPOSITORY TREE (ROOT → LEVEL-4 MAX)
==================================================

This section is the **single authoritative directory specification** for `agentic_workflow_10_11`.

Depth policy:

* Root = Level 0
* Level-1, Level-2, Level-3 = folders
* Level-4 = files allowed under Level-3 folders
* NO folder may exist deeper than Level-3 (no Level-4 folders; only Level-4 files)
* No folder or subfolder at Levels 0–3 may be empty.
* Every directory in the canonical tree must contain at least one valid file defined for its level.

Windsurf MUST:

* Conform the repo layout to this tree.
* Create any missing directories/files as needed (respecting zero-loss).
* Move mislocated code/tests into the correct layer/engine subtrees.

```text
# ============================================================================
# AGENTIC AI FOLDER TREE (SECTION 3)
# OPENAI-ALIGNED L1–L5, HIGH ATOMICITY, LOW NOISE
# ============================================================================

/agentic_workflow_10_11                         # LEVEL 0
│
├── agentic_core/                              # LEVEL 1 — L1–L5 implementation
│   │
│   ├── l1_planning/                           # LEVEL 2 — Cognition (no tools)
│   │   ├── planners/                          # LEVEL 3
│   │   │   ├── strategy_planner.py            # High-level mission strategy
│   │   │   ├── research_planner.py            # Company/contact research plans
│   │   │   ├── message_planner.py             # Outreach / messaging plans
│   │   │   ├── refinement_planner.py          # Self-check / refinement loops
│   │   │   ├── safety_planner.py              # Safety reasoning (L1 only)
│   │   │   ├── rag_plan_builder.py            # Plans RAG tool sequences
│   │   │   ├── kg_plan_builder.py             # Plans KG traversal sequences
│   │   │   ├── temporal_plan_builder.py       # Plans temporal invalidation runs
│   │   │   └── chain_of_thought_planner.py    # CoT / ToT plan shaper
│   │   │
│   │   ├── schemas/                           # LEVEL 3 — Planning schemas
│   │   │   ├── strategy_schema.json
│   │   │   ├── research_schema.json
│   │   │   ├── message_schema.json
│   │   │   ├── refinement_schema.json
│   │   │   ├── retrieval_plan_schema.json
│   │   │   ├── temporal_plan_schema.json
│   │   │   └── kg_plan_schema.json
│   │   │
│   │   └── utils/                             # LEVEL 3 — Pure helpers
│   │       ├── planning_utils.py
│   │       └── planner_validation.py
│   │
│   ├── l2_execution/                          # LEVEL 2 — Action / tools layer
│   │   ├── tools/                             # LEVEL 3 — Atomic tool families (grouped by comments)
│   │   │   # -----------------------------------------------------------------
│   │   │   # RETRIEVAL CORE (FAMILY: RETRIEVAL)
│   │   │   # -----------------------------------------------------------------
│   │   │   ├── bm25_tool.py                   # Sparse retrieval
│   │   │   ├── dense_retrieval_tool.py        # Vector retrieval
│   │   │   ├── hybrid_router_tool.py          # Chooses sparse / dense / hybrid
│   │   │   ├── reranker_tool.py               # Cross-encoder re-ranker
│   │   │   ├── snippet_extraction_tool.py     # Extract best span from docs
│   │   │   └── text_cleaning_tool.py          # Normalize / sanitize text
│   │   │
│   │   │   # -----------------------------------------------------------------
│   │   │   # RAG-SPECIFIC TOOLS (FAMILY: RAG)
│   │   │   # -----------------------------------------------------------------
│   │   │   ├── rrf_fusion_tool.py             # Reciprocal Rank Fusion
│   │   │   ├── rag_filter_tool.py             # Dedupe / cluster / top-k filter
│   │   │   ├── rag_query_rewriter_tool.py     # Query rewrite / expansion
│   │   │   ├── hyde_tool.py                   # HYDE synthetic doc generator
│   │   │   └── chunking_tool.py               # Online chunking (execution-time)
│   │   │
│   │   │   # -----------------------------------------------------------------
│   │   │   # KG / GRAPH TOOLS (FAMILY: KG)
│   │   │   # -----------------------------------------------------------------
│   │   │   ├── kg_lookup_tool.py              # Node lookup (ID / label)
│   │   │   ├── kg_traversal_tool.py           # Controlled multi-hop traversal
│   │   │   └── kg_relation_expand_tool.py     # Expand related entities/edges
│   │   │
│   │   │   # -----------------------------------------------------------------
│   │   │   # TEMPORAL AGENT TOOLS (FAMILY: TEMPORAL)
│   │   │   # -----------------------------------------------------------------
│   │   │   ├── temporal_extraction_tool.py    # Extract temporal spans/events
│   │   │   ├── temporal_invalidation_tool.py  # Apply invalidation decisions
│   │   │   └── temporal_event_builder_tool.py # Construct temporal event records
│   │   │
│   │   │   # -----------------------------------------------------------------
│   │   │   # CORE INFRASTRUCTURE TOOLS (FAMILY: INFRA)
│   │   │   # -----------------------------------------------------------------
│   │   │   ├── embedding_tool.py              # Embeddings via model / API
│   │   │   ├── search_tool.py                 # Meta-search (web/internal)
│   │   │   ├── http_tool.py                   # Safe HTTP client
│   │   │   ├── sql_tool.py                    # Parameterized SQL execution
│   │   │   ├── file_tool.py                   # File IO abstraction
│   │   │   ├── serialization_tool.py          # JSON/YAML serialize/deserialize
│   │   │   ├── crypto_hash_tool.py            # Hashing, checksums
│   │   │   └── diff_tool.py                   # Text / JSON diff computation
│   │   │
│   │   ├── engines/                          # LEVEL 3 — Domain executors
│   │   │   ├── resume/
│   │   │   │   ├── resume_generation_executor.py   # Executes resume-gen missions
│   │   │   │   ├── resume_research_executor.py     # Executes resume research
│   │   │   │   └── resume_validation_executor.py   # Validates resume outputs
│   │   │   └── outreach/
│   │   │       ├── outreach_message_executor.py    # Outreach copy executor
│   │   │       ├── outreach_research_executor.py   # Outreach research executor
│   │   │       └── outreach_validation_executor.py # Validates outreach outputs
│   │   │
│   │   ├── wrappers/                         # LEVEL 3 — Tool middlewares
│   │   │   └── execution_wrappers.py          # Telemetry, retries, timeouts
│   │   │
│   │   └── utils/                            # LEVEL 3 — Execution helpers
│   │       ├── execution_utils.py
│   │       └── retry_policies.py
│   │
│   ├── l3_orchestration/                     # LEVEL 2 — DAG orchestration
│   │   ├── framework/
│   │   │   ├── dag_engine.py                 # DAG runtime implementation
│   │   │   ├── dag_node.py                   # Node definitions / contracts
│   │   │   ├── dag_runner.py                 # DAG execution loop
│   │   │   ├── recursion_controller.py       # Controls recursion depth & budget
│   │   │   └── arbitration_engine.py         # Critic/verifier/arbiter logic
│   │   │
│   │   ├── engines/
│   │   │   ├── resume/
│   │   │   │   ├── resume_orchestrator.py
│   │   │   │   └── resume_workflow_dag.yaml  # YAML DAG spec: nodes + edges
│   │   │   └── outreach/
│   │   │       ├── outreach_orchestrator.py
│   │   │       └── outreach_workflow_dag.yaml
│   │   │
│   │   └── utils/
│   │       ├── orchestration_utils.py
│   │       └── dag_validation.py
│   │
│   ├── l4_memory_state/                      # LEVEL 2 — Storage, temporal, KG
│   │   ├── providers/                        # LEVEL 3 — Storage backends
│   │   │   ├── chroma_provider.py            # Vector store backing for RAG
│   │   │   ├── postgres_provider.py          # Relational DB backing
│   │   │   ├── redis_provider.py             # Redis / cache backing
│   │   │   └── embedding_provider.py         # Embedding index management
│   │   │
│   │   ├── temporal/                         # LEVEL 3 — Temporal agent backend
│   │   │   ├── chunking.py                   # Batch/offline chunking logic
│   │   │   ├── statement_extraction.py       # Extract candidate statements
│   │   │   ├── temporal_range_extraction.py  # valid_at / invalid_at extraction
│   │   │   ├── triplet_extraction.py         # (subject, predicate, object)
│   │   │   ├── event_generation.py           # Build TemporalEvent objects
│   │   │   ├── entity_resolution.py          # Canonical entity resolution
│   │   │   └── invalidation.py               # Temporal invalidation logic
│   │   │
│   │   └── mappings/                         # LEVEL 3 — Domain → storage mapping
│   │       ├── resume_mapping.py
│   │       └── outreach_mapping.py
│   │
│   └── l5_safety/                            # LEVEL 2 — Safety / policy
│       ├── filters/                          # LEVEL 3
│       │   ├── pii_filter.py
│       │   ├── toxicity_detector.py
│       │   ├── hallucination_detector.py
│       │   └── injection_detector.py
│       │
│       ├── policies/
│       │   ├── resume_policy.yaml
│       │   └── outreach_policy.yaml
│       │
│       └── validators/
│           ├── safety_validator.py
│           └── content_validator.py
│
├── apps/                                     # LEVEL 1 — Thin app layer
│   ├── resume_engine/
│   │   ├── adapters/
│   │   │   └── resume_adapter.py             # Maps external → agentic core
│   │   │
│   │   └── pipelines/
│   │       ├── resume_pipeline.py            # Main resume-gen entrypoint
│   │       └── resume_enrichment.py          # Optional enrichment flow
│   │
│   └── outreach_engine/
│       ├── adapters/
│       │   └── outreach_adapter.py
│       │
│       └── pipelines/
│           ├── outreach_pipeline.py
│           └── outreach_enrichment.py
│
├── prompt_governance/                        # LEVEL 1 — Prompt ACL & bundles
│   ├── manifests/                            # LEVEL 2
│   │   ├── prompt_registry.json              # Index of all prompt bundles
│   │   ├── injection_layers_manifest.json    # Valid layer ordering
│   │   ├── domain_manifest.json              # resume / outreach / global
│   │   └── tool_manifest.json                # Maps L2 tools → tooling bundles
│   │
│   ├── PromptACLs/                           # LEVEL 2 — Access control
│   │   ├── acl_global.json
│   │   ├── acl_resume.json
│   │   ├── acl_outreach.json
│   │   ├── acl_l1_planning.json
│   │   ├── acl_l2_execution.json
│   │   └── acl_l3_orchestration.json
│   │
│   ├── PromptDefinitions/                    # LEVEL 2 — Structural definitions
│   │   ├── definitions_global.json
│   │   ├── definitions_resume.json
│   │   ├── definitions_outreach.json
│   │   ├── definitions_rag.json
│   │   ├── definitions_kg.json
│   │   └── definitions_temporal.json
│   │
│   ├── governance_metadata/                  # LEVEL 2 — Governance, not content
│   │   ├── readme.md
│   │   ├── governance_rules.json
│   │   ├── override_rules.json
│   │   └── merging_strategies.json
│   │
│   ├── PromptVersions/                       # LEVEL 2 — Version lineages
│   │   ├── global_versions.json
│   │   ├── resume_versions.json
│   │   └── outreach_versions.json
│   │
│   ├── Layered_Injection_Bundles/            # LEVEL 2 — Injection v5 layers
│   │   ├── framing/
│   │   │   ├── global_framing_v1_bundle.txt
│   │   │   ├── resume_framing_v1_bundle.txt
│   │   │   └── outreach_framing_v1_bundle.txt
│   │   │
│   │   ├── context/
│   │   │   ├── global_context_v1_bundle.txt
│   │   │   ├── resume_context_v1_bundle.txt
│   │   │   ├── outreach_context_v1_bundle.txt
│   │   │   └── temporal_context_v1_bundle.txt
│   │   │
│   │   ├── reasoning/
│   │   │   ├── cot_v1_bundle.txt
│   │   │   ├── critic_v1_bundle.txt
│   │   │   └── meta_reasoner_v1_bundle.txt
│   │   │
│   │   ├── tooling/
│   │   │   ├── rag_tooling_v1_bundle.txt
│   │   │   ├── kg_tooling_v1_bundle.txt
│   │   │   ├── temporal_tooling_v1_bundle.txt
│   │   │   ├── resume_tooling_v1_bundle.txt
│   │   │   └── outreach_tooling_v1_bundle.txt
│   │   │
│   │   ├── safety/
│   │   │   ├── safety_global_v1_bundle.txt
│   │   │   ├── safety_resume_v1_bundle.txt
│   │   │   └── safety_outreach_v1_bundle.txt
│   │   │
│   │   └── output/
│   │       ├── output_resume_v1_bundle.txt
│   │       ├── output_outreach_v1_bundle.txt
│   │       └── output_generic_v1_bundle.txt
│   │
│   ├── Domains/                              # LEVEL 2 — Domain overrides
│   │   ├── resume_domain_overrides.json
│   │   ├── resume_prompt_defaults.json
│   │   ├── outreach_domain_overrides.json
│   │   └── outreach_prompt_defaults.json
│   │
│   └── InjectionPolicies/                    # LEVEL 2 — Layering rules
│       ├── layer_order.json                  # framing→context→reasoning→tooling→safety→output
│       ├── conflict_resolution.json
│       └── safety_guardrail_policies.json
│
├── observability/                            # LEVEL 1 — Tracing / metrics / logs
│   ├── trace/
│   │   ├── dag_spans.log                     # DAG-level traces
│   │   └── tool_spans.log                    # L2 tool spans
│   │
│   ├── metrics/
│   │   ├── cost_metrics.json                 # Cost per mission / step
│   │   └── token_usage.json                  # Token accounting
│   │
│   ├── logs/
│   │   ├── agent.log
│   │   └── safety.log
│   │
│   └── cost/
│       └── model_costs.json                  # Model pricing / per-token config
│
├── schemas/                                  # LEVEL 1 — Data contracts
│   ├── shared/
│   │   └── shared_types.json
│   │
│   ├── l1_planning/
│   │   └── planning_types.json
│   │
│   ├── l2_execution/
│   │   ├── execution_types.json
│   │   └── tool_io_types.json
│   │
│   ├── l3_orchestration/
│   │   └── orchestration_types.json
│   │
│   ├── l4_memory/
│   │   └── memory_types.json
│   │
│   └── l5_safety/
│       └── safety_types.json
│
├── tests/                                    # LEVEL 1 — Global test tree
│   ├── L1_planning/
│   │   ├── resume/
│   │   │   ├── test_strategy_planner_resume.py
│   │   │   ├── test_research_planner_resume.py
│   │   │   └── test_message_planner_resume.py
│   │   │
│   │   ├── outreach/
│   │   │   ├── test_strategy_planner_outreach.py
│   │   │   ├── test_research_planner_outreach.py
│   │   │   └── test_message_planner_outreach.py
│   │   │
│   │   └── shared/
│   │       ├── test_refinement_planner.py
│   │       ├── test_safety_planner.py
│   │       └── test_planner_validation.py
│   │
│   ├── L2_execution/
│   │   ├── resume/
│   │   │   ├── test_resume_generation_executor.py
│   │   │   ├── test_resume_research_executor.py
│   │   │   └── test_resume_validation_executor.py
│   │   │
│   │   ├── outreach/
│   │   │   ├── test_outreach_message_executor.py
│   │   │   ├── test_outreach_research_executor.py
│   │   │   └── test_outreach_validation_executor.py
│   │   │
│   │   └── tools/
│   │       ├── test_bm25_tool.py
│   │       ├── test_dense_retrieval_tool.py
│   │       ├── test_hybrid_router_tool.py
│   │       ├── test_rrf_fusion_tool.py
│   │       ├── test_rag_filter_tool.py
│   │       ├── test_rag_query_rewriter_tool.py
│   │       ├── test_hyde_tool.py
│   │       ├── test_reranker_tool.py
│   │       ├── test_chunking_tool.py
│   │       ├── test_text_cleaning_tool.py
│   │       ├── test_snippet_extraction_tool.py
│   │       ├── test_kg_lookup_tool.py
│   │       ├── test_kg_traversal_tool.py
│   │       ├── test_kg_relation_expand_tool.py
│   │       ├── test_temporal_extraction_tool.py
│   │       ├── test_temporal_invalidation_tool.py
│   │       ├── test_temporal_event_builder_tool.py
│   │       ├── test_embedding_tool.py
│   │       ├── test_search_tool.py
│   │       ├── test_http_tool.py
│   │       ├── test_sql_tool.py
│   │       ├── test_file_tool.py
│   │       ├── test_serialization_tool.py
│   │       ├── test_crypto_hash_tool.py
│   │       └── test_diff_tool.py
│   │
│   ├── L3_orchestration/
│   │   ├── resume/
│   │   │   ├── test_resume_orchestrator_basic.py
│   │   │   └── test_resume_workflow_validation.py
│   │   │
│   │   ├── outreach/
│   │   │   ├── test_outreach_orchestrator_basic.py
│   │   │   └── test_outreach_workflow_validation.py
│   │   │
│   │   └── framework/
│   │       ├── test_dag_engine.py
│   │       ├── test_dag_node.py
│   │       ├── test_dag_runner.py
│   │       ├── test_recursion_controller.py
│   │       └── test_arbitration_engine.py
│   │
│   ├── L4_memory_state/
│   │   ├── temporal/
│   │   │   ├── test_chunking.py
│   │   │   ├── test_statement_extraction.py
│   │   │   ├── test_temporal_range_extraction.py
│   │   │   ├── test_triplet_extraction.py
│   │   │   ├── test_event_generation.py
│   │   │   ├── test_entity_resolution.py
│   │   │   └── test_invalidation.py
│   │   │
│   │   ├── providers/
│   │   │   ├── test_chroma_provider.py
│   │   │   ├── test_postgres_provider.py
│   │   │   ├── test_redis_provider.py
│   │   │   └── test_embedding_provider.py
│   │   │
│   │   └── mappings/
│   │       ├── test_resume_mapping.py
│   │       └── test_outreach_mapping.py
│   │
│   ├── L5_safety/
│   │   ├── filters/
│   │   │   ├── test_pii_filter.py
│   │   │   ├── test_toxicity_detector.py
│   │   │   ├── test_hallucination_detector.py
│   │   │   └── test_injection_detector.py
│   │   │
│   │   ├── policies/
│   │   │   ├── test_resume_policy.py
│   │   │   └── test_outreach_policy.py
│   │   │
│   │   └── validators/
│   │       ├── test_safety_validator.py
│   │       └── test_content_validator.py
│   │
│   ├── integration/
│   │   ├── resume/
│   │   │   ├── test_resume_end_to_end_small_corpus.py
│   │   │   └── test_resume_rag_integration.py
│   │   │
│   │   └── outreach/
│   │       ├── test_outreach_end_to_end_small_corpus.py
│   │       └── test_outreach_rag_integration.py
│   │
│   ├── e2e/
│   │   ├── resume/
│   │   │   └── test_resume_full_stack.py
│   │   └── outreach/
│   │       └── test_outreach_full_stack.py
│   │
│   ├── regression/
│   │   ├── resume/
│   │   │   └── test_resume_regressions.py
│   │   └── outreach/
│   │       └── test_outreach_regressions.py
│   │
│   ├── fixtures/
│   │   ├── resume/
│   │   │   ├── sample_resume_1.json
│   │   │   ├── sample_resume_2.json
│   │   │   └── sample_resume_rag_query.json
│   │   │
│   │   ├── outreach/
│   │   │   ├── sample_outreach_profile_1.json
│   │   │   ├── sample_outreach_profile_2.json
│   │   │   └── sample_outreach_rag_query.json
│   │   │
│   │   └── common/
│   │       ├── small_corpus_docs.json
│   │       └── kg_sample_graph.json
│   │
│   ├── data/
│   │   ├── sample_resumes/
│   │   │   ├── resume_foo.json
│   │   │   └── resume_bar.json
│   │   ├── sample_outreach/
│   │   │   ├── outreach_email_foo.json
│   │   │   └── outreach_email_bar.json
│   │   └── kg_samples/
│   │       ├── kg_nodes.json
│   │       └── kg_edges.json
│   │
│   └── helpers.py                             # Shared test helpers
│
└── runtime/                                   # LEVEL 1 — Centralized caches
    └── cache/                                 # LEVEL 2
        ├── __pycache__/                       # LEVEL 3
        ├── venv/
        ├── mypy/
        ├── pytest/
        ├── ruff/
        └── tmp/


Rules:

* NO additional top-level directories beyond those in this tree unless strictly necessary (and then documented).
* NO additional depth (no Level-4 folders).
* Agentic logic MUST live under `agentic_core/`.
* Apps MUST be thin, under `apps/`.
* Tests MUST live under the single global `/agentic_workflow_10_11/tests/`.
* Any violation MUST be corrected by Windsurf during patching.

==================================================================================================
4 — AGENTIC WORKFLOW (DAG + TOOLING + ROUTING + SAFETY + OBSERVABILITY)
=======================================================================

This section constrains how L1–L5 cooperate at runtime.

---

## 4.1 — DAG ORCHESTRATION (L3)

Workflows MUST follow the canonical 5-step loop:

```text
Mission → Scene → Think → Act → Observe
```

Each **DAG node** (L3) MUST define:

* `InputSchema` (typed)
* `OutputSchema` (typed)
* `FailureModes` (enumerated)
* `Invariants` (what must be true on entry/exit)
* Typed, acyclic transitions (no cycles in the DAG graph)

Constraints:

* Recursion controllers MUST live in `agentic_core/l3_orchestration/framework/`.
* Planning recursion belongs in L1 (pure cognitive recursion).
* L3 MUST NOT call tools directly; it calls L2 executors.
* L3 MUST NOT embed business logic in prompts; it delegates to L1 and L2.

---

## 4.2 — TOOL CONTRACT (L2)

Each tool in `agentic_core/l2_execution/tools/` MUST declare:

* `InputSchema`
* `OutputSchema`
* `FailureModes`
* `Timeout`
* `Retry` policy
* `CircuitBreaker` behavior
* `CostLimit` and cost annotations
* `SafetyChecks` (pre & post)

Constraints:

* Tools MUST NOT orchestrate or plan.
* Tools MUST NOT perform multi-step reasoning; they execute a single bounded action.
* Tools MUST be idempotent where possible, or clearly mark side effects.

---

## 4.3 — MODEL ROUTING

Model usage rules:

* L1 + L3 MUST use frontier reasoning models (for planning and DAG control).
* L2 MUST use efficient models optimized for execution.
* L4 MAY use frontier or efficient models depending on cost/latency.
* L5 MUST use safe, robust models for safety judgments.

Routing MUST enforce:

* Token budgets (max tokens per call, per mission)
* Latency budgets (per step and per mission)
* Cost decorators (attach cost estimates to each call, aggregated across mission)

Routing policy MUST be configurable (per environment: dev/stage/prod).

---

## 4.4 — OBSERVABILITY (EVENT MODEL)

Every agentic action across L1–L5 MUST emit an observability event with:

```text
mission_id
session_id
step_id
layer_id
recursion_depth
trace_id
span_id
parent_span_id
timestamp_start
timestamp_end
latency_ms
model_name
model_version
token_in
token_out
cost_snapshot
tool_name (if L2)
tool_args_redacted
tool_latency_ms
safety_snapshot
error_type (if any)
error_message (if any)
```

Constraints:

* Events MUST be exportable into `/agentic_workflow_10_11/observability/trace/` and `/metrics/` and `/logs/`.
* No PII in logs; use hashing/redaction.
* Traces MUST be OpenTelemetry-compatible.

---

## 4.5 — SAFETY (L5)

Safety MUST provide:

* PII detection and redaction
* Hallucination checks (answers must be grounded in retrieved or known data)
* Injection shielding (defense against prompt injection)
* Constitutional guardrails (domain-specific constraints)
* Data vs. instruction isolation (user data NEVER treated as system instructions)
* Engine-specific overrides under `l5_safety/policies/<engine>/`

Safety policies MUST be enforced for:

* All outbound user-facing content
* All tool invocations that can change external state (emails, DB writes, APIs)

==================================================================================================
5 — MEMORY, TEMPORAL AGENT, RAG, & KG (L4)
==========================================

All Temporal Agent, RAG and KG logic MUST live under:

```text
/agentic_workflow_10_11/agentic_core/l4_memory_state/
```

Submodules (as per tree) MUST be used for:

* `providers/` → DB, vector store, KG backends
* `temporal/` → temporal chunking, statement extraction, temporal ranges, triplets, events, invalidation, entity resolution
* `mappings/` → per-engine mapping (resume/outreach)

Memory types MUST be explicitly modeled:

* Short-term = session state
* Long-term = RAG + KG
* Episodic = temporal events
* Semantic = embeddings
* Action memory = tool outputs

Constraints:

* L1, L2, L3, L5 MUST NOT mutate storage directly; they call into L4 APIs.
* L4 MUST define clear retention & eviction policies.
* Temporal validity MUST be encoded in schemas (`valid_at`, `invalid_at`, etc.).

==================================================================================================
6 — PROMPT GOVERNANCE (INSTRUCTIONAL INJECTION v5)
==================================================

Prompt governance MUST live under:

```text
/agentic_workflow_10_11/prompt_governance/
```

Rules:

* NO prompt text in code.
* ALL prompts MUST be loaded from files (e.g., `.txt`, `.md`, `.json`, `.yaml`), never inline in Python.
* ALL prompts MUST be referenced via a central `Prompt_Registry` (data file or equivalent).
* Prompts MUST implement Instructional Injection v5 layering:

```text
Framing → Context → Reasoning → Tooling → Safety → Output
```

Each prompt bundle MUST:

* Be schema-first (define expected output structure)
* Be deterministic (stable fields, stable ordering)
* Be versioned (semantic versioning: v1.0.0, v1.1.0, etc.)
* Never be deleted; old versions MUST remain available for rollback.

Data vs Instruction:

* User content = data only.
* System / developer / governance prompts = instructions only.
* No mixing.

==================================================================================================
7 — IMPORT HYGIENE (L1–L5 DEPENDENCY DAG)
=========================================

Dependency DAG:

```text
L1 (planning)  = PURE (no imports from L2–L5)
L2 (execution) ← L1
L3 (orchestration) ← L1 + L2
L4 (memory/state) ← none (no upward imports; only used as dependency)
L5 (safety) ← none (no upward imports)
```

Forbidden:

* Any circular imports.
* L4 → L3, L2, L1.
* L5 → L3, L2, L1.
* Cross-engine imports (resume engine importing outreach engine).
* Any duplication of shared directories.

Windsurf MUST:

* Fix imports to obey this DAG.
* Add tests if needed to prevent regressions.

==================================================================================================
8 — TEST STRUCTURE INVARIANT (GLOBAL TEST TREE)
===============================================

A single global `/agentic_workflow_10_11/tests/` tree MUST exist exactly as in Section 3.

Constraints:

* No tests under `apps/`.
* No tests inside engine folders under `agentic_core/`.
* No alternate test trees (e.g., `tests_unit/`, `unit_tests/`, etc.).

Engine-specific tests MUST be separated at file level, for example:

* `tests/L1_planning/resume/...`
* `tests/L1_planning/outreach/...`
* `tests/L2_execution/resume/...`
* `tests/L2_execution/outreach/...`
* etc.

Windsurf MUST:

* Relocate misplaced tests.
* Correct imports and fixtures.
* Ensure every L1–L5 module has at least basic coverage.

==================================================================================================
9 — MODEL CONTEXT PROTOCOL (MCP) INTEGRATION
============================================

Windsurf MUST integrate MCP as the standard for external tools / data sources.

Requirements:

* Only MCP-registered tools may be exposed to the agent runtime.
* MCP tools MUST declare schemas for input and output.
* MCP servers MUST be discoverable and configurable per environment.
* MCP interactions MUST be logged and observable.

Security:

* MCP tool access MUST honor agent-specific ACLs.
* No direct network calls from L1/L2; they MUST go through MCP or sanctioned adapters.

==================================================================================================
10 — GLOBAL SCHEMA LAYER (DATA CONTRACTS)
=========================================

Schemas MUST live under:

```text
/agentic_workflow_10_11/schemas/
```

All domain data MUST be represented with:

* JSON Schema (2020-12) or equivalent
* Auto-generated Pydantic (or equivalent type) models
* Backward-compatibility policy (no breaking changes without version bump)

Constraints:

* No loose dicts crossing layer boundaries; always typed objects.
* Any cross-layer interface MUST be defined in `schemas/`.
* Schema regression tests MUST exist to prevent breaking changes.

==================================================================================================
11 — PROMPT BUILDER (CANONICAL PATTERN)
=======================================

A central Prompt Builder MUST:

* Compose system, developer, and user instructions using Injection v5.
* Enforce the layering: Framing / Context / Reasoning / Tooling / Safety / Output.
* Attach schemas and examples to each prompt call.
* Support prompt diffing and regression evaluation.

Code MUST:

* Load base templates from `prompt_governance/`.
* Fill in variable slots programmatically (goal, constraints, schemas, examples, etc.).
* Never inline large prompt strings directly in L1–L5 code.

==================================================================================================
12 — SELF-CORRECTION & ARBITRATION LAYER
========================================

A self-correction layer MUST exist (typically in L3):

* Critic model (evaluates candidate outputs or plans).
* Verifier model (checks constraints, facts, safety).
* Arbiter (chooses between candidates, or decides to re-plan / re-execute).

This layer:

* MUST operate deterministically (same inputs → same arbitration result).
* MUST log reasoning and arbitration decisions (non-sensitive summaries).
* MUST be testable with golden evaluation cases.

==================================================================================================
13 — AGENT OPS (OBSERVABILITY + RELIABILITY)
============================================

Agent Ops MUST include:

* Token-level cost tracking per mission / per step.
* Latency distributions (p50/p90/p99) per tool, per model, per DAG node.
* Error taxonomy (clear categories: tool_error, model_error, safety_block, etc.).
* Tool reliability scoring (success/failure rates).
* Model reliability scoring (per use-case).
* Canary scenarios for critical flows.

All of this MUST be reflected in `/observability/metrics/` and `/observability/logs/`.

==================================================================================================
14 — SECURITY LAYER (IDENTITY, POLICY, ISOLATION)
=================================================

Security MUST treat:

* Users
* Agents
* Services

as **distinct principals**, each with its own identity and policy.

Requirements:

* Agent identities MUST be distinct from user identities.
* Least privilege: each agent only gets the tools / data it needs.
* Policy Decision Engine (PDE) MUST gate all high-risk actions (e.g., sending messages, mutating DBs).
* Execution environments for code tools MUST be sandboxed (no raw host access).

No secrets:

* Secrets MUST NOT be hard-coded; they must come from secure config.
* Logs MUST NOT contain secrets or raw tokens.

==================================================================================================
15 — HUMAN-IN-THE-LOOP (HITL) SUPPORT
=====================================

The system MUST support:

* Explicit HITL checkpoints in DAGs (L3).
* Human approval / rejection flows for consequential actions.
* Human-provided corrections feeding back into evaluation sets.

HITL interactions MUST be:

* Logged as structured events.
* Used to create new golden examples for evaluation.

==================================================================================================
16 — RAG & KNOWLEDGE OPTIMIZATION
=================================

Retrieval MUST:

* Support hybrid retrieval (dense + sparse + RRF or equivalent).
* Support query rewriting (HYDE-style or similar) where appropriate.
* Avoid duplicative context in the prompt (deduping / clustering).
* Respect freshness and temporal validity when using temporal KGs.

Constraints:

* RAG MUST be deterministic given the same corpus and query.
* RAG components MUST be testable with golden queries.

==================================================================================================
17 — EVALUATION FRAMEWORK
=========================

Evaluation MUST include:

* Golden datasets (human-annotated) for core flows.
* LLM-as-Judge style semantic evaluation (for quality) where human review is infeasible at scale.
* Regression evaluation per model / prompt version change.
* Toolpath evaluation (checking correct tools were used with correct arguments).

CI/CD:

* Pull requests that change L1–L5, schemas, prompts, or tools MUST run the evaluation suite.
* Regressions MUST block merges unless explicitly overridden with justification.

==================================================================================================
18 — DEPLOYMENT LAYER (L6 APPLICATION)
======================================

While not part of L1–L5, deployment rules are required:

* A REST (or equivalent) interface MUST be defined for the main agent flows.
* Sessions MUST be managed cleanly (session IDs, expiring sessions).
* AuthN / AuthZ MUST protect all endpoints.
* Environments: dev, staging, prod MUST be separated.
* Model versions MUST be pinned per environment.
* Rollbacks MUST be possible if quality degrades.

==================================================================================================
19 — VALIDATION GATE
====================

Before ANY Phase is considered complete, ALL of the following MUST be TRUE:

* 0 import errors
* 0 pytest failures
* 0 lint (Ruff) errors
* 0 mypy blockers (if mypy is used)
* No circular imports
* L1–L5 boundaries intact (per Section 7)
* DAGs valid (no cycles, correct schemas)
* Retrieval deterministic and correct
* Temporal agent functioning and consistent
* Safety enforced and effective
* Zero-loss continuity preserved (no behavior loss)

ANY failure MUST trigger the PATCH_LOOP again.

==================================================================================================
20 — MODE-B PATCH LOOP
======================

PATCH_LOOP:

```text
LOOP:
  • Emit patches (apply_patch + write_to_file ONLY)
  • Run validations (imports, tests, lint, type checks, structure)
  • If ANY requirement fails → continue patching
EXIT ONLY when ALL required keys are TRUE.
```

VALIDATION_LOOP:

* MUST output a TRUE/FALSE matrix for each key in Section 19.
* MUST end with the exact line:

```text
PHASE <N> VALIDATION COMPLETE — ALL KEYS TRUE.
```

No explanations. No extra text. Only the matrix + the completion line.

==================================================================================================
END — WINDSURF GLOBAL RULES (FINAL COMPREHENSIVE, ZERO-LOSS EDITION)
====================================================================

```
