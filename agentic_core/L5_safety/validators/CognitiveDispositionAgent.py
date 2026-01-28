from __future__ import annotations

"""
[PHASE 15 REFACTOR] Cognitive Disposition Agent.
STRICT COMPLIANCE: Native Sovereign Capabilities.

PURPOSE:
- AI-powered architectural triage via Sovereign Gateway
- Enhanced decision making for SSOT execution
- Cognitive analysis of structural violations
- Intelligent file disposition recommendations

INTEGRATION:
- Used by execute_ssot.py with --enable-cda flag
- Enhances AutonomousDecisionEngine with cognitive insights
- Provides 15% cognitive factor in confidence calculations

STATUS: PRODUCTION READY - Keep and enhance
"""

from pathlib import Path
from dataclasses import dataclass
import json
import logging

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

Logger = logging.getLogger(__name__)


@dataclass
class DispositionDecision:
    action: str
    target_path: str | None = None
    reason: str = ""
    confidence: float = 0.0


class CognitiveDispositionAgent(SovereignBaseAgent):
    """AI-Powered Architectural Triage Agent via Sovereign Gateway.
    
    DEPRECATION STATUS: KEEP - This agent is actively used and valuable.
    
    USAGE:
    - Integrated in execute_ssot.py with --enable-cda flag
    - Enhances decision making with cognitive analysis
    - Provides intelligent violation triage
    
    FUTURE ENHANCEMENTS:
    - Add more sophisticated violation pattern recognition
    - Integrate with more LLM providers
    - Add learning from historical dispositions
    - Expand beyond file-level to architectural analysis
    """

    def __init__(self, project_root: Path | None = None, confidence_threshold: float = 0.75):
        super().__init__()
        self.project_root = project_root or Path.cwd()
        self.confidence_threshold = confidence_threshold
        
        # [ENHANCEMENT] Track analytics for future improvements
        self.analytics = {
            "analyses_performed": 0,
            "cache_hits": 0,
            "average_confidence": 0.0,
            "action_distribution": {}
        }

        self.layer_map = {
            "L0_maintenance": "Maintenance",
            "L1_cognition": "Cognitive",
            "L2_execution": "Execution",
            "L3_orchestration": "Orchestration",
            "L4_state": "State",
            "L5_safety": "Safety",
            "L6_observability": "observability",
        }

    async def analyze_violation_async(
        self, file_path: Path, violation_type: str, context: dict = None
    ) -> DispositionDecision:
        """Analyze violation using Native LLM Gateway."""
        context = context or {}
        
        # [ANALYTICS] Track usage
        self.analytics["analyses_performed"] += 1

        cache_key = f"cda:{file_path.name}:{violation_type}"
        cached = self.cache_get(cache_key)
        if cached:
            self.analytics["cache_hits"] += 1
            return DispositionDecision(**cached)

        prompt = self._build_prompt(file_path, violation_type, context)

        try:
            response = await self.llm_generate(
                prompt,
                provider="google",
                generation_config={"response_mime_type": "application/json", "temperature": 0.1},
            )

            try:
                data = json.loads(response["content"])
            except:
                text = response["content"].replace("```json", "").replace("```", "").strip()
                data = json.loads(text)

            decision = DispositionDecision(
                action=data.get("action", "MANUAL_REVIEW"),
                target_path=data.get("target_path"),
                reason=data.get("reason", "Parsed from LLM"),
                confidence=float(data.get("confidence", 0.0)),
            )
            
            # [ANALYTICS] Track action distribution and confidence
            action = decision.action
            self.analytics["action_distribution"][action] = self.analytics["action_distribution"].get(action, 0) + 1
            
            # Update average confidence
            total = self.analytics["analyses_performed"]
            current_avg = self.analytics["average_confidence"]
            self.analytics["average_confidence"] = ((current_avg * (total - 1)) + decision.confidence) / total

            await self.cache_set(cache_key, decision.__dict__, ttl=3600)

            return decision

        except Exception as e:
            Logger.error(f"CDA Analysis failed: {e}")
            return DispositionDecision(action="MANUAL_REVIEW", reason=f"Error: {e}")
    
    def get_analytics(self) -> dict:
        """Get usage analytics for the CognitiveDispositionAgent.
        
        Returns:
            dict: Analytics data including usage statistics and performance metrics
        """
        return {
            **self.analytics,
            "cache_hit_rate": self.analytics["cache_hits"] / max(self.analytics["analyses_performed"], 1),
            "project_root": str(self.project_root),
            "confidence_threshold": self.confidence_threshold,
        }

    def _build_prompt(self, file_path: Path, violation_type: str, context: dict) -> str:
        return f"""
        Analyze File: {file_path.name}
        Violation: {violation_type}
        Context: {json.dumps(context)}

        Determine if this file should be MOVED, ARCHIVED, or IGNORED based on {json.dumps(self.layer_map)}.
        Return JSON.
        """
