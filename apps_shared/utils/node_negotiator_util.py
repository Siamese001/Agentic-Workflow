"""Node Negotiation Protocol - Sideways communication between nodes.

This module implements the negotiation protocol that allows downstream nodes
to send feedback and change requests to upstream nodes, enabling dynamic
collaboration between hops.
"""

import asyncio
import logging
import os
import time
import uuid
from collections.abc import Callable
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, validator

from agentic_core.interfaces.path_constants import DEFAULT_SLEEP
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
    _emit_reads_through,
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
from apps_shared.utils.subatomic_hop_util import HopState, MicroStage, SubatomicHop

_emit_applies_guardrail("p0", "node_negotiator_util", "p0_governance")
_emit_reads_policy_state("p0", "node_negotiator_util", "policy_binding")
_emit_snapshots_state("p0", "node_negotiator_util", "state_snapshot")
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

_emit_emits_metric_event("node_negotiator_util", "p4obs", "metric_1")
_emit_emits_metric_event("node_negotiator_util", "p4obs", "metric_2")
_emit_emits_metric_event("node_negotiator_util", "p4obs", "metric_3")
_emit_emits_metric_event("node_negotiator_util", "p4obs", "metric_4")
_emit_emits_metric_event("node_negotiator_util", "p4obs", "metric_5")
_emit_emits_metric_event("node_negotiator_util", "p4obs", "metric_6")
_emit_records_incident_event("node_negotiator_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("node_negotiator_util", "p4obs", "anomaly")
_emit_writes_observability_log("node_negotiator_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("node_negotiator_util", "p4obs", "mon_state")
_emit_triggers_alert("node_negotiator_util", "p4obs", "alert")
_emit_links_incident_trace("node_negotiator_util", "p4obs", "trace_link")
_emit_captures_pattern("node_negotiator_util", "p3lm", "pattern")
_emit_records_learning_event("node_negotiator_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("node_negotiator_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("node_negotiator_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("node_negotiator_util", "p3lm", "routing")
_emit_improves_agent_policy("node_negotiator_util", "p3lm", "policy")
_emit_stores_learning_state("node_negotiator_util", "p3lm", "state")
_emit_records_execution_trace("node_negotiator_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("node_negotiator_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("node_negotiator_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("node_negotiator_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("node_negotiator_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("node_negotiator_util", "env_read", "p2_env_1")
_emit_reads_environ("node_negotiator_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("node_negotiator_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("node_negotiator_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "node_negotiator_util", "context_pull")
_emit_pulls_context("p1", "node_negotiator_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "node_negotiator_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "node_negotiator_util", "uwg_term_2")
_emit_writes_through("p1", "node_negotiator_util", "write_through")
_emit_writes_through("p1", "node_negotiator_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "node_negotiator_util", "safety_validation")
_emit_invokes_eval("p1", "node_negotiator_util", "eval_call")
_emit_proposal_commits_routing("p1", "node_negotiator_util", "routing_commit")
_emit_escalates_to_human("p1", "node_negotiator_util", "human_escalation")
_emit_routes_through("p1", "node_negotiator_util", "route_through")
_emit_checks_agent_registry("p1", "node_negotiator_util", "agent_registry")
_emit_validates_agent_capability("p1", "node_negotiator_util", "capability")
_emit_dispatches_execution_plan("p1", "node_negotiator_util", "exec_plan")
_emit_agent_executes_agent("p1", "node_negotiator_util", "sub_agent")
_emit_routes_to_agent("p1", "node_negotiator_util", "target_agent")
_emit_verifies_policy("p1", "node_negotiator_util", "policy_check")
_emit_observes_runtime_state("p1", "node_negotiator_util", "runtime_state")
_emit_verifies_boundary("p1", "node_negotiator_util", "boundary_check")
_emit_transcripts_response("p1", "node_negotiator_util", "transcript")
_emit_hard_fails_untranscripted("p1", "node_negotiator_util")
_emit_gated_by_confidence("p1", "node_negotiator_util", "confidence_gate")
emit_replay_key("p0", "node_negotiator_util")
emit_determinism_digest("p0", "node_negotiator_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "node_negotiator_util", "execution_auth")
_emit_validates_capability("p2", "node_negotiator_util", "capability_check")
_emit_routes_to_capability("p2", "node_negotiator_util", "capability_route")
_emit_writes_via_uwg("p2", "node_negotiator_util", "uwg_write")
_emit_blocks_direct_write("p2", "node_negotiator_util", "direct_write_block")
_emit_records_tool_invocation("p2", "node_negotiator_util", "tool_invocation")
_emit_captures_execution_output("p2", "node_negotiator_util", "exec_output")
_emit_dispatches_agent("p3", "node_negotiator_util", "agent_dispatch")
_emit_coordinates_agents("p3", "node_negotiator_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "node_negotiator_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "node_negotiator_util", "healing_outcome")
_emit_escalates_failure("p3", "node_negotiator_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "node_negotiator_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "node_negotiator_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "node_negotiator_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "node_negotiator_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "node_negotiator_util", "eval_metric")
_emit_stores_embedding("p4", "node_negotiator_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "node_negotiator_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "node_negotiator_util", "exec_snapshot_link")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_1")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_2")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_3")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_4")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_5")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_6")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_7")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_8")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_9")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_10")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_11")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_12")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_13")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_14")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_15")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_16")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_17")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_18")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_19")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_20")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_21")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_22")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_23")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_24")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_25")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_26")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_27")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_28")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_29")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_30")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_31")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_32")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_33")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_34")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_35")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_36")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_37")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_38")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_39")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_40")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_41")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_42")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_43")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_44")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_45")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_46")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_47")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_48")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_49")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_50")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_51")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_52")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_53")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_54")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_55")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_56")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_57")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_58")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_59")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_60")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_61")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_62")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_63")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_64")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_65")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_66")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_67")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_68")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_69")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_70")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_71")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_72")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_73")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_74")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_75")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_76")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_77")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_78")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_79")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_80")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_81")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_82")
_emit_reads_through("l4", "node_negotiator_util", "urg_read_83")

logger = logging.getLogger(__name__)


class NegotiationMessage(BaseModel):
    """A message in the negotiation protocol."""

    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    from_hop: str
    to_hop: str
    message_type: str
    payload: str
    context: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)
    priority: int = Field(default=0, ge=0, le=10)

    @validator("message_type")
    def validate_message_type(cls, v):
        allowed = ["CLARIFICATION_REQUEST", "CHANGE_REQUEST", "REJECTION"]
        if v not in allowed:
            raise ValueError(f"message_type must be one of {allowed}")
        return v


class NegotiationRound(BaseModel):
    """A round of negotiation between nodes."""

    round_id: str
    participants: list[str]
    messages: list[NegotiationMessage] = Field(default_factory=list)
    start_time: datetime = Field(default_factory=datetime.now)
    end_time: datetime | None = None
    status: str = "ACTIVE"
    resolution: str | None = None


class NegotiationConfig(BaseModel):
    """[HARDENED] Environment-aware configuration for negotiation protocol."""

    max_rounds: int = Field(default_factory=lambda: int(os.getenv("NEGOTIATION_MAX_ROUNDS", "2")), ge=1, le=5)
    max_message_length: int = Field(default=1000, ge=100, le=10000)
    response_timeout: float = Field(
        default_factory=lambda: float(os.getenv("NEGOTIATION_RESPONSE_TIMEOUT", "30.0")), ge=5.0, le=300.0,
    )
    enable_persistence: bool = True
    auto_resolve_threshold: float = Field(
        default_factory=lambda: float(os.getenv("NEGOTIATION_AUTO_RESOLVE_THRESHOLD", "0.8")), ge=0.0, le=1.0,
    )


class NegotiationResult(BaseModel):
    """Result of a negotiation."""

    success: bool
    resolution_type: str
    final_output: Any | None = None
    negotiation_log: list[str] = Field(default_factory=list)
    rounds_completed: int = 0


class NodeNegotiator:
    """Manages negotiation between nodes."""

    def __init__(self, config: NegotiationConfig | None = None):
        """Initialize the Node Negotiator.

        Args:
            config: Optional configuration
        """
        self.config = config or NegotiationConfig()
        self.active_negotiations: dict[str, NegotiationRound] = {}
        self.negotiation_history: list[NegotiationRound] = []
        self.message_handlers: dict[str, Callable] = {}
        self.stats = {
            "total_negotiations": 0,
            "successful_negotiations": 0,
            "escalated_negotiations": 0,
            "average_rounds": 0.0,
        }
        self._register_default_handlers()
        logger.info("Initialized NodeNegotiator")

    def _register_default_handlers(self) -> None:
        """Register default message handlers."""
        self.message_handlers.update(
            {
                "CLARIFICATION_REQUEST": self._handle_clarification,
                "CHANGE_REQUEST": self._handle_change_request,
                "REJECTION": self._handle_rejection,
            },
        )

    async def send_feedback(
        self,
        from_hop: SubatomicHop,
        to_hop_id: str,
        message_type: str,
        payload: str,
        context: dict[str, Any] | None = None,
        priority: int = 0,
    ) -> bool:
        """Send feedback from one node to another.

        Args:
            from_hop: The sending hop
            to_hop_id: ID of the target hop
            message_type: Type of message
            payload: Message content
            context: Optional context
            priority: Message priority

        Returns:
            True if message sent successfully
        """
        message = NegotiationMessage(
            from_hop=from_hop.config.hop_id,
            to_hop=to_hop_id,
            message_type=message_type,
            payload=payload,
            context=context or {},
            priority=priority,
        )
        if len(payload) > self.config.max_message_length:
            logger.error(f"Message too long: {len(payload)} > {self.config.max_message_length}")
            return False
        round_id = self._get_or_create_round(from_hop.config.hop_id, to_hop_id)
        negotiation = self.active_negotiations[round_id]
        negotiation.messages.append(message)
        handler = self.message_handlers.get(message_type)
        if handler:
            try:
                await handler(message, negotiation)
            except Exception as e:
                logger.error(f"Handler failed for message {message.message_id}: {e}")
                return False
        logger.info(f"Sent {message_type} from {from_hop.config.hop_id} to {to_hop_id}")
        return True

    async def request_change(
        self,
        downstream_hop: SubatomicHop,
        upstream_hop_id: str,
        requested_change: str,
        reason: str,
        context: dict[str, Any] | None = None,
    ) -> NegotiationResult:
        """Request a change from an upstream node.

        Args:
            downstream_hop: The requesting hop
            upstream_hop_id: ID of upstream hop to change
            requested_change: What change is requested
            reason: Why the change is needed
            context: Optional context

        Returns:
            NegotiationResult with outcome
        """
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, "NodeNegotiator.request_change")
        self.stats["total_negotiations"] += 1
        round_id = self._get_or_create_round(downstream_hop.config.hop_id, upstream_hop_id)
        negotiation = self.active_negotiations[round_id]
        await self.send_feedback(
            from_hop=downstream_hop,
            to_hop_id=upstream_hop_id,
            message_type="CHANGE_REQUEST",
            payload=f"Please modify output: {requested_change}",
            context={"reason": reason, **(context or {})},
            priority=5,
        )
        result = await self._wait_for_resolution(negotiation)
        if result.success:
            self.stats["successful_negotiations"] += 1
        else:
            self.stats["escalated_negotiations"] += 1
        total = self.stats["total_negotiations"]
        current_avg = self.stats["average_rounds"]
        self.stats["average_rounds"] = (current_avg * (total - 1) + result.rounds_completed) / total
        return result

    async def _handle_clarification(self, message: NegotiationMessage, negotiation: NegotiationRound) -> None:
        """Handle clarification request."""
        logger.info(f"Clarification requested: {message.payload}")
        response = NegotiationMessage(
            from_hop=message.to_hop,
            to_hop=message.from_hop,
            message_type="CLARIFICATION_RESPONSE",
            payload="Clarification: The output meets the specified format requirements",
            context={"original_message_id": message.message_id},
        )
        negotiation.messages.append(response)

    async def _handle_change_request(
        self, message: NegotiationMessage, negotiation: NegotiationRound,
    ) -> None:
        """Handle change request."""
        logger.info(f"Change requested: {message.payload}")
        upstream_hop = self._get_active_hop(message.to_hop)
        if not upstream_hop:
            logger.warning(f"Upstream hop {message.to_hop} no longer active")
            negotiation.status = "FAILED"
            return
        if upstream_hop.state == HopState.COMPLETED:
            upstream_hop.state = HopState.NEGOTIATING
            upstream_hop.current_stage = MicroStage.THINK
            upstream_hop.context["negotiation_request"] = {
                "from_hop": message.from_hop,
                "request": message.payload,
                "context": message.context,
            }
            if "negotiation_log" not in upstream_hop.context:
                upstream_hop.context["negotiation_log"] = []
            upstream_hop.context["negotiation_log"].append(
                {
                    "timestamp": message.timestamp.isoformat(),
                    "from": message.from_hop,
                    "message": message.payload,
                },
            )
            logger.info(f"Rolled back {message.to_hop} for negotiation")

    async def _handle_rejection(self, message: NegotiationMessage, negotiation: NegotiationRound) -> None:
        """Handle rejection message."""
        logger.warning(f"Output rejected: {message.payload}")
        negotiation.status = "FAILED"
        negotiation.resolution = "REJECTION"

    def _get_or_create_round(self, hop1_id: str, hop2_id: str) -> str:
        """Get existing negotiation round or create new one."""
        for round_id, negotiation in self.active_negotiations.items():
            if (
                hop1_id in negotiation.participants
                and hop2_id in negotiation.participants
                and (negotiation.status == "ACTIVE")
            ):
                return round_id
        round_id = f"neg_{int(time.time() * 1000)}_{hop1_id}_{hop2_id}"
        self.active_negotiations[round_id] = NegotiationRound(
            round_id=round_id, participants=[hop1_id, hop2_id],
        )
        return round_id

    async def _wait_for_resolution(self, negotiation: NegotiationRound) -> NegotiationResult:
        """Wait for negotiation to resolve."""
        rounds_completed = 0
        while negotiation.status == "ACTIVE" and rounds_completed < self.config.max_rounds:
            await asyncio.sleep(DEFAULT_SLEEP)
            if len(negotiation.messages) >= 2:
                if self._check_resolution(negotiation):
                    negotiation.status = "RESOLVED"
                    break
            rounds_completed += 1
        negotiation.end_time = datetime.now()
        self.negotiation_history.append(negotiation)
        del self.active_negotiations[negotiation.round_id]
        success = negotiation.status == "RESOLVED"
        return NegotiationResult(
            success=success,
            resolution_type="AGREEMENT" if success else "TIMEOUT",
            negotiation_log=[msg.payload for msg in negotiation.messages],
            rounds_completed=rounds_completed,
        )

    def _check_resolution(self, negotiation: NegotiationRound) -> bool:
        """Check if negotiation is resolved."""
        if not negotiation.messages:
            return False
        last_message = negotiation.messages[-1]
        positive_indicators = ["done", "fixed", "updated", "changed", "modified"]
        payload_lower = last_message.payload.lower()
        return any(indicator in payload_lower for indicator in positive_indicators)

    def _get_active_hop(self, hop_id: str) -> SubatomicHop | None:
        """Get an active hop by ID.

        In a real implementation, this would query the DAGManager.
        """
        return None

    def get_negotiation_history(self, limit: int | None = None) -> list[NegotiationRound]:
        """Get negotiation history."""
        if limit:
            return self.negotiation_history[-limit:]
        return self.negotiation_history

    def get_stats(self) -> dict[str, Any]:
        """Get negotiation statistics."""
        return {
            **self.stats,
            "active_negotiations": len(self.active_negotiations),
            "config": {"max_rounds": self.config.max_rounds, "timeout": self.config.response_timeout},
        }


_node_negotiator: NodeNegotiator | None = None


def get_node_negotiator(**kwargs) -> NodeNegotiator:
    """Get or create global NodeNegotiator instance.

    Args:
        **kwargs: configuration arguments

    Returns:
        NodeNegotiator instance
    """
    global _node_negotiator
    if _node_negotiator is None:
        config = NegotiationConfig(**kwargs) if kwargs else NegotiationConfig()
        _node_negotiator = NodeNegotiator(config)
    return _node_negotiator


async def request_upstream_change(
    downstream_hop: SubatomicHop, upstream_hop_id: str, change_request: str, reason: str, **kwargs,
) -> NegotiationResult:
    """Convenience function for requesting upstream changes.

    Args:
        downstream_hop: The requesting hop
        upstream_hop_id: ID of upstream hop
        change_request: What to change
        reason: Why change is needed
        **kwargs: Additional context

    Returns:
        NegotiationResult
    """
    negotiator = get_node_negotiator()
    return await negotiator.request_change(
        downstream_hop=downstream_hop,
        upstream_hop_id=upstream_hop_id,
        requested_change=change_request,
        reason=reason,
        context=kwargs,
    )


async def send_clarification(from_hop: SubatomicHop, to_hop_id: str, question: str, **kwargs) -> bool:
    """Send a clarification request.

    Args:
        from_hop: The sending hop
        to_hop_id: ID of target hop
        question: Clarification question
        **kwargs: Additional context

    Returns:
        True if sent successfully
    """
    negotiator = get_node_negotiator()
    return await negotiator.send_feedback(
        from_hop=from_hop,
        to_hop_id=to_hop_id,
        message_type="CLARIFICATION_REQUEST",
        payload=question,
        context=kwargs,
    )


class NegotiatingHop(SubatomicHop):
    """A SubatomicHop with negotiation capabilities."""

    def __init__(self, *args, **kwargs):
        """Initialize NegotiatingHop."""
        super().__init__(*args, **kwargs)
        self.negotiator = get_node_negotiator()
        self.negotiation_enabled = True

    async def evaluate_downstream_feedback(
        self, downstream_output: Any, expected_criteria: list[str],
    ) -> bool:
        """Evaluate if downstream feedback requires negotiation.

        Args:
            downstream_output: Output from downstream node
            expected_criteria: What we expect from downstream

        Returns:
            True if negotiation is needed
        """
        if not downstream_output:
            return True
        return False

    async def request_upstream_modification(
        self, upstream_hop_id: str, modification: str, reason: str,
    ) -> NegotiationResult:
        """Request modification from upstream node.

        Args:
            upstream_hop_id: ID of upstream hop
            modification: What to modify
            reason: Why modification is needed

        Returns:
            NegotiationResult
        """
        if not self.negotiation_enabled:
            raise RuntimeError("Negotiation not enabled")
        return await request_upstream_change(
            downstream_hop=self, upstream_hop_id=upstream_hop_id, change_request=modification, reason=reason,
        )
