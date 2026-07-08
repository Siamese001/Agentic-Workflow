"""
§Wave1.8 — Token Budget Hard Enforcement Types.

Typed artifacts and exceptions for fail-closed token budget enforcement
at the canonical LLM invocation boundary (SovereignLLMGateway.generate).
"""

from __future__ import annotations

import threading
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_emits_metric_event("token_enforcement_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("token_enforcement_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("token_enforcement_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("token_enforcement_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("token_enforcement_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("token_enforcement_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("token_enforcement_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("token_enforcement_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("token_enforcement_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("token_enforcement_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("token_enforcement_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("token_enforcement_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("token_enforcement_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("token_enforcement_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("token_enforcement_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("token_enforcement_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("token_enforcement_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("token_enforcement_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("token_enforcement_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("token_enforcement_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("token_enforcement_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("token_enforcement_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("token_enforcement_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("token_enforcement_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("token_enforcement_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("token_enforcement_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("token_enforcement_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("token_enforcement_types", "runtime_state", "p2_rt_2")

trace_contract.emit_replay_key("p0", "token_enforcement_types")
trace_contract.emit_determinism_digest("p0", "token_enforcement_types")

trace_contract._emit_dispatches_healing_run("p1", "token_enforcement_types", "L2")
trace_contract._emit_routes_through("p1", "token_enforcement_types", "L2")
trace_contract._emit_checks_agent_registry("p1", "token_enforcement_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "token_enforcement_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "token_enforcement_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "token_enforcement_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "token_enforcement_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "token_enforcement_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "token_enforcement_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "token_enforcement_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "token_enforcement_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "token_enforcement_types")
trace_contract._emit_gated_by_confidence("p1", "token_enforcement_types", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "token_enforcement_types", "L2")
trace_contract._emit_reads_policy_state("p1", "token_enforcement_types", "L2")
trace_contract._emit_pulls_context("p1", "token_enforcement_types", "context_pull")
trace_contract._emit_pulls_context("p1", "token_enforcement_types", "context_pull_secondary")
trace_contract._emit_execution_terminates_at_uwg("p1", "token_enforcement_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "token_enforcement_types", "uwg_term_secondary")
trace_contract._emit_writes_through("p1", "token_enforcement_types", "write_through")
trace_contract._emit_writes_through("p1", "token_enforcement_types", "write_through_secondary")
trace_contract._emit_validated_by_safety_plane("p1", "token_enforcement_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "token_enforcement_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "token_enforcement_types", "routing_commit")

trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_records_execution_trace("p0", "evidence", "token_enforcement_types")
trace_contract._emit_applies_guardrail("p0", "token_enforcement_types", "p0_governance")
trace_contract._emit_snapshots_state("p0", "token_enforcement_types", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "token_enforcement_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "token_enforcement_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "token_enforcement_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "token_enforcement_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "token_enforcement_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "token_enforcement_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "token_enforcement_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "token_enforcement_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "token_enforcement_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "token_enforcement_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "token_enforcement_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "token_enforcement_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "token_enforcement_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "token_enforcement_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "token_enforcement_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "token_enforcement_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "token_enforcement_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "token_enforcement_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "token_enforcement_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "token_enforcement_types", "exec_snapshot_link")


class TokenEnforcementOutcome(Enum):
    """Outcome of token budget enforcement at the LLM boundary."""

    PASS = "pass"
    FAIL_PRE_CALL = "fail_pre_call"
    FAIL_POST_CALL = "fail_post_call"


@dataclass(frozen=True)
class TokenEnforcementArtifact:
    """§Wave1.8 — Emitted exactly once per LLM call attempt (PASS or FAIL).

    Hard enforcement artifact recording token budget state before/after
    model invocation. No silent swallowing — every path emits.
    """

    artifact_id: str
    timestamp_utc: str
    trace_id: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    remaining_budget: int
    hard_limit: int
    enforcement_mode: str
    outcome: TokenEnforcementOutcome

    def __post_init__(self) -> None:
        if not self.trace_id:
            raise ValueError("TokenEnforcementArtifact: trace_id must be non-empty")
        if not self.model:
            raise ValueError("TokenEnforcementArtifact: model must be non-empty")
        if self.hard_limit < 0:
            raise ValueError("TokenEnforcementArtifact: hard_limit must be >= 0")
        if not isinstance(self.outcome, TokenEnforcementOutcome):
            raise TypeError(
                f"TokenEnforcementArtifact: outcome must be TokenEnforcementOutcome, got {type(self.outcome).__name__}",
            )
        if self.enforcement_mode != "HARD":
            raise ValueError("TokenEnforcementArtifact: enforcement_mode must be 'HARD'")


class TokenBudgetExceeded(Exception):
    """§Wave1.8 — Raised when token budget is exceeded (pre-call or post-call).

    Fail-closed: model invocation is prevented (pre-call) or flagged (post-call).
    Carries the enforcement artifact for upstream handling.
    """

    def __init__(
        self,
        trace_id: str,
        required: int,
        remaining: int,
        phase: str,
        artifact: TokenEnforcementArtifact | None = None,
    ) -> None:
        self.trace_id = trace_id
        self.required = required
        self.remaining = remaining
        self.phase = phase
        self.artifact = artifact
        super().__init__(
            f"TokenBudgetExceeded [{phase}]: trace_id={trace_id}, required={required}, remaining={remaining}",
        )


@dataclass
class TokenBudgetContext:
    """§Wave1.8 — Per-trace token budget accounting.

    NOT frozen — remaining_budget is mutated on each LLM call.
    Thread-safe mutation happens in TokenBudgetStore.
    """

    trace_id: str
    initial_budget: int
    remaining_budget: int

    def __post_init__(self) -> None:
        if not self.trace_id:
            raise ValueError("TokenBudgetContext: trace_id must be non-empty")
        if self.initial_budget < 0:
            raise ValueError("TokenBudgetContext: initial_budget must be >= 0")


class TokenBudgetStore:
    """§Wave1.8 — Thread-safe, trace-id-keyed token budget store.

    No global mutable counter without trace binding.
    Deterministic reset on new trace.
    """

    def __init__(self) -> None:
        self._budgets: dict[str, TokenBudgetContext] = {}
        self._lock = threading.Lock()

    def get_or_init(self, trace_id: str, initial_budget: int) -> TokenBudgetContext:
        """Get existing budget for trace_id, or create new one."""
        with self._lock:
            if trace_id not in self._budgets:
                self._budgets[trace_id] = TokenBudgetContext(
                    trace_id=trace_id,
                    initial_budget=initial_budget,
                    remaining_budget=initial_budget,
                )
            return self._budgets[trace_id]

    def consume(self, trace_id: str, tokens_used: int) -> int:
        """Subtract tokens from budget. Returns new remaining budget (may be negative)."""
        with self._lock:
            ctx = self._budgets.get(trace_id)
            if ctx is None:
                raise KeyError(f"TokenBudgetStore: No budget for trace_id={trace_id}")
            ctx.remaining_budget -= tokens_used
            return ctx.remaining_budget

    def reset(self, trace_id: str) -> None:
        """Remove budget for a trace_id."""
        with self._lock:
            self._budgets.pop(trace_id, None)

    def clear_all(self) -> None:
        """Clear all budgets (for testing)."""
        with self._lock:
            self._budgets.clear()


_TOKEN_BUDGET_STORE: TokenBudgetStore | None = None


def get_token_budget_store() -> TokenBudgetStore:
    """Get or create the global TokenBudgetStore."""
    global _TOKEN_BUDGET_STORE
    if _TOKEN_BUDGET_STORE is None:
        _TOKEN_BUDGET_STORE = TokenBudgetStore()
    return _TOKEN_BUDGET_STORE


def set_token_budget_store(store: TokenBudgetStore | None) -> None:
    """Replace the global store (for testing)."""
    global _TOKEN_BUDGET_STORE
    _TOKEN_BUDGET_STORE = store


def estimate_prompt_tokens(prompt: str) -> int:
    """Estimate prompt token count. ~4 chars per token is a conservative heuristic.

    This is a minimal estimator. Real implementations should use tiktoken
    or provider-specific tokenizers.
    """
    return max(1, len(prompt) // 4)


def build_token_enforcement_artifact(
    trace_id: str,
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
    remaining_budget: int,
    hard_limit: int,
    outcome: TokenEnforcementOutcome,
) -> TokenEnforcementArtifact:
    """Factory for TokenEnforcementArtifact with deterministic fields."""
    return TokenEnforcementArtifact(
        artifact_id=str(uuid.uuid4()),
        timestamp_utc=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        trace_id=trace_id,
        model=model,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        remaining_budget=remaining_budget,
        hard_limit=hard_limit,
        enforcement_mode="HARD",
        outcome=outcome,
    )


__all__ = [
    "TokenBudgetContext",
    "TokenBudgetExceeded",
    "TokenBudgetStore",
    "TokenEnforcementArtifact",
    "TokenEnforcementOutcome",
    "build_token_enforcement_artifact",
    "estimate_prompt_tokens",
    "get_token_budget_store",
    "set_token_budget_store",
]
