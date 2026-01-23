"""
HOP Orchestrator (LIC Sovereign Architecture).

Coordinates the execution of HOP agents 1-8.
Handles retry loops and manages immutable state transitions.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from apps_lic.domain.config.loader import load_agent_specs
from apps_lic.domain.config.schemas import AgentSpecs
from apps_lic.shared.core.immutable_buffer import ImmutableStagingBuffer
from apps_lic.shared.core.trace_registry import TraceRegistry
from apps_lic.shared.core.mixins import SubatomicTestingMixin, MCPHardenedMixin, HealerMixin
from apps_lic.shared.core.agent_base import LICAgentBase


class HOPOrchestratorAgent(LICAgentBase, SubatomicTestingMixin, MCPHardenedMixin, HealerMixin):
    """
    V2 Orchestrator for LIC Outreach Pipeline.

    Manages the execution flow and self-correcting loops (S6->S2, S5 Retry).
    """

    def __init__(self, llm_client: Any | None = None, mission_id: str = "default") -> None:
        self.config: AgentSpecs = load_agent_specs()
        self.llm = llm_client
        # Persistence: Trace lives in logs/missions/{mission_id}/trace.jsonl
        trace_path = Path(f"logs/missions/{mission_id}/trace.jsonl")
        self.registry = TraceRegistry(persistence_path=trace_path)
        self.agents: dict[str, LICAgentBase] = {}

        # Global Safety Limits
        self.GLOBAL_STEP_LIMIT = 20  # Absolute max hops to prevent infinite loops

    def register_agent(self, hop_id: str, agent: LICAgentBase) -> None:
        """Registers a LIC-compliant agent instance."""
        self.agents[hop_id] = agent

    def run_mission(self, mission_input: dict[str, Any]) -> dict[str, Any]:
        """
        Executes the full pipeline for a single mission.

        Returns:
            Dict containing status, report, and execution traces.
        """
        # 1. Initialize Root Buffer
        buffer = ImmutableStagingBuffer()
        buffer.write_once("mission_input", mission_input)
        if "recipient_profile" in mission_input:
            buffer.write_once("recipient_profile", mission_input["recipient_profile"])

        self.registry.add_trace(
            "ORCHESTRATOR_START", {"mission_id": mission_input.get("mission_id")}
        )

        try:
            step_count = 0

            # Phase 1-4: Foundation (Linear)
            for hop in ["HOP1", "HOP2", "HOP3", "HOP4"]:
                step_count += 1
                if step_count > self.GLOBAL_STEP_LIMIT:
                    self.registry.add_trace(
                        "CRITICAL_FAILURE", {"reason": "Global step limit exceeded"}
                    )
                    raise RuntimeError(
                        f"Mission aborted: Exceeded global step limit of {self.GLOBAL_STEP_LIMIT}"
                    )
                self._execute_hop(hop, buffer)

            # Phase 5-7: Generation & Validation (Looping)
            max_iterations = 10  # Safety limit
            iteration = 0

            while iteration < max_iterations:
                iteration += 1

                # Check global step limit before each loop iteration
                step_count += 3  # HOP5, HOP6, HOP7
                if step_count > self.GLOBAL_STEP_LIMIT:
                    self.registry.add_trace(
                        "CRITICAL_FAILURE", {"reason": "Global step limit exceeded"}
                    )
                    raise RuntimeError(
                        f"Mission aborted: Exceeded global step limit of {self.GLOBAL_STEP_LIMIT}"
                    )

                # 5. Generate
                self._execute_hop("HOP5", buffer)
                # 6. Validate
                self._execute_hop("HOP6", buffer)
                # 7. Gate Decision
                self._execute_hop("HOP7", buffer)

                gate = buffer.read("hop7_gate_decision")
                if gate["decision"] == "PASS":
                    break

                # Check loop limits
                if not self._check_retry_limits(gate):
                    self.registry.add_trace(
                        "ORCHESTRATOR_LIMIT_EXCEEDED",
                        {"action": gate["action"], "iteration": iteration},
                    )
                    break

                # Handle Retries via Buffer Forking
                action = gate["action"]
                buffer = self._handle_retry(gate, buffer)

                # Re-execute from the appropriate HOP based on retry type
                if action == "RETRY_HOP2":
                    # Factual failure: Re-execute research, then continue through pipeline
                    self._execute_hop("HOP2", buffer)
                    # Don't need to re-execute HOP3/HOP4 as they don't depend on HOP2
                    # Loop will continue with HOP5
                elif action == "RETRY_HOP5":
                    # Creative failure: Just loop back to HOP5 (already handled by while loop)
                    pass

            # Phase 8: Reporting
            self._execute_hop("HOP8", buffer)

            return {
                "status": "SUCCESS",
                "report": buffer.read("hop8_qa_report"),
                "traces": self.registry.get_traces(),
            }

        except Exception as e:
            self.registry.add_trace("ORCHESTRATOR_ERROR", {"error": str(e)})
            return {"status": "FAILED", "error": str(e), "traces": self.registry.get_traces()}

    def _execute_hop(self, hop_id: str, buffer: ImmutableStagingBuffer) -> None:
        """Execute a single HOP agent."""
        if hop_id not in self.agents:
            raise RuntimeError(f"Agent {hop_id} not registered")

        agent = self.agents[hop_id]
        agent.run_phase(buffer, self.registry)

    def _handle_retry(
        self, gate: dict, current_buffer: ImmutableStagingBuffer
    ) -> ImmutableStagingBuffer:
        """
        Creates a new buffer snapshot to allow 'overwriting' state
        in a retry loop without violating V2 immutability.

        Args:
            gate: Gate decision containing action directive
            current_buffer: Current immutable buffer state

        Returns:
            New buffer with selective state retention
        """
        action = gate["action"]
        self.registry.add_trace(
            "ORCHESTRATOR_RETRY", {"action": action, "reason": gate.get("reason")}
        )

        new_buffer = ImmutableStagingBuffer()
        # Seed new buffer with legacy data we want to keep
        snapshot = current_buffer.get_snapshot()

        # Determine which keys to 'clear' (don't copy to new buffer)
        keys_to_purge = ["hop5_generation", "hop6_validation_report", "hop7_gate_decision"]
        if action == "RETRY_HOP2":
            keys_to_purge.append("hop2_research")

        for k, v in snapshot.items():
            if k not in keys_to_purge:
                new_buffer.write_once(k, v)

        return new_buffer

    def _check_retry_limits(self, gate: dict) -> bool:
        """
        Check if retry limits have been exceeded.

        Uses TraceRegistry to count retries instead of internal state.
        """
        action = gate["action"]
        traces = self.registry.get_traces()

        # Count retries by action type
        retry_count = sum(
            1
            for t in traces
            if t.get("type") == "ORCHESTRATOR_RETRY"
            and t.get("details", {}).get("action") == action
        )

        if action == "RETRY_HOP2":
            max_retries = self.config.gate_decision_agent.max_factual_loops
        elif action == "RETRY_HOP5":
            max_retries = self.config.gate_decision_agent.max_creative_retries
        else:
            return False  # Unknown action, halt

        return retry_count < max_retries
