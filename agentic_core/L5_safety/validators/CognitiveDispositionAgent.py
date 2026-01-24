from __future__ import annotations

"""
[PHASE 15 REFACTOR] Cognitive Disposition Agent.
STRICT COMPLIANCE: Native Sovereign Capabilities.
"""

from pathlib import Path
from dataclasses import dataclass
import json
import logging

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.base_agents.subatomic_testing_mixin import SubatomicTestingMixin

Logger = logging.getLogger(__name__)


@dataclass
class DispositionDecision:
    action: str
    target_path: str | None = None
    reason: str = ""
    confidence: float = 0.0


class CognitiveDispositionAgent(SubatomicTestingMixin, SovereignBaseAgent):
    """AI-Powered Architectural Triage Agent via Sovereign Gateway."""

    def __init__(self, project_root: Path | None = None, confidence_threshold: float = 0.8):
        super().__init__()
        self.project_root = project_root or Path.cwd()
        self.confidence_threshold = confidence_threshold

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

        cache_key = f"cda:{file_path.name}:{violation_type}"
        cached = self.cache_get(cache_key)
        if cached:
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

            await self.cache_set(cache_key, decision.__dict__, ttl=3600)

            return decision

        except Exception as e:
            Logger.error(f"CDA Analysis failed: {e}")
            return DispositionDecision(action="MANUAL_REVIEW", reason=f"Error: {e}")

    def _build_prompt(self, file_path: Path, violation_type: str, context: dict) -> str:
        return f"""
        Analyze File: {file_path.name}
        Violation: {violation_type}
        Context: {json.dumps(context)}

        Determine if this file should be MOVED, ARCHIVED, or IGNORED based on {json.dumps(self.layer_map)}.
        Return JSON.
        """
