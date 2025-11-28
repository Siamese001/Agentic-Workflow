"""Safety stack shim for v10.8."""

from __future__ import annotations

import json
from typing import Any, Dict

from agent_stacks_v10_8.components.safety import (
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

    async def constitutional_review_from_state_async(
        self, state: Dict[str, Any], workflow_id: str
    ) -> Dict[str, Any]:
        """Extract the final resume payload using the legacy fallback chain."""

        artifacts_bucket = state.get("artifacts", {})
        final_resume: Any = None
        if isinstance(artifacts_bucket, dict):
            inner = artifacts_bucket.get("artifacts", {})
            if isinstance(inner, dict):
                final_resume = inner.get("final_resume")

        if final_resume is None:
            draft_state = state.get("draft", {})
            if isinstance(draft_state, dict):
                final_resume = draft_state.get("final_draft")
                if final_resume is None:
                    sections = draft_state.get("sections", {})
                    if isinstance(sections, dict):
                        summary = sections.get("summary", {})
                        if isinstance(summary, dict):
                            final_resume = summary.get("draft")

        if final_resume is None:
            final_resume = state.get("resume", {}).get("master_resume", {})

        draft_text = json.dumps(final_resume)
        result = await self.run_constitutional_review_async(
            draft_text,
            workflow_id or state.get("metadata", {}).get("workflow_id", ""),
        )
        payload = result.model_dump() if hasattr(result, "model_dump") else result
        return {"qa": {"constitutional_review": payload}}
