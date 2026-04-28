"""Tier 4 cluster fixture tests — Prompt B.

Validates the AV..BT scenario+replay fixtures against their cluster's
static contract. Pure JSON inspection: no runtime, no proof harness,
no replay machinery, no OTEL exporter.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agentic_core.runtime.prove_requirements import tier_fixture_bootstrap
from agentic_core.runtime.prove_requirements.tier4_cluster_refs import (
    governance_state_refs,
    planning_routing_refs,
    execution_output_refs,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
TRACES = REPO_ROOT / "artifacts/runtime/requirements_proof/traces"
REPLAY = REPO_ROOT / "artifacts/runtime/requirements_proof/replay"

CLUSTER_BY_REQ_ID = {
    'REQ-L5-AUTHORITY-REGISTRY-BIND-001': governance_state_refs,
    'REQ-L5-RUNTIME-CERT-BIND-001': governance_state_refs,
    'REQ-L5-GUARDRAIL-FAMILIES-001': governance_state_refs,
    'REQ-L5-GOV-CONTEXT-INVARIANT-001': governance_state_refs,
    'REQ-UWG-DURABLE-WRITE-CTX-INVARIANT-001': governance_state_refs,
    'REQ-L4-POLICY-BLUEPRINT-STATE-001': governance_state_refs,
    'REQ-GATE-LAYER-INVOCATION-MAP-001': governance_state_refs,
    'REQ-U0-IDENTITY-TENANT-SESSION-001': planning_routing_refs,
    'REQ-U0-QUOTA-BASELINE-001': planning_routing_refs,
    'REQ-U0-SCHEMA-NORMALIZATION-001': planning_routing_refs,
    'REQ-L1-INTENT-FRAME-001': planning_routing_refs,
    'REQ-L1-PLANNING-PRIORS-001': planning_routing_refs,
    'REQ-L0-ROUTE-INPUT-PREFLIGHT-001': planning_routing_refs,
    'REQ-L0-CACHE-FALLBACK-HITL-001': planning_routing_refs,
    'REQ-L0-ROUTECONTRACT-TELEMETRY-001': planning_routing_refs,
    'REQ-L3-MANAGED-WORKFLOW-001': planning_routing_refs,
    'REQ-C0-RETRIEVAL-PLAN-001': execution_output_refs,
    'REQ-PA-LOAD-RESOLVE-BOM-001': execution_output_refs,
    'REQ-PA-TOKEN-BUDGET-DETERMINISM-001': execution_output_refs,
    'REQ-L2-E1-FROZEN-ROOM-001': execution_output_refs,
    'REQ-L2-E5-SEAL-DISPATCH-001': execution_output_refs,
    'REQ-L2-SEQUENCER-CONTRACT-001': execution_output_refs,
    'REQ-EXIT-HITL-FREEZE-001': execution_output_refs,
    'REQ-L6-RUNTIME-EXHAUST-INGEST-001': execution_output_refs,
    'REQ-E2E-EVIDENCE-GROUNDEDNESS-001': execution_output_refs,
}

SCENARIOS = [
    ('REQ-L5-AUTHORITY-REGISTRY-BIND-001', 'AV', 'l5_authority_registry_bind'),
    ('REQ-L5-RUNTIME-CERT-BIND-001', 'AW', 'l5_runtime_cert_bind'),
    ('REQ-L5-GUARDRAIL-FAMILIES-001', 'AX', 'l5_guardrail_families'),
    ('REQ-L5-GOV-CONTEXT-INVARIANT-001', 'AY', 'l5_gov_context_invariant'),
    ('REQ-UWG-DURABLE-WRITE-CTX-INVARIANT-001', 'AZ', 'uwg_durable_write_ctx_invariant'),
    ('REQ-L4-POLICY-BLUEPRINT-STATE-001', 'BA', 'l4_policy_blueprint_state'),
    ('REQ-GATE-LAYER-INVOCATION-MAP-001', 'BB', 'gate_layer_invocation_map'),
    ('REQ-U0-IDENTITY-TENANT-SESSION-001', 'BC', 'u0_identity_tenant_session'),
    ('REQ-U0-QUOTA-BASELINE-001', 'BD', 'u0_quota_baseline'),
    ('REQ-U0-SCHEMA-NORMALIZATION-001', 'BE', 'u0_schema_normalization'),
    ('REQ-L1-INTENT-FRAME-001', 'BF', 'l1_intent_frame'),
    ('REQ-L1-PLANNING-PRIORS-001', 'BG', 'l1_planning_priors'),
    ('REQ-L0-ROUTE-INPUT-PREFLIGHT-001', 'BH', 'l0_route_input_preflight'),
    ('REQ-L0-CACHE-FALLBACK-HITL-001', 'BI', 'l0_cache_fallback_hitl'),
    ('REQ-L0-ROUTECONTRACT-TELEMETRY-001', 'BJ', 'l0_routecontract_telemetry'),
    ('REQ-L3-MANAGED-WORKFLOW-001', 'BK', 'l3_managed_workflow'),
    ('REQ-C0-RETRIEVAL-PLAN-001', 'BL', 'c0_retrieval_plan'),
    ('REQ-PA-LOAD-RESOLVE-BOM-001', 'BM', 'pa_load_resolve_bom'),
    ('REQ-PA-TOKEN-BUDGET-DETERMINISM-001', 'BN', 'pa_token_budget_determinism'),
    ('REQ-L2-E1-FROZEN-ROOM-001', 'BO', 'l2_e1_frozen_room'),
    ('REQ-L2-E5-SEAL-DISPATCH-001', 'BP', 'l2_e5_seal_dispatch'),
    ('REQ-L2-SEQUENCER-CONTRACT-001', 'BQ', 'l2_sequencer_contract'),
    ('REQ-EXIT-HITL-FREEZE-001', 'BR', 'exit_hitl_freeze'),
    ('REQ-L6-RUNTIME-EXHAUST-INGEST-001', 'BS', 'l6_runtime_exhaust_ingest'),
    ('REQ-E2E-EVIDENCE-GROUNDEDNESS-001', 'BT', 'e2e_evidence_groundedness'),
]


@pytest.fixture(scope="module", autouse=True)
def _bootstrap() -> None:
    tier_fixture_bootstrap.materialize()


def _load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


@pytest.mark.parametrize("req_id,letters,slug", SCENARIOS)
def test_tier4_trace_fixture_validates(req_id: str, letters: str, slug: str) -> None:
    key = f"{letters}_{slug}"
    p = TRACES / f"scenario_{key}.json"
    assert p.is_file(), f"missing trace fixture: {p}"
    payload = _load(p)
    cluster = CLUSTER_BY_REQ_ID[req_id]
    ok, errors = cluster.validate_contract(req_id, payload)
    assert ok, f"{req_id} contract errors: {errors}"


@pytest.mark.parametrize("req_id,letters,slug", SCENARIOS)
def test_tier4_replay_pair_invariant_digest_matches(req_id: str, letters: str, slug: str) -> None:
    key = f"{letters}_{slug}"
    r1 = _load(REPLAY / f"replay_{key}_run_1.json")
    r2 = _load(REPLAY / f"replay_{key}_run_2.json")
    assert r1.get("step1_req_id") == req_id
    assert r2.get("step1_req_id") == req_id
    assert r1.get("invariant_digest") == r2.get("invariant_digest")
    assert r1.get("invariant_digest")


def test_tier4_clusters_total_25() -> None:
    total = (
        len(governance_state_refs.STEP1_REQ_IDS)
        + len(planning_routing_refs.STEP1_REQ_IDS)
        + len(execution_output_refs.STEP1_REQ_IDS)
    )
    assert total == 25, f"cluster total != 25 (got {total})"
