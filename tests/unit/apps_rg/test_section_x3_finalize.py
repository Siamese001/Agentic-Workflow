"""Unit tests for spine section X3 finalize edge cases."""
from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from apps_rg.runtime.spine.section_x3_finalize import (
    finalize_section_lane_x3,
    persist_section_x3_mirror,
    refresh_section_exit_after_x3_change,
)


def test_persist_section_x3_mirror_merges_extra(tmp_path: Path) -> None:
    x3 = SimpleNamespace(x3_code="X3_ALLOW", pass_=True)
    x3.to_dict = lambda: {"x3_code": "X3_ALLOW", "pass": True}  # type: ignore[method-assign]

    doc = persist_section_x3_mirror(
        tmp_path,
        x3,
        x3_doc_extra={"proof_eligible": True, "judge_proof_eligible": False},
    )
    assert doc["proof_eligible"] is True
    loaded = (tmp_path / "x3_disposition.json").read_text(encoding="utf-8")
    assert "proof_eligible" in loaded


@patch("apps_rg.runtime.spine.section_x3_finalize.ExitEvalPipeline")
@patch("apps_rg.runtime.spine.exit_lane_hooks.finalize_section_exit_after_l2")
def test_finalize_section_lane_x3_writes_exit_receipt(
    mock_exit_hooks: MagicMock,
    mock_pipeline_cls: MagicMock,
    tmp_path: Path,
) -> None:
    mock_pipeline_cls.return_value.run.return_value = SimpleNamespace(
        disposition=SimpleNamespace(value="X3_DENY")
    )
    runtime_payload: dict = {"run_id": "r1", "request_id": "req1"}
    x3 = SimpleNamespace(
        x3_code="X3_REVIEW_JUDGE_SOFT_FAIL",
        pass_=False,
    )
    x3.to_dict = lambda: {"x3_code": "X3_REVIEW_JUDGE_SOFT_FAIL", "pass": False}  # type: ignore[method-assign]

    (tmp_path / "sealed_l2_artifact.json").write_text(
        '{"schema_version":"section_sealed_l2_artifact_v1"}', encoding="utf-8"
    )
    runtime_payload["sealed_l2_artifact_ref"] = "sealed_l2_artifact.json"
    finalize_section_lane_x3(
        artifact_dir=tmp_path,
        section_id="executive_summary",
        runtime_payload=runtime_payload,
        x3_result=x3,
        skip_exit_receipts=False,
    )
    assert (tmp_path / "x3_disposition.json").is_file()
    mock_exit_hooks.assert_called_once()
    assert runtime_payload.get("spine_exit_eval_disposition") == "X3_DENY"


@patch("apps_rg.runtime.spine.section_x3_finalize.ExitEvalPipeline")
@patch("apps_rg.runtime.spine.exit_lane_hooks.finalize_section_exit_after_l2")
def test_refresh_section_exit_after_x3_change(
    mock_exit_hooks: MagicMock,
    mock_pipeline_cls: MagicMock,
    tmp_path: Path,
) -> None:
    mock_exit_hooks.reset_mock()
    runtime_payload = {"run_id": "r2"}
    (tmp_path / "sealed_l2_artifact.json").write_text(
        '{"schema_version":"section_sealed_l2_artifact_v1"}', encoding="utf-8"
    )
    runtime_payload["sealed_l2_artifact_ref"] = "sealed_l2_artifact.json"
    refresh_section_exit_after_x3_change(
        tmp_path,
        section_id="competencies",
        runtime_payload=runtime_payload,
        x3_doc={"x3_code": "X3_ALLOW", "pass": True},
    )
    mock_pipeline_cls.return_value.run.assert_called_once()
    mock_exit_hooks.assert_called_once()
