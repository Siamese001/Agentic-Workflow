"""Narrow CLI proof: ``python -m apps_rg --section executive_summary`` uses canonical_dispatch, not product dispatch."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from apps_rg.runtime.cli_section_execution_report import (
    CLI_SECTION_EXECUTION_REPORT_FILE,
    build_section_cli_execution_report_lines,
    build_section_cli_execution_report_payload,
    parse_cli_execution_summary_block,
    persist_cli_section_execution_report,
)

from apps_rg.runtime.section_cli_defaults import (
    CLI_PROVIDER_RESOLUTION_DEV_DEFAULT_MOCK,
    CLI_PROVIDER_RESOLUTION_DEV_DEFAULT_QWEN_VLLM,
)

REPO = Path(__file__).resolve().parents[2]
_EXEC_SUMMARY_JD_FIXTURE = REPO / "tests" / "_fixtures" / "ci-probe-jd.txt"
_EXEC_SUMMARY_BRIEF_FIXTURE = REPO / "tests" / "_fixtures" / "ci-probe-briefing.txt"

# Deterministic provider trace: strip ambient modular provider; optional Qwen offline stub.
_EXEC_SUMMARY_SUBPROCESS_STRIP_KEYS: frozenset[str] = frozenset(
    {
        "APPS_RG_MODULAR_LANE_PROVIDER",
        "APPS_RG_QWEN_OFFLINE_CONTRACT_STUB",
        "VLLM_BASE_URL",
        "APPS_RG_QWEN_TIMEOUT_SECONDS",
    }
)


def _exec_summary_subprocess_env(
    *,
    allow_non_allow_exit_zero: bool,
    qwen_offline_contract_stub: bool,
) -> dict[str, str]:
    import os

    env = {k: v for k, v in os.environ.items() if k not in _EXEC_SUMMARY_SUBPROCESS_STRIP_KEYS}
    if allow_non_allow_exit_zero:
        env["APPS_RG_ALLOW_NON_ALLOW_EXIT_ZERO"] = "1"
    else:
        env.pop("APPS_RG_ALLOW_NON_ALLOW_EXIT_ZERO", None)
    if qwen_offline_contract_stub:
        env["APPS_RG_QWEN_OFFLINE_CONTRACT_STUB"] = "1"
    return env


def _latest_exec_summary_real_run_dir() -> Path:
    from apps_rg.runtime.runtime_proof_layout import resolve_run_dir_from_pointer

    rd = resolve_run_dir_from_pointer(REPO, "executive_summary", "real")
    assert rd is not None, "expected latest_real_run.json → executive_summary real bucket"
    return rd


_SECTION_ENV = _exec_summary_subprocess_env(
    allow_non_allow_exit_zero=True,
    qwen_offline_contract_stub=True,
)


def _assert_stdout_matches_persisted_report(rd: Path, stdout: str) -> dict[str, Any]:
    report_path = rd / CLI_SECTION_EXECUTION_REPORT_FILE
    assert report_path.is_file(), f"missing {report_path}"
    data = json.loads(report_path.read_text(encoding="utf-8"))
    parsed = parse_cli_execution_summary_block(stdout)

    def _expect_str(payload_value: Any) -> str:
        if isinstance(payload_value, bool):
            return str(payload_value).lower()
        if payload_value is None:
            return ""
        return str(payload_value)

    required_stdout = (
        "STATUS",
        "CLI_PATH_STATUS",
        "PRODUCT_STATUS",
        "PROCESS_EXIT_CODE",
    )
    for req in required_stdout:
        assert req in parsed, f"missing required stdout key {req!r}; have {sorted(parsed.keys())}"

    # stdout label RUNTIME_GENERATION_STATUS maps to payload key runtime_generation_status_report
    stdout_to_payload_key: dict[str, str] = {
        "RUNTIME_GENERATION_STATUS": "runtime_generation_status_report",
    }
    for upper_key, parsed_val in parsed.items():
        snake_key = stdout_to_payload_key.get(upper_key, upper_key.lower())
        if snake_key not in data:
            continue
        assert parsed_val == _expect_str(data[snake_key]), (
            f"mismatch field {upper_key}: stdout={parsed_val!r} json={data[snake_key]!r}"
        )

    mock_note_raw = data.get("mock_judge_accounting_note")
    if isinstance(mock_note_raw, str) and mock_note_raw.strip():
        assert parsed.get("MOCK_JUDGES_ACCOUNTING_NOTE") == mock_note_raw.strip()

    assert data["x3_disposition_ref"] == "x3_disposition.json"
    assert data["run_manifest_ref"] == "run_manifest.json"
    return data


def _cli_argv() -> list[str]:
    return [
        "--section",
        "executive_summary",
        "--target-company",
        "CI-Probe-Co",
        "--target-role",
        "Software Engineer",
        "--jd",
        str(_EXEC_SUMMARY_JD_FIXTURE),
        "--manual-brief",
        str(_EXEC_SUMMARY_BRIEF_FIXTURE),
    ]


def _subprocess_env() -> dict[str, str]:
    return dict(_SECTION_ENV)


def _subprocess_env_provider_unset() -> dict[str, str]:
    return _exec_summary_subprocess_env(
        allow_non_allow_exit_zero=True,
        qwen_offline_contract_stub=True,
    )


def test_executive_summary_cli_fails_on_stale_default_targeting_files() -> None:
    r = subprocess.run(
        [
            sys.executable,
            "-m",
            "apps_rg",
            "--section",
            "executive_summary",
            "--target-company",
            "Unify Consulting",
            "--target-role",
            "SVP Engineering",
            "--jd",
            str(REPO / "apps_rg" / "config" / "default_jd_targeting.txt"),
            "--manual-brief",
            str(REPO / "apps_rg" / "config" / "default_targeting_briefing.txt"),
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
        env=_subprocess_env(),
    )
    assert r.returncode == 2, (r.stdout, r.stderr)
    assert "not updated" in (r.stderr or "").lower()


def test_executive_summary_cli_fails_without_target_company() -> None:
    r = subprocess.run(
        [
            sys.executable,
            "-m",
            "apps_rg",
            "--section",
            "executive_summary",
            "--target-role",
            "VP Engineering",
            "--jd",
            str(_EXEC_SUMMARY_JD_FIXTURE),
            "--manual-brief",
            str(_EXEC_SUMMARY_BRIEF_FIXTURE),
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
        env=_subprocess_env(),
    )
    assert r.returncode == 2
    assert "--target-company" in (r.stderr or "")


def test_executive_summary_dry_run_still_requires_updated_targeting() -> None:
    r = subprocess.run(
        [
            sys.executable,
            "-m",
            "apps_rg",
            "--dry-run",
            "--section",
            "executive_summary",
            "--target-company",
            "Unify Consulting",
            "--target-role",
            "SVP Engineering",
            "--jd",
            str(REPO / "apps_rg" / "config" / "default_jd_targeting.txt"),
            "--manual-brief",
            str(REPO / "apps_rg" / "config" / "default_targeting_briefing.txt"),
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
        env=_subprocess_env(),
    )
    assert r.returncode == 2
    assert "not updated" in (r.stderr or "").lower()


def test_executive_summary_cli_fails_without_mandatory_targeting_inputs() -> None:
    r = subprocess.run(
        [sys.executable, "-m", "apps_rg", "--section", "executive_summary"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
        env=_subprocess_env(),
    )
    assert r.returncode == 2, r.stdout
    assert "--target-company" in (r.stderr or "")
    assert "--jd" in (r.stderr or "")
    assert "--manual-brief" in (r.stderr or "")


def test_no_standalone_executive_summary_pipeline_module():
    assert not (REPO / "apps_rg" / "runtime" / "pipeline" / "executive_summary_pipeline.py").is_file()


def test_canonical_cli_invokes_lane_not_dispatch_apps_rg_run(monkeypatch: pytest.MonkeyPatch) -> None:
    from apps_rg.__main__ import main

    called: dict[str, bool] = {"dispatch": False, "canonical": False}

    def _bad_dispatch(**_: object) -> dict:
        called["dispatch"] = True
        raise AssertionError("dispatch_apps_rg_run must not run for --section executive_summary")

    monkeypatch.setattr(
        "agentic_core.runtime.entry.apps_rg_dispatch.dispatch_apps_rg_run",
        _bad_dispatch,
    )

    real_run = __import__(
        "apps_rg.runtime.orchestration.canonical_dispatch",
        fromlist=["run_canonical_apps_rg_from_cli_primitives"],
    ).run_canonical_apps_rg_from_cli_primitives

    def _wrap_canonical(**kwargs: object):
        called["canonical"] = True
        assert str(kwargs.get("section") or "") == "executive_summary"
        assert kwargs.get("lane_provider_resolution_source") == CLI_PROVIDER_RESOLUTION_DEV_DEFAULT_QWEN_VLLM
        return real_run(**kwargs)

    monkeypatch.setattr(
        "apps_rg.runtime.orchestration.canonical_dispatch.run_canonical_apps_rg_from_cli_primitives",
        _wrap_canonical,
    )

    monkeypatch.setenv("APPS_RG_ALLOW_NON_ALLOW_EXIT_ZERO", "1")
    monkeypatch.delenv("APPS_RG_MODULAR_LANE_PROVIDER", raising=False)
    rc = main(_cli_argv())
    assert rc == 0
    assert called["canonical"] is True
    assert called["dispatch"] is False


def test_subprocess_cli_emits_exec_summary_artifacts_and_x3_shape() -> None:
    cmd = [sys.executable, "-m", "apps_rg", *_cli_argv()]
    r = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=180, env=_subprocess_env())
    assert r.returncode == 0, r.stderr + r.stdout

    rd = _latest_exec_summary_real_run_dir()
    for name in (
        "compiled_prompt.txt",
        "compiled_prompt_artifact.json",
        "canonical_claim_ledger_v2.json",
        "x2_gate_outputs.json",
        "x3_disposition.json",
    ):
        assert (rd / name).is_file(), f"missing {name} in {rd}"

    import json

    x3 = json.loads((rd / "x3_disposition.json").read_text(encoding="utf-8"))
    assert "x3_code" in x3
    assert "pass" in x3
    assert x3["x3_code"] in {
        "X3_ALLOW",
        "X3_BLOCK",
        "X3_REVIEW_JUDGE_PROVIDER_BLOCKED",
        "X3_REVIEW_MOCKED_PLUMBING_ONLY",
        "X3_REVIEW_PRODUCT_QUALITY",
        "X3_REVIEW_JUDGE_SOFT_FAIL",
    }


def test_resolve_cli_lane_provider_with_source_dev_default_qwen_vllm(monkeypatch: pytest.MonkeyPatch) -> None:
    from apps_rg.runtime.section_cli_defaults import resolve_cli_lane_provider_with_source

    monkeypatch.delenv("APPS_RG_MODULAR_LANE_PROVIDER", raising=False)
    p, src = resolve_cli_lane_provider_with_source(None)
    assert p == "qwen_vllm"
    assert src == CLI_PROVIDER_RESOLUTION_DEV_DEFAULT_QWEN_VLLM
    assert CLI_PROVIDER_RESOLUTION_DEV_DEFAULT_MOCK == CLI_PROVIDER_RESOLUTION_DEV_DEFAULT_QWEN_VLLM


def test_resolve_cli_lane_provider_with_source_env(monkeypatch: pytest.MonkeyPatch) -> None:
    from apps_rg.runtime.section_cli_defaults import (
        CLI_PROVIDER_RESOLUTION_ENV_APPS_RG_MODULAR_LANE_PROVIDER,
        resolve_cli_lane_provider_with_source,
    )

    monkeypatch.setenv("APPS_RG_MODULAR_LANE_PROVIDER", "qwen_vllm")
    p, src = resolve_cli_lane_provider_with_source(None)
    assert p == "qwen_vllm"
    assert src == CLI_PROVIDER_RESOLUTION_ENV_APPS_RG_MODULAR_LANE_PROVIDER


def test_executive_summary_dispatch_module_main_is_fail_closed() -> None:
    r = subprocess.run(
        [sys.executable, "-m", "apps_rg.runtime.sections.executive_summary_lane", "--help"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 2
    assert "Deprecated runtime interface" in (r.stderr or "")
    assert "python -m apps_rg --section executive_summary" in (r.stderr or "")


def test_resolve_cli_lane_provider_with_source_cli_override() -> None:
    from apps_rg.runtime.section_cli_defaults import (
        CLI_PROVIDER_RESOLUTION_CLI_OVERRIDE,
        resolve_cli_lane_provider_with_source,
    )

    p, src = resolve_cli_lane_provider_with_source("qwen_vllm")
    assert p == "qwen_vllm"
    assert src == CLI_PROVIDER_RESOLUTION_CLI_OVERRIDE


def test_subprocess_run_manifest_records_dev_default_qwen_stub_real_llm() -> None:
    import json

    cmd = [sys.executable, "-m", "apps_rg", *_cli_argv()]
    r = subprocess.run(
        cmd,
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180,
        env=_subprocess_env_provider_unset(),
    )
    assert r.returncode == 0, r.stderr + r.stdout

    rd = _latest_exec_summary_real_run_dir()
    manifest = json.loads((rd / "run_manifest.json").read_text(encoding="utf-8"))
    assert manifest["provider_resolution_source"] == CLI_PROVIDER_RESOLUTION_DEV_DEFAULT_QWEN_VLLM
    # Dev default may use the Qwen offline contract stub (structure-only) or a real vLLM path.
    assert manifest["runtime_generation_status"] in {"REAL_LLM", "OFFLINE_CONTRACT_STUB"}
    assert isinstance(manifest["proof_eligible"], bool)

    trace = json.loads((rd / "prompt_selection_trace.json").read_text(encoding="utf-8"))
    assert trace["provider_resolution_source"] == CLI_PROVIDER_RESOLUTION_DEV_DEFAULT_QWEN_VLLM


def test_exec_summary_cli_x3_disposition_exit_1_reports_cli_path_pass_not_product_fail() -> None:
    """Blocked product (X3 non-ALLOW) with default exit policy → exit 1; report separates CLI vs product.

    Default bare lane with the offline contract stub may X3_ALLOW; disable the stub and point vLLM at a
    closed local port so the transport path returns BLOCKED without changing production defaults.
    """
    cmd = [sys.executable, "-m", "apps_rg", *_cli_argv()]
    env = _exec_summary_subprocess_env(
        allow_non_allow_exit_zero=False,
        qwen_offline_contract_stub=False,
    )
    env["VLLM_BASE_URL"] = "http://127.0.0.1:1/v1"
    env["APPS_RG_QWEN_TIMEOUT_SECONDS"] = "3"
    r = subprocess.run(
        cmd,
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180,
        env=env,
    )
    assert r.returncode == 1, r.stderr + r.stdout

    rd = _latest_exec_summary_real_run_dir()
    x3 = json.loads((rd / "x3_disposition.json").read_text(encoding="utf-8"))
    x3_code = str(x3.get("x3_code") or "")
    pq = str(x3.get("product_quality_status") or "UNKNOWN")
    manifest = json.loads((rd / "run_manifest.json").read_text(encoding="utf-8"))
    expected_status = (
        "PASS_RUNTIME_PROOF_ELIGIBLE" if bool(manifest.get("proof_eligible")) else "PASS_NONCERTIFYING_RUNTIME_PROOF"
    )

    parsed = parse_cli_execution_summary_block(r.stdout)
    assert parsed.get("STATUS") == expected_status
    assert parsed.get("CLI_PATH_STATUS") == "PASS"
    assert parsed.get("PRODUCT_STATUS") == x3_code
    assert parsed.get("PROCESS_EXIT_CODE") == "1"
    assert parsed.get("EXPECTED_NONZERO_EXIT") == "true"
    assert parsed.get("PRODUCT_QUALITY_STATUS") == pq
    assert parsed.get("PROOF_ELIGIBLE") == "false"

    rep = _assert_stdout_matches_persisted_report(rd, r.stdout)
    assert rep["process_exit_code"] == 1
    assert rep["expected_nonzero_exit"] is True
    assert rep["product_status"] == x3_code


def test_exec_summary_cli_allow_non_allow_exit_zero_exit_0_product_status_unchanged() -> None:
    """Relax process exit only; PRODUCT_STATUS and X3 artifacts stay authoritative."""
    cmd = [sys.executable, "-m", "apps_rg", *_cli_argv()]
    r = subprocess.run(
        cmd,
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180,
        env=_subprocess_env_provider_unset(),
    )
    assert r.returncode == 0, r.stderr + r.stdout

    rd = _latest_exec_summary_real_run_dir()
    x3 = json.loads((rd / "x3_disposition.json").read_text(encoding="utf-8"))
    x3_code = str(x3.get("x3_code") or "")

    parsed = parse_cli_execution_summary_block(r.stdout)
    assert parsed.get("PROCESS_EXIT_CODE") == "0"
    assert parsed.get("EXPECTED_NONZERO_EXIT") == "false"
    assert parsed.get("PRODUCT_STATUS") == x3_code
    assert parsed.get("CLI_PATH_STATUS") == "PASS"

    rep = _assert_stdout_matches_persisted_report(rd, r.stdout)
    assert rep["process_exit_code"] == 0
    assert rep["expected_nonzero_exit"] is False
    assert rep["product_status"] == x3_code


def test_cli_execution_report_expected_nonzero_matches_allow_policy(tmp_path: Path) -> None:
    x3_path = tmp_path / "x3_disposition.json"
    x3_path.write_text(
        json.dumps(
            {
                "x3_code": "X3_BLOCK",
                "product_quality_status": "FAIL",
                "pass": False,
                "x2_failed_gates": ["x2_sentence_coverage_pass"],
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "run_manifest.json").write_text(
        json.dumps({"proof_eligible": False}),
        encoding="utf-8",
    )
    result = {
        "exit_status": "error",
        "outcome_authorized": False,
        "artifact_dir": str(tmp_path),
        "x3_disposition": "X3_BLOCK",
        "fault": "",
    }
    lines = build_section_cli_execution_report_lines(
        result=result,
        lane_provider_resolution_source=CLI_PROVIDER_RESOLUTION_DEV_DEFAULT_MOCK,
        allow_non_allow_exit_zero_effective=False,
        process_exit_code=1,
    )
    text = "\n".join(lines)
    parsed = parse_cli_execution_summary_block(text)
    assert parsed["EXPECTED_NONZERO_EXIT"] == "true"
    assert parsed["PRODUCT_STATUS"] == "X3_BLOCK"

    lines_allow = build_section_cli_execution_report_lines(
        result=result,
        lane_provider_resolution_source=CLI_PROVIDER_RESOLUTION_DEV_DEFAULT_MOCK,
        allow_non_allow_exit_zero_effective=True,
        process_exit_code=0,
    )
    parsed_allow = parse_cli_execution_summary_block("\n".join(lines_allow))
    assert parsed_allow["EXPECTED_NONZERO_EXIT"] == "false"
    assert parsed_allow["PRODUCT_STATUS"] == "X3_BLOCK"

    payload = build_section_cli_execution_report_payload(
        result=result,
        lane_provider_resolution_source=CLI_PROVIDER_RESOLUTION_DEV_DEFAULT_MOCK,
        allow_non_allow_exit_zero_effective=False,
        process_exit_code=1,
    )
    persist_cli_section_execution_report(tmp_path, payload)
    disk = json.loads((tmp_path / CLI_SECTION_EXECUTION_REPORT_FILE).read_text(encoding="utf-8"))
    assert disk == payload
