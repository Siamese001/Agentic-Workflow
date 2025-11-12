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

        package = self.architect.compose(sanitized_inputs, route)
        draft = self.cta.adjust(package.draft, route)
        draft = self.signature.attach(draft, route)

        def _retry(
            qa_result, current_draft, current_artifacts
        ) -> tuple[str, dict[str, str]] | None:
            refreshed = self.architect.compose(sanitized_inputs, route)
            refreshed_draft = self.cta.adjust(refreshed.draft, route)
            refreshed_draft = self.signature.attach(refreshed_draft, route)
            if refreshed_draft == current_draft:
                return None
            return refreshed_draft, refreshed.artifacts

        verdict: ValidationResult = self.validator.check(
            draft,
            route,
            pii_map,
            artifacts=package.artifacts,
            retry_fn=_retry,
            token_count=len(draft.split()),
            latency_ms=package.total_latency_ms,
        )
        return {"draft": verdict.final_draft, "verdict": verdict}
