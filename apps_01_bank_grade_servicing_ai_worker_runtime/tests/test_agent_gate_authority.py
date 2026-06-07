"""The keystone property: the deterministic control plane is authoritative.

The L2 worker is the least-trusted component. These tests prove that a WRONG
model recommendation, or an UNKNOWN (fail-closed) worker, can never change the
disposition or cause a durable write. The gate decides on evidence, not the
model's word.
"""

from __future__ import annotations

import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from src.runtime import run_workflow  # noqa: E402
from src.runtime.agent import AgentDecision  # noqa: E402


def _injected(recommendation, *, is_unknown=False):
    return AgentDecision(
        recommendation=recommendation,
        rationale="(injected for test)",
        complaint_sensitive=False,
        evidence_conflicted=False,
        proposed_state_diff=None,
        is_unknown=is_unknown,
        provenance={"source": "injected"},
    )


# --- The model recommendation is recorded but untrusted ------------------------
def test_model_gate_agreement_recorded_and_agrees_on_recorded_fixtures():
    expected = {"A": "approve", "B": "escalate", "C": "hold"}
    for sid, bucket in expected.items():
        t = run_workflow(sid, "approve" if sid == "B" else None)
        mga = t.model_gate_agreement
        assert mga is not None
        assert mga["gate_expectation"] == bucket
        assert mga["model_bucket"] == bucket
        assert mga["agreement"] is True
        # The real model decision is on the trace with provenance.
        assert t.l2_agent_decision["provenance"]["source"] == "replay"


# --- Gate overrides a WRONG model ---------------------------------------------
def test_gate_overrides_model_that_wrongly_approves_a_conflicted_case(monkeypatch):
    # Model wrongly says "approve" on the conflicted case (C).
    monkeypatch.setattr(
        "src.runtime.engine.decide",
        lambda scn: _injected("approve_courtesy_adjustment"),
    )
    t = run_workflow("C")
    # The gate still abstains. The wrong model changed nothing.
    assert t.final_exit == "X3E_SAFE_ABSTAIN"
    assert t.l4_archive_record is None
    assert t.uwg_validation_result is None
    assert t.model_gate_agreement["agreement"] is False
    assert t.model_gate_agreement["model_bucket"] == "approve"
    assert t.model_gate_agreement["gate_expectation"] == "hold"


def test_gate_overrides_model_that_wrongly_approves_a_complaint_case(monkeypatch):
    # Model wrongly says "approve" on the complaint-sensitive case (B), no reviewer.
    monkeypatch.setattr(
        "src.runtime.engine.decide",
        lambda scn: _injected("approve_courtesy_adjustment"),
    )
    t = run_workflow("B", None)
    # The gate still escalates to a human. No write.
    assert t.final_exit == "X3B_ESCALATE_HITL"
    assert t.l4_archive_record is None
    assert t.model_gate_agreement["agreement"] is False


# --- UNKNOWN worker fails closed ----------------------------------------------
def test_unknown_worker_never_auto_commits_a_clean_case(monkeypatch):
    # Even a clean case (A): if the worker fails, we do NOT auto-commit.
    monkeypatch.setattr(
        "src.runtime.engine.decide",
        lambda scn: _injected(None, is_unknown=True),
    )
    t = run_workflow("A")
    assert t.final_exit == "X3B_ESCALATE_HITL"  # escalate to human, not commit
    assert t.l4_archive_record is None
    # UNKNOWN surfaces at the L2 stage gate and in the exhaust bundle.
    assert t.gate_verdicts["L2"] == "UNKNOWN"
    assert t.runtime_exhaust_bundle["unknown_present"] is True
    assert t.model_gate_agreement["model_is_unknown"] is True


# --- A correct model still cannot bypass the write gate ------------------------
def test_correct_model_still_routes_through_uwg_only(monkeypatch):
    # Model correctly approves the clean case, but the durable write still only
    # happens via UWG -> L4, never directly from L2.
    monkeypatch.setattr(
        "src.runtime.engine.decide",
        lambda scn: _injected("approve_courtesy_adjustment"),
    )
    t = run_workflow("A")
    assert t.final_exit == "X3C_COMMIT_REQUEST_TO_UWG"
    assert t.l2_execution_artifact["seal_receipt"]["durable_write_performed"] is False
    assert t.uwg_validation_result is not None and t.uwg_validation_result.approved
    assert t.l4_archive_record.created_by == "UWG_APPROVED_COMMIT"
