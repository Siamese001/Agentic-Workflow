import os
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from apps_lic.engines.message_type_requirement_gate import MESSAGE_ROLE_SPECIFIC
from apps_lic.engines.recipient_classification import CLASS_RECRUITER
from apps_lic.engines.validation_exit import (
    ANTHROPIC_MESSAGES_API,
    DEFAULT_X1D_JUDGE_MODEL,
    DEFAULT_X1D_JUDGE_PROVIDER,
    JUDGE_AVAILABLE,
    JUDGE_EVIDENCE_SUPPORT,
    LIVE_CLAUDE_API_CALL,
    STATUS_X1D_BLOCKED,
    X1DJudgeResult,
    evaluate_x1d,
    required_x1d_profiles,
)
from apps_lic.engines.x1d_claude_judge_adapter import (
    DEFAULT_CLAUDE_TRANSPORT_MODEL_ID,
    AnthropicClaudeX1DTransport,
    parse_claude_x1d_response,
    raw_response_digest,
)
from apps_lic.engines.x1d_preflight import (
    ISSUE_API_KEY_MISSING,
    ISSUE_FAKE_MODE,
    ISSUE_NON_LIVE_TRANSPORT,
    ISSUE_SDK_MISSING,
    ISSUE_UNAVAILABLE_EXPECTED_MODE,
    ISSUE_WRONG_MODEL_ID,
    PREFLIGHT_BLOCKED,
    PREFLIGHT_FAKE_ONLY,
    PREFLIGHT_READY,
    PREFLIGHT_UNAVAILABLE,
    X1D_MODE_FAKE,
    X1D_MODE_LIVE,
    X1D_MODE_UNAVAILABLE_EXPECTED,
    normalize_x1d_mode,
    run_claude_x1d_preflight,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
W7_CONFIG = (
    REPO_ROOT
    / "apps_lic"
    / "config"
    / "domain_contract"
    / "validation_exit.v1.yaml"
)


class RecordingLiveClaudeTransport:
    live_claude_transport = True

    def __init__(self, response):
        self.response = response
        self.payloads = []

    def __call__(self, payload):
        self.payloads.append(payload)
        return self.response


class RecordingFakeTransport:
    live_claude_transport = False

    def __init__(self):
        self.payloads = []

    def __call__(self, payload):
        self.payloads.append(payload)
        return {"score": 1.0, "passed": True, "issues": [], "required_repairs": []}


def _x1d_required_request():
    return SimpleNamespace(
        reasoning_policy=SimpleNamespace(x1d_llm_judge_depth=1),
        recipient_class=CLASS_RECRUITER,
        message_type=MESSAGE_ROLE_SPECIFIC,
        modifiers={},
    )


def _x2_pass():
    return SimpleNamespace(passed=True)


def test_w1_config_freezes_live_claude_preflight_policy() -> None:
    with W7_CONFIG.open(encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    preflight = config["x1d"]["preflight_policy"]
    assert preflight["required_transport_model_id"] == DEFAULT_CLAUDE_TRANSPORT_MODEL_ID
    assert preflight["modes"] == ["fake", "live", "unavailable-expected"]
    assert preflight["fake_mode_can_clear_exit"] is False
    assert preflight["unavailable_expected_mode_can_clear_exit"] is False
    assert "ANTHROPIC_API_KEY" in preflight["live_mode_requires"]
    assert "anthropic_sdk" in preflight["live_mode_requires"]
    assert "minimal_rubric_json_parse" in preflight["live_mode_requires"]
    assert "raw_response_digest" in preflight["live_mode_requires"]
    assert config["x1d"]["live_call_policy"]["required_raw_response_digest"] is True


def test_x1d_mode_normalization_accepts_runner_modes() -> None:
    assert normalize_x1d_mode("fake") == X1D_MODE_FAKE
    assert normalize_x1d_mode("live") == X1D_MODE_LIVE
    assert normalize_x1d_mode("unavailable_expected") == X1D_MODE_UNAVAILABLE_EXPECTED
    assert normalize_x1d_mode("unavailable-expected") == X1D_MODE_UNAVAILABLE_EXPECTED
    assert normalize_x1d_mode("mock") == ""


def test_fake_x1d_preflight_mode_is_deterministic_but_cannot_clear() -> None:
    transport = RecordingFakeTransport()

    receipt = run_claude_x1d_preflight(
        mode=X1D_MODE_FAKE,
        env={},
        transport=transport,
        anthropic_sdk_available_override=False,
    )

    assert receipt.preflight_status == PREFLIGHT_FAKE_ONLY
    assert receipt.clearance_allowed is False
    assert receipt.expected_unavailable is False
    assert receipt.issues == (ISSUE_FAKE_MODE,)
    assert transport.payloads == []


def test_unavailable_expected_mode_reports_missing_key_without_calling_transport() -> None:
    transport = RecordingFakeTransport()

    receipt = run_claude_x1d_preflight(
        mode=X1D_MODE_UNAVAILABLE_EXPECTED,
        env={},
        transport=transport,
        anthropic_sdk_available_override=False,
    )

    assert receipt.preflight_status == PREFLIGHT_UNAVAILABLE
    assert receipt.availability_status == "unavailable"
    assert receipt.expected_unavailable is True
    assert receipt.clearance_allowed is False
    assert ISSUE_API_KEY_MISSING in receipt.issues
    assert ISSUE_SDK_MISSING in receipt.issues
    assert ISSUE_UNAVAILABLE_EXPECTED_MODE in receipt.issues
    assert transport.payloads == []


def test_live_x1d_preflight_missing_key_or_sdk_fails_closed() -> None:
    missing_key = run_claude_x1d_preflight(
        mode=X1D_MODE_LIVE,
        env={},
        anthropic_sdk_available_override=True,
    )
    assert missing_key.preflight_status == PREFLIGHT_UNAVAILABLE
    assert missing_key.clearance_allowed is False
    assert missing_key.issues == (ISSUE_API_KEY_MISSING,)

    missing_sdk = run_claude_x1d_preflight(
        mode=X1D_MODE_LIVE,
        api_key="sk-ant-test",
        env={},
        anthropic_sdk_available_override=False,
    )
    assert missing_sdk.preflight_status == PREFLIGHT_UNAVAILABLE
    assert missing_sdk.clearance_allowed is False
    assert missing_sdk.issues == (ISSUE_SDK_MISSING,)


def test_live_x1d_preflight_blocks_wrong_model_and_non_live_transport() -> None:
    wrong_model = run_claude_x1d_preflight(
        mode=X1D_MODE_LIVE,
        api_key="sk-ant-test",
        env={},
        transport_model_id="claude-not-sonnet-4-6",
        anthropic_sdk_available_override=True,
    )
    assert wrong_model.preflight_status == PREFLIGHT_BLOCKED
    assert wrong_model.model_id_configured is False
    assert wrong_model.issues == (ISSUE_WRONG_MODEL_ID,)

    fake_transport = RecordingFakeTransport()
    non_live = run_claude_x1d_preflight(
        mode=X1D_MODE_LIVE,
        api_key="sk-ant-test",
        env={},
        transport=fake_transport,
        anthropic_sdk_available_override=True,
    )
    assert non_live.preflight_status == PREFLIGHT_BLOCKED
    assert non_live.issues == (ISSUE_NON_LIVE_TRANSPORT,)
    assert fake_transport.payloads == []


def test_live_x1d_preflight_blocks_live_shaped_non_anthropic_transport() -> None:
    transport = RecordingLiveClaudeTransport(
        {
            "score": 1.0,
            "passed": True,
            "issues": [],
            "required_repairs": [],
            "availability_status": JUDGE_AVAILABLE,
            "transport_provenance": LIVE_CLAUDE_API_CALL,
            "transport_provider": ANTHROPIC_MESSAGES_API,
            "transport_call_id": "msg_not_anthropic_transport",
            "model": DEFAULT_X1D_JUDGE_MODEL,
            "provider": DEFAULT_X1D_JUDGE_PROVIDER,
        }
    )

    receipt = run_claude_x1d_preflight(
        mode=X1D_MODE_LIVE,
        api_key="sk-ant-test",
        env={},
        transport=transport,
        anthropic_sdk_available_override=True,
    )

    assert receipt.preflight_status == PREFLIGHT_BLOCKED
    assert receipt.minimal_rubric_call_attempted is False
    assert receipt.clearance_allowed is False
    assert receipt.issues == (ISSUE_NON_LIVE_TRANSPORT,)
    assert transport.payloads == []


def test_live_x1d_preflight_blocks_injected_anthropic_client() -> None:
    receipt = run_claude_x1d_preflight(
        mode=X1D_MODE_LIVE,
        api_key="sk-ant-test",
        env={},
        transport=AnthropicClaudeX1DTransport(api_key="sk-ant-test", client=object()),
        anthropic_sdk_available_override=True,
    )

    assert receipt.preflight_status == PREFLIGHT_BLOCKED
    assert receipt.clearance_allowed is False
    assert receipt.issues == (ISSUE_NON_LIVE_TRANSPORT,)


def test_unparseable_claude_response_parser_persists_digest() -> None:
    request = _x1d_required_request()
    profile = required_x1d_profiles(request)[0]

    parsed = parse_claude_x1d_response("not-json", profile=profile)

    assert parsed.passed is False
    assert "judge_response_not_parseable" in parsed.issues
    assert parsed.raw_response_digest == raw_response_digest("not-json")


def test_manual_live_shaped_judge_receipts_cannot_clear_x1d() -> None:
    request = _x1d_required_request()
    profile = required_x1d_profiles(request)[0]

    hand_built = X1DJudgeResult(
        judge_id=JUDGE_EVIDENCE_SUPPORT,
        model=DEFAULT_X1D_JUDGE_MODEL,
        provider=DEFAULT_X1D_JUDGE_PROVIDER,
        score=0.99,
        threshold=profile.threshold,
        passed=True,
        availability_status=JUDGE_AVAILABLE,
        transport_provenance=LIVE_CLAUDE_API_CALL,
        transport_provider=ANTHROPIC_MESSAGES_API,
        transport_call_id="msg_without_digest",
    )
    blocked = evaluate_x1d(request, x2_result=_x2_pass(), judge_results=(hand_built,))

    assert blocked.status == STATUS_X1D_BLOCKED
    assert f"non_live_claude_judge:{JUDGE_EVIDENCE_SUPPORT}" in blocked.reason_codes

    parsed = parse_claude_x1d_response(
        {
            "score": 0.99,
            "passed": True,
            "issues": [],
            "required_repairs": [],
            "availability_status": JUDGE_AVAILABLE,
            "transport_provenance": LIVE_CLAUDE_API_CALL,
            "transport_provider": ANTHROPIC_MESSAGES_API,
            "transport_call_id": "msg_with_digest",
            "model": DEFAULT_X1D_JUDGE_MODEL,
            "provider": DEFAULT_X1D_JUDGE_PROVIDER,
        },
        profile=profile,
    )
    parsed_blocked = evaluate_x1d(request, x2_result=_x2_pass(), judge_results=(parsed,))

    assert parsed.raw_response_digest.startswith("sha256:")
    assert parsed.transport_provenance == ""
    assert parsed_blocked.status == STATUS_X1D_BLOCKED


def test_live_claude_x1d_preflight_opt_in_environment_marker() -> None:
    if os.environ.get("APPS_LIC_RUN_LIVE_CLAUDE_X1D") != "1":
        pytest.skip("Set APPS_LIC_RUN_LIVE_CLAUDE_X1D=1 to call live Claude.")

    receipt = run_claude_x1d_preflight(mode=X1D_MODE_LIVE)

    assert receipt.preflight_status == PREFLIGHT_READY
    assert receipt.clearance_allowed is True
    assert receipt.transport_provenance == LIVE_CLAUDE_API_CALL
