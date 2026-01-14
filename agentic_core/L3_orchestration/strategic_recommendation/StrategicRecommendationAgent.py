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
from __future__ import annotations
from dataclasses import dataclass

import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.common.healing.healer_mixin import HealerMixin

log = logging.getLogger(__name__)


@dataclass
class StrategicRecommendationAgent(MCPHardenedMixin, HealerMixin):
    """
    L3 Orchestration agent: Reviews full autonomy report data and generates high-signal strategic recommendations.
    
    Purpose:
    - Analyzes dashboardData (territories, metrics, gaps) for cross-layer patterns.
    - Outputs structured JSON with strategic review paragraph and prioritized recommendations.
    - Integrated into report generator → injects into autonomy_dashboard.html
    """
    
    def __init__(self, project_root: Optional[Path] = None, llm_client: Any = None) -> None:
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
    
    def plan(self, dashboard_data: List[Dict[str, Any]]) -> str:
        """
        Generate strategic prompt from data patterns.
        
        Args:
            dashboard_data: List of territory metrics from dashboard
            
        Returns:
            Structured prompt for LLM to generate recommendations
        """
        # Identify key gaps (handle None values gracefully)
        def safe_get(row: Dict, key: str, default: float = 0) -> float:
            val = row.get(key, default)
            return val if val is not None else default
        
        low_invocation = [r['Territory'] for r in dashboard_data 
                        if safe_get(r, 'Invocation %', 0) < 50 and r.get('Territory') != 'TOTAL']
        low_mcp = [r['Territory'] for r in dashboard_data 
                 if safe_get(r, 'Hardened %', 0) < 50 and r.get('Territory') != 'TOTAL']
        low_tests = [r['Territory'] for r in dashboard_data 
                   if safe_get(r, 'Test %', 0) < 80 and r.get('Territory') != 'TOTAL']
        high_complexity = [r['Territory'] for r in dashboard_data 
                         if safe_get(r, 'Avg CC', 0) > 15 and r.get('Territory') != 'TOTAL']
        
        # Get total row
        total_row = next((r for r in dashboard_data if r.get('Territory') == 'TOTAL'), {})
        
        # Extract values with None handling
        health = safe_get(total_row, 'Health', 0)
        total_agents = total_row.get('Total', 0) or 0
        heal_cap = safe_get(total_row, 'Heal Cap %', 0)
        invocation = safe_get(total_row, 'Invocation %', 0)
        hardened = safe_get(total_row, 'Hardened %', 0)
        test_cov = safe_get(total_row, 'Test %', 0)
        
        prompt = f"""
You are a senior agentic systems architect reviewing autonomy metrics.
Generate:
1. One paragraph strategic review highlighting cross-layer risks (invocation gaps, MCP hardening, test coverage, complexity, healing discipline).
2. Top 10 prioritized recommendations (broader, actionable, with estimated impact).

Key signals:
- Low invocation (<50%) in: {', '.join(low_invocation[:5]) or 'none'}
- Low MCP hardening (<50%) in: {', '.join(low_mcp[:5]) or 'none'}
- Low test coverage (<80%) in: {', '.join(low_tests[:5]) or 'none'}
- High complexity (>15 CC) in: {', '.join(high_complexity[:5]) or 'none'}
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
    
    def act(self, plan: str, dashboard_data: List[Dict[str, Any]]) -> Dict[str, Any]:
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
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
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
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            return {"review": "Parsing failed", "recommendations": []}
    
    def _generate_fallback_recommendations(self, dashboard_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate rule-based recommendations when LLM is unavailable.
        
        Generates TWO types of observations:
        1. MACRO OBSERVATIONS: Architectural insights about portfolio structure
        2. METRICS OBSERVATIONS: Specific metric-focused recommendations
        
        Args:
            dashboard_data: Dashboard metrics
            
        Returns:
            Dict with review, macro_observations, and recommendations
        """
        # Helper for None-safe value extraction
        def safe_val(row: Dict, key: str, default: float = 0) -> float:
            val = row.get(key, default)
            return val if val is not None else default
        
        total_row = next((r for r in dashboard_data if r.get('Territory') == 'TOTAL'), {})
        non_total_rows = [r for r in dashboard_data if r.get('Territory') != 'TOTAL']
        
        # Extract key metrics
        health = safe_val(total_row, 'Health', 0)
        invocation = safe_val(total_row, 'Invocation %', 0)
        mcp_hardened = safe_val(total_row, 'Hardened %', 0)
        test_coverage = safe_val(total_row, 'Test %', 0)
        heal_cap = safe_val(total_row, 'Heal Cap %', 0)
        typed_pct = safe_val(total_row, 'Typed %', 0)
        documented_pct = safe_val(total_row, 'Documented %', 0)
        total_agents = total_row.get('Total', 0) or 0
        total_territories = len(non_total_rows)
        
        # ========================================
        # MACRO OBSERVATIONS (Architectural)
        # ========================================
        macro_observations = []
        
        # 1. Portfolio Size & Consolidation Analysis
        agents_per_territory = total_agents / max(total_territories, 1)
        small_territories = [r for r in non_total_rows if (r.get('Total', 0) or 0) <= 2]
        large_territories = [r for r in non_total_rows if (r.get('Total', 0) or 0) >= 20]
        
        if len(small_territories) > 5:
            macro_observations.append({
                "type": "consolidation",
                "severity": "medium",
                "title": "Territory Fragmentation Detected",
                "observation": f"{len(small_territories)} territories have ≤2 agents each. Consider consolidating micro-territories to reduce cognitive overhead and improve maintainability.",
                "territories": [t['Territory'] for t in small_territories[:5]],
                "action": "Merge related micro-territories or promote agents to parent territories."
            })
        
        if total_agents > 250:
            macro_observations.append({
                "type": "scale",
                "severity": "info",
                "title": "Large Agent Portfolio",
                "observation": f"Portfolio contains {total_agents} agents across {total_territories} territories ({agents_per_territory:.1f} agents/territory avg). At this scale, automated governance and discovery become critical.",
                "action": "Ensure automated discovery, health monitoring, and healing are fully operational."
            })
        
        # 2. Layer Balance Analysis
        layer_counts = {}
        for row in non_total_rows:
            territory = row.get('Territory', '')
            for layer in ['L0', 'L1', 'L2', 'L3', 'L4', 'L5', 'L6']:
                if layer in territory:
                    layer_counts[layer] = layer_counts.get(layer, 0) + (row.get('Total', 0) or 0)
                    break
        
        if layer_counts:
            max_layer = max(layer_counts, key=layer_counts.get)
            min_layer = min(layer_counts, key=layer_counts.get)
            if layer_counts[max_layer] > 3 * layer_counts.get(min_layer, 1):
                macro_observations.append({
                    "type": "imbalance",
                    "severity": "medium",
                    "title": "Layer Imbalance Detected",
                    "observation": f"{max_layer} has {layer_counts[max_layer]} agents while {min_layer} has only {layer_counts.get(min_layer, 0)}. Heavy concentration in one layer may indicate architectural drift.",
                    "action": f"Review {max_layer} for potential decomposition or consolidation opportunities."
                })
        
        # 3. Base Class Health
        base_territories = [r for r in non_total_rows if 'Base' in r.get('Territory', '')]
        if base_territories:
            unhealthy_bases = [r for r in base_territories if safe_val(r, 'Health', 0) < 80]
            if unhealthy_bases:
                macro_observations.append({
                    "type": "foundation",
                    "severity": "critical",
                    "title": "Base Class Health Risk",
                    "observation": f"{len(unhealthy_bases)} base class territories have health <80%. Base classes are foundational—issues here cascade to all inheriting agents.",
                    "territories": [t['Territory'] for t in unhealthy_bases],
                    "action": "Prioritize base class remediation before addressing leaf agents."
                })
        
        # 4. Apps vs Core Distribution
        apps_rows = [r for r in non_total_rows if 'Apps' in r.get('Territory', '')]
        core_rows = [r for r in non_total_rows if 'Apps' not in r.get('Territory', '')]
        apps_agents = sum(r.get('Total', 0) or 0 for r in apps_rows)
        core_agents = sum(r.get('Total', 0) or 0 for r in core_rows)
        
        if apps_agents > 0 and core_agents > 0:
            ratio = apps_agents / core_agents
            if ratio > 0.5:
                macro_observations.append({
                    "type": "architecture",
                    "severity": "info",
                    "title": "Significant Application Layer",
                    "observation": f"Application agents ({apps_agents}) represent {ratio*100:.0f}% of core agents ({core_agents}). Ensure app-layer agents properly delegate to core primitives rather than duplicating logic.",
                    "action": "Audit app agents for core logic duplication; refactor shared patterns into L2/L3."
                })
        
        # ========================================
        # METRICS OBSERVATIONS (Specific Gaps)
        # ========================================
        recommendations = []
        
        # Generate strategic review from actual data
        review_parts = [f"Portfolio health at {health:.1f}% with {total_agents} agents across {total_territories} territories."]
        
        # Test Coverage (most impactful)
        if test_coverage < 95:
            gap = 95 - test_coverage
            zero_test_territories = [r for r in non_total_rows if safe_val(r, 'Test %', 0) == 0]
            review_parts.append(f"Test coverage at {test_coverage:.1f}% (target 95%) increases regression risk.")
            recommendations.append({
                "priority": 1,
                "category": "Testing",
                "title": "Expand Test Coverage",
                "detail": f"Current: {test_coverage:.1f}% | Gap: {gap:.1f}pp | {len(zero_test_territories)} territories at 0%",
                "action": "Add unit tests for core behaviors. Focus on zero-coverage territories first.",
                "impact": "High - Prevents regressions during healing and refactoring cycles."
            })
        
        # Healing Invocation
        if invocation < 100:
            gap = 100 - invocation
            low_invocation = [r for r in non_total_rows if safe_val(r, 'Invocation %', 0) < 80]
            review_parts.append(f"Healing invocation at {invocation:.1f}% (target 100%) indicates incomplete healing chains.")
            recommendations.append({
                "priority": 2,
                "category": "Healing",
                "title": "Complete Healing Chain Invocation",
                "detail": f"Current: {invocation:.1f}% | Gap: {gap:.1f}pp | {len(low_invocation)} territories below 80%",
                "action": "Add super().heal_repository() calls to agents that override heal_repository().",
                "impact": "High - Ensures healing propagates through MRO chain."
            })
        
        # MCP Hardening
        if mcp_hardened < 100:
            gap = 100 - mcp_hardened
            unhardened = [r for r in non_total_rows if safe_val(r, 'Hardened %', 0) < 100]
            review_parts.append(f"MCP hardening at {mcp_hardened:.1f}% (target 100%) exposes tool boundaries.")
            recommendations.append({
                "priority": 3,
                "category": "Security",
                "title": "Complete MCP Hardening",
                "detail": f"Current: {mcp_hardened:.1f}% | Gap: {gap:.1f}pp | {len(unhardened)} territories incomplete",
                "action": "Apply MCPHardenedMixin to all agents touching external APIs or tools.",
                "impact": "Critical - Prevents injection and boundary violations."
            })
        
        # Complexity
        high_cc_territories = [r for r in non_total_rows if safe_val(r, 'Avg CC', 0) > 15]
        if high_cc_territories:
            avg_cc = sum(safe_val(r, 'Avg CC', 0) for r in high_cc_territories) / len(high_cc_territories)
            recommendations.append({
                "priority": 4,
                "category": "Maintainability",
                "title": "Reduce Cyclomatic Complexity",
                "detail": f"{len(high_cc_territories)} territories have Avg CC >15 (avg: {avg_cc:.1f})",
                "action": "Refactor complex methods into smaller primitives. Target CC ≤10.",
                "impact": "Medium - Reduces bug density and improves testability."
            })
        
        # Typing
        if typed_pct < 100:
            gap = 100 - typed_pct
            recommendations.append({
                "priority": 5,
                "category": "Code Quality",
                "title": "Complete Type Annotations",
                "detail": f"Current: {typed_pct:.1f}% | Gap: {gap:.1f}pp",
                "action": "Add type hints to function parameters and return types.",
                "impact": "Medium - Enables static analysis and IDE support."
            })
        
        # Documentation
        if documented_pct < 100:
            gap = 100 - documented_pct
            recommendations.append({
                "priority": 6,
                "category": "Code Quality",
                "title": "Complete Documentation",
                "detail": f"Current: {documented_pct:.1f}% | Gap: {gap:.1f}pp",
                "action": "Add docstrings to all public methods and classes.",
                "impact": "Medium - Reduces hallucinated tool usage by constraining search space."
            })
        
        # Format recommendations for display
        formatted_recs = []
        for i, rec in enumerate(sorted(recommendations, key=lambda x: x['priority']), 1):
            formatted_recs.append(
                f"{i}. {rec['title']}<br>"
                f"<span style='color:#666'>{rec['detail']}</span><br>"
                f"<b>Action:</b> {rec['action']}<br>"
                f"<span style='color:#059669'><b>Impact:</b> {rec['impact']}</span>"
            )
        
        return {
            "review": " ".join(review_parts),
            "macro_observations": macro_observations,
            "recommendations": formatted_recs[:10]
        }
    
    def run(self, dashboard_data: List[Dict[str, Any]]) -> Dict[str, Any]:
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

    def heal_repository(self, dry_run: bool = True, **kwargs) -> Dict[str, int]:
        """Invoke healing chain via super()."""
        return super().heal_repository(dry_run=dry_run, **kwargs)
