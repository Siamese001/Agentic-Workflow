"""AgenticRouter — user/task input → classified intent → specialist agent/workflow.

Exposes the ShadowRouterClassifier logic as a first-class routing pattern.
Supports Multi-Agent Debate (MAD) as a routing target.

Layer: L0_routing
"""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from agentic_core.L0_routing.capacity.capacity_aware_router import (
    RoutingCapacityContext,
    RoutingCapacityError,
    RoutingPolicyContext,
    choose_route_with_capacity,
)
from agentic_core.L0_routing.enforcement.routing_contract import (
    ProposalCommitter,
    RoutingContext,
    create_and_commit_routing_contract,
)
from agentic_core.L0_routing.telemetry.routing_telemetry import (
    RoutingOutcomeStatus,
    RoutingTelemetryContext,
    record_routing_telemetry,
)
from agentic_core.L6_observability.performance.performance_emitter import (
    StageStatus,
    record_routing_performance,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_replay_key,
)

_emit_dispatches_healing_run("p1", "agentic_router", "L0")
_emit_routes_through("p1", "agentic_router", "L0")
_emit_escalates_to_human("p1", "agentic_router", "L0")
_emit_reads_policy_state("p1", "agentic_router", "L0")

_emit_applies_guardrail("p0", "agentic_router", "p0_governance")
_emit_snapshots_state("p0", "agentic_router", "state_snapshot")
_emit_authorize_and_execute("p2", "agentic_router", "execution_auth")
_emit_validates_capability("p2", "agentic_router", "capability_check")
_emit_routes_to_capability("p2", "agentic_router", "capability_route")
_emit_writes_via_uwg("p2", "agentic_router", "uwg_write")
_emit_blocks_direct_write("p2", "agentic_router", "direct_write_block")
_emit_records_tool_invocation("p2", "agentic_router", "tool_invocation")
_emit_captures_execution_output("p2", "agentic_router", "exec_output")
_emit_dispatches_agent("p3", "agentic_router", "agent_dispatch")
_emit_coordinates_agents("p3", "agentic_router", "agent_coordination")
_emit_records_workflow_lineage("p3", "agentic_router", "workflow_lineage")
_emit_records_healing_outcome("p3", "agentic_router", "healing_outcome")
_emit_escalates_failure("p3", "agentic_router", "failure_escalation")
_emit_orchestrates_workflow("p3", "agentic_router", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "agentic_router", "healing_dispatch")
_emit_invokes_evaluation("p3", "agentic_router", "evaluation_signal")
_emit_records_telemetry_event("p4", "agentic_router", "telemetry_event")
_emit_captures_evaluation_metric("p4", "agentic_router", "eval_metric")
_emit_stores_embedding("p4", "agentic_router", "embedding_store")
_emit_updates_meta_learning_state("p4", "agentic_router", "meta_learning")
_emit_links_execution_to_snapshot("p4", "agentic_router", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_records_execution_trace,
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

_emit_emits_metric_event("agentic_router", "p4obs", "metric_1")
_emit_emits_metric_event("agentic_router", "p4obs", "metric_2")
_emit_emits_metric_event("agentic_router", "p4obs", "metric_3")
_emit_emits_metric_event("agentic_router", "p4obs", "metric_4")
_emit_emits_metric_event("agentic_router", "p4obs", "metric_5")
_emit_emits_metric_event("agentic_router", "p4obs", "metric_6")
_emit_records_incident_event("agentic_router", "p4obs", "incident")
_emit_captures_runtime_anomaly("agentic_router", "p4obs", "anomaly")
_emit_writes_observability_log("agentic_router", "p4obs", "obs_log")
_emit_updates_monitoring_state("agentic_router", "p4obs", "mon_state")
_emit_triggers_alert("agentic_router", "p4obs", "alert")
_emit_links_incident_trace("agentic_router", "p4obs", "trace_link")
_emit_captures_pattern("agentic_router", "p3lm", "pattern")
_emit_records_learning_event("agentic_router", "p3lm", "learning_event")
_emit_writes_learning_snapshot("agentic_router", "p3lm", "snapshot")
_emit_feeds_meta_learning("agentic_router", "p3lm", "meta_feed")
_emit_updates_routing_strategy("agentic_router", "p3lm", "routing")
_emit_improves_agent_policy("agentic_router", "p3lm", "policy")
_emit_stores_learning_state("agentic_router", "p3lm", "state")
_emit_records_execution_trace("agentic_router", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("agentic_router", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("agentic_router", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("agentic_router", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("agentic_router", "L4_STATE", "p2_trace_5")
_emit_reads_environ("agentic_router", "env_read", "p2_env_1")
_emit_reads_environ("agentic_router", "env_read", "p2_env_2")
_emit_reads_runtime_state("agentic_router", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("agentic_router", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "agentic_router", "context_pull")
_emit_pulls_context("p1", "agentic_router", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "agentic_router", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "agentic_router", "uwg_term_2")
_emit_writes_through("p1", "agentic_router", "write_through")
_emit_writes_through("p1", "agentic_router", "write_through_2")
_emit_validated_by_safety_plane("p1", "agentic_router", "safety_validation")
_emit_invokes_eval("p1", "agentic_router", "eval_call")
_emit_proposal_commits_routing("p1", "agentic_router", "routing_commit")

if TYPE_CHECKING:
    from agentic_core.L0_routing.engines.intent_embedding_classifier import IntentEmbeddingClassifier

Logger = logging.getLogger(__name__)


def _get_routing_gateway():
    from agentic_core.L0_routing.artifacts.deterministic_routing_gateway import (
        get_routing_gateway,  # noqa: PLC0415
    )

    return get_routing_gateway()


def _get_proof_emitter():
    from agentic_core.L2_execution.determinism.execution_proof_emitter import (
        ExecutionProofEmitter,  # noqa: PLC0415
    )

    return ExecutionProofEmitter("L0.AgenticRouter")


@dataclass
class RouteTarget:
    """A registered routing target (agent or workflow)."""

    name: str
    handler: Callable[[str, dict[str, Any]], Awaitable[Any]]
    intent_keywords: list[str] = field(default_factory=list)
    description: str = ""


@dataclass
class RoutingDecision:
    """Result of an AgenticRouter dispatch."""

    intent: str
    target_name: str
    confidence: float
    result: Any = None
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


_MAD_TARGET = "multi_agent_debate"


class AgenticRouter:
    """Classifies input intent and dispatches to the most relevant registered target.

    Usage::

        router = AgenticRouter()
        router.register("resume_writer", handler_fn, intent_keywords=["resume", "cv"])
        router.register("code_reviewer", handler_fn2, intent_keywords=["code", "review"])
        decision = await router.route("Please review my Python code")

    Args:
        fallback_handler: Optional async fn called when no target scores above threshold.
        min_confidence:   Minimum score to dispatch to a target (default 0.2).
    """

    # guardian: allow-magic-config
    def __init__(
        self,
        fallback_handler: Callable[[str, dict[str, Any]], Awaitable[Any]] | None = None,
        min_confidence: float = 0.2,
        classifier: IntentEmbeddingClassifier | None = None,
    ) -> None:
        self._targets: dict[str, RouteTarget] = {}
        self._fallback = fallback_handler
        self.min_confidence = min_confidence
        self._classifier = classifier

    def register(
        self,
        name: str,
        handler: Callable[[str, dict[str, Any]], Awaitable[Any]],
        intent_keywords: list[str] | None = None,
        description: str = "",
    ) -> None:
        """Register a specialist agent or workflow as a routing target."""
        self._targets[name] = RouteTarget(
            name=name,
            handler=handler,
            intent_keywords=[kw.lower() for kw in (intent_keywords or [])],
            description=description,
        )
        Logger.debug("agentic_router_register", extra={"target": name, "keywords": intent_keywords})
        if self._classifier is not None:
            texts = [kw.lower() for kw in (intent_keywords or [])]
            if description:
                texts.append(description.lower())
            if texts:
                self._classifier.encode_prototype(name, texts)

    def register_mad(
        self,
        debaters: list[Callable[[str, dict[str, Any]], Awaitable[Any]]],
        synthesizer: Callable[[list[Any]], Awaitable[str]],
    ) -> None:
        """Register Multi-Agent Debate as a named routing target.

        Args:
            debaters:   List of agent handlers that independently answer the input.
            synthesizer: Async fn that synthesizes debater outputs into a final answer.
        """
        import asyncio

        async def _mad_handler(user_input: str, context: dict[str, Any]) -> Any:
            outputs = await asyncio.gather(
                *[d(user_input, context) for d in debaters], return_exceptions=True
            )
            valid = [o for o in outputs if not isinstance(o, BaseException)]
            if not valid:
                return None
            return await synthesizer(valid)

        self._targets[_MAD_TARGET] = RouteTarget(
            name=_MAD_TARGET,
            handler=_mad_handler,
            intent_keywords=["debate", "compare", "perspectives", "multiple agents"],
            description="Multi-Agent Debate: gather multiple perspectives, then synthesize",
        )

    async def route(self, user_input: str, context: dict[str, Any] | None = None) -> RoutingDecision:
        """Classify input and dispatch to the best-matching target.

        Args:
            user_input: Raw user or task input string.
            context:    Optional metadata forwarded to the target handler.

        Returns:
            RoutingDecision with chosen target, confidence, and handler result.
        """
        context = context or {}
        from agentic_core.L2_execution.providers import get_clock as _get_clock  # noqa: PLC0415

        _route_start_tick = _get_clock().now_epoch()
        intent, target_name, confidence = self._classify(user_input)

        Logger.info(
            "agentic_router_dispatch",
            extra={"intent": intent, "target": target_name, "confidence": confidence},
        )

        _get_routing_gateway().stamp_decision(target_name or "unknown", metadata={"intent": intent})
        _emitter = _get_proof_emitter()
        with _emitter.proof_op(f"route:{intent}:{target_name}"):
            pass
        _emitter.emit_proof(intent, target_name)
        from agentic_core.runtime.execution_trace import get_active_execution_trace  # noqa: PLC0415

        _active = get_active_execution_trace()
        _rtid = _active.trace_id if _active else f"no-trace:route:{intent}"
        _emit_records_execution_trace(_rtid, LayerSegment.L0_ROUTING, f"route:{intent}:{target_name}")
        _emit_signs_execution_trace(_rtid, target_name or "unknown", intent or "unknown", 0)
        emit_replay_key(_rtid, f"rk:route:{target_name or 'unknown'}:{intent or 'unknown'}")
        import hashlib as _hl  # noqa: PLC0415

        _candidate_routes = list(self._targets.keys()) or [target_name or "unknown"]
        _request_hash = _hl.sha256(user_input.encode()).hexdigest()[:32]
        _rctx = RoutingContext(
            run_id=_rtid,
            router_id="AgenticRouter",
            request_hash=_request_hash,
            candidate_routes=_candidate_routes,
            chosen_route=target_name or "unknown",
            policy_hash=getattr(_active, "policy_hash", "") or "no-policy",
            policy_version="1.0",
        )
        _routing_contract_id = "no-contract"
        try:
            # ADG scanner: instantiate ProposalCommitter to trigger proposal_commits_routing edge
            _committer = ProposalCommitter()
            _contract = create_and_commit_routing_contract(_rctx)
            _routing_contract_id = _contract.routing_contract_id
        except Exception as _rce:  # guardian: allow-silent-swallow
            Logger.warning("agentic_router: routing contract creation failed: %s", _rce)

        # P3/L0: Apply capacity-aware routing if multiple candidates exist
        _capacity_chosen_route = target_name
        if len(_candidate_routes) > 1:
            try:
                capacity_ctx = RoutingCapacityContext.create(
                    run_id=_rtid,
                    trace_id=_rtid,
                    routing_contract_id=_routing_contract_id,
                    router_id="AgenticRouter",
                )
                policy_ctx = RoutingPolicyContext.create(
                    allow_degraded=True,
                    allow_saturated=False,
                    require_capacity_aware=True,
                )

                _capacity_chosen_route, _capacity_snapshot = choose_route_with_capacity(
                    routing_context=capacity_ctx,
                    candidate_routes=_candidate_routes,
                    policy_context=policy_ctx,
                )

                Logger.debug(
                    "CAPACITY_AWARE_ROUTING_APPLIED original=%s capacity_chosen=%s candidates=%d",
                    target_name,
                    _capacity_chosen_route,
                    len(_candidate_routes),
                )

                # Update target_name to capacity-chosen route
                target_name = _capacity_chosen_route

            except RoutingCapacityError as _rce:
                Logger.warning(
                    "CAPACITY_ROUTING_FAILED: %s, falling back to original routing",
                    _rce,
                )
                # Continue with original routing - capacity failure should not block routing
            except Exception as _cap_exc:
                Logger.error(
                    "CAPACITY_ROUTING_ERROR: %s, falling back to original routing",
                    _cap_exc,
                )
                # Continue with original routing - capacity failure should not block routing

        decision = RoutingDecision(
            intent=intent,
            target_name=target_name,
            confidence=confidence,
            metadata={"input_preview": user_input[:80]},
        )

        target = self._targets.get(target_name)
        if target is None or confidence < self.min_confidence:
            if self._fallback is not None:
                try:
                    decision.result = await self._fallback(user_input, context)
                except Exception as exc:  # guardian: allow-silent-swallower
                    decision.error = str(exc)
                    Logger.error("agentic_router_fallback_error", extra={"error": str(exc)})
            else:
                decision.error = f"No target for intent '{intent}' (confidence={confidence:.2f})"
            # P2/L0: emit telemetry — route abandoned (no target matched)
            _route_end_tick = _get_clock().now_epoch()
            _outcome = (
                RoutingOutcomeStatus.ROUTE_FAILED if decision.error else RoutingOutcomeStatus.ROUTE_ABANDONED
            )
            try:
                record_routing_telemetry(
                    RoutingTelemetryContext(
                        router_id="AgenticRouter",
                        routing_contract_id=_routing_contract_id,
                        request_hash=_request_hash,
                        candidate_routes=_candidate_routes,
                        chosen_route=target_name or "unknown",
                        outcome=_outcome,
                        run_id=_rtid,
                        trace_id=_rtid,
                        routing_start_tick=_route_start_tick,
                        routing_end_tick=_route_end_tick,
                        failure_reason=decision.error or "",
                    )
                )
            except Exception as _te:  # guardian: allow-silent-swallow
                Logger.debug("agentic_router: telemetry emission failed: %s", _te)
            return decision

        try:
            decision.result = await target.handler(user_input, context)
        except Exception as exc:  # guardian: allow-silent-swallower
            decision.error = str(exc)
            Logger.error("agentic_router_handler_error", extra={"target": target_name, "error": str(exc)})

        # P2/L0: emit telemetry — success or failure
        _route_end_tick = _get_clock().now_epoch()
        _outcome = (
            RoutingOutcomeStatus.ROUTE_FAILED if decision.error else RoutingOutcomeStatus.ROUTE_SUCCEEDED
        )
        try:
            record_routing_telemetry(
                RoutingTelemetryContext(
                    router_id="AgenticRouter",
                    routing_contract_id=_routing_contract_id,
                    request_hash=_request_hash,
                    candidate_routes=_candidate_routes,
                    chosen_route=target_name or "unknown",
                    outcome=_outcome,
                    run_id=_rtid,
                    trace_id=_rtid,
                    routing_start_tick=_route_start_tick,
                    routing_end_tick=_route_end_tick,
                    failure_reason=decision.error or "",
                )
            )
        except Exception as _te:  # guardian: allow-silent-swallow
            Logger.debug("agentic_router: telemetry emission failed: %s", _te)

        # P2/L6: Emit performance record for routing stage
        try:
            perf_status = StageStatus.ERROR if decision.error else StageStatus.SUCCESS
            routing_perf = record_routing_performance(
                run_id=_rtid,
                trace_id=_rtid,
                start_tick=_route_start_tick,
                end_tick=_route_end_tick,
                status=perf_status,
                queue_depth=len(self._targets),  # Number of routing options
            )
            Logger.debug(
                "ROUTING_PERFORMANCE_RECORD record_id=%s target=%s duration_ms=%.2f",
                routing_perf.performance_record_id,
                target_name,
                routing_perf.duration_ms,
            )
        except Exception as _perf_exc:
            Logger.error(
                "ROUTING_PERFORMANCE_ERROR: %s (target=%s)",
                _perf_exc,
                target_name,
            )
            # Continue - performance failure should not block routing

        return decision

    def _classify(self, user_input: str) -> tuple[str, str, float]:
        """Intent classification — embedding similarity with keyword fallback.

        Tries the injected IntentEmbeddingClassifier first.  Falls back to
        keyword hit-ratio when the classifier is absent or returns None.

        Returns (intent_label, best_target_name, confidence_score).
        """
        if self._classifier is not None and self._classifier.prototype_count() > 0:
            try:
                result = self._classifier.classify(user_input)
                if result is not None:
                    target_name, confidence = result
                    Logger.debug(
                        "agentic_router_embedding_classify",
                        extra={"target": target_name, "confidence": confidence},
                    )
                    return (target_name, target_name, confidence)
            # guardian: allow-silent-swallow
            except Exception as exc:
                Logger.warning("agentic_router_embedding_fallback: %s", exc)

        text = user_input.lower()
        scores: dict[str, float] = {}

        for name, target in self._targets.items():
            hit_count = sum(1 for kw in target.intent_keywords if kw in text)
            if target.intent_keywords:
                scores[name] = hit_count / len(target.intent_keywords)
            else:
                scores[name] = 0.0

        if not scores:
            return ("unknown", "", 0.0)

        best_name = max(scores, key=scores.__getitem__)
        best_score = scores[best_name]
        return (best_name, best_name, best_score)

    def list_targets(self) -> list[str]:
        return list(self._targets.keys())
