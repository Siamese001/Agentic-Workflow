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

from l5_constitutional_engine import ConstitutionalEngine
from l5_injection_detector import InjectionDetector
from l5_policy_engine import PolicyEngine
from safety_modes import SafetyMode, mode_defaults
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

        constitutional_patch = self.constitutional_engine.evaluate(content)
        policy_patch = self.policy_engine.evaluate(intent)
        injection_patch = self.injection_detector.scan(content)

        constitutional_eval = constitutional_patch.get("constitutional_evaluation", {})
        policy_eval = policy_patch.get("policy_evaluation", {})
        injection_eval = injection_patch.get("injection_scan", {})

        violations = constitutional_eval.get("violations")
        is_injection = injection_eval.get("is_injection")
        policy_allowed = policy_eval.get("allowed")

        block_on = mode_defaults(self.safety_mode).get("block_on", [])

        blocked = False
        if "violation" in block_on and violations:
            blocked = True
        if "injection" in block_on and is_injection:
            blocked = True
        if "policy_denied" in block_on and policy_allowed is False:
            blocked = True

        patch: StatePatch = StatePatch(
            {
                "safety_gateway": {
                    "constitutional": constitutional_eval,
                    "policy": policy_eval,
                    "injection": injection_eval,
                    "content_safety": {
                        "pii": constitutional_eval.get("pii", {}),
                        "bias": constitutional_eval.get("bias", {}),
                    },
                    "status": "blocked" if blocked else "allowed",
                    "mode": self.safety_mode.value,
                }
            }
        )
        log_safety_decision(payload, patch)
        return patch
