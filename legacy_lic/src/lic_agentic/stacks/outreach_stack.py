"""Primary orchestration stack for LIC outreach."""
from __future__ import annotations

from dataclasses import dataclass

from ..agents.k1_router_agent import RouterAgent
from ..agents.k3_message_architect import DraftPackage, MessageArchitect
from ..agents.k5_cta_agent import CTAAgent
from ..agents.k6_signature_agent import SignatureAgent
from ..agents.k7_validator_agent import ValidationResult, ValidatorAgent
from ..qa import QAValidator
from ..reasoning.toggles import ReasoningToggles
from ..safety.bias_auditor import audit_bias
from ..safety.pii_sanitizer import sanitize_pii
from ..safety.prompt_injection import detect_injection
from ..telemetry import PolicyController


@dataclass(frozen=True)
class StackInputs:
    prompt: str
    company_id: str | None = None
    contact_id: str | None = None


class OutreachStack:
    """Coordinates the LIC outreach workflow."""  # pragma: no cover

    def __init__(self, toggles: ReasoningToggles):
        self.toggles = toggles
        self.policy = PolicyController()
        self.router = RouterAgent()
        self.architect = MessageArchitect(toggles)
        self.cta = CTAAgent()
        self.signature = SignatureAgent()
        self.validator = ValidatorAgent(qa_validator=QAValidator(), max_retries=1)

    def run(self, inputs: StackInputs) -> dict:
        finding = detect_injection(inputs.prompt)
        if finding.is_injection and finding.severity == "high":
            return {"end": "safety_block", "reason": finding.rationale}

        sanitized_inputs, pii_map = sanitize_pii(inputs)
        bias = audit_bias(sanitized_inputs)
        route = self.router.route(sanitized_inputs, bias)

        package = self.architect.compose(
            sanitized_inputs,
            route,
            max_calls=self._max_retrieval_calls(),
        )
        if isinstance(package, DraftPackage):
            draft = package.draft
            artifacts = dict(package.artifacts)
            latency_ms = package.total_latency_ms or 0
        else:
            draft = str(package)
            artifacts = {"baseline": "Value proposition here."}
            latency_ms = 0

        draft = self.cta.adjust(draft, route)
        draft = self.signature.attach(draft, route)

        verdict: ValidationResult = self.validator.check(
            draft,
            route,
            pii_map,
            artifacts=artifacts,
        )

        policy_update = self.policy.update(
            latency_p95_ms=latency_ms or 1000,
            qa_pass_rate=1.0 if verdict.passed else 0.0,
            token_drift=self.validator.metrics.token_drift(),
        )
        self._apply_policy_update(policy_update)

        return {"draft": verdict.final_draft, "verdict": verdict, "artifacts": artifacts}

    def _max_retrieval_calls(self) -> int:
        base = self.architect._default_budget()
        scaled = int(round(base * self.policy.budget_multiplier))
        return max(1, min(6, scaled))

    def _apply_policy_update(self, update) -> None:
        toggles_dict = self.toggles.model_dump()
        toggles_dict.update(
            {
                "temperature_cap": update.temperature_cap,
                "tot_branches": update.tot_branches,
            }
        )
        self.toggles = ReasoningToggles(**toggles_dict)
        self.architect.update_toggles(self.toggles)
