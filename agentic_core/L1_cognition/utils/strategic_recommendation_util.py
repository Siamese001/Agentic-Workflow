"""Strategic Recommendation Utility - Deterministic recommendation generation.

This module provides deterministic recommendation functionality previously
implemented in StrategicRecommendationAgent. Converted from agent to utility script
as part of SCRIPT agent conversion (Micro-wave 6).

Usage:
    from agentic_core.L1_cognition.utils.strategic_recommendation_util import (
        generate_strategic_prompt, parse_recommendations, generate_fallback_recommendations
    )

    # Generate strategic prompt
    prompt = generate_strategic_prompt(dashboard_data)
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from typing import Any

Logger = logging.getLogger(__name__)


@dataclass
class RecommendationResult:
    """Result of strategic recommendation generation."""

    review: str
    recommendations: list[str]
    source: str  # "llm" or "fallback"


def _safe_get(row: dict[str, Any], key: str, default: float = 0.0) -> float:
    """Safely get a numeric value from dashboard row."""
    val = row.get(key, default)
    if val is None or val == "N/A":
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def generate_strategic_prompt(dashboard_data: list[dict[str, Any]]) -> str:
    """Generate strategic prompt from dashboard data patterns.

    Args:
        dashboard_data: List of territory metrics from dashboard

    Returns:
        Structured prompt for LLM to generate recommendations
    """
    # Identify problem areas
    low_invocation = [
        r["Territory"]
        for r in dashboard_data
        if _safe_get(r, "Invocation %", 0) < 50 and r.get("Territory") != "TOTAL"
    ]
    low_mcp = [
        r["Territory"]
        for r in dashboard_data
        if _safe_get(r, "Hardened %", 0) < 50 and r.get("Territory") != "TOTAL"
    ]
    low_tests = [
        r["Territory"]
        for r in dashboard_data
        if _safe_get(r, "Test %", 0) < 80 and r.get("Territory") != "TOTAL"
    ]
    high_complexity = [
        r["Territory"]
        for r in dashboard_data
        if _safe_get(r, "Avg CC", 0) > 15 and r.get("Territory") != "TOTAL"
    ]

    # Get totals
    total_row = next((r for r in dashboard_data if r.get("Territory") == "TOTAL"), {})
    health = _safe_get(total_row, "Health", 0)
    total_agents = total_row.get("Total", 0) or 0
    heal_cap = _safe_get(total_row, "Heal Cap %", 0)
    invocation = _safe_get(total_row, "Invocation %", 0)
    hardened = _safe_get(total_row, "Hardened %", 0)
    test_cov = _safe_get(total_row, "Test %", 0)

    prompt = f"""You are a senior agentic systems architect reviewing autonomy metrics.
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


def parse_llm_response(response: str) -> dict[str, Any]:
    """Parse LLM response to extract JSON.

    Args:
        response: Raw LLM response

    Returns:
        Parsed dict with review and recommendations
    """
    try:
        # Try to find JSON in the response
        json_match = re.search(r"\{.*\}", response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except json.JSONDecodeError as e:  # guardian: allow-log-and-swallow -- JSON parse failure: falls back to empty recommendations dict; intentional fallback for malformed LLM responses
        logging.getLogger(__name__).warning(
            "strategic_recommendation_util: JSON parse failed, returning empty recommendations: %s", e
        )

    # Fallback: return empty structure
    return {"review": "", "recommendations": []}


def generate_fallback_recommendations(dashboard_data: list[dict[str, Any]]) -> RecommendationResult:
    """Generate fallback recommendations when LLM is unavailable.

    Args:
        dashboard_data: Dashboard metrics

    Returns:
        RecommendationResult with fallback recommendations
    """
    low_invocation = [
        r["Territory"]
        for r in dashboard_data
        if _safe_get(r, "Invocation %", 0) < 50 and r.get("Territory") != "TOTAL"
    ]
    low_mcp = [
        r["Territory"]
        for r in dashboard_data
        if _safe_get(r, "Hardened %", 0) < 50 and r.get("Territory") != "TOTAL"
    ]
    low_tests = [
        r["Territory"]
        for r in dashboard_data
        if _safe_get(r, "Test %", 0) < 80 and r.get("Territory") != "TOTAL"
    ]

    recommendations = []

    if low_invocation:
        recommendations.append(f"1. Boost Invocation Coverage<br>Focus on: {', '.join(low_invocation[:3])}")
    if low_mcp:
        recommendations.append(
            f"2. Strengthen MCP Hardening<br>Priority territories: {', '.join(low_mcp[:3])}"
        )
    if low_tests:
        recommendations.append(f"3. Increase Test Coverage<br>Target: {', '.join(low_tests[:3])}")

    if not recommendations:
        recommendations.append("1. Maintain Current Performance<br>All metrics within acceptable thresholds")

    total_row = next((r for r in dashboard_data if r.get("Territory") == "TOTAL"), {})
    health = _safe_get(total_row, "Health", 0)

    review = f"System health at {health:.1f}%. "
    if low_invocation or low_mcp or low_tests:
        review += "Identified gaps in invocation, hardening, or test coverage requiring attention."
    else:
        review += "All autonomy metrics performing within expected parameters."

    return RecommendationResult(
        review=review,
        recommendations=recommendations,
        source="fallback",
    )


def analyze_dashboard(dashboard_data: list[dict[str, Any]]) -> dict[str, Any]:
    """Analyze dashboard and return structured insights.

    Args:
        dashboard_data: List of territory metrics

    Returns:
        Dictionary with analysis results
    """
    prompt = generate_strategic_prompt(dashboard_data)
    fallback = generate_fallback_recommendations(dashboard_data)

    return {
        "prompt": prompt,
        "fallback": {
            "review": fallback.review,
            "recommendations": fallback.recommendations,
        },
        "metrics": {
            "territories_analyzed": len([r for r in dashboard_data if r.get("Territory") != "TOTAL"]),
            "has_llm_option": True,
        },
    }
