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
/agentic_workflow_10_11                     # LEVEL 0
│
├── agentic_core/                           # LEVEL 1
│   │
│   ├── l1_planning/                        # LEVEL 2 (SHARED — NO ENGINE SPLITS)
│   │   ├── planners/                       # LEVEL 3
│   │   │   ├── strategy_planner.py         # LEVEL 4
│   │   │   ├── research_planner.py
│   │   │   ├── message_planner.py
│   │   │   ├── refinement_planner.py
│   │   │   └── safety_planner.py
│   │   ├── schemas/                        # LEVEL 3
│   │   │   ├── strategy_schema.json        # LEVEL 4
│   │   │   ├── research_schema.json
│   │   │   ├── message_schema.json
│   │   │   └── refinement_schema.json
│   │   └── utils/                          # LEVEL 3
│   │       ├── planning_utils.py           # LEVEL 4
│   │       └── planner_validation.py
│   │
│   ├── l2_execution/                       # LEVEL 2
│   │   ├── tools/                          # LEVEL 3
│   │   │   ├── rag_tool.py                 # LEVEL 4
│   │   │   ├── search_tool.py
│   │   │   ├── http_tool.py
│   │   │   ├── sql_tool.py
│   │   │   ├── file_tool.py
│   │   │   └── embedding_tool.py
│   │   ├── engines/                        # LEVEL 3
│   │   │   ├── resume/                     # LEVEL 4
│   │   │   │   ├── resume_generation_executor.py
│   │   │   │   ├── resume_research_executor.py
│   │   │   │   └── resume_validation_executor.py
│   │   │   └── outreach/                   # LEVEL 4
│   │   │       ├── outreach_message_executor.py
│   │   │       ├── outreach_research_executor.py
│   │   │       └── outreach_validation_executor.py
│   │   ├── wrappers/                       # LEVEL 3
│   │   │   └── execution_wrappers.py       # LEVEL 4
│   │   └── utils/                          # LEVEL 3
│   │       ├── execution_utils.py          # LEVEL 4
│   │       └── retry_policies.py
│   │
│   ├── l3_orchestration/                   # LEVEL 2
│   │   ├── framework/                      # LEVEL 3
│   │   │   ├── dag_engine.py               # LEVEL 4
│   │   │   ├── dag_node.py
│   │   │   ├── dag_runner.py
│   │   │   └── recursion_controller.py
│   │   ├── engines/                        # LEVEL 3
│   │   │   ├── resume/                     # LEVEL 4
│   │   │   │   ├── resume_orchestrator.py
│   │   │   │   └── resume_workflow_dag.yaml
│   │   │   └── outreach/                   # LEVEL 4
│   │   │       ├── outreach_orchestrator.py
│   │   │       └── outreach_workflow_dag.yaml
│   │   └── utils/                          # LEVEL 3
│   │       ├── orchestration_utils.py      # LEVEL 4
│   │       └── dag_validation.py
│   │
│   ├── l4_memory_state/                    # LEVEL 2
│   │   ├── providers/                      # LEVEL 3
│   │   │   ├── chroma_provider.py          # LEVEL 4
│   │   │   ├── postgres_provider.py
│   │   │   └── embedding_provider.py
│   │   ├── temporal/                       # LEVEL 3
│   │   │   ├── chunking.py                 # LEVEL 4
│   │   │   ├── statement_extraction.py
│   │   │   ├── temporal_range_extraction.py
│   │   │   ├── triplet_extraction.py
│   │   │   ├── event_generation.py
│   │   │   ├── entity_resolution.py
│   │   │   └── invalidation.py
│   │   └── mappings/                       # LEVEL 3
│   │       ├── resume_mapping.py           # LEVEL 4
│   │       └── outreach_mapping.py
│   │
│   └── l5_safety/                          # LEVEL 2
│       ├── filters/                        # LEVEL 3
│       │   ├── pii_filter.py               # LEVEL 4
│       │   ├── toxicity_detector.py
│       │   └── hallucination_detector.py
│       ├── policies/                       # LEVEL 3
│       │   ├── resume_policy.yaml          # LEVEL 4
│       │   └── outreach_policy.yaml
│       └── validators/                     # LEVEL 3
│           └── safety_validator.py         # LEVEL 4
│
├── apps/                                   # LEVEL 1
│   ├── resume_engine/                      # LEVEL 2
│   │   ├── adapters/                       # LEVEL 3
│   │   │   └── resume_adapter.py           # LEVEL 4
│   │   └── pipelines/                      # LEVEL 3
│   │       ├── resume_pipeline.py          # LEVEL 4
│   │       └── resume_enrichment.py
│   │
│   └── outreach_engine/                    # LEVEL 2
│       ├── adapters/                       # LEVEL 3
│       │   └── outreach_adapter.py         # LEVEL 4
│       └── pipelines/                      # LEVEL 3
│           ├── outreach_pipeline.py        # LEVEL 4
│           └── outreach_enrichment.py
│
├── prompt_governance/                      # LEVEL 1
│   ├── Layered_Injection_Bundles/          # LEVEL 2
│   │   ├── framing/                        # LEVEL 3
│   │   ├── context/                        # LEVEL 3
│   │   ├── reasoning/                      # LEVEL 3
│   │   ├── tooling/                        # LEVEL 3
│   │   ├── safety/                         # LEVEL 3
│   │   └── output/                         # LEVEL 3
│   ├── l1_planning/                        # LEVEL 2
│   │   ├── strategy.txt                    # LEVEL 3
│   │   ├── research.txt                    # LEVEL 3
│   │   └── safety.txt                      # LEVEL 3
│   ├── l2_execution/                       # LEVEL 2
│   │   ├── resume_execution.txt            # LEVEL 3
│   │   └── outreach_execution.txt          # LEVEL 3
│   └── l3_orchestration/                   # LEVEL 2
│       ├── workflow_supervision.txt        # LEVEL 3
│       └── dag_guidance.txt                # LEVEL 3
│
├── observability/                          # LEVEL 1
│   ├── trace/                              # LEVEL 2
│   │   ├── dag_spans.log                   # LEVEL 3
│   │   └── tool_spans.log                  # LEVEL 3
│   ├── metrics/                            # LEVEL 2
│   │   ├── cost_metrics.json               # LEVEL 3
│   │   └── token_usage.json                # LEVEL 3
│   ├── logs/                               # LEVEL 2
│   │   ├── agent.log                       # LEVEL 3
│   │   └── safety.log                      # LEVEL 3
│   └── cost/                               # LEVEL 2
│       └── model_costs.json                # LEVEL 3
│
├── schemas/                                # LEVEL 1
│   ├── shared/                             # LEVEL 2
│   │   └── shared_types.json               # LEVEL 3
│   ├── l1_planning/                        # LEVEL 2
│   │   └── planning_types.json             # LEVEL 3
│   ├── l2_execution/                       # LEVEL 2
│   │   └── execution_types.json            # LEVEL 3
│   ├── l3_orchestration/                   # LEVEL 2
│   │   └── orchestration_types.json        # LEVEL 3
│   ├── l4_memory/                          # LEVEL 2
│   │   └── memory_types.json               # LEVEL 3
│   └── l5_safety/                          # LEVEL 2
│       └── safety_types.json               # LEVEL 3
│
├── tests/                                  # LEVEL 1
│   ├── L1_planning/                        # LEVEL 2
│   │   ├── resume/                         # LEVEL 3
│   │   ├── outreach/                       # LEVEL 3
│   │   └── shared/                         # LEVEL 3
│   ├── L2_execution/                       # LEVEL 2
│   │   ├── resume/                         # LEVEL 3
│   │   ├── outreach/                       # LEVEL 3
│   │   └── tools/                          # LEVEL 3
│   ├── L3_orchestration/                   # LEVEL 2
│   │   ├── resume/                         # LEVEL 3
│   │   ├── outreach/                       # LEVEL 3
│   │   └── framework/                      # LEVEL 3
│   ├── L4_memory_state/                    # LEVEL 2
│   │   ├── temporal/                       # LEVEL 3
│   │   ├── providers/                      # LEVEL 3
│   │   └── mappings/                       # LEVEL 3
│   ├── L5_safety/                          # LEVEL 2
│   │   ├── filters/                        # LEVEL 3
│   │   ├── policies/                       # LEVEL 3
│   │   └── validators/                     # LEVEL 3
│   ├── integration/                        # LEVEL 2
│   │   ├── resume/                         # LEVEL 3
│   │   └── outreach/                       # LEVEL 3
│   ├── e2e/                                # LEVEL 2
│   │   ├── resume/                         # LEVEL 3
│   │   └── outreach/                       # LEVEL 3
│   ├── regression/                         # LEVEL 2
│   │   ├── resume/                         # LEVEL 3
│   │   └── outreach/                       # LEVEL 3
│   ├── fixtures/                           # LEVEL 2
│   │   ├── resume/                         # LEVEL 3
│   │   ├── outreach/                       # LEVEL 3
│   │   └── common/                         # LEVEL 3
│   ├── data/                               # LEVEL 2
│   │   ├── sample_resumes/                 # LEVEL 3
│   │   ├── sample_outreach/                # LEVEL 3
│   │   └── kg_samples/                     # LEVEL 3
│   └── helpers.py                          # LEVEL 2 (file)
│
└── runtime/                                 # LEVEL 1
    └── cache/                               # LEVEL 2
        ├── __pycache__/                     # LEVEL 3
        ├── venv/                            # LEVEL 3
        ├── mypy/                            # LEVEL 3
        ├── pytest/                          # LEVEL 3
        ├── ruff/                            # LEVEL 3
        └── tmp/                             # LEVEL 3
```

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
