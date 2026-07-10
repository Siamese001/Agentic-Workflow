"""apps-test-model: HARNESS.

Deterministic checks for the apps_rg live CLI contract harness.
"""

from __future__ import annotations

import sys

import pytest

from tests._apps_contract import lane_cli_common as harness


def test_canonical_argv_uses_supported_external_claude_provider() -> None:
    argv = harness.base_canonical_argv("headline")

    assert argv[:3] == [sys.executable, "-m", "apps_rg"]
    provider_index = argv.index("--provider")
    assert argv[provider_index + 1] == "external_claude"
    assert "retired_provider_profile" not in argv


def test_canonical_argv_preserves_explicit_lane_inputs() -> None:
    argv = harness.base_canonical_argv(
        "competencies",
        artifact_dir="artifacts/test-run",
        target_company="Example Co",
        target_role="Chief Architect",
        jd="fixtures/jd.txt",
        manual_brief="fixtures/brief.md",
    )

    assert argv[argv.index("--section") + 1] == "competencies"
    assert argv[argv.index("--artifact-dir") + 1] == "artifacts/test-run"
    assert argv[argv.index("--target-company") + 1] == "Example Co"
    assert argv[argv.index("--target-role") + 1] == "Chief Architect"
    assert argv[argv.index("--jd") + 1] == "fixtures/jd.txt"
    assert argv[argv.index("--manual-brief") + 1] == "fixtures/brief.md"


def test_contract_env_removes_retired_stub_controls(monkeypatch: pytest.MonkeyPatch) -> None:
    retired_controls = (
        "APPS_RG_RETIRED_PROVIDER_OFFLINE_CONTRACT_STUB",
        "APPS_RG_TEST_HARNESS",
        "APPS_RG_MOCK_JUDGES",
        "APPS_RG_SKIP_RETIRED_PROVIDER_PROFILE_HEALTH",
        "APPS_RG_L2_FORCE_STUB",
    )
    for key in retired_controls:
        monkeypatch.setenv(key, "1")

    env = harness.contract_env(live_l2=True)

    assert all(key not in env for key in retired_controls)
    assert env["APPS_RG_L2_PROVIDER_MODE"] == "live_allowed"
    assert env["PYTEST_APPS_RG_LIVE_L2"] == "1"


def test_live_availability_requires_nonblank_anthropic_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "  ")
    assert harness.external_claude_live_available() is False

    monkeypatch.setenv("ANTHROPIC_API_KEY", "credential-present")
    assert harness.external_claude_live_available() is True


def test_fast_mode_always_skips_live_lane(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APPS_RG_CONTRACT_HARNESS_FAST", "1")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "credential-present")

    assert harness.should_skip_contract_live_lane() is True
    assert "APPS_RG_CONTRACT_HARNESS_FAST=1" in harness.live_lane_skip_reason("headline")
