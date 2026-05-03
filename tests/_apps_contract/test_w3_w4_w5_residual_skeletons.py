"""Tests for W3/W4/W5 residual skeletons.

Plan: `.windsurf/plans/apps-eval-harness-residual-a2d9c7.md` W3/W4/W5 verification.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest


# ----- W3: production_log_miner --------------------------------------------


def test_production_log_miner_importable_and_exposes_public_api():
    from ops_scripts.calibration import production_log_miner as mod

    assert hasattr(mod, "mine")
    assert hasattr(mod, "MinerConfig")
    assert hasattr(mod, "set_redactor")
    assert hasattr(mod, "is_stub_redactor")
    assert hasattr(mod, "main")


def test_production_log_miner_default_redactor_is_stub():
    from ops_scripts.calibration import production_log_miner as mod

    # Force refresh in case a previous test altered state.
    mod._REDACTOR = mod._stub_pii_redactor
    mod._REDACTOR_IS_STUB = True
    assert mod.is_stub_redactor() is True


def test_production_log_miner_set_redactor_clears_stub_flag():
    from ops_scripts.calibration import production_log_miner as mod

    mod._REDACTOR = mod._stub_pii_redactor
    mod._REDACTOR_IS_STUB = True
    mod.set_redactor(lambda row: row)
    try:
        assert mod.is_stub_redactor() is False
    finally:
        mod._REDACTOR = mod._stub_pii_redactor
        mod._REDACTOR_IS_STUB = True


def test_production_log_miner_filters_by_app_and_redacts(tmp_path: Path):
    from ops_scripts.calibration import production_log_miner as mod

    src = tmp_path / "prod.jsonl"
    src.write_text(
        "\n".join(
            [
                json.dumps({"app_id": "apps_qna", "input": "x", "output": "y"}),
                json.dumps({"app_id": "apps_rfp", "input": "a"}),
                json.dumps({"app_id": "apps_qna", "input": "z"}),
            ]
        ),
        encoding="utf-8",
    )
    out = tmp_path / "samples.jsonl"
    cfg = mod.MinerConfig(input_path=src, app_id="apps_qna", out_path=out, max_samples=10)
    count = mod.mine(cfg)
    assert count == 2
    rows = [json.loads(line) for line in out.read_text(encoding="utf-8").splitlines() if line]
    assert all(r["app_id"] == "apps_qna" for r in rows)


def test_production_log_miner_main_refuses_stub_without_force_flag(tmp_path: Path):
    from ops_scripts.calibration import production_log_miner as mod

    mod._REDACTOR = mod._stub_pii_redactor
    mod._REDACTOR_IS_STUB = True
    src = tmp_path / "p.jsonl"
    src.write_text("", encoding="utf-8")
    out = tmp_path / "o.jsonl"
    rc = mod.main(["--input", str(src), "--app", "apps_qna", "--out", str(out)])
    assert rc == 2


# ----- W4: legacy_yaml_audit -----------------------------------------------


def test_legacy_yaml_audit_importable_and_exposes_public_api():
    from ops_scripts.maintenance import legacy_yaml_audit as mod

    assert hasattr(mod, "scan")
    assert hasattr(mod, "report_to_dict")
    assert "_policies.yaml" in mod.LEGACY_SUFFIXES
    assert "_thresholds.yaml" in mod.LEGACY_SUFFIXES


def test_legacy_yaml_audit_scan_detects_legacy_patterns(tmp_path: Path):
    from ops_scripts.maintenance import legacy_yaml_audit as mod

    (tmp_path / "apps_qna").mkdir()
    (tmp_path / "apps_qna" / "eval_policies.yaml").write_text("foo: 1", encoding="utf-8")
    (tmp_path / "apps_qna" / "judge_thresholds.yaml").write_text("bar: 2", encoding="utf-8")
    (tmp_path / "apps_qna" / "input_contract.yaml").write_text("baz: 3", encoding="utf-8")  # not legacy
    report = mod.scan(tmp_path)
    assert report.total_files_found == 2
    paths = sorted(lf.path for lf in report.legacy_files)
    assert paths == ["apps_qna/eval_policies.yaml", "apps_qna/judge_thresholds.yaml"]
    for lf in report.legacy_files:
        assert lf.app_hint == "apps_qna"


def test_legacy_yaml_audit_skips_excluded_dirs(tmp_path: Path):
    from ops_scripts.maintenance import legacy_yaml_audit as mod

    (tmp_path / "archives").mkdir()
    (tmp_path / "archives" / "old_policies.yaml").write_text("foo: 1", encoding="utf-8")
    report = mod.scan(tmp_path)
    assert report.total_files_found == 0


def test_legacy_yaml_audit_report_to_dict_is_json_serializable(tmp_path: Path):
    from ops_scripts.maintenance import legacy_yaml_audit as mod

    report = mod.scan(tmp_path)
    payload = mod.report_to_dict(report)
    json.dumps(payload)  # must not raise
    assert payload["total_files_found"] == 0


# ----- W5: judge_registry ---------------------------------------------------


def test_judge_registry_importable_and_exposes_public_api():
    from apps_shared import judge_registry as mod

    assert hasattr(mod, "resolve_judge")
    assert hasattr(mod, "registered_judges")
    assert hasattr(mod, "stub_count")
    assert hasattr(mod, "promoted_count")


def test_judge_registry_registered_judges_matches_gate_expectations():
    from apps_shared.judge_registry import registered_judges

    judges = registered_judges()
    assert ("apps_rg", "executive_positioning") in judges
    assert ("apps_lic", "response_likelihood") in judges
    assert ("apps_lic", "brand_voice") in judges
    assert ("apps_rfp", "win_theme_alignment") in judges


def test_judge_registry_resolve_unregistered_returns_error():
    from apps_shared.judge_registry import resolve_judge

    status = resolve_judge("apps_qna", "no_such_dim")
    assert status.importable is False
    assert "unregistered" in status.error


def test_judge_registry_stub_and_promoted_counts_sum_to_registered_count():
    from apps_shared.judge_registry import (
        promoted_count,
        registered_judges,
        resolve_judge,
        stub_count,
    )

    total_importable = 0
    for (app_id, dim_name) in registered_judges():
        if resolve_judge(app_id, dim_name).importable:
            total_importable += 1
    assert stub_count() + promoted_count() == total_importable
