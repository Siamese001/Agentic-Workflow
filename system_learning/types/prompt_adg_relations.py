"""ADG relation constants for the prompt provenance and learning system.

All 35 relation names used across the prompt lifecycle are defined here as
module-level string constants so that every engine imports the same
canonical string rather than typing it ad-hoc.

Relation families
-----------------
PROVENANCE_*     — how the prompt was constructed (section 3)
SAFETY_*         — L5 policy/guardrail/budget decisions (section 4)
EXECUTION_*      — runtime routing and model execution (section 5)
OUTCOME_*        — execution outcome events (section 6)
RETRIEVAL_*      — RAG context linkage (section 7)
DRIFT_*          — inter-version quality signals (section 8)
OPTIMIZATION_*   — meta-learning optimization lineage (section 13)
BUDGET_*         — token budget tracking (section 14)
HITL_*           — human-in-the-loop feedback (section 11)

Naming convention
-----------------
All constants follow snake_case and are prefixed by their family so
relation sets can be filtered cleanly.

Usage::

    from system_learning.types.prompt_adg_relations import (
        PROVENANCE_TEMPLATE_USED_BY,
        OUTCOME_PRODUCED_ANSWER,
        DRIFT_REGRESSION_DETECTED,
    )
"""

from __future__ import annotations

# ===========================================================================
# PROVENANCE family — how the prompt was assembled
# ===========================================================================

PROVENANCE_TEMPLATE_USED_BY: str = "template_used_by"
PROVENANCE_FEWSHOT_USED_BY: str = "fewshot_used_by"
PROVENANCE_INSTRUCTION_INJECTION_SOURCE: str = "instruction_injection_source"
PROVENANCE_C0_CONTEXT_SOURCE: str = "c0_context_source"
PROVENANCE_USES_S0_RULE: str = "prompt_uses_s0_rule"
PROVENANCE_USES_D0_FENCE: str = "prompt_uses_d0_fence"
PROVENANCE_USES_I0_INSTRUCTION: str = "prompt_uses_i0_instruction"
PROVENANCE_USES_C0_CONTEXT: str = "prompt_uses_c0_context"
PROVENANCE_CONTAINS_U0_INPUT: str = "prompt_contains_u0_input"

# ===========================================================================
# SAFETY family — L5 safety validation edges
# ===========================================================================

SAFETY_VALIDATED_BY_POLICY: str = "compiled_prompt_validated_by_policy"
SAFETY_CHECKED_BY_GUARDRAIL: str = "compiled_prompt_checked_by_guardrail"
SAFETY_BUDGET_CHECKED: str = "compiled_prompt_budget_checked"
SAFETY_ALLOWED: str = "compiled_prompt_allowed"
SAFETY_BLOCKED: str = "compiled_prompt_blocked"

# ===========================================================================
# EXECUTION family — runtime routing and model invocation
# ===========================================================================

EXECUTION_ROUTES_TO: str = "compiled_prompt_routes_to"
EXECUTION_EXECUTED_BY_MODEL: str = "compiled_prompt_executed_by_model"
EXECUTION_GENERATES_TRACE: str = "compiled_prompt_generates_trace"

# ===========================================================================
# OUTCOME family — execution outcome events
# ===========================================================================

OUTCOME_PRODUCED_ANSWER: str = "compiled_prompt_produced_answer"
OUTCOME_FAILED: str = "compiled_prompt_failed"
OUTCOME_TRIGGERED_HEALER: str = "compiled_prompt_triggered_healer"
OUTCOME_ESCALATED_HITL: str = "compiled_prompt_escalated_hitl"
OUTCOME_PASSED_REPLAY: str = "compiled_prompt_passed_replay"
OUTCOME_FAILED_REPLAY: str = "compiled_prompt_failed_replay"

# ===========================================================================
# RETRIEVAL family — RAG and grounding linkage
# ===========================================================================

RETRIEVAL_RETRIEVES_VIA: str = "compiled_prompt_retrieves_via"
RETRIEVAL_USES_CHUNK: str = "compiled_prompt_uses_chunk"
RETRIEVAL_USES_CITATION_SET: str = "compiled_prompt_uses_citation_set"
RETRIEVAL_SCORES_GROUNDEDNESS: str = "compiled_prompt_scores_groundedness"

# ===========================================================================
# DRIFT family — inter-version quality signals
# ===========================================================================

DRIFT_VERSION_REPLACED_BY: str = "prompt_version_replaced_by"
DRIFT_TEMPLATE_SUPERSEDED: str = "prompt_template_superseded"
DRIFT_REGRESSION_DETECTED: str = "prompt_prompt_regression_detected"
DRIFT_IMPROVEMENT_DETECTED: str = "prompt_prompt_improvement_detected"

# ===========================================================================
# OPTIMIZATION family — meta-learning optimization lineage
# ===========================================================================

OPTIMIZATION_PROPOSAL_COMMITS: str = "prompt_proposal_commits_optimization"

# ===========================================================================
# BUDGET family — token budget tracking
# ===========================================================================

BUDGET_TOKEN_PROFILE: str = "compiled_prompt_token_profile"
BUDGET_TRUNCATED: str = "compiled_prompt_truncated"
BUDGET_EXCEEDED: str = "compiled_prompt_exceeded_budget"

# ===========================================================================
# HITL family — human-in-the-loop feedback
# ===========================================================================

HITL_CAUSED_ESCALATION: str = "compiled_prompt_caused_escalation"
HITL_PATCH_APPLIED: str = "hitl_patch_applied"
HITL_PREFERENCE_RECORD_CREATED: str = "preference_record_created"
HITL_USED_FOR_DPO: str = "preference_used_for_dpo"

# ===========================================================================
# Full relation sets — for validation and filtering
# ===========================================================================

PROVENANCE_RELATIONS: frozenset[str] = frozenset(
    {
        PROVENANCE_TEMPLATE_USED_BY,
        PROVENANCE_FEWSHOT_USED_BY,
        PROVENANCE_INSTRUCTION_INJECTION_SOURCE,
        PROVENANCE_C0_CONTEXT_SOURCE,
        PROVENANCE_USES_S0_RULE,
        PROVENANCE_USES_D0_FENCE,
        PROVENANCE_USES_I0_INSTRUCTION,
        PROVENANCE_USES_C0_CONTEXT,
        PROVENANCE_CONTAINS_U0_INPUT,
    },
)

SAFETY_RELATIONS: frozenset[str] = frozenset(
    {
        SAFETY_VALIDATED_BY_POLICY,
        SAFETY_CHECKED_BY_GUARDRAIL,
        SAFETY_BUDGET_CHECKED,
        SAFETY_ALLOWED,
        SAFETY_BLOCKED,
    },
)

EXECUTION_RELATIONS: frozenset[str] = frozenset(
    {
        EXECUTION_ROUTES_TO,
        EXECUTION_EXECUTED_BY_MODEL,
        EXECUTION_GENERATES_TRACE,
    },
)

OUTCOME_RELATIONS: frozenset[str] = frozenset(
    {
        OUTCOME_PRODUCED_ANSWER,
        OUTCOME_FAILED,
        OUTCOME_TRIGGERED_HEALER,
        OUTCOME_ESCALATED_HITL,
        OUTCOME_PASSED_REPLAY,
        OUTCOME_FAILED_REPLAY,
    },
)

RETRIEVAL_RELATIONS: frozenset[str] = frozenset(
    {
        RETRIEVAL_RETRIEVES_VIA,
        RETRIEVAL_USES_CHUNK,
        RETRIEVAL_USES_CITATION_SET,
        RETRIEVAL_SCORES_GROUNDEDNESS,
    },
)

DRIFT_RELATIONS: frozenset[str] = frozenset(
    {
        DRIFT_VERSION_REPLACED_BY,
        DRIFT_TEMPLATE_SUPERSEDED,
        DRIFT_REGRESSION_DETECTED,
        DRIFT_IMPROVEMENT_DETECTED,
    },
)

OPTIMIZATION_RELATIONS: frozenset[str] = frozenset(
    {OPTIMIZATION_PROPOSAL_COMMITS},
)

BUDGET_RELATIONS: frozenset[str] = frozenset(
    {
        BUDGET_TOKEN_PROFILE,
        BUDGET_TRUNCATED,
        BUDGET_EXCEEDED,
    },
)

HITL_RELATIONS: frozenset[str] = frozenset(
    {
        HITL_CAUSED_ESCALATION,
        HITL_PATCH_APPLIED,
        HITL_PREFERENCE_RECORD_CREATED,
        HITL_USED_FOR_DPO,
    },
)

ALL_PROMPT_RELATIONS: frozenset[str] = (
    PROVENANCE_RELATIONS
    | SAFETY_RELATIONS
    | EXECUTION_RELATIONS
    | OUTCOME_RELATIONS
    | RETRIEVAL_RELATIONS
    | DRIFT_RELATIONS
    | OPTIMIZATION_RELATIONS
    | BUDGET_RELATIONS
    | HITL_RELATIONS
)

__all__ = [
    "ALL_PROMPT_RELATIONS",
    "BUDGET_EXCEEDED",
    "BUDGET_RELATIONS",
    "BUDGET_TOKEN_PROFILE",
    "BUDGET_TRUNCATED",
    "DRIFT_IMPROVEMENT_DETECTED",
    "DRIFT_REGRESSION_DETECTED",
    "DRIFT_RELATIONS",
    "DRIFT_TEMPLATE_SUPERSEDED",
    "DRIFT_VERSION_REPLACED_BY",
    "EXECUTION_EXECUTED_BY_MODEL",
    "EXECUTION_GENERATES_TRACE",
    "EXECUTION_RELATIONS",
    "EXECUTION_ROUTES_TO",
    "HITL_CAUSED_ESCALATION",
    "HITL_PATCH_APPLIED",
    "HITL_PREFERENCE_RECORD_CREATED",
    "HITL_RELATIONS",
    "HITL_USED_FOR_DPO",
    "OPTIMIZATION_PROPOSAL_COMMITS",
    "OPTIMIZATION_RELATIONS",
    "OUTCOME_ESCALATED_HITL",
    "OUTCOME_FAILED",
    "OUTCOME_FAILED_REPLAY",
    "OUTCOME_PASSED_REPLAY",
    "OUTCOME_PRODUCED_ANSWER",
    "OUTCOME_RELATIONS",
    "OUTCOME_TRIGGERED_HEALER",
    "PROVENANCE_C0_CONTEXT_SOURCE",
    "PROVENANCE_CONTAINS_U0_INPUT",
    "PROVENANCE_FEWSHOT_USED_BY",
    "PROVENANCE_INSTRUCTION_INJECTION_SOURCE",
    "PROVENANCE_RELATIONS",
    "PROVENANCE_TEMPLATE_USED_BY",
    "PROVENANCE_USES_C0_CONTEXT",
    "PROVENANCE_USES_D0_FENCE",
    "PROVENANCE_USES_I0_INSTRUCTION",
    "PROVENANCE_USES_S0_RULE",
    "RETRIEVAL_RELATIONS",
    "RETRIEVAL_RETRIEVES_VIA",
    "RETRIEVAL_SCORES_GROUNDEDNESS",
    "RETRIEVAL_USES_CHUNK",
    "RETRIEVAL_USES_CITATION_SET",
    "SAFETY_ALLOWED",
    "SAFETY_BLOCKED",
    "SAFETY_BUDGET_CHECKED",
    "SAFETY_CHECKED_BY_GUARDRAIL",
    "SAFETY_RELATIONS",
    "SAFETY_VALIDATED_BY_POLICY",
]
