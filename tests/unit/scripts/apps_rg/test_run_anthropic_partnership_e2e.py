"""apps-test-model: APP CONTRACT.

Bounded Anthropic partnership E2E launcher tests.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.apps_rg.run_anthropic_partnership_e2e import (
    extract_exact_run_dir,
    validate_pinned_baseline,
)


def test_launcher_direct_help_bootstraps_repo_imports() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    completed = subprocess.run(  # noqa: S603 - argv is a fixed local test command.
        [sys.executable, "scripts/apps_rg/run_anthropic_partnership_e2e.py", "--help"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        timeout=30,
        shell=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert "usage:" in completed.stdout


def test_extract_exact_run_dir_requires_one_child_of_output_root(tmp_path: Path) -> None:
    root = tmp_path / "runs"
    run = root / "e2e_001"
    run.mkdir(parents=True)
    stdout = f"FRESH_E2E_ARTIFACT_DIR root={root} run_dir={run} route_flag=FLAG\n"

    assert extract_exact_run_dir(stdout, root) == run.resolve()

    with pytest.raises(RuntimeError, match="COUNT_INVALID:0"):
        extract_exact_run_dir("no receipt", root)
    outside = tmp_path / "outside"
    outside.mkdir()
    with pytest.raises(RuntimeError, match="OUTSIDE_ROOT"):
        extract_exact_run_dir(
            f"FRESH_E2E_ARTIFACT_DIR root={root} run_dir={outside} route_flag=FLAG\n",
            root,
        )


def test_validate_pinned_baseline_rejects_digest_drift(tmp_path: Path) -> None:
    baseline_run = tmp_path / "artifacts" / "baseline"
    baseline_run.mkdir(parents=True)
    mandatory = baseline_run / "APPS_RG_MANDATORY_RUN_OUTPUT.json"
    mandatory.write_text(
        json.dumps(
            {
                "result_summary": {
                    "exit_status": "success",
                    "outcome_authorized": True,
                    "x3_disposition": "X3D",
                }
            }
        ),
        encoding="utf-8",
    )
    digest = hashlib.sha256(mandatory.read_bytes()).hexdigest()
    contract = tmp_path / "baseline.json"
    contract.write_text(
        json.dumps(
            {
                "schema_version": "apps_rg.e2e_baseline.v1",
                "baseline_id": "test-pass",
                "baseline_run_dir": "artifacts/baseline",
                "mandatory_output_sha256": digest,
                "git_commit": "a" * 40,
                "expected_exit_status": "success",
                "expected_outcome_authorized": True,
                "expected_x3_disposition": "X3D",
                "target_company": "Anthropic",
                "target_role": "Manager of Applied AI Architecture, Partnerships",
            }
        ),
        encoding="utf-8",
    )

    assert validate_pinned_baseline(tmp_path, contract)["mandatory_output_sha256"] == digest
    mandatory.write_text("drift", encoding="utf-8")
    with pytest.raises(RuntimeError, match="PINNED_BASELINE_DIGEST_MISMATCH"):
        validate_pinned_baseline(tmp_path, contract)
