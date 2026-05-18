"""Unit tests for competencies live ``qwen_vllm`` HTTP /v1/models preflight (fail-fast gate)."""
from __future__ import annotations

from types import SimpleNamespace

import pytest

from apps_rg.runtime.dispatch.competencies_dispatch import clarify_x3_for_competencies_live_provider_preflight
from apps_rg.runtime.exit.competencies_x3 import X3Disposition, aggregate_x3
from apps_rg.runtime.providers.competencies_live_provider_gate import (
    REASON_PROVIDER_UNAVAILABLE,
    STATUS_BLOCKED_LIVE_PROVIDER,
    blocked_live_provider_preflight_result,
    competencies_vllm_preflight_timeout_s,
    live_provider_gate_audit_payload_failure,
    qwen_openai_base_tcp_preflight,
    qwen_vllm_http_models_preflight,
)
from apps_rg.runtime.section_proof.mock_runtime_proof_policy import compute_lane_proof_bundle
from apps_rg.runtime.qwen_offline_contract_stub import OFFLINE_CONTRACT_STUB_RUNTIME_STATUS
from apps_rg.runtime.validators.competencies_x2 import resolve_competencies_provider_transport_x2


def test_tcp_preflight_monkeypatch_os_error(monkeypatch: pytest.MonkeyPatch) -> None:
    import apps_rg.runtime.providers.competencies_live_provider_gate as gate

    def _boom(*_a: object, **_k: object) -> None:
        raise ConnectionRefusedError("refused")

    monkeypatch.setattr(gate.socket, "create_connection", _boom)
    ok, detail = qwen_openai_base_tcp_preflight(
        provider_url="http://127.0.0.1:59998/v1",
        timeout_s=1.0,
    )
    assert ok is False
    assert "ConnectionRefusedError" in detail


def test_blocked_live_provider_preflight_result_strings() -> None:
    pr = blocked_live_provider_preflight_result(
        model="Qwen/Qwen2.5-32B-Instruct-AWQ",
        base_url="http://localhost:8000/v1",
        preflight_detail="ConnectionRefusedError: refused",
        timeout_s=5.0,
    )
    assert pr.runtime_generation_status == "BLOCKED"
    assert STATUS_BLOCKED_LIVE_PROVIDER in (pr.exact_provider_error or "")
    assert REASON_PROVIDER_UNAVAILABLE in (pr.exact_provider_error or "")
    assert "POST attempted" in (pr.exact_provider_error or "")
    assert "HTTP /v1/models" in (pr.exact_provider_error or "")


def test_gate_audit_payload_failure_shape() -> None:
    body = live_provider_gate_audit_payload_failure(
        provider_base_url="http://localhost:8000/v1",
        preflight_detail="errno",
        timeout_s=5.0,
    )
    assert body["live_provider_gate_status"] == STATUS_BLOCKED_LIVE_PROVIDER
    assert body["provider_unreachable_reason"] == REASON_PROVIDER_UNAVAILABLE
    assert body["http_post_attempted"] is False
    assert body["preflight_transport"] == "http_v1_models"


def test_competencies_preflight_timeout_env_parse(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APPS_RG_COMPETENCIES_VLLM_PREFLIGHT_TIMEOUT_SECONDS", "12")
    assert competencies_vllm_preflight_timeout_s() == 12.0


def test_clarify_x3_live_preflight_blocked_rewrites_copy() -> None:
    base = X3Disposition(
        x3_code="X3_BLOCK",
        decisive_reason="X2 deterministic gate failure",
        review_reason="",
        authorization_scope="PLUMBING_ONLY",
        proceed_to_runtime=False,
        pass_=False,
        runtime_generation_status="BLOCKED",
        x1d_evaluator_mode="BLOCKED_PROVIDER_UNAVAILABLE",
        product_quality_status="PARTIAL",
        x2_failed_gates=["x2_competency_exactly_8_categories"],
        blocked_judges=[],
        mocked_judges=[],
        soft_failed_judges=[],
        decisive_judge_failures=[],
        final_summary_hash="a",
        claim_ledger_hash="b",
        required_remediation=["Fix failed X2 gates: x2_competency_exactly_8_categories", "other"],
    )
    out = clarify_x3_for_competencies_live_provider_preflight(base, live_preflight_blocked=True)
    assert "BLOCKED_LIVE_PROVIDER" in out.decisive_reason
    assert out.x2_failed_gates == []
    assert not any(str(r).startswith("Fix failed X2 gates") for r in out.required_remediation)


def test_aggregate_x3_blocked_generation_not_allow() -> None:
    x3 = aggregate_x3(
        resume_display_text="",
        claim_ledger=[],
        x2_gates=[{"gate_id": "x2_json_parse_valid", "pass": True}],
        x1d_judges=[],
        runtime_generation_status="BLOCKED",
        product_quality_status="PARTIAL",
    )
    assert x3.x3_code == "X3_BLOCK"
    assert x3.pass_ is False


def test_proof_bundle_blocked_generation_not_eligible() -> None:
    args = SimpleNamespace(
        mock_judges=False,
        provider="qwen_vllm",
        allow_non_allow_exit_zero=False,
        allow_test_mock_provider=False,
    )
    x3 = SimpleNamespace(x3_code="X3_BLOCK", pass_=False)
    bundle = compute_lane_proof_bundle(
        args,
        runtime_generation_status="BLOCKED",
        x1d_judges=[
            {
                "evaluator_mode": "MODEL_BACKED",
                "provider_status": "MODEL_BACKED_PASS",
            },
        ],
        x2_gates=[{"gate_id": "x2_json_parse_valid", "pass": True}],
        x3=x3,
    )
    assert bundle["proof_eligible"] is False


def test_provider_transport_x2_blocked_preflight_overrides_generation_status() -> None:
    ok, req, att = resolve_competencies_provider_transport_x2(
        cli_provider="qwen_vllm",
        runtime_generation_status="BLOCKED",
        live_preflight_blocked=True,
    )
    assert ok is False
    assert req == "qwen_vllm"
    assert att == "blocked_http_models_preflight"


def test_provider_transport_x2_cli_qwen_offline_stub_coherent() -> None:
    ok, req, att = resolve_competencies_provider_transport_x2(
        cli_provider="qwen_vllm",
        runtime_generation_status=OFFLINE_CONTRACT_STUB_RUNTIME_STATUS,
        live_preflight_blocked=False,
    )
    assert ok is True
    assert att == "offline_contract_stub"


def test_provider_transport_x2_cli_qwen_mocked_generation_fails() -> None:
    ok, _, att = resolve_competencies_provider_transport_x2(
        cli_provider="qwen_vllm",
        runtime_generation_status="MOCKED",
        live_preflight_blocked=False,
    )
    assert ok is False
    assert att == "mocked_generation"


def test_http_models_preflight_monkeypatch(monkeypatch: pytest.MonkeyPatch) -> None:
    import apps_rg.runtime.providers.competencies_live_provider_gate as gate

    def _fail(
        *_a: object,
        **kwargs: object,
    ) -> tuple[bool, dict[str, object], str | None]:
        _ = kwargs
        return False, {"error": "url_down", "status": "unhealthy"}, "http_v1_models_probe_failure"

    monkeypatch.setattr(gate, "run_http_models_preflight", _fail)
    ok, detail, snap = qwen_vllm_http_models_preflight(
        provider_url="http://127.0.0.1:59999/v1",
        timeout_s=1.0,
    )
    assert ok is False
    assert detail
    assert isinstance(snap, dict)


def test_competencies_dispatch_offline_branch_uses_effective_stub() -> None:
    """Regression: synthetic stub gate must use effective_offline (honors disable env)."""
    from pathlib import Path

    import apps_rg.runtime.dispatch.competencies_dispatch as cd

    text = Path(cd.__file__).read_text(encoding="utf-8")
    assert "if effective_offline_contract_stub_enabled():" in text
    assert "\nif offline_contract_stub_enabled():" not in text
