from __future__ import annotations

"""
InputValidationGuardrail: Consolidated input validation with composable rules.
Merges: input_validator, PII_Sanitizer, PromptInjectionDetector, BiasDetector, safety_guardrail
"""

import logging
import re
from dataclasses import dataclass, field
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L5_safety.utils.decorators_util import standard_heal

logger = logging.getLogger(__name__)


@dataclass
class InputValidationGuardrail(SovereignBaseAgent):
    """
    Consolidated input validation with composable rule sets.
    Handles: PII detection, prompt injection, bias detection, format validation.
    """

    debug_mode: bool = False
    enabled_rules: list[str] = field(
        default_factory=lambda: [
            "pii_detection",
            "prompt_injection",
            "bias_detection",
            "format_validation",
        ],
    )

    def __post_init__(self):
        self.name = "InputValidationGuardrail"
        self.validation_count = 0
        self.violations_found = 0

    async def validate(self, input_text: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """Validate input against enabled rules."""
        logger.info(f"[{self.name}] Validating input")

        result = {
            "valid": True,
            "violations": [],
            "rules_applied": [],
        }

        try:
            for rule in self.enabled_rules:
                rule_result = await self._apply_rule(rule, input_text, context)
                result["rules_applied"].append(rule)

                if not rule_result.get("valid"):
                    result["valid"] = False
                    result["violations"].extend(rule_result.get("violations", []))

            self.validation_count += 1
            if not result["valid"]:
                self.violations_found += 1

            return result

        except Exception as e:
            logger.error(f"[{self.name}] Validation error: {e}")
            return {
                "valid": False,
                "violations": [{"type": "validation_error", "message": str(e)}],
                "error": str(e),
            }

    async def _apply_rule(self, rule: str, input_text: str, context: dict | None = None) -> dict[str, Any]:
        """Apply a specific validation rule."""
        if rule == "pii_detection":
            return self._detect_pii(input_text)
        elif rule == "prompt_injection":
            return self._detect_prompt_injection(input_text)
        elif rule == "bias_detection":
            return self._detect_bias(input_text)
        elif rule == "format_validation":
            return self._validate_format(input_text)
        return {"valid": True}

    def _detect_pii(self, text: str) -> dict[str, Any]:
        """Detect personally identifiable information."""
        violations = []

        # Email pattern
        if re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", text):
            violations.append(
                {
                    "type": "pii_email",
                    "severity": "high",
                    "message": "Email address detected in input",
                },
            )

        # Phone pattern
        if re.search(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b", text):
            violations.append(
                {
                    "type": "pii_phone",
                    "severity": "high",
                    "message": "Phone number detected in input",
                },
            )

        # SSN pattern
        if re.search(r"\b\d{3}-\d{2}-\d{4}\b", text):
            violations.append(
                {
                    "type": "pii_ssn",
                    "severity": "critical",
                    "message": "Social security number detected in input",
                },
            )

        return {
            "valid": len(violations) == 0,
            "violations": violations,
        }

    def _detect_prompt_injection(self, text: str) -> dict[str, Any]:
        """Detect prompt injection attempts."""
        violations = []
        injection_patterns = [
            r"ignore.*previous.*instruction",
            r"forget.*everything",
            r"you.*are.*now",
            r"developer.*mode",
            r"jailbreak",
        ]

        for pattern in injection_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                violations.append(
                    {
                        "type": "prompt_injection",
                        "severity": "high",
                        "message": f"Potential prompt injection detected: {pattern}",
                    },
                )

        return {
            "valid": len(violations) == 0,
            "violations": violations,
        }

    def _detect_bias(self, text: str) -> dict[str, Any]:
        """Detect biased language patterns."""
        violations = []
        bias_patterns = {
            r"always|never|all|none": "absolute_language",
            r"should|must|have to": "prescriptive_language",
        }

        for pattern, bias_type in bias_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                violations.append(
                    {
                        "type": f"bias_{bias_type}",
                        "severity": "low",
                        "message": f"Potential bias detected: {bias_type}",
                    },
                )

        return {
            "valid": len(violations) == 0,
            "violations": violations,
        }

    def _validate_format(self, text: str) -> dict[str, Any]:
        """Validate input format."""
        violations = []

        if not text or len(text.strip()) == 0:
            violations.append(
                {
                    "type": "empty_input",
                    "severity": "medium",
                    "message": "Input is empty",
                },
            )

        if len(text) > 1000000:
            violations.append(
                {
                    "type": "oversized_input",
                    "severity": "high",
                    "message": "Input exceeds maximum length",
                },
            )

        return {
            "valid": len(violations) == 0,
            "violations": violations,
        }

    def _run_self_tests(self) -> bool:
        """Validate agent structure."""
        assert hasattr(self, "name"), "Missing name"
        assert hasattr(self, "enabled_rules"), "Missing enabled_rules"
        return True

    @standard_heal
    def heal_repository(self, dry_run: bool = True, **kwargs) -> dict[str, Any]:
        """Repository healing with parent chain invocation."""
        result = super().heal_repository(dry_run=dry_run, **kwargs)
        return {"violations_fixed": 0, "skipped": 0, "parent": result}

    def heal(self, violation: dict) -> dict:
        """Heal input validation violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (pii, injection, bias, format)
                - input: Input that caused the violation
                - severity: Severity level

        Returns:
            Dictionary with healing results following standard_heal format.
        """
        return {
            "violations_fixed": 0,
            "violations_found": 1,
            "errors": 0,
            "skipped": 1,
            "reason": "Input validation violations require content revision",
        }
