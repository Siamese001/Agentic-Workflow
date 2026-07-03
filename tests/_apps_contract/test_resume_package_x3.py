"""Offline resume package aggregation (deterministic X2 rollup → package X3; no providers)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.runtime.package.resume_package_manifest import (
    RUNTIME_PROOFS,
    ResumePackageProofPaths,
    repo_root_default,
    resolve_resume_package_paths,
)
from apps_rg.runtime.shadow.l6_handoff_packet import build_l6_shadow_handoff_dict
from apps_rg.runtime.package.resume_package_l6_audit import audit_l6_shadow_packet_for_lane
from apps_rg.runtime.internal.resume_package_disposition import (
    X3_ALLOW_CODE,
    X3_BLOCKED_DETERMINISTIC,
    X3_BLOCK_L6_HANDOFF_INCOMPLETE,
    X3_REVIEW_SECTION,
    emit_resume_package_artifacts,
    evaluate_resume_package,
)
from apps_rg.runtime.internal.generated_lane_rollup import GENERATED_LANES


_ART = RUNTIME_PROOFS


@pytest.fixture(autouse=True)
def _resume_package_contract_test_harness(monkeypatch: pytest.MonkeyPatch) -> None:
    """Synthetic package fixtures are not product runs; disable fail-closed lane bar."""
    monkeypatch.setenv("APPS_RG_TEST_HARNESS", "1")
    monkeypatch.setenv("APPS_RG_SECTION_RUNTIME_EXHAUST_KILL_SWITCH", "0")
    monkeypatch.delenv("APPS_RG_WHOLE_RUN_ENVELOPE", raising=False)
    monkeypatch.delenv("APPS_RG_CORRELATED_CLI_RUN", raising=False)


def _mk_x2(pass_all: bool) -> dict[str, object]:
    if pass_all:
        return {"gate_family": "test", "all_pass": True, "failed_gate_ids": [], "gates": []}
    return {
        "gate_family": "test",
        "all_pass": False,
        "failed_gate_ids": ["x2_fake_fail"],
        "gates": [{"gate_id": "x2_fake_fail", "pass": False, "gate_type": "deterministic"}],
    }


def _x3_stub(code: str = X3_ALLOW_CODE) -> dict[str, object]:
    return {
        "x3_code": code,
        "authorization_scope": "PLUMBING_ONLY",
        "proceed_to_runtime": False,
        "pass": code == X3_ALLOW_CODE,
        "decisive_reason": "",
        "review_reason": None if code == X3_ALLOW_CODE else "review",
    }


def _emit_lane_dir(rr: Path, lk: str) -> dict[str, str]:
    ldir = rr / _ART / f"synth_lane_{lk}"
    ldir.mkdir(parents=True, exist_ok=True)
    (ldir / "provider_request.json").write_text(
        json.dumps(
            {
                "provider_requested": "retired_provider_profile",
                "provider_attempted": True,
                "model": "Synthetic/RetiredProviderStub",
                "temperature": 0.4,
                "max_tokens": 1200,
                "prompt_hash": "a" * 16,
            }
        ),
        encoding="utf-8",
    )
    rid = f"synthetic_{lk}"
    l2: dict[str, object] = {
        "run_id": rid,
        "section_id": lk,
        "runtime_generation_status": "REAL_LLM",
        "product_quality_status": "PASS",
        "product_quality_reason": "synthetic_fixture",
        "prompt_id": f"synthetic_prompt_{lk}",
        "prompt_hash": "b" * 16,
    }
    if lk == "unify_bullets":
        specs = [f"bul_unify_{i:03d}" for i in range(1, 7)]
        l2["bullets"] = [
            {
                "bullet_id": bid,
                "bullet_text": f"text for {bid}",
                "has_metric": bid == "bul_unify_006",
                "metric_raw": "metric" if bid == "bul_unify_006" else "",
                "source_fact_ids": [bid],
            }
            for bid in specs
        ]
    elif lk == "ibm_bullets":
        l2["bullets"] = [
            {
                "bullet_id": bid,
                "bullet_text": f"ibm {bid}",
                "has_metric": False,
                "metric_raw": "",
                "source_fact_ids": [bid],
            }
            for bid in (
                "bul_ibm_001",
                "bul_ibm_002",
                "bul_ibm_003",
                "bul_ibm_004",
                "bul_ibm_005",
            )
        ]

    (ldir / "l2_output.json").write_text(json.dumps(l2), encoding="utf-8")
    (ldir / "x1d_llm_judge_outputs.json").write_text(json.dumps({"judges": []}), encoding="utf-8")
    (ldir / "x2_gate_outputs.json").write_text(json.dumps(_mk_x2(True)), encoding="utf-8")
    (ldir / "x3_disposition.json").write_text(json.dumps(_x3_stub()), encoding="utf-8")
    rid = str(l2.get("run_id") or f"synthetic_{lk}")
    exhaust = {
        "schema_version": "section_runtime_exhaust_bundle_v1",
        "section_id": lk,
        "run_id": rid,
        "x3_code": X3_ALLOW_CODE,
        "current_run_closed": True,
        "created_after_exit": True,
    }
    (ldir / "runtime_exhaust_bundle.json").write_text(json.dumps(exhaust), encoding="utf-8")
    (ldir / "exit_disposition_receipt.json").write_text(
        json.dumps({"x3_code": X3_ALLOW_CODE, "run_id": rid}),
        encoding="utf-8",
    )
    (ldir / "l6_shadow_handoff_receipt.json").write_text(
        json.dumps({"section_id": lk, "run_id": rid, "handoff_sealed": True}),
        encoding="utf-8",
    )

    l6 = build_l6_shadow_handoff_dict(
        artifact_dir=ldir,
        repo_root=rr,
        section_id=lk,
        prompt_id=str(l2["prompt_id"]),
        temperature=0.4,
        max_tokens=1200,
    )
    (ldir / "l6_shadow_eval_package.json").write_text(json.dumps(l6), encoding="utf-8")

    return {
        "l2_output.json": f"{_ART}/synth_lane_{lk}/l2_output.json",
        "x1d_llm_judge_outputs.json": f"{_ART}/synth_lane_{lk}/x1d_llm_judge_outputs.json",
        "x2_gate_outputs.json": f"{_ART}/synth_lane_{lk}/x2_gate_outputs.json",
        "x3_disposition.json": f"{_ART}/synth_lane_{lk}/x3_disposition.json",
        "l6_shadow_eval_package.json": f"{_ART}/synth_lane_{lk}/l6_shadow_eval_package.json",
    }


def _write_minimal_fixture_tree(rr: Path) -> ResumePackageProofPaths:
    """Build a coherent fake proof tree under tmp repo root (seven generated lanes ALLOW)."""
    lanes_block: dict[str, object] = {}
    for lk in GENERATED_LANES:
        refs = _emit_lane_dir(rr, lk)
        lanes_block[lk] = {
            "runtime_generation_status": "REAL_LLM",
            "x2_failed": 0,
            "x3_code": X3_ALLOW_CODE,
            "artifact_refs": refs,
        }

    rollup = {"rollup_id": "synthetic_rollup", "lanes": lanes_block}
    (rr / _ART / "generated_lane_rollup").mkdir(parents=True, exist_ok=True)
    (rr / _ART / "generated_lane_rollup" / "generated_lane_rollup.json").write_text(
        json.dumps(rollup), encoding="utf-8"
    )

    lc_x2_path = rr / _ART / "locked_copy" / "locked_copy_x2_gate_outputs.json"
    lc_x2_path.parent.mkdir(parents=True, exist_ok=True)
    (lc_x2_path.parent / "locked_copy_manifest.json").write_text("{}", encoding="utf-8")
    lc_x2_path.write_text(json.dumps(_mk_x2(True)), encoding="utf-8")

    asm = rr / _ART / "final_resume_assembly"
    asm.mkdir(parents=True, exist_ok=True)
    (asm / "final_resume.json").write_text("{}", encoding="utf-8")
    (asm / "final_resume_manifest.json").write_text(
        json.dumps(
            {
                "calls": {
                    "provider_calls_made": False,
                    "PROVIDER_MODEL_calls_made": False,
                    "retired_provider_calls_made": False,
                    "judge_calls_made": False,
                },
                "rollup_id_source": "synthetic",
            }
        ),
        encoding="utf-8",
    )
    (asm / "final_resume_x2_gate_outputs.json").write_text(json.dumps(_mk_x2(True)), encoding="utf-8")

    dm_dir = rr / _ART / "docx_manifest"
    dm_dir.mkdir(parents=True, exist_ok=True)
    (dm_dir / "docx_manifest.json").write_text(
        json.dumps(
            {
                "guarantees": {
                    "provider_calls_made": False,
                    "PROVIDER_MODEL_calls_made": False,
                    "retired_provider_calls_made": False,
                    "judge_calls_made": False,
                }
            }
        ),
        encoding="utf-8",
    )
    (dm_dir / "docx_manifest_x2_gate_outputs.json").write_text(json.dumps(_mk_x2(True)), encoding="utf-8")

    docx_rel = f"{_ART}/docx/out.docx"
    doc_dir = rr / _ART / "docx"
    doc_dir.mkdir(parents=True, exist_ok=True)
    (doc_dir / "out.docx").write_bytes(b"fake docx")
    drm = {
        "output_docx": docx_rel,
        "verification": {
            k: False
            for k in (
                "provider_calls_made",
                "PROVIDER_MODEL_calls_made",
                "retired_provider_calls_made",
                "judge_calls_made",
            )
        },
    }
    (doc_dir / "docx_render_manifest.json").write_text(json.dumps(drm), encoding="utf-8")
    (doc_dir / "docx_render_x2_gate_outputs.json").write_text(json.dumps(_mk_x2(True)), encoding="utf-8")

    return resolve_resume_package_paths(repo_root=rr, output_rel=f"{_ART}/resume_package")


def _workspace_package_paths_or_skip() -> ResumePackageProofPaths:
    rr = repo_root_default()
    p = resolve_resume_package_paths(repo_root=rr)
    if not (
        p.rollup_json.is_file()
        and p.final_resume_x2_json.is_file()
        and p.docx_render_x2_json.is_file()
        and p.package_manifest_json().is_file()
        and p.package_x3_json().is_file()
        and p.package_receipt_json().is_file()
    ):
        pytest.skip("resume_package artifacts absent; call emit_resume_package_artifacts() in tests or run canonical lanes first")
    return p


def test_package_manifest_x3_and_receipt_exist():
    p = _workspace_package_paths_or_skip()
    assert p.package_manifest_json().is_file()
    assert p.package_x3_json().is_file()
    assert p.package_receipt_json().is_file()


def test_manifest_references_rollups_and_proofs():
    p = _workspace_package_paths_or_skip()
    m = json.loads(p.package_manifest_json().read_text(encoding="utf-8"))
    s = m["sources"]
    assert "generated_lane_rollup" in s["generated_lane_rollup_json"].replace("\\", "/")
    assert "locked_copy_manifest_json" in s
    assert "final_resume_manifest_json" in s
    assert "docx_manifest_json" in s
    assert "docx_render_manifest_json" in s


def test_section_x3_summary_not_allow_for_real_workspace_when_review():
    p = resolve_resume_package_paths(repo_root=repo_root_default())
    if not p.package_x3_json().is_file():
        pytest.skip("package X3 disposition not emitted yet")
    d = json.loads(p.package_x3_json().read_text(encoding="utf-8"))
    if d["final_x3_code"] == X3_ALLOW_CODE:
        assert d["section_level_x3"]["all_generated_lane_x3_allow"] is True
    else:
        assert d["section_level_x3"]["all_generated_lane_x3_allow"] is False
        assert d["final_x3_code"] != X3_ALLOW_CODE


@pytest.mark.parametrize(
    "layer",
    ["locked_copy_x2", "final_resume_x2"],
)
def test_deterministic_x2_failure_blocks(tmp_path: Path, layer: str):
    paths = _write_minimal_fixture_tree(tmp_path)
    rollup = json.loads(paths.rollup_json.read_text(encoding="utf-8"))

    payloads = {
        "locked_copy_x2": (paths.locked_copy_x2_json, _mk_x2(False)),
        "final_resume_x2": (paths.final_resume_x2_json, _mk_x2(False)),
        "docx_manifest_x2": (paths.docx_manifest_x2_json, _mk_x2(False)),
        "docx_render_x2": (paths.docx_render_x2_json, _mk_x2(False)),
    }
    pj, blob = payloads[layer]
    pj.write_text(json.dumps(blob), encoding="utf-8")

    dsp = evaluate_resume_package(
        paths=paths,
        rollup=rollup,
        locked_x2=json.loads(paths.locked_copy_x2_json.read_text(encoding="utf-8")),
        final_manifest=json.loads(paths.final_resume_manifest_json.read_text(encoding="utf-8")),
        final_x2=json.loads(paths.final_resume_x2_json.read_text(encoding="utf-8")),
        docx_manifest=json.loads(paths.docx_manifest_json.read_text(encoding="utf-8")),
        docx_manifest_x2=json.loads(paths.docx_manifest_x2_json.read_text(encoding="utf-8")),
        docx_render_manifest=json.loads(paths.docx_render_manifest_json.read_text(encoding="utf-8")),
        docx_render_x2=json.loads(paths.docx_render_x2_json.read_text(encoding="utf-8")),
    )
    assert dsp["final_x3_code"] == X3_BLOCKED_DETERMINISTIC
    assert dsp["deterministic_blocked"] is True


@pytest.mark.parametrize("layer", ["docx_manifest_x2", "docx_render_x2"])
def test_docx_x2_failure_blocks_only_when_docx_required(
    tmp_path: Path, layer: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APPS_RG_DOCX_OUTPUT_REQUIRED", "1")
    paths = _write_minimal_fixture_tree(tmp_path)
    rollup = json.loads(paths.rollup_json.read_text(encoding="utf-8"))

    payloads = {
        "docx_manifest_x2": (paths.docx_manifest_x2_json, _mk_x2(False)),
        "docx_render_x2": (paths.docx_render_x2_json, _mk_x2(False)),
    }
    pj, blob = payloads[layer]
    pj.write_text(json.dumps(blob), encoding="utf-8")

    dsp = evaluate_resume_package(
        paths=paths,
        rollup=rollup,
        locked_x2=json.loads(paths.locked_copy_x2_json.read_text(encoding="utf-8")),
        final_manifest=json.loads(paths.final_resume_manifest_json.read_text(encoding="utf-8")),
        final_x2=json.loads(paths.final_resume_x2_json.read_text(encoding="utf-8")),
        docx_manifest=json.loads(paths.docx_manifest_json.read_text(encoding="utf-8")),
        docx_manifest_x2=json.loads(paths.docx_manifest_x2_json.read_text(encoding="utf-8")),
        docx_render_manifest=json.loads(paths.docx_render_manifest_json.read_text(encoding="utf-8")),
        docx_render_x2=json.loads(paths.docx_render_x2_json.read_text(encoding="utf-8")),
    )
    assert dsp["final_x3_code"] == X3_BLOCKED_DETERMINISTIC
    assert dsp["deterministic_blocked"] is True


def test_section_review_yields_review_not_allow(tmp_path: Path):
    paths = _write_minimal_fixture_tree(tmp_path)
    rollup_raw = paths.rollup_json.read_text(encoding="utf-8")
    rollup_obj = json.loads(rollup_raw)
    first_lane = GENERATED_LANES[0]
    lane = dict(rollup_obj["lanes"][first_lane])
    lane["x3_code"] = "X3_REVIEW_JUDGE_SOFT_FAIL"
    rollup_obj["lanes"][first_lane] = lane
    x3_rel = lane["artifact_refs"]["x3_disposition.json"]
    x3_abs = tmp_path / x3_rel
    x3_abs.write_text(json.dumps(_x3_stub("X3_REVIEW_JUDGE_SOFT_FAIL")), encoding="utf-8")
    ldir = x3_abs.parent
    l2_blob = json.loads((ldir / "l2_output.json").read_text(encoding="utf-8"))
    l6_upd = build_l6_shadow_handoff_dict(
        artifact_dir=ldir,
        repo_root=tmp_path,
        section_id=first_lane,
        prompt_id=str(l2_blob["prompt_id"]),
        temperature=0.4,
        max_tokens=1200,
    )
    l6_rel = lane["artifact_refs"]["l6_shadow_eval_package.json"]
    (tmp_path / l6_rel).write_text(json.dumps(l6_upd), encoding="utf-8")

    dsp = evaluate_resume_package(
        paths=paths,
        rollup=rollup_obj,
        locked_x2=json.loads(paths.locked_copy_x2_json.read_text(encoding="utf-8")),
        final_manifest=json.loads(paths.final_resume_manifest_json.read_text(encoding="utf-8")),
        final_x2=json.loads(paths.final_resume_x2_json.read_text(encoding="utf-8")),
        docx_manifest=json.loads(paths.docx_manifest_json.read_text(encoding="utf-8")),
        docx_manifest_x2=json.loads(paths.docx_manifest_x2_json.read_text(encoding="utf-8")),
        docx_render_manifest=json.loads(paths.docx_render_manifest_json.read_text(encoding="utf-8")),
        docx_render_x2=json.loads(paths.docx_render_x2_json.read_text(encoding="utf-8")),
    )
    assert dsp["deterministic_blocked"] is False
    assert dsp["final_x3_code"] == X3_REVIEW_SECTION
    assert dsp["explicit_waiver_needed_for_allow_when_section_review"] is True


def test_all_sections_allow_pkg_allow(tmp_path: Path):
    paths = _write_minimal_fixture_tree(tmp_path)
    rollup = json.loads(paths.rollup_json.read_text(encoding="utf-8"))
    dsp = evaluate_resume_package(
        paths=paths,
        rollup=rollup,
        locked_x2=json.loads(paths.locked_copy_x2_json.read_text(encoding="utf-8")),
        final_manifest=json.loads(paths.final_resume_manifest_json.read_text(encoding="utf-8")),
        final_x2=json.loads(paths.final_resume_x2_json.read_text(encoding="utf-8")),
        docx_manifest=json.loads(paths.docx_manifest_json.read_text(encoding="utf-8")),
        docx_manifest_x2=json.loads(paths.docx_manifest_x2_json.read_text(encoding="utf-8")),
        docx_render_manifest=json.loads(paths.docx_render_manifest_json.read_text(encoding="utf-8")),
        docx_render_x2=json.loads(paths.docx_render_x2_json.read_text(encoding="utf-8")),
    )
    assert dsp["deterministic_blocked"] is False
    assert dsp["final_x3_code"] == X3_ALLOW_CODE
    assert dsp["explicit_waiver_needed_for_allow_when_section_review"] is False


def test_emit_synthesized_tree_writes_three_contract_files(tmp_path: Path):
    paths = _write_minimal_fixture_tree(tmp_path)
    out = emit_resume_package_artifacts(paths=paths)
    assert paths.package_manifest_json().is_file()
    assert paths.package_x3_json().is_file()
    assert paths.package_receipt_json().is_file()
    assert out["resume_package_disposition"]["final_x3_code"] == X3_ALLOW_CODE


def test_current_workspace_expectation_review_when_not_allow():
    p = _workspace_package_paths_or_skip()
    d = json.loads(p.package_x3_json().read_text(encoding="utf-8"))
    if d["section_level_x3"]["all_generated_lane_x3_allow"] is False:
        if d["deterministic_blocked"]:
            assert d["final_x3_code"] == X3_BLOCKED_DETERMINISTIC
        else:
            assert d["final_x3_code"] == X3_REVIEW_SECTION
            assert d["deterministic_blocked"] is False


def test_package_module_has_no_foreign_network_providers():
    rf = Path(__file__).resolve().parents[2] / "apps_rg" / "runtime" / "internal" / "resume_package_disposition.py"
    src = rf.read_text(encoding="utf-8")
    banned = ("openai", "anthropic", "google.generativeai", "httpx.get", "requests.")
    for b in banned:
        assert b not in src.lower()


def test_metadata_flags_no_registry_v1_core():
    p = _workspace_package_paths_or_skip()
    m = json.loads(p.package_x3_json().read_text(encoding="utf-8"))["metadata_confirmation"]
    assert m["registry_changes_in_this_packaging_task"] is False
    assert m["v1_prompt_edits_in_this_packaging_task"] is False
    assert m["agentic_core_edits_in_this_packaging_task"] is False


def test_blocked_when_l6_packet_incomplete(tmp_path: Path):
    paths = _write_minimal_fixture_tree(tmp_path)
    rollup = json.loads(paths.rollup_json.read_text(encoding="utf-8"))
    hk = paths.repo_root / rollup["lanes"]["headline"]["artifact_refs"]["l6_shadow_eval_package.json"]
    broken = json.loads(hk.read_text(encoding="utf-8"))
    del broken["packet_type"]
    hk.write_text(json.dumps(broken), encoding="utf-8")
    dsp = evaluate_resume_package(
        paths=paths,
        rollup=rollup,
        locked_x2=json.loads(paths.locked_copy_x2_json.read_text(encoding="utf-8")),
        final_manifest=json.loads(paths.final_resume_manifest_json.read_text(encoding="utf-8")),
        final_x2=json.loads(paths.final_resume_x2_json.read_text(encoding="utf-8")),
        docx_manifest=json.loads(paths.docx_manifest_json.read_text(encoding="utf-8")),
        docx_manifest_x2=json.loads(paths.docx_manifest_x2_json.read_text(encoding="utf-8")),
        docx_render_manifest=json.loads(paths.docx_render_manifest_json.read_text(encoding="utf-8")),
        docx_render_x2=json.loads(paths.docx_render_x2_json.read_text(encoding="utf-8")),
    )
    assert dsp["final_x3_code"] == X3_BLOCK_L6_HANDOFF_INCOMPLETE
    assert dsp["l6_shadow_handoff_audit"]["l6_handoff_blocked"] is True


@pytest.mark.parametrize(
    ("field", "bad_value"),
    [
        ("promotion_allowed", True),
        ("learning_mutation_performed", True),
        ("runtime_approval_authority", "L6_ADMIN"),
        ("current_run_mutation_allowed", True),
    ],
)
def test_blocked_when_l6_safety_field_bad(tmp_path: Path, field: str, bad_value: object):
    paths = _write_minimal_fixture_tree(tmp_path)
    rollup = json.loads(paths.rollup_json.read_text(encoding="utf-8"))
    hk = paths.repo_root / rollup["lanes"]["executive_summary"]["artifact_refs"]["l6_shadow_eval_package.json"]
    p = json.loads(hk.read_text(encoding="utf-8"))
    p[field] = bad_value
    hk.write_text(json.dumps(p), encoding="utf-8")
    dsp = evaluate_resume_package(
        paths=paths,
        rollup=rollup,
        locked_x2=json.loads(paths.locked_copy_x2_json.read_text(encoding="utf-8")),
        final_manifest=json.loads(paths.final_resume_manifest_json.read_text(encoding="utf-8")),
        final_x2=json.loads(paths.final_resume_x2_json.read_text(encoding="utf-8")),
        docx_manifest=json.loads(paths.docx_manifest_json.read_text(encoding="utf-8")),
        docx_manifest_x2=json.loads(paths.docx_manifest_x2_json.read_text(encoding="utf-8")),
        docx_render_manifest=json.loads(paths.docx_render_manifest_json.read_text(encoding="utf-8")),
        docx_render_x2=json.loads(paths.docx_render_x2_json.read_text(encoding="utf-8")),
    )
    assert dsp["final_x3_code"] == X3_BLOCK_L6_HANDOFF_INCOMPLETE


def test_human_label_missing_not_fatal_via_lane_audit(tmp_path: Path):
    paths = _write_minimal_fixture_tree(tmp_path)
    rollup = json.loads(paths.rollup_json.read_text(encoding="utf-8"))
    lane_key = GENERATED_LANES[0]
    l6_rel = rollup["lanes"][lane_key]["artifact_refs"]["l6_shadow_eval_package.json"]
    pkt = json.loads((paths.repo_root / l6_rel).read_text(encoding="utf-8"))
    pkt["human_label_status"] = "MISSING"
    assert pkt["human_label_required"] is True

    rec = audit_l6_shadow_packet_for_lane(lane_key=lane_key, packet=pkt)
    assert rec["checks"]["x3_l6_human_label_status_valid"] is True
    assert rec["fatal"] is False


def test_package_manifest_extras_cover_all_lanes(tmp_path: Path):
    paths = _write_minimal_fixture_tree(tmp_path)
    manifest = emit_resume_package_artifacts(paths=paths)["resume_package_manifest"]
    refs = (manifest.get("extras") or {}).get("lane_l6_shadow_eval_package_refs") or {}
    assert set(refs) == set(GENERATED_LANES)
    assert all(isinstance(refs[k], str) and refs[k] for k in GENERATED_LANES)


def test_package_disposition_includes_nonempty_l6_ref_per_lane(tmp_path: Path):
    paths = _write_minimal_fixture_tree(tmp_path)
    rollup = json.loads(paths.rollup_json.read_text(encoding="utf-8"))
    dsp = evaluate_resume_package(
        paths=paths,
        rollup=rollup,
        locked_x2=json.loads(paths.locked_copy_x2_json.read_text(encoding="utf-8")),
        final_manifest=json.loads(paths.final_resume_manifest_json.read_text(encoding="utf-8")),
        final_x2=json.loads(paths.final_resume_x2_json.read_text(encoding="utf-8")),
        docx_manifest=json.loads(paths.docx_manifest_json.read_text(encoding="utf-8")),
        docx_manifest_x2=json.loads(paths.docx_manifest_x2_json.read_text(encoding="utf-8")),
        docx_render_manifest=json.loads(paths.docx_render_manifest_json.read_text(encoding="utf-8")),
        docx_render_x2=json.loads(paths.docx_render_x2_json.read_text(encoding="utf-8")),
    )
    per = dsp["l6_shadow_handoff_audit"]["per_lane"]
    for lk in GENERATED_LANES:
        assert per[lk]["l6_shadow_eval_ref_repo_relative"]


def test_non_generation_guarantees_false():
    p = _workspace_package_paths_or_skip()
    g = json.loads(p.package_x3_json().read_text(encoding="utf-8"))["non_generation_stage_guarantees"]
    assert g["provider_calls_made"] is False
    assert g["retired_provider_calls_made"] is False
    assert g["judge_calls_made"] is False
