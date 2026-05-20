"""Contract: live qwen_vllm section CLI requires Docker container + HTTP /v1/models health."""

from __future__ import annotations

from pathlib import Path

import pytest

from apps_rg.runtime.section_cli_defaults import SectionCliConfigError

REPO = Path(__file__).resolve().parents[2]
_FRESH_JD = REPO / "tests" / "_fixtures" / "ci-probe-jd.txt"
_FRESH_BRIEF = REPO / "tests" / "_fixtures" / "ci-probe-briefing.txt"


def test_main_returns_2_when_vllm_http_unreachable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("VLLM_BASE_URL", "http://127.0.0.1:9/")
    monkeypatch.setenv("APPS_RG_QWEN_DISABLE_OFFLINE_STUB", "1")
    monkeypatch.delenv("APPS_RG_QWEN_OFFLINE_CONTRACT_STUB", raising=False)
    monkeypatch.delenv("APPS_RG_SKIP_QWEN_VLLM_HEALTH", raising=False)
    monkeypatch.setattr(
        "apps_rg.runtime.section_cli_preflight._docker_container_running",
        lambda _c: (True, ""),
    )

    from apps_rg.__main__ import main

    rc = main(
        [
            "--section",
            "headline",
            "--target-company",
            "CI-Probe-Co",
            "--target-role",
            "Engineer",
            "--jd",
            str(_FRESH_JD),
            "--manual-brief",
            str(_FRESH_BRIEF),
        ]
    )
    assert rc == 2


def test_main_returns_2_for_mock_provider_before_lane(monkeypatch: pytest.MonkeyPatch) -> None:
    """Argparse no longer lists mock; invalid values still fail at resolve."""
    monkeypatch.setenv("APPS_RG_QWEN_DISABLE_OFFLINE_STUB", "1")
    monkeypatch.delenv("APPS_RG_QWEN_OFFLINE_CONTRACT_STUB", raising=False)

    from apps_rg.__main__ import main

    with pytest.raises(SystemExit):
        main(
            [
                "--section",
                "headline",
                "--provider",
                "mock",
                "--target-company",
                "CI",
                "--target-role",
                "Eng",
            ]
        )


def test_require_health_raises_with_clear_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("APPS_RG_QWEN_OFFLINE_CONTRACT_STUB", raising=False)
    monkeypatch.delenv("APPS_RG_SKIP_QWEN_VLLM_HEALTH", raising=False)
    monkeypatch.setattr(
        "apps_rg.runtime.section_cli_preflight._docker_container_running",
        lambda _c: (False, "container not running"),
    )
    from apps_rg.runtime.section_cli_preflight import require_qwen_vllm_cli_health

    with pytest.raises(SectionCliConfigError, match="docker container health check failed"):
        require_qwen_vllm_cli_health(lane_provider="qwen_vllm")
