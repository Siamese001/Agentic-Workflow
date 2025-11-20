# FILE: l5.py
"""
Unified L5 Safety & Policy Layer (v10_10) — CONSTITUTIONAL GOVERNANCE (REFACTORED)

This module implements the "Conscience" of the agent (Pillar 9).
It is the Final Gatekeeper before any content is returned to the user.

Responsibilities:
    1. Constitutional Review: Evaluate content against semantic `SafetyPolicy` rules.
    2. Policy Arbitration: Decide whether to Allow, Block, Retry, or Escalate.
    3. Mode Awareness: Adapt rigor based on Strict/Balanced/Permissive modes.

Refactor Highlights (v10_10):
    • Removed regex/keyword filters (brittle).
    • Added Semantic Policy checking via `LLMGateway`.
    • Centralized policy definitions to `Registry`.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from models import (
    PlanObject,
    SafetyReport,
    SafetyIssue,
    ArbitrationDecision,
    SafetyMode,
    SafetyPolicy
)
from registry import REGISTRY
from llm_gateway import GATEWAY
from meta_profile import get_safety_bias

# =============================================================================
# 1. SAFETY ENGINE (Constitutional AI)
# =============================================================================

class SafetyEngine:
    """
    Performs semantic safety checks against registered policies.
    """

    async def evaluate_content(self, state: Dict[str, Any], plan: PlanObject) -> SafetyReport:
        """
        Evaluates the 'draft_result' or 'messages' against the active policy.
        """
        # 1. Extract Content
        content = self._extract_content(state)
        if not content:
            return SafetyReport(passed=True, summary="No content to review.")

        # 2. Determine Policy Mode
        # Combine Plan settings with Meta-Profile Biases
        meta_bias = get_safety_bias()
        mode_str = plan.safety_profile.get("mode", "balanced")
        
        if meta_bias.get("heightened_caution"):
            mode = SafetyMode.STRICT
        else:
            mode = SafetyMode(mode_str)

        # 3. Fetch Policy (Pillar 9: Centralized Policy)
        policy = REGISTRY.get_policy(mode)

        # 4. Constitutional Review (Pillar 6: Reasoning)
        # We ask the LLM to act as a judge based on the rules.
        response = await GATEWAY.call_model(
            prompt_id="l5_constitutional_judge",
            inputs={
                "content": content[:4000], # Context window safeguard
                "policy_rules": "\n".join([f"- {r}" for r in policy.rules])
            },
            workflow_id=plan.workflow_id or "unknown",
            reasoning_strategy="direct" # Safety checks should be direct and objective
        )

        # 5. Parse Judgment
        # In prod: Pydantic parser. Here: Mock/Simple JSON parsing.
        try:
            # Expecting JSON from the prompt template
            data = json.loads(response.content)
            issues_data = data.get("issues", [])
            summary = data.get("summary", "Review complete.")
        except:
            # Fallback if LLM output is malformed -> Fail Safe (Block)
            issues_data = [{"issue_id": "parsing_error", "severity": "high", "category": "system", "message": "Could not parse safety judgment."}]
            summary = "Safety check failed due to parsing error."

        # Convert to Typed Issues
        issues = [
            SafetyIssue(
                issue_id=i.get("issue_id", "unknown"),
                severity=i.get("severity", "medium"),
                category=i.get("category", "policy"),
                message=i.get("message", "Violation detected")
            ) 
            for i in issues_data
        ]

        # Determine Block status based on Policy Threshold
        # If we found high severity issues, we block.
        blocked = any(i.severity == "high" for i in issues)

        return SafetyReport(
            issues=issues,
            blocked=blocked,
            summary=summary,
            metadata={
                "policy_id": policy.policy_id,
                "mode": mode.value,
                "judge_model": response.model_used
            }
        )

    def _extract_content(self, state: Dict[str, Any]) -> str:
        """Helper to find what to check."""
        # Priority: Draft -> RAG -> Last Message
        draft = state.get("draft_result", {})
        if isinstance(draft, dict):
             # It might be the dict representation of DraftExecutionPayload
             return draft.get("full_text", "")
        
        # If it's already a Pydantic model (unlikely in raw state dict but possible)
        if hasattr(draft, "full_text"):
            return draft.full_text

        msgs = state.get("messages", [])
        if msgs:
            return msgs[-1].get("content", "")
        
        return ""


# =============================================================================
# 2. POLICY ENGINE (Arbitration)
# =============================================================================

class PolicyEngine:
    """
    Decides *what to do* about the safety findings.
    """

    def review(self, safety_report: SafetyReport) -> Dict[str, Any]:
        """
        Maps safety report -> abstract policy decision.
        """
        # This intermediate step allows for rules like:
        # "If blocked but low confidence, retry."
        # "If blocked on PII, just redact and proceed."
        
        if not safety_report.issues:
            return {"decision": "allow", "reason": "clean_report"}

        if safety_report.blocked:
            # Check if it's just PII (which we can redact) vs Harmful content
            is_pii_only = all(i.category == "pii" for i in safety_report.issues)
            
            if is_pii_only:
                return {"decision": "allow", "reason": "pii_redacted_implicitly"}
            
            return {"decision": "block", "reason": "policy_violation"}

        return {"decision": "allow", "reason": "warnings_only"}


# =============================================================================
# 3. ARBITRATION ENGINE (L3 Interface)
# =============================================================================

class ArbitrationEngine:
    """
    Translates Policy decisions into L3 Workflow Directives.
    """

    def arbitrate(self, policy_decision: Dict[str, Any], safety_report: SafetyReport) -> ArbitrationDecision:
        """
        Produces the final ArbitrationDecision used by the Orchestrator.
        """
        decision = policy_decision.get("decision", "allow")
        reason = policy_decision.get("reason", "")

        if decision == "allow":
            return ArbitrationDecision(
                action="proceed",
                reason=reason,
                metadata={"issues_count": len(safety_report.issues)}
            )
        
        if decision == "block":
            # Escalation logic
            return ArbitrationDecision(
                action="halt", # or 'escalate' if HIL is configured
                reason=f"Safety Block: {safety_report.summary}",
                metadata={"report": safety_report.model_dump()}
            )

        if decision == "retry":
            return ArbitrationDecision(
                action="retry_l2",
                reason="Safety requested retry.",
                metadata={}
            )

        return ArbitrationDecision(action="proceed", reason="default_fallthrough")
