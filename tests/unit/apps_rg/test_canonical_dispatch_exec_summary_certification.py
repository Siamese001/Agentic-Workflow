"""Regression tests for full-run executive-summary judge certification."""

from __future__ import annotations

import json
from pathlib import Path

import pytest


def test_canonical_full_resume_fails_on_exec_summary_judge_block(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    from apps_rg.runtime.orchestration import canonical_dispatch as cd

    class _FakeResult:
        run_id = "run-looks-successful"
        request_id = "req-looks-successful"
        x3_disposition = "X3D"
        fault = ""
        terminal_r5 = False

    from apps_rg.cache.whole_run_entrypoint_preflight import WholeRunCachePreflightOutcome

    def _fake_spine(**kwargs: object) -> _FakeResult:
        art = Path(kwargs["artifact_dir"])
        es_dir = art / "lanes" / "executive_summary"
        es_dir.mkdir(parents=True, exist_ok=True)
        (art / "agentic_core_how_trace.json").write_text("{}", encoding="utf-8")
        (art / "r4_run_manifest.json").write_text("{}", encoding="utf-8")
        (es_dir / "x3_disposition.json").write_text(
            json.dumps(
                {
                    "x3_code": "X3_REVIEW_JUDGE_SOFT_FAIL",
                    "pass": False,
                    "publish_disposition": "judge_certification_required",
                    "x1d_certified": False,
                    "blocking_judge_ids": ["gemini_pro"],
                }
            ),
            encoding="utf-8",
        )
        return _FakeResult()

    monkeypatch.setattr(cd, "run_integrated_single_action_spine", _fake_spine)
    monkeypatch.setattr(cd, "_default_artifact_dir", lambda explicit: tmp_path / "full_resume_old")
    monkeypatch.setattr(cd, "emit_integrated_run_bundle_index", lambda *a, **k: None)
    monkeypatch.setattr(cd, "_augment_integrated_manifest_with_apps_rg_docx", lambda *a, **k: None)
    monkeypatch.setattr(cd, "_augment_r4_run_manifest_for_apps_rg_l2_fault", lambda *a, **k: None)
    monkeypatch.setattr(
        "apps_rg.cache.whole_run_entrypoint_preflight.run_whole_run_cache_preflight",
        lambda **kwargs: WholeRunCachePreflightOutcome(
            entrypoint="canonical_dispatch",
            generation_required=True,
        ),
    )
    monkeypatch.setattr(
        "apps_rg.cache.whole_run_entrypoint_preflight.maybe_ingest_r1b_post_exit",
        lambda **k: None,
    )
    monkeypatch.setattr(
        "apps_rg.cache.cache_preflight_evidence.write_whole_run_cache_preflight_artifact",
        lambda *a, **k: None,
    )
    monkeypatch.setattr(
        "apps_rg.cache.cache_preflight_evidence.write_cache_miss_receipt",
        lambda *a, **k: None,
    )

    result = cd.run_canonical_full_resume_from_cli_primitives(
        target_company="Anthropic",
        target_role="Manager of Applied AI Architecture, Partnerships",
        jd="JD text",
        manual_brief="Brief text",
        artifact_dir=str(tmp_path / "full_resume_old"),
    )

    assert result["exit_status"] == "error"
    assert result["execution_status"] == "failed"
    assert result["outcome_authorized"] is False
    assert result["x3_disposition"] == "X3_REVIEW_JUDGE_SOFT_FAIL"
    assert result["executive_summary_certification_block"]["blocking_judge_ids"] == ["gemini_pro"]
