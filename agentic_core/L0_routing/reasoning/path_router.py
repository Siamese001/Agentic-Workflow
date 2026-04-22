"""
L0 Path Router - Deterministic Path Selection (GAP-02)

Implements strict Path A/B/C/D dispatch semantics with deterministic logic.
No business logic, no wall-clock usage, pure path selection.
"""

import hashlib
import json
import logging
from enum import Enum
from typing import TypedDict

from agentic_core.L0_routing.enforcement.routing_contract import (
    ProposalCommitter,
    RoutingContext,
    RoutingContractError,
    create_and_commit_routing_contract,
)
from agentic_core.L0_routing.utils.routing_telemetry import (
    RoutingOutcomeStatus,
    RoutingTelemetryContext,
    record_routing_telemetry,
)
from agentic_core.runtime.contracts.abstain_contract import (
    DECISION_ABSTAIN,
    DEFAULT_ABSTAIN_THRESHOLD,
    plan_abstain,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_snapshots_state,
    emit_determinism_digest,
    emit_replay_key,
)

from .assembly_stage import GovernedPayload

_log = logging.getLogger(__name__)


def _resolve_trace_id() -> str:
    from agentic_core.runtime.types.execution_trace import get_active_execution_trace  # noqa: PLC0415

    active = get_active_execution_trace()
    if active and getattr(active, "trace_id", None):
        return active.trace_id
    return "no-trace:path-router"


def _stable_payload_hash(payload: GovernedPayload) -> str:
    serialized = json.dumps(
        {
            "input_text": getattr(payload, "input_text", None),
            "check_ids": list(getattr(payload, "check_ids", ()) or ()),
            "sanitized": bool(getattr(payload, "sanitized", False)),
            "d0_injections": getattr(payload, "d0_injections", None),
        },
        sort_keys=True,
        default=str,
        separators=(",", ":"),
    )
    return hashlib.sha256(serialized.encode()).hexdigest()[:32]


def _get_routing_gateway():
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_get_routing_gateway", "state_snapshot")
    _emit_applies_guardrail(str(_uuid.uuid4()), "_get_routing_gateway", "p0_governance")
    from agentic_core.L0_routing.reasoning.deterministic_routing_gateway import (
        get_routing_gateway,  # noqa: PLC0415
    )

    return get_routing_gateway()


def _get_proof_emitter():
    from agentic_core.L2_execution.utils.execution_proof_emitter import (  # guardian: allow-layer-violation -- L0 module uses L2 type/utility; intentional cross-layer dependency in enforcement/routing layer
        ExecutionProofEmitter,  # noqa: PLC0415
    )

    return ExecutionProofEmitter("L0.PathRouter")


class Path(Enum):
    """Deterministic path enumeration for L0 routing."""

    A = "A"
    B = "B"
    C = "C"
    D = "D"


R5_ROUTE: str = "R5"
"""Stable route label for the D4.1 fallback / abstain outcome (WC-G08 / F17).

This is intentionally a module-level string constant rather than a ``Path``
enum value so the existing ``Path.A/B/C/D`` enum is byte-unchanged. The D3
abstain primitive pairs ``decision="abstain"`` with ``action="emit_r5_candidate"``;
when the router acts on that action the resulting :class:`RoutingResult`
carries ``route=R5_ROUTE``.
"""


R1A_ROUTE: str = "R1A"
"""Stable route label for the v9 D1 exact-cache hit (audit-1f9180 W1b).

Emitted by :meth:`PathRouter.route_with_gates` when
:func:`agentic_core.L0_routing.reasoning.route_gates.check_route_gates`
returns a D1 hit. Terminal arm — caller returns the cached payload
immediately without invoking ``select_path`` or any L2 step.
"""

R1B_ROUTE: str = "R1B"
"""Stable route label for the v9 D2 semantic-cache hit (audit-1f9180 W1b).

Emitted by :meth:`PathRouter.route_with_gates` when
:func:`agentic_core.L0_routing.reasoning.route_gates.check_route_gates`
returns a D2 hit. Terminal arm — caller returns the cached payload
immediately without invoking ``select_path`` or any L2 step.
"""


class RoutingResult(TypedDict):
    """Serializable result emitted by :meth:`PathRouter.route_with_confidence`.

    Stable public contract consumed by Wave D5 (LOW_NORMATIVE_COVERAGE
    consumer). Every field is a primitive so the dict round-trips through
    ``json.dumps`` / ``json.loads`` without transformation.

    Fields:
        route: ``"A"``, ``"B"``, ``"C"``, ``"D"``, or ``"R5"``.
        reason: Human-readable justification (echoed from the D3 abstain
            decision's ``reason`` field for both R5 and proceed branches).
        confidence: Input confidence value in [0.0, 1.0], echoed from the D3
            decision.
        threshold: Floor used for the comparison, echoed from the D3 decision.
        action: ``"emit_r5_candidate"`` when ``route == "R5"``;
            ``"continue"`` otherwise. Downstream dispatch hint.
    """

    route: str
    reason: str
    confidence: float
    threshold: float
    action: str


class PathRouter:
    """
    Deterministic path router for governed payloads.

    Implements strict Path A/B/C/D dispatch semantics with zero business logic.
    """

    def select_path(self, payload: GovernedPayload) -> Path:
        """
        Select routing path based on payload characteristics.

        Deterministic logic:
        - If payload.check_ids empty → Path.A
        - If payload.sanitized is True → Path.B
        - If len(payload.check_ids) == 1 → Path.C
        - Else → Path.D

        Args:
            payload: GovernedPayload to route

        Returns:
            Selected Path enum value
        """
        _trace_id = _resolve_trace_id()
        _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "PathRouter.select_path")
        emit_replay_key(_trace_id, f"rk:path:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:path:{_trace_id[:16]}")

        from agentic_core.L2_execution.utils.providers import get_clock as _get_clock  # noqa: PLC0415  # guardian: allow-layer-violation -- L0 module uses L2 type/utility; intentional cross-layer dependency in enforcement/routing layer

        _path_start_tick = _get_clock().now_epoch()
        if not payload.check_ids:
            chosen = Path.A
        elif payload.sanitized:
            chosen = Path.B
        elif len(payload.check_ids) == 1:
            chosen = Path.C
        else:
            chosen = Path.D
        _get_routing_gateway().stamp_decision(chosen.value)
        _emitter = _get_proof_emitter()
        with _emitter.proof_op(f"select_path:{chosen.value}"):
            pass
        from agentic_core.runtime.types.execution_trace import get_active_execution_trace  # noqa: PLC0415

        _active = get_active_execution_trace()
        _rtid = _active.trace_id if _active else f"{_trace_id}:{chosen.value}"
        _payload_hash = _stable_payload_hash(payload)
        _candidate_routes = [p.value for p in Path]
        _rctx = RoutingContext(
            run_id=_rtid,
            router_id="PathRouter",
            request_hash=_payload_hash,
            candidate_routes=_candidate_routes,
            chosen_route=chosen.value,
            policy_hash=getattr(_active, "policy_hash", "") or "no-policy",
            policy_version="1.0",
        )
        _routing_contract_id = "no-contract"
        try:
            _committer = ProposalCommitter()
            _contract = create_and_commit_routing_contract(_rctx)
            _routing_contract_id = _contract.routing_contract_id
        except (ValueError, TypeError, RuntimeError) as _rce:
            raise RoutingContractError(
                f"PathRouter refused to emit raw route without contract: chosen={chosen.value} error={_rce}",
            ) from _rce
        # P2/L0: emit routing telemetry
        _path_end_tick = _get_clock().now_epoch()
        try:
            record_routing_telemetry(
                RoutingTelemetryContext(
                    router_id="PathRouter",
                    routing_contract_id=_routing_contract_id,
                    request_hash=_payload_hash,
                    candidate_routes=_candidate_routes,
                    chosen_route=chosen.value,
                    outcome=RoutingOutcomeStatus.ROUTE_SUCCEEDED,
                    run_id=_rtid,
                    trace_id=_rtid,
                    routing_start_tick=_path_start_tick,
                    routing_end_tick=_path_end_tick,
                ),
            )
        except (
            ValueError,
            TypeError,
            RuntimeError,
        ) as _te:  # guardian: allow-log-and-swallow -- telemetry emission: non-fatal, routing result returned regardless
            _log.warning("path_router: telemetry emission failed: %s", _te)
        return chosen

    def route_with_confidence(
        self,
        payload: GovernedPayload,
        confidence: float,
        threshold: float = DEFAULT_ABSTAIN_THRESHOLD,
    ) -> RoutingResult:
        """Confidence-aware dispatch that consumes the D3 abstain primitive.

        Wave D4.1 (WC-G08 / F17). Delegates the abstain / proceed decision
        to :func:`plan_abstain` so the router NEVER re-implements confidence
        gating inline. Behavior:

        * If the D3 decision is ``"abstain"``: emit an R5 :class:`RoutingResult`
          with ``route="R5"``. ``select_path`` is NOT called. No routing
          contract is committed. The caller (D5 consumer) decides whether
          to refine, retry, or surface the abstain to the user.
        * Otherwise: delegate to :meth:`select_path` for A/B/C/D selection.
          ``select_path``'s existing contract commit, telemetry emission,
          and ``RoutingContractError`` semantics are UNCHANGED. The selected
          Path is wrapped in a :class:`RoutingResult` for uniform downstream
          consumption.

        Args:
            payload: Governed payload to route (only consulted on the proceed
                branch).
            confidence: Confidence / coverage score in ``[0.0, 1.0]``. Values
                strictly below ``threshold`` trigger the R5 branch.
            threshold: Abstain floor in ``[0.0, 1.0]``. Defaults to
                :data:`DEFAULT_ABSTAIN_THRESHOLD`.

        Returns:
            A :class:`RoutingResult` with ``route`` in
            ``{"A", "B", "C", "D", "R5"}``.

        Raises:
            ValueError: Propagated from :func:`plan_abstain` if ``confidence``
                or ``threshold`` is outside ``[0.0, 1.0]``.
            RoutingContractError: Propagated from :meth:`select_path` on
                contract failure. The R5 branch never raises this.
        """
        decision = plan_abstain(confidence, threshold)
        if decision["decision"] == DECISION_ABSTAIN:
            _log.info(
                "path_router: R5 abstain route fired; confidence=%.4f threshold=%.4f",
                confidence,
                threshold,
            )
            return RoutingResult(
                route=R5_ROUTE,
                reason=decision["reason"],
                confidence=decision["confidence"],
                threshold=decision["threshold"],
                action=decision["action"],
            )
        chosen = self.select_path(payload)
        return RoutingResult(
            route=chosen.value,
            reason=decision["reason"],
            confidence=decision["confidence"],
            threshold=decision["threshold"],
            action=decision["action"],
        )

    def route_with_gates(
        self,
        payload: GovernedPayload,
        request: dict,
        namespace: str,
        confidence: float,
        threshold: float = DEFAULT_ABSTAIN_THRESHOLD,
        *,
        tenant_id: str = "",
        replay_mode: bool = False,
        flow_class: str | None = None,
    ) -> tuple[RoutingResult, dict | None]:
        """v9 D1/D2 gate-aware dispatch (audit-1f9180 W1b).

        Consults :func:`agentic_core.L0_routing.reasoning.route_gates.check_route_gates`
        BEFORE falling through to the existing :meth:`route_with_confidence`
        selector. Semantics:

        * On **D1 exact hit**: returns ``(RoutingResult{route="R1A", ...}, cached_payload)``.
          Caller short-circuits the pipeline, returns ``cached_payload`` to its caller.
          ``select_path`` is NOT invoked. No routing contract is committed here.
        * On **D2 semantic hit**: returns ``(RoutingResult{route="R1B", ...}, cached_payload)``.
          Same short-circuit semantics as D1.
        * On **both miss**: delegates to :meth:`route_with_confidence` and
          returns ``(result, None)``. The ``None`` in position [1] signals
          "no cache hit, proceed with the returned RoutingResult".

        Both gates are env-gated and default to disabled; when both are off
        this method is behaviorally identical to ``route_with_confidence``
        (via the second-tuple-element None).

        This method is purely additive — the existing
        :meth:`route_with_confidence` and :meth:`select_path` methods are
        unchanged, and all 5 existing callers of ``route_with_confidence``
        continue to work without modification.

        Args:
            payload: Governed payload to route if both gates miss.
            request: Canonical request dict consulted by the gates for
                exact-hash and semantic-similarity matching. Must be
                JSON-serializable. Typically mirrors ``payload`` plus
                orchestration context (trace_id, tenant_id, etc.).
            namespace: Logical cache namespace for the D2 gate.
            confidence: Confidence / coverage score for the D3 abstain
                primitive on the gate-miss fall-through.
            threshold: Abstain floor, forwarded to
                :meth:`route_with_confidence`.
            tenant_id: Tenant scope for D2 key derivation.
            replay_mode: Forces both gates to miss when True (replay parity).
            flow_class: Forces D2 miss when in
                :data:`~agentic_core.L4_state.utils.memory.semantic_cache_manager.SemanticCacheManager.MUST_BYPASS_FLOWS`.

        Returns:
            Tuple of ``(RoutingResult, cached_payload_or_None)``. When
            element [1] is not ``None``, the caller MUST return that payload
            to its own caller without further routing work.
        """
        # Replay mode: force gate miss so replayed traces bypass cache state
        # entirely. Matches SemanticCacheManager.recall's replay_mode semantics.
        if not replay_mode:
            from agentic_core.L0_routing.reasoning.route_gates import (  # noqa: PLC0415
                check_route_gates as _check_route_gates,
            )

            gate_result = _check_route_gates(
                request,
                namespace=namespace,
                tenant_id=tenant_id,
                replay_mode=replay_mode,
                flow_class=flow_class,
                confidence=confidence,
            )
            if gate_result is not None:
                contract, cached_payload = gate_result
                route_label = contract["selected_route"].value  # R1A or R1B
                _log.info(
                    "path_router: gate hit route=%s namespace=%s",
                    route_label,
                    namespace,
                )
                return (
                    RoutingResult(
                        route=route_label,
                        reason=contract["reason_codes"][0] if contract["reason_codes"] else "gate_hit",
                        confidence=contract["confidence"],
                        threshold=threshold,
                        action="emit_cached_response",
                    ),
                    cached_payload,
                )
        # Gate miss (or replay) — delegate to existing confidence-aware selector.
        result = self.route_with_confidence(payload, confidence, threshold)
        return result, None
