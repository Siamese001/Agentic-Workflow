"""Primary orchestration stack for LIC outreach."""
from __future__ import annotations

from dataclasses import dataclass

from ..agents.k1_router_agent import RouterAgent
from ..agents.k3_message_architect import MessageArchitect
from ..agents.k5_cta_agent import CTAAgent
from ..agents.k6_signature_agent import SignatureAgent
from ..agents.k7_validator_agent import ValidationResult, ValidatorAgent
from ..reasoning.toggles import ReasoningToggles
from ..safety.bias_auditor import audit_bias
from ..safety.pii_sanitizer import sanitize_pii
from ..safety.prompt_injection import detect_injection


@dataclass(frozen=True)
class StackInputs:
    prompt: str
    company_id: str | None = None
    contact_id: str | None = None


class OutreachStack:
    """Coordinates the LIC outreach workflow."""

    def __init__(self, toggles: ReasoningToggles):
        self.toggles = toggles
        self.router = RouterAgent()
        self.architect = MessageArchitect(toggles)
        self.cta = CTAAgent()
        self.signature = SignatureAgent()
        self.validator = ValidatorAgent()

    def run(self, inputs: StackInputs) -> dict:
        finding = detect_injection(inputs.prompt)
        if finding.is_injection and finding.severity == "high":
            return {"end": "safety_block", "reason": finding.rationale}

        sanitized_inputs, pii_map = sanitize_pii(inputs)
        bias = audit_bias(sanitized_inputs)
        route = self.router.route(sanitized_inputs, bias)

        draft = self.architect.compose(sanitized_inputs, route)
        draft = self.cta.adjust(draft, route)
        draft = self.signature.attach(draft, route)

        verdict: ValidationResult = self.validator.check(draft, route, pii_map)
        return {"draft": draft, "verdict": verdict}
