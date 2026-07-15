from __future__ import annotations

import stat
from pathlib import Path

import pytest

from apps_rg.evals.c03_proxy_eval import (
    build_proxy_report,
    emit_proxy_artifacts,
    validate_proxy_report,
    validate_proxy_summary,
)
from ops_scripts.ci.check_apps_rg_resume_graph_w6 import validate_artifact

REPO_ROOT = Path(__file__).resolve().parents[4]
PROFILE = REPO_ROOT / "apps_rg/config/domain_contract/resume_graph_evaluation_profile.yaml"
BLOCKER = REPO_ROOT / "docs/reports/apps_rg/c03_resume_graph_w6_blocker.json"


def test_proxy_is_explicitly_non_authoritative_and_deterministic() -> None:
    first = build_proxy_report(profile_path=PROFILE, blocker_path=BLOCKER)
    second = build_proxy_report(profile_path=PROFILE, blocker_path=BLOCKER)
    assert first == second
    assert first["evidence_class"] == "PROVISIONAL_MODEL_PROXY"
    assert first["authority"]["official_w6_status"] == "UNKNOWN"
    assert first["authority"]["release_gate_eligible"] is False
    assert first["authority"]["promotion_eligible"] is False
    assert first["authority"]["active_threshold"] is None


def test_proxy_outputs_are_private_and_official_checker_rejects_summary(
    tmp_path: Path,
) -> None:
    report_path = tmp_path / "controlled" / "full.json"
    summary_path = tmp_path / "controlled" / "summary.json"
    _, summary = emit_proxy_artifacts(
        profile_path=PROFILE,
        blocker_path=BLOCKER,
        report_path=report_path,
        summary_path=summary_path,
    )
    assert stat.S_IMODE(report_path.stat().st_mode) == 0o600
    assert stat.S_IMODE(summary_path.stat().st_mode) == 0o600
    assert stat.S_IMODE(report_path.parent.stat().st_mode) == 0o700
    assert summary["official_status"] == "UNKNOWN"
    assert validate_artifact(summary_path)


def test_report_and_summary_tampering_is_rejected(tmp_path: Path) -> None:
    report_path = tmp_path / "controlled" / "full.json"
    summary_path = tmp_path / "controlled" / "summary.json"
    report, summary = emit_proxy_artifacts(
        profile_path=PROFILE,
        blocker_path=BLOCKER,
        report_path=report_path,
        summary_path=summary_path,
    )
    report["authority"]["promotion_eligible"] = True
    with pytest.raises(ValueError):
        validate_proxy_report(report)
    summary["official_status"] = "PASS"
    with pytest.raises(ValueError):
        validate_proxy_summary(summary)


def test_closed_schema_rejects_provenance_override() -> None:
    report = build_proxy_report(profile_path=PROFILE, blocker_path=BLOCKER)
    report["source"]["operator_override"] = "forged"
    # The record digest covers nested provenance, so even a nested extra field
    # cannot survive validation.
    with pytest.raises(ValueError):
        validate_proxy_report(report)
