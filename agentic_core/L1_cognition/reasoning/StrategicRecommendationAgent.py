"""Strategic Recommendation Agent - Backward compatibility shim.

DEPRECATED: This agent has been converted to a utility script.
Use agentic_core.L1_cognition.utils.strategic_recommendation_util instead.

This module maintains backward compatibility by delegating to the utility.
Will be removed in a future release.

AGENT-DELETION-AUTHORIZED: 2026-04-24 (W3.1 of agent-deprecation-migration-d7a3f2)
Authorization date: 2026-04-24
Archive-eligible date: 2026-07-23 (90-day cooling per constitutional \u00a73)
Consumers at authorization: 0 (verified via w3_verify_zero_consumers.py grep of
`from agentic_core.L1_cognition.reasoning.StrategicRecommendationAgent import` and `import agentic_core.L1_cognition.reasoning.StrategicRecommendationAgent` across live code,
excluding self and archives/ paths — zero hits).
Unique logic: none (pure delegation to agentic_core.L1_cognition.utils.strategic_recommendation_util per DEPRECATED docstring above).
Target archive path on or after eligibility date:
  archives/agents/2026-07-23/agentic_core__L1_cognition__reasoning__StrategicRecommendationAgent.py
Cooling-timer artifact: artifacts/agent_deprecation/w3_StrategicRecommendationAgent.json
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
            except (RuntimeError, ValueError, TypeError, AttributeError, OSError) as e:  # guardian: allow-log-and-swallow -- LLM completion failure: non-fatal; falls back to default recommendation
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
