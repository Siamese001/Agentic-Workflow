"""PA Runtime ADG / Trace Spans (spec lines 1754-1855).

Eight named child spans the PA pipeline emits under the request trace root.
Each span has a stable name, a parent, and the deterministic attribute set
the runtime ADG ingestion stage expects.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class SpanDefinition:
    name: str
    parent: str
    description: str
    attributes: tuple[str, ...]


PA_PARENT_SPAN_NAME: str = "prompt_assembly.run"


PA_SPAN_DEFINITIONS: tuple[SpanDefinition, ...] = (
    SpanDefinition(
        "prompt_assembly.boundary_check",
        PA_PARENT_SPAN_NAME,
        "PA.0 seven-check boundary gate",
        ("plan_id", "route_id", "boundary_status", "fail_reason"),
    ),
    SpanDefinition(
        "prompt_assembly.bom_resolve",
        PA_PARENT_SPAN_NAME,
        "PA.1 12-stage BOM resolution",
        ("bom_id", "slots_requested", "slots_available", "slots_missing"),
    ),
    SpanDefinition(
        "prompt_assembly.compose_slots",
        PA_PARENT_SPAN_NAME,
        "PA.2 canonical-order slot composition",
        ("slot_codes_present", "authority_violations"),
    ),
    SpanDefinition(
        "prompt_assembly.security_pass",
        PA_PARENT_SPAN_NAME,
        "PA.3 U0 + C0 + H0 airlock pass",
        (
            "u0_disposition",
            "u0_injection_score",
            "c0_pass_count",
            "c0_strip_count",
            "c0_quarantine_count",
            "c0_reject_count",
            "h0_accepted",
        ),
    ),
    SpanDefinition(
        "prompt_assembly.validate_slot_contract",
        PA_PARENT_SPAN_NAME,
        "PA.4 17-check validation matrix",
        ("validation_passed_count", "validation_failed_count", "validation_failed_ids"),
    ),
    SpanDefinition(
        "prompt_assembly.budget",
        PA_PARENT_SPAN_NAME,
        "PA.5 token budget + trim",
        (
            "input_token_estimate",
            "reserved_output_tokens",
            "overflow_status",
            "trim_actions_count",
        ),
    ),
    SpanDefinition(
        "prompt_assembly.provider_render",
        PA_PARENT_SPAN_NAME,
        "PA.6 provider-lane rendering",
        ("provider_lane", "model_id", "schema_bound", "tools_bound"),
    ),
    SpanDefinition(
        "prompt_assembly.final_emit",
        PA_PARENT_SPAN_NAME,
        "PA.7 sign + emit + dispatch outcome",
        ("artifact_id", "manifest_hash", "signature_status", "dispatch_disposition"),
    ),
)


SPAN_NAMES: frozenset[str] = frozenset(s.name for s in PA_SPAN_DEFINITIONS)


@dataclass(frozen=True)
class SpanRecord:
    name: str
    parent: str
    attributes: dict[str, Any] = field(default_factory=dict)
    duration_ms: float = 0.0


@dataclass
class SpanCollector:
    """Test-friendly span buffer."""

    spans: list[SpanRecord] = field(default_factory=list)

    def emit(self, name: str, attributes: dict[str, Any] | None = None, duration_ms: float = 0.0) -> None:
        if name not in SPAN_NAMES:
            raise ValueError("unknown PA span: " + name)
        parent = next(s.parent for s in PA_SPAN_DEFINITIONS if s.name == name)
        self.spans.append(
            SpanRecord(name=name, parent=parent, attributes=dict(attributes or {}), duration_ms=duration_ms)
        )

    def names(self) -> tuple[str, ...]:
        return tuple(s.name for s in self.spans)


__all__ = [
    "PA_PARENT_SPAN_NAME",
    "PA_SPAN_DEFINITIONS",
    "SPAN_NAMES",
    "SpanCollector",
    "SpanDefinition",
    "SpanRecord",
]
