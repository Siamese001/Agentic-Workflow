"""Route Contract — AG-RGGOV-W6 Core Contract

Canonical dataclass for L0 routing output.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass(frozen=True, slots=True)
class RouteContract:
    """L0 routing output contract.

    Contains routing decision and execution path.
    """

    request_id: str
    run_id: str
    app_id: str
    trace_id: str

    # Routing decision
    route_id: str  # e.g., "R3_SIMPLE_GROUNDED_READ", "R5_MANAGED_WORKFLOW"
    l3_required: bool  # Whether L3 orchestration is needed

    # Execution path flags
    grounding_required: bool
    model_generation_required: bool
    write_authority_present: bool

    # Routing metadata
    reason_codes: tuple[str, ...] = field(default_factory=tuple)
    routing_timestamp: str = ""
    route_version: str = "W6.0"
