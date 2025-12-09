"""Layer 5 safety module consolidating safety components."""



from __future__ import annotations
import re
from typing import Any, Dict, List

from injection_output_profiles import DEFAULT_SAFETY_OUTPUT_PROFILE
from l5_policy import (
    PolicyEngine,
    SafetyMode,
    evaluate_routing_permissions,
    permissions as tool_permissions,
)
from prompt_system import DEFAULT_INJECTION_PATTERNS, INSTRUCTIONAL_INJECTION_ALL
from utils_logger import SAFETY_LOG, log_safety_decision
from utils_types import StatePatch

EMAIL_TOKEN = "@"
PHONE_REGEX = re.compile(r"\d{3}-\d{3}-\d{4}")
BIAS_KEYWORDS = ["gender", "race", "ethnicity"]


def detect_pii(text: str) -> Dict[str, object]:
    """Deterministic PII detection based on simple patterns."""

    instances: List[str] = []
    if EMAIL_TOKEN in text:
        instances.append("email-like")
    phone_matches = PHONE_REGEX.findall(text)
    if phone_matches:
        instances.extend(phone_matches)

    return {"pii_found": bool(instances), "instances": instances}


def detect_bias(text: str) -> Dict[str, object]:
    """Deterministic bias detection using keyword scanning."""

    categories = [keyword for keyword in BIAS_KEYWORDS if keyword in text.lower()]
    return {"bias_found": bool(categories), "categories": categories}


class InjectionDetector:
    """Lightweight detector for common prompt injection patterns."""

    def __init__(self) -> None:
        self.patterns: List[str] = DEFAULT_INJECTION_PATTERNS
        self.instructional_types: List[str] = INSTRUCTIONAL_INJECTION_ALL
        self.pattern_taxonomy: Dict[str, str] = {
            "override_system": "SYSTEM_OVERRIDE",
            "ignore_previous_instructions": "IGNORING_SYSTEM",
            "disable_safety": "DISABLE_SAFETY_PROTOCOLS",
            "run_arbitrary_code": "ARBITRARY_CODE_EXECUTION",
        }

    def scan(self, content: str) -> StatePatch:
        """Return a StatePatch flagging detected injection patterns."""

        matches: List[str] = []
        matched_patterns: List[str] = []
        regex_matches: List[str] = []
        lower_content = content.lower()
        for pattern in self.patterns:
            normalized_pattern = pattern.replace("_", " ")
            if pattern in lower_content or normalized_pattern in lower_content:
                matches.append(pattern)
                matched_patterns.append(pattern)
            boundary_pattern = rf"\b{re.escape(normalized_pattern)}\b"
            if re.search(boundary_pattern, lower_content):
                regex_matches.append(pattern)

        taxonomy_tags = [self.pattern_taxonomy.get(pattern, "UNKNOWN_INJECTION") for pattern in matched_patterns]

        patch: StatePatch = StatePatch(
            {
                "injection_scan": {
                    "matches": matches,
                    "is_injection": len(matches) > 0,
                    "matched_patterns": matched_patterns,
                    "instructional_types": self.instructional_types,
                    "regex_matches": regex_matches,
                    "taxonomy_tags": taxonomy_tags,
                }
            }
        )
        return patch


class ConstitutionalEngine:
    """Evaluate content against deterministic constitutional rules."""

    DEFAULT_RULES: List[Dict[str, str]] = [
        {"id": "no_harm", "pattern": "harm", "description": "Avoid promoting harm."},
        {"id": "no_malware", "pattern": "malware", "description": "Avoid malicious software."},
        {"id": "no_privacy", "pattern": "private data", "description": "Avoid collecting private data."},
        {
            "id": "restricted_biomed",
            "pattern": "restricted_biomed",
            "description": "Avoid restricted biomedical guidance.",
        },
        {
            "id": "political_advocacy",
            "pattern": "political_advocacy",
            "description": "Avoid political advocacy.",
        },
        {
            "id": "cybersecurity_unsafe",
            "pattern": "cybersecurity_unsafe",
            "description": "Avoid unsafe cybersecurity guidance.",
        },
    ]

    def __init__(self, rules: List[Dict[str, str]] | None = None) -> None:
        self.rules = rules or list(self.DEFAULT_RULES)

    def evaluate(self, content: str) -> StatePatch:
        """Return a StatePatch capturing any matched constitutional rules."""

        violations: List[Dict[str, str]] = []
        for rule in self.rules:
            if rule["pattern"].lower() in content.lower():
                violations.append(
                    {
                        "rule": rule["id"],
                        "description": rule["description"],
                        "matched": rule["pattern"],
                    }
                )

        patch: StatePatch = StatePatch(
            {
                "constitutional_evaluation": {
                    "violations": violations,
                    "compliant": len(violations) == 0,
                    "pii": detect_pii(content),
                    "bias": detect_bias(content),
                }
            }
        )
        return patch


class SafetyGateway:
    """Deterministic gateway that wraps safety evaluations into a patch."""

    def __init__(
        self,
        constitutional_engine: ConstitutionalEngine | None = None,
        policy_engine: PolicyEngine | None = None,
        injection_detector: InjectionDetector | None = None,
        safety_mode: SafetyMode = SafetyMode.BALANCED,
    ) -> None:
        self.constitutional_engine = constitutional_engine or ConstitutionalEngine()
        self.policy_engine = policy_engine or PolicyEngine()
        self.injection_detector = injection_detector or InjectionDetector()
        self.safety_mode = safety_mode

    def evaluate(self, payload: Dict[str, Any]) -> StatePatch:
        """Perform safety checks on the provided payload and return a StatePatch."""

        content = str(payload.get("content", ""))
        intent = payload.get("intent") if isinstance(payload.get("intent"), dict) else {}
        routing_permissions = evaluate_routing_permissions(payload)

        constitutional_patch = self.constitutional_engine.evaluate(content)
        policy_patch = self.policy_engine.evaluate(intent)
        injection_patch = self.injection_detector.scan(content)

        constitutional_eval = constitutional_patch.get("constitutional_evaluation", {})
        policy_eval = policy_patch.get("policy_evaluation", {})
        injection_eval = injection_patch.get("injection_scan", {})

        violations = constitutional_eval.get("violations")
        is_injection = injection_eval.get("is_injection")
        policy_allowed = policy_eval.get("allowed")

        blocked = False
        if self.safety_mode == SafetyMode.STRICT:
            blocked = bool(violations) or bool(is_injection) or policy_allowed is False
        elif self.safety_mode == SafetyMode.BALANCED:
            blocked = bool(is_injection) or policy_allowed is False
        elif self.safety_mode == SafetyMode.PERMISSIVE:
            blocked = bool(is_injection)

        patch: StatePatch = StatePatch(
            {
                "safety_gateway": {
                    "constitutional": constitutional_patch.get("constitutional_evaluation", {}),
                    "policy": policy_patch.get("policy_evaluation", {}),
                    "injection": injection_patch.get("injection_scan", {}),
                    "tool_permissions": tool_permissions,
                    "routing_permissions": routing_permissions,
                    "taxonomy": {
                        "primitive_injection_patterns": DEFAULT_INJECTION_PATTERNS,
                        "instructional_injection_types": INSTRUCTIONAL_INJECTION_ALL,
                    },
                },
                "content_safety": {
                    "pii": constitutional_patch.get("constitutional_evaluation", {}).get("pii", {}),
                    "bias": constitutional_patch.get("constitutional_evaluation", {}).get("bias", {}),
                },
                "injection_safety": {
                    "prompt_shield": DEFAULT_SAFETY_OUTPUT_PROFILE.prompt_shield,
                    "data_instruction_separation": DEFAULT_SAFETY_OUTPUT_PROFILE.data_instruction_separation,
                    "constitutional_guardrails_enabled": DEFAULT_SAFETY_OUTPUT_PROFILE.constitutional_guardrails_enabled,
                    "delegation_guardrails_enabled": DEFAULT_SAFETY_OUTPUT_PROFILE.delegation_guardrails_enabled,
                    "adversarial_mode_enabled": DEFAULT_SAFETY_OUTPUT_PROFILE.adversarial_mode_enabled,
                },
                "status": "blocked" if blocked else "allowed",
                "mode": self.safety_mode.value,
            }
        )
        log_safety_decision(payload, patch)
        return patch
