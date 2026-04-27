"""
tests/runtime/test_end_to_end_grounded_read.py

Spec-named test 16 of 14 (numbered for completeness; Phase 10).

End-to-end walkthrough of Scenario A (the canonical R3 simple grounded
read). Asserts the FULL chain from u0.intake through l6.evaluate fires
in the right order with the right contract digests, ending with
ALLOW_FINISH.

This is the smoke test for "does the entire read-only path work?".
"""

from __future__ import annotations

import pytest


SCENARIO = "A_grounded_read"

# Canonical end-to-end ordering for R3 simple grounded read.
EXPECTED_CHAIN = (
    "runtime.request",
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
)


@pytest.fixture(scope="module")
def trace(runtime_traces: dict[str, dict]) -> dict:
    return runtime_traces[SCENARIO]


@pytest.fixture(scope="module")
def names(trace: dict) -> set[str]:
    return {s["name"] for s in trace["spans"]}


def test_all_expected_spans_present(names: set[str]) -> None:
    missing = set(EXPECTED_CHAIN) - names
    assert not missing, f"E2E grounded-read missing spans: {sorted(missing)}"


def test_no_unexpected_spans(names: set[str]) -> None:
    """R3 grounded read has a closed span set -- L3, UWG, HITL, weak-refine
    must not appear."""
    forbidden = {
        "l3.workflow_start",
        "l3.step_dispatch",
        "uwg.commit_request",
        "uwg.commit_receipt",
        "c0.6.weak_support_refinement",
        "hitl.packetization",
        "l6.rca_or_proposal",
        "l6.promotion_attempt",
        "l2.e4.heal",
    }
    leaked = forbidden & names
    assert not leaked, f"Scenario A leaked forbidden spans: {sorted(leaked)}"


def test_ordering_root_to_leaf(spans_by_name: dict[str, dict[str, dict]]) -> None:
    """Walk the chain by start time; each subsequent stage must start at
    or after the previous one's start."""
    last = -1
    for span_name in EXPECTED_CHAIN:
        span = spans_by_name[SCENARIO][span_name]
        assert span["start_unix_ns"] >= last, (
            f"E2E ordering violation at {span_name}: started before predecessor"
        )
        last = span["start_unix_ns"]


def test_total_span_count_matches_expected(trace: dict) -> None:
    """Scenario A produces exactly len(EXPECTED_CHAIN) spans -- nothing
    extra, nothing missing."""
    assert trace["span_count"] == len(EXPECTED_CHAIN), (
        f"Scenario A span_count={trace['span_count']}, expected {len(EXPECTED_CHAIN)}"
    )


def test_disposition_is_allow_finish(spans_by_name: dict[str, dict[str, dict]]) -> None:
    span = spans_by_name[SCENARIO]["exit.x3.disposition"]
    rc = " ".join(span.get("reason_codes") or [])
    assert "ALLOW_FINISH" in rc
    assert span["status"] == "OK"


def test_contract_digests_chain_complete(spans_by_name: dict[str, dict[str, dict]]) -> None:
    """Each contract-emitting stage carries its contract_digest."""
    digests = {
        "u0.intake": "intake_envelope",
        "l1.plan": "L1PlanContract",
        "l0.route_decision": "RouteContract",
        "c0.5.final_evidence_contract": "FinalEvidenceContract",
        "prompt_assembly.compile": "CompiledPromptArtifact",
        "l2.e5.seal": "SealedL2Artifact",
    }
    for span_name in digests:
        cd = spans_by_name[SCENARIO][span_name].get("contract_digest")
        assert cd is not None, f"Scenario A {span_name} missing contract_digest"


def test_token_telemetry_recorded(spans_by_name: dict[str, dict[str, dict]]) -> None:
    """E3 records actual generation cost."""
    e3 = spans_by_name[SCENARIO]["l2.e3.exec"]
    assert e3.get("tokens_in") is not None
    assert e3.get("tokens_out") is not None


def test_exit_pipeline_status_clean(spans_by_name: dict[str, dict[str, dict]]) -> None:
    for span_name in ("exit.preflight", "exit.x1.gates", "exit.x2.aggregate", "exit.x3.disposition"):
        assert spans_by_name[SCENARIO][span_name]["status"] == "OK"


def test_l6_observed_clean_run(spans_by_name: dict[str, dict[str, dict]]) -> None:
    """L6 fires ingest+evaluate but no RCA needed for a clean read."""
    assert spans_by_name[SCENARIO]["l6.ingest"]["status"] == "OK"
    assert spans_by_name[SCENARIO]["l6.evaluate"]["status"] == "OK"


def test_replay_anchors_present(spans_by_name: dict[str, dict[str, dict]]) -> None:
    """The end-to-end chain must carry replay_key on its anchors so
    Phase-6 deterministic replay can verify the run."""
    for span_name in ("l0.route_decision", "c0.0.preflight", "c0.5.final_evidence_contract",
                       "exit.x3.disposition"):
        rk = spans_by_name[SCENARIO][span_name].get("replay_key")
        assert rk is not None, f"Scenario A {span_name} missing replay_key anchor"


def test_artifact_refs_recorded_at_fetch(spans_by_name: dict[str, dict[str, dict]]) -> None:
    """Retrieved chunks are pinned via artifact_refs so Phase-6 replay
    can re-fetch the same evidence."""
    span = spans_by_name[SCENARIO]["c0.2.fetch"]
    refs = span.get("artifact_refs") or []
    assert len(refs) > 0, "Scenario A c0.2.fetch must declare artifact_refs"


def test_request_run_ids_propagated_end_to_end(
    runtime_traces: dict[str, dict],
    spans_by_name: dict[str, dict[str, dict]],
) -> None:
    intake = spans_by_name[SCENARIO]["u0.intake"]
    req = intake["request_id"]
    run = intake["run_id"]
    for s in runtime_traces[SCENARIO]["spans"]:
        assert s["request_id"] == req
        assert s["run_id"] == run
