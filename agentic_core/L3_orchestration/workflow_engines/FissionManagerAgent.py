from __future__ import annotations

"""
[PHASE 14 REFACTOR] FissionManagerAgent.
STRICT COMPLIANCE: No direct SDK imports. Uses SovereignLLMGateway.
"""
import json
import logging
import os
from dataclasses import dataclass

from agentic_core.base_agents.atomic_execution_mixin import atomic_execution_mixin
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.base_agents.subatomic_testing_mixin import subatomic_testing_mixin

Logger = logging.getLogger(__name__)


@dataclass
class FissionResult:
    triggered: bool
    reason: str
    new_files: dict[str, str]
    original_file: str
    success: bool
    error_message: str | None = None


(AtomicExecutionMixin,)


class FissionManagerAgent(SubatomicTestingMixin, SovereignBaseAgent):
    """L3 Orchestration Layer: Atomic Fission via Gateway."""

    def __init__(self, line_limit: int = 800, deletion_guardrail: int = 110, max_rounds: int = 3) -> None:
        super().__init__()
        self.line_limit = line_limit
        self.deletion_guardrail = deletion_guardrail
        self.max_rounds = max_rounds

    async def execute_fission(self, file_path: str, content: str, reason: str) -> FissionResult:
        Logger.info(f"FISSION TRIGGERED: {file_path} ({reason})")

        prompt = self._get_fission_prompt(file_path, content)

        try:
            # [PHASE 14] Native Gateway Call with Phase 13 Thinking Config
            response = await self.llm_generate(
                prompt,
                provider="google",
                model=os.getenv("GEMINI_PRO_MODEL", "gemini-2.5-pro"),
                generation_config={"response_mime_type": "application/json", "temperature": 0.2},
            )

            new_files = self._parse_fission_response(response["content"], file_path)

            if new_files:
                return FissionResult(True, reason, new_files, file_path, True)
            return FissionResult(True, reason, {}, file_path, False, "Empty response")

        except Exception as e:
            Logger.error(f"Fission failed: {e}")
            return FissionResult(True, reason, {}, file_path, False, str(e))

    def _get_fission_prompt(self, file_name: str, content: str) -> str:
        return f"ATOMIC FISSION REQUEST: Split {file_name} into 3 logical sub-modules.\nReturn ONLY JSON mapping filenames to content.\n\nCODE:\n{content[:4000]}..."

    def _parse_fission_response(self, text: str, original_file: str) -> dict[str, str]:
        try:
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            return json.loads(text)
        except Exception as e:
            Logger.warning(f"Fission parse failed: {e}")
            return {}

    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """
        Heal violations detected by FissionManagerAgent.

        Args:
            violation: Dictionary containing violation details with keys:
                - file: Path to the file with the violation
                - type: Type of violation detected
                - message: Description of the violation

        Returns:
            Dictionary with keys:
                - status: 'success', 'partial_success', 'failed', or 'skipped'
                - details: Human-readable summary
                - artifacts: List of modified files
                - errors: List of error messages
        """
        violation.get("file") or violation.get("file_path")
        violation_type = violation.get("type", "unknown")

        # Default implementation - FissionManagerAgent manages code fission
        try:
            return {
                "status": "skipped",
                "details": f"FissionManagerAgent heal() not yet implemented for {violation_type}",
                "artifacts": [],
                "errors": [],
            }
        except Exception as e:
            return {
                "status": "failed",
                "details": f"FissionManagerAgent heal() failed: {str(e)}",
                "artifacts": [],
                "errors": [str(e)],
            }
