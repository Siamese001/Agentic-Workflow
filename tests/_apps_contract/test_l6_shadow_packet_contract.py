"""Contract tests for apps_rg L6 shadow handoff packets (rollup + package X3 integration)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.runtime.package.resume_package_l6_audit import TOP_REQUIRED_SCALAR, audit_l6_shadow_packet_for_lane
from apps_rg.runtime.package.resume_package_manifest import RUNTIME_PROOFS, resolve_resume_package_paths, repo_root_default
from apps_rg.runtime.shadow.l6_handoff_packet import (
    IBM_REWRITE_POLICY_ID,
    L6_PACKET_TYPE,
    L6_PACKET_VERSION,
    UNIFY_REWRITE_POLICY_ID,
)
from apps_rg.runtime.reports.generated_lane_rollup import GENERATED_LANES

REPO_ROOT = Path(__file__).resolve().parents[2]
ROLLUP_JSON = REPO_ROOT / "artifacts" / "apps_rg" / "runtime_proofs" / "generated_lane_rollup" / "generated_lane_rollup.json"
PKG_X3 = REPO_ROOT / RUNTIME_PROOFS / "resume_package" / "resume_package_x3_disposition.json"
RESUME_PKG_MOD = REPO_ROOT / "apps_rg" / "runtime" / "package" / "resume_package_x3.py"


@pytest.fixture(scope="module")
def rollup_workspace() -> dict:
    if not ROLLUP_JSON.is_file():
        pytest.skip(f"Missing {ROLLUP_JSON} — run generated_lane_rollup after lane dispatches")
    return json.loads(ROLLUP_JSON.read_text(encoding="utf-8"))


def _l6_packet(repo_root: Path, rollup: dict, lane_key: str) -> dict:
    rel = rollup["lanes"][lane_key]["artifact_refs"]["l6_shadow_eval_package.json"]
    raw = json.loads((repo_root / rel).read_text(encoding="utf-8"))
    assert isinstance(raw, dict)
    return raw


REGEN_HINT = (
    "Run the seven REAL_LLM lane dispatches, "
    "`python -m apps_rg.runtime.reports.generated_lane_rollup`, "
    "then `python -m apps_rg.runtime.package.resume_package_x3`."
)


@pytest.fixture(scope="module")
def rollup_handoff_v1(rollup_workspace: dict) -> dict:
    bad: list[str] = []
    for lk in GENERATED_LANES:
        pkt = _l6_packet(REPO_ROOT, rollup_workspace, lk)
        if pkt.get("packet_type") != L6_PACKET_TYPE or str(pkt.get("packet_version")) != str(L6_PACKET_VERSION):
            bad.append(lk)
    if bad:
        pytest.skip(
            "Workspace L6 artifacts are legacy or incomplete for lanes "
            f"{sorted(bad)}. {REGEN_HINT}"
        )
    return rollup_workspace


def _ref_exists(rr: Path, ref: object) -> bool:
    return isinstance(ref, str) and bool(ref.strip()) and (rr / ref.strip()).is_file()


def test_each_generated_lane_rollups_l6_shadow_file(rollup_workspace: dict):
    for lk in GENERATED_LANES:
        rel = rollup_workspace["lanes"][lk]["artifact_refs"]["l6_shadow_eval_package.json"]
        assert (REPO_ROOT / rel).is_file(), lk


def test_l6_packet_required_top_level_fields(rollup_handoff_v1: dict):
    for lk in GENERATED_LANES:
        pkt = _l6_packet(REPO_ROOT, rollup_handoff_v1, lk)
        missing = sorted(TOP_REQUIRED_SCALAR - set(pkt.keys()))
        assert not missing, f"{lk}: {missing}"
        assert pkt["packet_type"] == L6_PACKET_TYPE


def test_l6_packet_refs_point_to_existing_artifacts(rollup_handoff_v1: dict):
    for lk in GENERATED_LANES:
        pkt = _l6_packet(REPO_ROOT, rollup_handoff_v1, lk)
        for key in (
            "section_output_ref",
            "x1d_judge_outputs_ref",
            "x2_gate_outputs_ref",
            "x3_disposition_ref",
        ):
            assert _ref_exists(REPO_ROOT, pkt.get(key)), f"{lk}:{key}"


def test_l6_packet_runtime_run_dir_links_when_present(rollup_handoff_v1: dict):
    """Newer handoffs include explicit runtime proof dir + L6 self-path (regenerate rollup after upgrade)."""
    for lk in GENERATED_LANES:
        pkt = _l6_packet(REPO_ROOT, rollup_handoff_v1, lk)
        rd = pkt.get("runtime_proof_run_dir_repo_relative")
        if isinstance(rd, str) and rd.strip():
            p = REPO_ROOT / rd.replace("\\", "/")
            assert p.is_dir(), f"{lk}:runtime_proof_run_dir_repo_relative:{rd}"
        l6p = pkt.get("l6_shadow_eval_package_repo_relative")
        if isinstance(l6p, str) and l6p.strip():
            p = REPO_ROOT / l6p.replace("\\", "/")
            assert p.is_file(), f"{lk}:l6_shadow_eval_package_repo_relative:{l6p}"


def test_l6_generator_and_gate_summaries(rollup_handoff_v1: dict):
    for lk in GENERATED_LANES:
        pkt = _l6_packet(REPO_ROOT, rollup_handoff_v1, lk)
        gm = pkt["generator_metadata"]
        for k in (
            "generator_provider",
            "generator_model",
            "prompt_id",
            "prompt_hash",
            "temperature",
            "max_tokens",
            "provider_request_ref",
        ):
            assert k in gm, f"{lk}:generator_metadata:{k}"
        x2s = pkt["x2_summary"]
        for k in ("x2_total", "x2_passed", "x2_failed", "failed_gate_ids"):
            assert k in x2s, f"{lk}:x2:{k}"
        x1s = pkt["x1d_summary"]
        for k in (
            "judge_provider_statuses",
            "judge_scores",
            "judge_thresholds",
            "normalized_scores",
            "normalized_thresholds",
            "decisive_failures",
            "soft_failed_judges",
            "blocked_judges",
            "mocked_judges",
        ):
            assert k in x1s, f"{lk}:x1d:{k}"
        x3s = pkt["x3_summary"]
        for k in ("x3_code", "authorization_scope", "proceed_to_runtime", "pass", "decisive_reason"):
            assert k in x3s, f"{lk}:x3:{k}"


def test_l6_placeholder_and_safety_flags(rollup_handoff_v1: dict):
    for lk in GENERATED_LANES:
        pkt = _l6_packet(REPO_ROOT, rollup_handoff_v1, lk)
        assert pkt["human_label_required"] is True
        assert pkt["human_label_status"] == "MISSING"
        assert pkt["human_label_ref"] is None
        assert pkt["benchmark_set_id"] is None
        assert pkt["calibration_status"] == "NOT_CALIBRATED"
        assert pkt["recommendation_packet_ref"] is None
        assert pkt["promotion_allowed"] is False
        assert pkt["learning_mutation_performed"] is False
        assert pkt["runtime_approval_authority"] == "NONE"
        assert pkt["current_run_mutation_allowed"] is False
        assert pkt["prompt_mutation_performed"] is False
        assert pkt["gate_mutation_performed"] is False
        assert pkt["judge_mutation_performed"] is False
        assert pkt["threshold_mutation_performed"] is False


def test_unify_bullets_rewrite_envelope_exact(rollup_handoff_v1: dict):
    pkt = _l6_packet(REPO_ROOT, rollup_handoff_v1, "unify_bullets")
    assert pkt["rewrite_policy_id"] == UNIFY_REWRITE_POLICY_ID
    rd = pkt["rewrite_distribution"]
    assert int(rd["HEAVY"]) == 2
    assert int(rd["MODERATE"]) == 3
    assert int(rd["LIGHT_PROTECTED"]) == 1
    brm = pkt["bullet_rewrite_map"]
    assert isinstance(brm, list) and len(brm) >= 6
    prot = next((r for r in brm if r.get("bullet_id") == "bul_unify_006"), None)
    assert prot is not None
    assert prot.get("protected") is True


def test_ibm_bullets_rewrite_envelope_exact(rollup_handoff_v1: dict):
    pkt = _l6_packet(REPO_ROOT, rollup_handoff_v1, "ibm_bullets")
    assert pkt["rewrite_policy_id"] == IBM_REWRITE_POLICY_ID
    rd = pkt["rewrite_distribution"]
    assert int(rd["HEAVY"]) == 0
    assert int(rd["MODERATE"]) == 3
    assert int(rd["LIGHT_PROTECTED"]) == 2
    brm = pkt["bullet_rewrite_map"]
    assert isinstance(brm, list) and len(brm) >= 5


def test_lane_audits_not_fatal_when_packets_complete(rollup_handoff_v1: dict):
    for lk in GENERATED_LANES:
        pkt = _l6_packet(REPO_ROOT, rollup_handoff_v1, lk)
        rec = audit_l6_shadow_packet_for_lane(lane_key=lk, packet=pkt)
        assert rec["fatal"] is False, (lk, rec.get("incomplete_field_paths_sorted"))


def test_resume_package_source_has_no_generation_calls():
    src = RESUME_PKG_MOD.read_text(encoding="utf-8").lower()
    for token in ("httpx.", "requests.", "openai", "anthropic", "google.generativeai"):
        assert token not in src


@pytest.mark.skipif(not PKG_X3.is_file(), reason="resume package not emitted yet")
def test_workspace_package_audit_covers_all_lanes(rollup_handoff_v1: dict):
    d = json.loads(PKG_X3.read_text(encoding="utf-8"))
    per = d.get("l6_shadow_handoff_audit", {}).get("per_lane") or {}
    if not per:
        pytest.skip("Stale resume_package_x3_disposition.json (no per_lane); re-run resume_package_x3 module.")
    assert set(per) == set(GENERATED_LANES)
    paths = resolve_resume_package_paths(repo_root=repo_root_default())
    rollup = json.loads(paths.rollup_json.read_text(encoding="utf-8"))
    for lk in GENERATED_LANES:
        rel_n = rollup["lanes"][lk]["artifact_refs"]["l6_shadow_eval_package.json"].replace("\\", "/")
        ref_obs = (per[lk].get("l6_shadow_eval_ref_repo_relative") or "").replace("\\", "/")
        if ref_obs != rel_n:
            pytest.skip(
                f"Stale resume_package_x3_disposition.json vs rollup for {lk}: "
                f"package refs {ref_obs!r}, rollup {rel_n!r}; re-run resume_package_x3 after rollup refresh."
            )

