"""Deterministic acceptance tests for the fee-adjustment mechanics lab.

These tests assert the runtime mechanics that the lab teaches:
  - exactly one X3 per Exit evaluation,
  - L2 never writes durable state,
  - HITL is only entered through Exit,
  - UWG is the only path to L4,
  - L6 only after the run boundary,
  - UNKNOWN never passes,
  - replay reproduces the exact same trace.
"""

from __future__ import annotations

import json
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from src.runtime import run_workflow  # noqa: E402
from src.runtime.contracts import GateVerdict, to_jsonable  # noqa: E402


def _stage_ids(trace) -> list[str]:
    return [r.stage_id for r in trace.stage_receipts]


# --- One workflow, three scenarios reach their expected terminal path ----------
def test_scenario_a_reaches_uwg_and_l4():
    t = run_workflow("A")
    assert t.final_exit == "X3C_COMMIT_REQUEST_TO_UWG"
    assert t.uwg_validation_result is not None and t.uwg_validation_result.approved
    assert t.l4_archive_record is not None
    assert "L4" in _stage_ids(t)


def test_scenario_b_escalates_then_commits_on_approval():
    pending = run_workflow("B", None)
    assert pending.final_exit == "X3B_ESCALATE_HITL"
    assert pending.l4_archive_record is None
    assert pending.runtime_exhaust_bundle["awaiting_reviewer"] is True
    assert "HITL" not in _stage_ids(pending)  # no reviewer decision yet

    approved = run_workflow("B", "approve")
    assert "HITL" in _stage_ids(approved)
    assert "RECLEAR" in _stage_ids(approved)
    assert approved.final_exit == "X3C_COMMIT_REQUEST_TO_UWG"
    assert approved.l4_archive_record is not None
    # Two Exit evaluations: initial escalate + re-clearance commit.
    assert [e["x3"] for e in approved.exit_disposition_history] == [
        "X3B_ESCALATE_HITL",
        "X3C_COMMIT_REQUEST_TO_UWG",
    ]


@pytest.mark.parametrize(
    "decision,expected_exit",
    [
        ("reject", "X3A_DENY_REROUTE"),
        ("request_more_evidence", "X3E_SAFE_ABSTAIN"),
        ("escalate_further", "X3B_ESCALATE_HITL"),
    ],
)
def test_scenario_b_non_approval_does_not_write(decision, expected_exit):
    t = run_workflow("B", decision)
    assert t.final_exit == expected_exit
    assert t.l4_archive_record is None
    assert t.uwg_validation_result is None


def test_scenario_c_abstains_and_does_not_write():
    t = run_workflow("C")
    assert t.final_exit == "X3E_SAFE_ABSTAIN"
    assert t.l4_archive_record is None
    assert t.uwg_validation_result is None
    # E4 same-authority repair only happens in Scenario C.
    assert "L2.E4" in _stage_ids(t)
    assert t.heal_receipt is not None
    assert t.heal_receipt["same_authority"] is True


# --- Spine invariants ----------------------------------------------------------
def test_l2_never_writes_durable_state():
    for sid in ("A", "B", "C"):
        t = run_workflow(sid)
        seal = t.l2_execution_artifact["seal_receipt"]
        assert seal["durable_write_performed"] is False


def test_hitl_only_entered_through_exit_x3b():
    # A and C never escalate, so HITL must never appear.
    for sid in ("A", "C"):
        t = run_workflow(sid)
        assert "HITL" not in _stage_ids(t)
        assert t.reviewer_decision is None


def test_uwg_is_only_path_to_l4():
    for sid, dec in [("A", None), ("B", "approve")]:
        t = run_workflow(sid, dec)
        assert t.l4_archive_record is not None
        assert t.uwg_validation_result is not None
        assert t.l4_archive_record.created_by == "UWG_APPROVED_COMMIT"
    # No UWG -> no L4.
    for sid, dec in [("C", None), ("B", "reject")]:
        t = run_workflow(sid, dec)
        assert t.uwg_validation_result is None
        assert t.l4_archive_record is None


def test_l6_only_after_run_boundary():
    # B awaiting reviewer: boundary not reached -> no L6.
    assert run_workflow("B", None).l6_post_run_evaluation is None
    # Completed runs: L6 present and inert.
    for sid, dec in [("A", None), ("C", None), ("B", "approve"), ("B", "reject")]:
        t = run_workflow(sid, dec)
        assert t.l6_post_run_evaluation is not None
        assert t.l6_post_run_evaluation["boundary"] == "after_current_run"


def test_exit_emits_exactly_one_x3_per_evaluation():
    for sid, dec in [("A", None), ("B", None), ("B", "approve"), ("C", None)]:
        t = run_workflow(sid, dec)
        for ev in t.exit_disposition_history:
            assert isinstance(ev["x3"], str) and ev["x3"].startswith("X3")


def test_unknown_is_never_pass():
    for sid, dec in [("A", None), ("B", None), ("B", "approve"), ("C", None)]:
        t = run_workflow(sid, dec)
        verdicts = set(t.gate_verdicts.values())
        assert GateVerdict.UNKNOWN.value not in verdicts
        assert t.runtime_exhaust_bundle["unknown_present"] is False


# --- Determinism / replay ------------------------------------------------------
@pytest.mark.parametrize("sid,dec", [("A", None), ("B", "approve"), ("C", None)])
def test_replay_reproduces_exact_trace(sid, dec):
    a = json.dumps(to_jsonable(run_workflow(sid, dec)), sort_keys=True)
    b = json.dumps(to_jsonable(run_workflow(sid, dec)), sort_keys=True)
    assert a == b


def test_evidence_packet_has_required_items():
    required = {
        "EV-FEE-EVENT",
        "EV-PRODUCT-RULE",
        "EV-FEE-POLICY",
        "EV-ACTIVITY",
        "EV-PRIOR-NOTES",
        "EV-ADJ-LEDGER",
        "EV-COMPLAINT",
        "EV-COMMS",
    }
    for sid in ("A", "B", "C"):
        ids = {e.id for e in run_workflow(sid).evidence_packet}
        assert required.issubset(ids)


def test_customer_narrative_is_data_not_authority():
    for sid in ("A", "B", "C"):
        t = run_workflow(sid)
        assert "customer_message" in t.prompt_boundary_check["data"]
        assert "customer_message" not in t.prompt_boundary_check["authority"]


# --- C0 retrieval / evidence custody ------------------------------------------
def test_c0_custody_sequence_pipeline_and_candidates():
    expected_pipeline = [
        "candidate_sources",
        "acl_check",
        "freshness_check",
        "contradiction_check",
        "support_classification",
        "final_evidence_packet",
    ]
    expected_sources = {
        "posted_fee_event_ledger",
        "fee_policy",
        "product_rule",
        "prior_servicing_notes",
        "adjustment_ledger",
        "customer_message",
        "complaint_indicator",
    }
    for sid in ("A", "B", "C"):
        cust = run_workflow(sid).c0_custody_sequence
        assert cust["pipeline"] == expected_pipeline
        ids = {c["source_id"] for c in cust["candidates"]}
        assert ids == expected_sources
        required_fields = {
            "source_id", "retrieved", "acl_status", "freshness", "quality_state",
            "contradiction_status", "authority_level", "included_in_final_packet",
            "exclusion_reason", "can_support_write",
        }
        for c in cust["candidates"]:
            assert required_fields.issubset(c.keys())


def test_customer_message_excluded_from_final_packet():
    for sid in ("A", "B", "C"):
        cust = run_workflow(sid).c0_custody_sequence
        msg = next(c for c in cust["candidates"] if c["source_id"] == "customer_message")
        assert msg["included_in_final_packet"] is False
        assert msg["exclusion_reason"]
        assert msg["can_support_write"] is False


def test_c0_outputs_final_evidence_contract_consumed_by_pa():
    for sid in ("A", "B", "C"):
        t = run_workflow(sid)
        fec = t.final_evidence_contract
        assert fec["consumed_by"] == "PA"
        assert fec["contract_id"] == f"FEC-{sid}"


def test_scenario_c_custody_marks_conflict():
    cust = run_workflow("C").c0_custody_sequence
    assert "adjustment_ledger" in cust["conflicted_sources"]
    assert "prior_servicing_notes" in cust["conflicted_sources"]
    assert cust["support_classification"] == "CONFLICTED"


# --- Exit evaluation checks ----------------------------------------------------
def test_exit_checks_present_and_exactly_one_x3():
    for sid, dec in [("A", None), ("B", None), ("B", "approve"), ("C", None)]:
        t = run_workflow(sid, dec)
        for e in t.exit_disposition_history:
            checks = e["exit_checks"]["checks"]
            assert checks["exactly_one_x3"] == "true"
            assert "LLM" in e["exit_checks"]["evaluator"]  # documents no-LLM evaluator


def test_exit_write_eligible_only_when_appropriate():
    # A: no complaint, diff present -> write eligible.
    assert run_workflow("A").exit_disposition_history[0]["exit_checks"]["checks"]["write_eligible"] == "true"
    # B initial (no reviewer): reviewer required, not yet approved -> not write eligible.
    b_initial = run_workflow("B", None).exit_disposition_history[0]["exit_checks"]["checks"]
    assert b_initial["write_eligible"] == "false"
    assert b_initial["reviewer_required"] == "true"
    # B after approval re-clearance -> write eligible.
    b_approved = run_workflow("B", "approve").exit_disposition_history[-1]["exit_checks"]["checks"]
    assert b_approved["write_eligible"] == "true"
    # C: conflict unresolved -> not write eligible.
    c_checks = run_workflow("C").exit_disposition_history[0]["exit_checks"]["checks"]
    assert c_checks["conflict_unresolved"] == "true"
    assert c_checks["write_eligible"] == "false"


# --- UWG validation checks -----------------------------------------------------
def test_uwg_checks_full_table_and_reviewer_authority():
    # A: no HITL -> reviewer_authority absent.
    a = run_workflow("A").uwg_validation_result
    assert "reviewer_authority" not in a.checks
    required = {
        "commit_request_complete", "proposed_state_diff_complete", "route_compatibility",
        "policy_fit", "evidence_sufficiency", "reason_code_present",
        "replay_audit_complete", "write_lock",
    }
    assert required.issubset(a.checks.keys())
    assert a.approved is True

    # B approved: HITL occurred -> reviewer_authority present and true.
    b = run_workflow("B", "approve").uwg_validation_result
    assert b.checks["reviewer_authority"] == "true"
    assert b.approved is True
