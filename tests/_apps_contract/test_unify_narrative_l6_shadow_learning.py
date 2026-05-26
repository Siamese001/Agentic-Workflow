"""L6 shadow learning for unify_narrative — post-X3 inert observation only."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests._apps_contract.lane_cli_common import (
    REPO_ROOT as REPO,
    artifact_dir_from_stdout,
    contract_artifact_dir,
    qwen_live_available,
    run_lane_cli,
)

pytestmark = pytest.mark.skipif(
    not qwen_live_available(),
    reason="unify_narrative L6 contract tests require live qwen_vllm",
)

_SYNTHETIC_COMPANY = "Synthetic Enterprise Corp."
_SYNTHETIC_ROLE = "SVP Engineering, Agentic AI Platforms"
_CACHED_RD: Path | None = None


def _latest() -> Path:
    global _CACHED_RD
    if _CACHED_RD is not None:
        return _CACHED_RD
    art = contract_artifact_dir("unify_narrative")
    rel = art.relative_to(REPO).as_posix()
    r = run_lane_cli(
        "unify_narrative",
        artifact_dir=rel,
        target_company=_SYNTHETIC_COMPANY,
        target_role=_SYNTHETIC_ROLE,
        timeout_s=600,
    )
    assert r.returncode == 0, r.stderr
    _CACHED_RD = artifact_dir_from_stdout(r)
    return _CACHED_RD


def test_canonical_run_emits_l6_shadow_learning_after_x3():
    rd = _latest()
    assert (rd / "x3_disposition.json").is_file()
    assert (rd / "l6_shadow_learning.json").is_file()
    x3 = json.loads((rd / "x3_disposition.json").read_text(encoding="utf-8"))
    learn = json.loads((rd / "l6_shadow_learning.json").read_text(encoding="utf-8"))
    assert learn.get("runtime_boundary_observed") is True
    assert learn.get("consumed_x3_code") == x3.get("x3_code")
    assert learn.get("section_id") == "unify_narrative"
    assert learn.get("current_run_mutation_assertion") is False
    assert learn.get("current_run_rescue_assertion") is False
    assert learn.get("durable_write_assertion") is False


def test_l6_learning_recommendations_are_future_run_only():
    learn = json.loads((_latest() / "l6_shadow_learning.json").read_text(encoding="utf-8"))
    for rec in learn.get("recommendation_records") or []:
        assert rec.get("applies_to") == "future_run_only"
