"""Post-W7 secondary live-sourced 15-contact company soak."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

from scripts.apps_lic.run_post_w7_live_15_contact_company_validation import (
    COMPANIES,
    LIVE_CONTACTS,
    SECONDARY_E2E_GATE_ROLE,
    SECONDARY_E2E_GATE_SHAPE,
    run_post_w7_live_15_contact_company_validation,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
RUNNER = REPO_ROOT / "scripts" / "apps_lic" / "run_post_w7_live_15_contact_company_validation.py"


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _is_public_linkedin_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme == "https" and parsed.netloc.endswith("linkedin.com")


def test_post_w7_live_sources_are_5_per_company_and_targeting_files_exist() -> None:
    assert SECONDARY_E2E_GATE_ROLE == "secondary_live_company_soak"
    assert SECONDARY_E2E_GATE_SHAPE == "5_per_company_15_company_validation"
    assert len(LIVE_CONTACTS) == 15
    counts = {company: 0 for company in COMPANIES}
    for contact in LIVE_CONTACTS:
        counts[contact.company_key] += 1
        assert _is_public_linkedin_url(contact.source_url)
    assert counts == {"aig": 5, "citi": 5, "neo4j": 5}
    for company in COMPANIES.values():
        assert company.jd_path.is_file(), company.jd_path
        assert company.briefing_path.is_file(), company.briefing_path


def test_post_w7_live_runner_produces_15_canonical_rows(tmp_path: Path) -> None:
    result = run_post_w7_live_15_contact_company_validation(output_dir=tmp_path)
    summary = result["summary"]
    rows = _load_json(tmp_path / "rows.json")["rows"]

    assert summary["acceptance_passed"] is True
    assert summary["live_contact_pull"] is True
    assert summary["profile_count"] == 15
    assert summary["company_counts"] == {"AIG": 5, "Citi": 5, "Neo4j": 5}
    assert summary["canonical_runtime_rows"] == 15
    assert summary["parseable_proof_bundle_count"] == 15
    assert summary["quality_violation_count"] == 0
    assert len(rows) == 15

    for row in rows:
        assert row["source_mode"] == "live_public_web_pull"
        assert row["runtime_artifact_dir"]
        assert row["canonical_producer"].endswith("canonical_dispatch")
        assert row["proof_bundle_status"] == "PASS"
        assert row["shared_x3_disposition"]
        assert row["no_send_assertion"] is True
        assert row["no_l4_write_assertion"] is True
        assert row["no_connector_post_assertion"] is True
        if row["outcome_authorized"] is True:
            assert row["proof_packet_id"]
            assert row["selected_candidate_id"]
            assert row["x2_result"] == "X2_VALIDATION_PASS"
            assert row["x1d_result"] in {"X1D_NOT_REQUIRED", "X1D_VALIDATION_PASS"}

    assert (tmp_path / "live_contact_pull.json").is_file()
    assert (tmp_path / "aggregate_report.md").is_file()


def test_post_w7_live_runner_cli_writes_expected_artifacts(tmp_path: Path) -> None:
    completed = subprocess.run(
        [
            sys.executable,
            str(RUNNER),
            "--output-dir",
            str(tmp_path),
        ],
        cwd=REPO_ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    payload = json.loads(completed.stdout)

    assert payload["output_dir"] == str(tmp_path.resolve())
    assert set(payload["artifact_files"]) == {
        "summary.json",
        "rows.json",
        "live_contact_pull.json",
        "aggregate_report.md",
    }
    summary = _load_json(tmp_path / "summary.json")
    assert summary["acceptance_passed"] is True
    assert summary["profile_count"] == 15
