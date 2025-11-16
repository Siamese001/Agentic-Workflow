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
from utils_types import StatePatch


class SafetyGateway:
    """Deterministic gateway that wraps safety evaluations into a patch."""

    def __init__(
        self,
        constitutional_engine: ConstitutionalEngine | None = None,
        policy_engine: PolicyEngine | None = None,
        injection_detector: InjectionDetector | None = None,
    ) -> None:
        self.constitutional_engine = constitutional_engine or ConstitutionalEngine()
        self.policy_engine = policy_engine or PolicyEngine()
        self.injection_detector = injection_detector or InjectionDetector()

    def evaluate(self, payload: Dict[str, Any]) -> StatePatch:
        """Perform safety checks on the provided payload and return a StatePatch."""

        content = str(payload.get("content", ""))
        intent = payload.get("intent") if isinstance(payload.get("intent"), dict) else {}

        constitutional_patch = self.constitutional_engine.evaluate(content)
        policy_patch = self.policy_engine.evaluate(intent)
        injection_patch = self.injection_detector.scan(content)

        patch: StatePatch = StatePatch(
            {
                "safety_gateway": {
                    "constitutional": constitutional_patch.get("constitutional_evaluation", {}),
                    "policy": policy_patch.get("policy_evaluation", {}),
                    "injection": injection_patch.get("injection_scan", {}),
                    "status": "blocked" if (
                        constitutional_patch.get("constitutional_evaluation", {}).get("violations")
                        or injection_patch.get("injection_scan", {}).get("is_injection")
                        or policy_patch.get("policy_evaluation", {}).get("allowed") is False
                    ) else "allowed",
                }
            }
        )
        return patch
