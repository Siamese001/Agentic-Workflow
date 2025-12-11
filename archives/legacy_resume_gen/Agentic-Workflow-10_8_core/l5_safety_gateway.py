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

# from archives.legacy_resume_gen.Agentic-Workflow-10_8_core.injection_output_profiles import DEFAULT_SAFETY_OUTPUT_PROFILE  # INVALID: Cannot import from path with hyphens
# from archives.legacy_resume_gen.Agentic-Workflow-10_8_core.l5_safety import ConstitutionalEngine  # INVALID: Cannot import from path with hyphens
# from archives.legacy_resume_gen.Agentic-Workflow-10_8_core.l5_safety import InjectionDetector  # INVALID: Cannot import from path with hyphens
# from archives.legacy_resume_gen.Agentic-Workflow-10_8_core.l5_policy import PolicyEngine  # INVALID: Cannot import from path with hyphens
# from archives.legacy_resume_gen.Agentic-Workflow-10_8_core.prompt_system import DEFAULT_INJECTION_PATTERNS, INSTRUCTIONAL_INJECTION_ALL  # INVALID: Cannot import from path with hyphens
# from archives.legacy_resume_gen.Agentic-Workflow-10_8_core.l5_policy import evaluate_routing_permissions  # INVALID: Cannot import from path with hyphens
# from archives.legacy_resume_gen.Agentic-Workflow-10_8_core.l5_policy import SafetyMode  # INVALID: Cannot import from path with hyphens
# from archives.legacy_resume_gen.Agentic-Workflow-10_8_core.l5_policy import permissions  # INVALID: Cannot import from path with hyphens
# from archives.legacy_resume_gen.Agentic-Workflow-10_8_core.l5_safety import log_safety_decision  # INVALID: Cannot import from path with hyphens
# from archives.legacy_resume_gen.Agentic-Workflow-10_8_core.utils_types import StatePatch  # INVALID: Cannot import from path with hyphens


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

    def evaluate(self, payload: Dict[str, object]) -> StatePatch:
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
