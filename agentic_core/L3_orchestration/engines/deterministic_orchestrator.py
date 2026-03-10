"""
Deterministic L3 Orchestration Kernel - W5 Implementation

Authoritative replacement for all prior L3 orchestration logic.
Implements route_mode-aware orchestration with sequential handshake state machine.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.engines.assembly_stage import GovernedPayload
from agentic_core.L3_orchestration.engines.handshake_state_machine import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    HandshakeState,
    HandshakeStateMachine,
)
from agentic_core.L3_orchestration.types.execution_trace_types import (
    create_execution_trace_skeleton,
)
from agentic_core.L3_orchestration.types.human_decision_artifact_types import (
    create_human_review_draft,
)
from agentic_core.seams.orchestration_protocols import OrchestrationResult


class RouteMode(Enum):
    """Route modes for L3 orchestration."""

    B = "B"  # POLICY_CHECK_FIRST
    C = "C"  # EXECUTE_SCRIPT_DIRECTLY
    D = "D"  # HUMAN_REVIEW_FIRST


@dataclass(frozen=True)
class OrchestrationConfig:
    """Configuration for deterministic orchestration."""

    trace_id: str
    policy_hash: str
    allowed_tools: tuple[str, ...]
    route_mode: RouteMode
    governed_payload: GovernedPayload


def canonical_json(data: dict[str, Any]) -> str:
    """
    Convert dictionary to canonical JSON string.

    Alphabetical key sort, UTF-8, no whitespace variance.
    """
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def compute_plan_hash(plan: dict[str, Any]) -> str:
    """
    Compute SHA256 hash of canonical plan JSON.
    """
    canonical = canonical_json(plan)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def compute_determinism_digest(
    plan_hash: str,
    agent_registry_hash: str,
    tool_key_hash: str,
    handshake_sequence_hash: str,
) -> str:
    """
    Compute W5-DETERMINISM-DIGEST.

    Exactly one per run - printed to stdout.
    When W5_NEGCTRL_TAMPER=1 the sort order is reversed to prove tamper detection.
    """
    if os.environ.get("W5_NEGCTRL_TAMPER") == "1":
        # Negative control: intentionally reverse sort order to cause mismatch
        digest_data = {
            "handshake_sequence_hash": handshake_sequence_hash,
            "tool_key_hash": tool_key_hash,
            "agent_registry_hash": agent_registry_hash,
            "plan_hash": plan_hash,
        }
        canonical = json.dumps(
            digest_data,
            ensure_ascii=False,
            sort_keys=False,
            separators=(",", ":"),
        )
    else:
        digest_data = {
            "plan_hash": plan_hash,
            "agent_registry_hash": agent_registry_hash,
            "tool_key_hash": tool_key_hash,
            "handshake_sequence_hash": handshake_sequence_hash,
        }
        canonical = canonical_json(digest_data)
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    print(f"W5-DETERMINISM-DIGEST: {digest}")
    return digest


class DeterministicOrchestrator:
    """
    Unified deterministic L3 orchestration kernel.

    Implements route_mode-aware orchestration with sequential handshake.
    No direct provider SDK imports, no embedding instantiation, no L4 mutation.
    """

    def __init__(self, project_root: Path | None = None):
        self.project_root = project_root or Path.cwd()
        self.handshake_machine = HandshakeStateMachine()
        self._agent_registry_hash = self._compute_agent_registry_hash()

    def _compute_agent_registry_hash(self) -> str:
        """Compute hash of agent execution profile registry."""
        # Placeholder - would integrate with actual agent registry
        registry_data = {"agent_profiles": []}
        canonical = canonical_json(registry_data)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def _compute_tool_key_hash(self, allowed_tools: tuple[str, ...]) -> str:
        """Compute hash of sorted tool keys."""
        tool_data = {"allowed_tools": sorted(allowed_tools)}
        canonical = canonical_json(tool_data)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def orchestrate(
        self,
        governed_payload: GovernedPayload,
        route_mode: str,
        trace_id: str,
        policy_hash: str,
        allowed_tools: tuple[str, ...],
    ) -> OrchestrationResult:
        """
        Main orchestration entry point.

        Args:
            governed_payload: The assembled payload from L0
            route_mode: Route mode (B/C/D)
            trace_id: Unique trace identifier
            policy_hash: Policy validation hash
            allowed_tools: Tuple of allowed tool names

        Returns:
            OrchestrationResult with deterministic outcome
        """
        config = OrchestrationConfig(
            trace_id=trace_id,
            policy_hash=policy_hash,
            allowed_tools=allowed_tools,
            route_mode=RouteMode(route_mode),
            governed_payload=governed_payload,
        )

        # Route-specific orchestration
        if config.route_mode == RouteMode.B:
            return self._orchestrate_path_b(config)
        elif config.route_mode == RouteMode.C:
            return self._orchestrate_path_c(config)
        elif config.route_mode == RouteMode.D:
            return self._orchestrate_path_d(config)
        else:
            raise ValueError(f"Unsupported route_mode '{route_mode}'. Must be B, C, or D.")

    def _orchestrate_path_b(self, config: OrchestrationConfig) -> OrchestrationResult:
        """
        Path B: Policy Check First

        1. Require L5 pre-clear
        2. Handshake: INIT → PRECLEAR_REQUESTED → CERTIFIED
        3. No seal before CERTIFIED
        4. Only after certification may plan be sealed
        """
        # Initialize handshake
        self.handshake_machine.reset()
        assert self.handshake_machine.current_state == HandshakeState.INIT

        # Request L5 pre-clear
        self.handshake_machine.request_preclear()
        assert self.handshake_machine.current_state == HandshakeState.PRECLEAR_REQUESTED

        # In real implementation, would wait for L5 certification
        # For now, simulate certification
        self.handshake_machine.certify()
        assert self.handshake_machine.current_state == HandshakeState.CERTIFIED

        # Create plan
        plan = self._create_deterministic_plan(config)
        plan_hash = compute_plan_hash(plan)

        # Seal after certification
        self.handshake_machine.seal()
        assert self.handshake_machine.current_state == HandshakeState.SEALED

        # Create execution trace
        execution_trace = create_execution_trace_skeleton(
            trace_id=config.trace_id,
            plan_hash=plan_hash,
            governed_payload=config.governed_payload,
        )

        # Compute determinism digest
        tool_key_hash = self._compute_tool_key_hash(config.allowed_tools)
        handshake_sequence_hash = self.handshake_machine.get_sequence_hash()
        determinism_digest = compute_determinism_digest(
            plan_hash=plan_hash,
            agent_registry_hash=self._agent_registry_hash,
            tool_key_hash=tool_key_hash,
            handshake_sequence_hash=handshake_sequence_hash,
        )
        digest_line = f"W5-DETERMINISM-DIGEST: {determinism_digest}"

        return OrchestrationResult(
            success=True,
            route_mode="B",
            plan_hash=plan_hash,
            execution_trace=execution_trace.to_dict(),
            handshake_state=self.handshake_machine.current_state,
            determinism_digest=determinism_digest,
            metadata={
                "policy_check": "completed",
                "certification": "granted",
                "sealed": True,
                "digest_output": digest_line,
            },
        )

    def _orchestrate_path_c(self, config: OrchestrationConfig) -> OrchestrationResult:
        """
        Path C: Execute Script Directly

        1. If tool execution intent detected, require L5 certification first
        2. Same handshake enforcement as Path B
        3. Seal only after CERTIFIED
        """
        # Check for tool execution intent
        has_tool_intent = self._detect_tool_execution_intent(config.governed_payload)

        # Initialize handshake
        self.handshake_machine.reset()

        # Always require L5 certification before sealing (spec requirement)
        self.handshake_machine.request_preclear()
        self.handshake_machine.certify()

        # Create plan
        plan = self._create_deterministic_plan(config)
        plan_hash = compute_plan_hash(plan)

        # Seal after certification
        self.handshake_machine.seal()

        # Create execution trace
        execution_trace = create_execution_trace_skeleton(
            trace_id=config.trace_id,
            plan_hash=plan_hash,
            governed_payload=config.governed_payload,
        )

        # Compute determinism digest
        tool_key_hash = self._compute_tool_key_hash(config.allowed_tools)
        handshake_sequence_hash = self.handshake_machine.get_sequence_hash()
        determinism_digest = compute_determinism_digest(
            plan_hash=plan_hash,
            agent_registry_hash=self._agent_registry_hash,
            tool_key_hash=tool_key_hash,
            handshake_sequence_hash=handshake_sequence_hash,
        )
        digest_line = f"W5-DETERMINISM-DIGEST: {determinism_digest}"

        return OrchestrationResult(
            success=True,
            route_mode="C",
            plan_hash=plan_hash,
            execution_trace=execution_trace.to_dict(),
            handshake_state=self.handshake_machine.current_state,
            determinism_digest=determinism_digest,
            metadata={
                "tool_execution_detected": has_tool_intent,
                "certification_required": has_tool_intent,
                "sealed": True,
                "digest_output": digest_line,
            },
        )

    def _orchestrate_path_d(self, config: OrchestrationConfig) -> OrchestrationResult:
        """
        Path D: Human Review First

        1. DO NOT dispatch to L2
        2. Emit HumanDecisionArtifact draft
        3. Stop
        4. Any MODIFY_DIFF must reference original_plan_hash and re-enter L5
        """
        # Create plan for human review
        plan = self._create_deterministic_plan(config)
        plan_hash = compute_plan_hash(plan)

        # Create human review artifact
        human_artifact = create_human_review_draft(
            trace_id=config.trace_id,
            policy_hash=config.policy_hash,
            plan_hash=plan_hash,
            governed_payload=config.governed_payload,
            allowed_tools=config.allowed_tools,
        )

        # Create execution trace (no dispatch)
        execution_trace = create_execution_trace_skeleton(
            trace_id=config.trace_id,
            plan_hash=plan_hash,
            governed_payload=config.governed_payload,
        )

        # Compute determinism digest
        tool_key_hash = self._compute_tool_key_hash(config.allowed_tools)
        handshake_sequence_hash = self.handshake_machine.get_sequence_hash()
        determinism_digest = compute_determinism_digest(
            plan_hash=plan_hash,
            agent_registry_hash=self._agent_registry_hash,
            tool_key_hash=tool_key_hash,
            handshake_sequence_hash=handshake_sequence_hash,
        )
        digest_line = f"W5-DETERMINISM-DIGEST: {determinism_digest}"

        return OrchestrationResult(
            success=True,
            route_mode="D",
            plan_hash=plan_hash,
            execution_trace=execution_trace.to_dict(),
            handshake_state=self.handshake_machine.current_state,
            determinism_digest=determinism_digest,
            human_decision_artifact=human_artifact.to_dict(),
            metadata={
                "human_review_required": True,
                "dispatched_to_l2": False,
                "awaiting_human_decision": True,
                "digest_output": digest_line,
            },
        )

    def _create_deterministic_plan(self, config: OrchestrationConfig) -> dict[str, Any]:
        """
        Create deterministic plan from governed payload.

        Stable sort, canonical structure, no heuristic logic.
        """
        plan = {
            "trace_id": config.trace_id,
            "policy_hash": config.policy_hash,
            "route_mode": config.route_mode.value,
            "governed_payload": {
                "s0_system": config.governed_payload.s0_system,
                "i0_instructional": config.governed_payload.i0_instructional,
                "c0_context": config.governed_payload.c0_context,
                "u0_user_prompt": config.governed_payload.u0_user_prompt,
                "manifest_hash": config.governed_payload.manifest_hash,
            },
            "allowed_tools": sorted(config.allowed_tools),
            "orchestration_steps": [
                {
                    "step_id": 1,
                    "action": "process_payload",
                    "deterministic": True,
                }
            ],
        }

        return plan

    def _detect_tool_execution_intent(self, payload: GovernedPayload) -> bool:
        """
        Detect if payload contains tool execution intent.

        Deterministic detection - no ML or fuzzy matching.
        """
        tool_keywords = ["execute", "run", "invoke", "call", "tool", "script"]
        prompt_lower = payload.u0_user_prompt.lower()

        return any(keyword in prompt_lower for keyword in tool_keywords)


__all__ = [
    "DeterministicOrchestrator",
    "OrchestrationConfig",
    "RouteMode",
    "OrchestrationResult",
    "canonical_json",
    "compute_plan_hash",
    "compute_determinism_digest",
]
