==================================================================================================
# WINDSURF GLOBAL RULES — MODE-B VERSION
# FINAL CONSOLIDATED + ZERO-LOSS + OPENAI-ALIGNED AGENTIC RULESET
# ==================================================================================================
# Windsurf MUST load and enforce ALL rules in this file. These rules override all other instructions
# and govern every Phase (PATCH + VALIDATION).

# Windsurf MUST operate ONLY in Mode-B:
#   • PATCH Phase → apply_patch + write_to_file ONLY
#   • VALIDATION Phase → TRUE/FALSE matrix + completion line ONLY
# No narrative, no explanations, no shell commands, no reasoning text.

# ==================================================================================================
# 0 — EXECUTION MODEL
# ==================================================================================================
Windsurf MUST:
  • modify ANY file as needed
  • ALWAYS self-correct violations of these rules
  • NEVER ask questions
  • NEVER stop early
  • continue patching until ALL validations pass

Modes:
  • PATCH_LOOP → apply_patch + write_to_file ONLY
  • VALIDATION_LOOP → TRUE/FALSE + completion line ONLY

# ==================================================================================================
# 1 — FILE OPERATIONS
# ==================================================================================================
Rules:
  • Existing files → apply_patch
  • New files → write_to_file
  • Directories → created implicitly
  • No placeholders, no partial diffs
  • All ambiguity MUST resolve toward rule compliance + zero-loss continuity

# ==================================================================================================
# 1.1 — CACHE HANDLING RULES
# ==================================================================================================
ALL cache, venv, and Python-generated artifacts MUST be relocated into:

    /runtime/cache/

MANDATORY mappings:
    __pycache__           → /runtime/cache/__pycache__/
    .venv                 → /runtime/cache/venv/
    .mypy_cache           → /runtime/cache/mypy/
    .pytest_cache         → /runtime/cache/pytest/
    .ruff_cache           → /runtime/cache/ruff/
    .cache                → /runtime/cache/tmp/
    cache                 → /runtime/cache/tmp/
    mycache               → /runtime/cache/tmp/
    tmp / temp / scratch  → /runtime/cache/tmp/

Windsurf MUST:
  • ensure these folders NEVER appear anywhere else
  • add /runtime/cache/ to .gitignore
  • relocate new caches automatically
  • preserve zero-loss continuity FOREVER

# ==================================================================================================
# 2 — ZERO-LOSS CONTINUITY
# ==================================================================================================
Windsurf MUST preserve ALL existing capabilities.
No regressions.  
No deletions.  
Duplicate/conflicting logic MUST be merged into a single correct version.

# ==================================================================================================
# 3 — CANONICAL REPOSITORY FOLDER ORGANIZATION (FULL + CONSOLIDATED)
# ==================================================================================================
Windsurf MUST enforce the following **complete repository folder organization**.
This section is the single authoritative directory specification.

## 3.1 — ROOT FOLDERS
```

/agentic_core/              # All agentic logic (L1–L5)
/apps/                      # Thin engine entrypoints
/prompt_governance/         # Instructional Injection + prompt governance
/observability/             # Traces, logs, metrics, cost
/tests/                     # Unified test tree
/runtime/cache/             # All caches relocated here

```

## 3.2 — AGENTIC CORE (L1–L5)
```

/agentic_core
│
├── l1_planning/                           # SHARED cognition
│
├── l2_execution/                          # Execution layer
│   ├── tools/                             # SHARED tools (HTTP, SQL, RAG)
│   └── engines/
│       ├── resume/
│       └── outreach/
│
├── l3_orchestration/                      # Workflow supervision
│   ├── framework/                         # SHARED DAG framework
│   └── engines/
│       ├── resume/
│       └── outreach/
│
├── l4_memory_state/                       # Memory + Temporal Agent + KG
│   ├── providers/                         # SHARED DB/vector-store providers
│   ├── temporal/
│   │    ├── chunking/
│   │    ├── statement_extraction/
│   │    ├── temporal_range_extraction/
│   │    ├── triplet_extraction/
│   │    ├── event_generation/
│   │    ├── entity_resolution/
│   │    ├── invalidation/
│   │    └── kg_ingestion/
│   └── mappings/
│       ├── resume/
│       └── outreach/
│
└── l5_safety/                             # Safety & policy engine
├── filters/                           # SHARED detectors (PII, hallucination, toxicity)
└── policies/
├── resume/
└── outreach/

```

**Rules:**
- SHARED:  
  l1_planning/, l2_execution/tools/, l3_orchestration/framework/, l4_memory_state/providers/, l5_safety/filters/
- ENGINE-SPECIFIC:  
  l2_execution/engines/*, l3_orchestration/engines/*, l4_memory_state/mappings/*, l5_safety/policies/*
- Agentic logic MUST NOT appear outside /agentic_core/.
- Engines MUST NOT import each other.

## 3.3 — APPS (ENTRYPOINTS ONLY)
```

/apps
│
├── resume_engine/
│    ├── adapters/
│    └── pipelines/
│
└── outreach_engine/
├── adapters/
└── pipelines/

```
Apps MUST NOT contain agentic logic.

## 3.4 — PROMPT GOVERNANCE
```

/prompt_governance/
Instructional_Injection_v5.md
Prompt_Constitution.md
Prompt_Registry.json
Layered_Injection_Bundles/
l1_planning/
l2_execution/
l3_orchestration/
l4_memory/
l5_safety/

```

## 3.5 — OBSERVABILITY
```

/observability/
trace/
metrics/
logs/
cost/

```

## 3.6 — TESTS (FULL GLOBAL STRUCTURE)
```

/tests
│
├── L1_planning/
├── L2_execution/
├── L3_orchestration/
├── L4_memory_state/
├── L5_safety/
│
├── integration/
├── e2e/
├── unit/
├── regression/
├── observability/
├── model_routing/
├── stress/
├── sandbox/
└── shared/
├── conftest.py
├── fixtures/
│     ├── resume/
│     ├── outreach/
│     └── common/
├── data/
└── helpers.py

```

## 3.7 — CACHE DIRECTORY
```

/runtime/cache/
**pycache**/
venv/
mypy/
pytest/
ruff/
tmp/

```

This folder is ignored and holds ALL caches.

# ==================================================================================================
# 4 — AGENTIC WORKFLOW (DAG + TOOLING + ROUTING + SAFETY + OBSERVABILITY)
# ==================================================================================================

## 4.1 — DAG ORCHESTRATION (L3)
Workflows MUST follow:

    Mission → Scene → Think → Act → Observe

Each DAG node MUST define:
  • InputSchema  
  • OutputSchema  
  • FailureModes  
  • Invariants  
  • typed, acyclic transitions  

Recursion controllers MUST live in L3; planning recursion in L1.

## 4.2 — TOOL CONTRACT (L2)
Each tool MUST declare:
  InputSchema  
  OutputSchema  
  FailureModes  
  Timeout  
  Retry policy  
  Circuit breaker  
  Cost limits  
  Safety checks

Tools MUST NOT reason or orchestrate.

## 4.3 — MODEL ROUTING
L1 + L3 use frontier reasoning models.  
L2 uses efficient execution models.  
Routing MUST enforce:
  • token budgets  
  • latency budgets  
  • cost decorators  

## 4.4 — OBSERVABILITY
All agentic actions MUST emit:

```

mission_id
step_id
recursion_depth
trace_id
spans
logs
metrics
cost_snapshot
safety_snapshot
tool_metadata

```

## 4.5 — SAFETY (L5)
Safety MUST include:
  • PII detection  
  • hallucination checks  
  • injection shielding  
  • constitutional guardrails  
  • data vs instruction isolation  
  • engine-specific overrides under l5_safety/policies/<engine>/

# ==================================================================================================
# 5 — MEMORY, TEMPORAL AGENT, RAG, & KG (L4)
# ==================================================================================================
ALL Temporal Agent + KG logic MUST exist under:

```

agentic_core/l4_memory_state/

```

Including:
  chunking/  
  statement_extraction/  
  temporal_range_extraction/  
  triplet_extraction/  
  event_generation/  
  entity_resolution/  
  invalidation/  
  kg_ingestion/  

Memory types:
  • short-term = session  
  • long-term = RAG + KG  
  • episodic = temporal events  
  • semantic = embeddings  
  • action memory = tool outputs  

Windsurf MUST enforce:
  • typed schemas  
  • deterministic serialization  
  • retention + eviction rules  
  • NO direct mutation from L1/L2/L3/L5

# ==================================================================================================
# 6 — PROMPT GOVERNANCE (INSTRUCTIONAL INJECTION v5)
# ==================================================================================================
Prompt governance MUST live under /prompt_governance/.

Rules:
  • NO prompt text in code  
  • ALL prompts MUST load via Prompt_Registry.json  
  • MUST follow Injection v5 layers:
    Framing → Context → Reasoning → Tooling → Safety → Output  
  • Prompts MUST be schema-first, deterministic, versioned  
  • NEVER delete prompt versions (only supersede)  
  • Maintain strict separation of data vs instructions

# ==================================================================================================
# 7 — IMPORT HYGIENE
# ==================================================================================================
Dependency DAG MUST be enforced:

```

L1 = pure
L2 ← L1
L3 ← L1 + L2
L4 ← none (no upward imports)
L5 ← none (no upward imports)

```

Forbidden:
  • ANY circular imports  
  • L4→L3  
  • L5→L3 or L5→L1  
  • ANY cross-engine imports  
  • ANY duplication of shared directories  

# ==================================================================================================
# 8 — TEST FOLDER STRUCTURE INVARIANT (FULL + ZERO-LOSS)
# ==================================================================================================
A SINGLE global /tests/ tree MUST exist (defined in Section 3.6).

Engine-specific tests MUST exist ONLY at file level:
```

tests/L1_planning/test_resume_planner.py
tests/L1_planning/test_outreach_planner.py
tests/L2_execution/test_resume_rag_executor.py
tests/L2_execution/test_outreach_contact_research_executor.py
tests/L3_orchestration/test_resume_orchestrator.py
tests/L3_orchestration/test_outreach_orchestrator.py

```

Forbidden:
  • tests under apps/
  • duplicated test trees
  • tests inside engine folders
  • flat, unlabeled test directories

Windsurf MUST:
  • relocate misplaced tests  
  • correct imports and fixtures  
  • enforce cross-engine independence  
  • enforce prompt usage through prompt_governance  
  • ensure every L1–L5 module has matching tests  

# ==================================================================================================
# 9 — VALIDATION GATE
# ==================================================================================================
Before completion ANY Phase:
  • 0 import errors  
  • 0 pytest failures  
  • 0 lint errors  
  • 0 mypy blockers  
  • no circular imports  
  • L1–L5 boundaries valid  
  • DAG valid  
  • deterministic retrieval  
  • observability correct  
  • safety correct  
  • zero-loss continuity guaranteed  

ANY failure MUST trigger patch loop.

# ==================================================================================================
# 10 — MODE-B PATCH LOOP
# ==================================================================================================
PATCH_LOOP:
  LOOP:
    • emit patches
    • run validations
    • if ANY key fails → continue patching
  EXIT ONLY when ALL TRUE

VALIDATION_LOOP:
  • MUST output TRUE/FALSE matrix
  • completion line:
        PHASE <N> VALIDATION COMPLETE — ALL KEYS TRUE.

# ==================================================================================================
# END — WINDSURF GLOBAL RULES (FINAL CONSOLIDATED, ZERO-LOSS EDITION)
# ==================================================================================================
```

