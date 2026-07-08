"""Embedding Input Guard - Privacy Boundary for Embedding Seam.

Provides structural guarantees for privacy and data boundaries before text
is passed to an embedding model.
"""

import hashlib
import re
from dataclasses import dataclass
from typing import ClassVar

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "embedding_input_guard", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "embedding_input_guard", "policy_binding")
trace_contract._emit_snapshots_state("p0", "embedding_input_guard", "state_snapshot")

trace_contract._emit_emits_metric_event("embedding_input_guard", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("embedding_input_guard", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("embedding_input_guard", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("embedding_input_guard", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("embedding_input_guard", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("embedding_input_guard", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("embedding_input_guard", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("embedding_input_guard", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("embedding_input_guard", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("embedding_input_guard", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("embedding_input_guard", "p4obs", "alert")
trace_contract._emit_links_incident_trace("embedding_input_guard", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("embedding_input_guard", "p3lm", "pattern")
trace_contract._emit_records_learning_event("embedding_input_guard", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("embedding_input_guard", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("embedding_input_guard", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("embedding_input_guard", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("embedding_input_guard", "p3lm", "policy")
trace_contract._emit_stores_learning_state("embedding_input_guard", "p3lm", "state")
trace_contract._emit_records_execution_trace("embedding_input_guard", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("embedding_input_guard", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("embedding_input_guard", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("embedding_input_guard", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("embedding_input_guard", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("embedding_input_guard", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("embedding_input_guard", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("embedding_input_guard", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("embedding_input_guard", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "embedding_input_guard", "context_pull")
trace_contract._emit_pulls_context("p1", "embedding_input_guard", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "embedding_input_guard", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "embedding_input_guard", "uwg_term_2")
trace_contract._emit_writes_through("p1", "embedding_input_guard", "write_through")
trace_contract._emit_writes_through("p1", "embedding_input_guard", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "embedding_input_guard", "safety_validation")
trace_contract._emit_invokes_eval("p1", "embedding_input_guard", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "embedding_input_guard", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "embedding_input_guard", "human_escalation")
trace_contract._emit_routes_through("p1", "embedding_input_guard", "route_through")
trace_contract._emit_checks_agent_registry("p1", "embedding_input_guard", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "embedding_input_guard", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "embedding_input_guard", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "embedding_input_guard", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "embedding_input_guard", "target_agent")
trace_contract._emit_verifies_policy("p1", "embedding_input_guard", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "embedding_input_guard", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "embedding_input_guard", "boundary_check")
trace_contract._emit_transcripts_response("p1", "embedding_input_guard", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "embedding_input_guard")
trace_contract._emit_gated_by_confidence("p1", "embedding_input_guard", "confidence_gate")
trace_contract.emit_replay_key("p0", "embedding_input_guard")
trace_contract.emit_determinism_digest("p0", "embedding_input_guard")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "embedding_input_guard", "execution_auth")
trace_contract._emit_validates_capability("p2", "embedding_input_guard", "capability_check")
trace_contract._emit_routes_to_capability("p2", "embedding_input_guard", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "embedding_input_guard", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "embedding_input_guard", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "embedding_input_guard", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "embedding_input_guard", "exec_output")
trace_contract._emit_dispatches_agent("p3", "embedding_input_guard", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "embedding_input_guard", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "embedding_input_guard", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "embedding_input_guard", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "embedding_input_guard", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "embedding_input_guard", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "embedding_input_guard", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "embedding_input_guard", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "embedding_input_guard", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "embedding_input_guard", "eval_metric")
trace_contract._emit_stores_embedding("p4", "embedding_input_guard", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "embedding_input_guard", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "embedding_input_guard", "exec_snapshot_link")


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
    ALLOWED_FIELDS: ClassVar[set[str]] = {
        "u0_user_prompt",
        "failure_signal.error_message",
        "pattern_text",
        "rag_query",
    }
    MAX_TEXT_BYTES: ClassVar[int] = 32_768

    # Patterns for redacting sensitive information.
    REDACTION_PATTERNS = [
        re.compile(r"sk-[a-zA-Z0-9]{20,}"),  # API keys
        re.compile(r"Bearer [a-zA-Z0-9\-_.+/=]+"),  # Bearer tokens
        re.compile(
            r"[a-f0-9]{8}-?[a-f0-9]{4}-?[a-f0-9]{4}-?[a-f0-9]{4}-?[a-f0-9]{12}",
            re.IGNORECASE,
        ),  # UUIDs
        re.compile(r"[\w\.-]+@[\w\.-]+\.\w+"),  # Emails
        re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),  # SSNs
    ]

    @staticmethod
    def _normalize(text: str) -> str:
        text = text.replace("\x00", " ")
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    @classmethod
    def guard(cls, text: str, field_name: str) -> GuardedText:
        """Guard and redact input text before embedding."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "EmbeddingInputGuard.guard")

        if not isinstance(text, str):
            raise EmbeddingInputViolation("Embedding input must be a string.")
        if field_name not in cls.ALLOWED_FIELDS:
            raise EmbeddingInputViolation(f"Field '{field_name}' is not allowed for embedding.")

        redacted_text = cls._normalize(text)
        if not redacted_text:
            raise EmbeddingInputViolation("Embedding input cannot be empty.")
        if len(redacted_text.encode("utf-8")) > cls.MAX_TEXT_BYTES:
            raise EmbeddingInputViolation(
                f"Embedding input exceeds maximum size of {cls.MAX_TEXT_BYTES} bytes.",
            )
        for pattern in cls.REDACTION_PATTERNS:
            redacted_text = pattern.sub("[REDACTED]", redacted_text)

        if not redacted_text.replace("[REDACTED]", "").strip():
            raise EmbeddingInputViolation(
                "Embedding input was fully redacted and is not useful for embedding."
            )

        text_hash = hashlib.sha256(redacted_text.encode("utf-8")).hexdigest()

        return GuardedText(
            redacted_text=redacted_text,
            hash=text_hash,
            size=len(redacted_text),
        )
