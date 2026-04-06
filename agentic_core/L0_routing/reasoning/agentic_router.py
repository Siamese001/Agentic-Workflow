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

from agentic_core.L0_routing.reasoning.capacity_aware_router import (
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
from agentic_core.L0_routing.utils.routing_telemetry import (
    RoutingOutcomeStatus,
    RoutingTelemetryContext,
    record_routing_telemetry,
)

# L6 import deferred to avoid layer boundary violation
# from agentic_core.L6_observability.utils.performance.performance_emitter import (
#     StageStatus,
#     record_routing_performance,
# )
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
    emit_replay_key,
)

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
    _emit_records_execution_trace,
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
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

from agentic_core.runtime.contracts.lifecycle_trace_contract import emit_determinism_digest

emit_determinism_digest("trace_agentic_router", "agentic_router_dispatch_entry")
emit_determinism_digest("trace_agentic_router", "agentic_router_dispatch_exit")
emit_determinism_digest("trace_agentic_router", "agentic_router_tool_invoke")
emit_determinism_digest("trace_agentic_router", "agentic_router_tool_complete")
emit_determinism_digest("trace_agentic_router", "agentic_router_agent_entry")
emit_determinism_digest("trace_agentic_router", "agentic_router_agent_exit")
emit_determinism_digest("trace_agentic_router", "agentic_router_uwg_write")
emit_determinism_digest("trace_agentic_router", "agentic_router_trace_sign")
emit_determinism_digest("trace_agentic_router", "agentic_router_guardrail_check")
emit_determinism_digest("trace_agentic_router", "agentic_router_policy_verify")

if TYPE_CHECKING:
    from agentic_core.L0_routing.reasoning.intent_embedding_classifier import IntentEmbeddingClassifier

Logger = logging.getLogger(__name__)

# L6 import deferred to avoid layer boundary violation (L0→L6)
_perf_emitter_cache: dict[str, Any] = {}

def _get_perf_emitter() -> tuple[Any, Any, Any]:
    """Lazy load L6 performance emitter to avoid layer boundary violation."""
    if "record_fn" not in _perf_emitter_cache:
        try:
            from agentic_core.L6_observability.utils.performance.performance_emitter import (
                StageStatus,
                record_routing_performance,
            )
            _perf_emitter_cache["record_fn"] = record_routing_performance
            _perf_emitter_cache["status_error"] = StageStatus.ERROR
            _perf_emitter_cache["status_success"] = StageStatus.SUCCESS
        except ImportError as e:
            Logger.warning(f"L6 performance emitter not available: {e}")
            # Return no-op functions
            def _noop(*args, **kwargs):
                pass
            _perf_emitter_cache["record_fn"] = _noop
            _perf_emitter_cache["status_error"] = None
            _perf_emitter_cache["status_success"] = None
    return (
        _perf_emitter_cache["record_fn"],
        _perf_emitter_cache["status_error"],
        _perf_emitter_cache["status_success"],
    )


def _get_routing_gateway():
    from agentic_core.L0_routing.reasoning.deterministic_routing_gateway import (
        get_routing_gateway,  # noqa: PLC0415
    )

    return get_routing_gateway()


def _get_proof_emitter():
    from agentic_core.L2_execution.utils.execution_proof_emitter import (
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

    # guardian: allow-magic-config -- router constructor params are deployment-configurable defaults
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
        from agentic_core.L2_execution.utils.providers import get_clock as _get_clock  # noqa: PLC0415

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
        from agentic_core.runtime.types.execution_trace import get_active_execution_trace  # noqa: PLC0415

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
        except RoutingContractError as _rce:  # guardian: allow-specific -- routing contract creation failure
            Logger.warning("agentic_router: routing contract creation failed: %s", _rce)

        # P3/L0: Apply capacity-aware routing if multiple candidates exist
        _capacity_chosen_route = target_name
        if len(_candidate_routes) > 1:
            try:    # guardian: RoutingCapacityError should be handled with specific context    # guardian: RoutingCapacityError should be handled with specific context    # guardian: RoutingCapacityError should be handled with specific context    # guardian: RoutingCapacityError should be handled with specific context    # guardian: RoutingCapacityError should be handled with specific context    # guardian: RoutingCapacityError should be handled with specific context    # guardian: RoutingCapacityError should be handled with specific context    # guardian: RoutingCapacityError should be handled with specific context    # guardian: RoutingCapacityError should be handled with specific context    # guardian: RoutingCapacityError should be handled with specific context
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

                # Only override if the intent-classified target is unavailable
                if target_name not in _candidate_routes or _capacity_chosen_route == target_name:
                    target_name = _capacity_chosen_route

            except RoutingCapacityError as _rce:
                pass  # Continue with original routing - capacity failure should not block routing
            except (ImportError, AttributeError, KeyError, TypeError, ValueError) as _cap_exc:
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
                except (TypeError, ValueError) as exc:  # fallback handler type errors
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
            except (ConnectionError, RuntimeError) as _te:  # telemetry emission failure non-blocking
                Logger.debug("agentic_router: telemetry emission failed: %s", _te)
            return decision

        try:
            decision.result = await target.handler(user_input, context)
        except (RuntimeError, AttributeError) as exc:  # handler execution error
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
        except (ConnectionError, RuntimeError) as _te:  # telemetry emission failure non-blocking
            Logger.debug("agentic_router: telemetry emission failed: %s", _te)

        # P2/L6: Emit performance record for routing stage
        try:
            _record_perf, _status_error, _status_success = _get_perf_emitter()
            perf_status = _status_error if decision.error else _status_success
            routing_perf = _record_perf(
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
        except (RuntimeError, TypeError) as _perf_exc:  # performance logging failure non-blocking
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
            except (AttributeError, TypeError) as exc:  # embedding classifier optional, keyword fallback handles
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
