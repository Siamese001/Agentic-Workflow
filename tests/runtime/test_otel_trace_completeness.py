"""
tests/runtime/test_otel_trace_completeness.py

Phase 5 acceptance test (one of the 14 spec-named tests).

Asserts that the OTEL trace harness:
  * produced one trace JSON per scenario in artifacts/runtime/requirements_proof/traces/
  * each trace has exactly one root span (parent_span_id="")
  * every span name appears in the canonical RUNTIME_SPAN_NAMES vocabulary
  * every span carries the required attribute set
  * every span carries the conditional attribute keys (value may be None)
  * status is in the closed vocabulary
  * trace_id, request_id, run_id are stable within a trace
  * parent_span_id resolves to a span in the same trace
  * the four scenarios collectively exercise every required runtime stage
    that the user spec lists

This is the FOUNDATIONAL OTEL test. PROVEN status for any record still
requires Phase 4 wiring of the recorder into live runtime code.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

# We import the contract from the proof package so the test fails loudly
# if the canonical span list ever drifts.
from agentic_core.runtime.prove_requirements.otel_contract import (
    ALLOWED_STATUSES,
    CONDITIONAL_ATTRS,
    REQUIRED_ATTRS,
    RUNTIME_SPAN_NAMES,
    validate_trace,
)


EXPECTED_SCENARIO_FILES = (
    "scenario_A_grounded_read.json",
    "scenario_B_managed_workflow.json",
    "scenario_C_weak_evidence.json",
    "scenario_D_anti_bypass.json",
    "scenario_E_authorized_commit.json",
)


@pytest.fixture(scope="module")
def traces_dir(proof_artifacts: Path) -> Path:
    return proof_artifacts / "traces"


@pytest.fixture(scope="module")
def all_traces(traces_dir: Path) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for fname in EXPECTED_SCENARIO_FILES:
        p = traces_dir / fname
        if not p.exists():
            pytest.fail(f"trace file missing: {p}")
        out[fname] = json.loads(p.read_text(encoding="utf-8"))
    return out


def test_traces_dir_exists(traces_dir: Path) -> None:
    assert traces_dir.exists() and traces_dir.is_dir()


def test_all_four_scenarios_emitted(traces_dir: Path) -> None:
    for fname in EXPECTED_SCENARIO_FILES:
        assert (traces_dir / fname).exists(), f"missing scenario file {fname}"


def test_each_trace_validates_against_contract(all_traces: dict[str, dict]) -> None:
    for fname, td in all_traces.items():
        ok, errs = validate_trace(td)
        assert ok, f"trace {fname} failed validation: {errs[:5]}"


def test_each_span_uses_canonical_name(all_traces: dict[str, dict]) -> None:
    for fname, td in all_traces.items():
        for s in td["spans"]:
            assert s["name"] in RUNTIME_SPAN_NAMES, (
                f"trace {fname} has non-canonical span name: {s['name']}"
            )


def test_each_span_has_required_attrs(all_traces: dict[str, dict]) -> None:
    for fname, td in all_traces.items():
        for s in td["spans"]:
            for attr in REQUIRED_ATTRS:
                assert attr in s, f"{fname}/{s['name']} missing required attr {attr}"


def test_each_span_has_conditional_attr_keys(all_traces: dict[str, dict]) -> None:
    """Conditional attrs must be PRESENT as keys (value may be None) so the
    contract is explicit -- consumers know we did not forget the field."""
    for fname, td in all_traces.items():
        for s in td["spans"]:
            for attr in CONDITIONAL_ATTRS:
                assert attr in s, (
                    f"{fname}/{s['name']} missing conditional attr key {attr}"
                )


def test_each_span_status_is_allowed(all_traces: dict[str, dict]) -> None:
    for fname, td in all_traces.items():
        for s in td["spans"]:
            assert s["status"] in ALLOWED_STATUSES, (
                f"{fname}/{s['name']} has unknown status {s['status']}"
            )


def test_each_trace_has_exactly_one_root(all_traces: dict[str, dict]) -> None:
    for fname, td in all_traces.items():
        roots = [s for s in td["spans"] if not s["parent_span_id"]]
        assert len(roots) == 1, (
            f"trace {fname} must have exactly one root; found {len(roots)}: "
            f"{[r['name'] for r in roots]}"
        )


def test_parent_span_ids_resolve_within_trace(all_traces: dict[str, dict]) -> None:
    for fname, td in all_traces.items():
        ids = {s["span_id"] for s in td["spans"]}
        for s in td["spans"]:
            parent = s["parent_span_id"]
            if parent:
                assert parent in ids, (
                    f"{fname}/{s['name']} parent_span_id={parent} not resolvable"
                )


def test_trace_request_run_ids_are_stable(all_traces: dict[str, dict]) -> None:
    for fname, td in all_traces.items():
        trace_ids = {s["trace_id"] for s in td["spans"]}
        request_ids = {s["request_id"] for s in td["spans"]}
        run_ids = {s["run_id"] for s in td["spans"]}
        assert len(trace_ids) == 1, f"{fname} has {len(trace_ids)} trace_ids"
        assert len(request_ids) == 1, f"{fname} has {len(request_ids)} request_ids"
        assert len(run_ids) == 1, f"{fname} has {len(run_ids)} run_ids"


def test_scenario_a_does_not_emit_l3_or_uwg_spans(all_traces: dict[str, dict]) -> None:
    """Scenario A is R3 simple grounded read; spec says no L3 step, no UWG commit."""
    td = all_traces["scenario_A_grounded_read.json"]
    span_names = {s["name"] for s in td["spans"]}
    forbidden = {"l3.workflow_start", "l3.step_dispatch", "uwg.commit_request", "uwg.commit_receipt"}
    leaked = forbidden & span_names
    assert not leaked, f"scenario A leaked forbidden spans: {leaked}"


def test_scenario_b_emits_l3_steps(all_traces: dict[str, dict]) -> None:
    """Scenario B is managed workflow; must emit L3 spans."""
    td = all_traces["scenario_B_managed_workflow.json"]
    span_names = {s["name"] for s in td["spans"]}
    assert "l3.workflow_start" in span_names
    assert "l3.step_dispatch" in span_names


def test_scenario_c_emits_weak_support_refinement(all_traces: dict[str, dict]) -> None:
    """Scenario C must trigger C0.6."""
    td = all_traces["scenario_C_weak_evidence.json"]
    span_names = {s["name"] for s in td["spans"]}
    assert "c0.6.weak_support_refinement" in span_names


def test_scenario_d_blocks_uwg_and_emits_hitl(all_traces: dict[str, dict]) -> None:
    """Scenario D is the bypass attack; UWG must NOT commit, HITL packet emits."""
    td = all_traces["scenario_D_anti_bypass.json"]
    span_names = {s["name"] for s in td["spans"]}
    assert "hitl.packetization" in span_names
    assert "uwg.commit_receipt" not in span_names, (
        "scenario D must NOT emit uwg.commit_receipt -- write must be blocked"
    )
    # Exit disposition must be BLOCKED status
    exit_x3 = [s for s in td["spans"] if s["name"] == "exit.x3.disposition"]
    assert exit_x3, "scenario D missing exit.x3.disposition span"
    assert exit_x3[0]["status"] == "BLOCKED", (
        f"scenario D exit.x3 status must be BLOCKED, got {exit_x3[0]['status']}"
    )


def test_collective_coverage_of_canonical_spans(all_traces: dict[str, dict]) -> None:
    """The four scenarios collectively must exercise the runtime spans that
    are required for ALL paths (the 'always' subset). Optional spans like
    L3, UWG commit_receipt, weak refinement, HITL packet appear only in
    scenarios where their preconditions hold."""
    always_required = {
        "u0.intake",
        "l1.plan",
        "l0.route_decision",
        "c0.0.preflight",
        "c0.1.retrieval_plan",
        "c0.2.fetch",
        "c0.2a.hydrate",
        "c0.3.graph_traverse",
        "c0.4.shape_rerank_stratify",
        "c0.5.final_evidence_contract",
        "prompt_assembly.compile",
        "l2.e1.prep",
        "l2.e2.valid",
        "l2.e3.exec",
        "l2.e5.seal",
        "exit.preflight",
        "exit.x1.gates",
        "exit.x2.aggregate",
        "exit.x3.disposition",
        "l6.ingest",
        "l6.evaluate",
    }
    union: set[str] = set()
    for td in all_traces.values():
        for s in td["spans"]:
            union.add(s["name"])
    missing = always_required - union
    assert not missing, (
        f"required runtime spans not exercised by any scenario: {sorted(missing)}"
    )


def test_zero_runtime_wiring_yet_documented_in_gaps(proof_artifacts: Path) -> None:
    """GAPS.md must explicitly state Phase 5 is contract-only, not wired
    into live runtime code -- honors 'do not claim' rule."""
    md = (proof_artifacts / "GAPS.md").read_text(encoding="utf-8")
    assert "OTEL CONTRACT" in md or "OTEL contract" in md.lower() or "contract" in md.lower()
    assert "does NOT wire OTEL emission into the live" in md
