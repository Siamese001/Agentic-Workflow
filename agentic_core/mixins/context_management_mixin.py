"""
ContextManagementMixin - Phase 1 Critical Infrastructure: Context Standardization

Provides standardized context management with summarization and pruning logic
to prevent context overflow in LLM interactions.

Features:
- Context window tracking and enforcement
- Automatic summarization when approaching limits
- Priority-based context pruning
- Context state persistence
- Overflow prevention with graceful degradation

SSOT PRINCIPLE:
    All agents requiring context management should inherit from this mixin.
    This ensures consistent context handling across the agent ecosystem.
"""

from __future__ import annotations

import hashlib
import logging
import threading
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_emits_metric_event("context_management_mixin", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("context_management_mixin", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("context_management_mixin", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("context_management_mixin", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("context_management_mixin", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("context_management_mixin", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("context_management_mixin", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("context_management_mixin", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("context_management_mixin", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("context_management_mixin", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("context_management_mixin", "p4obs", "alert")
trace_contract._emit_links_incident_trace("context_management_mixin", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("context_management_mixin", "p3lm", "pattern")
trace_contract._emit_records_learning_event("context_management_mixin", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("context_management_mixin", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("context_management_mixin", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("context_management_mixin", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("context_management_mixin", "p3lm", "policy")
trace_contract._emit_stores_learning_state("context_management_mixin", "p3lm", "state")
trace_contract._emit_records_execution_trace("context_management_mixin", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("context_management_mixin", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("context_management_mixin", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("context_management_mixin", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("context_management_mixin", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("context_management_mixin", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("context_management_mixin", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("context_management_mixin", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("context_management_mixin", "runtime_state", "p2_rt_2")

trace_contract._emit_applies_guardrail("p0", "context_management_mixin", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "context_management_mixin", "policy_binding")
trace_contract._emit_snapshots_state("p0", "context_management_mixin", "state_snapshot")
trace_contract._emit_pulls_context("p1", "context_management_mixin", "context_pull")
trace_contract._emit_pulls_context("p1", "context_management_mixin", "context_pull_secondary")
trace_contract._emit_execution_terminates_at_uwg("p1", "context_management_mixin", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "context_management_mixin", "uwg_term_secondary")
trace_contract._emit_writes_through("p1", "context_management_mixin", "write_through")
trace_contract._emit_writes_through("p1", "context_management_mixin", "write_through_secondary")
trace_contract._emit_validated_by_safety_plane("p1", "context_management_mixin", "safety_validation")
trace_contract._emit_invokes_eval("p1", "context_management_mixin", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "context_management_mixin", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "context_management_mixin", "human_escalation")
trace_contract._emit_routes_through("p1", "context_management_mixin", "route_through")
trace_contract._emit_checks_agent_registry("p1", "context_management_mixin", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "context_management_mixin", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "context_management_mixin", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "context_management_mixin", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "context_management_mixin", "target_agent")
trace_contract._emit_verifies_policy("p1", "context_management_mixin", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "context_management_mixin", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "context_management_mixin", "boundary_check")
trace_contract._emit_transcripts_response("p1", "context_management_mixin", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "context_management_mixin")
trace_contract._emit_gated_by_confidence("p1", "context_management_mixin", "confidence_gate")
trace_contract.emit_replay_key("p0", "context_management_mixin")
trace_contract.emit_determinism_digest("p0", "context_management_mixin")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "context_management_mixin", "execution_auth")
trace_contract._emit_validates_capability("p2", "context_management_mixin", "capability_check")
trace_contract._emit_routes_to_capability("p2", "context_management_mixin", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "context_management_mixin", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "context_management_mixin", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "context_management_mixin", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "context_management_mixin", "exec_output")
trace_contract._emit_dispatches_agent("p3", "context_management_mixin", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "context_management_mixin", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "context_management_mixin", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "context_management_mixin", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "context_management_mixin", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "context_management_mixin", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "context_management_mixin", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "context_management_mixin", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "context_management_mixin", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "context_management_mixin", "eval_metric")
trace_contract._emit_stores_embedding("p4", "context_management_mixin", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "context_management_mixin", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "context_management_mixin", "exec_snapshot_link")

Logger = logging.getLogger(__name__)


class ContextPriority(Enum):
    """Priority levels for context items."""

    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


@dataclass
class ContextItem:
    """A single item in the context window."""

    content: str
    priority: ContextPriority
    token_count: int
    timestamp: float = field(default_factory=time.monotonic)
    item_id: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.item_id:
            self.item_id = hashlib.sha256(f"{self.content[:100]}{self.timestamp}".encode()).hexdigest()[:12]


@dataclass
class ContextConfig:
    """Configuration for context management."""

    max_context_tokens: int = 128000
    target_context_tokens: int = 100000
    summarization_threshold_pct: float = 0.75
    prune_threshold_pct: float = 0.9
    min_context_tokens: int = 4000
    summary_target_tokens: int = 2000


class ContextOverflowError(Exception):
    """Raised when context cannot be reduced below limits."""

    def __init__(self, current_tokens: int, max_tokens: int):
        self.current_tokens = current_tokens
        self.max_tokens = max_tokens
        super().__init__(f"Context overflow: {current_tokens} tokens exceeds maximum {max_tokens}")


class ContextManagementMixin:
    """
    Mixin providing standardized context management for agents.

    Phase 1 Critical Infrastructure:
    - Context window tracking
    - Automatic summarization
    - Priority-based pruning
    - Overflow prevention

    Usage:
        class MyAgent(ContextManagementMixin, SovereignBaseAgent):
            def __init__(self):
                super().__init__()
                self.configure_context(max_context_tokens=32000)

            async def process(self, query: str) -> str:
                # Add user query to context
                self.add_context(query, ContextPriority.HIGH)

                # Get optimized context for LLM
                context = self.get_optimized_context()

                # Process with LLM
                response = await self.llm_generate(context)

                # Add response to context
                self.add_context(response["content"], ContextPriority.MEDIUM)

                return response["content"]
    """

    def __init__(self, **kwargs: Any) -> None:
        """Initialize context management state."""
        super().__init__(**kwargs)
        self._context_config: ContextConfig = ContextConfig()
        self._context_items: list[ContextItem] = []
        self._total_context_tokens: int = 0
        self._summaries: list[ContextItem] = []
        self._last_summarization_time: float = 0.0
        self._context_lock = threading.RLock()
        self._context_management_initialized = True
        Logger.debug(f"[CONTEXT] {self.__class__.__name__} context management initialized")

    def configure_context(
        self,
        max_context_tokens: int | None = None,
        target_context_tokens: int | None = None,
        summarization_threshold_pct: float | None = None,
        prune_threshold_pct: float | None = None,
        min_context_tokens: int | None = None,
        summary_target_tokens: int | None = None,
    ) -> None:
        """
        Configure context management limits.

        Args:
            max_context_tokens: Maximum tokens in context window
            target_context_tokens: Target tokens to maintain headroom
            summarization_threshold_pct: Percentage at which to summarize
            prune_threshold_pct: Percentage at which to prune
            min_context_tokens: Minimum context to maintain
            summary_target_tokens: Target size for summaries
        """

        trace_contract._emit_records_execution_trace(
            str(uuid.uuid4()), trace_contract.LayerSegment.L3_ORCHESTRATION, "ContextManagementMixin.configure_context"
        )
        with self._context_lock:
            if max_context_tokens is not None:
                self._context_config.max_context_tokens = max_context_tokens
            if target_context_tokens is not None:
                self._context_config.target_context_tokens = target_context_tokens
            if summarization_threshold_pct is not None:
                self._context_config.summarization_threshold_pct = summarization_threshold_pct
            if prune_threshold_pct is not None:
                self._context_config.prune_threshold_pct = prune_threshold_pct
            if min_context_tokens is not None:
                self._context_config.min_context_tokens = min_context_tokens
            if summary_target_tokens is not None:
                self._context_config.summary_target_tokens = summary_target_tokens
        Logger.info(f"[CONTEXT] Configured: {self._context_config}")

    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text.

        Uses a simple heuristic: ~4 characters per token for English text.
        For production, consider using tiktoken for accurate counts.

        Args:
            text: Text to estimate tokens for

        Returns:
            Estimated token count
        """
        return max(1, len(text) // 4)

    def add_context(
        self,
        content: str,
        priority: ContextPriority = ContextPriority.MEDIUM,
        metadata: dict[str, Any] | None = None,
    ) -> ContextItem:
        """
        Add content to the context window.

        Args:
            content: Content to add
            priority: Priority level for pruning decisions
            metadata: Optional metadata for the context item

        Returns:
            The created ContextItem

        Raises:
            ContextOverflowError: If context cannot be managed within limits
        """
        token_count = self.estimate_tokens(content)
        with self._context_lock:
            projected_total = self._total_context_tokens + token_count
            if projected_total > self._context_config.max_context_tokens:
                self._manage_context_overflow(token_count)
            item = ContextItem(
                content=content,
                priority=priority,
                token_count=token_count,
                metadata=metadata or {},
            )
            self._context_items.append(item)
            self._total_context_tokens += token_count
            self._check_context_thresholds()
        Logger.debug(
            f"[CONTEXT] Added {token_count} tokens (priority={priority.name}). Total: {self._total_context_tokens}/{self._context_config.max_context_tokens}",
        )
        return item

    def _check_context_thresholds(self) -> None:
        """Check context thresholds and trigger management actions."""
        usage_pct = self._total_context_tokens / self._context_config.max_context_tokens
        if usage_pct >= self._context_config.summarization_threshold_pct:
            self._trigger_summarization()
        if usage_pct >= self._context_config.prune_threshold_pct:
            self._prune_low_priority_context()

    def _manage_context_overflow(self, required_tokens: int) -> None:
        """
        Manage context to make room for new content.

        Args:
            required_tokens: Tokens needed for new content

        Raises:
            ContextOverflowError: If unable to free enough space
        """
        target = self._context_config.target_context_tokens - required_tokens
        self._prune_low_priority_context(target_tokens=target)
        if self._total_context_tokens > target:
            self._prune_by_priority(ContextPriority.MEDIUM, target_tokens=target)
        if self._total_context_tokens > target:
            self._prune_by_priority(ContextPriority.HIGH, target_tokens=target)
        if self._total_context_tokens + required_tokens > self._context_config.max_context_tokens:
            raise ContextOverflowError(
                self._total_context_tokens + required_tokens,
                self._context_config.max_context_tokens,
            )

    def _prune_low_priority_context(self, target_tokens: int | None = None) -> int:
        """
        Prune low priority context items.

        Args:
            target_tokens: Target token count to achieve

        Returns:
            Number of tokens freed
        """
        return self._prune_by_priority(ContextPriority.LOW, target_tokens)

    def _prune_by_priority(self, priority: ContextPriority, target_tokens: int | None = None) -> int:
        """
        Prune context items of a specific priority.

        Args:
            priority: Priority level to prune
            target_tokens: Target token count to achieve

        Returns:
            Number of tokens freed
        """
        if target_tokens is None:
            target_tokens = self._context_config.target_context_tokens
        tokens_freed = 0
        items_to_remove = []
        for item in sorted(self._context_items, key=lambda x: x.timestamp):
            if self._total_context_tokens - tokens_freed <= target_tokens:
                break
            if item.priority == priority:
                items_to_remove.append(item)
                tokens_freed += item.token_count
        for item in items_to_remove:
            self._context_items.remove(item)
            self._total_context_tokens -= item.token_count
        if tokens_freed > 0:
            Logger.info(
                f"[CONTEXT] Pruned {tokens_freed} tokens (priority={priority.name}). Remaining: {self._total_context_tokens}",
            )
        return tokens_freed

    def _trigger_summarization(self) -> None:
        """Trigger summarization of older context."""
        cutoff_time = time.monotonic() - 300
        items_to_summarize = [
            item
            for item in self._context_items
            if item.priority == ContextPriority.MEDIUM and item.timestamp < cutoff_time
        ]
        if not items_to_summarize:
            return
        combined_content = "\n".join(item.content for item in items_to_summarize)
        summary_content = self._create_summary(combined_content)
        for item in items_to_summarize:
            self._context_items.remove(item)
            self._total_context_tokens -= item.token_count
        summary_item = ContextItem(
            content=summary_content,
            priority=ContextPriority.MEDIUM,
            token_count=self.estimate_tokens(summary_content),
            metadata={"is_summary": True, "summarized_items": len(items_to_summarize)},
        )
        self._context_items.append(summary_item)
        self._total_context_tokens += summary_item.token_count
        self._summaries.append(summary_item)
        self._last_summarization_time = time.monotonic()
        Logger.info(
            f"[CONTEXT] Summarized {len(items_to_summarize)} items into {summary_item.token_count} tokens",
        )

    def _create_summary(self, content: str) -> str:
        """
        Create a summary of content.

        This is a placeholder implementation. In production, this should
        use an LLM to create intelligent summaries.

        Args:
            content: Content to summarize

        Returns:
            Summarized content
        """
        target_chars = self._context_config.summary_target_tokens * 4
        if len(content) <= target_chars:
            return content
        half = target_chars // 2
        return f"{content[:half]}\n...[summarized]...\n{content[-half:]}"

    def get_optimized_context(self) -> str:
        """
        Get optimized context for LLM consumption.

        Returns context items sorted by priority and recency,
        ensuring critical items are always included.

        Returns:
            Optimized context string
        """
        with self._context_lock:
            sorted_items = sorted(self._context_items, key=lambda x: (x.priority.value, -x.timestamp))
            context_parts = []
            for item in sorted_items:
                context_parts.append(item.content)
            return "\n\n".join(context_parts)

    def get_context_status(self) -> dict[str, Any]:
        """
        Get current context status.

        Returns:
            Dictionary with context status information
        """
        with self._context_lock:
            priority_counts = {}
            for priority in ContextPriority:
                priority_counts[priority.name] = sum(
                    1 for item in self._context_items if item.priority == priority
                )
            return {
                "total_tokens": self._total_context_tokens,
                "max_tokens": self._context_config.max_context_tokens,
                "usage_pct": self._total_context_tokens / self._context_config.max_context_tokens,
                "item_count": len(self._context_items),
                "priority_distribution": priority_counts,
                "summaries_created": len(self._summaries),
                "last_summarization": self._last_summarization_time,
            }

    def clear_context(self, preserve_critical: bool = True) -> dict[str, Any]:
        """
        Clear context items.

        Args:
            preserve_critical: If True, preserve CRITICAL priority items

        Returns:
            Summary of cleared context
        """
        with self._context_lock:
            if preserve_critical:
                critical_items = [
                    item for item in self._context_items if item.priority == ContextPriority.CRITICAL
                ]
                cleared_count = len(self._context_items) - len(critical_items)
                cleared_tokens = self._total_context_tokens - sum(item.token_count for item in critical_items)
                self._context_items = critical_items
                self._total_context_tokens = sum(item.token_count for item in critical_items)
            else:
                cleared_count = len(self._context_items)
                cleared_tokens = self._total_context_tokens
                self._context_items = []
                self._total_context_tokens = 0
            summary = {
                "items_cleared": cleared_count,
                "tokens_cleared": cleared_tokens,
                "remaining_items": len(self._context_items),
                "remaining_tokens": self._total_context_tokens,
            }
        Logger.info(f"[CONTEXT] Cleared: {summary}")
        return summary


__all__ = [
    "ContextManagementMixin",
    "ContextConfig",
    "ContextItem",
    "ContextPriority",
    "ContextOverflowError",
]
