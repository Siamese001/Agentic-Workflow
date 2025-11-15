"""Safety stack shim for v10.8."""

from __future__ import annotations

from typing import Any, Dict

from stacks_v10_7.safety import (
    BiasDetectorAgent,
    ConstitutionalReviewerAgent,
    PIISanitizerAgent,
    PromptInjectionDetectorAgent,
)


class SafetyStackV10_8:
    """Wrapper that exposes safety-only capabilities."""

    def __init__(self, context: Any, debug_mode: bool = False) -> None:
        self.context = context
        self.debug_mode = debug_mode
        self._pii_sanitizer = PIISanitizerAgent(context, debug_mode)
        self._bias_detector = BiasDetectorAgent(context, debug_mode)
        self._prompt_injection_detector = PromptInjectionDetectorAgent(
            context, debug_mode
        )
        self._constitutional_reviewer = ConstitutionalReviewerAgent(
            context, debug_mode
        )

    def sanitize_resume(self, resume: Dict[str, Any]) -> Dict[str, Any]:
        """Run the legacy PII sanitizer."""

        return self._pii_sanitizer.run(resume)

    def detect_bias(self, text: str, workflow_id: str = "") -> Dict[str, Any]:
        """Run the local bias detector."""

        return self._bias_detector.run(text, workflow_id)

    async def detect_prompt_injection_async(
        self, user_input: str, workflow_id: str
    ) -> Dict[str, Any]:
        """Delegate to the v10.7 prompt injection detector."""

        return await self._prompt_injection_detector.run_async(user_input, workflow_id)

    async def run_constitutional_review_async(
        self, final_draft: str, workflow_id: str
    ) -> Any:
        """Delegate final constitutional review without changing behavior."""

        return await self._constitutional_reviewer.run_async(final_draft, workflow_id)
