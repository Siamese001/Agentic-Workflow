"""
Phase 7 -- anti-bypass negative controls.

A registry of 30 named mutators. Each takes a clean, validation-passing
scenario trace and corrupts ONE invariant. The Phase 7 test then runs
``validate_trace_full(mutated_trace, scenario)`` and asserts at least one
detector fires. If a mutator's bypass goes UNDETECTED, the test fails --
which means a real attacker could exploit that gap.

The mutators are grouped by attack surface:

  Structural (parent / root / cycle):    M01..M06
  Schema (required, conditional, status, vocab): M07..M13
  Trace identity (uuid drift):           M14..M16
  Scenario A invariants:                 M17..M19
  Scenario B invariants:                 M20..M21
  Scenario C invariants:                 M22..M23
  Scenario D invariants:                 M24..M27
  Replay-determinism (silent drift):     M28..M30
"""

from __future__ import annotations

import copy
import uuid
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Tuple


@dataclass(frozen=True)
class Negative:
    """One named bypass attempt."""

    code: str            # M01, M02, ...
    name: str            # short human-readable label
    scenario: str        # which scenario this mutator applies to
    description: str
    mutator: Callable[[Dict[str, Any]], Dict[str, Any]]


def _clone(trace: Dict[str, Any]) -> Dict[str, Any]:
    return copy.deepcopy(trace)


# ---------------------------------------------------------------------------
# Structural mutators
# ---------------------------------------------------------------------------

def _m01_remove_root(trace: Dict[str, Any]) -> Dict[str, Any]:
    t = _clone(trace)
    t["spans"] = [s for s in t["spans"] if s["name"] != "runtime.request"]
    return t


def _m02_two_roots(trace: Dict[str, Any]) -> Dict[str, Any]:
    t = _clone(trace)
    for s in t["spans"]:
        if s["name"] == "u0.intake":
            s["parent_span_id"] = ""
            break
    return t


def _m03_unresolvable_parent(trace: Dict[str, Any]) -> Dict[str, Any]:
    t = _clone(trace)
    for s in t["spans"]:
        if s["name"] == "exit.x1.gates":
            s["parent_span_id"] = "ffffffffffffffff"
            break
    return t


def _m04_zero_spans(trace: Dict[str, Any]) -> Dict[str, Any]:
    t = _clone(trace)
    t["spans"] = []
    return t


def _m05_self_parent(trace: Dict[str, Any]) -> Dict[str, Any]:
    t = _clone(trace)
    for s in t["spans"]:
        if s["name"] == "l2.e3.exec":
            s["parent_span_id"] = s["span_id"]
            break
    return t


def _m06_drop_required_intake(trace: Dict[str, Any]) -> Dict[str, Any]:
    t = _clone(trace)
    t["spans"] = [s for s in t["spans"] if s["name"] != "u0.intake"]
    return t


# ---------------------------------------------------------------------------
# Schema mutators
# ---------------------------------------------------------------------------

def _m07_missing_required_status(trace: Dict[str, Any]) -> Dict[str, Any]:
    t = _clone(trace)
    for s in t["spans"]:
        if s["name"] == "u0.intake":
            del s["status"]
            break
    return t


def _m08_missing_required_latency(trace: Dict[str, Any]) -> Dict[str, Any]:
    t = _clone(trace)
    for s in t["spans"]:
        if s["name"] == "l2.e3.exec":
            del s["latency_ms"]
            break
    return t


def _m09_missing_conditional_route_id_key(trace: Dict[str, Any]) -> Dict[str, Any]:
    t = _clone(trace)
    for s in t["spans"]:
        if s["name"] == "exit.x3.disposition":
            del s["route_id"]
            break
    return t


def _m10_invalid_status_value(trace: Dict[str, Any]) -> Dict[str, Any]:
    t = _clone(trace)
    for s in t["spans"]:
        if s["name"] == "l2.e3.exec":
            s["status"] = "YOLO"
            break
    return t


def _m11_unknown_span_name(trace: Dict[str, Any]) -> Dict[str, Any]:
    t = _clone(trace)
    # Inject a clone of u0.intake but with a forbidden name
    if t["spans"]:
        evil = _clone(t["spans"][0])
        evil["name"] = "evil.bypass"
        evil["span_id"] = uuid.uuid4().hex[:16]
        t["spans"].append(evil)
    return t


def _m12_missing_request_id(trace: Dict[str, Any]) -> Dict[str, Any]:
    t = _clone(trace)
    for s in t["spans"]:
        if s["name"] == "l1.plan":
            del s["request_id"]
            break
    return t


def _m13_missing_run_id(trace: Dict[str, Any]) -> Dict[str, Any]:
    t = _clone(trace)
    for s in t["spans"]:
        if s["name"] == "l0.route_decision":
            del s["run_id"]
            break
    return t


# ---------------------------------------------------------------------------
# Trace-identity drift
# ---------------------------------------------------------------------------

def _m14_drift_trace_id(trace: Dict[str, Any]) -> Dict[str, Any]:
    t = _clone(trace)
    if t["spans"]:
        t["spans"][0]["trace_id"] = "ff" * 16
    return t


def _m15_drift_request_id(trace: Dict[str, Any]) -> Dict[str, Any]:
    t = _clone(trace)
    if len(t["spans"]) >= 2:
        t["spans"][1]["request_id"] = "req-evil"
    return t


def _m16_drift_run_id(trace: Dict[str, Any]) -> Dict[str, Any]:
    t = _clone(trace)
    if len(t["spans"]) >= 3:
        t["spans"][2]["run_id"] = "run-evil"
    return t


# ---------------------------------------------------------------------------
# Scenario A invariants (no L3, no UWG, no weak-refinement, no HITL)
# ---------------------------------------------------------------------------

def _m17_a_emit_l3(trace: Dict[str, Any]) -> Dict[str, Any]:
    t = _clone(trace)
    if t["spans"]:
        evil = _clone(t["spans"][0])
        evil.update(name="l3.workflow_start", span_id=uuid.uuid4().hex[:16])
        t["spans"].append(evil)
    return t


def _m18_a_emit_uwg_commit(trace: Dict[str, Any]) -> Dict[str, Any]:
    t = _clone(trace)
    if t["spans"]:
        ev = _clone(t["spans"][0])
        ev.update(name="uwg.commit_request", span_id=uuid.uuid4().hex[:16])
        t["spans"].append(ev)
        ev2 = _clone(t["spans"][0])
        ev2.update(name="uwg.commit_receipt", span_id=uuid.uuid4().hex[:16])
        t["spans"].append(ev2)
    return t


def _m19_a_emit_hitl_packet(trace: Dict[str, Any]) -> Dict[str, Any]:
    t = _clone(trace)
    if t["spans"]:
        ev = _clone(t["spans"][0])
        ev.update(name="hitl.packetization", span_id=uuid.uuid4().hex[:16])
        t["spans"].append(ev)
    return t


# ---------------------------------------------------------------------------
# Scenario B invariants (must have L3, must NOT commit)
# ---------------------------------------------------------------------------

def _m20_b_drop_l3_workflow(trace: Dict[str, Any]) -> Dict[str, Any]:
    t = _clone(trace)
    t["spans"] = [s for s in t["spans"] if s["name"] != "l3.workflow_start"]
    return t


def _m21_b_emit_uwg_commit_receipt(trace: Dict[str, Any]) -> Dict[str, Any]:
    t = _clone(trace)
    if t["spans"]:
        ev = _clone(t["spans"][0])
        ev.update(name="uwg.commit_receipt", span_id=uuid.uuid4().hex[:16])
        t["spans"].append(ev)
    return t


# ---------------------------------------------------------------------------
# Scenario C invariants (weak-refinement required, weak-reason required)
# ---------------------------------------------------------------------------

def _m22_c_drop_weak_refinement(trace: Dict[str, Any]) -> Dict[str, Any]:
    t = _clone(trace)
    t["spans"] = [s for s in t["spans"] if s["name"] != "c0.6.weak_support_refinement"]
    return t


def _m23_c_strip_weak_reason(trace: Dict[str, Any]) -> Dict[str, Any]:
    t = _clone(trace)
    for s in t["spans"]:
        if s["name"] == "c0.5.final_evidence_contract":
            s["reason_codes"] = []
            break
    return t


# ---------------------------------------------------------------------------
# Scenario D invariants (HITL required, no UWG receipt, status=BLOCKED)
# ---------------------------------------------------------------------------

def _m24_d_drop_hitl(trace: Dict[str, Any]) -> Dict[str, Any]:
    t = _clone(trace)
    t["spans"] = [s for s in t["spans"] if s["name"] != "hitl.packetization"]
    return t


def _m25_d_emit_uwg_commit_receipt(trace: Dict[str, Any]) -> Dict[str, Any]:
    t = _clone(trace)
    if t["spans"]:
        ev = _clone(t["spans"][0])
        ev.update(name="uwg.commit_receipt", span_id=uuid.uuid4().hex[:16])
        t["spans"].append(ev)
    return t


def _m26_d_set_exit_status_ok(trace: Dict[str, Any]) -> Dict[str, Any]:
    t = _clone(trace)
    for s in t["spans"]:
        if s["name"] == "exit.x3.disposition":
            s["status"] = "OK"
            break
    return t


def _m27_d_set_exit_status_abstain(trace: Dict[str, Any]) -> Dict[str, Any]:
    t = _clone(trace)
    for s in t["spans"]:
        if s["name"] == "exit.x3.disposition":
            s["status"] = "ABSTAINED"
            break
    return t


# ---------------------------------------------------------------------------
# Replay-determinism mutators (silent field drift)
# ---------------------------------------------------------------------------

def _m28_drift_policy_hash(trace: Dict[str, Any]) -> Dict[str, Any]:
    t = _clone(trace)
    for s in t["spans"]:
        if s["name"] == "u0.intake":
            s["policy_hash"] = "0" * 16
            break
    return t


def _m29_drift_contract_digest(trace: Dict[str, Any]) -> Dict[str, Any]:
    t = _clone(trace)
    for s in t["spans"]:
        if s["name"] == "l2.e5.seal":
            s["contract_digest"] = "0" * 16
            break
    return t


def _m30_drift_reason_codes(trace: Dict[str, Any]) -> Dict[str, Any]:
    t = _clone(trace)
    for s in t["spans"]:
        if s["name"] == "exit.x3.disposition":
            s["reason_codes"] = ["BYPASSED"]
            break
    return t


# ---------------------------------------------------------------------------
# Scenario E mutators (positive-commit path bypasses)
# ---------------------------------------------------------------------------

def _m31_e_drop_commit_request(trace: Dict[str, Any]) -> Dict[str, Any]:
    """Strip commit_request -- if commit_receipt remains, it is orphaned."""
    t = _clone(trace)
    t["spans"] = [s for s in t["spans"] if s["name"] != "uwg.commit_request"]
    return t


def _m32_e_drop_commit_receipt(trace: Dict[str, Any]) -> Dict[str, Any]:
    """Strip commit_receipt -- the commit is now silently incomplete.
    Scenario E shape validator must catch the missing required span."""
    t = _clone(trace)
    t["spans"] = [s for s in t["spans"] if s["name"] != "uwg.commit_receipt"]
    return t


def _m33_e_strip_allow_commit_marker(trace: Dict[str, Any]) -> Dict[str, Any]:
    """Remove ALLOW_COMMIT from x3 reason_codes -- commit becomes
    unauthorized (orphan commit_request without authorization)."""
    t = _clone(trace)
    for s in t["spans"]:
        if s["name"] == "exit.x3.disposition":
            s["reason_codes"] = [r for r in (s.get("reason_codes") or [])
                                 if "ALLOW_COMMIT" not in r]
            break
    return t


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

# All four scenarios are eligible inputs; mutators specific to a scenario
# state which scenario they target via the `scenario` field. Generic
# mutators target scenario A as a stable canonical baseline.

NEGATIVES: Tuple[Negative, ...] = (
    Negative("M01", "remove_root", "A_grounded_read", "Strip the runtime.request root entirely.", _m01_remove_root),
    Negative("M02", "two_roots", "A_grounded_read", "Make u0.intake a second root.", _m02_two_roots),
    Negative("M03", "unresolvable_parent", "A_grounded_read", "Point exit.x1.gates parent at a non-existent span.", _m03_unresolvable_parent),
    Negative("M04", "zero_spans", "A_grounded_read", "Empty the spans array entirely.", _m04_zero_spans),
    Negative("M05", "self_parent", "A_grounded_read", "Make l2.e3.exec its own parent (cycle).", _m05_self_parent),
    Negative("M06", "drop_required_intake", "A_grounded_read", "Remove u0.intake entirely.", _m06_drop_required_intake),
    Negative("M07", "missing_status", "A_grounded_read", "Delete the status field on u0.intake.", _m07_missing_required_status),
    Negative("M08", "missing_latency", "A_grounded_read", "Delete latency_ms on l2.e3.exec.", _m08_missing_required_latency),
    Negative("M09", "missing_route_id_key", "A_grounded_read", "Delete the route_id KEY on exit.x3 (not just set None).", _m09_missing_conditional_route_id_key),
    Negative("M10", "invalid_status_value", "A_grounded_read", "Set status=YOLO on l2.e3.exec.", _m10_invalid_status_value),
    Negative("M11", "unknown_span_name", "A_grounded_read", "Inject a span named 'evil.bypass'.", _m11_unknown_span_name),
    Negative("M12", "missing_request_id", "A_grounded_read", "Delete request_id on l1.plan.", _m12_missing_request_id),
    Negative("M13", "missing_run_id", "A_grounded_read", "Delete run_id on l0.route_decision.", _m13_missing_run_id),
    Negative("M14", "drift_trace_id", "A_grounded_read", "Change trace_id on a single span.", _m14_drift_trace_id),
    Negative("M15", "drift_request_id", "A_grounded_read", "Change request_id on a single span.", _m15_drift_request_id),
    Negative("M16", "drift_run_id", "A_grounded_read", "Change run_id on a single span.", _m16_drift_run_id),
    Negative("M17", "scenario_a_emit_l3", "A_grounded_read", "Inject l3.workflow_start in Scenario A.", _m17_a_emit_l3),
    Negative("M18", "scenario_a_emit_uwg_commit", "A_grounded_read", "Inject uwg.commit_request/receipt in Scenario A.", _m18_a_emit_uwg_commit),
    Negative("M19", "scenario_a_emit_hitl", "A_grounded_read", "Inject hitl.packetization in Scenario A.", _m19_a_emit_hitl_packet),
    Negative("M20", "scenario_b_drop_l3", "B_managed_workflow", "Remove l3.workflow_start from Scenario B.", _m20_b_drop_l3_workflow),
    Negative("M21", "scenario_b_emit_uwg_receipt", "B_managed_workflow", "Inject uwg.commit_receipt in Scenario B (proposal-only violation).", _m21_b_emit_uwg_commit_receipt),
    Negative("M22", "scenario_c_drop_weak_refine", "C_weak_evidence", "Remove c0.6.weak_support_refinement from Scenario C.", _m22_c_drop_weak_refinement),
    Negative("M23", "scenario_c_strip_weak_reason", "C_weak_evidence", "Strip WEAK reason_code from c0.5 in Scenario C.", _m23_c_strip_weak_reason),
    Negative("M24", "scenario_d_drop_hitl", "D_anti_bypass", "Remove hitl.packetization from Scenario D.", _m24_d_drop_hitl),
    Negative("M25", "scenario_d_emit_uwg_receipt", "D_anti_bypass", "Inject uwg.commit_receipt in Scenario D (the actual attack).", _m25_d_emit_uwg_commit_receipt),
    Negative("M26", "scenario_d_status_ok", "D_anti_bypass", "Set exit.x3 status=OK in Scenario D.", _m26_d_set_exit_status_ok),
    Negative("M27", "scenario_d_status_abstain", "D_anti_bypass", "Set exit.x3 status=ABSTAINED in Scenario D.", _m27_d_set_exit_status_abstain),
    Negative("M28", "drift_policy_hash", "A_grounded_read", "Drift policy_hash on u0.intake (replay-determinism).", _m28_drift_policy_hash),
    Negative("M29", "drift_contract_digest", "A_grounded_read", "Drift contract_digest on l2.e5.seal (replay-determinism).", _m29_drift_contract_digest),
    Negative("M30", "drift_reason_codes", "A_grounded_read", "Drift reason_codes on exit.x3 (replay-determinism).", _m30_drift_reason_codes),
    Negative("M31", "scenario_e_drop_commit_request", "E_authorized_commit", "Remove uwg.commit_request from Scenario E (orphans the receipt).", _m31_e_drop_commit_request),
    Negative("M32", "scenario_e_drop_commit_receipt", "E_authorized_commit", "Remove uwg.commit_receipt from Scenario E (silent incomplete commit).", _m32_e_drop_commit_receipt),
    Negative("M33", "scenario_e_strip_allow_commit", "E_authorized_commit", "Strip ALLOW_COMMIT marker from x3 in Scenario E (unauthorized commit).", _m33_e_strip_allow_commit_marker),
)


def all_codes() -> Tuple[str, ...]:
    return tuple(n.code for n in NEGATIVES)


def get_by_code(code: str) -> Negative:
    for n in NEGATIVES:
        if n.code == code:
            return n
    raise KeyError(f"unknown negative code: {code}")
