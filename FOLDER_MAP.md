# FOLDER_MAP.md  
# Agentic-Workflow-10_10  
A learnability-first map of every meaningful folder in the project, explaining  
what each folder does, how it fits into the OpenAI L1–L5 agentic architecture,  
and where documentation for each layer must live.

This version includes the rule:  
**Each major folder must contain a `docs/` subfolder where ALL local documentation, READMEs, reports, and summaries for that folder must go.**  
No documentation is permitted at the repo root.

---

# ======================
# TOP-LEVEL STRUCTURE
# ======================

Your real project code lives in the following major folders:

```
config/
core/
eval/
infra/
infrastructure/        ← legacy (to be merged into infra)
l1/
l2/
l4/
l5/
meta/
orchestration/
providers/
retrievers/
runtime/
tools/
```

Each of these MUST contain:
```
docs/
    README.md
    layer_notes.md
    design_reports/
    schema_docs/
    evaluations/
```

Example:
```
l1/
   docs/
      README.md
      planning_overview.md
```

---

# ======================================================
# 1. ROOT-LEVEL PYTHON FILES — “TOOLS & COMMAND SURFACE”
# ======================================================

| File | Purpose |
|------|---------|
| **atomic_integration_bridge.py** | Integration glue for external SDKs / app surfaces. |
| **dependency_analyzer.py** | Builds dependency graph. |
| **dependency_report.json** | Output of dependency analyzer. |
| **fix_imports.py** | Automates import path rewrites. |
| **update_imports_reorganization.py** | Helper for migration / refactors. |
| **graph_query.py** | Query interface for KG/Neo4j. |
| **graph_store_neo4j.py** | Neo4j storage layer. |
| **import_check.py** | Validates module imports. |
| **observability.py** | Central telemetry/logging. |
| **sdk_validation_test.py** / `sdk_validation_results.json` | Provider SDK validation. |
| **pytest.ini** | Global PyTest config. |

**Rule:**  
Root-level READMEs, design docs, and summaries MUST go into:

```
root_docs/
    README.md
    architecture_overview.md
    change_history.md
```

No documentation stays at the root outside `root_docs/`.

---

# ======================================
# 2. config/ — “Profiles & Parameters”
# ======================================

**Contains:**  
- `meta_profile.py`

**Purpose:**  
Central configuration & profile definitions used across all layers.

**Docs location:**  
```
config/docs/
    README.md
    profiles_overview.md
    config_schema.md
```

---

# ================================================
# 3. core/ — “Agent Kernel: Registry & Messaging”
# ================================================

**Contains:**  
- `agent_bus.py`
- `agent_registry.py`
- `agent_router_policy.py`

**Purpose:**  
Kernel-level abstractions: registry, messaging bus, routing policy.

**Docs:**  
```
core/docs/
    README.md
    agent_bus.md
    registry_design.md
```

---

# ===============================================
# 4. eval/ — “Self-Diagnosis & Health Checking”
# ===============================================

**Contains:**  
`health/` with:  
- `adapter.py`  
- `failure_detector.py`  
- `repair_policies.py`

**Purpose:**  
Self-repair, failure detection, health scoring.

**Docs:**  
```
eval/docs/
    README.md
    health_system.md
    evaluation_reports/
```

---

# =================================================
# 5. infra/ — “Context, Routing, Reasoning Utilities”
# =================================================

**Subpackages:**  
- `context_engine/`
- `model_routing/`
- `reasoning/`

**Purpose:**  
Reusable infrastructure powering L1–L3:
- context window assembly  
- model selection  
- reasoning primitives  

**Docs:**  
```
infra/docs/
    README.md
    reasoning_algorithms.md
    context_engine_schema.md
    routing_policies.md
```

---

# ==================================================================
# 6. infrastructure/ — “Legacy Infra (Duplicate of infra/)”
# ==================================================================

**Purpose:**  
Old infrastructure folder; must be merged with `infra/`.

**Docs:**  
```
infrastructure/docs/
    migration_plan.md
```

---

# ============================
# 7. l1/ — “Planning Layer”
# ============================

**Contains:**  
- `vector_search_planning.py`

**Purpose:**  
Pure planning. No execution.

**Docs:**  
```
l1/docs/
    README.md
    planning_methods.md
    planner_examples.md
```

---

# ==========================
# 8. l2/ — “Action Layer”
# ==========================

**Contains:**  
- `factual_qa.py`
- `kg_writer.py`

**Purpose:**  
Execution of tools & external actions.

**Docs:**  
```
l2/docs/
    README.md
    tool_catalog.md
    execution_policies.md
```

---

# ==========================
# 9. l4/ — “Memory Layer”
# ==========================

**Contains:**  
- `manager.py`
- `types.py`

**Purpose:**  
State, memory, persistence.

**Docs:**  
```
l4/docs/
    README.md
    state_machine.md
    memory_architecture.md
```

---

# ==========================
# 10. l5/ — “Safety Layer”
# ==========================

**Contains:**  
- `injection_detection.py`
- `policy.py`
- `types.py`

**Purpose:**  
Safety, policy constraints, security checks.

**Docs:**  
```
l5/docs/
    README.md
    safety_policies.md
    injection_detection_specs.md
```

---

# ========================================
# 11. meta/ — “Meta-Reasoning & Validation”
# ========================================

**Contains:**  
- `cache/redis_cache.py`
- `schema_validation.py`
- `retrieval/hybrid_ranker.py`
- `metacognition/`

**Purpose:**  
Self-reasoning, schema validation, hybrid ranking.

**Docs:**  
```
meta/docs/
    README.md
    hybrid_ranker_algorithm.md
    schema_validation.md
    metacognition_notes.md
```

---

# =============================
# 12. orchestration/ — “L3”
# =============================

**Purpose:**  
Workflow-level controllers and routing.

**Docs:**  
```
orchestration/docs/
    README.md
    workflow_graphs.md
    controllers.md
```

---

# ===================================
# 13. providers/ — “External APIs”
# ===================================

**Purpose:**  
Wrap OpenAI, Anthropic, Pinecone, Redis, etc.

**Docs:**  
```
providers/docs/
    README.md
    api_wrappers_overview.md
    provider_capabilities.md
```

---

# =====================================
# 14. retrievers/ — “RAG Components”
# =====================================

**Docs:**  
```
retrievers/docs/
    README.md
    retriever_catalog.md
    RAG_pipelines.md
```

---

# ============================
# 15. runtime/ — “Runtime Glue”
# ============================

**Docs:**  
```
runtime/docs/
    README.md
    runtime_flow.md
```

---

# ============================
# 16. tools/ — “Utility Tools”
# ============================

**Docs:**  
```
tools/docs/
    README.md
    utility_reference.md
```

---

# ====================
# ROOT DOCS DIRECTORY
# ====================

All project-wide documentation must go here, not in root:

```
root_docs/
    README.md
    architecture_overview.md
    design_history.md
    roadmap.md
```

---

# END OF MAP
