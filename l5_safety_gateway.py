"""
L5 — Safety Gateway

Responsibilities:
    • Serve as the primary enforcement point for safety and policy checks.
    • Evaluate intents and outputs from lower layers before execution or release.
    • Route escalations to constitutional and policy engines without duplicating their logic.

Produces StatePatch outputs only.
"""
from __future__ import annotations

from typing import Any, Dict

from injection_output_profiles import DEFAULT_SAFETY_OUTPUT_PROFILE
from l5_constitutional_engine import ConstitutionalEngine
from l5_injection_detector import InjectionDetector
from l5_policy_engine import PolicyEngine
from prompt_taxonomy import DEFAULT_INJECTION_PATTERNS, INSTRUCTIONAL_INJECTION_ALL
from routing_permissions import evaluate_routing_permissions
from safety_modes import SafetyMode
from tool_permissions import permissions as tool_permissions
from utils_logger import log_safety_decision
from utils_types import StatePatch


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
