"""Safety guard stack agents - LIC Sovereign Specialists."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any

from apps_lic.shared.core.agent_base import LICAgentBase
from apps_lic.shared.core.immutable_buffer import ImmutableStagingBuffer
from apps_lic.shared.core.trace_registry import TraceRegistry
from pydantic import BaseModel, Field


def track_metrics(name):
    """Stub decorator for track_metrics - TODO: Replace with sovereign equivalent"""

    def decorator(func):
        return func

    return decorator


@dataclass
class PIISanitizerSpecialist(LICAgentBase, SubatomicTestingMixin):
    """Performs local PII detection using regex heuristics."""

    # Sovereign Configuration
    pii_patterns: dict[str, Any] = field(
        default_factory=lambda: {
            "EMAIL": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
            "PHONE": re.compile(r"\b(?:\+?1[ -]?)?\(?\d{3}\)?[ -]?\d{3}[ -]?\d{4}\b"),
            "NAME": re.compile(r"\b[A-Z][a-z]+ [A-Z][a-z]+\b"),
        }
    )

    def __post_init__(self) -> None:
        """Initialize Sovereign Capabilities."""
        super().__post_init__()

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
        for pii_type, pattern in self.pii_patterns.items():
            text = pattern.sub(f"[{pii_type}_REDACTED]", text)
        return text


@dataclass
class BiasDetectorSpecialist(LICAgentBase, SubatomicTestingMixin):
    """LIC Sovereign Bias Detector - Runs local bias detection with dynamic constitution rules."""

    # Sovereign Configuration
    name: str = "BiasDetectorSpecialist"
    sensitivity_level: float = 0.85
    prohibited_terms: list[str] = field(
        default_factory=lambda: ["guaranteed", "unlimited", "risk-free"]
    )

    def __post_init__(self) -> None:
        """Initialize Sovereign Capabilities."""
        super().__post_init__()

    def _process(self, buffer: ImmutableStagingBuffer, registry: TraceRegistry) -> None:
        """Execute bias detection on buffer content."""
        registry.add_trace("PHASE_START", {"agent": self.__class__.__name__})

        mission_input = buffer.read("mission_input") or {}
        text = mission_input.get("text", "")

        # Sovereign bias detection using configured terms
        patterns_found = [term for term in self.prohibited_terms if term.lower() in text.lower()]

        # Add bias patterns detection
        bias_patterns = ["always", "never", "everyone", "no one"]
        additional_patterns = [p for p in bias_patterns if p.lower() in text.lower()]
        patterns_found.extend(additional_patterns)

        result = {
            "bias_detected": len(patterns_found) > 0,
            "patterns": patterns_found,
        }

        buffer.write_once("bias_detection_result", result)
        registry.add_trace("PHASE_COMPLETE", {"agent": self.__class__.__name__, "result": result})

    def scan_content(self, text: str) -> dict[str, Any]:
        """Public interface for bias scanning - used in simulation."""
        self.log_info(f"Scanning content for bias: '{text[:50]}...'")

        # Sovereign bias detection using configured terms
        patterns_found = [term for term in self.prohibited_terms if term.lower() in text.lower()]

        # Add bias patterns detection
        bias_patterns = ["always", "never", "everyone", "no one"]
        additional_patterns = [p for p in bias_patterns if p.lower() in text.lower()]
        patterns_found.extend(additional_patterns)

        result = {
            "has_bias": len(patterns_found) > 0,
            "bias_detected": len(patterns_found) > 0,  # Keep for compatibility
            "patterns": patterns_found,
            "sensitivity_level": self.sensitivity_level,
        }

        self.log_info(f"Bias scan complete: {result}")
        return result


@dataclass
class PromptInjectionDetectorSpecialist(LICAgentBase, SubatomicTestingMixin):
    """Detects prompt-injection attacks."""

    # Sovereign Configuration
    detection_threshold: float = 0.8
    attack_patterns: list[str] = field(
        default_factory=lambda: ["ignore previous instructions", "system prompt", "jailbreak"]
    )

    def __post_init__(self) -> None:
        """Initialize Sovereign Capabilities."""
        super().__post_init__()

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


@dataclass
class ConstitutionalReviewerAgent(LICAgentBase, SubatomicTestingMixin):
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
