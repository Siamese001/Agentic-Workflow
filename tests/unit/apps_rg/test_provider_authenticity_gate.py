"""W1 provider authenticity gate — classifier, stub fast-fail, FAILED_PROVIDER (apps_rg-local)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from agentic_core.runtime.providers.provider_types import (
    ProviderKind,
    ProviderMode,
    ProviderProfile,
    ProviderResponse,
)
from apps_rg.l2_recipe.resume_generation_contract import MODE_STUB_RECEIPT
from apps_rg.l2_recipe.resume_output_shape import (
    BLOCKED_STUB_PROVIDER,
    FAILED_PROVIDER,
    STUB_RECEIPT,
)
from apps_rg.runtime.bindings.l2_envelope_adapter import (
    _execute_approved_work_order,
    _provider_profile_for_cpa,
    _resolve_l2_envelope_provider_mode,
)
from apps_rg.runtime.providers.provider_run_mode import (
    AppsRgEnvelopeProviderResolutionError,
    ProviderRunMode,
    assert_provider_authentic_for_full_resume,
    classify_provider_run_mode,
)


def _live_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "apps_rg.runtime.providers.provider_run_mode._pytest_active",
        lambda: False,
    )
    monkeypatch.setenv("APPS_RG_L2_PROVIDER_MODE", "local_only")
    monkeypatch.delenv("APPS_RG_L2_FORCE_STUB", raising=False)


def test_classify_live_required_when_not_pytest(monkeypatch: pytest.MonkeyPatch) -> None:
    _live_env(monkeypatch)
    assert classify_provider_run_mode() == ProviderRunMode.LIVE_REQUIRED


def test_classify_explicit_stub_contract_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "apps_rg.runtime.providers.provider_run_mode._pytest_active",
        lambda: False,
    )
    monkeypatch.setenv("APPS_RG_L2_PROVIDER_MODE", "local_only")
    assert (
        classify_provider_run_mode(resume_artifact_contract_mode=MODE_STUB_RECEIPT)
        == ProviderRunMode.EXPLICIT_STUB
    )


def test_classify_test_stub_under_pytest() -> None:
    assert classify_provider_run_mode() == ProviderRunMode.TEST_STUB


def test_live_required_force_stub_blocked(monkeypatch: pytest.MonkeyPatch) -> None:
    _live_env(monkeypatch)
    monkeypatch.setenv("APPS_RG_L2_FORCE_STUB", "1")
    stub = ProviderProfile(
        profile_id="apps_rg_envelope_stub",
        provider_kind=ProviderKind.STUB,
    )
    v = assert_provider_authentic_for_full_resume(
        run_mode=ProviderRunMode.LIVE_REQUIRED,
        profile=stub,
    )
    assert v is not None
    assert v.generation_status == BLOCKED_STUB_PROVIDER


def test_live_required_stub_profile_blocked(monkeypatch: pytest.MonkeyPatch) -> None:
    _live_env(monkeypatch)
    stub = ProviderProfile(
        profile_id="apps_rg_envelope_stub",
        provider_kind=ProviderKind.STUB,
    )
    v = assert_provider_authentic_for_full_resume(
        run_mode=ProviderRunMode.LIVE_REQUIRED,
        profile=stub,
    )
    assert v is not None
    assert v.generation_status == BLOCKED_STUB_PROVIDER


def test_live_required_stub_kind_blocked(monkeypatch: pytest.MonkeyPatch) -> None:
    _live_env(monkeypatch)
    p = ProviderProfile(
        profile_id="custom_id_no_keyword",
        provider_kind=ProviderKind.STUB,
    )
    v = assert_provider_authentic_for_full_resume(
        run_mode=ProviderRunMode.LIVE_REQUIRED,
        profile=p,
    )
    assert v is not None
    assert v.generation_status == BLOCKED_STUB_PROVIDER


def test_explicit_stub_allows_stub_profile(monkeypatch: pytest.MonkeyPatch) -> None:
    _live_env(monkeypatch)
    monkeypatch.setenv("APPS_RG_L2_PROVIDER_MODE", "stub_only")
    stub = ProviderProfile(
        profile_id="apps_rg_envelope_stub",
        provider_kind=ProviderKind.STUB,
    )
    assert (
        assert_provider_authentic_for_full_resume(
            run_mode=ProviderRunMode.EXPLICIT_STUB,
            profile=stub,
        )
        is None
    )


def test_test_stub_allows_stub(monkeypatch: pytest.MonkeyPatch) -> None:
    _ = monkeypatch
    stub = ProviderProfile(
        profile_id="apps_rg_envelope_stub",
        provider_kind=ProviderKind.STUB,
    )
    assert (
        assert_provider_authentic_for_full_resume(
            run_mode=ProviderRunMode.TEST_STUB,
            profile=stub,
        )
        is None
    )


def test_unknown_provider_lane_live_required(monkeypatch: pytest.MonkeyPatch) -> None:
    _live_env(monkeypatch)

    class _Cpa:
        target_provider = "unknown_vendor_xyz"
        target_model = "m"

    with pytest.raises(AppsRgEnvelopeProviderResolutionError):
        _provider_profile_for_cpa(
            _Cpa(),
            provider_mode=ProviderMode.LOCAL_ONLY,
            run_mode=ProviderRunMode.LIVE_REQUIRED,
        )


def test_explicit_stub_unknown_lane_returns_stub(monkeypatch: pytest.MonkeyPatch) -> None:
    _live_env(monkeypatch)
    monkeypatch.setenv("APPS_RG_L2_PROVIDER_MODE", "stub_only")

    class _Cpa:
        target_provider = "unknown_vendor_xyz"
        target_model = "m"

    prof = _provider_profile_for_cpa(
        _Cpa(),
        provider_mode=_resolve_l2_envelope_provider_mode(),
        run_mode=ProviderRunMode.EXPLICIT_STUB,
    )
    assert prof.provider_kind == ProviderKind.STUB


def test_live_http_error_no_stub_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    _live_env(monkeypatch)
    prep = MagicMock()
    prep.replay_bindings.determinism = MagicMock()
    prep.lineage_root = MagicMock()
    awo = MagicMock()
    awo.validation_packet_id = "v1"
    awo.budget_snapshot.repair_ceiling = 3

    cpa = MagicMock()
    cpa.trace_id = "t"
    cpa.target_provider = "local_vllm"
    cpa.target_model = "Qwen/Qwen2.5-32B-Instruct-AWQ"
    cpa.request_id = "r"
    cpa.run_id = "run"
    cpa.compilation_hash = "h"
    cpa.max_tokens = 8192
    cpa.temperature = 0.0
    cpa.prompt_blocks = ()
    cpa.system_preamble = "s"
    cpa.user_instruction = "u"
    cpa.replay_key = "rk"
    cpa.allowed_models = ("Qwen/Qwen2.5-32B-Instruct-AWQ",)

    bad = ProviderResponse(
        success=False,
        text="",
        receipt=None,
        error_message="HTTP 400 bad request",
    )
    with patch(
        "apps_rg.runtime.bindings.l2_envelope_adapter.ProviderGateway.invoke",
        return_value=bad,
    ):
        receipt = _execute_approved_work_order(
            cpa=cpa,
            approved_work_order=awo,
            prep_output=prep,
            attempt_number=1,
            resume_artifact_contract_mode=None,
        )
    lc = dict(receipt.local_check_results or {})
    assert lc.get("generation_status") == FAILED_PROVIDER
    assert lc.get("full_resume_generated") is False
    assert lc.get("outcome_authorized") is False
    diff = dict(receipt.proposed_state_diff or {})
    assert diff.get("generation_status") == FAILED_PROVIDER
    assert isinstance(diff.get("provider_error"), dict)
    assert "HTTP 400" in str(diff.get("provider_error", {}).get("message", ""))


def test_live_timeout_failed_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    _live_env(monkeypatch)
    prep = MagicMock()
    prep.replay_bindings.determinism = MagicMock()
    prep.lineage_root = MagicMock()
    awo = MagicMock()
    awo.validation_packet_id = "v1"
    awo.budget_snapshot.repair_ceiling = 3

    cpa = MagicMock()
    cpa.trace_id = "t"
    cpa.target_provider = "local_vllm"
    cpa.target_model = "Qwen/Qwen2.5-32B-Instruct-AWQ"
    cpa.request_id = "r"
    cpa.run_id = "run"
    cpa.compilation_hash = "h"
    cpa.max_tokens = 8192
    cpa.temperature = 0.0
    cpa.prompt_blocks = ()
    cpa.system_preamble = "s"
    cpa.user_instruction = "u"
    cpa.replay_key = "rk"
    cpa.allowed_models = ("Qwen/Qwen2.5-32B-Instruct-AWQ",)

    bad = ProviderResponse(
        success=False,
        text="",
        receipt=None,
        error_message="timeout waiting for vLLM",
    )
    with patch(
        "apps_rg.runtime.bindings.l2_envelope_adapter.ProviderGateway.invoke",
        return_value=bad,
    ):
        receipt = _execute_approved_work_order(
            cpa=cpa,
            approved_work_order=awo,
            prep_output=prep,
            attempt_number=1,
            resume_artifact_contract_mode=None,
        )
    assert dict(receipt.local_check_results or {}).get("generation_status") == FAILED_PROVIDER


def test_explicit_stub_marks_stub_receipt_on_success(monkeypatch: pytest.MonkeyPatch) -> None:
    _live_env(monkeypatch)
    monkeypatch.setenv("APPS_RG_L2_PROVIDER_MODE", "stub_only")
    prep = MagicMock()
    prep.replay_bindings.determinism = MagicMock()
    prep.lineage_root = MagicMock()
    awo = MagicMock()
    awo.validation_packet_id = "v1"
    awo.budget_snapshot.repair_ceiling = 3

    cpa = MagicMock()
    cpa.trace_id = "t"
    cpa.target_provider = "local_vllm"
    cpa.target_model = "Qwen/Qwen2.5-32B-Instruct-AWQ"
    cpa.request_id = "r"
    cpa.run_id = "run"
    cpa.compilation_hash = "h"
    cpa.max_tokens = 8192
    cpa.temperature = 0.0
    cpa.prompt_blocks = ()
    cpa.system_preamble = "s"
    cpa.user_instruction = "u"
    cpa.replay_key = "rk"
    cpa.allowed_models = ("Qwen/Qwen2.5-32B-Instruct-AWQ",)

    stub_json = '{"stub_response": true, "hash": "x"}'
    ok = ProviderResponse(success=True, text=stub_json, receipt=None)
    with patch(
        "apps_rg.runtime.bindings.l2_envelope_adapter.ProviderGateway.invoke",
        return_value=ok,
    ):
        receipt = _execute_approved_work_order(
            cpa=cpa,
            approved_work_order=awo,
            prep_output=prep,
            attempt_number=1,
            resume_artifact_contract_mode=MODE_STUB_RECEIPT,
        )
    lc = dict(receipt.local_check_results or {})
    assert lc.get("generation_status") == STUB_RECEIPT
    assert lc.get("full_resume_generated") is False
