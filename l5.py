# FILE: l5.py
"""
Unified L5 Safety & Policy Layer (v10_9) — PURE SAFETY / POLICY

This module implements ALL high-level safety, policy, arbitration, and
model-routing responsibilities for the v10_9 agentic workflow.

Responsibilities (L5 only):
    • SafetyContracts        (allowed audiences, forbidden terms, toxicity thresholds)
    • SafetyOutputProfile    (prompt shielding / stability contracts / JSON constraints)
    • SafetyConfig           (policy rules, injection patterns, PII/bias toggles)
    • SafetyMode             (STRICT / BALANCED / PERMISSIVE)
    • Redaction utilities    (PII removal)
    • Bias scanning          (age-related, gendered, stereotyped patterns)
    • Prompt injection detection (deterministic heuristic detector)
    • Constitutional review  (rule-based)
    • SafetyEngine           (aggregated safety report using contracts + config)
    • PolicyEngine           (allow / retry / replan / block, mode-aware)
    • ArbitrationEngine      (normalize L5 action → L3 orchestrator hint)
    • ModelRouter            (model selection heuristic; used by routing/meta layers)

Layer constraints (Agentic Guardrails):
    • NO L1 cognition (no planning).
    • NO L2 execution (no tool/LLM calls).
    • NO L3 orchestration (no DAGs, no phases).
    • NO L4 state mutation (no StateAdapter usage).
    • NO provider/SDK imports (Anthropic/Gemini/OpenAI/etc.).
    • All logic is deterministic and side-effect free.

Integration points:
    • L3 Orchestrator calls SafetyEngine.evaluate_content(...) to get
      a safety_report (plain dict).
    • L3 then calls PolicyEngine.review(safety_report) for policy decision.
    • L3 then calls ArbitrationEngine.decide(...) to convert policy →
      normalized action ("proceed", "retry_l2", "rerun_l1", "halt" or "escalate").
    • Higher meta-layers may use ModelRouter for routing hints, but
      model invocation happens in routing/providers, not here.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from models import PlanObject
from runtime_utils import SafetyException


# ============================================================================
# 1. SAFETY CONTRACTS (L5 RUNTIME-CONTRACT LEVEL)
# ============================================================================


@dataclass
class SafetyContracts:
    """
    Determines allowed safety rules and restrictions:
        • allowed audiences
        • forbidden content
        • toxicity thresholds
        • bias patterns
        • PII patterns
        • feature toggles for detection subsystems

    This dataclass is pure configuration; it does not implement any
    logic itself.
    """

    allowed_audience: List[str] = field(
        default_factory=lambda: ["general", "professional", "executive"]
    )
    forbidden_terms: List[str] = field(
        default_factory=lambda: ["explicit", "violence", "hate", "slur"]
    )
    pii_patterns: List[str] = field(
        default_factory=lambda: ["@", "+1", "xxx-xxx"]
    )
    max_toxicity: float = 0.25
    enable_prompt_injection_detection: bool = True
    enable_bias_detection: bool = True


DEFAULT_SAFETY_CONTRACTS = SafetyContracts()


# ============================================================================
# 2. OUTPUT PROFILE (PROMPT SHIELDING / STABILITY CONTRACTS)
# ============================================================================


@dataclass
class SafetyOutputProfile:
    """
    Output-level safety controls, ported from v10_8.

    These flags do NOT execute any behavior by themselves, but they are
    used by:
        • prompt system (META layer) to shape envelopes
        • safety gateways to annotate output expectations
        • downstream services for policy enforcement

    L5 may attach these flags as metadata; it does not render prompts.
    """

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


# ============================================================================
# 3. POLICY / INJECTION CONFIG (v10_8 BACKPORT, L5-ONLY)
# ============================================================================


@dataclass
class SafetyRule:
    """Granular safety rule definition (metadata only)."""

    id: str
    description: str
    enabled: bool
    severity: str
    tags: List[str] = field(default_factory=list)


@dataclass
class PolicyRule:
    """
    Policy rule definition.

    action:  logical action label (e.g., "exfiltrate_data")
    allowed: whether the action is allowed
    reason:  optional short explanation
    """

    action: str
    allowed: bool
    reason: Optional[str]


@dataclass
class InjectionPattern:
    """Pattern for prompt injection detection (taxonomy-level)."""

    pattern: str
    enabled: bool
    tags: List[str] = field(default_factory=list)


@dataclass
class SafetyConfig:
    """
    Aggregated safety configuration:

        • policy_rules:  list of PolicyRule instances
        • injection_patterns: list of InjectionPattern instances
        • pii_enabled: toggle PII detection
        • bias_enabled: toggle bias detection
    """

    policy_rules: List[PolicyRule]
    injection_patterns: List[InjectionPattern]
    pii_enabled: bool
    bias_enabled: bool


DEFAULT_INJECTION_PATTERNS: List[str] = [
    "ignore previous instructions",
    "override system",
    "disable safety",
    "run arbitrary code",
]

DEFAULT_POLICY_DENY_LIST: List[str] = [
    "exfiltrate_data",
    "execute_code",
    "publish_unreviewed",
]


def load_default_safety_config() -> SafetyConfig:
    """
    Deterministic default SafetyConfig used when none is provided.

    This is a metadata-only description of policy/injection patterns.
    SafetyEngine uses it as additional context for classification but
    does not directly enforce policy decisions (that is PolicyEngine's job).
    """
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


class SafetyMode(str, Enum):
    """
    Safety operating mode, ported from v10_8:

        STRICT     – block on any serious issue (injection, policy, constitutional).
        BALANCED   – block on injection or policy violations.
        PERMISSIVE – block primarily on injection; allow more borderline cases.
    """

    STRICT = "strict"
    BALANCED = "balanced"
    PERMISSIVE = "permissive"


def mode_defaults(mode: SafetyMode) -> Dict[str, bool]:
    """
    Lightweight helper returning mode-specific behavior hints.

    L5 PolicyEngine uses this metadata to interpret safety_report issues.
    """
    if mode == SafetyMode.STRICT:
        return {"block_on_any": True}
    if mode == SafetyMode.BALANCED:
        return {"block_on_injection_or_policy": True}
    if mode == SafetyMode.PERMISSIVE:
        return {"block_on_injection_only": True}
    return {}


# ============================================================================
# 4. REDACTION UTILITIES (PII)
# ============================================================================

_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_PHONE_RE = re.compile(r"\b(?:\+?1[ -]?)?\(?\d{3}\)?[ -]?\d{3}[ -]?\d{4}\b")
_SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")


def redact_pii(text: str) -> str:
    """
    Remove common PII markers deterministically.

    This function is side-effect free and does not depend on any
    providers or external tools.
    """
    if not text:
        return text
    text = _EMAIL_RE.sub("[EMAIL_REDACTED]", text)
    text = _PHONE_RE.sub("[PHONE_REDACTED]", text)
    text = _SSN_RE.sub("[SSN_REDACTED]", text)
    return text


# ============================================================================
# 5. FORBIDDEN CONTENT / TOXICITY / BIAS
# ============================================================================


def scan_forbidden(text: str, forbidden_terms: List[str]) -> List[str]:
    """Return list of forbidden terms found in content."""
    hits: List[str] = []
    lower = text.lower()
    for term in forbidden_terms:
        if term in lower:
            hits.append(term)
    return hits


def toxicity_score(text: str) -> float:
    """
    Heuristic toxicity metric:
        - Too many exclamation marks
        - Aggressive words
        - Negative sentiment indicators (simple heuristic)

    This is deterministic and does not call any external APIs.
    """
    if not text:
        return 0.0
    aggressive = ["damn", "stupid", "idiot", "screw", "hate"]
    count = sum(text.lower().count(a) for a in aggressive)
    count += text.count("!")
    toks = len(text.split()) + 1
    return min(1.0, count / toks)


def scan_bias(text: str) -> List[str]:
    """
    Deterministic bias scan for:
        • age-related terms
        • gendered terms
        • stereotype patterns

    This is not a complete fairness system; it is a heuristics-based
    first-pass that can be extended or replaced by more advanced
    pipelines in providers/tooling.
    """
    lower = text.lower()
    patterns = {
        "age_bias": ["old", "young", "elderly", "junior", "senior citizen"],
        "gendered_terms": ["he/she", "him/her", "manpower", "chairman"],
        "stereotypes": ["aggressive female", "emotional woman"],
    }

    hits: List[str] = []
    for label, terms in patterns.items():
        for t in terms:
            if t in lower:
                hits.append(f"{label}:{t}")
    return hits


# ============================================================================
# 6. PROMPT INJECTION DETECTION (v10_9 + v10_8 PATTERN BACKPORT)
# ============================================================================

_PI_PATTERNS = [
    r"ignore all previous instructions",
    r"my real task is",
    r"please repeat the following",
    r"break character",
    r"system override",
]


def detect_prompt_injection(text: str, injection_patterns: Optional[List[InjectionPattern]] = None) -> Dict[str, Any]:
    """
    Deterministic prompt injection detector using substring + regex patterns.

    It combines:
        • v10_9 generic regex patterns (_PI_PATTERNS)
        • v10_8-style InjectionPattern taxonomy (if provided)

    Returns:
        {
            "detected": bool,
            "reason": str,
            "confidence": float,
            "matched_patterns": [<strings>],
        }
    """
    if not text:
        return {"detected": False, "reason": "", "confidence": 0.0, "matched_patterns": []}

    lower = text.lower()
    matched: List[str] = []

    # Built-in regex patterns
    for pattern in _PI_PATTERNS:
        if re.search(pattern, lower):
            matched.append(f"regex:{pattern}")

    # v10_8 injection patterns
    if injection_patterns:
        for pat in injection_patterns:
            if not pat.enabled:
                continue
            if pat.pattern.lower() in lower:
                matched.append(f"pattern:{pat.pattern}")

    if matched:
        return {
            "detected": True,
            "reason": f"Matched patterns: {', '.join(matched)}",
            "confidence": 0.95,
            "matched_patterns": matched,
        }

    return {"detected": False, "reason": "", "confidence": 0.0, "matched_patterns": []}


# ============================================================================
# 7. CONSTITUTIONAL REVIEW (Deterministic Rule Set)
# ============================================================================

_CONSTITUTION_RULES = {
    "no_hate": lambda t: "hate" not in t.lower(),
    "no_explicit": lambda t: "explicit" not in t.lower(),
    "no_violence": lambda t: "violence" not in t.lower(),
    "tone_professional": lambda t: "idiot" not in t.lower() and "stupid" not in t.lower(),
}


def constitutional_review(text: str) -> Dict[str, Any]:
    """
    Deterministic constitutional review engine.

    Returns:
        {
            "passed": bool,
            "violations": [...],
            "confidence": float,
        }
    """
    if not text:
        return {"passed": True, "violations": [], "confidence": 1.0}

    violations: List[str] = []
    for rule, fn in _CONSTITUTION_RULES.items():
        if not fn(text):
            violations.append(rule)

    passed = len(violations) == 0
    conf = 1.0 - (len(violations) / max(len(_CONSTITUTION_RULES), 1))

    return {
        "passed": passed,
        "violations": violations,
        "confidence": round(conf, 3),
    }


# ============================================================================
# 8. SAFETY ENGINE
# ============================================================================


class SafetyEngine:
    """
    Full safety engine that aggregates:
        • PII redaction
        • forbidden content scan
        • toxicity analysis
        • prompt injection detection (with taxonomy)
        • bias scan
        • constitutional review

    Primary API used by L3:

        evaluate_content(state: dict, plan: PlanObject) -> safety_report: dict

    It may still expose a lower-level validate(content, audience) helper
    for unit testing and tooling, but orchestration goes through
    evaluate_content.

    This class is deterministic and does not call external LLMs/tools.
    """

    def __init__(
        self,
        contracts: SafetyContracts = DEFAULT_SAFETY_CONTRACTS,
        config: Optional[SafetyConfig] = None,
        output_profile: SafetyOutputProfile = DEFAULT_SAFETY_OUTPUT_PROFILE,
    ):
        self.contracts = contracts
        self.config = config or load_default_safety_config()
        self.output_profile = output_profile

    def validate(self, content: str, audience: str = "general") -> Dict[str, Any]:
        """
        Validate a single content string against contracts and config and
        return a structured safety report.

        The returned dict is intentionally compatible with SafetyReport
        structures used in models.py and L2 SafetyExecutor.
        """
        if audience not in self.contracts.allowed_audience:
            raise SafetyException(f"Audience '{audience}' not permitted.")

        # PII redaction
        redacted = redact_pii(content) if self.config.pii_enabled else content

        # Forbidden terms
        forbidden = scan_forbidden(content, self.contracts.forbidden_terms)

        # Toxicity
        tox = toxicity_score(content)
        tox_flag = tox > self.contracts.max_toxicity

        # Bias
        bias_issues: List[str] = scan_bias(content) if (self.contracts.enable_bias_detection and self.config.bias_enabled) else []

        # Prompt injection (generic + pattern-based)
        pi = (
            detect_prompt_injection(content, self.config.injection_patterns)
            if self.contracts.enable_prompt_injection_detection
            else {"detected": False, "reason": "", "confidence": 0.0, "matched_patterns": []}
        )

        # Constitutional evaluation
        const = constitutional_review(content)

        # Build issues list (structured codes)
        issues: List[str] = []
        if redacted != content:
            issues.append("pii_redacted")
        issues.extend(f"forbidden:{t}" for t in forbidden)
        if tox_flag:
            issues.append("toxicity")
        issues.extend(bias_issues)
        if pi.get("detected"):
            issues.append("prompt_injection")
        if not const["passed"]:
            issues.extend(f"constitutional:{v}" for v in const["violations"])

        # Attach output-profile metadata as a sub-block for downstream layers
        output_profile_block = {
            "prompt_shield": self.output_profile.prompt_shield,
            "data_instruction_separation": self.output_profile.data_instruction_separation,
            "constitutional_guardrails_enabled": self.output_profile.constitutional_guardrails_enabled,
            "delegation_guardrails_enabled": self.output_profile.delegation_guardrails_enabled,
            "adversarial_mode_enabled": self.output_profile.adversarial_mode_enabled,
            "strict_json_output": self.output_profile.strict_json_output,
            "enforce_schema": self.output_profile.enforce_schema,
            "stability_contracts": self.output_profile.stability_contracts,
            "error_normalization": self.output_profile.error_normalization,
            "minimality_constraints": self.output_profile.minimality_constraints,
        }

        return {
            "passed": len(issues) == 0,
            "issues": issues,
            "toxicity_score": tox,
            "audience": audience,
            "prompt_injection": pi,
            "constitutional": const,
            "sanitized": redacted,
            "output_profile": output_profile_block,
            # Attach a light taxonomy view of injection patterns for observability
            "injection_taxonomy": {
                "patterns": [p.pattern for p in self.config.injection_patterns if p.enabled],
            },
        }

    def evaluate_content(self, state: Dict[str, Any], plan: PlanObject) -> Dict[str, Any]:
        """
        Main entrypoint used by L3.

        Extracts the relevant content from the orchestration state and
        evaluates it under the safety contract with respect to the plan.
        """
        # Determine audience
        audience = str(plan.get("audience", state.get("audience", "general")))

        # Content priority:
        #   1. draft_result["draft"]
        #   2. messages[-1]["content"]
        #   3. summary
        content = ""

        draft_result = state.get("draft_result") or {}
        draft_list = draft_result.get("draft") or []
        if isinstance(draft_list, list) and draft_list:
            content = "\n".join(str(x) for x in draft_list)
        else:
            messages = state.get("messages") or []
            if messages:
                last = messages[-1]
                if isinstance(last, dict):
                    content = str(last.get("content", ""))
        if not content:
            content = str(state.get("summary", ""))

        return self.validate(content, audience=audience)


# ============================================================================
# 9. POLICY ENGINE (allow / retry / replan / block) — MODE-AWARE
# ============================================================================


class PolicyEngine:
    """
    High-level policy enforcement engine.

    Maps a safety_report to a policy decision:
        • allow       → proceed
        • retry       → re-run L2 stage
        • replan      → re-run L1 → L2
        • block       → halt workflow

    v10_9 version is enhanced with:
        • SafetyMode awareness (STRICT / BALANCED / PERMISSIVE)
        • SafetyConfig metadata (policy rules, injection patterns)

    This engine is deterministic and does not call external services.
    """

    def __init__(
        self,
        safety_config: Optional[SafetyConfig] = None,
        mode: SafetyMode = SafetyMode.BALANCED,
    ) -> None:
        self.config = safety_config or load_default_safety_config()
        self.mode = mode
        self._mode_defaults = mode_defaults(mode)

    def _has_policy_violation(self, safety_report: Dict[str, Any]) -> bool:
        """
        Simple policy evaluation: if any issue corresponds to a deny-list
        action, treat it as a policy violation.

        In this reference implementation, we do not parse full intents,
        but we provide the hook for more advanced behavior.
        """
        issues = safety_report.get("issues", []) or []
        # For now, we only check for structural policy codes like "forbidden:*"
        return any(str(issue).startswith("forbidden:") for issue in issues)

    def review(self, safety_report: Dict[str, Any]) -> Dict[str, Any]:
        """
        Return a structured policy decision from a safety_report.

        Shape:
            {
              "decision": "allow|retry|replan|block",
              "reason":   "<short string>",
            }

        SafetyMode + config influence which issues are considered blocking.
        """
        issues = safety_report.get("issues", []) or []
        passed = safety_report.get("passed", False)

        # If safety explicitly passed with no issues, we allow irrespective of mode.
        if passed and not issues:
            return {"decision": "allow", "reason": "no_issues_detected"}

        has_prompt_injection = any("prompt_injection" in str(x) for x in issues)
        has_const_violation = any("constitutional" in str(x) for x in issues)
        has_toxicity = any("toxicity" in str(x) for x in issues)
        has_policy_violation = self._has_policy_violation(safety_report)
        has_pii_redacted = any("pii_redacted" in str(x) for x in issues)

        # Interpret mode defaults
        block_on_any = self._mode_defaults.get("block_on_any", False)
        block_on_injection_or_policy = self._mode_defaults.get(
            "block_on_injection_or_policy", False
        )
        block_on_injection_only = self._mode_defaults.get(
            "block_on_injection_only", False
        )

        # STRICT mode: block on any serious signal
        if block_on_any:
            if has_prompt_injection or has_const_violation or has_policy_violation or has_toxicity:
                return {"decision": "block", "reason": "strict_block_on_issue"}

        # BALANCED mode: focus on injection + policy as blockers
        if block_on_injection_or_policy:
            if has_prompt_injection:
                return {"decision": "block", "reason": "prompt_injection_detected"}
            if has_policy_violation:
                return {"decision": "replan", "reason": "policy_violation"}

        # PERMISSIVE mode: primarily react to injection; policy violation suggests replan
        if block_on_injection_only:
            if has_prompt_injection:
                return {"decision": "block", "reason": "prompt_injection_detected"}
            if has_policy_violation:
                return {"decision": "replan", "reason": "policy_violation"}

        # Constitutional violations (any mode): prefer replan
        if has_const_violation:
            return {"decision": "replan", "reason": "constitutional_violations"}

        # Toxicity: suggest retry (e.g., regenerate safer variant)
        if has_toxicity:
            return {"decision": "retry", "reason": "toxicity_exceeded"}

        # PII redaction alone is not a blocker: allow but record
        if has_pii_redacted:
            return {"decision": "allow", "reason": "pii_was_redacted"}

        # Fallback: if there are issues but none matched above, be conservative
        if issues:
            if self.mode == SafetyMode.STRICT:
                return {"decision": "block", "reason": "unclassified_safety_issue_strict"}
            if self.mode == SafetyMode.BALANCED:
                return {"decision": "replan", "reason": "unclassified_safety_issue"}
            # PERMISSIVE
            return {"decision": "allow", "reason": "issues_non_blocking_permissive"}

        # Absolute fallback
        return {"decision": "allow", "reason": "default_allow"}


# ============================================================================
# 10. ARBITRATION ENGINE (policy → orchestrator action)
# ============================================================================


class ArbitrationEngine:
    """
    Determines final normalized L5 action from a policy decision and
    the underlying safety_report:

        • proceed   — workflow may continue
        • retry_l2  — re-run L2 stage (same plan)
        • rerun_l1  — re-plan at L1 then re-run L2
        • halt      — stop the workflow
        • escalate  — escalate to external HIL / safety gateway (v10_8 parity)

    The returned dict is intentionally simple so L3 can route based on
    action and record the hint for self-correction/meta-learning.
    """

    def decide(self, policy: Dict[str, Any], safety_report: Dict[str, Any]) -> Dict[str, Any]:
        decision = policy.get("decision")

        if decision == "allow":
            return {"action": "proceed", "reason": policy.get("reason", "no_issues")}

        if decision == "retry":
            return {"action": "retry_l2", "reason": policy.get("reason", "retry_requested")}

        if decision == "replan":
            return {"action": "rerun_l1", "reason": policy.get("reason", "replan_requested")}

        if decision == "block":
            # Determine whether we should escalate or just halt.
            issues = safety_report.get("issues", []) or []
            has_prompt_injection = any("prompt_injection" in str(x) for x in issues)
            has_severe_const = any("constitutional" in str(x) for x in issues)
            # For injection or strong constitutional failures, we escalate.
            if has_prompt_injection or has_severe_const:
                return {"action": "escalate", "reason": policy.get("reason", "blocked_escalation")}
            return {"action": "halt", "reason": policy.get("reason", "blocked_by_policy")}

        # Fallback
        return {"action": "proceed", "reason": "default_allow"}


# ============================================================================
# 11. MODEL ROUTER (optional; not wired into L3 in v10_9)
# ============================================================================


@dataclass
class RoutingCriteria:
    """
    Model routing criteria used by ModelRouter.

    Fields:
        task_type: str  — e.g., "strategy", "rag", "drafting", "qa", "safety"
        complexity: str — "low", "medium", "high"
        latency_target_ms: int
        cost_ceiling_usd: float
        risk_level: str — "normal", "strict", "high_safety"
        model_available: bool
    """

    task_type: str
    complexity: str = "low"         # "low", "medium", "high"
    latency_target_ms: int = 2000
    cost_ceiling_usd: float = 0.05
    risk_level: str = "normal"      # "normal", "strict", "high_safety"
    model_available: bool = True


@dataclass
class RoutingDecision:
    """
    Routing decision produced by ModelRouter.

    Fields:
        model: str      — logical model name (e.g., "gpt-4.1")
        endpoint: str   — endpoint flavor (e.g., "standard", "fast")
        rationale: str  — short explanation
    """

    model: str
    endpoint: str
    rationale: str


class ModelRouter:
    """
    Determines which model + endpoint to use based on:

        • complexity
        • latency
        • cost
        • risk
        • availability

    NOTE:
        This router is NOT currently wired into L3; it is designed to
        be used by routing/meta layers or provider/tool clients. It does
        not execute any model calls itself.
    """

    def select(self, criteria: RoutingCriteria) -> RoutingDecision:
        # High complexity or strict-risk tasks
        if criteria.complexity == "high" or criteria.risk_level in ("strict", "high_safety"):
            selected = RoutingDecision(
                model="gpt-4.1",
                endpoint="standard",
                rationale="high_complexity_or_risk",
            )

        # Fast-latency tasks
        elif criteria.latency_target_ms < 1000:
            selected = RoutingDecision(
                model="gpt-4.1-mini",
                endpoint="fast",
                rationale="latency_optimized",
            )

        else:
            selected = RoutingDecision(
                model="gpt-4.1-mini",
                endpoint="standard",
                rationale="default_route",
            )

        # Fallback if model unavailable
        if not criteria.model_available:
            selected = RoutingDecision(
                model="gpt-4.1-mini",
                endpoint="backup-fast",
                rationale="primary_model_unavailable",
            )

        return selected
