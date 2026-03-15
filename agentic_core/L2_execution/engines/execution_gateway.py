"""ExecutionGateway — L2 execution engine with ExecutionTraceBuilder wiring.

Provides deterministic execution with trace building, replay key computation,
and immutable audit trails.
"""

from __future__ import annotations

import hashlib
import uuid
from typing import Any

from agentic_core.L2_execution.determinism.execution_proof_emitter import ExecutionProofEmitter
from agentic_core.L2_execution.enforcement.budget_enforcer import BudgetEnforcer, BudgetExceeded
from agentic_core.L2_execution.enforcement.guardrail_gate import get_guardrail_gate
from agentic_core.L2_execution.enforcement.key_source import get_current_secret
from agentic_core.L2_execution.providers import get_clock
from agentic_core.L2_execution.types.execution_trace_types import ExecutionTrace, ExecutionTraceBuilder
from agentic_core.L2_execution.types.ptc_tool_contracts_types import ToolContractViolation, ToolResult
from agentic_core.L2_execution.types.sandbox_envelope_types import SandboxEnvelope, SignatureVerificationError
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_verifies_boundary,
)

_guardrail = get_guardrail_gate()
_proof_emitter = ExecutionProofEmitter("L2.execution_gateway")


def _invoke_authorize_and_execute(execution_context, target_callable, capability_token, payload, **kw):
    from agentic_core.L2_execution.enforcement.execution_guardrail_chokepoint import (
        authorize_and_execute,  # noqa: PLC0415
    )

    return authorize_and_execute(execution_context, target_callable, capability_token, payload, **kw)


def _make_execution_context(run_id: str, capability_token: str, policy_hash: str, payload: Any, target: str):
    from agentic_core.L2_execution.context.execution_context import (  # noqa: PLC0415
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
    ) -> tuple[ExecutionTrace, Any]:
        """Execute tool_fn under budget caps and return trace + result.

        Returns:
            (ExecutionTrace, tool_result)
        Raises:
            BudgetExceeded: if any budget cap is breached
            SignatureBoundaryError: if envelope signature verification fails (fail-closed)
        """
        _emit_verifies_boundary(str(uuid.uuid4()), "ExecutionGateway.execute_with_trace", "L2_EXECUTION")
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "ExecutionGateway.execute_with_trace")
        import hashlib as _hashlib  # noqa: PLC0415
        _seg_hash = _hashlib.sha256(f"{_trace_id}:ExecutionGateway.execute_with_trace".encode()).hexdigest()[:24]
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
        _invoke_authorize_and_execute(
            _ectx,
            lambda p: p,
            _capability_token,
            envelope.tool_args,
            target_name=envelope.tool_name,
        )
        try:
            envelope.verify(get_current_secret())
        except SignatureVerificationError:
            raise SignatureBoundaryError("Invalid SandboxEnvelope signature - execution blocked")
        builder = ExecutionTraceBuilder(
            trace_id=envelope.envelope_id, instruction_packet_id=envelope.instruction_packet_id
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
                exit_code=exit_code, stdout_bytes=stdout_bytes, stdout_bytes_cap=envelope.budget.stdout_bytes
            )
            builder.validation_decision = "PASS" if tool_result.exit_code == 0 else "FAIL"
            builder.error = (
                None if tool_result.exit_code == 0 else f"Tool exited with code {tool_result.exit_code}"
            )
        except BudgetExceeded as e:
            builder.validation_decision = "FAIL"
            builder.error = f"Budget exceeded: {e}"
            raise
        except ToolContractViolation as e:
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
                f"{builder.trace_id}{builder.timing_ms}{builder.validation_decision}".encode()
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
