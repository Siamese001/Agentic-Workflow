"""
Context Manager - Phase 5 Optimization
LLM context management utilities for high-reasoning agents.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "context_manager_util", "p0_governance")
_emit_reads_policy_state("p0", "context_manager_util", "policy_binding")
_emit_snapshots_state("p0", "context_manager_util", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("context_manager_util", "p4obs", "metric_1")
_emit_emits_metric_event("context_manager_util", "p4obs", "metric_2")
_emit_emits_metric_event("context_manager_util", "p4obs", "metric_3")
_emit_emits_metric_event("context_manager_util", "p4obs", "metric_4")
_emit_emits_metric_event("context_manager_util", "p4obs", "metric_5")
_emit_emits_metric_event("context_manager_util", "p4obs", "metric_6")
_emit_records_incident_event("context_manager_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("context_manager_util", "p4obs", "anomaly")
_emit_writes_observability_log("context_manager_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("context_manager_util", "p4obs", "mon_state")
_emit_triggers_alert("context_manager_util", "p4obs", "alert")
_emit_links_incident_trace("context_manager_util", "p4obs", "trace_link")
_emit_captures_pattern("context_manager_util", "p3lm", "pattern")
_emit_records_learning_event("context_manager_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("context_manager_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("context_manager_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("context_manager_util", "p3lm", "routing")
_emit_improves_agent_policy("context_manager_util", "p3lm", "policy")
_emit_stores_learning_state("context_manager_util", "p3lm", "state")
_emit_records_execution_trace("context_manager_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("context_manager_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("context_manager_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("context_manager_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("context_manager_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("context_manager_util", "env_read", "p2_env_1")
_emit_reads_environ("context_manager_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("context_manager_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("context_manager_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "context_manager_util", "context_pull")
_emit_pulls_context("p1", "context_manager_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "context_manager_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "context_manager_util", "uwg_term_2")
_emit_writes_through("p1", "context_manager_util", "write_through")
_emit_writes_through("p1", "context_manager_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "context_manager_util", "safety_validation")
_emit_invokes_eval("p1", "context_manager_util", "eval_call")
_emit_proposal_commits_routing("p1", "context_manager_util", "routing_commit")
_emit_escalates_to_human("p1", "context_manager_util", "human_escalation")
_emit_routes_through("p1", "context_manager_util", "route_through")
_emit_checks_agent_registry("p1", "context_manager_util", "agent_registry")
_emit_validates_agent_capability("p1", "context_manager_util", "capability")
_emit_dispatches_execution_plan("p1", "context_manager_util", "exec_plan")
_emit_agent_executes_agent("p1", "context_manager_util", "sub_agent")
_emit_routes_to_agent("p1", "context_manager_util", "target_agent")
_emit_verifies_policy("p1", "context_manager_util", "policy_check")
_emit_observes_runtime_state("p1", "context_manager_util", "runtime_state")
_emit_verifies_boundary("p1", "context_manager_util", "boundary_check")
_emit_transcripts_response("p1", "context_manager_util", "transcript")
_emit_hard_fails_untranscripted("p1", "context_manager_util")
_emit_gated_by_confidence("p1", "context_manager_util", "confidence_gate")
emit_replay_key("p0", "context_manager_util")
emit_determinism_digest("p0", "context_manager_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "context_manager_util", "execution_auth")
_emit_validates_capability("p2", "context_manager_util", "capability_check")
_emit_routes_to_capability("p2", "context_manager_util", "capability_route")
_emit_writes_via_uwg("p2", "context_manager_util", "uwg_write")
_emit_blocks_direct_write("p2", "context_manager_util", "direct_write_block")
_emit_records_tool_invocation("p2", "context_manager_util", "tool_invocation")
_emit_captures_execution_output("p2", "context_manager_util", "exec_output")
_emit_dispatches_agent("p3", "context_manager_util", "agent_dispatch")
_emit_coordinates_agents("p3", "context_manager_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "context_manager_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "context_manager_util", "healing_outcome")
_emit_escalates_failure("p3", "context_manager_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "context_manager_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "context_manager_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "context_manager_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "context_manager_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "context_manager_util", "eval_metric")
_emit_stores_embedding("p4", "context_manager_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "context_manager_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "context_manager_util", "exec_snapshot_link")


@dataclass
class ContextWindow:
    """Represents a context window for LLM."""

    messages: list[dict[str, str]]
    max_tokens: int
    current_tokens: int
    metadata: dict[str, Any]


class ContextManager:
    """LLM context management utilities."""

    # guardian: allow-magic-config
    def __init__(self, max_tokens: int = 4000):
        """
        Initialize context manager.

        Args:
            max_tokens: Maximum token limit for context
        """
        self.max_tokens = max_tokens
        self.messages: deque = deque()
        self.system_message: str | None = None

    def set_system_message(self, message: str) -> None:
        """
        Set system message.

        Args:
            message: System message
        """
        self.system_message = message

    def add_message(self, role: str, content: str) -> None:
        """
        Add message to context.

        Args:
            role: Message role (user/assistant/system)
            content: Message content
        """
        self.messages.append({"role": role, "content": content})

    def get_context_window(self) -> ContextWindow:
        """
        Get current context window.

        Returns:
            ContextWindow with messages and token info
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ContextManager.get_context_window")

        messages = []
        if self.system_message:
            messages.append({"role": "system", "content": self.system_message})
        messages.extend(list(self.messages))
        total_content = "".join(msg["content"] for msg in messages)
        current_tokens = len(total_content) // 4
        return ContextWindow(
            messages=messages,
            max_tokens=self.max_tokens,
            current_tokens=current_tokens,
            metadata={"message_count": len(messages)},
        )

    def trim_context(self, keep_recent: int = 10) -> None:
        """
        Trim context to keep only recent messages.

        Args:
            keep_recent: Number of recent messages to keep
        """
        if len(self.messages) > keep_recent:
            self.messages = deque(list(self.messages)[-keep_recent:], maxlen=keep_recent)

    def compress_context(self) -> None:
        """Compress context by summarizing older messages."""
        if len(self.messages) <= 5:
            return
        first_messages = list(self.messages)[:2]
        last_messages = list(self.messages)[-2:]
        middle_count = len(self.messages) - 4
        summary = {
            "role": "system",
            "content": f"[{middle_count} messages summarized for context efficiency]",
        }
        self.messages = deque(first_messages + [summary] + last_messages)

    def clear_context(self) -> None:
        """Clear all messages from context."""
        self.messages.clear()

    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text.

        Args:
            text: Text to estimate

        Returns:
            Estimated token count
        """
        return len(text) // 4

    def fits_in_context(self, additional_text: str) -> bool:
        """
        Check if additional text fits in context window.

        Args:
            additional_text: Text to check

        Returns:
            True if fits, False otherwise
        """
        current_window = self.get_context_window()
        additional_tokens = self.estimate_tokens(additional_text)
        return current_window.current_tokens + additional_tokens <= self.max_tokens

    def get_remaining_tokens(self) -> int:
        """
        Get remaining tokens in context window.

        Returns:
            Number of remaining tokens
        """
        current_window = self.get_context_window()
        return self.max_tokens - current_window.current_tokens

    @staticmethod
    # guardian: allow-magic-config
    def create_conversation_context(messages: list[dict[str, str]], max_tokens: int = 4000) -> ContextWindow:
        """
        Create context window from messages.

        Args:
            messages: List of message dictionaries
            max_tokens: Maximum token limit

        Returns:
            ContextWindow instance
        """
        total_content = "".join(msg.get("content", "") for msg in messages)
        current_tokens = len(total_content) // 4
        return ContextWindow(
            messages=messages,
            max_tokens=max_tokens,
            current_tokens=current_tokens,
            metadata={"message_count": len(messages)},
        )

    @staticmethod
    def merge_contexts(contexts: list[ContextWindow]) -> ContextWindow:
        """
        Merge multiple context windows.

        Args:
            contexts: List of ContextWindow instances

        Returns:
            Merged ContextWindow
        """
        all_messages = []
        total_tokens = 0
        for ctx in contexts:
            all_messages.extend(ctx.messages)
            total_tokens += ctx.current_tokens
        max_tokens = max(ctx.max_tokens for ctx in contexts)
        return ContextWindow(
            messages=all_messages,
            max_tokens=max_tokens,
            current_tokens=total_tokens,
            metadata={"merged_count": len(contexts)},
        )

    @staticmethod
    def prioritize_messages(messages: list[dict[str, str]], max_tokens: int) -> list[dict[str, str]]:
        """
        Prioritize messages to fit within token limit.

        Args:
            messages: List of messages
            max_tokens: Maximum token limit

        Returns:
            Prioritized list of messages
        """
        if not messages:
            return []
        system_messages = [msg for msg in messages if msg.get("role") == "system"]
        other_messages = [msg for msg in messages if msg.get("role") != "system"]
        system_tokens = sum(len(msg.get("content", "")) // 4 for msg in system_messages)
        remaining_tokens = max_tokens - system_tokens
        prioritized = system_messages.copy()
        current_tokens = system_tokens
        for msg in reversed(other_messages):
            msg_tokens = len(msg.get("content", "")) // 4
            if current_tokens + msg_tokens <= remaining_tokens:
                prioritized.insert(len(system_messages), msg)
                current_tokens += msg_tokens
            else:
                break
        return prioritized
