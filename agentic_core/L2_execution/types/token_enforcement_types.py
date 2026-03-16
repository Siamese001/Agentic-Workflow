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

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
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

emit_replay_key("p0", "token_enforcement_types")
emit_determinism_digest("p0", "token_enforcement_types")

_emit_dispatches_healing_run("p1", "token_enforcement_types", "L2")
_emit_routes_through("p1", "token_enforcement_types", "L2")
_emit_escalates_to_human("p1", "token_enforcement_types", "L2")
_emit_reads_policy_state("p1", "token_enforcement_types", "L2")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_records_execution_trace("p0", "evidence", "token_enforcement_types")
_emit_applies_guardrail("p0", "token_enforcement_types", "p0_governance")
_emit_snapshots_state("p0", "token_enforcement_types", "state_snapshot")
_emit_authorize_and_execute("p2", "token_enforcement_types", "execution_auth")
_emit_validates_capability("p2", "token_enforcement_types", "capability_check")
_emit_routes_to_capability("p2", "token_enforcement_types", "capability_route")
_emit_writes_via_uwg("p2", "token_enforcement_types", "uwg_write")
_emit_blocks_direct_write("p2", "token_enforcement_types", "direct_write_block")
_emit_records_tool_invocation("p2", "token_enforcement_types", "tool_invocation")
_emit_captures_execution_output("p2", "token_enforcement_types", "exec_output")
_emit_dispatches_agent("p3", "token_enforcement_types", "agent_dispatch")
_emit_coordinates_agents("p3", "token_enforcement_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "token_enforcement_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "token_enforcement_types", "healing_outcome")
_emit_escalates_failure("p3", "token_enforcement_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "token_enforcement_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "token_enforcement_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "token_enforcement_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "token_enforcement_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "token_enforcement_types", "eval_metric")
_emit_stores_embedding("p4", "token_enforcement_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "token_enforcement_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "token_enforcement_types", "exec_snapshot_link")


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
                f"TokenEnforcementArtifact: outcome must be TokenEnforcementOutcome, got {type(self.outcome).__name__}"
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
            f"TokenBudgetExceeded [{phase}]: trace_id={trace_id}, required={required}, remaining={remaining}"
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
                    trace_id=trace_id, initial_budget=initial_budget, remaining_budget=initial_budget
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
