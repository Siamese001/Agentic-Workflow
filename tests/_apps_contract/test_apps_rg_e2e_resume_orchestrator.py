"""Contract tests for `apps_rg.runtime.orchestrate_full_resume` (step order + JSON shape).

Full real-LLM E2E is exercised manually via the module CLI; these tests stub subprocess + package emit.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest import mock

import pytest

from apps_rg.runtime import orchestrate_full_resume as ofr
from apps_rg.runtime.locked_copy.locked_copy_manifest import sha256_hex


REPO_ROOT = Path(__file__).resolve().parents[2]


class _FakeProc:
    __slots__ = ("returncode", "stdout", "stderr")

    def __init__(self, *, code: int = 0, out: str = "", err: str = "") -> None:
        self.returncode = code
        self.stdout = out
        self.stderr = err


def _lane_tail(mod: str) -> str:
    tail = mod.rsplit(".", 1)[-1]
    if tail.endswith("_lane"):
        return tail[: -len("_lane")]
    return tail.replace("_dispatch", "")


def _stub_canonical_base_resume(repo: Path, *, text: str) -> Path:
    p = repo / "apps_rg" / "resume" / "base"
    p.mkdir(parents=True, exist_ok=True)
    out = p / "amit_ayer_base_resume_v1.json"
    out.write_text(text, encoding="utf-8")
    return out


def test_lane_modules_canonical_sequence() -> None:
    tails = [_lane_tail(m) for m in ofr.LANE_MODULES]
    assert tails == [
        "headline",
        "executive_summary",
        "unify_bullets",
        "unify_narrative",
        "ibm_bullets",
        "ibm_narrative",
        "competencies",
    ]


def _canonical_success_stub() -> dict[str, Any]:
    return {
        "exit_status": "success",
        "execution_status": "completed",
        "outcome_authorized": True,
        "x3_disposition": "X3_ALLOW",
        "fault": "",
        "error": "",
        "artifact_dir": "",
        "run_id": "",
        "request_id": "",
        "l7_how_trace_emitted": False,
        "terminal_r5": False,
        "executive_summary_cli_output_text": "",
        "headline_cli_output_text": "",
        "unify_bullets_cli_output_text": "",
        "unify_narrative_cli_output_text": "",
        "ibm_bullets_cli_output_text": "",
        "ibm_narrative_cli_output_text": "",
        "competencies_cli_output_text": "",
    }


def test_run_orchestration_step_order_without_real_providers(tmp_path: Path) -> None:
    repo = tmp_path.resolve()
    canon_text = '{"orchestrator_test_stub":true}\n'
    _stub_canonical_base_resume(repo, text=canon_text)

    rollup_dir = repo / "artifacts" / "apps_rg" / "runtime_proofs" / "generated_lane_rollup"
    rollup_dir.mkdir(parents=True, exist_ok=True)
    rollup_blob = {"rollup_id": "test-rollup", "lanes": {}}
    (rollup_dir / "generated_lane_rollup.json").write_text(json.dumps(rollup_blob), encoding="utf-8")

    fr_dir = repo / "artifacts" / "apps_rg" / "runtime_proofs" / "final_resume_assembly"
    fr_dir.mkdir(parents=True)
    fr_x2 = {
        "gate_family": "final_resume_assembly_x2",
        "all_pass": True,
        "failed_gate_ids": [],
        "gates": [],
    }
    (fr_dir / "final_resume_x2_gate_outputs.json").write_text(json.dumps(fr_x2), encoding="utf-8")

    recorded: list[list[str]] = []
    canonical_calls: list[dict[str, Any]] = []

    def fake_canonical(**kwargs: Any) -> dict[str, Any]:
        canonical_calls.append(kwargs)
        return _canonical_success_stub()

    def fake_run(argv, cwd=None, **_kwargs):  # type: ignore[no-untyped-def]
        recorded.append(list(argv))
        return _FakeProc()

    disposition = {
        "final_x3_code": "X3_ALLOW",
        "deterministic_blocked": False,
        "deterministic_proof_summary": {"l6_handoff_agg_checks_all_true": True},
        "l6_shadow_handoff_audit": {"l6_handoff_blocked": False, "aggregate_checks": {}},
        "section_level_x3": {"lanes_detail": [], "rollup_x3_non_allow": []},
        "non_generation_stage_guarantees": {
            "provider_calls_made": False,
            "qwen_calls_made": False,
            "judge_calls_made": False,
        },
        "explicit_waiver_needed_for_allow_when_section_review": False,
    }

    with (
        mock.patch("subprocess.run", side_effect=fake_run),
        mock.patch(
            "apps_rg.runtime.orchestrate_full_resume.run_canonical_apps_rg_from_cli_primitives",
            side_effect=fake_canonical,
        ),
        mock.patch(
            "apps_rg.runtime.orchestrate_full_resume._run_docx_emit",
            return_value={
                "manifest": {"gates_all_pass": True, "failed_gate_ids": []},
                "render": {"gates_all_pass": True, "failed_gate_ids": []},
            },
        ),
        mock.patch(
            "apps_rg.runtime.package.resume_package_x3.emit_resume_package_artifacts",
            return_value={
                "resume_package_disposition": disposition,
                "resume_package_manifest_path": repo / "manifest.json",
                "resume_package_x3_disposition_path": repo / "x3.json",
            },
        ),
    ):
        out = ofr.run_orchestration(
            repo=repo,
            provider="qwen_vllm",
            x1d_judges="gemini_pro",
            allow_non_allow_exit_zero=False,
            mock_judges=True,
            allow_test_mock_judges=True,
            jd_text=None,
            briefing=None,
            base_resume=None,
            output_docx=None,
        )

    assert [c.get("section") for c in canonical_calls] == list(ofr.SECTION_ORDER)
    assert all(c.get("lane_mock_judges") for c in canonical_calls)
    assert all(c.get("lane_allow_test_mock_judges") for c in canonical_calls)

    rollup_hit = locked_hit = assembler_hit = False
    for av in recorded:
        if "-m" in av:
            i = av.index("-m")
            mod = av[i + 1]
            if mod == "apps_rg.runtime.reports.generated_lane_rollup":
                rollup_hit = True
            elif mod == "apps_rg.runtime.locked_copy.locked_copy_builder":
                locked_hit = True
            elif mod == "apps_rg.runtime.assembly.final_resume_assembler":
                assembler_hit = True

    assert rollup_hit and locked_hit and assembler_hit
    assert out["orchestrator_status"] == "PASS"
    assert out["package_x3_code"] == "X3_ALLOW"
    assert "paths" in out and out["paths"]["final_docx"].endswith("amit_ayer_resume_v1.docx")
    assert out["final_resume_assembly_result"]["all_pass"] is True
    assert out["docx_manifest_result"]["gates_all_pass"] is True
    assert out["docx_render_result"]["gates_all_pass"] is True
    assert out["l6_handoff_summary"]["generated_lane_l6_artifact_audit"] == {}
    assert out["base_resume_default_used"] is True
    assert out["base_resume_path"] == ofr.CANONICAL_BASE_RESUME_REPO_REL.as_posix()
    assert out["base_resume_exists"] is True
    assert out["base_resume_hash"] == sha256_hex(canon_text)
    assert len(out["base_resume_hash"]) == 64


def test_override_base_resume_used_when_provided(tmp_path: Path) -> None:
    repo = tmp_path.resolve()
    canon = '{"canonical":true}\n'
    _stub_canonical_base_resume(repo, text=canon)
    alt_rel = Path("apps_rg/resume/base/alt_resume_for_orchestrator_test.json")
    alt_abs = repo / alt_rel
    alt_abs.parent.mkdir(parents=True, exist_ok=True)
    alt_txt = "{\"override\":42}\n"
    alt_abs.write_text(alt_txt, encoding="utf-8")

    rollup_dir = repo / "artifacts" / "apps_rg" / "runtime_proofs" / "generated_lane_rollup"
    rollup_dir.mkdir(parents=True, exist_ok=True)
    (rollup_dir / "generated_lane_rollup.json").write_text(json.dumps({"rollup_id": "t", "lanes": {}}), encoding="utf-8")

    fr_dir = repo / "artifacts" / "apps_rg" / "runtime_proofs" / "final_resume_assembly"
    fr_dir.mkdir(parents=True)
    (fr_dir / "final_resume_x2_gate_outputs.json").write_text(
        json.dumps({"all_pass": True, "failed_gate_ids": [], "gates": []}),
        encoding="utf-8",
    )

    disposition = {
        "final_x3_code": "X3_ALLOW",
        "deterministic_blocked": False,
        "deterministic_proof_summary": {"l6_handoff_agg_checks_all_true": True},
        "l6_shadow_handoff_audit": {},
        "section_level_x3": {"lanes_detail": [], "rollup_x3_non_allow": []},
        "non_generation_stage_guarantees": {
            "provider_calls_made": False,
            "qwen_calls_made": False,
            "judge_calls_made": False,
        },
        "explicit_waiver_needed_for_allow_when_section_review": False,
    }

    with (
        mock.patch("subprocess.run", return_value=_FakeProc()),
        mock.patch(
            "apps_rg.runtime.orchestrate_full_resume.run_canonical_apps_rg_from_cli_primitives",
            return_value=_canonical_success_stub(),
        ),
        mock.patch(
            "apps_rg.runtime.orchestrate_full_resume._run_docx_emit",
            return_value={
                "manifest": {"gates_all_pass": True, "failed_gate_ids": []},
                "render": {"gates_all_pass": True, "failed_gate_ids": []},
            },
        ),
        mock.patch(
            "apps_rg.runtime.package.resume_package_x3.emit_resume_package_artifacts",
            return_value={
                "resume_package_disposition": disposition,
                "resume_package_manifest_path": repo / "manifest.json",
                "resume_package_x3_disposition_path": repo / "x3.json",
            },
        ),
    ):
        out = ofr.run_orchestration(
            repo=repo,
            provider="qwen_vllm",
            x1d_judges="gemini_pro",
            allow_non_allow_exit_zero=False,
            mock_judges=True,
            allow_test_mock_judges=True,
            jd_text=None,
            briefing=None,
            base_resume=alt_rel,
            output_docx=None,
        )

    assert out["base_resume_default_used"] is False
    assert out["base_resume_path"] == alt_rel.as_posix()
    assert out["base_resume_hash"] == sha256_hex(alt_txt)


def test_orchestrator_rejects_unsupported_provider(tmp_path: Path) -> None:
    repo = tmp_path.resolve()
    canon_text = '{"stub":true}\n'
    _stub_canonical_base_resume(repo, text=canon_text)
    with pytest.raises(ValueError, match="Unsupported orchestrator"):
        ofr.run_orchestration(
            repo=repo,
            provider="mock",
            x1d_judges="gemini_pro",
            allow_non_allow_exit_zero=False,
            mock_judges=True,
            allow_test_mock_judges=False,
            jd_text=None,
            briefing=None,
            base_resume=None,
            output_docx=None,
        )


def test_orchestrator_rejects_mock_judges_without_allow_test_hatch(tmp_path: Path) -> None:
    repo = tmp_path.resolve()
    canon_text = '{"stub":true}\n'
    _stub_canonical_base_resume(repo, text=canon_text)
    with pytest.raises(ValueError, match="allow-test-mock-judges"):
        ofr.run_orchestration(
            repo=repo,
            provider="qwen_vllm",
            x1d_judges="gemini_pro",
            allow_non_allow_exit_zero=False,
            mock_judges=True,
            allow_test_mock_judges=False,
            jd_text=None,
            briefing=None,
            base_resume=None,
            output_docx=None,
        )


def test_missing_default_base_resume_fails_before_subprocess(tmp_path: Path) -> None:
    repo = tmp_path.resolve()
    (repo / "apps_rg" / "resume" / "base").mkdir(parents=True)

    with mock.patch("subprocess.run") as prun:
        with pytest.raises(ValueError, match="canonical default base resume"):
            ofr.run_orchestration(
                repo=repo,
                provider="qwen_vllm",
                x1d_judges="gemini_pro",
                allow_non_allow_exit_zero=False,
                mock_judges=True,
                allow_test_mock_judges=True,
                jd_text=None,
                briefing=None,
                base_resume=None,
                output_docx=None,
            )
        prun.assert_not_called()


def test_main_allow_non_allow_exit_zero_returns_zero_on_partial(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    partial = {
        "orchestrator_status": "PARTIAL",
        "package_x3_code": "X3_REVIEW_JUDGE_PROVIDER_BLOCKED",
        "paths": {"final_docx": "x"},
        "deterministic_gates_summary": {},
        "generated_lane_x2_and_x3_summary": {},
        "section_x3_summary": {},
        "l6_handoff_summary": {},
        "final_resume_assembly_result": {},
        "docx_manifest_result": {},
        "docx_render_result": {},
        "non_generation_calls": {},
    }
    monkeypatch.setattr(ofr, "run_orchestration", lambda **_: partial)
    monkeypatch.setattr(ofr, "find_repo_root", lambda: REPO_ROOT)
    code = ofr.main(
        [
            "--provider",
            "qwen_vllm",
            "--x1d-judges",
            "gemini_pro",
            "--mock-judges",
            "--allow-test-mock-judges",
            "--allow-non-allow-exit-zero",
        ],
    )
    assert code == 0


def test_main_fail_non_allow_partial_exit_code(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    partial = {
        "orchestrator_status": "PARTIAL",
        "package_x3_code": "X3_REVIEW_JUDGE_PROVIDER_BLOCKED",
        "paths": {},
        "deterministic_gates_summary": {},
        "generated_lane_x2_and_x3_summary": {},
        "section_x3_summary": {},
        "l6_handoff_summary": {},
        "final_resume_assembly_result": {},
        "docx_manifest_result": {},
        "docx_render_result": {},
        "non_generation_calls": {},
    }
    monkeypatch.setattr(ofr, "run_orchestration", lambda **_: partial)
    monkeypatch.setattr(ofr, "find_repo_root", lambda: REPO_ROOT)
    code = ofr.main(
        ["--provider", "qwen_vllm", "--x1d-judges", "gemini_pro", "--mock-judges", "--allow-test-mock-judges"]
    )
    assert code == 2
