"""ExecutionGateway — L2 execution engine with ExecutionTraceBuilder wiring.

Provides deterministic execution with trace building, replay key computation,
and immutable audit trails.
"""

from __future__ import annotations

import hashlib
import time
from typing import Any

from agentic_core.L2_execution.enforcement.budget_enforcer import BudgetEnforcer, BudgetExceeded
from agentic_core.L2_execution.enforcement.key_source import get_current_secret
from agentic_core.L2_execution.types.execution_trace import ExecutionTrace, ExecutionTraceBuilder
from agentic_core.L2_execution.types.sandbox_envelope import SandboxEnvelope, SignatureVerificationError


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
        # FAIL-CLOSED: Verify signature BEFORE ANY side-effects (logging, state, IO, network)
        try:
            envelope.verify(get_current_secret())
        except SignatureVerificationError:
            # No logging, no state changes, immediate fail-closed exit
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

        start_ms = int(time.time() * 1000)

        stdout_bytes: bytes = b""
        exit_code: int = -1
        try:
            # Execute under budget caps — returns (exit_code, stdout_bytes) per Contract [3]
            exit_code, stdout_bytes = self._budget_enforcer.run(envelope, tool_fn)
            builder.validation_decision = "PASS" if exit_code == 0 else "FAIL"
            builder.error = None if exit_code == 0 else f"Tool exited with code {exit_code}"
        except BudgetExceeded as e:
            builder.validation_decision = "FAIL"
            builder.error = f"Budget exceeded: {e}"
            raise
        finally:
            builder.timing_ms = int(time.time() * 1000) - start_ms
            # Wire stdout_bytes and exit_code into trace extra for ToolResult audit (Contract [3])
            builder.extra = {
                "stdout_bytes": len(stdout_bytes),
                "stdout_hash": hashlib.sha256(stdout_bytes).hexdigest(),
                "exit_code": exit_code,
                "budget_compute_ms": envelope.budget.compute_ms,
                "budget_memory_mb": envelope.budget.memory_mb,
                "budget_stdout_bytes": envelope.budget.stdout_bytes,
            }
            # hash_chain_root via deterministic inputs
            builder.hash_chain_root = hashlib.sha256(
                f"{builder.trace_id}{builder.timing_ms}{builder.validation_decision}".encode()
            ).hexdigest()

        trace = builder.seal()
        return trace, stdout_bytes  # return raw stdout_bytes for ToolResult construction

    def create_envelope(
        self,
        tool_name: str,
        tool_args: dict[str, Any],
        instruction_packet_id: str,
        agent_id: str,
        **metadata: Any,
    ) -> SandboxEnvelope:
        """Create a signed SandboxEnvelope for execution."""
        from agentic_core.L2_execution.types.sandbox_envelope import ToolBudget

        env_metadata = {"agent_id": agent_id, **metadata}
        envelope = SandboxEnvelope(
            envelope_id=f"{instruction_packet_id}_{tool_name}",
            tool_name=tool_name,
            tool_args=tool_args,
            instruction_packet_id=instruction_packet_id,
            invocation_metadata=env_metadata,
            budget=ToolBudget(),  # Use defaults
        )
        return envelope
