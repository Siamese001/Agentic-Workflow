# FILE: v10_9_clean/l5.py
"""
Unified L5 Safety & Policy Layer (v10_9)

This file contains all high-level safety, policy, constitutional, and routing
logic for the v10_9 agentic architecture.

Included components:
    • SafetyContracts
    • Redaction utilities
    • SafetyEngine
    • PolicyEngine
    • ArbitrationEngine
    • ModelRouting (model selection policy)

L5 is authoritative for:
    • safety gating
    • policy-compliant routing
    • sanitization
    • fallback paths
    • arbitration decisions

Pure safety/policy:
    • NO planning (L1)
    • NO execution (L2)
    • NO orchestration (L3)
    • NO state management (L4)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List

from exceptions import SafetyException
from constants import CANONICAL_MODEL_DEFAULT


# ============================================================================
# SAFETY CONTRACTS
# ============================================================================

@dataclass
class SafetyContracts:
    """
    Defines safety validation rules and metadata for:
        • PII redaction
        • forbidden content
        • model routing constraints
        • allowed audience
    """

    allowed_audience: List[str] = field(default_factory=lambda: ["general", "professional"])
    forbidden_terms: List[str] = field(default_factory=lambda: ["explicit", "violence", "hate"])
    pii_patterns: List[str] = field(default_factory=lambda: ["@", "+1", "xxx-xxx"])
    max_toxicity: float = 0.25


DEFAULT_SAFETY_CONTRACTS = SafetyContracts()


# ============================================================================
# REDACTION UTILITIES
# ============================================================================

import re

_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_PHONE_RE = re.compile(r"\b(?:\+?1[ -]?)?\(?\d{3}\)?[ -]?\d{3}[ -]?\d{4}\b")

def redact_pii(text: str) -> str:
    """Remove emails and phone numbers deterministically."""
    if not text:
        return text
    text = _EMAIL_RE.sub("[EMAIL_REDACTED]", text)
    text = _PHONE_RE.sub("[PHONE_REDACTED]", text)
    return text


def scan_forbidden(text: str, forbidden_terms: List[str]) -> List[str]:
    """Return list of forbidden terms found in text."""
    issues = []
    if not text:
        return issues
    lower = text.lower()
    for term in forbidden_terms:
        if term in lower:
            issues.append(term)
    return issues


# ============================================================================
# SAFETY ENGINE
# ============================================================================

class SafetyEngine:
    """
    Performs deterministic safety checks:
        • PII redaction
        • forbidden content scan
        • toxicity heuristic
        • audience restrictions
    """

    def __init__(self, contracts: SafetyContracts | None = None):
        self.contracts = contracts or DEFAULT_SAFETY_CONTRACTS

    def validate(self, content: str, audience: str = "general") -> Dict[str, Any]:
        if audience not in self.contracts.allowed_audience:
            raise SafetyException(f"Audience '{audience}' not allowed.")

        if not isinstance(content, str):
            content = str(content)

        redacted = redact_pii(content)
        forbidden_hits = scan_forbidden(content, self.contracts.forbidden_terms)

        # Simple toxicity heuristic:
        toxicity_score = float(content.count("!") / (len(content.split()) + 1))
        toxic = toxicity_score > self.contracts.max_toxicity

        issues = []
        if redacted != content:
            issues.append("pii_redacted")
        if forbidden_hits:
            issues.extend([f"forbidden:{x}" for x in forbidden_hits])
        if toxic:
            issues.append("toxicity")

        return {
            "passed": len(issues) == 0,
            "issues": issues,
            "sanitized": redacted,
            "toxicity_score": toxicity_score,
            "audience": audience,
        }


# ============================================================================
# POLICY ENGINE
# ============================================================================

class PolicyEngine:
    """
    High-level policy enforcement engine that:
        • inspects safety report
        • blocks unsafe outputs
        • adjusts plan metadata
        • instructs orchestration to retry or replan
    """

    def review(self, safety_report: Dict[str, Any]) -> Dict[str, Any]:
        issues = safety_report.get("issues", [])
        passed = safety_report.get("passed", False)

        if passed:
            return {"decision": "allow", "reason": "safe"}

        if "toxicity" in issues:
            return {"decision": "retry", "reason": "toxicity_detected"}

        if any("forbidden" in x for x in issues):
            return {"decision": "replan", "reason": "forbidden_content"}

        if "pii_redacted" in issues:
            return {"decision": "allow", "reason": "pii_redacted_auto"}

        return {"decision": "block", "reason": "unclassified_safety_issue"}


# ============================================================================
# ARBITRATION ENGINE
# ============================================================================

class ArbitrationEngine:
    """
    Determines the final action after L2 execution, L4 state integration,
    and L5 policy review.

    Possible outcomes:
        • allow
        • retry
        • replan
        • block
    """

    def decide(self, policy_decision: Dict[str, Any], safety_report: Dict[str, Any]) -> Dict[str, Any]:
        decision = policy_decision.get("decision")

        if decision == "allow":
            return {"action": "proceed"}

        if decision == "retry":
            return {"action": "retry_l2"}

        if decision == "replan":
            return {"action": "rerun_l1"}

        if decision == "block":
            return {"action": "halt"}

        return {"action": "proceed"}


# ============================================================================
# MODEL ROUTING POLICY
# ============================================================================

@dataclass
class RoutingCriteria:
    task_type: str
    complexity: str = "low"         # low | medium | high
    latency_target_ms: int = 2000
    cost_ceiling_usd: float = 0.05
    risk_level: str = "normal"      # normal | strict | high_safety
    model_available: bool = True


@dataclass
class RoutingDecision:
    model: str
    endpoint: str
    rationale: str


class ModelRouter:
    """
    Determines *which model* and *which endpoint* should be used
    based on routing criteria + META_PROFILE flags.
    """

    def select(self, criteria: RoutingCriteria) -> RoutingDecision:
        # High complexity or risk → stronger model
        if criteria.complexity == "high" or criteria.risk_level in ("strict", "high_safety"):
            selected = RoutingDecision(
                model="gpt-4.1",
                endpoint="standard",
                rationale="High complexity or elevated risk"
            )
        # Low latency → lightweight fast model
        elif criteria.latency_target_ms < 1000:
            selected = RoutingDecision(
                model="gpt-4.1-mini",
                endpoint="fast",
                rationale="Low latency target"
            )
        else:
            selected = RoutingDecision(
                model="gpt-4.1-mini",
                endpoint="standard",
                rationale="Default route"
            )

        # Fallback if model is unavailable
        if not criteria.model_available:
            selected = RoutingDecision(
                model="gpt-4.1-mini",
                endpoint="fast",
                rationale="Primary route unavailable → fallback"
            )

        return selected
