# FILE: l5.py
"""
Unified L5 Safety & Policy Layer (v10_9) — PURE SAFETY / POLICY (META-AWARE, RESTORED)

This module implements ALL high-level safety, policy, arbitration, and
model-routing responsibilities for the v10_9 agentic workflow.

Responsibilities (L5 only):
    • SafetyEngine           (aggregated safety report from content).
    • PolicyEngine           (allow / retry / replan / block, mode-aware).
    • ArbitrationEngine      (normalize L5 action → L3 orchestrator hint).
    • Lightweight model-routing hints (delegated to routing.py for execution).

L5 consumes, but does NOT own:
    • L2 safety outputs (SafetyExecutionPayload).
    • L4 state (read-only views).
    • meta_profile biases (SafetyBias, PlanningBias, RoutingBias, etc.).
    • L1 plan metadata (audience, risk level, surfaces).

Layer constraints (Agentic Guardrails):
    • NO L1 planning (no PlanObject creation).
    • NO L2 execution (no tool/LLM calls).
    • NO L3 DAG/orchestration.
    • NO L4 state mutation (no StateAdapter usage).
    • NO provider/SDK imports (Anthropic/Gemini/OpenAI, etc.).

Integration points:
    • main_v10_9:
        - calls SafetyEngine.evaluate_content(state, plan) → safety_report: dict
        - calls PolicyEngine.review(safety_report) → policy_decision: dict
        - calls ArbitrationEngine.arbitrate(policy_decision, safety_report)
          → ArbitrationDecision (from models) used to hint L3/HIL behavior.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from models import ArbitrationDecision
from meta_profile import get_safety_bias, get_planning_bias


# ============================================================================
# 1. SAFETY MODES
# ============================================================================


class SafetyMode(str, Enum):
    """
    Safety operating mode:

        STRICT     – block on any serious issue (injection, policy, constitutional).
        BALANCED   – block on injection or strong policy violations.
        PERMISSIVE – block primarily on injection; allow more borderline cases.
    """

    STRICT = "strict"
    BALANCED = "balanced"
    PERMISSIVE = "permissive"


def _derive_mode_from_meta(base_mode: SafetyMode) -> SafetyMode:
    """
    Combine base SafetyMode with meta_profile biases:

        • safety_bias.heightened_caution  → STRICT
        • planning_bias.conservative      → tilt to STRICT
        • safety_bias.human_review_important alone → BALANCED is ok
    """
    safety_bias = get_safety_bias()
    planning_bias = get_planning_bias()

    if safety_bias.get("heightened_caution") or planning_bias.get("conservative"):
        return SafetyMode.STRICT

    # If the only signal is "human_review_important", balanced is fine.
    if base_mode == SafetyMode.PERMISSIVE and safety_bias.get("human_review_important"):
        return SafetyMode.BALANCED

    return base_mode


# ============================================================================
# 2. REDACTION & SCANNING UTILITIES
# ============================================================================

_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_PHONE_RE = re.compile(r"\b(?:\+?1[ -]?)?\(?\d{3}\)?[ -]?\d{3}[ -]?\d{4}\b")
_SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")


def redact_pii(text: str) -> str:
    """Remove common PII markers deterministically."""
    if not text:
        return text
    text = _EMAIL_RE.sub("[EMAIL_REDACTED]", text)
    text = _PHONE_RE.sub("[PHONE_REDACTED]", text)
    text = _SSN_RE.sub("[SSN_REDACTED]", text)
    return text


def scan_forbidden(text: str, forbidden_terms: List[str]) -> List[str]:
    """Return list of forbidden terms found in content."""
    hits: List[str] = []
    lower = text.lower()
    for term in forbidden_terms:
        if term.lower() in lower:
            hits.append(term)
    return hits


def toxicity_score(text: str) -> float:
    """
    Heuristic toxicity metric:
        - Looks for coarse toxic markers.
        - Normalized to [0.0, 1.0].
    """
    if not text:
        return 0.0
    lower = text.lower()
    markers = ["idiot", "stupid", "hate", "kill", "trash"]
    count = sum(lower.count(m) for m in markers)
    toks = len(text.split()) or 1
    return min(1.0, count / toks)


def scan_bias(text: str) -> List[str]:
    """
    Deterministic bias scan for:
        • age-related terms
        • gendered terms
        • stereotype patterns
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
# 3. PROMPT INJECTION & CONSTITUTIONAL REVIEW
# ============================================================================

_PI_PATTERNS = [
    r"ignore all previous instructions",
    r"disregard prior instructions",
    r"my real task is",
    r"reveal the system prompt",
    r"break character",
    r"disable safety",
]


def detect_prompt_injection(text: str) -> Dict[str, Any]:
    """
    Deterministic prompt injection detector using simple regex patterns.

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

    for pattern in _PI_PATTERNS:
        if re.search(pattern, lower):
            matched.append(pattern)

    if matched:
        return {
            "detected": True,
            "reason": f"Matched injection patterns: {', '.join(matched)}",
            "confidence": 0.95,
            "matched_patterns": matched,
        }

    return {"detected": False, "reason": "", "confidence": 0.0, "matched_patterns": []}


_CONSTITUTION_RULES = {
    "no_hate": lambda t: "hate" not in t.lower(),
    "no_explicit": lambda t: "explicit" not in t.lower(),
    "no_violence": lambda t: "violence" not in t.lower(),
    "tone_professional": lambda t: "idiot" not in t.lower() and "stupid" not in t.lower(),
}


def constitutional_review(text: str) -> Dict[str, Any]:
    """
    Deterministic constitutional review.

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
# 4. SAFETY ENGINE
# ============================================================================


@dataclass
class SafetyEngine:
    """
    Full safety engine that aggregates:

        • PII redaction
        • forbidden content scan
        • toxicity analysis
        • prompt injection detection
        • bias scan
        • constitutional review

    Primary API used by main_v10_9:

        evaluate_content(state: dict, plan: PlanObject) -> safety_report: dict

    This class is deterministic and does not call external LLMs/tools.
    """

    forbidden_terms: List[str] = field(
        default_factory=lambda: ["explicit", "violence", "hate", "slur", "password", "api key"]
    )

    def _extract_content_and_audience(self, state: Dict[str, Any], plan: Any) -> (str, str):
        # Audience.
        audience = str(getattr(plan, "get", lambda *_: None)("audience", None) or state.get("audience", "general"))

        # Content priority:
        #   1. draft_result["draft"] or draft_result["full_text"]
        #   2. messages[-1]["content"]
        #   3. summary
        content = ""

        draft_result = state.get("draft_result") or {}
        draft_payload = draft_result.get("payload") or draft_result
        if isinstance(draft_payload, dict):
            full_text = draft_payload.get("full_text") or ""
            draft_list = draft_payload.get("draft") or []
            if full_text:
                content = full_text
            elif isinstance(draft_list, list) and draft_list:
                content = "\n".join(str(x) for x in draft_list)

        if not content:
            messages = state.get("messages") or []
            if messages:
                last = messages[-1]
                if isinstance(last, dict):
                    content = str(last.get("content", ""))

        if not content:
            content = str(state.get("summary", ""))

        return content, audience

    def validate(self, content: str, audience: str = "general") -> Dict[str, Any]:
        """
        Validate a single content string and return a structured safety report.

        The returned dict is intentionally compatible with SafetyReport-like
        structures but remains plain-JSON.
        """
        redacted = redact_pii(content)
        forbidden = scan_forbidden(content, self.forbidden_terms)
        tox = toxicity_score(content)
        bias_hits = scan_bias(content)
        inj = detect_prompt_injection(content)
        const = constitutional_review(content)

        issues: List[str] = []
        if redacted != content:
            issues.append("pii_redacted")
        issues.extend(f"forbidden:{t}" for t in forbidden)
        if tox > 0.0:
            issues.append("toxicity")
        issues.extend(bias_hits)
        if inj["detected"]:
            issues.append("prompt_injection")
        if not const["passed"]:
            issues.extend(f"constitutional:{v}" for v in const["violations"])

        return {
            "passed": len(issues) == 0,
            "issues": issues,
            "toxicity_score": tox,
            "audience": audience,
            "prompt_injection": inj,
            "constitutional": const,
            "sanitized": redacted,
        }

    def evaluate_content(self, state: Dict[str, Any], plan: Any) -> Dict[str, Any]:
        """
        Main entrypoint used by main_v10_9.

        Extracts the relevant content from the orchestration state and
        evaluates it under the safety engine.
        """
        content, audience = self._extract_content_and_audience(state, plan)
        return self.validate(content, audience=audience)


# ============================================================================
# 5. POLICY ENGINE (META-AWARE, MODE-AWARE)
# ============================================================================


@dataclass
class PolicyEngine:
    """
    High-level policy enforcement engine.

    Maps a safety_report to a policy decision:
        • allow       → proceed
        • retry       → re-run L2 stage
        • replan      → re-run L1 → L2
        • block       → halt workflow (or escalate)

    PolicyEngine is aware of:
        • SafetyMode    (STRICT/BALANCED/PERMISSIVE)
        • Meta biases   (SafetyBias, PlanningBias)
    """

    base_mode: SafetyMode = SafetyMode.BALANCED

    def review(self, safety_report: Dict[str, Any]) -> Dict[str, Any]:
        """
        Return a structured policy decision from a safety_report.

        Shape:
            {
              "decision": "allow|retry|replan|block",
              "reason":   "<short string>",
              "mode":     "<effective mode>",
            }
        """
        issues = safety_report.get("issues", []) or []
        passed = safety_report.get("passed", False)
        inj = safety_report.get("prompt_injection", {}) or {}
        tox = float(safety_report.get("toxicity_score", 0.0))

        # Combine base mode with meta-profile adjustments.
        mode = _derive_mode_from_meta(self.base_mode)

        if passed and not issues:
            return {"decision": "allow", "reason": "no_issues_detected", "mode": mode.value}

        has_prompt_injection = inj.get("detected", False) or any(
            "prompt_injection" in str(x) for x in issues
        )
        has_const_violation = any("constitutional" in str(x) for x in issues)
        has_toxicity = any("toxicity" in str(x) for x in issues)
        has_forbidden = any(str(x).startswith("forbidden:") for x in issues)
        has_pii_redacted = any("pii_redacted" in str(x) for x in issues)

        # STRICT: block on any serious signal.
        if mode == SafetyMode.STRICT:
            if has_prompt_injection or has_const_violation or has_forbidden or has_toxicity:
                return {"decision": "block", "reason": "strict_block_on_issue", "mode": mode.value}

        # BALANCED: focus on injection + policy as blockers.
        if mode == SafetyMode.BALANCED:
            if has_prompt_injection:
                return {"decision": "block", "reason": "prompt_injection_detected", "mode": mode.value}
            if has_forbidden:
                return {"decision": "replan", "reason": "forbidden_content", "mode": mode.value}

        # PERMISSIVE: primarily react to injection; policy types cause replan.
        if mode == SafetyMode.PERMISSIVE:
            if has_prompt_injection:
                return {"decision": "block", "reason": "prompt_injection_detected", "mode": mode.value}
            if has_forbidden:
                return {"decision": "replan", "reason": "policy_violation", "mode": mode.value}

        # Constitutional violations (any mode): prefer replan.
        if has_const_violation:
            return {"decision": "replan", "reason": "constitutional_violations", "mode": mode.value}

        # Toxicity: suggest retry (e.g., regenerate safer variant).
        if has_toxicity or tox > 0.25:
            return {"decision": "retry", "reason": "toxicity_exceeded", "mode": mode.value}

        # PII redaction alone is not a blocker: allow but record.
        if has_pii_redacted:
            return {"decision": "allow", "reason": "pii_was_redacted", "mode": mode.value}

        # Fallback: there are issues, but none clearly mapped.
        if issues:
            if mode == SafetyMode.STRICT:
                return {"decision": "block", "reason": "unclassified_safety_issue_strict", "mode": mode.value}
            if mode == SafetyMode.BALANCED:
                return {"decision": "replan", "reason": "unclassified_safety_issue", "mode": mode.value}
            return {"decision": "allow", "reason": "issues_non_blocking_permissive", "mode": mode.value}

        return {"decision": "allow", "reason": "default_allow", "mode": mode.value}


# ============================================================================
# 6. ARBITRATION ENGINE (policy → orchestrator hint)
# ============================================================================


@dataclass
class ArbitrationEngine:
    """
    Normalize PolicyEngine decisions into ArbitrationDecision objects.

    Actions (normalized):

        • proceed   — workflow may continue
        • retry_l2  — re-run L2 stage (same plan)
        • rerun_l1  — re-plan at L1 then re-run L2
        • halt      — stop the workflow
        • escalate  — escalate to external HIL/safety review
    """

    def arbitrate(self, policy_decision: Dict[str, Any], safety_report: Dict[str, Any]) -> ArbitrationDecision:
        decision = policy_decision.get("decision", "allow")
        mode = policy_decision.get("mode", SafetyMode.BALANCED.value)

        if decision == "allow":
            return ArbitrationDecision(
                action="proceed",
                reason=policy_decision.get("reason", "no_issues"),
                metadata={"mode": mode, "safety_report": safety_report},
            )

        if decision == "retry":
            return ArbitrationDecision(
                action="retry_l2",
                reason=policy_decision.get("reason", "retry_requested"),
                metadata={"mode": mode, "safety_report": safety_report},
            )

        if decision == "replan":
            return ArbitrationDecision(
                action="rerun_l1",
                reason=policy_decision.get("reason", "replan_requested"),
                metadata={"mode": mode, "safety_report": safety_report},
            )

        if decision == "block":
            issues = safety_report.get("issues", []) or []
            has_prompt_injection = any("prompt_injection" in str(x) for x in issues)
            has_const = any("constitutional" in str(x) for x in issues)

            if has_prompt_injection or has_const:
                return ArbitrationDecision(
                    action="escalate",
                    reason=policy_decision.get("reason", "blocked_escalation"),
                    metadata={"mode": mode, "safety_report": safety_report},
                )
            return ArbitrationDecision(
                action="halt",
                reason=policy_decision.get("reason", "blocked_by_policy"),
                metadata={"mode": mode, "safety_report": safety_report},
            )

        return ArbitrationDecision(
            action="proceed",
            reason="default_allow",
            metadata={"mode": mode, "safety_report": safety_report},
        )
