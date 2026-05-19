"""Mock CLI runs: verify section_input_usage_ledger dual-source receipts for all sections."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]

SECTION_IDS = (
    "headline",
    "executive_summary",
    "competencies",
    "unify_bullets",
    "unify_narrative",
    "ibm_bullets",
    "ibm_narrative",
)

_STRIP = frozenset(
    {
        "APPS_RG_MODULAR_LANE_PROVIDER",
        "APPS_RG_QWEN_OFFLINE_CONTRACT_STUB",
        "VLLM_BASE_URL",
        "APPS_RG_QWEN_TIMEOUT_SECONDS",
    }
)


def _env() -> dict[str, str]:
    env = {k: v for k, v in os.environ.items() if k not in _STRIP}
    env["APPS_RG_ALLOW_NON_ALLOW_EXIT_ZERO"] = "1"
    env["APPS_RG_QWEN_OFFLINE_CONTRACT_STUB"] = "1"
    return env


def _latest_mock_run_dir(section_id: str) -> Path:
    from apps_rg.runtime.runtime_proof_layout import resolve_run_dir_from_pointer

    rd = resolve_run_dir_from_pointer(REPO, section_id, "mock")
    assert rd is not None, f"no mock run pointer for {section_id}"
    return rd


def _assert_usage_ledger_dual_source(doc: dict) -> None:
    assert doc.get("skills_authority_source_type") == "augmented_skills_graph"
    assert doc.get("skills_authority_status") == "PASS"
    claim_type = doc.get("claim_evidence_source_type")
    assert claim_type in ("candidate_fact_ledger", "selected_role_fact_set", "base_resume_fallback")
    ia = doc.get("input_authority") or {}
    assert ia.get("augmented_skills_graph") == "SKILLS_COMPETENCY_AUTHORITY"
    assert doc.get("legacy_broad_skills_ledger_skills_authority") is not True
    riu = doc.get("required_input_usage") or {}
    assert "augmented_skills_graph" in riu
    assert riu["augmented_skills_graph"]["authority"] == "SKILLS_COMPETENCY_AUTHORITY"
    if claim_type == "candidate_fact_ledger":
        assert ia.get("broad_skills_ledger") == "CLAIM_EVIDENCE_ONLY_DEPRECATED_SKILLS_LABEL"


@pytest.mark.parametrize("section_id", SECTION_IDS)
def test_mock_cli_refreshes_dual_source_usage_ledger(section_id: str) -> None:
    r = subprocess.run(
        [
            sys.executable,
            "-m",
            "apps_rg",
            "--section",
            section_id,
            "--provider",
            "mock",
            "--mock-judges",
            "--allow-test-mock-judges",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env=_env(),
    )
    assert r.returncode == 0, f"{section_id} stderr={r.stderr!r} stdout={r.stdout!r}"
    led_path = _latest_mock_run_dir(section_id) / "section_input_usage_ledger.json"
    assert led_path.is_file(), led_path
    doc = json.loads(led_path.read_text(encoding="utf-8"))
    _assert_usage_ledger_dual_source(doc)
    x2_path = _latest_mock_run_dir(section_id) / "x2_source_fact_pool_receipt.json"
    if x2_path.is_file():
        x2 = json.loads(x2_path.read_text(encoding="utf-8"))
        assert x2.get("skills_authority_source_type") in (None, "augmented_skills_graph")
        if x2.get("skills_authority_status"):
            assert x2.get("skills_authority_status") == "PASS"
            assert x2.get("skills_authority_x2_boundary") == "PASS"
