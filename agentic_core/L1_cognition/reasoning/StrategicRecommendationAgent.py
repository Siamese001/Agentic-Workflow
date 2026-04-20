"""Strategic Recommendation Agent - Backward compatibility shim.

DEPRECATED: This agent has been converted to a utility script.
Use agentic_core.L1_cognition.utils.strategic_recommendation_util instead.

This module maintains backward compatibility by delegating to the utility.
Will be removed in a future release.
"""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L1_cognition.utils.strategic_recommendation_util import (
    analyze_dashboard as _analyze_dashboard,
)
from agentic_core.L1_cognition.utils.strategic_recommendation_util import (
    generate_fallback_recommendations as _generate_fallback_recommendations,
)
from agentic_core.L1_cognition.utils.strategic_recommendation_util import (
    generate_strategic_prompt as _generate_strategic_prompt,
)
from agentic_core.L1_cognition.utils.strategic_recommendation_util import (
    parse_llm_response as _parse_llm_response,
)


class StrategicRecommendationAgent(SovereignBaseAgent):
    """
    DEPRECATED: Strategic Recommendation Agent - now delegates to strategic_recommendation_util.

    This class is maintained for backward compatibility only.
    New code should use agentic_core.L1_cognition.utils.strategic_recommendation_util directly.
    """

    def __init__(self, project_root: Path | None = None, llm_client: Any | None = None):
        """Initialize StrategicRecommendationAgent (deprecated, use strategic_recommendation_util instead)."""
        super().__init__(name="StrategicRecommendationAgent", layer="L1")

        warnings.warn(
            "StrategicRecommendationAgent is deprecated. Use agentic_core.L1_cognition.utils.strategic_recommendation_util instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.llm_client = llm_client

    def plan(self, dashboard_data: list[dict[str, Any]]) -> str:
        """Generate strategic prompt from data patterns."""
        return _generate_strategic_prompt(dashboard_data)

    def act(self, plan: str, dashboard_data: list[dict[str, Any]]) -> dict[str, Any]:
        """Call LLM with structured prompt or generate fallback recommendations."""
        if self.llm_client:
            try:
                response = self.llm_client.complete(plan)
                return _parse_llm_response(response)
            except (RuntimeError, ValueError, TypeError, AttributeError, OSError) as e:  # guardian: allow-log-and-swallow  -- ADG-burn: log_and_swallow
                import logging

                logging.getLogger(__name__).debug(
                    "StrategicRecommendationAgent: Exception swallowed at L62: %s", e
                )

        fallback = _generate_fallback_recommendations(dashboard_data)
        return {
            "review": fallback.review,
            "recommendations": fallback.recommendations,
        }

    def analyze(self, dashboard_data: list[dict[str, Any]]) -> dict[str, Any]:
        """Analyze dashboard and return structured insights."""
        return _analyze_dashboard(dashboard_data)
