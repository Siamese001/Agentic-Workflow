"""03.5 L0 RouteTelemetryEvent.

Realizes 03.5 PHASE 3 ``RouteTelemetryEvent`` and the OTEL span shape (``l0.route_decision``).

The OTEL span itself is emitted by the surrounding integration layer (not in the
doctrine module). Here we provide the deterministic event payload shape with
``event_hash`` derived from canonical JSON.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field

from . import DoctrineContractError

_MAX_STR = 512
_MAX_LIST = 64
_MAX_REASON = 32


def _need_str(value: object, name: str, *, allow_empty: bool = False) -> None:
    if not isinstance(value, str):
        raise DoctrineContractError(f"{name} must be str, got {type(value).__name__}")
    if len(value) > _MAX_STR:
        raise DoctrineContractError(f"{name} exceeds {_MAX_STR} chars")
    if not allow_empty and not value:
        raise DoctrineContractError(f"{name} must be non-empty")


def _need_str_tuple(values: object, name: str, *, max_len: int = _MAX_LIST) -> None:
    if not isinstance(values, tuple):
        raise DoctrineContractError(f"{name} must be tuple")
    if len(values) > max_len:
        raise DoctrineContractError(f"{name} exceeds {max_len}")
    for idx, item in enumerate(values):
        if not isinstance(item, str) or not item or len(item) > _MAX_STR:
            raise DoctrineContractError(f"{name}[{idx}] must be non-empty str <= {_MAX_STR}")


def _need_bool(value: object, name: str) -> None:
    if not isinstance(value, bool):
        raise DoctrineContractError(f"{name} must be bool")


def _need_finite_float_in_unit(value: object, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise DoctrineContractError(f"{name} must be float in [0,1]")
    if value != value:
        raise DoctrineContractError(f"{name} must not be NaN")
    if value < 0.0 or value > 1.0:
        raise DoctrineContractError(f"{name} must be in [0,1], got {value}")


@dataclass(frozen=True)
class RouteTelemetryEvent:
    """03.5 PHASE 3 RouteTelemetryEvent.

    Fields are exactly those listed under 03.5 §RouteTelemetryEvent.
    The ``timestamp_or_run_clock_offset`` SHOULD be a normalized run-clock offset
    (in milliseconds since trace_root start), not wall-clock — wall-clock is
    excluded from the deterministic digest per 03.5 §PHASE 2.
    """

    event_id: str
    request_id: str
    run_id: str
    trace_root: str
    route_span_id: str
    l1_plan_id: str
    route_contract_id: str
    selected_route_id: str
    execution_form: str
    confidence: float
    reason_codes: tuple[str, ...]
    rejected_routes: tuple[str, ...]
    fallback_chain: tuple[str, ...]
    policy_hash: str
    blueprint_hash: str
    replay_key: str
    downstream_requirements: tuple[str, ...]
    ptc_allowed_downstream: bool
    timestamp_or_run_clock_offset: int
    event_hash: str = ""

    def __post_init__(self) -> None:
        for name in (
            "event_id",
            "request_id",
            "run_id",
            "trace_root",
            "route_span_id",
            "l1_plan_id",
            "route_contract_id",
            "selected_route_id",
            "execution_form",
            "policy_hash",
            "blueprint_hash",
            "replay_key",
        ):
            _need_str(getattr(self, name), f"RouteTelemetryEvent.{name}")
        _need_str(self.event_hash, "RouteTelemetryEvent.event_hash", allow_empty=True)
        _need_finite_float_in_unit(self.confidence, "RouteTelemetryEvent.confidence")
        _need_str_tuple(self.reason_codes, "RouteTelemetryEvent.reason_codes", max_len=_MAX_REASON)
        _need_str_tuple(self.rejected_routes, "RouteTelemetryEvent.rejected_routes")
        _need_str_tuple(self.fallback_chain, "RouteTelemetryEvent.fallback_chain")
        _need_str_tuple(
            self.downstream_requirements,
            "RouteTelemetryEvent.downstream_requirements",
        )
        _need_bool(self.ptc_allowed_downstream, "RouteTelemetryEvent.ptc_allowed_downstream")
        if isinstance(self.timestamp_or_run_clock_offset, bool) or not isinstance(
            self.timestamp_or_run_clock_offset, int
        ):
            raise DoctrineContractError(
                "RouteTelemetryEvent.timestamp_or_run_clock_offset must be int",
            )
        if self.timestamp_or_run_clock_offset < 0:
            raise DoctrineContractError(
                "RouteTelemetryEvent.timestamp_or_run_clock_offset must be >= 0",
            )
        # Closed-vocabulary check on selected_route_id and execution_form.
        if self.selected_route_id not in (
            "R1A_EXACT_CACHE",
            "R1B_SEMANTIC_CACHE",
            "R3_SIMPLE_GROUNDED_READ",
            "R4_SINGLE_ACTION",
            "R3R4_MANAGED_WORKFLOW",
            "R5_FALLBACK",
        ):
            raise DoctrineContractError(
                f"RouteTelemetryEvent.selected_route_id={self.selected_route_id!r} not in v15 vocabulary",
            )
        if self.execution_form not in (
            "TERMINAL_SHORTCIRCUIT",
            "SINGLE_STEP",
            "MANAGED_WORKFLOW",
        ):
            raise DoctrineContractError(
                f"RouteTelemetryEvent.execution_form={self.execution_form!r} not in v15 vocabulary",
            )

    def canonical_payload(self) -> dict[str, object]:
        """Return JSON-friendly dict EXCLUDING event_hash (used to compute it)."""
        payload = asdict(self)
        payload.pop("event_hash", None)
        # timestamp_or_run_clock_offset stays — it is run-clock, not wall-clock.
        return payload

    def with_hash(self) -> "RouteTelemetryEvent":
        """Return a copy with ``event_hash`` populated deterministically."""
        encoded = json.dumps(
            self.canonical_payload(),
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        digest = hashlib.sha256(encoded).hexdigest()
        return RouteTelemetryEvent(
            event_id=self.event_id,
            request_id=self.request_id,
            run_id=self.run_id,
            trace_root=self.trace_root,
            route_span_id=self.route_span_id,
            l1_plan_id=self.l1_plan_id,
            route_contract_id=self.route_contract_id,
            selected_route_id=self.selected_route_id,
            execution_form=self.execution_form,
            confidence=self.confidence,
            reason_codes=self.reason_codes,
            rejected_routes=self.rejected_routes,
            fallback_chain=self.fallback_chain,
            policy_hash=self.policy_hash,
            blueprint_hash=self.blueprint_hash,
            replay_key=self.replay_key,
            downstream_requirements=self.downstream_requirements,
            ptc_allowed_downstream=self.ptc_allowed_downstream,
            timestamp_or_run_clock_offset=self.timestamp_or_run_clock_offset,
            event_hash=f"evt:{digest}",
        )


@dataclass(frozen=True)
class RouteSpanAttributes:
    """03.5 §OTEL span attributes for ``l0.route_decision``.

    Frozen, validated. Integration layer reads these and emits the OTEL span.
    """

    route_id: str
    execution_form: str
    confidence: float
    reason_codes: tuple[str, ...]
    freshness_class: str
    cache_policy: str
    support_target: str
    cost_tier: str
    requires_c0: bool
    requires_l3: bool
    requires_l2: bool
    ptc_allowed_downstream: bool
    route_digest: str

    def __post_init__(self) -> None:
        for name in (
            "route_id",
            "execution_form",
            "freshness_class",
            "cache_policy",
            "support_target",
            "cost_tier",
            "route_digest",
        ):
            _need_str(getattr(self, name), f"RouteSpanAttributes.{name}")
        _need_finite_float_in_unit(self.confidence, "RouteSpanAttributes.confidence")
        _need_str_tuple(self.reason_codes, "RouteSpanAttributes.reason_codes", max_len=_MAX_REASON)
        for name in ("requires_c0", "requires_l3", "requires_l2", "ptc_allowed_downstream"):
            _need_bool(getattr(self, name), f"RouteSpanAttributes.{name}")


__all__ = ["RouteSpanAttributes", "RouteTelemetryEvent"]
