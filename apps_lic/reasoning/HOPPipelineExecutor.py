"""HOPPipelineExecutor — Canonical parameterized HOP pipeline stage agent.

Consolidates: HOP1-HOP9 pipeline stage agents.
Created: 2026-02-08 (Structural Agent Count Reduction)

Each stage's _process() logic is preserved in hop_stage_registry.py.
This executor dispatches to the registered stage implementation.

GOVERNANCE: reasoning_profile is injected from the L0-stamped
SignedExecutionEnvelope and treated as READ-ONLY constraints.
The executor may not modify or override any profile field.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from apps_lic.utils.hop_stage_capability import HOPStageCapability
from apps_lic.utils.LICAgentBase import LICAgentBase

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

if TYPE_CHECKING:
    from agentic_core.interfaces.routing_types import ReasoningIntensityProfile


@dataclass
class HOPPipelineExecutor(HOPStageCapability, LICAgentBase):
    """Parameterized HOP pipeline stage agent.

    Usage:
        stage = HOPPipelineExecutor(stage_id=4)
        stage = HOPPipelineExecutor(stage_id=4, reasoning_profile=profile)

    When reasoning_profile is provided it is treated as READ-ONLY policy
    constraints stamped by L0. The executor must not mutate or override it.
    When absent, stage handlers fall back to static DEFAULT_TOGGLES.
    """

    stage_id: int = 0
    stage_name: str = field(init=False, default="unknown")
    reasoning_profile: ReasoningIntensityProfile | None = field(default=None, repr=False)

    _STAGE_NAMES = {
        1: "profile_analysis",
        2: "research",
        3: "sender_grounding",
        4: "routing",
        5: "generation",
        6: "validation",
        7: "gate_decision",
        8: "qa_report",
        9: "integration",
    }

    def __post_init__(self) -> None:
        self.stage_name = self._STAGE_NAMES.get(self.stage_id, "unknown")

    def _process(self, context: dict | None = None, **kwargs) -> dict:
        """Dispatch to stage-specific processing.

        Domain logic for each stage is preserved via the stage registry.
        reasoning_profile (if present) is forwarded as a read-only constraint.
        """
        from apps_lic.engines import hop_stage_registry

        handler = hop_stage_registry.get_stage_handler(self.stage_id)
        if handler is None:
            return {"stage": self.stage_id, "error": f"No handler for stage {self.stage_id}"}
        return handler(self, context or {}, reasoning_profile=self.reasoning_profile, **kwargs)
