from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


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
