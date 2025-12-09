"""Layer 5 policy module consolidating policy components."""



from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from utils_types import StatePatch


class SafetyMode(str, Enum):
    STRICT = "strict"
    BALANCED = "balanced"
    PERMISSIVE = "permissive"


def mode_defaults(mode: SafetyMode) -> Dict[str, bool]:
    if mode == SafetyMode.STRICT:
        return {"block_on_any": True}
    if mode == SafetyMode.BALANCED:
        return {"block_on_injection_or_policy": True}
    if mode == SafetyMode.PERMISSIVE:
        return {"block_on_injection_only": True}
    return {}


@dataclass
class SafetyRule:
    id: str
    description: str
    enabled: bool
    severity: str
    tags: List[str] = field(default_factory=list)


@dataclass
class PolicyRule:
    action: str
    allowed: bool
    reason: Optional[str]


@dataclass
class InjectionPattern:
    pattern: str
    enabled: bool
    tags: List[str] = field(default_factory=list)


@dataclass
class SafetyConfig:
    policy_rules: List[PolicyRule]
    injection_patterns: List[InjectionPattern]
    pii_enabled: bool
    bias_enabled: bool


DEFAULT_INJECTION_PATTERNS = [
    "ignore previous instructions",
    "override system",
    "disable safety",
    "run arbitrary code",
]

DEFAULT_POLICY_DENY_LIST = [
    "exfiltrate_data",
    "execute_code",
    "publish_unreviewed",
]


def load_default_safety_config() -> SafetyConfig:
    injection_patterns = [
        InjectionPattern(pattern=pattern, enabled=True, tags=["default", "injection"])
        for pattern in DEFAULT_INJECTION_PATTERNS
    ]
    policy_rules = [
        PolicyRule(action=action, allowed=False, reason="action blocked by policy")
        for action in DEFAULT_POLICY_DENY_LIST
    ]

    return SafetyConfig(
        policy_rules=policy_rules,
        injection_patterns=injection_patterns,
        pii_enabled=True,
        bias_enabled=True,
    )


permissions = {
    "drafting": {"allowed": True},
    "rag": {"allowed": True},
    "bullet": {"allowed": True},
    "qa": {"allowed": True},
}


PERMITTED_MODELS: Set[str] = {"gpt-4o", "gpt-4o-mini"}
PERMITTED_ENDPOINTS: Set[str] = {"default", "fast"}


def evaluate_routing_permissions(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Return metadata describing routing allowance for the payload."""

    model = str(payload.get("model", "")).strip()
    endpoint = str(payload.get("endpoint", "")).strip()

    return {
        "model": model or None,
        "endpoint": endpoint or None,
        "model_allowed": bool(model) and model in PERMITTED_MODELS,
        "endpoint_allowed": bool(endpoint) and endpoint in PERMITTED_ENDPOINTS,
    }


class PolicyEngine:
    """Deterministic policy evaluation engine."""

    def __init__(self, config: SafetyConfig | None = None) -> None:
        self._config = config or load_default_safety_config()

    def evaluate(self, intent: Dict[str, str] | None = None) -> StatePatch:
        """Return a StatePatch describing policy allowances for the given intent."""

        intent = intent or {}
        action = intent.get("action", "unspecified")
        rule = next(
            (policy_rule for policy_rule in self._config.policy_rules if policy_rule.action == action),
            PolicyRule(action=action, allowed=True, reason=None),
        )
        allowed = rule.allowed

        patch: StatePatch = StatePatch(
            {
                "policy_evaluation": {
                    "action": action,
                    "allowed": allowed,
                    "denied_reason": rule.reason if not allowed else None,
                    "denied_actions": [policy_rule.action for policy_rule in self._config.policy_rules if not policy_rule.allowed],
                }
            }
        )
        return patch
