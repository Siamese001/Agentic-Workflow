"""
Strategic Recommendation Agent
L3 Orchestration agent: Reviews full autonomy report data and generates high-signal strategic recommendations.

Restored: 2026-01-13 | Version: 2.0.0
Original: archives/unmapped_drift/20260107/agentic_core/L3_orchestration/strategic_recommendation/

Purpose:
- Analyzes dashboardData (territories, metrics, gaps) for cross-layer patterns.
- Outputs structured JSON with:
  - Strategic review paragraph
  - Top 5-15 prioritized recommendations (broader than per-territory)
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
    
    def __init__(self, project_root: Optional[Path] = None, llm_client: Any = None):
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
        
        Args:
            dashboard_data: Dashboard metrics
            
        Returns:
            Dict with review and recommendations
        """
        # Helper for None-safe value extraction
        def safe_val(row: Dict, key: str, default: float = 0) -> float:
            val = row.get(key, default)
            return val if val is not None else default
        
        total_row = next((r for r in dashboard_data if r.get('Territory') == 'TOTAL'), {})
        recommendations = []
        
        # Analyze key metrics (handle None values)
        health = safe_val(total_row, 'Health', 0)
        invocation = safe_val(total_row, 'Invocation %', 0)
        mcp_hardened = safe_val(total_row, 'Hardened %', 0)
        test_coverage = safe_val(total_row, 'Test %', 0)
        heal_cap = safe_val(total_row, 'Heal Cap %', 0)
        total_agents = total_row.get('Total', 0) or 0
        
        # Generate review
        review = f"Portfolio health at {health:.1f}% with {total_agents} agents. "
        
        if invocation < 60:
            review += f"Critical invocation gap at {invocation:.1f}% (target 100%) indicates healing protocols are not being actively used. "
            recommendations.append("1. Boost Healing Invocation<br>Add super().heal_repository() calls in except blocks across agents with missing invocation. Target: +40% invocation boost.")
        
        if mcp_hardened < 80:
            review += f"MCP hardening at {mcp_hardened:.1f}% (target 100%) exposes tool boundaries to injection risks. "
            recommendations.append("2. Harden External Tool Boundaries<br>Apply MCPHardenedMixin and @hardened decorators to all agents touching external APIs. Target: 100% coverage.")
        
        if test_coverage < 90:
            review += f"Test coverage at {test_coverage:.1f}% (target 95%) increases regression risk. "
            recommendations.append("3. Expand Test Coverage<br>Add unit tests for core behaviors and regression baselines. Focus on agents with 0% coverage first.")
        
        if heal_cap < 100:
            recommendations.append("4. Complete Healing Capability Rollout<br>Add HealerMixin to all agents. Enables standardized self-recovery tools across the portfolio.")
        
        # Add complexity recommendations
        high_cc_territories = [r for r in dashboard_data 
                             if r.get('Avg CC', 0) > 15 and r['Territory'] != 'TOTAL']
        if high_cc_territories:
            recommendations.append("5. Reduce Cyclomatic Complexity<br>Refactor methods with CC>15 into smaller primitives. Focus on L5 validators and L3 orchestrators first.")
        
        # Add layer-specific recommendations
        l5_rows = [r for r in dashboard_data if 'L5' in r.get('Territory', '')]
        if l5_rows and any(r.get('Hardened %', 0) < 80 for r in l5_rows):
            recommendations.append("6. Strengthen L5 Safety Layer<br>L5 is the last line of defense. Ensure 100% MCP hardening and comprehensive validation chains.")
        
        l1_rows = [r for r in dashboard_data if 'L1' in r.get('Territory', '')]
        if l1_rows and any(r.get('Test %', 0) < 80 for r in l1_rows):
            recommendations.append("7. Fortify L1 Cognition Testing<br>Cognitive layer brittleness cascades downstream. Add tests for reasoning modules and chain-of-thought proxies.")
        
        # Infrastructure recommendations
        infra_rows = [r for r in dashboard_data if 'Infrastructure' in r.get('Territory', '')]
        if infra_rows:
            recommendations.append("8. Standardize Infrastructure Primitives<br>Implement circuit breakers, retries, rate limits, and feature flags across all layers.")
        
        # Observability
        if total_row.get('Observable %', 0) < 90:
            recommendations.append("9. Enhance Observability<br>Add structured logging, metrics, and tracing to enable production debugging and failure analysis.")
        
        # Documentation
        if total_row.get('Documented %', 0) < 80:
            recommendations.append("10. Improve Documentation<br>Add docstrings to public methods. Clear interfaces reduce hallucinated tool usage by constraining search space.")
        
        # Ensure we have at least 5 recommendations
        if len(recommendations) < 5:
            recommendations.append("5. Maintain Momentum<br>Continue systematic improvements across healing, testing, and hardening dimensions.")
        
        return {
            "review": review.strip(),
            "recommendations": recommendations[:10]
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
