"""D6 — Eval harness RAG dims wire-up tests.

Validates that:
  1. The 3 RAG eval dims (context_recall, context_precision, answer_relevancy)
     in eval_rubrics.yaml have fail_closed_if_unknown: true (flipped from
     intentional_failopen per D6).
  2. All 8 dims in the rubric have fail_closed_if_unknown declared.
  3. The E2E exit bundle exposes final_evidence_contract so downstream
     RAG dim producers can consume it.

Plan: apps-underwriting-ai-deferred-scope-e8b2f4 D6.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
RUBRIC_PATH = (
    REPO_ROOT
    / "apps_underwriting_ai"
    / "config"
    / "domain_contract"
    / "eval_rubrics.yaml"
)
FIXTURE_DIR = REPO_ROOT / "apps_underwriting_ai" / "fixtures"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from apps_underwriting_ai.integrations.underwriting_exit_fec_producer import (
    UnderwritingExitFecProducer,
)

_RAG_DIM_IDS = {"context_recall", "context_precision", "answer_relevancy"}


def _load_rubric() -> list[dict]:
    data = yaml.safe_load(RUBRIC_PATH.read_text(encoding="utf-8"))
    assert isinstance(data, list) and len(data) == 1, "Expected 1 rubric entry"
    return data[0]["score_dimensions"]


# ---------------------------------------------------------------------------
# D6.1 — RAG dims have fail_closed_if_unknown: true
# ---------------------------------------------------------------------------

@pytest.mark.governance
@pytest.mark.parametrize("dim_id", sorted(_RAG_DIM_IDS))
def test_rag_dim_fail_closed_if_unknown(dim_id: str) -> None:
    """RAG dim must have fail_closed_if_unknown: true post D6 flip."""
    dims = _load_rubric()
    dim_map = {d["dimension_id"]: d for d in dims}
    assert dim_id in dim_map, f"RAG dim {dim_id!r} missing from eval_rubrics.yaml"
    dim = dim_map[dim_id]
    assert dim.get("fail_closed_if_unknown") is True, (
        f"RAG dim {dim_id!r} must have fail_closed_if_unknown: true (D6 flip); "
        f"got {dim.get('fail_closed_if_unknown')!r}"
    )


# ---------------------------------------------------------------------------
# D6.2 — all 8 dims declare fail_closed_if_unknown
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_all_dims_declare_fail_closed_if_unknown() -> None:
    """Every dimension in the rubric must declare fail_closed_if_unknown."""
    dims = _load_rubric()
    missing = [
        d["dimension_id"]
        for d in dims
        if "fail_closed_if_unknown" not in d
    ]
    assert not missing, (
        f"Dims missing fail_closed_if_unknown declaration: {sorted(missing)}"
    )


# ---------------------------------------------------------------------------
# D6.3 — exit bundle exposes final_evidence_contract for RAG dim producers
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_exit_bundle_exposes_final_evidence_contract_for_rag_producers() -> None:
    """produce_exit_bundle() must include final_evidence_contract in the result."""
    fec = {
        "c0_mode": "SUBMITTED_DOCUMENT_EVIDENCE_ONLY",
        "c0_state": "PASS",
        "evidence_ids": ["doc-001", "doc-002"],
        "support_score": 0.91,
        "evidence_sufficiency": "sufficient",
    }
    ctx = {
        "demo_policy_hash": "sha256-policy-test",
        "blueprint_hash": "sha256-blueprint-test",
        "route_contract": {"route_family": "R3R4_MANAGED_WORKFLOW"},
        "verdict": "APPROVE",
        "reason_code_bundle": ["RC000_CREDIT_SCORE_STRONG"],
        "hitl_posture": "HITL_NONE",
        "demo_packet_id": "d6-test-001",
    }
    producer = UnderwritingExitFecProducer()
    bundle = producer.produce_exit_bundle(fec, ctx)
    assert "final_evidence_contract" in bundle, (
        "Exit bundle must include 'final_evidence_contract' for RAG dim producers. "
        f"Keys present: {sorted(bundle.keys())}"
    )
    fec_in_bundle = bundle["final_evidence_contract"]
    assert isinstance(fec_in_bundle, dict), (
        f"final_evidence_contract must be a dict; got {type(fec_in_bundle)}"
    )
    assert "evidence_ids" in fec_in_bundle, (
        "final_evidence_contract must carry 'evidence_ids' for RAG dim producers."
    )
