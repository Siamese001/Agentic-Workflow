from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

import pytest

from apps_rg.runtime.reports import generated_lane_rollup as glr
from apps_rg.runtime.runtime_proof_layout import resolve_run_dir_from_pointer

REPO_ROOT = Path(__file__).resolve().parents[2]
ROLLUP_JSON = (
    REPO_ROOT / "artifacts" / "apps_rg" / "runtime_proofs" / "generated_lane_rollup" / "generated_lane_rollup.json"
)
ROLLUP_PY = REPO_ROOT / "apps_rg" / "runtime" / "reports" / "generated_lane_rollup.py"


def _lane_artifact_base(lane: str) -> Path:
    """Prefer latest real run dir; fall back to legacy flat lane root for migration."""
    rd = resolve_run_dir_from_pointer(REPO_ROOT, lane, "real")
    if rd is not None and (rd / "x2_gate_outputs.json").is_file():
        return rd
    legacy = glr.RUNTIME_PROOFS / lane
    if (legacy / "x2_gate_outputs.json").is_file():
        return legacy
    pytest.skip(f"No x2_gate_outputs for lane {lane}")


@pytest.fixture(scope="module")
def rollup_data() -> dict:
    """Assumes `python -m apps_rg.runtime.reports.generated_lane_rollup` was run."""
    if not ROLLUP_JSON.is_file():
        pytest.skip(f"Missing rollup artifact: {ROLLUP_JSON} — run generated_lane_rollup first")
    return json.loads(ROLLUP_JSON.read_text(encoding="utf-8"))


def test_all_seven_lanes_present(rollup_data: dict):
    lanes = rollup_data["lanes"]
    assert set(lanes.keys()) == set(glr.GENERATED_LANES)


def test_each_lane_has_l2_x2_x1d_x3_l6_artifacts(rollup_data: dict):
    for lane, row in rollup_data["lanes"].items():
        for name in ("l2_output.json", "x2_gate_outputs.json", "x1d_llm_judge_outputs.json", "x3_disposition.json", "l6_shadow_eval_package.json"):
            rel = row["artifact_refs"][name]
            assert (REPO_ROOT / rel.replace("/", "\\")).is_file(), f"{lane}: {rel}"


def test_x2_failed_gates_explicitly_recorded():
    """Every failing X2 gate appears in failed_gate_ids; artifact failed_gates matches pass-derived set when present."""
    for lane in glr.GENERATED_LANES:
        base = _lane_artifact_base(lane)
        raw = json.loads((base / "x2_gate_outputs.json").read_text(encoding="utf-8"))
        x2n = glr._normalize_x2(raw)
        gates = x2n["gates"]
        failed_from_pass = {g["gate_id"] for g in gates if isinstance(g, dict) and not g.get("pass", True)}
        assert failed_from_pass == set(x2n["failed_gate_ids"])
        assert x2n["x2_failed"] == len(failed_from_pass)
        if isinstance(raw, dict) and "failed_gates" in raw and raw["failed_gates"] is not None:
            assert set(raw["failed_gates"]) == failed_from_pass


def test_no_proceed_when_blocked_or_soft_failed(rollup_data: dict):
    for lane, row in rollup_data["lanes"].items():
        if row.get("blocked_judges") or row.get("soft_failed_judges"):
            assert row.get("proceed_to_runtime") is False, lane


def test_unify_bullets_x3_matches_disk(rollup_data: dict):
    """Rollup reflects on-disk X3 (ALLOW is not guaranteed when judges/providers regress)."""
    base = _lane_artifact_base("unify_bullets")
    disk = json.loads((base / "x3_disposition.json").read_text(encoding="utf-8"))
    assert rollup_data["lanes"]["unify_bullets"]["x3_code"] == disk.get("x3_code")


def test_l6_offline_all_lanes(rollup_data: dict):
    for lane, row in rollup_data["lanes"].items():
        assert row.get("l6_offline_only") is True, lane


def test_rollup_module_has_no_agentic_core_import():
    text = ROLLUP_PY.read_text(encoding="utf-8")
    assert "from agentic_core" not in text
    assert "import agentic_core" not in text
    assert "agentic_core." not in text


def test_collect_lane_matches_build_rollup():
    try:
        full = glr.build_rollup(rollup_artifact_mode="real")
        mode: Literal["real", "mock"] = "real"
    except FileNotFoundError:
        try:
            full = glr.build_rollup(rollup_artifact_mode="mock")
            mode = "mock"
        except FileNotFoundError:
            pytest.skip("No complete run-scoped artifacts for all seven lanes (run mock or real dispatches)")
    assert full["lanes"]["headline"] == glr.collect_lane("headline", rollup_artifact_mode=mode)


def test_freshness_metadata_present(rollup_data: dict):
    assert "evidence_pack_commands" in rollup_data
    for lane in glr.GENERATED_LANES:
        fr = rollup_data["lanes"][lane]["freshness"]
        assert fr.get("canonical_command")
        assert fr.get("generated_at_utc")
        assert "artifact_mtimes_utc" in fr
        assert "l2_run_id" in fr
        assert fr.get("runtime_generation_status") == rollup_data["lanes"][lane]["runtime_generation_status"]


def test_summary_has_runtime_generation_buckets(rollup_data: dict):
    s = rollup_data["summary"]
    assert "lanes_runtime_generation_REAL_LLM" in s
    assert "lanes_runtime_generation_MOCKED" in s
    if "current_rollup_artifact_mode" in rollup_data:
        assert rollup_data["current_rollup_artifact_mode"] in ("real_only", "mock")
        assert "artifact_isolation" in rollup_data


def test_lane_rows_include_run_pointer_fields(rollup_data: dict):
    row = rollup_data["lanes"]["headline"]
    if "rollup_source_run_dir" not in row:
        pytest.skip("Rollup JSON predates run-scoped pointers; regenerate rollup")
    for key in (
        "latest_real_run_id",
        "rollup_source_run_dir",
        "latest_real_artifact_path",
    ):
        assert key in row


def test_no_registry_import_in_rollup():
    text = ROLLUP_PY.read_text(encoding="utf-8")
    lowered = text.lower()
    assert "registry" not in lowered
