# FILE: l5.py
"""
Unified L5 Safety & Policy Layer (v10_10) — CONSTITUTIONAL GOVERNANCE

This module implements Pillar 9 (Safety & Policy).
It acts as the "Supreme Court" of the architecture, interpreting abstract
safety policies and rendering verdicts on agent outputs.

Responsibilities:
    1. Policy Management: Source of Truth for Safety Modes (Strict/Balanced).
    2. Constitutional Review: Delegate judgment to `ConstitutionalSafetyAgent`.
    3. Arbitration: Map judgments to Workflow Actions (Halt/Retry/Proceed).

Refactor Highlights (v10_10):
    • Removes Regex/Keyword lists.
    • Implements semantic policy checks.
    • strictly typed `ArbitrationDecision` outputs.
"""

from __future__ import annotations

from typing import Any, Dict, List

from models import (
    PlanObject,
    SafetyPayload,
    SafetyPolicy,
    SafetyRule,
    SafetyMode,
    ArbitrationDecision,
    SafetyFinding
)
from cognitive_agents import ConstitutionalSafetyAgent
from meta_profile import get_safety_bias

# =============================================================================
# 1. POLICY FACTORY (The Constitution)
# =============================================================================

class PolicyFactory:
    """
    Defines the "Laws" the agent must follow.
    In a larger system, these might be loaded from a database.
    """

    @staticmethod
    def get_policy(mode: SafetyMode) -> SafetyPolicy:
        
        # Common Rules
        base_rules = [
            SafetyRule(rule_id="no_pii", description="Do not output personally identifiable information (emails, phone numbers).", severity="high", category="pii"),
            SafetyRule(rule_id="no_harm", description="Do not generate hate speech, violence, or self-harm content.", severity="critical", category="harm"),
        ]

        # Mode-Specific Rules
        if mode == SafetyMode.STRICT:
            return SafetyPolicy(
                policy_id="strict_v1",
                mode=mode,
                rules=base_rules + [
                    SafetyRule(rule_id="tone_check", description="Maintain a formal, objective tone. No slang.", severity="medium", category="tone"),
                    SafetyRule(rule_id="no_speculation", description="Do not speculate on financial or medical outcomes.", severity="high", category="risk")
                ],
                threshold=0.0 # Zero tolerance
            )
        
        elif mode == SafetyMode.PERMISSIVE:
            return SafetyPolicy(
                policy_id="permissive_v1",
                mode=mode,
                rules=base_rules, # Only base PII/Harm rules
                threshold=0.8
            )
        
        # Default: Balanced
        return SafetyPolicy(
            policy_id="balanced_v1",
            mode=SafetyMode.BALANCED,
            rules=base_rules + [
                 SafetyRule(rule_id="professionalism", description="Maintain professional demeanor.", severity="low", category="tone")
            ],
            threshold=0.5
        )

# =============================================================================
# 2. SAFETY ENGINE (The Judge)
# =============================================================================

class SafetyEngine:
    """
    Orchestrates the review process.
    """
    def __init__(self):
        self.agent = ConstitutionalSafetyAgent()

    async def evaluate_content(self, state: Dict[str, Any], plan: PlanObject) -> SafetyPayload:
        """
        Conducts a safety review of the current state.
        """
        # 1. Identify Content
        # We check the 'draft_result' first, as that's the output we care about.
        # Fallback to messages if drafting hasn't happened.
        content_source = "unknown"
        content_text = ""
        
        if state.get("draft_result"):
            draft = state["draft_result"]
            # Handle Pydantic serialization dicts or objects
            if isinstance(draft, dict):
                content_text = draft.get("full_text", "")
            elif hasattr(draft, "full_text"):
                content_text = draft.full_text
            content_source = "draft_result"
        
        if not content_text:
            msgs = state.get("messages", [])
            if msgs:
                content_text = msgs[-1].get("content", "")
                content_source = "last_message"

        if not content_text:
            # Nothing to check
            return SafetyPayload(blocked=False, findings=[], policy_version="none")

        # 2. Determine Policy Mode (Meta-Aware)
        meta_bias = get_safety_bias()
        # Priority: Meta-Profile Bias > Plan Config > Default
        if meta_bias.get("bias_safety_strict"):
            target_mode = SafetyMode.STRICT
        else:
            # Map string from plan meta to Enum, default balanced
            mode_str = plan.meta.get("safety_mode", "balanced")
            try:
                target_mode = SafetyMode(mode_str)
            except ValueError:
                target_mode = SafetyMode.BALANCED

        policy = PolicyFactory.get_policy(target_mode)

        # 3. Execute Semantic Review (The Agent)
        payload = await self.agent.evaluate(content_text, policy)
        
        return payload


# =============================================================================
# 3. ARBITRATION ENGINE (The Enforcer)
# =============================================================================

class ArbitrationEngine:
    """
    Converts Safety Judgments into Workflow Actions.
    """

    def arbitrate(self, safety_result: SafetyPayload) -> ArbitrationDecision:
        """
        Decides next steps based on the payload.
        """
        # 1. Clean Pass
        if not safety_result.blocked and not safety_result.findings:
            return ArbitrationDecision(
                action="proceed",
                reason="Safety check passed.",
                metadata={"policy": safety_result.policy_version}
            )

        # 2. Blocked
        if safety_result.blocked:
            # Check severity of findings
            critical = any(f.rule_id in ["no_harm", "no_pii"] for f in safety_result.findings)
            
            if critical:
                return ArbitrationDecision(
                    action="halt",
                    reason="Critical safety violation detected.",
                    metadata={"findings": [f.rule_id for f in safety_result.findings]}
                )
            
            # If blocked but not critical, maybe retry?
            return ArbitrationDecision(
                action="retry_l2", # Ask L2 to rewrite
                reason="Safety policy violation (non-critical). Requesting rewrite.",
                metadata={"findings": [f.rule_id for f in safety_result.findings]}
            )

        # 3. Warnings (Not blocked, but findings exist)
        return ArbitrationDecision(
            action="proceed",
            reason="Proceeding with warnings.",
            metadata={"warnings": [f.rule_id for f in safety_result.findings]}
        )
