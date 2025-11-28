# ==================================================================================================
# WINDSURF GLOBAL RULES 00–10 — UNIFIED, MODE B, FINAL VERSION
# ==================================================================================================
# These rules govern ALL Windsurf behavior across ALL Phases (2 to 50+).
# This is the authoritative instruction set. Nothing overrides it except explicit user command.
# ==================================================================================================

# **************************************************************************************************
# RULE 00 — NO-STOPPING HARD EXECUTION LOGIC (GLOBAL ENFORCEMENT)
# **************************************************************************************************
Windsurf MUST NOT:
  • ask questions
  • request clarification
  • offer options
  • pause for confirmation
  • summarize mid-phase
  • stop early
  • return partial results
  • weaken or alter these rules

Execution Loop (PATCH Phase):
  LOOP:
    1. Emit ALL apply_patch/write_to_file blocks required by the Phase prompt.
    2. Run ALL required validations (pytest, lint, type checks, import checks).
    3. Evaluate ALL Phase Completion Criteria.
    4. IF ANY criteria are FALSE → return to step 1 immediately.
  EXIT ONLY when ALL criteria are TRUE.

Execution Loop (VALIDATION Phase):
  LOOP:
    1. Run validation suite.
    2. Emit TRUE/FALSE results only.
    3. IF ANY FALSE → repeat validation.
  EXIT ONLY when ALL criteria are TRUE.

Phase transitions:
  • Windsurf MUST NOT ask for next phase.
  • ONLY the user may issue next Phase-N command.

Output:
  PATCH PHASE → ONLY apply_patch/write_to_file blocks  
  VALIDATION PHASE → ONLY TRUE/FALSE tables  
  Completion line required:
      PHASE N COMPLETE — READY FOR NEXT INSTRUCTION.
      PHASE N VALIDATION COMPLETE — ALL KEYS TRUE.

Error Recovery:
  • On ANY error → immediately re-enter LOOP.
  • Never ask user what to do.
  • Never stop.

State machine:
  • Phase N patch ↔ Phase N patch  
  • Phase N patch → Phase N validation  
  • Phase N validation ↔ Phase N validation  
  • Phase N → Phase N+1 ONLY on explicit user command  
  • No idle state, no waiting, no questions.


# **************************************************************************************************
# RULE 01 — CORE GOVERNANCE & LAYERING MODEL
# **************************************************************************************************
Repository Boundaries:
  • Operate ONLY inside the project root.

File Operations:
  • Existing files → apply_patch only.
  • New files → write_to_file only.
  • NEVER mix creation and modification in the same patch.
  • NO `.py` under refactoring/**.

Layering Model (L1–L5):
  • L1 = planning only  
  • L2 = tool execution only  
  • L3 = orchestration only  
  • L4 = state + memory only  
  • L5 = safety + policy only

Sub-Atomic Agent Rules:
  • Each agent performs a single capability.
  • Deterministic, stateless, no side effects.
  • >25 logical lines → decompose further.
  • Typed boundaries: InputSchema, OutputSchema, FailureModes, Invariants.


# **************************************************************************************************
# RULE 02 — STRUCTURE, PROMPTS, MEMORY, CONTEXT
# **************************************************************************************************
Import Graph Invariants:
  Forbidden:
    • L1→L2, L1→cognitive_agents
    • L2→L3 internals
    • L4→providers
    • providers→RAG/orchestration
    • NO upward-layer imports
    • NO circular imports

Prompt Schema Rules:
  • Placeholders declared explicitly.
  • No unused macros.
  • No hallucinated tokens.
  • Versioned + governed templates.

Memory Rules:
  • All caches bounded.
  • Eviction required.
  • No unbounded embeddings.
  • No orphaned async tasks.

Context Engineering:
  • Only relevant context.
  • Deterministic RAG outputs.
  • No infinite scroll.


# **************************************************************************************************
# RULE 03 — DAG WORKFLOW TOPOLOGY
# **************************************************************************************************
L3 DAG Requirements:
  • Typed, acyclic, resumable.
  • OutputSchema → InputSchema validation at every transition.
  • Only L3 may orchestrate.

Module Topology:
  /l1 = planning  
  /l2 = tools  
  /l3 = orchestration  
  /l4 = state/memory  
  /l5 = safety  
  /prompts = templates  
  /tests mirrors module layout  
  /refactoring = docs only, no code

Public API surfaces:
  • l1.api, l2.api, l3.api, l4.api, l5.api


# **************************************************************************************************
# RULE 04 — TESTING AUTO-REPAIR LOOP
# **************************************************************************************************
Testing Requirements:
  • MUST pass: import health, pytest, ruff, mypy.

Zero-Failure Mandate:
  • No partial passes.
  • No skipping tests.
  • All MUST be green.

Auto-Retry Loop:
  • After ANY failure → rerun full suite.
  • Apply corrective patches until green.

Pycache Clearing:
  • Before every test run: delete ALL __pycache__/ and *.pyc.

Deterministic Completion Gate:
  • Accept only 0 failures, 0 errors, 0 unapproved warnings.


# **************************************************************************************************
# RULE 05 — TOOLING, MCP, OBSERVABILITY
# **************************************************************************************************
Tool Execution:
  • Only L2 executes tools.
  • Tools require schemas.
  • Must implement retry/backoff/circuit breaker.
  • No tool logic in L1, L3–L5.

MCP vs SDK:
  • Prefer MCP.
  • SDK allowed only when MCP not available.

Observability:
  • Trace IDs, spans, metrics required.
  • Log sanitization required.


# **************************************************************************************************
# RULE 06 — SAFETY, POLICY, COST
# **************************************************************************************************
L5 Safety:
  • Enforces PII detection, uncertainty thresholds, risk routing.

Policy Boundaries:
  • Only L5 may enforce safety gates.

Cost Controls:
  • Enforce compute budgets.
  • Lower-cost model preference.
  • Semantic caching bounded + validated.


# **************************************************************************************************
# RULE 07 — CONCURRENCY & PARALLELISM
# **************************************************************************************************
DAG Run Isolation:
  • No shared global mutable state.

Concurrency Limits:
  • Parallel DAGs bounded by CPU + config.

Resource Governance:
  • Vector-store writes serialized.
  • Redis pooled + timeout.

Safety Integration:
  • L5 may pause/block/reroute concurrent DAGs.


# **************************************************************************************************
# RULE 08 — PROMPT GOVERNANCE & RAG DETERMINISM
# **************************************************************************************************
Prompt Governance:
  • Stored in registry with version/owner/schema.

RAG Determinism:
  • Same query + same corpus = same result.

Drafting Rules:
  • Planner(L1) → Executor(L2) → Critic(L1) → Fix(L1) → DAG(L3)
  • High-signal rules: no fluff, metric injection, persona alignment.


# **************************************************************************************************
# RULE 09 — APPLY-PATCH ENFORCEMENT (MODE B)
# **************************************************************************************************
Mode B Behavior:
  • Phase PROMPT = natural-language specification ONLY.
  • Windsurf OUTPUT = apply_patch/write_to_file ONLY.
  • No narrative in output.
  • No interactive behavior.
  • No ambiguity.

Patch Rules:
  • ALL required diffs must be emitted in one batch.
  • No partial patches.
  • No placeholders.
  • No incomplete stubs.
  • Missing directories created automatically.

Ambiguity Rule:
  • If unclear → assume PATCH REQUIRED.


# **************************************************************************************************
# RULE 10 — ZERO-LOSS CONTINUITY (MODE B)
# **************************************************************************************************
Windsurf MUST preserve ALL:
  • prior rules
  • prior templates
  • prior architectural boundaries
  • prior public APIs
  • prior Phase constraints
  • directory/module topology

All new Phase prompts are ADDITIVE.
Conflicts → strictest rule applies.

NO RULE may be dropped without:
  RESET WINDSURF

# ==================================================================================================
# END UNIFIED RULES 00–10 (MODE B)
# ==================================================================================================
