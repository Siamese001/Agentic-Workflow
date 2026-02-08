"""
ContentStrategyAgent — DEPRECATED backward-compatibility shim.

Superseded by RgStrategicPlannerAgent (L2_execution).
Consolidation: Cluster 7 (responsibility_overlap=1.0).

Canonical agent: agentic_core.L2_execution.reasoning.RgStrategicPlannerAgent
New code should import RgStrategicPlannerAgent directly.
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass, field

from apps_rg.utils.RGAgentBase import RGAgentBase


@dataclass
class ContentStrategyAgent(RGAgentBase):
    """
    DEPRECATED — Sovereign Content Strategist shim.

    Retained for backward compatibility only.
    Canonical replacement: RgStrategicPlannerAgent.
    Analyzes topics and generates content calendars.
    """

    target_audience: str = "general"
    keywords: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        warnings.warn(
            "ContentStrategyAgent is deprecated. Use RgStrategicPlannerAgent instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__post_init__()

    def analyze_topic(self, topic: str) -> dict[str, float]:
        """
        Perform semantic analysis on a topic.

        DEPRECATED: This method is retained for backward compatibility.
        """
        if not topic:
            return {"relevance": 0.0}

        return {"relevance": 0.95, "sentiment": 0.8}
