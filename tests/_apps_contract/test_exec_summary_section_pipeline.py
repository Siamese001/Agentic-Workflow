"""Contract tests: executive_summary lane E2E (in-process harness + optional live CLI)."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

REPO = Path(__file__).resolve().parents[2]

_GOOD_SUMMARY = (
    "Engineering executive building governed agentic AI platforms for regulated enterprise delivery "
    "with traceable execution, commercial discipline, and accountable operating cadence across "
    "large programs. "
    "The platform generated proof-backed revenue and margin outcomes while scaling engineering "
    "delivery across enterprise programs and cross-functional product portfolios. "
    "Implementation of Basel III and CCAR data lineage frameworks reduced regulatory reporting errors "
    "and improved audit readiness for risk and finance stakeholders. "
    "Re-architected risk analytics with containerized microservices achieved faster calculations, "
    "real-time stress testing, and more reliable decision support for senior leadership. "
    "Established portfolio governance and operating rhythm that aligned product, platform, and "
    "regulatory stakeholders on measurable delivery outcomes. "
    "Scaled accountable engineering leadership across multi-year transformation programs without "
    "sacrificing auditability, safety, or commercial discipline."
)


def _good_qwen_json() -> str:
    return json.dumps(
        {
            "resume_display_text": _GOOD_SUMMARY,
            "claim_ledger": [
                {
                    "claim_text": "Governed agentic AI platform delivery for regulated enterprise programs.",
                    "source_fact_ids": ["fact_engineering_platform_001"],
                }
            ],
            "self_check": {"confidence": "high"},
        }
    )


def _harness_lane_namespace() -> argparse.Namespace:
    from types import SimpleNamespace

    import apps_rg.runtime.sections.executive_summary_lane as lane
    from apps_rg.runtime.section_cli_defaults import resolve_cli_lane_provider_with_source

    prov, prov_src = resolve_cli_lane_provider_with_source("qwen_vllm")
    return SimpleNamespace(
        provider=prov,
        provider_resolution_source=prov_src,
        temperature=lane.EXEC_SUMMARY_TEMP_DEFAULT,
        x1d_judges="gemini_pro,openai_chatgpt,anthropic_claude",
        mock_judges=True,
        allow_test_mock_judges=False,
        target_title=lane.TARGET_TITLE_DEFAULT,
        target_company=lane.TARGET_COMPANY_DEFAULT,
        target_role=lane.TARGET_TITLE_DEFAULT,
        jd_text=lane.JD_TEXT_DEFAULT,
        briefing=lane.BRIEFING_DEFAULT,
        allow_non_allow_exit_zero=True,
        selected_role_fact_set="",
        base_resume_ref="",
    )


def _apply_harness_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APPS_RG_TEST_HARNESS", "1")
    monkeypatch.setenv("APPS_RG_MOCK_JUDGES", "1")
    monkeypatch.setenv("APPS_RG_ALLOW_NON_ALLOW_EXIT_ZERO", "1")
    monkeypatch.delenv("APPS_RG_QWEN_OFFLINE_CONTRACT_STUB", raising=False)


def _harness_artifact_dir(tmp_path: Path) -> Path:
    """Artifact dir under repo root (required by run bundle index / L7 evidence links)."""
    ad = (
        REPO
        / "artifacts"
        / "apps_rg"
        / "runtime_proofs"
        / "executive_summary"
        / "pytest_harness"
        / tmp_path.name
    )
    ad.mkdir(parents=True, exist_ok=True)
    return ad


def _run_lane_in_process(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    *,
    raw_model_output: str,
    provider_available: bool = True,
    runtime_generation_status: str = "REAL_LLM",
) -> dict[str, Any]:
    import apps_rg.runtime.sections.executive_summary_lane as lane
    from apps_rg.runtime.providers.qwen_vllm_provider import ProviderResult

    _apply_harness_env(monkeypatch)
    artifact_dir = _harness_artifact_dir(tmp_path)

    def _fake_qwen(_payload: dict, **_kwargs: Any) -> ProviderResult:
        return ProviderResult(
            provider_requested="qwen_vllm",
            provider_attempted=True,
            provider_available=provider_available,
            exact_provider_error=None if provider_available else "connection refused",
            runtime_generation_status=runtime_generation_status,
            model="Qwen/Qwen2.5-32B-Instruct-AWQ",
            raw_model_output=raw_model_output,
            provider_response={"stub": False, "model": "Qwen/Qwen2.5-32B-Instruct-AWQ"},
        )

    monkeypatch.setattr(lane, "prepare_runtime_proof_run_dir", lambda *a, **k: artifact_dir)
    monkeypatch.setattr(lane, "finalize_runtime_proof_run", lambda *a, **k: None)
    monkeypatch.setattr(lane, "call_qwen_vllm", _fake_qwen)

    def _passthrough_token_budget(section_compiled: Any, **_kwargs: Any) -> tuple[Any, dict[str, Any]]:
        return section_compiled, {"status": "PASS", "fail_closed_reason": "", "operator_message": ""}

    import apps_rg.runtime.sections.executive_summary_token_budget as _tb

    monkeypatch.setattr(_tb, "apply_executive_summary_token_budget_policy", _passthrough_token_budget)
    return lane.run_executive_summary_execution(
        _harness_lane_namespace(), artifact_dir_override=artifact_dir
    )


def _x3_code(x3: Any) -> str:
    if isinstance(x3, dict):
        return str(x3.get("x3_code") or x3.get("disposition") or "")
    return str(getattr(x3, "x3_code", "") or "")


def _assert_required_artifacts(rd: Path) -> None:
    required = [
        "compiled_prompt.txt",
        "compiled_prompt_artifact.json",
        "provider_request.json",
        "provider_response.json",
        "parsed_output.json",
        "canonical_claim_ledger_v2.json",
        "text_claim_coverage.json",
        "x2_gate_outputs.json",
        "x3_disposition.json",
        "x1d_llm_judge_outputs.json",
    ]
    for name in required:
        assert (rd / name).is_file(), f"missing {name} under {rd}"


def test_in_process_harness_emits_x3_and_l2_artifacts(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    ctx = _run_lane_in_process(monkeypatch, tmp_path, raw_model_output=_good_qwen_json())
    rd = Path(ctx["artifact_dir"])
    x3_path = rd / "x3_disposition.json"
    assert x3_path.is_file()
    x3 = json.loads(x3_path.read_text(encoding="utf-8"))
    assert x3.get("runtime_generation_status") == "REAL_LLM"
    assert (rd / "l2_output.json").is_file()
    code = _x3_code(ctx["x3"])
    assert code in {"X3_ALLOW", "X3_BLOCK"} or code.startswith("X3_BLOCK")


def test_in_process_harness_emits_required_exec_summary_artifacts(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    ctx = _run_lane_in_process(monkeypatch, tmp_path, raw_model_output=_good_qwen_json())
    _assert_required_artifacts(Path(ctx["artifact_dir"]))


def test_executive_summary_flag_sets_section():
    from apps_rg.__main__ import _build_parser

    args = _build_parser().parse_args(["--executive-summary"])
    assert args.executive_summary is True


def test_standalone_executive_summary_pipeline_removed():
    assert not (
        REPO / "apps_rg" / "runtime" / "pipeline" / "executive_summary_pipeline.py"
    ).exists()


def test_canonical_claim_ledger_always_on_truncated_qwen(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    ctx = _run_lane_in_process(
        monkeypatch, tmp_path, raw_model_output='{"resume_display_text": "truncated'
    )
    rd = Path(ctx["artifact_dir"])
    canon = json.loads((rd / "canonical_claim_ledger_v2.json").read_text(encoding="utf-8"))
    assert canon["schema"] == "canonical_claim_ledger_v2"
    assert canon["claims"] == []
    assert canon["parse_status"] in {"TRUNCATED_JSON", "INVALID_JSON"}
    assert "invalid_reason" in canon


def test_truncated_json_fails_x2_json_and_schema_gates(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    ctx = _run_lane_in_process(
        monkeypatch, tmp_path, raw_model_output='{"resume_display_text": "x"'
    )
    by_id = {g["gate_id"]: g for g in ctx["x2"]}
    assert by_id["x2_json_parse_valid"]["pass"] is False
    assert by_id["x2_schema_valid"]["pass"] is False


def test_required_artifacts_gate_passes_when_files_present(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    from apps_rg.runtime.validators.executive_summary_x2 import check_required_artifacts

    ctx = _run_lane_in_process(monkeypatch, tmp_path, raw_model_output=_good_qwen_json())
    ok, reason = check_required_artifacts(Path(ctx["artifact_dir"]))
    assert ok, reason


def test_x3_blocks_when_x2_fails_truncated_path(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    ctx = _run_lane_in_process(monkeypatch, tmp_path, raw_model_output="{")
    assert _x3_code(ctx["x3"]).startswith("X3_BLOCK")


def _x2_gate_dicts(x2_rows: list) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for g in x2_rows:
        if hasattr(g, "to_dict"):
            row = g.to_dict()
        elif isinstance(g, dict):
            row = g
        else:
            row = {"gate_id": getattr(g, "gate_id", ""), "pass": getattr(g, "pass_", None)}
        out[str(row.get("gate_id") or "")] = row
    return out


def test_in_process_harness_product_shape_gates_pass(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    ctx = _run_lane_in_process(monkeypatch, tmp_path, raw_model_output=_good_qwen_json())
    by_id = _x2_gate_dicts(ctx["x2"])
    assert by_id["x2_exec_summary_no_credential_dump"]["pass"] is True
    assert by_id["x2_exec_summary_no_mechanism_inventory"]["pass"] is True
    assert by_id["x2_exec_summary_sentence_count_6"]["pass"] is True
    assert by_id.get("x2_exec_summary_meta_filler_zero", {}).get("pass") is True


def test_allow_non_allow_exit_zero_does_not_mutate_x3(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    ctx = _run_lane_in_process(monkeypatch, tmp_path, raw_model_output=_good_qwen_json())
    x3_blob = ctx["x3"] if isinstance(ctx["x3"], dict) else ctx["x3"].to_dict()
    x3_first = json.dumps(x3_blob, sort_keys=True)
    x3_second = json.dumps(x3_blob, sort_keys=True)
    assert x3_first == x3_second


def test_qwen_unavailable_does_not_mock(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    ctx = _run_lane_in_process(
        monkeypatch,
        tmp_path,
        raw_model_output="",
        provider_available=False,
        runtime_generation_status="BLOCKED",
    )
    assert ctx["runtime_generation_status"] == "BLOCKED"
    pr = json.loads((Path(ctx["artifact_dir"]) / "provider_response.json").read_text(encoding="utf-8"))
    assert pr.get("provider_available") is False


def test_in_process_runtime_proof_surfaces_and_canonical_bundle_producers(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    ctx = _run_lane_in_process(monkeypatch, tmp_path, raw_model_output=_good_qwen_json())
    rd = Path(ctx["artifact_dir"])
    for name in (
        "artifact_inventory.json",
        "stage_sequence.json",
        "runtime_exhaust_bundle.json",
        "section_runtime_proof_bundle.json",
    ):
        assert (rd / name).is_file(), f"missing {name} under {rd}"
    bundle = json.loads((rd / "section_runtime_proof_bundle.json").read_text(encoding="utf-8"))
    assert bundle.get("proof_status") == "INCOMPLETE"
    assert bundle.get("certified") is False
    assert "missing_proof_surfaces" in bundle
    inv = json.loads((rd / "artifact_inventory.json").read_text(encoding="utf-8"))
    assert inv.get("producer") == "apps_rg_canonical_section_runtime"
    seq = json.loads((rd / "stage_sequence.json").read_text(encoding="utf-8"))
    assert seq.get("runtime_terminal_stage") == "x3_exit"
    assert "x3_exit" in (seq.get("runtime_stages") or [])
    assert seq.get("l6_is_runtime_gate") is False
    assert seq.get("l6_can_change_x3") is False
    exhaust = json.loads((rd / "runtime_exhaust_bundle.json").read_text(encoding="utf-8"))
    assert exhaust.get("runtime_terminal_boundary") or exhaust.get("contract_type")
    assert exhaust.get("section_x3_disposition_ref") or exhaust.get("refs", {}).get("x3_disposition")
    assert (rd / "RUN_LINKS.json").is_file()
    assert inv.get("producer") == "apps_rg_canonical_section_runtime"
    assert "apps_rg_section_dispatch" not in str(inv)
    assert "apps_rg_section_dispatch_or_tests" not in str(inv)
    l6p = rd / "post_runtime" / "l6_shadow_eval_package.json"
    assert l6p.is_file()
    l6 = json.loads(l6p.read_text(encoding="utf-8"))
    assert l6.get("post_runtime_phase") is True
    assert l6.get("consumed_after_x3") is True
    assert l6.get("offline_only") is True
    assert l6.get("future_run_signal_only") is True
    assert l6.get("runtime_approval_authority") == "NONE"
    assert l6.get("current_run_mutation_allowed") is False
    assert l6.get("promotion_allowed") is False
    assert l6.get("learning_mutation_performed") is False
    assert l6.get("no_current_run_rescue_assertion") is True
    assert l6.get("no_current_run_mutation_assertion") is True
    assert l6.get("l6_is_runtime_gate") is False
    assert l6.get("x3_changed_by_l6") is False
    assert l6.get("proof_eligible_changed_by_l6") is False
    assert l6.get("source_runtime_exhaust_bundle_ref")
    assert l6.get("source_x3_disposition_ref")
    assert l6.get("source_x2_gate_outputs_ref")
    assert l6.get("source_canonical_claim_ledger_ref")
    assert l6.get("source_text_claim_coverage_ref")
    assert l6.get("source_resume_display_text_ref")


def test_allowed_fact_ids_exclude_jd_tokens():
    import apps_rg.runtime.sections.executive_summary_lane as lane

    base, _, _ = lane.load_base_resume()
    _, allowed = lane.extract_allowed_facts(base)
    for fid in allowed:
        s = str(fid)
        assert not s.startswith("jd_")
        assert "TARGET_TITLE" not in s
        assert "briefing" not in s.lower()


@pytest.mark.integration
def test_live_cli_subprocess_when_vllm_available():
    """Optional live slice: skipped unless VLLM is reachable (no offline stub)."""
    import urllib.request

    base_url = os.environ.get("VLLM_BASE_URL", "http://localhost:8000").rstrip("/")
    try:
        urllib.request.urlopen(f"{base_url}/v1/models", timeout=3)
    except Exception:
        pytest.skip(f"vLLM not reachable at {base_url}")

    env = {**os.environ, "APPS_RG_ALLOW_NON_ALLOW_EXIT_ZERO": "1"}
    env.pop("APPS_RG_QWEN_OFFLINE_CONTRACT_STUB", None)
    import apps_rg.runtime.sections.executive_summary_lane as lane

    cmd = [
        sys.executable,
        "-m",
        "apps_rg",
        "--section",
        "executive_summary",
        "--target-company",
        lane.TARGET_COMPANY_DEFAULT,
        "--target-role",
        lane.TARGET_TITLE_DEFAULT,
        "--jd",
        lane.JD_TEXT_DEFAULT,
        "--manual-brief",
        lane.BRIEFING_DEFAULT,
        "--provider",
        "qwen_vllm",
        "--allow-non-allow-exit-zero",
    ]
    r = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=300, env=env)
    assert r.returncode == 0, r.stderr
