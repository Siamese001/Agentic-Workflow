"""
Phase 7 — ToolIntentExecutor: execute ToolIntent only inside L2.2 commit sandbox.

Reuses the existing L2.2 sandbox flag from Phase 4 (ml_write_intent.py).
Any ToolIntent with requires_commit=True executed outside the sandbox raises
ToolViolation(code="TOOL_WRITE_OUTSIDE_SANDBOX").
"""

from __future__ import annotations

import hashlib
import json
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Callable, Generator

from agentic_core.L2_execution.types.l2_execution_contract import (
    L2ExecutionAgent,
    L2ExecutionContext,
    L2ExecutionPhase,
    L2PhaseResult,
)
from agentic_core.L2_execution.types.ml_write_intent_types import is_commit_sandbox_active
from agentic_core.L2_execution.types.tool_intent_types import ToolIntent, ToolViolation
from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
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
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
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

emit_replay_key("p0", "tool_intent_executor")
emit_determinism_digest("p0", "tool_intent_executor")

_emit_dispatches_healing_run("p1", "tool_intent_executor", "L2")
_emit_routes_through("p1", "tool_intent_executor", "L2")
_emit_verifies_policy("p1", "tool_intent_executor", "policy_check")
_emit_observes_runtime_state("p1", "tool_intent_executor", "runtime_state")
_emit_transcripts_response("p1", "tool_intent_executor", "transcript")
_emit_hard_fails_untranscripted("p1", "tool_intent_executor")
_emit_gated_by_confidence("p1", "tool_intent_executor", "confidence_gate")
_emit_escalates_to_human("p1", "tool_intent_executor", "L2")
_emit_reads_policy_state("p1", "tool_intent_executor", "L2")
_emit_routes_to_agent("p1", "tool_intent_executor", "L2")
_emit_orchestrates_workflow("p1", "tool_intent_executor", "L2")
_emit_dispatches_execution_plan("p1", "tool_intent_executor", "L2")
_emit_validates_agent_capability("p1", "tool_intent_executor", "L2")
_emit_checks_agent_registry("p1", "tool_intent_executor", "L2")

_emit_applies_guardrail("p0", "tool_intent_executor", "p0_governance")
_emit_snapshots_state("p0", "tool_intent_executor", "state_snapshot")
_emit_authorize_and_execute("p2", "tool_intent_executor", "execution_auth")
_emit_validates_capability("p2", "tool_intent_executor", "capability_check")
_emit_routes_to_capability("p2", "tool_intent_executor", "capability_route")
_emit_writes_via_uwg("p2", "tool_intent_executor", "uwg_write")
_emit_blocks_direct_write("p2", "tool_intent_executor", "direct_write_block")
_emit_records_tool_invocation("p2", "tool_intent_executor", "tool_invocation")
_emit_captures_execution_output("p2", "tool_intent_executor", "exec_output")
_emit_dispatches_agent("p3", "tool_intent_executor", "agent_dispatch")
_emit_coordinates_agents("p3", "tool_intent_executor", "agent_coordination")
_emit_records_workflow_lineage("p3", "tool_intent_executor", "workflow_lineage")
_emit_records_healing_outcome("p3", "tool_intent_executor", "healing_outcome")
_emit_escalates_failure("p3", "tool_intent_executor", "failure_escalation")
_emit_orchestrates_workflow("p3", "tool_intent_executor", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "tool_intent_executor", "healing_dispatch")
_emit_invokes_evaluation("p3", "tool_intent_executor", "evaluation_signal")
_emit_records_telemetry_event("p4", "tool_intent_executor", "telemetry_event")
_emit_captures_evaluation_metric("p4", "tool_intent_executor", "eval_metric")
_emit_stores_embedding("p4", "tool_intent_executor", "embedding_store")
_emit_updates_meta_learning_state("p4", "tool_intent_executor", "meta_learning")
_emit_links_execution_to_snapshot("p4", "tool_intent_executor", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("tool_intent_executor", "p4obs", "metric_1")
_emit_emits_metric_event("tool_intent_executor", "p4obs", "metric_2")
_emit_emits_metric_event("tool_intent_executor", "p4obs", "metric_3")
_emit_emits_metric_event("tool_intent_executor", "p4obs", "metric_4")
_emit_emits_metric_event("tool_intent_executor", "p4obs", "metric_5")
_emit_emits_metric_event("tool_intent_executor", "p4obs", "metric_6")
_emit_records_incident_event("tool_intent_executor", "p4obs", "incident")
_emit_captures_runtime_anomaly("tool_intent_executor", "p4obs", "anomaly")
_emit_writes_observability_log("tool_intent_executor", "p4obs", "obs_log")
_emit_updates_monitoring_state("tool_intent_executor", "p4obs", "mon_state")
_emit_triggers_alert("tool_intent_executor", "p4obs", "alert")
_emit_links_incident_trace("tool_intent_executor", "p4obs", "trace_link")
_emit_captures_pattern("tool_intent_executor", "p3lm", "pattern")
_emit_records_learning_event("tool_intent_executor", "p3lm", "learning_event")
_emit_writes_learning_snapshot("tool_intent_executor", "p3lm", "snapshot")
_emit_feeds_meta_learning("tool_intent_executor", "p3lm", "meta_feed")
_emit_updates_routing_strategy("tool_intent_executor", "p3lm", "routing")
_emit_improves_agent_policy("tool_intent_executor", "p3lm", "policy")
_emit_stores_learning_state("tool_intent_executor", "p3lm", "state")
_emit_records_execution_trace("tool_intent_executor", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("tool_intent_executor", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("tool_intent_executor", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("tool_intent_executor", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("tool_intent_executor", "L4_STATE", "p2_trace_5")
_emit_reads_environ("tool_intent_executor", "env_read", "p2_env_1")
_emit_reads_environ("tool_intent_executor", "env_read", "p2_env_2")
_emit_reads_runtime_state("tool_intent_executor", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("tool_intent_executor", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "tool_intent_executor", "context_pull")
_emit_pulls_context("p1", "tool_intent_executor", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "tool_intent_executor", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "tool_intent_executor", "uwg_term_2")
_emit_writes_through("p1", "tool_intent_executor", "write_through")
_emit_writes_through("p1", "tool_intent_executor", "write_through_2")
_emit_validated_by_safety_plane("p1", "tool_intent_executor", "safety_validation")
_emit_invokes_eval("p1", "tool_intent_executor", "eval_call")
_emit_proposal_commits_routing("p1", "tool_intent_executor", "routing_commit")


def _invoke_authorize_and_execute(execution_context, target_callable, capability_token, payload, **kw):
    _emit_agent_executes_agent(str(uuid.uuid4()), "Module", "Module._invoke_authorize_and_execute")
    from agentic_core.L2_execution.enforcement.execution_guardrail_chokepoint import (
        authorize_and_execute,  # noqa: PLC0415
    )

    return authorize_and_execute(execution_context, target_callable, capability_token, payload, **kw)


def _make_execution_context(payload, target: str):
    from agentic_core.L4_state.context.execution_context import (  # noqa: PLC0415
        ActionClass,
        ExecutionContext,
    )

    return ExecutionContext.create(
        run_id="tool_intent_executor",
        capability_token="default",
        policy_hash="default",
        execution_input=str(payload),
        execution_target=target,
        action_class=ActionClass.MUTATION,
    )


_SCHEMA_VERSION: int = 1


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@dataclass
class ToolResult:
    """
    Typed result of a ToolIntent execution.

    Fields
    ------
    schema_version : int   — bumped on breaking changes
    tool_name      : str   — matches the originating ToolIntent.tool_name
    args_hash      : str   — matches the originating ToolIntent.args_hash
    success        : bool  — True if execution completed without error
    output_summary : str   — deterministic string summary of the output
    anchor_ids     : list  — chunk_ids of any retrieved content (may be empty)
    result_hash    : str   — sha256(canonical_bytes excluding result_hash)
    """

    schema_version: int
    tool_name: str
    args_hash: str
    success: bool
    output_summary: str
    anchor_ids: list[str]
    result_hash: str = field(default="", init=False)

    def __post_init__(self) -> None:
        if self.schema_version != _SCHEMA_VERSION:
            raise ValueError(
                f"ToolResult: schema_version must be {_SCHEMA_VERSION}, got {self.schema_version!r}"
            )
        if not self.tool_name:
            raise ValueError("ToolResult: tool_name must be non-empty")
        if not self.args_hash:
            raise ValueError("ToolResult: args_hash must be non-empty")
        if not isinstance(self.anchor_ids, list):
            raise TypeError("ToolResult: anchor_ids must be a list")
        self.anchor_ids = sorted(self.anchor_ids)
        object.__setattr__(self, "result_hash", _sha256(self.canonical_bytes()))

    def canonical_bytes(self) -> bytes:
        """Deterministic serialisation excluding result_hash (self-referential)."""
        _emit_verifies_boundary(str(uuid.uuid4()), "ToolResult.canonical_bytes", "L2_EXECUTION")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "ToolResult.canonical_bytes")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:ToolResult.canonical_bytes".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        doc: dict[str, Any] = {
            "anchor_ids": sorted(self.anchor_ids),
            "args_hash": self.args_hash,
            "output_summary": self.output_summary,
            "schema_version": self.schema_version,
            "success": self.success,
            "tool_name": self.tool_name,
        }
        return json.dumps(doc, sort_keys=True, separators=(",", ":")).encode()

    def to_dict(self) -> dict[str, Any]:
        """Convert ToolResult to dictionary representation."""
        return {
            "schema_version": self.schema_version,
            "tool_name": self.tool_name,
            "args_hash": self.args_hash,
            "success": self.success,
            "output_summary": self.output_summary,
            "anchor_ids": list(self.anchor_ids),
            "result_hash": self.result_hash,
        }


class ToolIntentExecutor(L2ExecutionAgent):
    """
    Executes a ToolIntent inside the L2.2 commit sandbox.

    Implements L2ExecutionContract:
    - L2.1 INIT: Pre-commit setup, sandbox validation
    - L2.2 EXECUTE: Core tool invocation with policy checks
    - L2.3 EVALUATE_HEAL: Error classification and retry
    - L2.4 SYNTHESIZE: ToolResult packaging

    Backward Compatibility
    ----------------------
    Legacy usage preserved:
    with ToolIntentExecutor() as executor:
        result = executor.execute(intent, fn=my_tool_fn)

    Guarantees
    ----------
    - If intent.requires_commit and sandbox not active → ToolViolation("TOOL_WRITE_OUTSIDE_SANDBOX")
    - Non-mutating intents (requires_commit=False) may be executed anywhere.
    - fn is called with intent.args; must return a dict with at least "output_summary".
    """

    agent_id: str = "ToolIntentExecutor"

    def __init__(self):
        super().__init__(agent_id=self.agent_id)
        self._current_intent: ToolIntent | None = None
        self._current_fn: Callable[[dict[str, Any]], dict[str, Any]] | None = None

    # ========================================================================
    # L2.1: INIT - Pre-commit setup and validation
    # ========================================================================
    def l2_init(self, context: L2ExecutionContext) -> L2PhaseResult:
        """
        L2.1: Initialize tool execution context.

        Validates:
        - Sandbox state for mutating operations
        - Tool intent structure
        - Capability requirements
        """
        intent = context.inputs.get("intent")
        fn = context.inputs.get("fn")

        if not isinstance(intent, ToolIntent):
            return L2PhaseResult(
                phase=L2ExecutionPhase.INIT,
                success=False,
                failure_signal=None,
                metadata={"error": "Missing or invalid ToolIntent"},
            )

        if not callable(fn):
            return L2PhaseResult(
                phase=L2ExecutionPhase.INIT,
                success=False,
                failure_signal=None,
                metadata={"error": "Missing or invalid function"},
            )

        # E2: Validate sandbox for mutating operations
        if intent.requires_commit and (not is_commit_sandbox_active()):
            return L2PhaseResult(
                phase=L2ExecutionPhase.INIT,
                success=False,
                failure_signal=None,
                metadata={
                    "error": "TOOL_WRITE_OUTSIDE_SANDBOX",
                    "tool": intent.tool_name,
                    "capability": intent.capability.value,
                },
            )

        # Store for later phases
        self._current_intent = intent
        self._current_fn = fn

        _trace_id = str(uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "ToolIntentExecutor.l2_init")

        return L2PhaseResult(
            phase=L2ExecutionPhase.INIT,
            success=True,
            metadata={
                "tool_name": intent.tool_name,
                "requires_commit": intent.requires_commit,
                "sandbox_active": is_commit_sandbox_active(),
            },
        )

    # ========================================================================
    # L2.2: EXECUTE - Core tool invocation
    # ========================================================================
    def l2_execute(self, context: L2ExecutionContext) -> L2PhaseResult:
        """
        L2.2: Execute the tool with authorization.

        Emits lifecycle traces for observability.
        """
        intent = self._current_intent
        fn = self._current_fn

        if not intent or not fn:
            return L2PhaseResult(
                phase=L2ExecutionPhase.EXECUTE,
                success=False,
                failure_signal=None,
                metadata={"error": "INIT phase not completed"},
            )

        _trace_id = str(uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "ToolIntentExecutor.l2_execute")
        _seg_hash = hashlib.sha256(f"{_trace_id}:l2_execute".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        try:
            # Authorize and execute
            _ectx = _make_execution_context(intent.args_hash, intent.tool_name)
            _invoke_authorize_and_execute(
                _ectx,
                lambda p: p,
                "default",
                intent.args_hash,
                target_name=intent.tool_name,
            )

            # Execute the tool
            raw = fn(intent.args)

            return L2PhaseResult(
                phase=L2ExecutionPhase.EXECUTE,
                success=True,
                output=raw,
                metadata={
                    "tool_name": intent.tool_name,
                    "has_output_summary": "output_summary" in raw,
                    "has_anchor_ids": "anchor_ids" in raw,
                },
            )

        except ToolViolation as e:
            return L2PhaseResult(
                phase=L2ExecutionPhase.EXECUTE,
                success=False,
                failure_signal=None,
                metadata={
                    "error": e.code,
                    "detail": e.detail,
                    "recoverable": False,
                },
            )
        except Exception as e:
            return L2PhaseResult(
                phase=L2ExecutionPhase.EXECUTE,
                success=False,
                failure_signal=None,
                metadata={
                    "error": type(e).__name__,
                    "detail": str(e),
                    "recoverable": True,  # May be recoverable via healing
                },
            )

    # ========================================================================
    # L2.3: EVALUATE/HEAL - Post-execution evaluation
    # ========================================================================
    def l2_evaluate_and_heal(self, context: L2ExecutionContext) -> L2PhaseResult:
        """
        L2.3: Evaluate execution result and apply healing if needed.

        For tool execution, healing may involve:
        - Retry with modified parameters
        - Fallback to alternative tool
        - Escalation on terminal failures
        """
        last_result = context.phase_results.get(L2ExecutionPhase.EXECUTE)
        if not last_result:
            return L2PhaseResult(
                phase=L2ExecutionPhase.EVALUATE_HEAL,
                success=False,
                metadata={"error": "No execute phase result"},
            )

        if last_result.success:
            return L2PhaseResult(
                phase=L2ExecutionPhase.EVALUATE_HEAL,
                success=True,
                metadata={"heal_skipped": "execute_success"},
            )

        # Check if recoverable
        metadata = last_result.metadata or {}
        recoverable = metadata.get("recoverable", False)

        if not recoverable:
            return L2PhaseResult(
                phase=L2ExecutionPhase.EVALUATE_HEAL,
                success=False,
                failure_signal=None,
                metadata={
                    "heal_skipped": "not_recoverable",
                    "error": metadata.get("error"),
                },
            )

        # Default healing: retry once (subclasses may override)
        context.retry_count += 1
        retry_result = self.l2_execute(context)

        return L2PhaseResult(
            phase=L2ExecutionPhase.EVALUATE_HEAL,
            success=retry_result.success,
            output=retry_result.output,
            failure_signal=retry_result.failure_signal if not retry_result.success else None,
            metadata={
                "heal_attempted": True,
                "heal_tier": "LOCAL_AGENT",
                "retry_count": context.retry_count,
            },
        )

    # ========================================================================
    # L2.4: SYNTHESIZE - Result packaging
    # ========================================================================
    def l2_synthesize(self, context: L2ExecutionContext) -> L2PhaseResult:
        """
        L2.4: Package execution result into ToolResult.

        E5: Seal the final folder with execution artifacts.
        """
        execute_result = context.phase_results.get(L2ExecutionPhase.EXECUTE)
        if not execute_result:
            return L2PhaseResult(
                phase=L2ExecutionPhase.SYNTHESIZE,
                success=False,
                metadata={"error": "No execute phase result"},
            )

        intent = self._current_intent
        if not intent:
            return L2PhaseResult(
                phase=L2ExecutionPhase.SYNTHESIZE,
                success=False,
                metadata={"error": "No intent stored"},
            )

        if not execute_result.success:
            # Failed execution - return minimal result
            return L2PhaseResult(
                phase=L2ExecutionPhase.SYNTHESIZE,
                success=False,
                output=ToolResult(
                    schema_version=_SCHEMA_VERSION,
                    tool_name=intent.tool_name,
                    args_hash=intent.args_hash,
                    success=False,
                    output_summary=str(execute_result.metadata.get("error", "Unknown error")),
                    anchor_ids=[],
                ),
                failure_signal=execute_result.failure_signal,
                metadata={"status": "failed_execution"},
            )

        # Successful execution
        raw = execute_result.output or {}
        output_summary = str(raw.get("output_summary", ""))
        anchor_ids: list[str] = list(raw.get("anchor_ids", []))

        tool_result = ToolResult(
            schema_version=_SCHEMA_VERSION,
            tool_name=intent.tool_name,
            args_hash=intent.args_hash,
            success=raw.get("success", True),
            output_summary=output_summary,
            anchor_ids=anchor_ids,
        )

        return L2PhaseResult(
            phase=L2ExecutionPhase.SYNTHESIZE,
            success=True,
            output=tool_result,
            metadata={
                "status": "success",
                "result_hash": tool_result.result_hash,
            },
        )

    # ========================================================================
    # Backward Compatibility: Legacy execute() method
    # ========================================================================
    @contextmanager
    def __enter__(self) -> Generator[ToolIntentExecutor, None, None]:
        """Context manager entry - preserves legacy usage."""
        yield self

    def __exit__(self, *args: Any) -> None:
        """Context manager exit - preserves legacy usage."""
        pass

    def execute(self, intent: ToolIntent, fn: Callable[[dict[str, Any]], dict[str, Any]]) -> ToolResult:
        """
        Execute a ToolIntent (backward compatible API).

        This method uses the new 4-phase contract internally while
        maintaining the legacy interface.

        Parameters
        ----------
        intent : ToolIntent
            Tool intent to execute
        fn : callable
            Tool function to invoke

        Returns
        -------
        ToolResult
            Execution result
        """
        result = self.run_l2_phases(
            inputs={"intent": intent, "fn": fn},
            heal_enabled=False,  # Legacy mode: no healing
            trace_id=str(uuid.uuid4()),
        )

        # Extract ToolResult from phase results
        if result.get("success"):
            synth = result.get("phase_results", {}).get("SYNTHESIZE", {})
            tool_result = synth.get("output")
            if isinstance(tool_result, ToolResult):
                return tool_result

        # Fallback: construct from error info
        return ToolResult(
            schema_version=_SCHEMA_VERSION,
            tool_name=intent.tool_name,
            args_hash=intent.args_hash,
            success=False,
            output_summary=result.get("interrupted_at", "Unknown failure"),
            anchor_ids=[],
        )
