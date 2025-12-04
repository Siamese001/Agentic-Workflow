"""
V10.8 Consolidated Module: Config Profiles
Merged from 10 source files
"""

# Consolidated imports
from __future__ import annotations
from dataclasses import dataclass
from dataclasses import dataclass, field
from enum import Enum
from observability import compute_optimization_hint
from pathlib import Path
from self_correction import SelfCorrectionSurface
from typing import Any, Dict
from typing import Any, Dict, List
from typing import Dict
from typing import List, Optional
import sys


# ============================================================
# From v10_8_conftest.py
# ============================================================

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# ============================================================
# From v10_8_injection_output_profiles.py
# ============================================================

@dataclass
class SafetyOutputProfile:
    prompt_shield: bool
    data_instruction_separation: bool
    constitutional_guardrails_enabled: bool
    delegation_guardrails_enabled: bool
    adversarial_mode_enabled: bool
    strict_json_output: bool
    enforce_schema: bool
    stability_contracts: bool
    error_normalization: bool
    minimality_constraints: bool


DEFAULT_SAFETY_OUTPUT_PROFILE = SafetyOutputProfile(
    prompt_shield=True,
    data_instruction_separation=True,
    constitutional_guardrails_enabled=True,
    delegation_guardrails_enabled=True,
    adversarial_mode_enabled=True,
    strict_json_output=False,     # opt-in for stacks using schema
    enforce_schema=False,
    stability_contracts=True,
    error_normalization=True,
    minimality_constraints=True,
)

# ============================================================
# From v10_8_injection_profiles.py
# ============================================================

@dataclass
class FramingProfile:
    global_goal: str
    success_criteria: str
    task_mode: str
    scope_boundaries: str
    cost_latency: Dict[str, Any]


DEFAULT_FRAMING_PROFILE = FramingProfile(
    global_goal="solve the user objective deterministically",
    success_criteria="correct, concise, aligned to instructions",
    task_mode="analytical",
    scope_boundaries="stay within provided state and allowed tools",
    cost_latency={"max_ms": 2000, "max_cost": 0.05},
)


@dataclass
class ContextProfile:
    untrusted_block_wrapping: bool
    canonicalize_inputs: bool
    apply_pruning_rules: bool
    enforce_structured_ordering: bool


DEFAULT_CONTEXT_PROFILE = ContextProfile(
    untrusted_block_wrapping=True,
    canonicalize_inputs=True,
    apply_pruning_rules=True,
    enforce_structured_ordering=True,
)

# ============================================================
# From v10_8_injection_tooling_profiles.py
# ============================================================

@dataclass
class ToolingProfile:
    tool_feedback_enabled: bool
    evidence_binding_enabled: bool
    cross_tool_reconciliation: bool
    shadow_validation_enabled: bool
    model_switch_awareness: bool


DEFAULT_TOOLING_PROFILE = ToolingProfile(
    tool_feedback_enabled=True,
    evidence_binding_enabled=True,
    cross_tool_reconciliation=True,
    shadow_validation_enabled=True,
    model_switch_awareness=True,
)

# ============================================================
# From v10_8_meta_profile.py
# ============================================================

@dataclass
class MetaProfile:
    routing_bias: Dict[str, Any] = field(default_factory=dict)
    planning_bias: Dict[str, Any] = field(default_factory=dict)


META_PROFILE = MetaProfile()


def update_meta_profile_from_spans_and_self_correction(spans, sc):
    """Update in-memory meta profile using spans and self-correction signals."""

    optimization_hint = compute_optimization_hint(spans or [])
    if optimization_hint.get("suggestion") == "reroute_fast":
        META_PROFILE.routing_bias["prefer_fast"] = True

    sc = sc or {}
    surface = sc.get("surface")
    recommendation = sc.get("recommendation") if isinstance(sc, dict) else None
    if (
        surface == SelfCorrectionSurface.QA_RECHECK.value
        and isinstance(recommendation, dict)
        and recommendation.get("needs_retry")
    ):
        META_PROFILE.planning_bias["conservative"] = True

# ============================================================
# From v10_8_rag_config.py
# ============================================================

@dataclass
class RetrievalConfig:
    queries: List[str]
    filters: Dict[str, Any]
    ranking: Dict[str, Any]
    metadata: Dict[str, Any] | None = None

    def to_plan_fragment(self) -> Dict[str, Any]:
        return {
            "queries": self.queries,
            "filters": self.filters,
            "ranking": self.ranking,
            "metadata": self.metadata or {},
        }

# ============================================================
# From v10_8_safety_config.py
# ============================================================

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

# ============================================================
# From v10_8_safety_modes.py
# ============================================================

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

# ============================================================
# From v10_8_tool_permissions.py
# ============================================================

Static tool permission declarations for L2 agents.
"""
from __future__ import annotations

permissions = {
    "drafting": {"allowed": True},
    "rag": {"allowed": True},
    "bullet": {"allowed": True},
    "qa": {"allowed": True},
}

# ============================================================
# From v10_8_routing_permissions.py
# ============================================================

Metadata helpers for routing permissions.
"""
from __future__ import annotations

from typing import Any, Dict, Set

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
