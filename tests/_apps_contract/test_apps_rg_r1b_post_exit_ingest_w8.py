"""W8 — apps_rg R1B post-Exit ingestion eligibility contract."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURES = REPO_ROOT / "artifacts" / "apps_rg" / "r1b_semantic_cache" / "w8_fixtures"


@pytest.fixture(scope="module", autouse=True)
def _ensure_w8_fixtures() -> None:
    if not (FIXTURES / "accepted_post_exit_ingestion.json").is_file():
        import subprocess
        import sys

        subprocess.run(
            [sys.executable, str(REPO_ROOT / "tools" / "apps_rg" / "emit_r1b_w8_fixtures.py")],
            check=True,
            cwd=str(REPO_ROOT),
        )


def test_w8_fixtures_present() -> None:
    for name in (
        "accepted_post_exit_ingestion",
        "rejected_mock_runtime_ingestion",
        "rejected_missing_x3_ingestion",
        "rejected_missing_proof_chunks_ingestion",
        "rejected_missing_required_digest_ingestion",
    ):
        assert (FIXTURES / f"{name}.json").is_file(), name


def test_accepted_fixture_post_exit_admissible() -> None:
    payload = json.loads((FIXTURES / "accepted_post_exit_ingestion.json").read_text(encoding="utf-8"))
    assert payload["admissible"] is True
    assert payload["exit_metadata_present"] is True
    assert payload["ingestion_phase"] == "post_exit_only"
    assert payload["record"]["cache_admissible"] is True


def test_rejected_fixtures_not_admissible() -> None:
    cases = {
        "rejected_mock_runtime_ingestion": "not_mock_runtime",
        "rejected_missing_x3_ingestion": "missing_exit_x3_disposition",
        "rejected_missing_proof_chunks_ingestion": "final_resume_chunk_present",
        "rejected_missing_required_digest_ingestion": "jd_digest_present",
    }
    for fixture_name, reason_fragment in cases.items():
        payload = json.loads((FIXTURES / f"{fixture_name}.json").read_text(encoding="utf-8"))
        assert payload["admissible"] is False, fixture_name
        assert reason_fragment in payload["non_admissible_reason"], fixture_name


def test_adapter_requires_post_exit_flag(tmp_path: Path) -> None:
    from apps_rg.cache.r1b_adapter import AppsRgR1BCacheAdapter

    adapter = AppsRgR1BCacheAdapter(runs_dir=str(tmp_path))
    assert (
        adapter.store_intent_and_output(
            intent={"target_company": "X", "target_role": "Y"},
            chunks=[],
        )
        is None
    )


def test_post_exit_ingest_module_exports() -> None:
    from apps_rg.cache import r1b_post_exit_eligibility, r1b_post_exit_ingest

    assert hasattr(r1b_post_exit_eligibility, "assess_post_exit_ingestion_eligibility")
    assert hasattr(r1b_post_exit_ingest, "ingest_post_exit_after_run")
