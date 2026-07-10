from __future__ import annotations

from dataclasses import dataclass

import pytest

from apps_rg.runtime.judges.x1d_panel_harness import (
    AdapterInvokeError,
    CanonicalJudgeContract,
    DeclaredTransportPolicy,
    JudgePanelRunner,
    PanelAdapterRegistry,
    PanelJudgeOutcome,
    TransportReceipt,
    audit_transport_parity,
    compute_contract_hash,
    validate_contract,
)


def _contract() -> CanonicalJudgeContract:
    return CanonicalJudgeContract(
        section_id="executive_summary",
        user_prompt="Grade this output.",
        deterministic_gate_summary={"x2_shape": {"pass": True}},
        output_schema_ref="schema:x1d",
        proof_boundary={
            "jd_is_targeting_context_only": True,
            "briefing_is_targeting_context_only": True,
            "judges_must_not_rewrite": True,
        },
    )


@dataclass
class _Adapter:
    provider_key: str
    fail_attempts: int = 0

    def declared_policy(self, *, attempt: int = 1) -> DeclaredTransportPolicy:
        return DeclaredTransportPolicy(
            max_output_tokens=1000,
            temperature=0.0,
            json_output_lock="json_object",
        )

    def invoke(
        self,
        contract: CanonicalJudgeContract,
        *,
        attempt: int = 1,
    ) -> tuple[PanelJudgeOutcome, TransportReceipt]:
        if attempt <= self.fail_attempts:
            raise AdapterInvokeError("temporary provider error")
        receipt = TransportReceipt(
            provider_key=self.provider_key,
            contract_hash=contract.contract_hash(),
            max_output_tokens=1000,
            temperature=0.0,
            json_output_lock="json_object",
            finish_or_stop_reason="stop",
            parse_status="ok",
            attempt=attempt,
        )
        outcome = PanelJudgeOutcome(
            provider_key=self.provider_key,
            contract_hash=contract.contract_hash(),
            input_hash=contract.input_hash(),
            evaluator_mode="REAL",
            provider_status="PASS",
            score=4.5,
            score_scale="0_to_5",
            threshold=4.0,
            pass_=True,
            decisive_failure=False,
            transport_receipt=receipt,
        )
        return outcome, receipt


def test_contract_hash_is_stable_and_validation_enforces_grade_only_boundaries() -> None:
    contract = _contract()
    reordered = CanonicalJudgeContract(
        section_id="executive_summary",
        user_prompt="Grade this output.",
        deterministic_gate_summary={"x2_shape": {"pass": True}},
        output_schema_ref="schema:x1d",
        proof_boundary={
            "judges_must_not_rewrite": True,
            "briefing_is_targeting_context_only": True,
            "jd_is_targeting_context_only": True,
        },
    )

    assert compute_contract_hash(contract) == compute_contract_hash(reordered)
    assert contract.input_hash() == contract.contract_hash()[:16]
    assert validate_contract(contract) == []

    bad = CanonicalJudgeContract(
        section_id="",
        user_prompt="",
        deterministic_gate_summary={},
        judge_task="REWRITE",
        proof_boundary={"judges_must_not_rewrite": False},
    )
    errors = validate_contract(bad)
    assert "judge_task must be 'GRADE_ONLY'" in errors[0]
    assert "section_id is required" in errors
    assert "user_prompt is required" in errors
    assert "deterministic_gate_summary is required" in errors
    assert "proof_boundary.judges_must_not_rewrite must be true when present" in errors


def test_panel_runner_retries_adapter_and_preserves_contract_hash() -> None:
    registry = PanelAdapterRegistry()
    registry.register(_Adapter("openai_chatgpt", fail_attempts=1))
    runner = JudgePanelRunner(registry)

    result = runner.run(_contract(), ["openai_chatgpt"], max_attempts=2)

    assert len(result.outcomes) == 1
    assert result.outcomes[0].provider_key == "openai_chatgpt"
    assert result.outcomes[0].transport_receipt is not None
    assert result.outcomes[0].transport_receipt.attempt == 2
    assert result.outcomes[0].contract_hash == result.contract_hash
    assert result.transport_violations == ()
    assert [attempt.attempt for attempt in result.attempts] == [1, 2]
    assert [attempt.status for attempt in result.attempts] == ["RETRYABLE_FAILURE", "PASS"]
    assert result.attempts[0].error == "temporary provider error"
    assert result.attempts[1].receipt_attempt == 2


def test_panel_runner_blocks_after_adapter_retries_exhausted() -> None:
    registry = PanelAdapterRegistry()
    registry.register(_Adapter("gemini_pro", fail_attempts=3))

    result = JudgePanelRunner(registry).run(_contract(), ["gemini_pro"], max_attempts=2)

    assert result.outcomes[0].provider_status == "JUDGE_PROVIDER_BLOCKED"
    assert result.outcomes[0].pass_ is False
    assert result.outcomes[0].findings == ("temporary provider error",)
    assert [attempt.status for attempt in result.attempts] == [
        "RETRYABLE_FAILURE",
        "EXHAUSTED",
    ]


def test_panel_registry_requires_keys_and_transport_parity_reports_mismatches() -> None:
    registry = PanelAdapterRegistry()
    with pytest.raises(ValueError, match="adapter.provider_key is required"):
        registry.register(_Adapter(""))
    with pytest.raises(KeyError, match="no panel adapter registered"):
        registry.get("missing")

    violations = audit_transport_parity(
        "openai_chatgpt",
        DeclaredTransportPolicy(max_output_tokens=1000, json_output_lock="json_object"),
        TransportReceipt(
            provider_key="wrong_provider",
            contract_hash="hash",
            max_output_tokens=500,
            temperature=0.2,
            json_output_lock="text",
            finish_or_stop_reason="max_tokens",
            parse_status="missing_schema_anchor",
        ),
    )

    assert {v.code for v in violations} == {
        "provider_key_mismatch",
        "max_output_tokens_below_declared",
        "json_output_lock_mismatch",
        "system_missing_score_schema",
        "truncation_stop_reason",
    }
