from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

import pytest

from apps_rg.runtime.reports import generated_lane_rollup as glr
from apps_rg.runtime.runtime_proof_layout import (
    finalize_runtime_proof_run,
    load_latest_successful_real_pointer,
    prepare_runtime_proof_run_dir,
    resolve_accepted_real_rollup_run_dir,
    resolve_run_dir_from_pointer,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
ROLLUP_JSON = (
    REPO_ROOT / "artifacts" / "apps_rg" / "runtime_proofs" / "generated_lane_rollup" / "generated_lane_rollup.json"
)
ROLLUP_PY = REPO_ROOT / "apps_rg" / "runtime" / "reports" / "generated_lane_rollup.py"


def _lane_artifact_base(lane: str) -> Path:
    """Prefer accepted REAL_LLM+qwen rollup dir; fall back to legacy flat lane root."""
    rd, tag = resolve_accepted_real_rollup_run_dir(REPO_ROOT, lane)
    if rd is not None and tag != "missing_successful_real_run" and (rd / "x2_gate_outputs.json").is_file():
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
        "latest_real_attempt_run_id",
        "latest_successful_real_run_id",
        "accepted_real_evidence_resolution",
    ):
        assert key in row


def test_summary_includes_accepted_evidence_diagnostics(rollup_data: dict):
    s = rollup_data["summary"]
    if "lanes_accepted_evidence_via_migration_scan" not in s:
        pytest.skip("Regenerate generated_lane_rollup.json after pointer-semantics upgrade")
    assert "lanes_latest_real_attempt_blocked_but_accepted_rollup_REAL_LLM" in s


def test_no_registry_import_in_rollup():
    text = ROLLUP_PY.read_text(encoding="utf-8")
    lowered = text.lower()
    assert "registry" not in lowered


_LANE_PT = "headline"


def _write_json(p: Path, obj: dict) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _write_min_proof_bundle(rd: Path, *, run_id: str, runtime_generation_status: str) -> None:
    _write_json(
        rd / "provider_request.json",
        {"provider_requested": "qwen_vllm", "provider_attempted": runtime_generation_status == "REAL_LLM"},
    )
    _write_json(
        rd / "l2_output.json",
        {
            "run_id": run_id,
            "section_id": _LANE_PT,
            "runtime_generation_status": runtime_generation_status,
            "headline_line": "Unit headline",
        },
    )
    _write_json(rd / "x2_gate_outputs.json", {"gates": [], "x2_passed": 0, "x2_failed": 0, "total_x2_gates": 0})
    _write_json(rd / "x1d_llm_judge_outputs.json", {"judges": []})
    _write_json(
        rd / "x3_disposition.json",
        {
            "x3_code": "X3_BLOCK",
            "blocked_judges": [],
            "soft_failed_judges": [],
            "proceed_to_runtime": False,
        },
    )
    _write_json(rd / "l6_shadow_eval_package.json", {"offline_only": True})


def test_finalize_real_llm_writes_latest_successful_real_pointer(tmp_path: Path):
    repo = tmp_path
    rid = "ok_run"
    ad = prepare_runtime_proof_run_dir(repo, _LANE_PT, "qwen_vllm", rid)
    _write_min_proof_bundle(ad, run_id=rid, runtime_generation_status="REAL_LLM")
    finalize_runtime_proof_run(
        repo,
        _LANE_PT,
        "qwen_vllm",
        ad,
        run_id=rid,
        section_id=_LANE_PT,
        runtime_generation_status="REAL_LLM",
        provider_requested="qwen_vllm",
        provider_attempted=True,
        command="pytest",
    )
    sp = load_latest_successful_real_pointer(repo, _LANE_PT)
    assert sp is not None
    assert sp.get("run_id") == rid
    assert sp.get("runtime_generation_status") == "REAL_LLM"


def test_finalize_blocked_does_not_update_latest_successful_real_pointer(tmp_path: Path):
    repo = tmp_path
    ok = "ok_run"
    ad_ok = prepare_runtime_proof_run_dir(repo, _LANE_PT, "qwen_vllm", ok)
    _write_min_proof_bundle(ad_ok, run_id=ok, runtime_generation_status="REAL_LLM")
    finalize_runtime_proof_run(
        repo,
        _LANE_PT,
        "qwen_vllm",
        ad_ok,
        run_id=ok,
        section_id=_LANE_PT,
        runtime_generation_status="REAL_LLM",
        provider_requested="qwen_vllm",
        provider_attempted=True,
        command="pytest",
    )
    blocked = "blocked_run"
    ad_b = prepare_runtime_proof_run_dir(repo, _LANE_PT, "qwen_vllm", blocked)
    _write_min_proof_bundle(ad_b, run_id=blocked, runtime_generation_status="BLOCKED")
    finalize_runtime_proof_run(
        repo,
        _LANE_PT,
        "qwen_vllm",
        ad_b,
        run_id=blocked,
        section_id=_LANE_PT,
        runtime_generation_status="BLOCKED",
        provider_requested="qwen_vllm",
        provider_attempted=True,
        command="pytest",
    )
    sp = load_latest_successful_real_pointer(repo, _LANE_PT)
    assert sp is not None and sp.get("run_id") == ok
    latest_attempt = resolve_run_dir_from_pointer(repo, _LANE_PT, "real")
    assert latest_attempt is not None and latest_attempt.name == blocked


def test_mock_finalize_does_not_write_latest_successful_real_pointer(tmp_path: Path):
    repo = tmp_path
    rid = "mock_run"
    ad = prepare_runtime_proof_run_dir(repo, _LANE_PT, "mock", rid)
    _write_min_proof_bundle(ad, run_id=rid, runtime_generation_status="MOCKED")
    _write_json(ad / "provider_request.json", {"provider_requested": "mock"})
    finalize_runtime_proof_run(
        repo,
        _LANE_PT,
        "mock",
        ad,
        run_id=rid,
        section_id=_LANE_PT,
        runtime_generation_status="MOCKED",
        provider_requested="mock",
        provider_attempted=False,
        command="pytest",
    )
    assert load_latest_successful_real_pointer(repo, _LANE_PT) is None


def test_migration_scan_finds_prior_real_llm_when_successful_pointer_removed(tmp_path: Path):
    """Simulates blocked contract test overwriting latest_real but not polluting accepted evidence."""
    repo = tmp_path
    good = "good_run"
    ad_g = prepare_runtime_proof_run_dir(repo, _LANE_PT, "qwen_vllm", good)
    _write_min_proof_bundle(ad_g, run_id=good, runtime_generation_status="REAL_LLM")
    finalize_runtime_proof_run(
        repo,
        _LANE_PT,
        "qwen_vllm",
        ad_g,
        run_id=good,
        section_id=_LANE_PT,
        runtime_generation_status="REAL_LLM",
        provider_requested="qwen_vllm",
        provider_attempted=True,
        command="pytest",
    )
    succ = repo / "artifacts" / "apps_rg" / "runtime_proofs" / _LANE_PT / "latest_successful_real_run.json"
    assert succ.is_file()
    succ.unlink()

    bad = "bad_run"
    ad_b = prepare_runtime_proof_run_dir(repo, _LANE_PT, "qwen_vllm", bad)
    _write_min_proof_bundle(ad_b, run_id=bad, runtime_generation_status="BLOCKED")
    finalize_runtime_proof_run(
        repo,
        _LANE_PT,
        "qwen_vllm",
        ad_b,
        run_id=bad,
        section_id=_LANE_PT,
        runtime_generation_status="BLOCKED",
        provider_attempted=False,
        command="pytest-qwen-unavailable-contract",
        provider_requested="qwen_vllm",
    )

    rd, tag = resolve_accepted_real_rollup_run_dir(repo, _LANE_PT)
    assert tag == "migration_real_llm_qwen_vllm_scan"
    assert rd is not None and rd.name == good


def test_collect_lane_rolls_up_via_successful_bundle_not_blocked_attempt(tmp_path: Path):
    repo = tmp_path
    good = "good_run"
    ad_g = prepare_runtime_proof_run_dir(repo, _LANE_PT, "qwen_vllm", good)
    _write_min_proof_bundle(ad_g, run_id=good, runtime_generation_status="REAL_LLM")
    finalize_runtime_proof_run(
        repo,
        _LANE_PT,
        "qwen_vllm",
        ad_g,
        run_id=good,
        section_id=_LANE_PT,
        runtime_generation_status="REAL_LLM",
        provider_requested="qwen_vllm",
        provider_attempted=True,
        command="pytest",
    )
    (repo / "artifacts" / "apps_rg" / "runtime_proofs" / _LANE_PT / "latest_successful_real_run.json").unlink()
    bad = "bad_run"
    ad_b = prepare_runtime_proof_run_dir(repo, _LANE_PT, "qwen_vllm", bad)
    _write_min_proof_bundle(ad_b, run_id=bad, runtime_generation_status="BLOCKED")
    finalize_runtime_proof_run(
        repo,
        _LANE_PT,
        "qwen_vllm",
        ad_b,
        run_id=bad,
        section_id=_LANE_PT,
        runtime_generation_status="BLOCKED",
        provider_requested="qwen_vllm",
        provider_attempted=False,
        command="pytest",
    )
    row = glr.collect_lane(_LANE_PT, repo=repo, rollup_artifact_mode="real")
    assert row["rollup_source_run_dir"].replace("\\", "/").endswith(f"{_LANE_PT}/real/{good}")
    assert row["accepted_real_evidence_resolution"] == "migration_real_llm_qwen_vllm_scan"
    assert row["runtime_generation_status"] == "REAL_LLM"
    assert row["latest_real_attempt_runtime_generation_status"] == "BLOCKED"


def test_collect_lane_raises_when_no_accepted_real_bundle(tmp_path: Path):
    repo = tmp_path
    only = "blocked_only"
    ad = prepare_runtime_proof_run_dir(repo, _LANE_PT, "qwen_vllm", only)
    _write_min_proof_bundle(ad, run_id=only, runtime_generation_status="BLOCKED")
    finalize_runtime_proof_run(
        repo,
        _LANE_PT,
        "qwen_vllm",
        ad,
        run_id=only,
        section_id=_LANE_PT,
        runtime_generation_status="BLOCKED",
        provider_requested="qwen_vllm",
        provider_attempted=False,
        command="pytest",
    )
    with pytest.raises(FileNotFoundError, match="missing_successful_real_run"):
        glr.collect_lane(_LANE_PT, repo=repo, rollup_artifact_mode="real")
