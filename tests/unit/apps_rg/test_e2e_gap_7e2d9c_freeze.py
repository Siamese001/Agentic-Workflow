"""W0 evidence-freeze guard for plan apps-rg-e2e-gap-remediation-7e2d9c.

Validates that the tracked fixture under ``tests/fixtures/e2e_gap_7e2d9c/`` still agrees
with the frozen AIG + Brown failing end-to-end signature. This is a fixture-integrity /
documentation guard: it reads static copies of the original (gitignored) bundle evidence
and asserts the three load-bearing facts the remediation waves must eliminate.

It deliberately imports nothing from ``apps_rg`` and needs no ``APPS_RG_TEST_HARNESS`` —
it runs in product mode and stays green regardless of how the live system evolves, because
it guards the frozen record, not the live run.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

# tests/unit/apps_rg/<this file> -> parents[2] == tests/
FIXTURE_DIR = Path(__file__).resolve().parents[2] / "fixtures" / "e2e_gap_7e2d9c"
MANIFEST_PATH = FIXTURE_DIR / "manifest.json"

TARGET_IDS = ("aig", "brown")

# The frozen signature (see manifest.json / README.md).
EXPECTED_X3_BLOCK_LANES = {
    "competencies",
    "unify_bullets",
    "ibm_bullets",
    "insurtech_bullets",
    "ey_bullets",
    "executive_summary",
    "headline",
}
EXPECTED_PRE_RUN_LANES = {
    "unify_narrative",
    "ibm_narrative",
    "insurtech_narrative",
    "ey_narrative",
}
EXPECTED_TOTAL_LANES = 11


def _load(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


@pytest.fixture(scope="module")
def manifest() -> dict:
    assert MANIFEST_PATH.is_file(), f"missing freeze manifest: {MANIFEST_PATH}"
    return _load(MANIFEST_PATH)


def test_manifest_shape(manifest: dict) -> None:
    assert manifest["schema_version"] == "apps_rg.e2e_gap_freeze.v1"
    assert manifest["plan"] == "apps-rg-e2e-gap-remediation-7e2d9c"
    assert manifest["wave"] == "W0"
    assert set(manifest["targets"]) == set(TARGET_IDS)


@pytest.mark.parametrize("target_id", TARGET_IDS)
def test_frozen_files_present(manifest: dict, target_id: str) -> None:
    target = manifest["targets"][target_id]
    for rel in target["frozen_files"]:
        assert (FIXTURE_DIR / rel).is_file(), f"frozen evidence missing: {rel}"


@pytest.mark.parametrize("target_id", TARGET_IDS)
def test_identity_matches_ingress(manifest: dict, target_id: str) -> None:
    target = manifest["targets"][target_id]
    ingress = _load(FIXTURE_DIR / target_id / "ingress_raw.json")
    assert ingress["target_company"] == target["target_company"]
    assert ingress["target_role"] == target["target_role"]


@pytest.mark.parametrize("target_id", TARGET_IDS)
def test_provider_never_attempted(target_id: str) -> None:
    """Assertion 1: the block is upstream of generation — provider never called."""
    provider = _load(FIXTURE_DIR / target_id / "competencies_provider_response.json")
    assert provider["provider_attempted"] is False
    assert provider["provider_available"] is False
    assert "C0.2 product hybrid dense lane" in provider["exact_provider_error"]


@pytest.mark.parametrize("target_id", TARGET_IDS)
def test_all_eleven_lanes_blocked(target_id: str) -> None:
    """Assertion 2: every lane blocked, zero authorized."""
    status = _load(FIXTURE_DIR / target_id / "full_run_section_status.json")
    lanes = {lane["lane"]: lane for lane in status["lanes"]}
    assert len(lanes) == EXPECTED_TOTAL_LANES

    for name in EXPECTED_X3_BLOCK_LANES:
        lane = lanes[name]
        assert lane["x3_code"] == "X3_BLOCK", name
        assert lane["runtime_generation_status"] == "REQUIRED_PROOF_ABSENT", name

    for name in EXPECTED_PRE_RUN_LANES:
        lane = lanes[name]
        assert lane["x3_code"].startswith("PRE_RUN"), name

    authorized = [
        lane for lane in lanes.values()
        if lane["x3_code"] not in ("X3_BLOCK",) and not lane["x3_code"].startswith("PRE_RUN")
    ]
    assert authorized == [], f"expected zero authorized lanes, got {authorized}"


@pytest.mark.parametrize("target_id", TARGET_IDS)
def test_integrated_evidence_status_zero_executed(target_id: str) -> None:
    """Assertion 2 cross-check: integrated evidence finalized nothing."""
    evidence = _load(FIXTURE_DIR / target_id / "integrated_lane_evidence_status.json")
    assert evidence["executed_lane_count"] == 0
    assert evidence["not_run_lane_count"] == EXPECTED_TOTAL_LANES
    assert evidence["lanes_finalized"] == []


@pytest.mark.parametrize("target_id", TARGET_IDS)
def test_exit_code_disposition_mismatch(manifest: dict, target_id: str) -> None:
    """Assertion 3: internal status is error, yet the aggregate disposition is allow-style X3A.

    This is the G4 (exit-code masking) + G16 (misleading aggregate) signature W1/W4 must fix.
    """
    terminal = _load(FIXTURE_DIR / target_id / "terminal_ret_packet.json")["payload"]
    # Internal state = error: non-empty fault and FAIL on Exec + Seal sub-stages.
    assert terminal["l2_fault"].strip(), "expected a non-empty internal l2_fault"
    sub = {stage["sub_stage_id"]: stage["status"] for stage in terminal["l2_sub_stages"]}
    assert sub["E3"] == "FAIL"
    assert sub["E5"] == "FAIL"

    # Aggregate disposition is the misleading allow-style X3A despite zero authorized lanes.
    disposition = _load(FIXTURE_DIR / target_id / "x3_disposition_receipt.json")["payload"]
    assert disposition["disposition"] == "X3A"

    # Manifest records the observed integrated-CLI exit code 0 (the masked failure).
    mismatch = manifest["proof_assertions"]["exit_code_mismatch"]
    assert mismatch["internal_status"] == "error"
    assert mismatch["integrated_cli_exit_code_observed"] == 0
    assert mismatch["misleading_aggregate_disposition"] == "X3A"
