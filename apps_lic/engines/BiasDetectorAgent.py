"""Safety guard stack agents - V2.5 Sovereign Specialists."""

from __future__ import annotations

import json
import re
from typing import Any

from pydantic import BaseModel, Field

from apps_lic.shared.v2_patterns.agent_base import V2AgentBase
from apps_lic.shared.v2_patterns.mixins import SubatomicTestingMixin, MCPHardenedMixin, HealerMixin
from apps_lic.shared.v2_patterns.immutable_buffer import ImmutableStagingBuffer
from apps_lic.shared.v2_patterns.trace_registry import TraceRegistry


class PIISanitizerSpecialist(V2AgentBase, SubatomicTestingMixin, MCPHardenedMixin, HealerMixin):
    """Performs local PII detection using regex heuristics."""

    PII_PATTERNS = {
        "EMAIL": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
        "PHONE": re.compile(r"\b(?:\+?1[ -]?)?\(?\d{3}\)?[ -]?\d{3}[ -]?\d{4}\b"),
        "NAME": re.compile(r"\b[A-Z][a-z]+ [A-Z][a-z]+\b"),
    }

    @track_metrics("run_pii_sanitizer")
    def run(self, resume: dict[str, Any]) -> dict[str, Any]:
        self.log_info("Sanitizing PII (local regex processing)...")
        sanitized_resume = json.loads(json.dumps(resume))

        def sanitize_node(node: Any) -> Any:
            if isinstance(node, dict):
                return {k: sanitize_node(v) for k, v in node.items()}
            if isinstance(node, list):
                return [sanitize_node(item) for item in node]
            if isinstance(node, str):
                return self._sanitize_text(node)
            return node

        sanitized = sanitize_node(sanitized_resume)
        self.log_info("PII sanitization complete.")
        return sanitized

    def _sanitize_text(self, text: str) -> str:
        for pii_type, pattern in self.PII_PATTERNS.items():
            text = pattern.sub(f"[{pii_type}_REDACTED]", text)
        return text


class BiasDetectorSpecialist(V2AgentBase, SubatomicTestingMixin, MCPHardenedMixin, HealerMixin):
    """V2.5 Sovereign Bias Detector - Runs local bias detection with dynamic constitution rules."""

    def _process(self, buffer: ImmutableStagingBuffer, registry: TraceRegistry) -> None:
        """Execute bias detection on buffer content."""
        registry.add_trace("PHASE_START", {"agent": self.__class__.__name__})

        mission_input = buffer.read("mission_input") or {}
        text = mission_input.get("text", "")

        # Simple bias pattern detection
        bias_patterns = ["always", "never", "everyone", "no one"]
        patterns_found = [p for p in bias_patterns if p.lower() in text.lower()]

        result = {
            "bias_detected": len(patterns_found) > 0,
            "patterns": patterns_found,
        }

        buffer.write_once("bias_detection_result", result)
        registry.add_trace("PHASE_COMPLETE", {"agent": self.__class__.__name__, "result": result})


class PromptInjectionDetectorSpecialist(
    V2AgentBase, SubatomicTestingMixin, MCPHardenedMixin, HealerMixin
):
    """Detects prompt-injection attacks."""

    class PIDetectionOutput(BaseModel):
        injection_detected: bool = Field(..., description="True if an attack was detected")
        reason: str = Field(..., description="Explanation for the detection")
        confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in the detection")

    @track_metrics("run_pi_detector")
    async def run_async(self, user_input: str, workflow_id: str) -> dict[str, Any]:
        self.log_info("Detecting prompt injection...")

        if not self.config.agent_stacks.enable_prompt_injection_detection:
            self.log_warning("Prompt injection detection is disabled.")
            return {
                "injection_detected": False,
                "reason": "Detector disabled",
                "confidence": 0.0,
            }

        client = self.get_model_client("prompt_injection_model")
        prompt_template = self.prompt_manager.get_template("prompt_injection_detector")

        prompt = await _format_prompt_with_defaults(
            prompt_template,
            {"user_input": user_input},
            self.budget_manager,
            client.goal_state,
            client.top_failures,
        )

        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=self.config.model_config.prompt_injection_model.temperature,
            response_format="json_object",
        )

        validated_output, error = self.validator.validate(
            response["content"],
            self.PIDetectionOutput,
        )
        if error:
            self.log_error(f"PromptInjectionDetector failed validation: {error}")
            return {
                "injection_detected": True,
                "reason": f"Detector validation failed: {error}",
                "confidence": 1.0,
            }

        if validated_output.injection_detected:
            self.log_warning(
                f"PROMPT INJECTION DETECTED (Confidence: {validated_output.confidence}): {validated_output.reason}"
            )

        return validated_output.model_dump()


class ConstitutionalReviewerAgent(BaseAgent):
    """Performs final constitutional review of the output."""

    @track_metrics("run_constitutional_review")
    async def run_async(
        self,
        final_draft: str,
        workflow_id: str,
    ) -> ConstitutionalReviewResult:
        self.log_info("Running final constitutional review...")

        if not self.config.agent_stacks.enable_constitutional_review:
            self.log_warning("Constitutional review is disabled. Passing by default.")
            return ConstitutionalReviewResult(
                review_passed=True,
                violations_found=[],
                feedback="Review disabled",
            )

        client = self.get_model_client("constitutional_review_model")
        prompt_template = self.prompt_manager.get_template("constitutional_review")

        rules = self.context.rules_loader.get_constitution_rules()
        constitution_text = json.dumps(rules)

        prompt = await _format_prompt_with_defaults(
            prompt_template,
            {"final_draft": final_draft, "constitution": constitution_text},
            self.budget_manager,
            client.goal_state,
            client.top_failures,
        )

        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=self.config.model_config.constitutional_review_model.temperature,
            response_format="json_object",
        )

        validated_output, error = self.validator.validate(
            response["content"],
            ConstitutionalReviewResult,
        )
        if error:
            self.log_error(
                f"ConstitutionalReviewer failed validation: {error}. Failing open (passing draft)."
            )
            return ConstitutionalReviewResult(
                review_passed=True,
                violations_found=["VALIDATION_ERROR"],
                feedback=error,
            )

        if not validated_output.review_passed:
            self.log_warning(f"CONSTITUTIONAL REVIEW FAILED: {validated_output.violations_found}")

        return validated_output
