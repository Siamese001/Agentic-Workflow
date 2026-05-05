"""QnA Capability Registry — registers live interview pack capability.

W1.2: Registry scaffold. Declares the live_interview_runtime_pack
capability with its L2 step adapters and exit FEC producer.

Plan: .windsurf/plans/apps-qna-spine-integration-e9c5b3.md W1.2
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass(frozen=True)
class CapabilityEntry:
    """A single registered capability with its adapters."""

    capability_id: str
    route_id: str
    description: str
    grounding_required: bool
    c0_required: bool
    l2_steps: tuple[str, ...] = ()
    exit_fec_producer: str = ""


_QNA_CAPABILITIES: dict[str, CapabilityEntry] = {}


def register_capability(entry: CapabilityEntry) -> None:
    """Register a capability entry."""
    _QNA_CAPABILITIES[entry.capability_id] = entry


def get_capability(capability_id: str) -> CapabilityEntry | None:
    """Look up a capability by id."""
    return _QNA_CAPABILITIES.get(capability_id)


def list_capabilities() -> tuple[CapabilityEntry, ...]:
    """Return all registered capabilities."""
    return tuple(_QNA_CAPABILITIES.values())


# Register the live interview runtime pack capability
register_capability(CapabilityEntry(
    capability_id="live_interview_runtime_pack",
    route_id="apps_qna.live_interview_runtime_pack_v1",
    description="Live interview runtime pack with C0 grounding",
    grounding_required=True,
    c0_required=True,
    l2_steps=("e1_prep", "e2_valid", "e3_exec", "e4_heal", "e5_seal"),
    exit_fec_producer="apps_qna.qna_exit_fec_producer",
))

register_capability(CapabilityEntry(
    capability_id="live_interview_runtime_pack_from_briefing",
    route_id="apps_qna.live_interview_runtime_pack_from_uploaded_brief_v1",
    description="Live interview runtime pack from uploaded briefing",
    grounding_required=False,
    c0_required=False,
    l2_steps=("e1_prep", "e2_valid", "e3_exec", "e4_heal", "e5_seal"),
    exit_fec_producer="apps_qna.qna_exit_fec_producer",
))


__all__ = [
    "CapabilityEntry",
    "get_capability",
    "list_capabilities",
    "register_capability",
]
