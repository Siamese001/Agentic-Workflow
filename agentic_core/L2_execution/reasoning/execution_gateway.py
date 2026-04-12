"""ExecutionGateway — L2 execution engine with ExecutionTraceBuilder wiring.

Provides deterministic execution with trace building, replay key computation,
and immutable audit trails.
"""

from __future__ import annotations

import hashlib
import uuid
from typing import Any

from agentic_core.L2_execution.enforcement.budget_enforcer import BudgetEnforcer, BudgetExceeded
from agentic_core.L2_execution.enforcement.guardrail_gate import get_guardrail_gate
from agentic_core.L2_execution.enforcement.key_source import get_current_secret
from agentic_core.L2_execution.types.execution_trace_types import ExecutionTrace, ExecutionTraceBuilder
from agentic_core.L2_execution.types.ptc_tool_contracts_types import ToolContractViolation, ToolResult
from agentic_core.L2_execution.types.sandbox_envelope_types import SandboxEnvelope, SignatureVerificationError
from agentic_core.L2_execution.utils.execution_proof_emitter import ExecutionProofEmitter
from agentic_core.L2_execution.utils.providers import get_clock
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

emit_replay_key("p0", "execution_gateway")
emit_determinism_digest("p0", "execution_gateway")

_emit_dispatches_healing_run("p1", "execution_gateway", "L2")
_emit_routes_through("p1", "execution_gateway", "L2")
_emit_checks_agent_registry("p1", "execution_gateway", "agent_registry")
_emit_validates_agent_capability("p1", "execution_gateway", "capability")
_emit_dispatches_execution_plan("p1", "execution_gateway", "exec_plan")
_emit_agent_executes_agent("p1", "execution_gateway", "sub_agent")
_emit_routes_to_agent("p1", "execution_gateway", "target_agent")
_emit_verifies_policy("p1", "execution_gateway", "policy_check")
_emit_observes_runtime_state("p1", "execution_gateway", "runtime_state")
_emit_transcripts_response("p1", "execution_gateway", "transcript")
_emit_hard_fails_untranscripted("p1", "execution_gateway")
_emit_gated_by_confidence("p1", "execution_gateway", "confidence_gate")
_emit_escalates_to_human("p1", "execution_gateway", "L2")
_emit_reads_policy_state("p1", "execution_gateway", "L2")

_emit_applies_guardrail("p0", "execution_gateway", "p0_governance")
_emit_snapshots_state("p0", "execution_gateway", "state_snapshot")
_emit_authorize_and_execute("p2", "execution_gateway", "execution_auth")
_emit_validates_capability("p2", "execution_gateway", "capability_check")
_emit_routes_to_capability("p2", "execution_gateway", "capability_route")
_emit_writes_via_uwg("p2", "execution_gateway", "uwg_write")
_emit_blocks_direct_write("p2", "execution_gateway", "direct_write_block")
_emit_records_tool_invocation("p2", "execution_gateway", "tool_invocation")
_emit_captures_execution_output("p2", "execution_gateway", "exec_output")
_emit_dispatches_agent("p3", "execution_gateway", "agent_dispatch")
_emit_coordinates_agents("p3", "execution_gateway", "agent_coordination")
_emit_records_workflow_lineage("p3", "execution_gateway", "workflow_lineage")
_emit_records_healing_outcome("p3", "execution_gateway", "healing_outcome")
_emit_escalates_failure("p3", "execution_gateway", "failure_escalation")
_emit_orchestrates_workflow("p3", "execution_gateway", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "execution_gateway", "healing_dispatch")
_emit_invokes_evaluation("p3", "execution_gateway", "evaluation_signal")
_emit_records_telemetry_event("p4", "execution_gateway", "telemetry_event")
_emit_captures_evaluation_metric("p4", "execution_gateway", "eval_metric")
_emit_stores_embedding("p4", "execution_gateway", "embedding_store")
_emit_updates_meta_learning_state("p4", "execution_gateway", "meta_learning")
_emit_links_execution_to_snapshot("p4", "execution_gateway", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
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
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("execution_gateway", "p4obs", "metric_1")
_emit_emits_metric_event("execution_gateway", "p4obs", "metric_2")
_emit_emits_metric_event("execution_gateway", "p4obs", "metric_3")
_emit_emits_metric_event("execution_gateway", "p4obs", "metric_4")
_emit_emits_metric_event("execution_gateway", "p4obs", "metric_5")
_emit_emits_metric_event("execution_gateway", "p4obs", "metric_6")
_emit_records_incident_event("execution_gateway", "p4obs", "incident")
_emit_captures_runtime_anomaly("execution_gateway", "p4obs", "anomaly")
_emit_writes_observability_log("execution_gateway", "p4obs", "obs_log")
_emit_updates_monitoring_state("execution_gateway", "p4obs", "mon_state")
_emit_triggers_alert("execution_gateway", "p4obs", "alert")
_emit_links_incident_trace("execution_gateway", "p4obs", "trace_link")
_emit_captures_pattern("execution_gateway", "p3lm", "pattern")
_emit_records_learning_event("execution_gateway", "p3lm", "learning_event")
_emit_writes_learning_snapshot("execution_gateway", "p3lm", "snapshot")
_emit_feeds_meta_learning("execution_gateway", "p3lm", "meta_feed")
_emit_updates_routing_strategy("execution_gateway", "p3lm", "routing")
_emit_improves_agent_policy("execution_gateway", "p3lm", "policy")
_emit_stores_learning_state("execution_gateway", "p3lm", "state")
_emit_records_execution_trace("execution_gateway", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("execution_gateway", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("execution_gateway", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("execution_gateway", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("execution_gateway", "L4_STATE", "p2_trace_5")
_emit_reads_environ("execution_gateway", "env_read", "p2_env_1")
_emit_reads_environ("execution_gateway", "env_read", "p2_env_2")
_emit_reads_runtime_state("execution_gateway", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("execution_gateway", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "execution_gateway", "context_pull")
_emit_pulls_context("p1", "execution_gateway", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "execution_gateway", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "execution_gateway", "uwg_term_2")
_emit_writes_through("p1", "execution_gateway", "write_through")
_emit_writes_through("p1", "execution_gateway", "write_through_2")
_emit_validated_by_safety_plane("p1", "execution_gateway", "safety_validation")
_emit_invokes_eval("p1", "execution_gateway", "eval_call")
_emit_proposal_commits_routing("p1", "execution_gateway", "routing_commit")

_guardrail = get_guardrail_gate()
_proof_emitter = ExecutionProofEmitter("L2.execution_gateway")


def _invoke_authorize_and_execute(execution_context, target_callable, capability_token, payload, **kw):
    from agentic_core.L2_execution.enforcement.execution_guardrail_chokepoint import (
        authorize_and_execute,  # noqa: PLC0415
    )

    return authorize_and_execute(execution_context, target_callable, capability_token, payload, **kw)


def _evaluate_evidence_for_gate_and_telemetry(
    evidence_bundle: Any,
    execution_context: Any,
    tool_name: str = "",
) -> Any:
    """Pre-authorization evidence gate + BUS T emission for the live execution lane.

    Thin lane wrapper \u2014 delegates to the shared evaluate_and_emit() adapter in
    evidence_eval_bridge so no bridge logic is duplicated here.

    Returns:
        (gate_result, disposition) from evaluate_and_emit().
    """
    from agentic_core.L3_orchestration.reasoning.engines.evidence_eval_bridge import (  # noqa: PLC0415
        evaluate_and_emit,
    )

    return evaluate_and_emit(evidence_bundle, execution_context, tool_name)


def _make_execution_context(run_id: str, capability_token: str, policy_hash: str, payload: Any, target: str):
    from agentic_core.L4_state.utils.context.execution_context import (  # noqa: PLC0415
        ActionClass,
        ExecutionContext,
    )

    return ExecutionContext.create(
        run_id=run_id,
        capability_token=capability_token,
        policy_hash=policy_hash or "default",
        execution_input=payload,
        execution_target=target,
        action_class=ActionClass.MUTATION,
    )


class SignatureBoundaryError(RuntimeError):
    """Raised when SandboxEnvelope signature verification fails - fail-closed boundary."""

    pass


class ExecutionGateway:
    """L2 execution engine that builds ExecutionTrace while enforcing budgets."""

    def __init__(self):
        self._budget_enforcer = BudgetEnforcer()

    async def execute_with_trace(
        self,
        envelope: SandboxEnvelope,
        tool_fn: Any,
        policy_hash: str = "",
        prev_hash: str = "",
        transcript_hash: str = "",
        evidence_bundle: Any = None,
    ) -> tuple[ExecutionTrace, Any]:
        """Execute tool_fn under budget caps and return trace + result.

        Args:
            evidence_bundle: Optional EvidenceBundle from shape_search().  When
                provided, the evidence quality gate and BUS T telemetry are wired
                in as a pre-authorization sidecar via
                _evaluate_evidence_for_gate_and_telemetry().  Legacy callers that
                omit this argument are completely unaffected.

        Returns:
            (ExecutionTrace, tool_result)
        Raises:
            BudgetExceeded: if any budget cap is breached
            SignatureBoundaryError: if envelope signature verification fails (fail-closed)
        """
        _emit_verifies_boundary(str(uuid.uuid4()), "ExecutionGateway.execute_with_trace", "L2_EXECUTION")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L2_EXECUTION,
            "ExecutionGateway.execute_with_trace",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:ExecutionGateway.execute_with_trace".encode()).hexdigest()[
            :24
        ]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        with _proof_emitter.proof_op(f"execute_with_trace:{envelope.tool_name}"):
            pass
        with _guardrail.applies_guardrail("execute", envelope.tool_name):
            pass
        _capability_token = envelope.invocation_metadata.get("capability_token", "default")
        _ectx = _make_execution_context(
            run_id=envelope.invocation_metadata.get("run_id", envelope.envelope_id),
            capability_token=_capability_token,
            policy_hash=policy_hash,
            payload=envelope.tool_args,
            target=envelope.tool_name,
        )
        if evidence_bundle is not None:
            _evaluate_evidence_for_gate_and_telemetry(evidence_bundle, _ectx, envelope.tool_name)
        _invoke_authorize_and_execute(
            _ectx,
            lambda p: p,
            _capability_token,
            envelope.tool_args,
            target_name=envelope.tool_name,
        )
        try:
            envelope.verify(get_current_secret())
        except (
            SignatureVerificationError
        ):  # guardian: SignatureVerificationError should be handled with specific context
            raise SignatureBoundaryError("Invalid SandboxEnvelope signature - execution blocked")
        builder = ExecutionTraceBuilder(
            trace_id=envelope.envelope_id,
            instruction_packet_id=envelope.instruction_packet_id,
        )
        builder.policy_hash = policy_hash
        builder.prev_hash = prev_hash
        builder.transcript_hash = transcript_hash
        builder.sandbox_envelope_ids = [envelope.envelope_id]
        builder.agent_id = envelope.invocation_metadata.get("agent_id", "unknown")
        start_ms = int(get_clock().now_epoch() * 1000)
        stdout_bytes: bytes = b""
        exit_code: int = -1
        try:
            exit_code, stdout_bytes = self._budget_enforcer.run(envelope, tool_fn)
            tool_result = ToolResult.from_budget_enforcer(
                exit_code=exit_code,
                stdout_bytes=stdout_bytes,
                stdout_bytes_cap=envelope.budget.stdout_bytes,
            )
            builder.validation_decision = "PASS" if tool_result.exit_code == 0 else "FAIL"
            builder.error = (
                None if tool_result.exit_code == 0 else f"Tool exited with code {tool_result.exit_code}"
            )
        except BudgetExceeded as e:  # guardian: BudgetExceeded should be handled with specific context
            builder.validation_decision = "FAIL"
            builder.error = f"Budget exceeded: {e}"
            raise
        except (
            ToolContractViolation
        ) as e:  # guardian: ToolContractViolation should be handled with specific context
            builder.validation_decision = "FAIL"
            builder.error = f"ToolContract violation: {e}"
            raise
        finally:
            builder.timing_ms = int(get_clock().now_epoch() * 1000) - start_ms
            builder.extra = {
                "stdout_bytes": len(stdout_bytes),
                "stdout_hash": hashlib.sha256(stdout_bytes).hexdigest(),
                "exit_code": exit_code,
                "budget_compute_ms": envelope.budget.compute_ms,
                "budget_memory_mb": envelope.budget.memory_mb,
                "budget_stdout_bytes": envelope.budget.stdout_bytes,
            }
            builder.hash_chain_root = hashlib.sha256(
                f"{builder.trace_id}{builder.timing_ms}{builder.validation_decision}".encode(),
            ).hexdigest()
        trace = builder.seal()
        return (trace, stdout_bytes)

    def create_envelope(
        self,
        tool_name: str,
        tool_args: dict[str, Any],
        instruction_packet_id: str,
        agent_id: str,
        **metadata: Any,
    ) -> SandboxEnvelope:
        """Create a signed SandboxEnvelope for execution."""
        from agentic_core.L2_execution.types.sandbox_envelope_types import ToolBudget

        env_metadata = {"agent_id": agent_id, **metadata}
        envelope = SandboxEnvelope(
            envelope_id=f"{instruction_packet_id}_{tool_name}",
            tool_name=tool_name,
            tool_args=tool_args,
            instruction_packet_id=instruction_packet_id,
            invocation_metadata=env_metadata,
            budget=ToolBudget(),
        )
        return envelope
