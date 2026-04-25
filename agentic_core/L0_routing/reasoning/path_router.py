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
from agentic_core.runtime.contracts.routing_features import RoutingFeatureVector
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


class RoutingFeatureDispatch(TypedDict):
    """W5.P4 return shape from :meth:`PathRouter.route_with_features`.

    Fields:
        result: The :class:`RoutingResult` for the selected route.
        gate_fired: Which stage of the feature-vector dispatch emitted
            the result. One of ``"r5_multi_signal"`` / ``"r3_gate"`` /
            ``"fallback"``.
        r5_primary_reason: If ``gate_fired == "r5_multi_signal"``, the
            primary reason code (see
            :data:`~agentic_core.runtime.contracts.abstain_contract.R5_REASON_CODES`);
            else ``"none"``.
        r5_triggered_reasons: All R5 reason codes that fired (empty on
            non-R5 paths).
        r3_reason_code: If ``gate_fired == "r3_gate"``, the reason code
            returned by :func:`check_r3_grounding_gate`; else ``""``.
    """

    result: "RoutingResult"
    gate_fired: str
    r5_primary_reason: str
    r5_triggered_reasons: tuple[str, ...]
    r3_reason_code: str


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

    def route_with_features(
        self,
        payload: GovernedPayload,
        features: "RoutingFeatureVector",
        *,
        confidence: float | None = None,
        threshold: float = DEFAULT_ABSTAIN_THRESHOLD,
        namespace: str = "",
        coverage_score: float | None = None,
        circuit_breaker_open: bool = False,
        budget_exceeded: bool = False,
        clarification_needed: bool = False,
        toxicity_flagged: bool = False,
    ) -> "RoutingFeatureDispatch":
        """Feature-vector aware dispatch (W5.P4).

        Consults the W3 gates in this order, returning as soon as one fires:

        1. **Multi-signal R5** — :func:`plan_abstain_multi_signal` fed from
           ``features`` + the scalar signal kwargs. Fires when any of the
           6 enabled triggers is true per YAML config.
        2. **R3 grounded-read gate** — :func:`check_r3_grounding_gate`
           consumes ``features.grounding_need_score`` and optional
           ``coverage_score``. Returns R3 with the gate's reason code.
        3. **Fallback** — delegates to :meth:`route_with_confidence` with
           the caller's scalar ``confidence`` (or ``features`` budget-
           derived proxy) and abstain threshold. Preserves all existing
           ``Path.A/B/C/D`` / R5 behavior when no feature-driven gate fires.

        Args:
            payload: Governed payload — consulted only if the fallback
                ``select_path`` is reached.
            features: Populated :class:`RoutingFeatureVector`. Must be
                present; use :func:`build_routing_feature_vector`
                (W5.P2) to construct it.
            confidence: Optional scalar confidence for the R5 low-confidence
                trigger. Defaults to ``1.0`` when ``features`` does not
                carry one, preserving existing "no abstain" semantics.
            threshold: Abstain floor, forwarded to
                :meth:`route_with_confidence` on fallback.
            namespace: Cache / agent namespace for per-namespace gate
                thresholds (W2.P1 YAML).
            coverage_score: Optional C0 aggregate coverage (W1b), enabling
                the R3 "coverage below floor" short-circuit.
            circuit_breaker_open: External signal — fires R5 unconditionally.
            budget_exceeded: External signal (TokenCap DENY) — fires R5.
            clarification_needed: External signal (L1 CLARIFY) — fires R5.
            toxicity_flagged: External signal (L5 guardrail) — fires R5.

        Returns:
            :class:`RoutingFeatureDispatch` carrying the :class:`RoutingResult`
            plus the gate that fired (``"r5_multi_signal"`` / ``"r3_gate"``
            / ``"fallback"``) and, for observability, the R3 gate's reason
            code when applicable.
        """
        from agentic_core.L0_routing.reasoning.route_gates import (  # noqa: PLC0415
            check_r3_grounding_gate,
        )
        from agentic_core.runtime.contracts.abstain_contract import (  # noqa: PLC0415
            R5Signals,
            plan_abstain_multi_signal,
        )

        effective_confidence = float(confidence) if confidence is not None else 1.0

        # --- Step 1: multi-signal R5 ------------------------------------
        r5_signals: R5Signals = {
            "confidence": effective_confidence,
            "confidence_threshold": threshold,
        }
        if features.has_ood_signal():
            r5_signals["ood_score"] = features.ood_score
        if circuit_breaker_open:
            r5_signals["circuit_breaker_open"] = True
        if budget_exceeded:
            r5_signals["budget_exceeded"] = True
        if clarification_needed:
            r5_signals["clarification_needed"] = True
        if toxicity_flagged:
            r5_signals["toxicity_flagged"] = True

        r5_decision = plan_abstain_multi_signal(r5_signals)
        if r5_decision["decision"] == DECISION_ABSTAIN:
            _log.info(
                "path_router: R5 multi-signal fired primary=%s",
                r5_decision["primary_reason"],
            )
            # W5.P5: emit R5-fired metric labeled by primary reason code.
            try:
                from agentic_core.L6_observability.routing_calibration_metrics import (  # noqa: PLC0415  guardian: allow-layer-violation -- W5.P5 R5-fired metric emission; observability call-back from L0 routing hot path, wrapped in try/except so routing never hard-depends on L6
                    record_r5_fired,
                )

                record_r5_fired(
                    r5_decision["primary_reason"],
                    namespace=namespace or "default",
                )
            except ImportError:  # guardian: allow-silent-swallow -- observability import optional; routing must not depend on it (pass-through)
                pass
            return RoutingFeatureDispatch(
                result=RoutingResult(
                    route=R5_ROUTE,
                    reason=r5_decision["reason"],
                    confidence=r5_decision["confidence"],
                    threshold=r5_decision["threshold"],
                    action=r5_decision["action"],
                ),
                gate_fired="r5_multi_signal",
                r5_primary_reason=r5_decision["primary_reason"],
                r5_triggered_reasons=r5_decision["triggered_reasons"],
                r3_reason_code="",
            )

        # --- Step 2: R3 grounded-read gate ------------------------------
        if features.has_grounding_signal():
            should_ground, r3_reason = check_r3_grounding_gate(
                features.grounding_need_score,
                namespace=namespace,
                coverage_score=coverage_score,
            )
            if should_ground:
                _log.info(
                    "path_router: R3 grounded-read selected reason=%s",
                    r3_reason,
                )
                return RoutingFeatureDispatch(
                    result=RoutingResult(
                        route="R3",
                        reason=r3_reason,
                        confidence=effective_confidence,
                        threshold=threshold,
                        action="continue",
                    ),
                    gate_fired="r3_gate",
                    r5_primary_reason="none",
                    r5_triggered_reasons=(),
                    r3_reason_code=r3_reason,
                )

        # --- Step 3: fallback to existing confidence-aware selector -----
        fallback = self.route_with_confidence(
            payload,
            effective_confidence,
            threshold,
        )
        return RoutingFeatureDispatch(
            result=fallback,
            gate_fired="fallback",
            r5_primary_reason="none",
            r5_triggered_reasons=(),
            r3_reason_code="",
        )
