"""Content policy stack for orchestrator-level gating."""
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class ContentPolicyRule(BaseModel):
    """Represents a single content policy rule."""

    id: str
    description: str
    forbidden_terms: List[str] = []
    required_context: Optional[str] = None


class PolicyDecision(BaseModel):
    """Result emitted by the policy stack."""

    allowed: bool
    reason: Optional[str] = None


RULEBOOK: List[ContentPolicyRule] = [
    ContentPolicyRule(
        id="disallowed_weapons",
        description="Rejects requests involving weapons or explosives.",
        forbidden_terms=["weapon", "bomb", "explosive", "grenade"],
    ),
    ContentPolicyRule(
        id="disallowed_personal_data",
        description="Prevents misuse of sensitive personal information.",
        forbidden_terms=["ssn", "social security", "credit card"],
    ),
]


class PolicyStack:
    """Evaluates content against a configurable rulebook."""

    def __init__(
        self,
        workflow_context: Any,
        debug_mode: bool = False,
        *,
        rulebook: Optional[List[ContentPolicyRule]] = None,
    ) -> None:
        self.workflow_context = workflow_context
        self.debug_mode = debug_mode
        self._rules = list(rulebook or RULEBOOK)

    def guard_user_input(self, user_input: str) -> PolicyDecision:
        text = user_input or ""
        return self._evaluate_text(text)

    def guard_plan(self, plan: Dict[str, Any]) -> PolicyDecision:
        serialized = self._serialize_payload(plan)
        return self._evaluate_text(serialized)

    def guard_output(self, output: Dict[str, Any]) -> PolicyDecision:
        serialized = self._serialize_payload(output)
        return self._evaluate_text(serialized)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _evaluate_text(self, text: str) -> PolicyDecision:
        lowered = (text or "").lower()
        for rule in self._rules:
            if not rule.forbidden_terms:
                continue
            if rule.required_context and rule.required_context.lower() not in lowered:
                continue
            for term in rule.forbidden_terms:
                candidate = term.lower()
                if candidate and candidate in lowered:
                    reason = (
                        f"Rule {rule.id} triggered: {rule.description} (term '{term}')"
                    )
                    return PolicyDecision(allowed=False, reason=reason)
        return PolicyDecision(allowed=True)

    def _serialize_payload(self, payload: Any) -> str:
        if payload is None:
            return ""
        if isinstance(payload, str):
            return payload
        if isinstance(payload, BaseModel):
            return payload.model_dump_json()
        if isinstance(payload, dict):
            try:
                return json.dumps(payload, sort_keys=True)
            except (TypeError, ValueError):
                return str(payload)
        try:
            return json.dumps(payload, default=str, sort_keys=True)
        except (TypeError, ValueError):
            return str(payload)
