"""Contract matrix: executive_summary CLI exit vs operator disposition (synthetic artifacts)."""

from __future__ import annotations

import json
from pathlib import Path

from apps_rg.runtime.cli_section_execution_report import (
    CLI_SECTION_EXECUTION_REPORT_FILE,
    build_section_cli_execution_report_lines,
    section_lane_process_exit_code,
)


def _fixture_dir(tmp_path: Path, scenario: str) -> Path:
    base = {
        "draft_soft_fail": {
            "x3_code": "X3_REVIEW_JUDGE_SOFT_FAIL",
            "pass": False,
            "product_quality_status": "PASS",
            "runtime_generation_status": "REAL_LLM",
            "expected_exit": 0,
            "operator_status": "DRAFT_READY",
        },
        "certified": {
            "x3_code": "X3_ALLOW",
            "pass": True,
            "product_quality_status": "PASS",
            "runtime_generation_status": "REAL_LLM",
            "expected_exit": 0,
            "operator_status": "CERTIFIED",
        },
        "x2_fail": {
            "x3_code": "X3_REVIEW_PRODUCT_QUALITY",
            "pass": False,
            "product_quality_status": "FAIL",
            "runtime_generation_status": "REAL_LLM",
            "expected_exit": 1,
            "operator_status": "NOT_READY",
        },
        "generation_blocked": {
            "x3_code": "X3_REVIEW_JUDGE_PROVIDER_BLOCKED",
            "pass": False,
            "product_quality_status": "PASS",
            "runtime_generation_status": "BLOCKED",
            "expected_exit": 1,
            "operator_status": "NOT_READY",
        },
    }[scenario]
    rd = tmp_path / scenario
    rd.mkdir()
    (rd / "run_manifest.json").write_text(
        json.dumps(
            {
                "section_id": "executive_summary",
                "runtime_generation_status": base["runtime_generation_status"],
                "proof_eligible": scenario == "certified",
            }
        ),
        encoding="utf-8",
    )
    (rd / "x3_disposition.json").write_text(
        json.dumps(
            {
                "x3_code": base["x3_code"],
                "pass": base["pass"],
                "product_quality_status": base["product_quality_status"],
            }
        ),
        encoding="utf-8",
    )
    (rd / "l2_output.json").write_text(
        json.dumps({"runtime_generation_status": base["runtime_generation_status"]}),
        encoding="utf-8",
    )
    base["_dir"] = rd
    return base  # type: ignore[return-value]


def test_operator_outcome_matrix(tmp_path: Path) -> None:
    for scenario in ("draft_soft_fail", "certified", "x2_fail", "generation_blocked"):
        spec = _fixture_dir(tmp_path, scenario)
        rd: Path = spec["_dir"]
        result = {
            "exit_status": "error" if spec["expected_exit"] else "success",
            "outcome_authorized": bool(spec["pass"]),
            "artifact_dir": str(rd),
            "fault": "",
        }
        rc = section_lane_process_exit_code(
            result=result,
            allow_non_allow_exit_zero_effective=False,
            section_id="executive_summary",
        )
        assert rc == spec["expected_exit"], scenario

        lines = build_section_cli_execution_report_lines(
            result=result,
            lane_provider_resolution_source=None,
            allow_non_allow_exit_zero_effective=False,
            process_exit_code=rc,
        )
        text = "\n".join(lines)
        assert f"OPERATOR_STATUS: {spec['operator_status']}" in text, scenario
        assert f"PROCESS_EXIT_CODE: {spec['expected_exit']}" in text, scenario

        payload_path = rd / CLI_SECTION_EXECUTION_REPORT_FILE
        from apps_rg.runtime.cli_section_execution_report import (
            persist_cli_section_execution_report,
            build_section_cli_execution_report_payload,
        )

        payload = build_section_cli_execution_report_payload(
            result=result,
            lane_provider_resolution_source=None,
            allow_non_allow_exit_zero_effective=False,
            process_exit_code=rc,
        )
        persist_cli_section_execution_report(rd, payload)
        assert payload["operator_status"] == spec["operator_status"]
