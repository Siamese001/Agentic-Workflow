"""PA Observability Events — eight named events from the spec.

Each event is a frozen dataclass with the exact field set listed in
``Prompt_Assembly_detailed.md`` §OBSERVABILITY EVENTS. Events are pure-data
records; emission to a sink is the caller's responsibility (the pipeline
orchestrator collects them in order so a span exporter or test harness can
consume them deterministically).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class PromptAssemblyEvent:
    """Marker base. Frozen + dataclass for stable equality/hashing."""

    event_type: str = "PromptAssemblyEvent"


@dataclass(frozen=True)
class PromptAssemblyStarted(PromptAssemblyEvent):
    """First event. Emitted at PA.0 entry."""

    request_id: str = ""
    plan_id: str = ""
    route_id: str = ""
    policy_hash: str = ""
    provider_lane: str = ""
    event_type: str = "PromptAssemblyStarted"


@dataclass(frozen=True)
class PromptBOMResolved(PromptAssemblyEvent):
    """Emitted after PA.1 BOM resolution."""

    bom_id: str = ""
    slots_requested: tuple[str, ...] = ()
    slots_available: tuple[str, ...] = ()
    slots_missing: tuple[str, ...] = ()
    event_type: str = "PromptBOMResolved"


@dataclass(frozen=True)
class PromptSecurityPassCompleted(PromptAssemblyEvent):
    """Emitted after PA.3 security pass."""

    u0_disposition: str = ""
    c0_classifier_disposition: str = ""
    h0_disposition: str = ""
    stripped_count: int = 0
    quarantined_count: int = 0
    event_type: str = "PromptSecurityPassCompleted"


@dataclass(frozen=True)
class PromptSlotValidationCompleted(PromptAssemblyEvent):
    """Emitted after PA.4 slot-contract validation."""

    validation_status: str = ""
    failed_checks: tuple[str, ...] = ()
    authority_violations: tuple[str, ...] = ()
    schema_status: str = ""
    tool_status: str = ""
    evidence_status: str = ""
    event_type: str = "PromptSlotValidationCompleted"


@dataclass(frozen=True)
class PromptBudgetCompleted(PromptAssemblyEvent):
    """Emitted after PA.5 budget enforcement."""

    input_token_estimate: int = 0
    output_token_reserve: int = 0
    trim_actions: tuple[str, ...] = ()
    overflow_status: str = ""
    event_type: str = "PromptBudgetCompleted"


@dataclass(frozen=True)
class PromptRenderedForProvider(PromptAssemblyEvent):
    """Emitted after PA.6 provider-aware rendering."""

    provider_adapter_id: str = ""
    model_id: str = ""
    schema_bound: bool = False
    tools_bound: bool = False
    event_type: str = "PromptRenderedForProvider"


@dataclass(frozen=True)
class CompiledPromptArtifactSigned(PromptAssemblyEvent):
    """Emitted at PA.7 emit when artifact is signed."""

    artifact_id: str = ""
    manifest_hash: str = ""
    signature_status: str = ""
    replay_key: str = ""
    event_type: str = "CompiledPromptArtifactSigned"


@dataclass(frozen=True)
class PromptAssemblyBlocked(PromptAssemblyEvent):
    """Emitted when any PA stage blocks dispatch."""

    reason_code: str = ""
    policy_hash: str = ""
    plan_id: str = ""
    route_id: str = ""
    recommended_disposition: str = ""
    event_type: str = "PromptAssemblyBlocked"


@dataclass(frozen=True)
class PromptAssemblyDispatched(PromptAssemblyEvent):
    """Emitted when artifact passes to L2."""

    artifact_id: str = ""
    l2_target: str = ""
    trace_root: str = ""
    event_type: str = "PromptAssemblyDispatched"


PA_EVENT_TYPES: tuple[type[PromptAssemblyEvent], ...] = (
    PromptAssemblyStarted,
    PromptBOMResolved,
    PromptSecurityPassCompleted,
    PromptSlotValidationCompleted,
    PromptBudgetCompleted,
    PromptRenderedForProvider,
    CompiledPromptArtifactSigned,
    PromptAssemblyBlocked,
    PromptAssemblyDispatched,
)


@dataclass
class EventBuffer:
    """Mutable in-memory event collector for the pipeline orchestrator."""

    events: list[PromptAssemblyEvent] = field(default_factory=list)

    def emit(self, event: PromptAssemblyEvent) -> None:
        self.events.append(event)

    def types(self) -> tuple[str, ...]:
        return tuple(e.event_type for e in self.events)

    def to_dicts(self) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for ev in self.events:
            d = {f: getattr(ev, f) for f in ev.__dataclass_fields__}  # guardian: allow-hallucinated-tool-name -- getattr is Python stdlib; reads event dataclass fields by name  # type: ignore[attr-defined]
            d["event_type"] = ev.event_type
            out.append(d)
        return out


__all__ = [
    "CompiledPromptArtifactSigned",
    "EventBuffer",
    "PA_EVENT_TYPES",
    "PromptAssemblyBlocked",
    "PromptAssemblyDispatched",
    "PromptAssemblyEvent",
    "PromptAssemblyStarted",
    "PromptBOMResolved",
    "PromptBudgetCompleted",
    "PromptRenderedForProvider",
    "PromptSecurityPassCompleted",
    "PromptSlotValidationCompleted",
]
