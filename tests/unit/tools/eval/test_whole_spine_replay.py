from __future__ import annotations

import json
import sys
from pathlib import Path

from tools.eval.whole_spine_replay import run_scenario


def _write_scenario(tmp_path: Path, command: list[str], receipt_name: str = "runtime.json") -> Path:
    (tmp_path / "jd.txt").write_text("job description", encoding="utf-8")
    (tmp_path / "briefing.md").write_text("# briefing", encoding="utf-8")
    (tmp_path / "policy.json").write_text('{"policy":"offline"}', encoding="utf-8")
    scenario = {
        "scenario_id": "offline-spine-smoke",
        "provider_mode": "offline_fixture",
        "expected_receipt_class": "SPINE_COMPLETE_CERTIFIED",
        "inputs": {
            "jd": "jd.txt",
            "briefing": "briefing.md",
            "policies": ["policy.json"],
        },
        "command": command,
        "runtime_receipt_path": "{output_dir}/" + receipt_name,
    }
    path = tmp_path / "scenario.json"
    path.write_text(json.dumps(scenario), encoding="utf-8")
    return path


def test_run_scenario_executes_command_and_hashes_inputs(tmp_path: Path) -> None:
    script = tmp_path / "emit_receipt.py"
    script.write_text(
        "import json, pathlib, sys\n"
        "pathlib.Path(sys.argv[1]).write_text(json.dumps({"
        "'receipt_class':'SPINE_COMPLETE_CERTIFIED',"
        "'provider_mode':'offline_fixture'}), encoding='utf-8')\n",
        encoding="utf-8",
    )
    scenario = _write_scenario(
        tmp_path,
        [sys.executable, str(script), "{output_dir}/runtime.json"],
    )

    receipt = run_scenario(
        scenario_path=scenario,
        output_dir=tmp_path / "out",
        repo_root=tmp_path,
        timeout_seconds=10,
    )

    assert receipt.passed is True
    assert receipt.exit_code == 0
    assert receipt.runtime_receipt_present is True
    assert receipt.runtime_receipt_class == "SPINE_COMPLETE_CERTIFIED"
    assert receipt.input_identity.jd_sha256
    assert receipt.input_identity.briefing_sha256
    assert receipt.input_identity.policy_sha256
    assert receipt.input_identity.bundle_sha256


def test_missing_runtime_receipt_fails_even_when_command_passes(tmp_path: Path) -> None:
    scenario = _write_scenario(tmp_path, [sys.executable, "-c", "print('no receipt')"])

    receipt = run_scenario(
        scenario_path=scenario,
        output_dir=tmp_path / "out",
        repo_root=tmp_path,
        timeout_seconds=10,
    )

    assert receipt.passed is False
    assert "RUNTIME_RECEIPT_MISSING" in receipt.reason_codes


def test_baseline_mismatch_blocks_candidate(tmp_path: Path) -> None:
    script = tmp_path / "emit_receipt.py"
    script.write_text(
        "import json, pathlib, sys\n"
        "pathlib.Path(sys.argv[1]).write_text(json.dumps({"
        "'receipt_class':'SPINE_COMPLETE_CERTIFIED',"
        "'provider_mode':'offline_fixture',"
        "'value':'candidate'}), encoding='utf-8')\n",
        encoding="utf-8",
    )
    scenario = _write_scenario(
        tmp_path,
        [sys.executable, str(script), "{output_dir}/runtime.json"],
    )
    baseline = tmp_path / "baseline.json"
    baseline.write_text(
        json.dumps(
            {
                "scenarios": {
                    "offline-spine-smoke": {
                        "runtime_receipt_sha256": "not-the-candidate-digest",
                        "provider_mode": "offline_fixture",
                        "expected_receipt_class": "SPINE_COMPLETE_CERTIFIED",
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    receipt = run_scenario(
        scenario_path=scenario,
        output_dir=tmp_path / "out",
        repo_root=tmp_path,
        baseline_path=baseline,
        timeout_seconds=10,
    )

    assert receipt.passed is False
    assert receipt.baseline.status == "REGRESSION"
    assert "BASELINE_REGRESSION" in receipt.reason_codes
