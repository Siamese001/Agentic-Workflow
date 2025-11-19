# FILE: l5.py
"""
Unified L5 Safety & Policy Layer (v10_9) — PURE SAFETY / POLICY

This module implements ALL high-level safety, policy, arbitration, and
model-routing responsibilities for the v10_9 agentic workflow.

Responsibilities (L5 only):
    • SafetyContracts        (allowed audiences, forbidden terms, toxicity thresholds)
    • Redaction utilities    (PII removal)
    • Bias scanning          (age-related, gendered, stereotyped patterns)
    • Prompt injection detection (deterministic heuristic detector)
    • Constitutional review  (rule-based)
    • SafetyEngine           (aggregated safety report)
    • PolicyEngine           (allow / retry / replan / block)
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
      normalized action ("proceed", "retry_l2", "rerun_l1", "halt").
    • Higher meta-layers may use ModelRouter for routing hints, but
      model invocation happens in routing/providers, not here.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from models import PlanObject
from runtime_utils import SafetyException


# ============================================================================
# 1. SAFETY CONTRACTS
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
# 2. REDACTION UTILITIES (PII)
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
# 3. FORBIDDEN CONTENT / TOXICITY / BIAS
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
# 4. PROMPT INJECTION DETECTION
# ============================================================================

_PI_PATTERNS = [
    r"ignore all previous instructions",
    r"my real task is",
    r"please repeat the following",
    r"break character",
    r"system override",
]


def detect_prompt_injection(text: str) -> Dict[str, Any]:
    """
    Deterministic prompt injection detector using substring + regex patterns.

    Returns:
        {
            "detected": bool,
            "reason": str,
            "confidence": float,
        }
    """
    if not text:
        return {"detected": False, "reason": "", "confidence": 0.0}

    lower = text.lower()
    for pattern in _PI_PATTERNS:
        if re.search(pattern, lower):
            return {
                "detected": True,
                "reason": f"Matched pattern: {pattern}",
                "confidence": 0.95,
            }

    return {"detected": False, "reason": "", "confidence": 0.0}


# ============================================================================
# 5. CONSTITUTIONAL REVIEW (Deterministic Rule Set)
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
# 6. SAFETY ENGINE
# ============================================================================


class SafetyEngine:
    """
    Full safety engine that aggregates:
        • PII redaction
        • forbidden content scan
        • toxicity analysis
        • prompt injection detection
        • bias scan
        • constitutional review

    Primary API used by L3:

        evaluate_content(state: dict, plan: PlanObject) -> safety_report: dict

    It may still expose a lower-level validate(content, audience) helper
    for unit testing and tooling, but orchestration goes through
    evaluate_content.

    This class is deterministic and does not call external LLMs/tools.
    """

    def __init__(self, contracts: SafetyContracts = DEFAULT_SAFETY_CONTRACTS):
        self.contracts = contracts

    def validate(self, content: str, audience: str = "general") -> Dict[str, Any]:
        """
        Validate a single content string against contracts and return a
        structured safety report.

        The returned dict is intentionally compatible with SafetyReport
        structures used in models.py and L2 SafetyExecutor.
        """
        if audience not in self.contracts.allowed_audience:
            raise SafetyException(f"Audience '{audience}' not permitted.")

        redacted = redact_pii(content)
        forbidden = scan_forbidden(content, self.contracts.forbidden_terms)
        tox = toxicity_score(content)
        tox_flag = tox > self.contracts.max_toxicity
        bias_issues = scan_bias(content) if self.contracts.enable_bias_detection else []
        pi = (
            detect_prompt_injection(content)
            if self.contracts.enable_prompt_injection_detection
            else {"detected": False, "reason": "", "confidence": 0.0}
        )
        const = constitutional_review(content)

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

        return {
            "passed": len(issues) == 0,
            "issues": issues,
            "toxicity_score": tox,
            "audience": audience,
            "prompt_injection": pi,
            "constitutional": const,
            "sanitized": redacted,
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
# 7. POLICY ENGINE (allow / retry / replan / block)
# ============================================================================


class PolicyEngine:
    """
    High-level policy enforcement engine.

    Maps a safety_report to a policy decision:
        • allow       → proceed
        • retry       → re-run L2 stage
        • replan      → re-run L1 → L2
        • block       → halt workflow

    This engine is deterministic and does not call external services.
    """

    def review(self, safety_report: Dict[str, Any]) -> Dict[str, Any]:
        """
        Return a structured policy decision from a safety_report.

        The shape is:

            {
              "decision": "allow|retry|replan|block",
              "reason":   "<short string>",
            }
        """
        issues = safety_report.get("issues", [])
        passed = safety_report.get("passed", False)

        if passed:
            return {"decision": "allow", "reason": "no_issues_detected"}

        if "prompt_injection" in issues:
            return {"decision": "block", "reason": "prompt_injection_detected"}

        if any("constitutional" in x for x in issues):
            return {"decision": "replan", "reason": "constitutional_violations"}

        if "toxicity" in issues:
            return {"decision": "retry", "reason": "toxicity_exceeded"}

        if any("forbidden" in x for x in issues):
            return {"decision": "replan", "reason": "forbidden_content"}

        if any("pii_redacted" in x for x in issues):
            return {"decision": "allow", "reason": "pii_was_redacted"}

        # Fallback
        return {"decision": "block", "reason": "unclassified_safety_issue"}


# ============================================================================
# 8. ARBITRATION ENGINE (policy → orchestrator action)
# ============================================================================


class ArbitrationEngine:
    """
    Determines final normalized L5 action from a policy decision and
    the underlying safety_report:

        • proceed   — workflow may continue
        • retry_l2  — re-run L2 stage (same plan)
        • rerun_l1  — re-plan at L1 then re-run L2
        • halt      — stop the workflow

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
            return {"action": "halt", "reason": policy.get("reason", "blocked_by_policy")}

        # Fallback
        return {"action": "proceed", "reason": "default_allow"}


# ============================================================================
# 9. MODEL ROUTER (optional; not wired into L3 in v10_9)
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
