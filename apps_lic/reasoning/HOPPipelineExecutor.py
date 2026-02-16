"""HOPPipelineExecutor — Canonical parameterized HOP pipeline stage agent.

Consolidates: HOP1-HOP9 pipeline stage agents.
Created: 2026-02-08 (Structural Agent Count Reduction)

Each stage's _process() logic is preserved in hop_stage_registry.py.
This executor dispatches to the registered stage implementation.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from apps_lic.utils.hop_stage_capability import HOPStageCapability
from apps_lic.utils.LICAgentBase import LICAgentBase


@dataclass
class HOPPipelineExecutor(HOPStageCapability, LICAgentBase):
    """Parameterized HOP pipeline stage agent.

    Usage:
        stage = HOPPipelineExecutor(stage_id=4)
    """

    stage_id: int = 0
    stage_name: str = field(init=False, default="unknown")

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
        Import and call the original _process implementations.
        """
        from apps_lic.engines import hop_stage_registry

        handler = hop_stage_registry.get_stage_handler(self.stage_id)
        if handler is None:
            return {"stage": self.stage_id, "error": f"No handler for stage {self.stage_id}"}
        return handler(self, context or {}, **kwargs)
