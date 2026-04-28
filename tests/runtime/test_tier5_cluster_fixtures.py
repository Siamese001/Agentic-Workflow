"""Tier 5 cluster fixture tests -- Prompt B.

Validates the BU..CS scenario+replay fixtures against their cluster's
static contract. Pure JSON inspection: no runtime, no proof harness,
no replay machinery, no OTEL exporter.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agentic_core.runtime.prove_requirements import tier_fixture_bootstrap
from agentic_core.runtime.prove_requirements.tier5_cluster_refs import (
    governance_migration_refs,
    planning_retrieval_prompt_refs,
    execution_evaluation_learning_refs,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
TRACES = REPO_ROOT / "artifacts/runtime/requirements_proof/traces"
REPLAY = REPO_ROOT / "artifacts/runtime/requirements_proof/replay"

CLUSTER_BY_REQ_ID = {
    'REQ-L5-CAPABILITY-TOKEN-SCHEMA-001': governance_migration_refs,
    'REQ-L5-CROSS-CHILD-CERT-CONSISTENCY-001': governance_migration_refs,
    'REQ-L5-CALIBRATION-ASSURANCE-001': governance_migration_refs,
    'REQ-L4-BLUEPRINT-VERSION-MIGRATION-001': governance_migration_refs,
    'REQ-L4-MEMORY-PROMOTION-STATE-001': governance_migration_refs,
    'REQ-L4-READ-SURFACE-REFRESH-001': governance_migration_refs,
    'REQ-U0-TRANSPORT-ENVELOPE-001': planning_retrieval_prompt_refs,
    'REQ-U0-DATA-LABELING-001': planning_retrieval_prompt_refs,
    'REQ-U0-REJECTION-PATH-001': planning_retrieval_prompt_refs,
    'REQ-L1-CONTEXTUAL-REFINEMENT-001': planning_retrieval_prompt_refs,
    'REQ-L1-DRAFT-PLAN-ROUTE-HINTS-001': planning_retrieval_prompt_refs,
    'REQ-L3-CONCURRENCY-FALLBACK-001': planning_retrieval_prompt_refs,
    'REQ-L3-STEP-READINESS-LEDGER-001': planning_retrieval_prompt_refs,
    'REQ-C0-SHAPE-RERANK-STRATIFY-001': planning_retrieval_prompt_refs,
    'REQ-PA-SLOT-COMPOSITION-001': planning_retrieval_prompt_refs,
    'REQ-L2-E2-VALID-WORK-ORDER-001': execution_evaluation_learning_refs,
    'REQ-L2-E3-EXEC-LANES-SANDBOX-001': execution_evaluation_learning_refs,
    'REQ-L2-E4-HEAL-SAME-AUTHORITY-001': execution_evaluation_learning_refs,
    'REQ-L2-RESOLUTION-CONTEXT-INVARIANT-001': execution_evaluation_learning_refs,
    'REQ-EXIT-INPUT-NORMALIZATION-001': execution_evaluation_learning_refs,
    'REQ-EXIT-GRADER-COMPOSITION-001': execution_evaluation_learning_refs,
    'REQ-EXIT-RETURN-RESPONSE-001': execution_evaluation_learning_refs,
    'REQ-L6-OUTCOME-TRAJECTORY-001': execution_evaluation_learning_refs,
    'REQ-L6-PROPOSAL-ADMISSION-001': execution_evaluation_learning_refs,
    'REQ-L6-MEMORY-PROMOTION-IFACE-001': execution_evaluation_learning_refs,
}

SCENARIOS = [
    ('REQ-L5-CAPABILITY-TOKEN-SCHEMA-001', 'BU', 'l5_capability_token_schema'),
    ('REQ-L5-CROSS-CHILD-CERT-CONSISTENCY-001', 'BV', 'l5_cross_child_cert_consistency'),
    ('REQ-L5-CALIBRATION-ASSURANCE-001', 'BW', 'l5_calibration_assurance'),
    ('REQ-L4-BLUEPRINT-VERSION-MIGRATION-001', 'BX', 'l4_blueprint_version_migration'),
    ('REQ-L4-MEMORY-PROMOTION-STATE-001', 'BY', 'l4_memory_promotion_state'),
    ('REQ-L4-READ-SURFACE-REFRESH-001', 'BZ', 'l4_read_surface_refresh'),
    ('REQ-U0-TRANSPORT-ENVELOPE-001', 'CA', 'u0_transport_envelope'),
    ('REQ-U0-DATA-LABELING-001', 'CB', 'u0_data_labeling'),
    ('REQ-U0-REJECTION-PATH-001', 'CC', 'u0_rejection_path'),
    ('REQ-L1-CONTEXTUAL-REFINEMENT-001', 'CD', 'l1_contextual_refinement'),
    ('REQ-L1-DRAFT-PLAN-ROUTE-HINTS-001', 'CE', 'l1_draft_plan_route_hints'),
    ('REQ-L3-CONCURRENCY-FALLBACK-001', 'CF', 'l3_concurrency_fallback'),
    ('REQ-L3-STEP-READINESS-LEDGER-001', 'CG', 'l3_step_readiness_ledger'),
    ('REQ-C0-SHAPE-RERANK-STRATIFY-001', 'CH', 'c0_shape_rerank_stratify'),
    ('REQ-PA-SLOT-COMPOSITION-001', 'CI', 'pa_slot_composition'),
    ('REQ-L2-E2-VALID-WORK-ORDER-001', 'CJ', 'l2_e2_valid_work_order'),
    ('REQ-L2-E3-EXEC-LANES-SANDBOX-001', 'CK', 'l2_e3_exec_lanes_sandbox'),
    ('REQ-L2-E4-HEAL-SAME-AUTHORITY-001', 'CL', 'l2_e4_heal_same_authority'),
    ('REQ-L2-RESOLUTION-CONTEXT-INVARIANT-001', 'CM', 'l2_resolution_context_invariant'),
    ('REQ-EXIT-INPUT-NORMALIZATION-001', 'CN', 'exit_input_normalization'),
    ('REQ-EXIT-GRADER-COMPOSITION-001', 'CO', 'exit_grader_composition'),
    ('REQ-EXIT-RETURN-RESPONSE-001', 'CP', 'exit_return_response'),
    ('REQ-L6-OUTCOME-TRAJECTORY-001', 'CQ', 'l6_outcome_trajectory'),
    ('REQ-L6-PROPOSAL-ADMISSION-001', 'CR', 'l6_proposal_admission'),
    ('REQ-L6-MEMORY-PROMOTION-IFACE-001', 'CS', 'l6_memory_promotion_iface'),
]


@pytest.fixture(scope="module", autouse=True)
def _bootstrap() -> None:
    tier_fixture_bootstrap.materialize()


def _load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


@pytest.mark.parametrize("req_id,letters,slug", SCENARIOS)
def test_tier5_trace_fixture_validates(req_id: str, letters: str, slug: str) -> None:
    key = f"{letters}_{slug}"
    p = TRACES / f"scenario_{key}.json"
    assert p.is_file(), f"missing trace fixture: {p}"
    payload = _load(p)
    cluster = CLUSTER_BY_REQ_ID[req_id]
    ok, errors = cluster.validate_contract(req_id, payload)
    assert ok, f"{req_id} contract errors: {errors}"


@pytest.mark.parametrize("req_id,letters,slug", SCENARIOS)
def test_tier5_replay_pair_invariant_digest_matches(req_id: str, letters: str, slug: str) -> None:
    key = f"{letters}_{slug}"
    r1 = _load(REPLAY / f"replay_{key}_run_1.json")
    r2 = _load(REPLAY / f"replay_{key}_run_2.json")
    assert r1.get("step1_req_id") == req_id
    assert r2.get("step1_req_id") == req_id
    assert r1.get("invariant_digest") == r2.get("invariant_digest")
    assert r1.get("invariant_digest")


def test_tier5_clusters_total_25() -> None:
    total = (
        len(governance_migration_refs.STEP1_REQ_IDS)
        + len(planning_retrieval_prompt_refs.STEP1_REQ_IDS)
        + len(execution_evaluation_learning_refs.STEP1_REQ_IDS)
    )
    assert total == 25, f"cluster total != 25 (got {total})"
