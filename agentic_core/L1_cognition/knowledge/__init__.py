"""L1 Reasoning Knowledge Base module.

Provides persistent reasoning knowledge base that stores successful reasoning patterns
and reusable solution fragments.
"""

# P4/L1 Reasoning Knowledge Base exports
from agentic_core.L1_cognition.knowledge.knowledge_orchestrator import (
    EvaluationResult,
    ReasoningContext,
    ReasoningTrace,
    capture_reasoning_pattern,
    get_pattern_recommendations,
    get_reasoning_knowledge_registry,
    pattern_stored,
    pattern_validated,
    pattern_versioned,
    query_reasoning_patterns,
    reasoning_pattern_captured,
    reasoning_pattern_reused,
    reset_reasoning_knowledge_registry,
    reuse_outcome_recorded,
    reuse_reasoning_pattern,
    validate_reasoning_pattern,
)
from agentic_core.L1_cognition.knowledge.reasoning_knowledge import (
    ReasoningKnowledgeError,
    ReasoningKnowledgeRecord,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "__init__")
emit_determinism_digest("p0", "__init__")

_emit_dispatches_healing_run("p1", "__init__", "L1")
_emit_routes_through("p1", "__init__", "L1")
_emit_escalates_to_human("p1", "__init__", "L1")
_emit_reads_policy_state("p1", "__init__", "L1")

_emit_snapshots_state("p0", "__init__", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "__init__", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "__init__")

__all__ = [
    # Reasoning Knowledge Records
    "ReasoningKnowledgeRecord",
    # Exception Classes
    "ReasoningKnowledgeError",
    # Context Classes
    "ReasoningTrace",
    "EvaluationResult",
    "ReasoningContext",
    # Knowledge Functions
    "capture_reasoning_pattern",
    "query_reasoning_patterns",
    "get_reasoning_knowledge_registry",
    "reset_reasoning_knowledge_registry",
    # Query Functions
    "reuse_reasoning_pattern",
    "get_pattern_recommendations",
    "validate_reasoning_pattern",
    # ADG Edge Emitters
    "reasoning_pattern_captured",
    "pattern_validated",
    "pattern_versioned",
    "pattern_stored",
    "reuse_outcome_recorded",
    "reasoning_pattern_reused",
]
