# =====================================================================
# WINDSURF PHASE EXECUTION TEMPLATE (CANONICAL)
# =====================================================================
# PURPOSE:
#   Provide Windsurf with a deterministic, completion-oriented,
#   zero-loss prompt template for all Phases 5+. This ensures:
#       • no scope creep
#       • no architectural drift
#       • no hallucinated imports/modules
#       • strict L1–L5 agentic boundaries
#       • tests-first development
#       • repeatable 95–100% completion behavior
#
#   Every new Phase prompt (5–10) MUST follow this template exactly.
#
# =====================================================================
# PRECONDITIONS (MANDATORY FOR ANY PHASE)
# =====================================================================
# Windsurf MUST first verify these conditions BEFORE implementing code:
#
#   1. run the import smoke test:
#         python -c "import l1, l2, l3, l4, l5"
#      → if any import fails: Windsurf must FIX imports BEFORE doing work.
#
#   2. run pytest --collect-only
#      → if it fails due to:
#          • duplicate test roots
#          • broken imports
#          • missing modules
#      → Windsurf MUST fix test infrastructure BEFORE doing work.
#
#   3. mypy MUST start cleanly without parse/import errors
#      → type errors allowed (Phase-dependent), but syntax/import errors
#        mean Windsurf must fix infrastructure BEFORE doing work.
#
#   4. Windsurf MUST NEVER modify working Phase 4 logic unless:
#         • failing test
#         • runtime failure
#         • type safety violation
#         • L1–L5 boundary violation
#
# =====================================================================
# SCOPE SECTION (REQUIRED)
# =====================================================================
# Windsurf MUST be explicitly told:
#
#   • What IS allowed (IN SCOPE)
#   • What is NOT allowed (OUT OF SCOPE)
#
# TEMPLATE:
#   IN SCOPE:
#     • (List concrete files/functions to create/edit)
#     • (Explicit new tests)
#     • (Targeted fixes only)
#
#   OUT OF SCOPE:
#     • No architectural redesign
#     • No rewriting stable code
#     • No new layers (unless explicitly requested)
#     • No concurrency, routing changes, etc. (unless phase requires)
#     • No modifying resume workflow
#
# =====================================================================
# IMPORT CONTRACTS (REQUIRED)
# =====================================================================
# Windsurf MUST use ONLY these import paths for consistency:
#
#   L1:
#     from l1.outreach_archetype_planning import RecipientProfile, ArchetypeContext
#     from l1.research_planning import ResearchPlanner
#     from l1.message_planning import MessagePlanner
#
#   L2:
#     from l2.contact_research_executor import ContactResearchExecutor
#     from l2.company_research_executor import CompanyResearchExecutor
#     from l2.message_generation_executor import MessageGenerationExecutor
#
#   L3:
#     from l3.outreach_orchestrator import OutreachOrchestrator
#     from l3.unified_workflow_orchestrator import UnifiedWorkflowOrchestrator
#
#   L4:
#     from l4.state_manager import StateManager
#     from l4.rag.rag_engine import RAGEngine (or stub)
#
#   L5:
#     from l5.safety_validator import SafetyValidator
#
# Windsurf MUST NOT invent new modules or import paths.
#
# =====================================================================
# CALLSTACK CONTRACT (CRITICAL)
# =====================================================================
# Windsurf must explicitly follow this pattern:
#
#   VALID OUTREACH CALLSTACK:
#     L3 orchestrator
#         → L1 archetype planner
#         → L1 research planner
#         → L2 company executor
#         → L2 contact executor
#         → L1 message planner
#         → L2 message generator
#         → L5 safety validator (FINAL)
#         → L4 state persistence
#
#   SAFETY CALLSTACK (Phase 5+):
#         L2 message generator → L5 SafetyValidator.evaluate → return result
#
#   RAG/TEMPORAL CALLSTACK (Phase 6+):
#         RAGEngine.retrieve → (hybrid, KG, temporal) → fused list
#
# Windsurf MUST NOT deviate.
#
# =====================================================================
# TEST-FIRST REQUIREMENT (MANDATORY)
# =====================================================================
# Windsurf MUST ALWAYS:
#
#   1. Generate or update the test suite FIRST
#   2. THEN implement code that satisfies those tests
#
# Rationale:
#   • Windsurf performs 5× better when constrained by explicit test files.
#
# =====================================================================
# DATACLASS CONTRACT (MANDATORY)
# =====================================================================
# Windsurf MUST NOT mix dicts and dataclasses.
#
# RULE:
#   • If a dataclass exists → use it.
#   • If a dataclass does not exist → create minimal one.
#
# REQUIRED DATACLASS OUTPUT TYPES:
#   • ArchetypeContext
#   • ResearchPlan
#   • ResearchBundle
#   • MessagePlan
#   • MessageResult
#   • LICPipelineResult
#   • SafetyResult
#
# =====================================================================
# SUCCESS CONDITIONS (PHASE COMPLETION CRITERIA)
# =====================================================================
# Windsurf MUST verify these at the end of ANY Phase prompt:
#
#   ✔ All new tests pass with pytest -q
#   ✔ run_single_outreach(...) still returns success=True
#   ✔ No resume regressions
#   ✔ No new mypy blocking errors (type errors OK)
#   ✔ Import graph cycle-free
#   ✔ L1–L5 boundary integrity preserved
#   ✔ No rewriting of stable Phase-4 logic
#
# =====================================================================
# END OF WINDSURF PHASE PROMPT TEMPLATE
# =====================================================================
