from __future__ import annotations

from agentic_core.L2_execution.tools import write_gateway as _wg

"\n[PHASE 15 REFACTOR] Cognitive Disposition Agent.\nSTRICT COMPLIANCE: Native Sovereign Capabilities.\n\nPURPOSE:\n- AI-powered architectural triage via Sovereign Gateway\n- Enhanced decision making for SSOT execution\n- Cognitive analysis of structural violations\n- Intelligent file disposition recommendations\n\nINTEGRATION:\n- Used by execute_ssot.py with --enable-cda flag\n- Enhances AutonomousDecisionEngine with cognitive insights\n- Provides 15% cognitive factor in confidence calculations\n\nSTATUS: PRODUCTION READY - Keep and enhance\n"
import json
import logging
from dataclasses import dataclass
from pathlib import Path

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L5_safety.config.structure_blueprint import LAYER_ROOTS

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

    # guardian: allow-magic-config
    def __init__(self, project_root: Path | None = None, confidence_threshold: float = 0.75):
        super().__init__()
        self.project_root = project_root or Path.cwd()
        self.confidence_threshold = confidence_threshold
        self.analytics = {
            "analyses_performed": 0,
            "cache_hits": 0,
            "average_confidence": 0.0,
            "action_distribution": {},
        }
        self.layer_map = {
            layer: layer.split("_", 1)[1].replace("_", " ").title() for layer in sorted(LAYER_ROOTS)
        }

    async def analyze_violation_async(
        self, file_path: Path, violation_type: str, context: dict = None
    ) -> DispositionDecision:
        """Analyze violation using Native LLM Gateway."""
        context = context or {}
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
            # guardian: allow-silent-swallow
            except:
                text = response["content"].replace("```json", "").replace("```", "").strip()
                data = json.loads(text)
            decision = DispositionDecision(
                action=data.get("action", "MANUAL_REVIEW"),
                target_path=data.get("target_path"),
                reason=data.get("reason", "Parsed from LLM"),
                confidence=float(data.get("confidence", 0.0)),
            )
            action = decision.action
            self.analytics["action_distribution"][action] = (
                self.analytics["action_distribution"].get(action, 0) + 1
            )
            total = self.analytics["analyses_performed"]
            current_avg = self.analytics["average_confidence"]
            self.analytics["average_confidence"] = (current_avg * (total - 1) + decision.confidence) / total
            await self.cache_set(cache_key, decision.__dict__, ttl=3600)
            return decision
        # guardian: allow-silent-swallow
        except Exception as e:
            Logger.error(f"CDA Analysis failed: {e}")
            return DispositionDecision(action="MANUAL_REVIEW", reason=f"Error: {e}")

    def analyze_violation(
        self, file_path: Path, violation_type: str, context: dict = None
    ) -> DispositionDecision:
        """Sync wrapper around analyze_violation_async.

        Wave 1 fix: callers should use this instead of asyncio.run() directly.
        """
        import asyncio

        return asyncio.run(self.analyze_violation_async(file_path, violation_type, context or {}))

    async def analyze_violations(self, violations: list, territory: str) -> list[DispositionDecision]:
        """Analyze a list of violations asynchronously.

        Wave 1 fix: this method is called by EnhancedAutonomousDecisionEngine
        but was missing from CognitiveDispositionAgent.
        """
        decisions = []
        for v in violations:
            path_str = v.get("file", v.get("path", ""))
            vtype = v.get("type", "UNKNOWN")
            ctx = {"territory": territory, **{k: v[k] for k in v if k not in ("file", "path", "type")}}
            try:
                decision = await self.analyze_violation_async(
                    file_path=Path(path_str) if path_str else Path("."), violation_type=vtype, context=ctx
                )
                decisions.append(decision)
            # guardian: allow-silent-swallow
            except Exception as _e:
                Logger.warning("[CDA] analyze_violations: skipping %s: %s", path_str, _e)
                decisions.append(DispositionDecision(action="MANUAL_REVIEW", reason=f"Error: {_e}"))
        return decisions

    # guardian: allow-type-erasure
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
        return f"\n        Analyze File: {file_path.name}\n        Violation: {violation_type}\n        Context: {json.dumps(context)}\n\n        Determine if this file should be MOVED, ARCHIVED, or IGNORED based on {json.dumps(self.layer_map)}.\n        Return JSON.\n        "

    # guardian: allow-type-erasure
    def heal(self, violation: dict) -> dict:
        """Heal cognitive disposition violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (cognitive_disposition)
                - path: Path to the violating file
                - context: Additional context for the violation

        Returns:
            Dictionary with healing results following standard_heal format:
                - violations_fixed: Number of violations fixed
                - violations_found: Total violations found
                - errors: Number of errors encountered
                - skipped: Number of violations skipped
        """
        from agentic_core.utils.decorators_compat_util import standard_heal

        @standard_heal
        # guardian: allow-type-erasure
        def _heal_cognitive_disposition(self, violation: dict) -> dict:
            """Internal heal method with standard_heal decorator."""
            path = violation.get("path", "")
            context = violation.get("context", {})
            violation_type = violation.get("type", "cognitive_disposition")
            Logger.info(f"[COGNITIVE] Healing {violation_type} violation at {path}")
            try:
                import asyncio

                file_path = Path(path)
                decision = asyncio.run(self.analyze_violation_async(file_path, violation_type, context))
                if decision.confidence >= self.confidence_threshold:
                    action = decision.action.lower()
                    if action == "archive":
                        from agentic_core.L5_safety.enforcement.archival_gatekeeper_gate import (
                            ArchivalGatekeeper,
                        )

                        archivist = ArchivalGatekeeper(self.project_root)
                        archivist.archive_file(file_path, reason=f"cognitive_disposition: {decision.reason}")
                        Logger.info(f"  Archived {path} based on cognitive analysis")
                        return {"violations_fixed": 1, "violations_found": 1, "errors": 0, "skipped": 0}
                    elif action == "move":
                        target_path = decision.target_path
                        if target_path:
                            target = Path(target_path)
                            _wg.ensure_dir(target.parent)
                            _wg.rename_path(file_path, target)
                            Logger.info(f"  Moved {path} -> {target_path}")
                            return {"violations_fixed": 1, "violations_found": 1, "errors": 0, "skipped": 0}
                        else:
                            Logger.warning("  No target path provided for move action")
                            return {"violations_fixed": 0, "violations_found": 1, "errors": 0, "skipped": 1}
                    elif action == "ignore":
                        Logger.info(f"  Ignoring {path} based on cognitive analysis")
                        return {"violations_fixed": 0, "violations_found": 1, "errors": 0, "skipped": 1}
                    else:
                        Logger.warning(f"  Unknown cognitive action: {action}")
                        return {"violations_fixed": 0, "violations_found": 1, "errors": 0, "skipped": 1}
                else:
                    Logger.warning(f"  Low confidence ({decision.confidence}) - requires manual review")
                    return {"violations_fixed": 0, "violations_found": 1, "errors": 0, "skipped": 1}
            # guardian: allow-silent-swallow
            except Exception as e:
                Logger.error(f"  Error in cognitive healing: {e}")
                return {"violations_fixed": 0, "violations_found": 1, "errors": 1, "skipped": 0}

        return _heal_cognitive_disposition(self, violation)

    # guardian: allow-type-erasure
    def heal_repository(self, *args, **kwargs) -> dict:
        """heal_repository() not implemented for CognitiveDispositionAgent."""
        raise NotImplementedError("heal_repository() not implemented for CognitiveDispositionAgent")
