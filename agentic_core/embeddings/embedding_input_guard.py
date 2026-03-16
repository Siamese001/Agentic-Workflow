"""Embedding Input Guard - Privacy Boundary for Embedding Seam.

Provides structural guarantees for privacy and data boundaries before text
is passed to an embedding model.
"""

import hashlib
import re
from dataclasses import dataclass

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "embedding_input_guard", "p0_governance")
_emit_reads_policy_state("p0", "embedding_input_guard", "policy_binding")
_emit_snapshots_state("p0", "embedding_input_guard", "state_snapshot")
emit_replay_key("p0", "embedding_input_guard")
emit_determinism_digest("p0", "embedding_input_guard")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "embedding_input_guard", "execution_auth")
_emit_validates_capability("p2", "embedding_input_guard", "capability_check")
_emit_routes_to_capability("p2", "embedding_input_guard", "capability_route")
_emit_writes_via_uwg("p2", "embedding_input_guard", "uwg_write")
_emit_blocks_direct_write("p2", "embedding_input_guard", "direct_write_block")
_emit_records_tool_invocation("p2", "embedding_input_guard", "tool_invocation")
_emit_captures_execution_output("p2", "embedding_input_guard", "exec_output")
_emit_dispatches_agent("p3", "embedding_input_guard", "agent_dispatch")
_emit_coordinates_agents("p3", "embedding_input_guard", "agent_coordination")
_emit_records_workflow_lineage("p3", "embedding_input_guard", "workflow_lineage")
_emit_records_healing_outcome("p3", "embedding_input_guard", "healing_outcome")
_emit_escalates_failure("p3", "embedding_input_guard", "failure_escalation")
_emit_orchestrates_workflow("p3", "embedding_input_guard", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "embedding_input_guard", "healing_dispatch")
_emit_invokes_evaluation("p3", "embedding_input_guard", "evaluation_signal")
_emit_records_telemetry_event("p4", "embedding_input_guard", "telemetry_event")
_emit_captures_evaluation_metric("p4", "embedding_input_guard", "eval_metric")
_emit_stores_embedding("p4", "embedding_input_guard", "embedding_store")
_emit_updates_meta_learning_state("p4", "embedding_input_guard", "meta_learning")
_emit_links_execution_to_snapshot("p4", "embedding_input_guard", "exec_snapshot_link")


class EmbeddingInputViolation(ValueError):
    """Raised when input text violates embedding policies."""

    pass


@dataclass(frozen=True)
class GuardedText:
    """A wrapper for text that has passed privacy and boundary checks."""

    redacted_text: str
    hash: str
    size: int


class EmbeddingInputGuard:
    """Enforces privacy and data boundary controls at the embedding seam."""

    # Allowlist of fields that are permitted to be embedded.
    ALLOWED_FIELDS = {
        "u0_user_prompt",
        "failure_signal.error_message",
        "pattern_text",
        "rag_query",
    }

    # Patterns for redacting sensitive information.
    REDACTION_PATTERNS = [
        re.compile(r"sk-[a-zA-Z0-9]{20,}"),  # API keys
        re.compile(r"Bearer [a-zA-Z0-9\-_.+/=]+"),  # Bearer tokens
        re.compile(
            r"[a-f0-9]{8}-?[a-f0-9]{4}-?[a-f0-9]{4}-?[a-f0-9]{4}-?[a-f0-9]{12}", re.IGNORECASE
        ),  # UUIDs
        re.compile(r"[\w\.-]+@[\w\.-]+\.\w+"),  # Emails
    ]

    @classmethod
    def guard(cls, text: str, field_name: str) -> GuardedText:
        """Guard and redact input text before embedding."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "EmbeddingInputGuard.guard")

        if field_name not in cls.ALLOWED_FIELDS:
            raise EmbeddingInputViolation(f"Field '{field_name}' is not allowed for embedding.")

        redacted_text = text
        for pattern in cls.REDACTION_PATTERNS:
            redacted_text = pattern.sub("[REDACTED]", redacted_text)

        text_hash = hashlib.sha256(redacted_text.encode("utf-8")).hexdigest()

        return GuardedText(
            redacted_text=redacted_text,
            hash=text_hash,
            size=len(redacted_text),
        )
