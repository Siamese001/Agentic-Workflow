"""L1 Plan Contract — AG-RGGOV-W6 Core Contract

Canonical dataclass for L1 planning output.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass(frozen=True, slots=True)
class L1PlanContract:
    """L1 planning output contract.

    Contains planning decisions, routing requirements, and execution prerequisites.
    """

    request_id: str
    run_id: str
    app_id: str
    trace_id: str

    # Planning decisions
    task_plan: tuple[str, ...] = field(default_factory=tuple)
    required_capabilities: tuple[str, ...] = field(default_factory=tuple)

    # Execution prerequisites (determine routing)
    grounding_required: bool = False  # C0 evidence collection needed
    model_generation_required: bool = False  # L2 model execution needed
    write_authority_present: bool = False  # State modification required

    # Profile binding
    profile_manifest_digest: str = ""

    # Receipt
    planning_timestamp: str = ""
    plan_version: str = "W6.0"
    l5_certification_ref: str = ""

    def __post_init__(self) -> None:
        from agentic_core.L5_safety.contracts.verify import verify_certification_ref
        if not verify_certification_ref(self.l5_certification_ref):
            raise ValueError(
                f"L1PlanContract: missing or invalid l5_certification_ref={self.l5_certification_ref!r} "
                "(AG-W0-5=fail_closed)"
            )
