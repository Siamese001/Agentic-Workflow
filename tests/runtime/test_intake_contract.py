"""
tests/runtime/test_intake_contract.py

Spec-named test 8 of 14 (Phase 10).

Asserts the contract for the ``u0.intake`` runtime stage as it appears
in every scenario trace produced by the harness.

What U0 intake guarantees per the user spec:
  * Validates transport, identity baseline, quota, schema, envelope
  * Carries a policy_hash so downstream stages can prove the intake
    contract did not drift between request and execution
  * Is the FIRST stage span (parent must be runtime.request)
  * Status must be OK on a healthy ingress; ERROR on rejection

This test validates only the contract-level evidence in the harness
trace. PROVEN status for any U0 record still requires the live
runtime code path to emit this span -- a future Phase-4 wiring task.
"""

from __future__ import annotations

import pytest


SCENARIOS = ("A_grounded_read", "B_managed_workflow", "C_weak_evidence", "D_anti_bypass")


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_intake_span_present(spans_by_name: dict[str, dict[str, dict]], scenario: str) -> None:
    assert "u0.intake" in spans_by_name[scenario], (
        f"scenario {scenario} missing u0.intake span"
    )


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_intake_status_is_ok(spans_by_name: dict[str, dict[str, dict]], scenario: str) -> None:
    """A clean harness trace must emit u0.intake with status=OK."""
    span = spans_by_name[scenario]["u0.intake"]
    assert span["status"] == "OK", (
        f"scenario {scenario} u0.intake status={span['status']!r}, expected OK"
    )


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_intake_carries_policy_hash(spans_by_name: dict[str, dict[str, dict]], scenario: str) -> None:
    """Spec: policy_hash MUST be attached at intake to anchor downstream proof."""
    span = spans_by_name[scenario]["u0.intake"]
    ph = span.get("policy_hash")
    assert ph is not None, f"scenario {scenario} u0.intake missing policy_hash"
    assert isinstance(ph, str) and len(ph) >= 8, (
        f"scenario {scenario} u0.intake policy_hash is malformed: {ph!r}"
    )


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_intake_parent_is_runtime_request(
    spans_by_name: dict[str, dict[str, dict]],
    runtime_traces: dict[str, dict],
    scenario: str,
) -> None:
    """U0 must be a direct child of the runtime.request root."""
    intake = spans_by_name[scenario]["u0.intake"]
    parent_id = intake["parent_span_id"]
    by_id = {s["span_id"]: s for s in runtime_traces[scenario]["spans"]}
    parent = by_id.get(parent_id)
    assert parent is not None, f"{scenario} u0.intake parent unresolvable"
    assert parent["name"] == "runtime.request", (
        f"{scenario} u0.intake parent is {parent['name']!r}, expected runtime.request"
    )


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_intake_carries_required_attrs(spans_by_name: dict[str, dict[str, dict]], scenario: str) -> None:
    """Required-attr keys per the spec: trace_id, span_id, parent_span_id,
    request_id, run_id, status, reason_codes, latency_ms."""
    span = spans_by_name[scenario]["u0.intake"]
    for attr in ("trace_id", "span_id", "parent_span_id", "request_id", "run_id",
                 "status", "reason_codes", "latency_ms"):
        assert attr in span, f"{scenario} u0.intake missing required attr {attr}"


def test_scenario_a_intake_carries_intake_envelope_digest(spans_by_name: dict[str, dict[str, dict]]) -> None:
    """Scenario A is the canonical reference; its intake envelope contract
    digest must be present and well-formed."""
    span = spans_by_name["A_grounded_read"]["u0.intake"]
    cd = span.get("contract_digest")
    assert cd is not None and isinstance(cd, str), (
        "Scenario A u0.intake must declare a contract_digest"
    )


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_intake_request_run_ids_propagate_to_all_spans(
    runtime_traces: dict[str, dict],
    spans_by_name: dict[str, dict[str, dict]],
    scenario: str,
) -> None:
    """The request_id/run_id minted at intake must propagate to every
    downstream span -- this is the spec's identity-propagation guarantee."""
    intake = spans_by_name[scenario]["u0.intake"]
    req = intake["request_id"]
    run = intake["run_id"]
    for s in runtime_traces[scenario]["spans"]:
        assert s["request_id"] == req, (
            f"{scenario} span {s['name']} has request_id={s['request_id']}, "
            f"expected {req} from u0.intake"
        )
        assert s["run_id"] == run, (
            f"{scenario} span {s['name']} has run_id={s['run_id']}, "
            f"expected {run} from u0.intake"
        )
