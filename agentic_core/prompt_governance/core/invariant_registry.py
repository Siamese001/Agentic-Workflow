"""Invariant registry for prompt governance enforcement constants.

No import-time validation side effects.
Call validate_invariant_registry() explicitly to verify schema integrity.
"""

from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "invariant_registry")
_emit_applies_guardrail("p0", "invariant_registry", "p0_governance")
_emit_reads_policy_state("p0", "invariant_registry", "policy_binding")
_emit_snapshots_state("p0", "invariant_registry", "state_snapshot")
emit_replay_key("p0", "invariant_registry")
emit_determinism_digest("p0", "invariant_registry")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

READ_ONLY_ISOLATION: dict = {
    "forbidden_verbs": ["write", "modify", "update", "delete"],
    "scope": "retrieval_context",
    "authority": "L1_prompt_governance",
}
MUTATION_BLOCK_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "forbidden_verbs": {"type": "array", "items": {"type": "string"}},
        "scope": {"type": "string"},
        "authority": {"type": "string"},
    },
    "required": ["forbidden_verbs", "scope", "authority"],
    "additionalProperties": False,
}
ITERATIVE_FEEDBACK_DIRECTIVE: str = "PRIVATE REASONING ONLY: You may refine your internal query up to 3 times before producing output. No mutation of external state. No authority granted. Re-query is advisory and read-only."


def validate_invariant_registry() -> None:
    """Validate READ_ONLY_ISOLATION against MUTATION_BLOCK_SCHEMA.

    Raises:
        RuntimeError: If READ_ONLY_ISOLATION fails schema validation.
    """
    from agentic_core.prompt_governance.security.validators.output_schema_validator import (
        validate_against_schema,
    )

    ok, code, _ = validate_against_schema(READ_ONLY_ISOLATION, MUTATION_BLOCK_SCHEMA)
    if not ok:
        raise RuntimeError(f"invariant_registry: READ_ONLY_ISOLATION fails MUTATION_BLOCK_SCHEMA: {code}")
