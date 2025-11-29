# ==================================================================================================
# WINDSURF GLOBAL RULES — CLEAN MODE-B VERSION
# ==================================================================================================
# Windsurf MUST load and enforce ALL rules in this file. These rules override ALL chat instructions
# and control Windsurf's behavior in ALL Phases.

# Windsurf MUST operate ONLY in Mode-B:
#   • PATCH Phase → apply_patch and write_to_file ONLY
#   • VALIDATION Phase → TRUE/FALSE table + completion line ONLY
# No narrative, no explanations, no shell commands, no reasoning text.

# ==================================================================================================
# 0 — EXECUTION MODEL
# ==================================================================================================
Windsurf MUST:
  • modify ANY file as needed (code, tests, configs, schemas, prompts)
  • ALWAYS self-correct violations of these rules
  • NEVER ask questions or stop early
  • continue patching until ALL validations are TRUE

Modes:
  • PATCH_LOOP → apply_patch/write_to_file ONLY
  • VALIDATION_LOOP → TRUE/FALSE + completion line ONLY

# ==================================================================================================
# 1 — FILE OPERATIONS
# ==================================================================================================
Rules:
  • Existing files → apply_patch
  • New files → write_to_file
  • Directories → created implicitly
  • No placeholders, stubs, or partial diffs
  • Ambiguity MUST be resolved toward rule compliance and zero-loss continuity

# ==================================================================================================
# 2 — ZERO-LOSS CONTINUITY
# ==================================================================================================
Windsurf MUST preserve ALL existing capabilities.  
No functionality may disappear or degrade.  
Duplicate or conflicting logic MUST be merged into a single working version.

# ==================================================================================================
# 3 — STRICT L1–L5 LAYERING
# ==================================================================================================
L1 Planning:
  • reasoning, planning, decomposition, critics

L2 Execution:
  • tool clients, external I/O, DB, RAG execution

L3 Orchestration:
  • DAGs, routing, workflow control

L4 Memory/State:
  • persistence, caches, embeddings, KG, temporal memory

L5 Safety:
  • safety validation, policy enforcement, escalation

Forbidden:
  • L1→L2/L3  
  • L2→L3 internals  
  • L4→orchestration/provider internals  
  • ANY upward imports  
  • ANY circular imports  

Apps MUST be thin shells (adapters/, pipelines/ ONLY).  
Agentic logic MUST live ONLY in agentic_core.

# ==================================================================================================
# 4 — DAG RULES (L3)
# ==================================================================================================
All workflows MUST implement:
  • Mission → Scene → Think → Act → Observe

Each DAG node MUST define:
  • InputSchema, OutputSchema, FailureModes, Invariants
  • typed, acyclic transitions

All DAG logic MUST reside in L3.

# ==================================================================================================
# 5 — CONTEXT + RETRIEVAL RULES
# ==================================================================================================
Windsurf MUST enforce:
  • deterministic retrieval  
  • curated context windows  
  • relevance-based selection  
  • hybrid retrieval (BM25 + dense)  

# ==================================================================================================
# 6 — TOOLING RULES (L2)
# ==================================================================================================
All tools MUST include:
  • retry/backoff  
  • timeouts  
  • circuit breaker  
  • typed I/O  
  • observability spans  
  • cost tracking  

Untyped or unsafe tools MUST be wrapped.

# ==================================================================================================
# 7 — OBSERVABILITY
# ==================================================================================================
All agentic operations MUST emit:
  • trace IDs, spans, logs, metrics  
  • DAG transitions, tool metadata  
  • safety decisions  

Missing telemetry MUST be added.

# ==================================================================================================
# 8 — SAFETY (L5)
# ==================================================================================================
Windsurf MUST enforce:
  • PII checks  
  • hallucination checks  
  • sensitive-content filters  
  • escalation + risk routing  
  • gating at L1, L2, L3, and output  

# ==================================================================================================
# 9 — COST RULES
# ==================================================================================================
Windsurf MUST enforce:
  • model routing (reasoning → expensive, execution → cheap)
  • token + latency budgets
  • bounded caches with eviction

# ==================================================================================================
# 10 — VALIDATION GATE
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
  • zero-loss continuity maintained

ANY failure MUST trigger patch loop.

# ==================================================================================================
# 11 — MODE-B PATCH LOOP
# ==================================================================================================
PATCH_LOOP:
  LOOP:
    • emit patches
    • run validations
    • if ANY key fails → continue patching
  EXIT ONLY when ALL TRUE

VALIDATION_LOOP:
  • TRUE/FALSE table only
  • completion line:
        PHASE <N> VALIDATION COMPLETE — ALL KEYS TRUE.

# ==================================================================================================
# 12 — TEST FOLDER STRUCTURE INVARIANT
# ==================================================================================================
tests/
  L1_planning/
  L2_execution/
  L3_orchestration/
  L4_memory_state/
  L5_safety/
  integration/
  e2e/
  unit/
  regression/
  observability/
  model_routing/
  stress/
  sandbox/
  shared/

Windsurf MUST:
  • relocate misplaced tests
  • delete tests under apps/
  • update imports, fixtures, conftests, datasets, golden files
  • maintain enforcement after ANY refactor

# ==================================================================================================
# END — WINDSURF GLOBAL RULES (CLEAN MODE-B VERSION)
# ==================================================================================================
