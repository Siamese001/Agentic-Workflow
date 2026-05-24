"""Unit tests for agentic_core multi-provider judge panel harness."""

from __future__ import annotations

import pytest

from agentic_core.runtime.judges.panel import (
    AdapterInvokeError,
    CanonicalJudgeContract,
    DeclaredTransportPolicy,
    GateClosureMap,
    GateClosureRule,
    JudgePanelRunner,
    PanelAdapterRegistry,
    audit_transport_parity,
    normalize_panel_score,
    reconcile_against_gate_closures,
    validate_contract,
)
from agentic_core.runtime.judges.panel.panel_types import PanelJudgeOutcome, TransportReceipt


def _contract() -> CanonicalJudgeContract:
    return CanonicalJudgeContract(
        section_id="executive_summary",
        user_prompt="Grade this output. DETERMINISTIC_GATE_SUMMARY: {}",
        deterministic_gate_summary={
            "x2_gate": {"pass": True, "detail": "ok"},
        },
        proof_boundary={
            "jd_is_targeting_context_only": True,
            "briefing_is_targeting_context_only": True,
            "judges_must_not_rewrite": True,
        },
    )


def _body(score: float = 4.2, *, pass_: bool = True) -> dict:
    return {
        "score_scale": "0_to_5",
        "score": score,
        "threshold": 4.0,
        "pass": pass_,
        "decisive_failure": False,
        "findings": [],
        "cited_sentence_indexes": [1],
        "remediation_suggestions": [],
    }


class _FakeAdapter:
    def __init__(
        self,
        provider_key: str,
        *,
        body: dict | None = None,
        max_tokens: int = 4096,
        fail_once: bool = False,
    ) -> None:
        self.provider_key = provider_key
        self._body = body or _body()
        self._max_tokens = max_tokens
        self._fail_once = fail_once
        self._calls = 0

    def declared_policy(self, *, attempt: int = 1) -> DeclaredTransportPolicy:
        return DeclaredTransportPolicy(
            max_output_tokens=self._max_tokens,
            json_output_lock="json_object",
            temperature=0.1,
        )

    def invoke(self, contract, *, attempt: int = 1):
        self._calls += 1
        if self._fail_once and self._calls == 1:
            raise AdapterInvokeError("simulated transport failure")
        norm = normalize_panel_score(self._body)
        receipt = TransportReceipt(
            provider_key=self.provider_key,
            contract_hash=contract.contract_hash(),
            max_output_tokens=self._max_tokens,
            temperature=0.1,
            json_output_lock="json_object",
            finish_or_stop_reason="stop",
            parse_status="ok",
            attempt=attempt,
        )
        outcome = PanelJudgeOutcome(
            provider_key=self.provider_key,
            contract_hash=contract.contract_hash(),
            input_hash=contract.input_hash(),
            evaluator_mode="MODEL_BACKED",
            provider_status="MODEL_BACKED_PASS" if norm.pass_ else "MODEL_BACKED_FAIL",
            score=norm.score,
            score_scale=norm.score_scale,
            threshold=norm.threshold,
            pass_=norm.pass_,
            decisive_failure=norm.decisive_failure,
            raw_body=dict(self._body),
            transport_receipt=receipt,
        )
        return outcome, receipt


def test_contract_hash_stable() -> None:
    c = _contract()
    assert c.contract_hash() == c.contract_hash()
    assert validate_contract(c) == []


def test_normalize_panel_score_identical_across_providers() -> None:
    body = _body(score=3.5, pass_=False)
    results = [normalize_panel_score(body) for _ in range(3)]
    assert results[0].pass_ == results[1].pass_ == results[2].pass_ is False


def test_panel_runner_same_contract_hash_all_providers() -> None:
    contract = _contract()
    reg = PanelAdapterRegistry()
    for key in ("gemini_pro", "openai_chatgpt", "anthropic_claude"):
        reg.register(_FakeAdapter(key))
    runner = JudgePanelRunner(reg)
    result = runner.run(contract, list(reg.keys()))
    assert result.contract_hash == contract.contract_hash()
    assert len(result.outcomes) == 3
    assert len({o.contract_hash for o in result.outcomes}) == 1
    assert result.transport_violations == ()


def test_transport_parity_detects_truncation() -> None:
    declared = DeclaredTransportPolicy(max_output_tokens=4096, json_output_lock="json_object")
    observed = TransportReceipt(
        provider_key="anthropic_claude",
        contract_hash="abc",
        max_output_tokens=4096,
        temperature=0.1,
        json_output_lock="json_object",
        finish_or_stop_reason="max_tokens",
        parse_status="ok",
    )
    violations = audit_transport_parity("anthropic_claude", declared, observed)
    assert any(v.code == "truncation_stop_reason" for v in violations)


def test_reconcile_suppresses_mapped_finding_on_passed_gate() -> None:
    body = {
        "score_scale": "0_to_5",
        "score": 2.5,
        "threshold": 4.0,
        "pass": False,
        "decisive_failure": False,
        "findings": ["credential_dump: penalized certs despite gate"],
    }
    gate_summary = {"x2_exec_summary_no_credential_dump": {"pass": True, "detail": "ok"}}
    cmap = GateClosureMap(
        rules=(
            GateClosureRule(
                gate_id="x2_exec_summary_no_credential_dump",
                forbidden_finding_codes=frozenset({"credential_dump"}),
            ),
        )
    )
    out = reconcile_against_gate_closures(body, gate_summary, cmap)
    assert out["findings"] == []
    # Reconcile suppresses findings only; score 2.5 < 4.0 remains fail (no score clamp).
    assert out["pass"] is False


def test_adapter_retry_on_transport_failure() -> None:
    contract = _contract()
    reg = PanelAdapterRegistry()
    reg.register(_FakeAdapter("gemini_pro", fail_once=True))
    result = JudgePanelRunner(reg).run(contract, ["gemini_pro"], max_attempts=2)
    assert result.outcomes[0].evaluator_mode == "MODEL_BACKED"


def test_invalid_contract_rejected() -> None:
    bad = CanonicalJudgeContract(
        section_id="",
        user_prompt="",
        deterministic_gate_summary={},
        judge_task="REWRITE",
    )
    assert validate_contract(bad)
    with pytest.raises(ValueError):
        JudgePanelRunner(PanelAdapterRegistry()).run(bad, ["gemini_pro"])
