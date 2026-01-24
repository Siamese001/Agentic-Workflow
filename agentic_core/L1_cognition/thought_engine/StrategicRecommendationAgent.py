from __future__ import annotations

"""
Strategic Recommendation Agent
L3 Orchestration agent: Reviews full autonomy report data and generates high-signal strategic recommendations.

Restored: 2026-01-13 | Version: 3.0.0
Refactored: 2026-01-14 | Improved macro + metrics observations

Purpose:
- Analyzes dashboardData (territories, metrics, gaps) for cross-layer patterns.
- Generates TWO types of observations:
  1. MACRO OBSERVATIONS: Architectural insights (consolidation, layer health, structural patterns)
  2. METRICS OBSERVATIONS: Specific metric-focused recommendations (invocation, coverage, complexity)
- Outputs structured JSON with strategic review and prioritized recommendations.
- Integrated into report generator → injects into autonomy_dashboard.html
"""

# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: engine, memory, state, workflow
# This boosts alignment detection — review and integrate appropriately

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agentic_core.base_agents.decorators import standard_heal

log = logging.getLogger(__name__)


@dataclass
class StrategicRecommendationAgent(SovereignBaseAgent):
    """
    L3 Orchestration agent: Reviews full autonomy report data and generates high-signal strategic recommendations.

    Purpose:
    - Analyzes dashboardData (territories, metrics, gaps) for cross-layer patterns.
    - Outputs structured JSON with strategic review paragraph and prioritized recommendations.
    - Integrated into report generator → injects into autonomy_dashboard.html
    """

    def __init__(self, project_root: Path | None = None, llm_client: Any = None) -> None:
        """
        Initialize Strategic Recommendation Agent.

        Args:
            project_root: Root directory of the project
            llm_client: Optional LLM client for generating recommendations
        """
        super().__init__()
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.llm_client = llm_client
        log.info("[L3 STRATEGIC] StrategicRecommendationAgent initialized")

    def plan(self, dashboard_data: list[dict[str, Any]]) -> str:
        """
        Generate strategic prompt from data patterns.

        Args:
            dashboard_data: List of territory metrics from dashboard

        Returns:
            Structured prompt for LLM to generate recommendations
        """

        # Identify key gaps (handle None and "N/A" values gracefully)
        def safe_get(row: dict, key: str, default: float = 0) -> float:
            val = row.get(key, default)
            if val is None or val == "N/A":
                return default
            try:
                return float(val)
            except (ValueError, TypeError):
                return default

        low_invocation = [
            r["Territory"]
            for r in dashboard_data
            if safe_get(r, "Invocation %", 0) < 50 and r.get("Territory") != "TOTAL"
        ]
        low_mcp = [
            r["Territory"]
            for r in dashboard_data
            if safe_get(r, "Hardened %", 0) < 50 and r.get("Territory") != "TOTAL"
        ]
        low_tests = [
            r["Territory"]
            for r in dashboard_data
            if safe_get(r, "Test %", 0) < 80 and r.get("Territory") != "TOTAL"
        ]
        high_complexity = [
            r["Territory"]
            for r in dashboard_data
            if safe_get(r, "Avg CC", 0) > 15 and r.get("Territory") != "TOTAL"
        ]

        # Get total row
        total_row = next((r for r in dashboard_data if r.get("Territory") == "TOTAL"), {})

        # Extract values with None handling
        health = safe_get(total_row, "Health", 0)
        total_agents = total_row.get("Total", 0) or 0
        heal_cap = safe_get(total_row, "Heal Cap %", 0)
        invocation = safe_get(total_row, "Invocation %", 0)
        hardened = safe_get(total_row, "Hardened %", 0)
        test_cov = safe_get(total_row, "Test %", 0)

        prompt = f"""
You are a senior agentic systems architect reviewing autonomy metrics.
Generate:
1. One paragraph strategic review highlighting cross-layer risks (invocation gaps, MCP hardening, test coverage, complexity, healing discipline).
2. Top 10 prioritized recommendations (broader, actionable, with estimated impact).

Key signals:
- Low invocation (<50%) in: {", ".join(low_invocation[:5]) or "none"}
- Low MCP hardening (<50%) in: {", ".join(low_mcp[:5]) or "none"}
- Low test coverage (<80%) in: {", ".join(low_tests[:5]) or "none"}
- High complexity (>15 CC) in: {", ".join(high_complexity[:5]) or "none"}
- Overall Health: {health:.1f}%
- Total Agents: {total_agents}
- Healing Capability: {heal_cap:.1f}%
- Invocation: {invocation:.1f}%
- MCP Hardened: {hardened:.1f}%
- Test Coverage: {test_cov:.1f}%

Output strict JSON:
{{"review": "paragraph text", "recommendations": ["1. Title<br>Details...", "2. Title<br>Details...", ...]}}
"""
        return prompt

    def act(self, plan: str, dashboard_data: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Call LLM with structured prompt or generate fallback recommendations.

        Args:
            plan: Strategic prompt
            dashboard_data: Dashboard metrics

        Returns:
            Dict with 'review' and 'recommendations' keys
        """
        if self.llm_client:
            try:
                response = self.llm_client.complete(plan)
                return self._parse_llm_response(response)
            except Exception as e:
                log.warning(f"[STRATEGIC] LLM call failed: {e}, using fallback")

        # Fallback: Generate rule-based recommendations
        return self._generate_fallback_recommendations(dashboard_data)

    def _parse_llm_response(self, response: str) -> dict[str, Any]:
        """
        Parse LLM response to extract JSON.

        Args:
            response: Raw LLM response

        Returns:
            Parsed dict with review and recommendations
        """
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Fallback parsing if LLM adds fluff
            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            return {"review": "Parsing failed", "recommendations": []}

    def _generate_fallback_recommendations(
        self, dashboard_data: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        Generate rule-based recommendations when LLM is unavailable.

        SSOT for strategic observations - generates both:
        1. macro_observations: Architectural insights (L0 warnings, layer balance, portfolio structure)
        2. metric_observations: Real-time metric status (complexity, test coverage, invocation)
        3. recommendations: Actionable improvement recommendations

        Args:
            dashboard_data: Dashboard metrics

        Returns:
            Dict with review, macro_observations, metric_observations, and recommendations
        """

        # Helper for None-safe value extraction (handles "N/A" strings)
        def safe_val(row: dict, key: str, default: float = 0) -> float:
            val = row.get(key, default)
            if val is None or val == "N/A":
                return default
            try:
                return float(val)
            except (ValueError, TypeError):
                return default

        total_row = next((r for r in dashboard_data if r.get("Territory") == "TOTAL"), {})
        non_total_rows = [r for r in dashboard_data if r.get("Territory") != "TOTAL"]

        # Extract key metrics
        health = safe_val(total_row, "Health", 0)
        invocation = safe_val(total_row, "Invocation %", 0)
        mcp_hardened = safe_val(total_row, "Hardened %", 0)
        test_coverage = safe_val(total_row, "Test %", 0)
        heal_cap = safe_val(total_row, "Heal Cap %", 0)
        typed_pct = safe_val(total_row, "Typed %", 0)
        documented_pct = safe_val(total_row, "Documented %", 0)
        total_agents = total_row.get("Total", 0) or 0
        total_territories = len(non_total_rows)

        # ========================================
        # MACRO OBSERVATIONS (Architectural)
        # ========================================
        macro_observations = []

        # L0 Maintenance - should NOT have healing (infrastructure layer)
        l0_rows = [r for r in non_total_rows if "L0" in r.get("Territory", "")]
        for l0_row in l0_rows:
            heal_cap = l0_row.get("Heal Cap %")
            if heal_cap != "N/A" and safe_val(l0_row, "Heal Cap %", 0) > 0:
                macro_observations.append(
                    {
                        "icon": "🔧",
                        "title": "L0 Maintenance Layer",
                        "text": f"L0 is infrastructure/scripts layer. Healing capability is N/A here (currently showing {heal_cap}%). Focus on stability, not self-healing.",
                        "color": "#6b7280",
                    }
                )

        # Apps territories observation
        apps_rows = [r for r in non_total_rows if "Apps" in r.get("Territory", "")]
        if apps_rows:
            avg_apps_test = sum(safe_val(r, "Test %", 0) for r in apps_rows) / len(apps_rows)
            if avg_apps_test < 60:
                macro_observations.append(
                    {
                        "icon": "📱",
                        "title": "Apps Test Coverage",
                        "text": f"Apps territories average {avg_apps_test:.0f}% test coverage. Target 80% for production safety.",
                        "color": "#ea580c",
                    }
                )

        # observability observation
        if safe_val(total_row, "Observable %", 0) > 95:
            macro_observations.append(
                {
                    "icon": "👁️",
                    "title": "Excellent observability",
                    "text": f"{safe_val(total_row, 'Observable %', 0):.1f}% observability coverage. Production debugging is well-supported.",
                    "color": "#16a34a",
                }
            )

        # ========================================
        # METRIC OBSERVATIONS (Real-time Status)
        # ========================================
        metric_observations = []

        # Complexity observation
        avg_cc = safe_val(total_row, "Avg CC", 0)
        if avg_cc > 30:
            metric_observations.append(
                {
                    "icon": "⚠️",
                    "title": "High Complexity",
                    "text": f"Average CC of {avg_cc:.1f} exceeds target (≤15). Refactor high-CC methods in L5 validators and L3 orchestrators.",
                    "color": "#ea580c",
                }
            )

        # Test coverage observation
        if test_coverage < 80:
            metric_observations.append(
                {
                    "icon": "🧪",
                    "title": "Test Coverage Gap",
                    "text": f"Test coverage at {test_coverage:.1f}% (target: 80%). Focus on L1 Cognition and Apps territories first.",
                    "color": "#dc2626",
                }
            )

        # Healing invocation observation
        if invocation > 85:
            metric_observations.append(
                {
                    "icon": "✅",
                    "title": "Strong Healing Invocation",
                    "text": f"{invocation:.1f}% healing invocation is excellent. Maintain this level.",
                    "color": "#16a34a",
                }
            )

        # ========================================
        # RECOMMENDATIONS (Actionable)
        # ========================================
        recommendations = []

        # Generate strategic review from actual data
        review_parts = [
            f"Portfolio health at {health:.1f}% with {total_agents} agents across {total_territories} territories."
        ]

        # Test Coverage (most impactful)
        if test_coverage < 95:
            gap = 95 - test_coverage
            zero_test_territories = [r for r in non_total_rows if safe_val(r, "Test %", 0) == 0]
            review_parts.append(
                f"Test coverage at {test_coverage:.1f}% (target 95%) increases regression risk."
            )
            recommendations.append(
                {
                    "priority": 1,
                    "category": "Testing",
                    "title": "Expand Test Coverage",
                    "detail": f"Current: {test_coverage:.1f}% | Gap: {gap:.1f}pp | {len(zero_test_territories)} territories at 0%",
                    "action": "Add unit tests for core behaviors. Focus on zero-coverage territories first.",
                    "impact": "High - Prevents regressions during healing and refactoring cycles.",
                }
            )

        # Healing Invocation
        if invocation < 100:
            gap = 100 - invocation
            low_invocation = [r for r in non_total_rows if safe_val(r, "Invocation %", 0) < 80]
            review_parts.append(
                f"Healing invocation at {invocation:.1f}% (target 100%) indicates incomplete healing chains."
            )
            recommendations.append(
                {
                    "priority": 2,
                    "category": "Healing",
                    "title": "Complete Healing Chain Invocation",
                    "detail": f"Current: {invocation:.1f}% | Gap: {gap:.1f}pp | {len(low_invocation)} territories below 80%",
                    "action": "Add super().heal_repository(**kwargs) calls to agents that override heal_repository().",
                    "impact": "High - Ensures healing propagates through MRO chain.",
                }
            )

        # MCP Hardening
        if mcp_hardened < 100:
            gap = 100 - mcp_hardened
            unhardened = [r for r in non_total_rows if safe_val(r, "Hardened %", 0) < 100]
            review_parts.append(
                f"MCP hardening at {mcp_hardened:.1f}% (target 100%) exposes tool boundaries."
            )
            recommendations.append(
                {
                    "priority": 3,
                    "category": "Security",
                    "title": "Complete MCP Hardening",
                    "detail": f"Current: {mcp_hardened:.1f}% | Gap: {gap:.1f}pp | {len(unhardened)} territories incomplete",
                    "action": "Apply MCPHardenedMixin to all agents touching external APIs or tools.",
                    "impact": "Critical - Prevents injection and boundary violations.",
                }
            )

        # Complexity
        high_cc_territories = [r for r in non_total_rows if safe_val(r, "Avg CC", 0) > 15]
        if high_cc_territories:
            avg_cc = sum(safe_val(r, "Avg CC", 0) for r in high_cc_territories) / len(
                high_cc_territories
            )
            recommendations.append(
                {
                    "priority": 4,
                    "category": "Maintainability",
                    "title": "Reduce Cyclomatic Complexity",
                    "detail": f"{len(high_cc_territories)} territories have Avg CC >15 (avg: {avg_cc:.1f})",
                    "action": "Refactor complex methods into smaller primitives. Target CC ≤10.",
                    "impact": "Medium - Reduces bug density and improves testability.",
                }
            )

        # Typing
        if typed_pct < 100:
            gap = 100 - typed_pct
            recommendations.append(
                {
                    "priority": 5,
                    "category": "Code Quality",
                    "title": "Complete Type Annotations",
                    "detail": f"Current: {typed_pct:.1f}% | Gap: {gap:.1f}pp",
                    "action": "Add type hints to function parameters and return types.",
                    "impact": "Medium - Enables static analysis and IDE support.",
                }
            )

        # Documentation
        if documented_pct < 100:
            gap = 100 - documented_pct
            recommendations.append(
                {
                    "priority": 6,
                    "category": "Code Quality",
                    "title": "Complete Documentation",
                    "detail": f"Current: {documented_pct:.1f}% | Gap: {gap:.1f}pp",
                    "action": "Add docstrings to all public methods and classes.",
                    "impact": "Medium - Reduces hallucinated tool usage by constraining search space.",
                }
            )

        # Format recommendations for display
        formatted_recs = []
        for i, rec in enumerate(sorted(recommendations, key=lambda x: x["priority"]), 1):
            formatted_recs.append(
                f"{i}. {rec['title']}<br>"
                f"<span style='color:#666'>{rec['detail']}</span><br>"
                f"<b>Action:</b> {rec['action']}<br>"
                f"<span style='color:#059669'><b>Impact:</b> {rec['impact']}</span>"
            )

        return {
            "review": " ".join(review_parts),
            "macro_observations": macro_observations,
            "metric_observations": metric_observations,
            "recommendations": formatted_recs[:10],
        }

    def run(self, dashboard_data: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Full execution: Generate strategic recommendations from dashboard data.

        Args:
            dashboard_data: List of territory metrics

        Returns:
            Dict with 'review' and 'recommendations' keys
        """
        plan = self.plan(dashboard_data)
        result = self.act(plan, dashboard_data)
        return result

    @standard_heal
    def heal_repository(self, dry_run: bool = True, **kwargs) -> dict[str, int]:
        """Invoke healing chain via super()."""
        return super().heal_repository(dry_run=dry_run, **kwargs)
