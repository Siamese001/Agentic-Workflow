"""Live-only Qwen vLLM policy — no offline stub env for apps_rg runs."""

from __future__ import annotations

import pytest

from apps_rg.runtime.qwen_live_only_guard import (
    assert_live_qwen_vllm_no_mocks,
    assert_production_cli_no_mock_judge_flags,
    live_qwen_mock_env_violations,
    production_mock_judge_cli_violations,
    resolve_cli_mock_judges,
)
from apps_rg.runtime.qwen_offline_contract_stub import (
    effective_offline_contract_stub_enabled,
    offline_contract_stub_enabled,
    synthetic_qwen_provider_result,
)


def test_stub_flags_always_disabled() -> None:
    assert offline_contract_stub_enabled() is False
    assert effective_offline_contract_stub_enabled() is False


def test_synthetic_qwen_raises() -> None:
    with pytest.raises(RuntimeError, match="disabled"):
        synthetic_qwen_provider_result(raw_model_output="{}", requested_model="qwen")


def test_live_qwen_mock_env_detects_stub(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APPS_RG_QWEN_OFFLINE_CONTRACT_STUB", "1")
    violations = live_qwen_mock_env_violations()
    assert any("APPS_RG_QWEN_OFFLINE_CONTRACT_STUB" in v for v in violations)


def test_assert_live_qwen_exits_on_stub_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APPS_RG_QWEN_OFFLINE_CONTRACT_STUB", "1")
    with pytest.raises(SystemExit) as exc:
        assert_live_qwen_vllm_no_mocks(context="test")
    assert exc.value.code == 2


def test_mock_judge_cli_flag_violation() -> None:
    assert production_mock_judge_cli_violations(["python", "-m", "apps_rg", "--mock-judges"])


def test_resolve_cli_mock_judges_default_off(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("APPS_RG_TEST_HARNESS", raising=False)
    monkeypatch.delenv("APPS_RG_MOCK_JUDGES", raising=False)
    assert resolve_cli_mock_judges() == (False, False)


def test_resolve_cli_mock_judges_test_harness_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APPS_RG_TEST_HARNESS", "1")
    monkeypatch.setenv("APPS_RG_MOCK_JUDGES", "1")
    assert resolve_cli_mock_judges() == (True, True)


def test_assert_production_cli_rejects_mock_judge_flag() -> None:
    with pytest.raises(SystemExit) as exc:
        assert_production_cli_no_mock_judge_flags(
            ["python", "-m", "apps_rg", "--mock-judges"]
        )
    assert exc.value.code == 2
