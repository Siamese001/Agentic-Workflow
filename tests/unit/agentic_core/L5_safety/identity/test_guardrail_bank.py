"""Unit tests for agentic_core.L5_safety.identity.guardrail_bank.

W2 (plan adg-testing-hotspots-wave-plan-a7f3c1) — Core P1 L5 safety chokepoint (x2.0).
``guardrail_bank`` (fan_in=14) resolves guardrail-family outcomes into a single bank
verdict by strict precedence (reject > remediate > allow), enforces G-15
(hard_constraint forbids remediate), and composes egress most-restrictive action.
"""

from __future__ import annotations

import pytest

from agentic_core.L5_safety.identity.guardrail_bank import (
    EgressInspectionResult,
    GuardrailBankVerdict,
    GuardrailFamily,
    GuardrailOutcome,
    resolve_bank_verdict,
)


def _outcome(
    action: str,
    *,
    layer: str = "client_universal",
    stage: str = "ingress",
    score: float = 0.5,
    hard: bool = False,
    evidence: str = "ev",
) -> GuardrailOutcome:
    return GuardrailOutcome(
        family=GuardrailFamily.KEYWORD, layer=layer, stage=stage,  # type: ignore[arg-type]
        action=action, score=score, evidence=evidence, hard_constraint=hard,  # type: ignore[arg-type]
    )


class TestGuardrailFamily:
    def test_is_str_enum_closed_set(self) -> None:
        assert isinstance(GuardrailFamily.PII, str)
        assert len(list(GuardrailFamily)) == 11
        assert GuardrailFamily.PII == "pii"


class TestGuardrailOutcome:
    def test_valid(self) -> None:
        assert _outcome("allow").action == "allow"

    @pytest.mark.parametrize("score", [-0.1, 1.1, 2.0])
    def test_score_out_of_range_raises(self, score: float) -> None:
        with pytest.raises(ValueError, match="score must be"):
            _outcome("allow", score=score)

    def test_bad_action_raises(self) -> None:
        with pytest.raises(ValueError, match="action must be"):
            _outcome("nope")

    def test_hard_constraint_forbids_remediate(self) -> None:
        with pytest.raises(ValueError, match="G-15"):
            _outcome("remediate", hard=True)

    def test_empty_evidence_raises(self) -> None:
        with pytest.raises(ValueError, match="evidence required"):
            _outcome("allow", evidence="")

    def test_to_dict_uses_family_value(self) -> None:
        assert _outcome("allow").to_dict()["family"] == "keyword"


class TestResolveBankVerdict:
    def test_empty_bank_allows(self) -> None:
        v = resolve_bank_verdict("ingress", ())
        assert v.verdict == "allow"
        assert v.digest  # deterministic non-empty digest

    def test_all_allow(self) -> None:
        v = resolve_bank_verdict("ingress", (_outcome("allow"), _outcome("allow")))
        assert v.verdict == "allow"

    def test_remediate_wins_over_allow(self) -> None:
        v = resolve_bank_verdict("ingress", (_outcome("allow"), _outcome("remediate")))
        assert v.verdict == "remediate"

    def test_reject_wins_over_remediate(self) -> None:
        v = resolve_bank_verdict("ingress", (_outcome("remediate"), _outcome("reject", hard=True)))
        assert v.verdict == "reject"

    def test_layer_ordering_client_universal_first(self) -> None:
        v = resolve_bank_verdict(
            "ingress",
            (_outcome("allow", layer="agent_domain"), _outcome("allow", layer="client_universal")),
        )
        assert v.ordered_outcomes[0].layer == "client_universal"

    def test_digest_is_deterministic(self) -> None:
        outcomes = (_outcome("allow"), _outcome("remediate"))
        assert resolve_bank_verdict("egress", outcomes).digest == resolve_bank_verdict("egress", outcomes).digest


class TestGuardrailBankVerdict:
    def test_requires_digest(self) -> None:
        with pytest.raises(ValueError, match="digest required"):
            GuardrailBankVerdict(stage="ingress", verdict="allow", ordered_outcomes=(), digest="")


class TestEgressInspectionResult:
    def _egress_bank(self, action: str = "allow") -> GuardrailBankVerdict:
        return resolve_bank_verdict("egress", (_outcome(action, stage="egress", hard=(action == "reject")),))

    def test_valid_allow(self) -> None:
        r = EgressInspectionResult(
            bank_verdict=self._egress_bank("allow"),
            guard_model_outcome=None,
            final_action="allow",
        )
        assert r.final_action == "allow"

    def test_non_egress_bank_stage_raises(self) -> None:
        ingress_bank = resolve_bank_verdict("ingress", (_outcome("allow"),))
        with pytest.raises(ValueError, match="must be 'egress'"):
            EgressInspectionResult(bank_verdict=ingress_bank, guard_model_outcome=None, final_action="allow")

    def test_final_action_must_be_most_restrictive(self) -> None:
        with pytest.raises(ValueError, match="most"):
            EgressInspectionResult(
                bank_verdict=self._egress_bank("reject"),
                guard_model_outcome=None,
                final_action="allow",  # bank said reject → allow is wrong
            )
