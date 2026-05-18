"""Canonical CLI routing for professional Competencies (section lane)."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from apps_rg.runtime.orchestration.canonical_dispatch import run_canonical_apps_rg_from_cli_primitives

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_run_canonical_apps_rg_section_competencies_invokes_lane(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[SimpleNamespace] = []

    def fake_lane_execution(args: SimpleNamespace, *, artifact_dir_override: Path | None = None) -> dict:
        calls.append(args)
        art = artifact_dir_override or Path("/tmp/comp_cli_proof")
        return {
            "artifact_dir": art,
            "repo_root": Path("/tmp"),
            "lane_key": "competencies",
            "runtime_payload": {"run_id": "comp_cli_stub"},
            "x3": SimpleNamespace(pass_=True, x3_code="X3_ALLOW"),
            "output_text": "COMPETENCIES_STUB",
            "exit_code": 0,
            "runtime_generation_status": "MOCKED",
            "competencies": [],
        }

    monkeypatch.setattr(
        "apps_rg.runtime.sections.competencies_lane.run_competencies_lane_execution",
        fake_lane_execution,
    )

    out = run_canonical_apps_rg_from_cli_primitives(
        target_company="Co",
        target_role="SVP Engineering",
        jd="",
        resume_path=str(REPO_ROOT / "apps_rg/resume/base/amit_ayer_base_resume_v1.json"),
        section="competencies",
        lane_provider="mock",
        lane_mock_judges=True,
    )
    assert calls, "expected competencies lane execution"
    assert out["competencies_cli_output_text"] == "COMPETENCIES_STUB"
    assert out["outcome_authorized"] is True


def test_python_m_apps_rg_help_lists_competencies_section() -> None:
    import subprocess
    import sys

    proc = subprocess.run(
        [sys.executable, "-m", "apps_rg", "--help"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0
    assert "competencies" in proc.stdout


def test_cli_section_competencies_avoids_product_dispatch(monkeypatch: pytest.MonkeyPatch) -> None:
    """``python -m apps_rg --section competencies`` must use canonical_dispatch, not product dispatch."""
    from apps_rg.__main__ import main

    called: dict[str, bool] = {"dispatch": False, "canonical": False}

    def _bad_dispatch(**_: object) -> dict:
        called["dispatch"] = True
        raise AssertionError("dispatch_apps_rg_run must not run for --section competencies")

    monkeypatch.setattr(
        "agentic_core.runtime.entry.apps_rg_dispatch.dispatch_apps_rg_run",
        _bad_dispatch,
    )

    real_run = __import__(
        "apps_rg.runtime.orchestration.canonical_dispatch",
        fromlist=["run_canonical_apps_rg_from_cli_primitives"],
    ).run_canonical_apps_rg_from_cli_primitives

    def _wrap_canonical(**kwargs: object):
        called["canonical"] = True
        assert str(kwargs.get("section") or "") == "competencies"
        return real_run(**kwargs)

    monkeypatch.setattr(
        "apps_rg.runtime.orchestration.canonical_dispatch.run_canonical_apps_rg_from_cli_primitives",
        _wrap_canonical,
    )

    monkeypatch.setenv("APPS_RG_ALLOW_NON_ALLOW_EXIT_ZERO", "1")
    monkeypatch.setenv("APPS_RG_QWEN_OFFLINE_CONTRACT_STUB", "1")
    rc = main(
        [
            "--section",
            "competencies",
            "--target-company",
            "Synthetic Enterprise Corp.",
            "--target-role",
            "SVP Engineering",
            "--resume",
            str(REPO_ROOT / "apps_rg/resume/base/amit_ayer_base_resume_v1.json"),
            "--provider",
            "qwen_vllm",
            "--mock-judges",
            "--allow-test-mock-judges",
        ]
    )
    assert rc == 0
    assert called["canonical"] is True
    assert called["dispatch"] is False
