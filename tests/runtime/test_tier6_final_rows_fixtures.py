"""Tier 6 final-row fixture + reference-only-policy tests (Prompt B).

Validates the 6 MUST-row scenario+replay fixtures (CT..CY) against the
must_release_blocking_refs contract AND the 15 NON_BLOCKING_REFERENCE
rows against the reference-only policy contract. Pure JSON inspection
plus selection-row read: no runtime, no proof harness, no replay
machinery, no OTEL exporter.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agentic_core.runtime.prove_requirements import tier_fixture_bootstrap
from agentic_core.runtime.prove_requirements.tier6_refs import (
    must_release_blocking_refs,
    reference_only_policy_refs,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
TRACES = REPO_ROOT / "artifacts/runtime/requirements_proof/traces"
REPLAY = REPO_ROOT / "artifacts/runtime/requirements_proof/replay"
ARTIFACTS = REPO_ROOT / "artifacts/runtime/requirements_proof"
SELECTION = REPO_ROOT / "docs/reference/contracts/tier6/TIER6_SELECTION.json"

MUST_SCENARIOS = [
    ("REQ-C0-WEAK-SUPPORT-REFINEMENT-001", "CT", "c0_weak_support_refinement"),
    ("REQ-E2E-ACCEPTANCE-COMMANDS-001", "CU", "e2e_acceptance_commands"),
    ("REQ-E2E-GOLDEN-PATH-001", "CV", "e2e_golden_path"),
    ("REQ-E2E-ROUTE-PATH-COVERAGE-001", "CW", "e2e_route_path_coverage"),
    ("REQ-EXIT-RUNTIME-TO-REGRESSION-001", "CX", "exit_runtime_to_regression"),
    ("REQ-L6-HUMAN-CALIBRATION-001", "CY", "l6_human_calibration"),
]

REFERENCE_ONLY_REQ_IDS = list(reference_only_policy_refs.STEP1_REQ_IDS)


@pytest.fixture(scope="module", autouse=True)
def _bootstrap() -> None:
    tier_fixture_bootstrap.materialize()


def _load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Cardinality / shape sanity checks.
# ---------------------------------------------------------------------------


def test_must_cluster_size_is_six() -> None:
    assert len(must_release_blocking_refs.STEP1_REQ_IDS) == 6


def test_reference_only_cluster_size_is_fifteen() -> None:
    assert len(reference_only_policy_refs.STEP1_REQ_IDS) == 15


def test_total_tier6_partitioned_to_twenty_one() -> None:
    must = set(must_release_blocking_refs.STEP1_REQ_IDS)
    ref = set(reference_only_policy_refs.STEP1_REQ_IDS)
    assert must.isdisjoint(ref)
    assert len(must | ref) == 21


# ---------------------------------------------------------------------------
# 6 MUST rows: trace contract + replay pair invariant_digest stability.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("req_id,letters,slug", MUST_SCENARIOS)
def test_tier6_must_trace_fixture_validates(req_id: str, letters: str, slug: str) -> None:
    key = f"{letters}_{slug}"
    p = TRACES / f"scenario_{key}.json"
    assert p.is_file(), f"missing trace fixture: {p}"
    payload = _load(p)
    ok, errors = must_release_blocking_refs.validate_contract(req_id, payload)
    assert ok, f"{req_id} contract errors: {errors}"


@pytest.mark.parametrize("req_id,letters,slug", MUST_SCENARIOS)
def test_tier6_must_replay_pair_invariant_digest_stable(req_id: str, letters: str, slug: str) -> None:
    key = f"{letters}_{slug}"
    r1 = REPLAY / f"replay_{key}_run_1.json"
    r2 = REPLAY / f"replay_{key}_run_2.json"
    assert r1.is_file() and r2.is_file()
    p1 = _load(r1)
    p2 = _load(r2)
    assert p1["step1_req_id"] == req_id
    assert p2["step1_req_id"] == req_id
    assert p1["expected_fail_reason"] == p2["expected_fail_reason"]
    assert p1["invariant_digest"] == p2["invariant_digest"], (
        f"{key}: invariant_digest drift between run_1 and run_2"
    )


def test_tier6_must_negative_control_rejection() -> None:
    """validate_contract must reject mismatched req_id + payload."""
    bad_payload = {
        "step1_req_id": "REQ-NOT-IN-CLUSTER",
        "expected_fail_reason": "WHATEVER",
    }
    ok, errors = must_release_blocking_refs.validate_contract("REQ-NOT-IN-CLUSTER", bad_payload)
    assert not ok
    assert any("not in MUST STEP1_REQ_IDS" in e for e in errors)


# ---------------------------------------------------------------------------
# 15 NON_BLOCKING_REFERENCE rows: reference-only policy contract.
# ---------------------------------------------------------------------------


def _selection_row_for(req_id: str) -> dict:
    sel = json.loads(SELECTION.read_text(encoding="utf-8"))
    for row in sel["selected"]:
        if row["req_id"] == req_id:
            # Map selection schema to row shape expected by validator.
            return {
                "step1_req_id": row["req_id"],
                "source_matrix_file": row["source_matrix_file"],
                "release_gate_rule": row["release_gate_rule"],
                "requirement_strength": row["requirement_strength"],
            }
    raise AssertionError(f"req_id not in selection: {req_id}")


@pytest.mark.parametrize("req_id", REFERENCE_ONLY_REQ_IDS)
def test_tier6_reference_only_contract_validates(req_id: str) -> None:
    row = _selection_row_for(req_id)
    ok, errors = reference_only_policy_refs.validate_reference_only_contract(req_id, row)
    assert ok, f"{req_id} reference-only errors: {errors}"


def test_tier6_reference_only_contract_rejects_wrong_release_gate() -> None:
    rid = REFERENCE_ONLY_REQ_IDS[0]
    row = _selection_row_for(rid) | {"release_gate_rule": "RELEASE_BLOCKING"}
    ok, errors = reference_only_policy_refs.validate_reference_only_contract(rid, row)
    assert not ok
    assert any("NON_BLOCKING_REFERENCE" in e for e in errors)


def test_tier6_reference_only_contract_rejects_wrong_strength() -> None:
    rid = REFERENCE_ONLY_REQ_IDS[0]
    row = _selection_row_for(rid) | {"requirement_strength": "MUST"}
    ok, errors = reference_only_policy_refs.validate_reference_only_contract(rid, row)
    assert not ok
    assert any("REFERENCE" in e for e in errors)


# ---------------------------------------------------------------------------
# Reference-only policy artifact shape.
# ---------------------------------------------------------------------------


def test_tier6_reference_only_policy_artifact_shape() -> None:
    p = ARTIFACTS / "tier6_reference_only_policy.json"
    assert p.is_file(), "policy artifact must materialize from clean checkout"
    data = _load(p)
    assert data["tier"] == "TIER6"
    assert data["policy_name"] == "TIER6_NON_BLOCKING_REFERENCE_POLICY"
    assert data["total_reference_only_rows"] == 15
    assert sorted(data["reference_only_req_ids"]) == sorted(REFERENCE_ONLY_REQ_IDS)
    assert "runtime proof" in data["rule"].lower()
    assert "no real replay execution" in data["caveat"].lower()
    assert "no real otel emission" in data["caveat"].lower()
