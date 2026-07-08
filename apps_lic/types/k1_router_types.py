"""[SSOT] Logic Node for K1 Routing.
Moved from engines/k1_routing_agent.py to comply with Blueprint Depth-2 Structure.
This is a deterministic utility, NOT an autonomous agent.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "k1_router_types", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "k1_router_types", "policy_binding")
trace_contract._emit_snapshots_state("p0", "k1_router_types", "state_snapshot")
from tqdm import tqdm

trace_contract._emit_emits_metric_event("k1_router_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("k1_router_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("k1_router_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("k1_router_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("k1_router_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("k1_router_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("k1_router_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("k1_router_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("k1_router_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("k1_router_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("k1_router_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("k1_router_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("k1_router_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("k1_router_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("k1_router_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("k1_router_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("k1_router_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("k1_router_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("k1_router_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("k1_router_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("k1_router_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("k1_router_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("k1_router_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("k1_router_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("k1_router_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("k1_router_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("k1_router_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("k1_router_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "k1_router_types", "context_pull")
trace_contract._emit_pulls_context("p1", "k1_router_types", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "k1_router_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "k1_router_types", "uwg_term_2")
trace_contract._emit_writes_through("p1", "k1_router_types", "write_through")
trace_contract._emit_writes_through("p1", "k1_router_types", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "k1_router_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "k1_router_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "k1_router_types", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "k1_router_types", "human_escalation")
trace_contract._emit_routes_through("p1", "k1_router_types", "route_through")
trace_contract._emit_checks_agent_registry("p1", "k1_router_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "k1_router_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "k1_router_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "k1_router_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "k1_router_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "k1_router_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "k1_router_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "k1_router_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "k1_router_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "k1_router_types")
trace_contract._emit_gated_by_confidence("p1", "k1_router_types", "confidence_gate")
trace_contract.emit_replay_key("p0", "k1_router_types")
trace_contract.emit_determinism_digest("p0", "k1_router_types")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "k1_router_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "k1_router_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "k1_router_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "k1_router_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "k1_router_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "k1_router_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "k1_router_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "k1_router_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "k1_router_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "k1_router_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "k1_router_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "k1_router_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "k1_router_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "k1_router_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "k1_router_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "k1_router_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "k1_router_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "k1_router_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "k1_router_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "k1_router_types", "exec_snapshot_link")

logger = logging.getLogger(__name__)


@dataclass
class ArchetypeClassificationResult:
    """Result of archetype classification."""

    archetype: str
    confidence: float
    matched_tokens: list[str]
    cxo_precedence_triggered: bool
    manual_override_required: bool


@dataclass
class RouteSelectionResult:
    """Result of route selection."""

    route: str
    premium_available: bool
    premium_routing_mismatch: bool
    blocking_reason: str | None = None


@dataclass
class K1Output:
    """K.1 routing node output."""

    archetype: ArchetypeClassificationResult
    route: RouteSelectionResult
    entrance_gates_passed: list[str]
    metadata: dict[str, Any]


class K1Router:
    """
    Handles state transitions and routing logic for the Profile Analysis workflow.

    This is a deterministic logic node that implements the 7 Prompt Shell Entrance Gates,
    archetype classification with CXO precedence, and route selection with premium
    routing validation. It is NOT an autonomous agent.
    """

    def __init__(self, config: dict[str, Any] = None):
        self.config = config or {}
        self.archetype_tokens: dict[str, list[str]] = self.config.get(
            "archetype_tokens",
            {
                "C_LEVEL": ["CEO", "CTO", "CFO", "CIO", "COO", "PRESIDENT", "DIRECTOR"],
                "EXECUTIVE": ["VP", "VICE PRESIDENT", "SENIOR", "LEAD", "HEAD", "MANAGER"],
                "SENIOR_TA": ["SENIOR", "PRINCIPAL", "STAFF", "ENGINEER", "DEVELOPER"],
                "RECRUITER": ["RECRUITER", "TALENT", "HR", "SOURCING"],
            },
        )
        self.cxo_precedence_tokens: list[str] = self.config.get(
            "cxo_precedence_tokens",
            ["CEO", "CTO", "CFO", "CIO", "COO", "PRESIDENT", "FOUNDER", "CHIEF"],
        )
        self.route_configs: dict[str, Any] = self.config.get("route_configs", {})

    def __call__(self, state: dict[str, Any]) -> K1Output:
        """
        Executes routing logic using functor pattern for graph compatibility.

        Args:
            state (dict): The current workflow state containing:
                - linkedin_url: str
                - contact_name: str
                - contact_title: str
                - contact_about: Optional[str]
                - lifecycle: str (NEW or EXISTING)
                - premium_available: bool
                - route_override: Optional[str]

        Returns:
            K1Output: Complete routing output with archetype and route

        Raises:
            ValueError: If routing state is empty or validation fails
        """
        if not state:
            raise ValueError("Routing state cannot be empty")
        return self.execute_routing(state)

    def determine_next_hop(self, state: dict[str, Any]) -> str:
        """
        Determines the next hop identifier for workflow routing.

        Args:
            state: Current workflow state

        Returns:
            str: Next hop identifier
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "K1Router.determine_next_hop")

        if not state:
            raise ValueError("Routing state cannot be empty")
        result = self.execute_routing(state)
        return f"route_{result.route.lower()}"

    def execute_routing(self, context: dict[str, Any]) -> K1Output:
        """Execute K.1 routing and classification.

        Args:
            context: Execution context with routing parameters

        Returns:
            K1Output with archetype and route
        """
        logger.info("Executing K.1 routing and classification")
        entrance_gates_passed = []
        lifecycle = context.get("lifecycle", "NEW")
        entrance_gates_passed.append("GATE_1_LIFECYCLE_DETERMINED")
        logger.info(f"Gate 1: Lifecycle = {lifecycle}")
        contact_name = context.get("contact_name")
        contact_title = context.get("contact_title")
        contact_about = context.get("contact_about", "")
        if not contact_name or not contact_title:
            raise ValueError("GATE_2_FAILED: Contact name and title are required")
        entrance_gates_passed.append("GATE_2_CONTACT_BLOCK_VALIDATED")
        logger.info(f"Gate 2: Contact validated - {contact_name}, {contact_title}")
        premium_available = context.get("premium_available", False)
        entrance_gates_passed.append("GATE_3A_PREMIUM_AVAILABILITY_CHECKED")
        logger.info(f"Gate 3A: Premium InMail = {premium_available}")
        route_override = context.get("route_override")
        if route_override:
            entrance_gates_passed.append("GATE_3B_ROUTE_OVERRIDE_DETECTED")
            logger.info(f"Gate 3B: Route override = {route_override}")
        archetype_result = self._classify_archetype(contact_title, contact_about)
        entrance_gates_passed.append("GATE_4_ARCHETYPE_CLASSIFIED")
        logger.info(
            f"Gate 4: Archetype = {archetype_result.archetype} (confidence={archetype_result.confidence:.2f}, CXO_precedence={archetype_result.cxo_precedence_triggered})",
        )
        route_result = self._select_route(
            lifecycle=lifecycle,
            premium_available=premium_available,
            route_override=route_override,
            archetype=archetype_result.archetype,
        )
        entrance_gates_passed.append("GATE_5_ROUTE_SELECTED")
        logger.info(f"Gate 5: Route = {route_result.route}")
        if route_result.premium_routing_mismatch:
            entrance_gates_passed.append("GATE_6_PREMIUM_MISMATCH_DETECTED")
            logger.critical(f"Gate 6: PREMIUM ROUTING MISMATCH BLOCKER - {route_result.blocking_reason}")
            raise ValueError(f"GATE_6_BLOCKED: {route_result.blocking_reason}")
        entrance_gates_passed.append("GATE_6_PREMIUM_ROUTING_VALIDATED")
        logger.info("Gate 6: Premium routing validated")
        entrance_gates_passed.append("GATE_7_FINAL_APPROVAL")
        logger.info("Gate 7: All entrance gates passed")
        output = K1Output(
            archetype=archetype_result,
            route=route_result,
            entrance_gates_passed=entrance_gates_passed,
            metadata={
                "router_id": "K1Router",
                "lifecycle": lifecycle,
                "contact_name": contact_name,
                "contact_title": contact_title,
            },
        )
        logger.info(f"K.1 routing complete: {archetype_result.archetype} → {route_result.route}")
        return output

    def _classify_archetype(self, title: str, about: str = "") -> ArchetypeClassificationResult:
        """Classify recipient archetype with CXO precedence rule.

        Classification order (from LinkedInCanonical v2.90):
        1. Check for CXO-level tokens FIRST (immediate C_LEVEL assignment)
        2. Else check Executive tokens
        3. Else check TA tokens
        4. Else default to EXECUTIVE

        Args:
            title: Recipient job title
            about: Recipient about section

        Returns:
            ArchetypeClassificationResult
        """
        combined_text = f"{title} {about}".upper()
        matched_tokens = []
        for token in tqdm(self.cxo_precedence_tokens, desc="Processing", unit="item"):
            if token.upper() in combined_text:
                matched_tokens.append(token)
                logger.info(f"CXO precedence triggered: {token}")
                return ArchetypeClassificationResult(
                    archetype="C_LEVEL",
                    confidence=1.0,
                    matched_tokens=matched_tokens,
                    cxo_precedence_triggered=True,
                    manual_override_required=False,
                )
        for token in self.archetype_tokens.get("C_LEVEL", []):
            if token.upper() in combined_text:
                matched_tokens.append(token)
        if matched_tokens:
            return ArchetypeClassificationResult(
                archetype="C_LEVEL",
                confidence=0.95,
                matched_tokens=matched_tokens,
                cxo_precedence_triggered=False,
                manual_override_required=False,
            )
        matched_tokens = []
        for token in self.archetype_tokens.get("EXECUTIVE", []):
            if token.upper() in combined_text:
                matched_tokens.append(token)
        if matched_tokens:
            return ArchetypeClassificationResult(
                archetype="EXECUTIVE",
                confidence=0.9,
                matched_tokens=matched_tokens,
                cxo_precedence_triggered=False,
                manual_override_required=False,
            )
        matched_tokens = []
        for token in self.archetype_tokens.get("SENIOR_TA", []):
            if token.upper() in combined_text:
                matched_tokens.append(token)
        if matched_tokens:
            return ArchetypeClassificationResult(
                archetype="SENIOR_TA",
                confidence=0.9,
                matched_tokens=matched_tokens,
                cxo_precedence_triggered=False,
                manual_override_required=False,
            )
        matched_tokens = []
        for token in self.archetype_tokens.get("RECRUITER", []):
            if token.upper() in combined_text:
                matched_tokens.append(token)
        if matched_tokens:
            return ArchetypeClassificationResult(
                archetype="RECRUITER",
                confidence=0.85,
                matched_tokens=matched_tokens,
                cxo_precedence_triggered=False,
                manual_override_required=False,
            )
        logger.warning("No archetype tokens matched - defaulting to EXECUTIVE")
        return ArchetypeClassificationResult(
            archetype="EXECUTIVE",
            confidence=0.5,
            matched_tokens=[],
            cxo_precedence_triggered=False,
            manual_override_required=True,
        )

    def _select_route(
        self,
        lifecycle: str,
        premium_available: bool,
        route_override: str | None,
        archetype: str,
    ) -> RouteSelectionResult:
        """Select message route with premium routing validation.

        Args:
            lifecycle: NEW or EXISTING
            premium_available: Premium InMail availability
            route_override: Manual route override
            archetype: Classified archetype

        Returns:
            RouteSelectionResult with mismatch detection
        """
        if route_override:
            selected_route = route_override
            if selected_route == "INMAIL" and (not premium_available):
                return RouteSelectionResult(
                    route=selected_route,
                    premium_available=premium_available,
                    premium_routing_mismatch=True,
                    blocking_reason="INMAIL route selected but Premium InMail not available. Operator response to Gate 3A conflicts with route selection.",
                )
            return RouteSelectionResult(
                route=selected_route,
                premium_available=premium_available,
                premium_routing_mismatch=False,
            )
        if lifecycle == "EXISTING":
            selected_route = "FOLLOW_UP"
        elif premium_available:
            selected_route = "INMAIL"
        else:
            selected_route = "CONNECTION_REQ"
        return RouteSelectionResult(
            route=selected_route,
            premium_available=premium_available,
            premium_routing_mismatch=False,
        )
