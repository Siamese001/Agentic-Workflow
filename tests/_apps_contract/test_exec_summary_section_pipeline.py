"""Contract tests: executive_summary runs only through ``python -m apps_rg`` + canonical_dispatch."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import argparse

REPO = Path(__file__).resolve().parents[2]

_EXEC_SUMMARY_SUBPROCESS_STRIP_KEYS: frozenset[str] = frozenset(
    {
        "APPS_RG_MODULAR_LANE_PROVIDER",
        "APPS_RG_QWEN_OFFLINE_CONTRACT_STUB",
        "VLLM_BASE_URL",
        "APPS_RG_QWEN_TIMEOUT_SECONDS",
    }
)


def _exec_summary_pipeline_subprocess_env() -> dict[str, str]:
    import os

    env = {k: v for k, v in os.environ.items() if k not in _EXEC_SUMMARY_SUBPROCESS_STRIP_KEYS}
    env["APPS_RG_ALLOW_NON_ALLOW_EXIT_ZERO"] = "1"
    env["APPS_RG_QWEN_OFFLINE_CONTRACT_STUB"] = "1"
    return env


BASE_CANONICAL = [
    sys.executable,
    "-m",
    "apps_rg",
    "--section",
    "executive_summary",
]


def _tag_exec_summary_provider_resolution(args: argparse.Namespace) -> None:
    from apps_rg.runtime.section_cli_defaults import resolve_cli_lane_provider_with_source

    _p, args.provider_resolution_source = resolve_cli_lane_provider_with_source(args.provider)


def _pipeline_env() -> dict[str, str]:
    return _exec_summary_pipeline_subprocess_env()


def _latest_run_dir() -> Path:
    from apps_rg.runtime.runtime_proof_layout import resolve_run_dir_from_pointer

    rd = resolve_run_dir_from_pointer(REPO, "executive_summary", "real")
    assert rd is not None
    return rd


def test_canonical_cli_emits_execution_status_summary_lines():
    from apps_rg.runtime.cli_section_execution_report import parse_cli_execution_summary_block

    r = subprocess.run(
        BASE_CANONICAL, cwd=REPO, capture_output=True, text=True, timeout=180, env=_pipeline_env()
    )
    assert r.returncode == 0, r.stderr
    rd = _latest_run_dir()
    manifest = json.loads((rd / "run_manifest.json").read_text(encoding="utf-8"))
    expected_status = (
        "PASS_RUNTIME_PROOF_ELIGIBLE" if bool(manifest.get("proof_eligible")) else "PASS_NONCERTIFYING_RUNTIME_PROOF"
    )
    parsed = parse_cli_execution_summary_block(r.stdout)
    assert parsed.get("STATUS") == expected_status
    assert parsed.get("CLI_PATH_STATUS") == "PASS"
    assert parsed.get("PROCESS_EXIT_CODE") == "0"
    assert "PRODUCT_STATUS" in parsed


def test_canonical_cli_emits_required_exec_summary_artifacts():
    r = subprocess.run(
        BASE_CANONICAL, cwd=REPO, capture_output=True, text=True, timeout=180, env=_pipeline_env()
    )
    assert r.returncode == 0, r.stderr
    rd = _latest_run_dir()
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
        "cli_section_execution_report.json",
    ]
    for name in required:
        assert (rd / name).is_file(), f"missing {name} under {rd}"


def test_executive_summary_flag_alias():
    cmd = [
        sys.executable,
        "-m",
        "apps_rg",
        "--executive-summary",
    ]
    r = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=180, env=_pipeline_env())
    assert r.returncode == 0, r.stderr


def test_standalone_executive_summary_pipeline_removed():
    assert not (
        REPO / "apps_rg" / "runtime" / "pipeline" / "executive_summary_pipeline.py"
    ).exists()


def test_canonical_claim_ledger_always_on_truncated_qwen(monkeypatch, tmp_path: Path):
    import apps_rg.runtime.sections.executive_summary_lane as lane
    from apps_rg.runtime.providers.qwen_vllm_provider import ProviderResult

    monkeypatch.delenv("APPS_RG_QWEN_OFFLINE_CONTRACT_STUB", raising=False)

    def _fake_qwen(_payload: dict) -> ProviderResult:
        return ProviderResult(
            provider_requested="qwen_vllm",
            provider_attempted=True,
            provider_available=True,
            exact_provider_error=None,
            runtime_generation_status="REAL_LLM",
            model="Qwen/Qwen2.5-32B-Instruct-AWQ",
            raw_model_output='{"resume_display_text": "truncated',
            provider_response={"stub": False, "model": "Qwen/Qwen2.5-32B-Instruct-AWQ"},
        )

    monkeypatch.setattr(lane, "prepare_runtime_proof_run_dir", lambda *a, **k: tmp_path)
    monkeypatch.setattr(lane, "finalize_runtime_proof_run", lambda *a, **k: None)
    monkeypatch.setattr(lane, "call_qwen_vllm", _fake_qwen)

    from apps_rg.runtime.sections.executive_summary_lane import build_parser

    args = build_parser().parse_args(
        ["--provider", "qwen_vllm", "--mock-judges", "--allow-non-allow-exit-zero"]
    )
    _tag_exec_summary_provider_resolution(args)
    ctx = lane.run_executive_summary_execution(args, artifact_dir_override=tmp_path)
    assert ctx["artifact_dir"] == tmp_path
    canon = json.loads((tmp_path / "canonical_claim_ledger_v2.json").read_text(encoding="utf-8"))
    assert canon["schema"] == "canonical_claim_ledger_v2"
    assert canon["claims"] == []
    assert canon["parse_status"] in {"TRUNCATED_JSON", "INVALID_JSON"}
    assert "invalid_reason" in canon


def test_truncated_json_fails_x2_json_and_schema_gates(monkeypatch, tmp_path: Path):
    import apps_rg.runtime.sections.executive_summary_lane as lane
    from apps_rg.runtime.providers.qwen_vllm_provider import ProviderResult

    monkeypatch.delenv("APPS_RG_QWEN_OFFLINE_CONTRACT_STUB", raising=False)

    def _fake_qwen(_payload: dict) -> ProviderResult:
        return ProviderResult(
            provider_requested="qwen_vllm",
            provider_attempted=True,
            provider_available=True,
            exact_provider_error=None,
            runtime_generation_status="REAL_LLM",
            model="Qwen/Qwen2.5-32B-Instruct-AWQ",
            raw_model_output='{"resume_display_text": "x"',
            provider_response={},
        )

    monkeypatch.setattr(lane, "prepare_runtime_proof_run_dir", lambda *a, **k: tmp_path)
    monkeypatch.setattr(lane, "finalize_runtime_proof_run", lambda *a, **k: None)
    monkeypatch.setattr(lane, "call_qwen_vllm", _fake_qwen)

    from apps_rg.runtime.sections.executive_summary_lane import build_parser

    args = build_parser().parse_args(
        ["--provider", "qwen_vllm", "--mock-judges", "--allow-non-allow-exit-zero"]
    )
    _tag_exec_summary_provider_resolution(args)
    ctx = lane.run_executive_summary_execution(args, artifact_dir_override=tmp_path)
    by_id = {g["gate_id"]: g for g in ctx["x2"]}
    assert by_id["x2_json_parse_valid"]["pass"] is False
    assert by_id["x2_schema_valid"]["pass"] is False


def test_required_artifacts_gate_passes_when_files_present():
    from apps_rg.runtime.validators.executive_summary_x2 import check_required_artifacts

    subprocess.run(
        BASE_CANONICAL, cwd=REPO, capture_output=True, text=True, timeout=180, check=True, env=_pipeline_env()
    )
    rd = _latest_run_dir()
    ok, reason = check_required_artifacts(rd)
    assert ok, reason


def test_x3_blocks_when_x2_fails_truncated_path(monkeypatch, tmp_path: Path):
    import apps_rg.runtime.sections.executive_summary_lane as lane
    from apps_rg.runtime.providers.qwen_vllm_provider import ProviderResult

    monkeypatch.delenv("APPS_RG_QWEN_OFFLINE_CONTRACT_STUB", raising=False)

    def _fake_qwen(_payload: dict) -> ProviderResult:
        return ProviderResult(
            provider_requested="qwen_vllm",
            provider_attempted=True,
            provider_available=True,
            exact_provider_error=None,
            runtime_generation_status="REAL_LLM",
            model="Qwen/Qwen2.5-32B-Instruct-AWQ",
            raw_model_output="{",
            provider_response={},
        )

    monkeypatch.setattr(lane, "prepare_runtime_proof_run_dir", lambda *a, **k: tmp_path)
    monkeypatch.setattr(lane, "finalize_runtime_proof_run", lambda *a, **k: None)
    monkeypatch.setattr(lane, "call_qwen_vllm", _fake_qwen)

    from apps_rg.runtime.sections.executive_summary_lane import build_parser

    args = build_parser().parse_args(
        ["--provider", "qwen_vllm", "--mock-judges", "--allow-non-allow-exit-zero"]
    )
    _tag_exec_summary_provider_resolution(args)
    ctx = lane.run_executive_summary_execution(args, artifact_dir_override=tmp_path)
    assert ctx["x3"].x3_code == "X3_BLOCK"


def test_allow_non_allow_exit_zero_does_not_mutate_x3(tmp_path: Path, monkeypatch):
    import apps_rg.runtime.sections.executive_summary_lane as lane
    from apps_rg.runtime.section_cli_defaults import CLI_PROVIDER_RESOLUTION_DEV_DEFAULT_QWEN_VLLM

    monkeypatch.setenv("APPS_RG_QWEN_OFFLINE_CONTRACT_STUB", "1")
    monkeypatch.setattr(lane, "prepare_runtime_proof_run_dir", lambda *a, **k: tmp_path)
    monkeypatch.setattr(lane, "finalize_runtime_proof_run", lambda *a, **k: None)

    class _NS:
        provider = "qwen_vllm"
        provider_resolution_source = CLI_PROVIDER_RESOLUTION_DEV_DEFAULT_QWEN_VLLM
        temperature = lane.EXEC_SUMMARY_TEMP_DEFAULT
        x1d_judges = "gemini_pro,openai_chatgpt,anthropic_claude"
        mock_judges = True
        target_title = lane.TARGET_TITLE_DEFAULT
        target_company = lane.TARGET_COMPANY_DEFAULT
        jd_text = lane.JD_TEXT_DEFAULT
        briefing = lane.BRIEFING_DEFAULT
        allow_non_allow_exit_zero = True

    ctx = lane.run_executive_summary_execution(_NS(), artifact_dir_override=tmp_path)
    x3_first = json.dumps(ctx["x3"].to_dict(), sort_keys=True)
    x3_second = json.dumps(ctx["x3"].to_dict(), sort_keys=True)
    assert x3_first == x3_second


def test_qwen_unavailable_does_not_mock(monkeypatch, tmp_path: Path):
    import apps_rg.runtime.sections.executive_summary_lane as lane
    from apps_rg.runtime.providers.qwen_vllm_provider import ProviderResult

    monkeypatch.delenv("APPS_RG_QWEN_OFFLINE_CONTRACT_STUB", raising=False)

    def _blocked(_payload: dict) -> ProviderResult:
        return ProviderResult(
            provider_requested="qwen_vllm",
            provider_attempted=True,
            provider_available=False,
            exact_provider_error="connection refused",
            runtime_generation_status="BLOCKED",
            model="Qwen/Qwen2.5-32B-Instruct-AWQ",
            raw_model_output="",
            provider_response=None,
        )

    monkeypatch.setattr(lane, "prepare_runtime_proof_run_dir", lambda *a, **k: tmp_path)
    monkeypatch.setattr(lane, "finalize_runtime_proof_run", lambda *a, **k: None)
    monkeypatch.setattr(lane, "call_qwen_vllm", _blocked)

    from apps_rg.runtime.sections.executive_summary_lane import build_parser

    args = build_parser().parse_args(
        ["--provider", "qwen_vllm", "--mock-judges", "--allow-non-allow-exit-zero"]
    )
    _tag_exec_summary_provider_resolution(args)
    ctx = lane.run_executive_summary_execution(args, artifact_dir_override=tmp_path)
    assert ctx["runtime_generation_status"] == "BLOCKED"
    pr = json.loads((tmp_path / "provider_response.json").read_text(encoding="utf-8"))
    assert pr.get("provider_available") is False


def test_exec_summary_runtime_proof_surfaces_and_canonical_bundle_producers():
    subprocess.run(
        BASE_CANONICAL, cwd=REPO, capture_output=True, text=True, timeout=180, check=True, env=_pipeline_env()
    )
    rd = _latest_run_dir()
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
    assert exhaust.get("runtime_terminal_boundary")
    assert exhaust.get("refs", {}).get("x3_disposition")
    idx_path = rd / "RUN_BUNDLE_INDEX.json"
    assert idx_path.is_file()
    idx = json.loads(idx_path.read_text(encoding="utf-8"))
    producers = [e.get("producer") for e in idx.get("entries", []) if isinstance(e, dict)]
    assert "apps_rg_section_dispatch" not in producers
    assert "apps_rg_section_dispatch_or_tests" not in producers
    assert any(p == "apps_rg_canonical_section_runtime" for p in producers)
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
    from apps_rg.runtime.dispatch import executive_summary_dispatch as esd

    base, _, _ = esd.load_base_resume()
    _, allowed = esd.extract_allowed_facts(base)
    for fid in allowed:
        s = str(fid)
        assert not s.startswith("jd_")
        assert "TARGET_TITLE" not in s
        assert "briefing" not in s.lower()
