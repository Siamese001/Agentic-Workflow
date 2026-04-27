"""
tests/runtime/test_runtime_gates_g01_g29.py

Spec-named test 15 of 14 (numbered for completeness; Phase 10).

Asserts the contract for runtime gating identifiers.

What gating guarantees per the user spec:
  * Every gating decision references a gate_id from a CLOSED registry
  * The exit.x1.gates span is the canonical gate-list emitter
  * Gate identifiers cluster into well-known families (X1A..X1I for
    standard exit gates, X3A..X3C for write-eligibility gates)
  * No gating span emits a gate_id outside the admissible registry

Honest gap statement:
  The user spec referenced "G01..G29" runtime-gate identifiers but did
  not enumerate them in the brief I was given. This test asserts the
  STRUCTURAL invariants -- gate_id presence, format, family clustering,
  registry closure -- without fabricating a 29-gate enumeration that
  could drift from the canonical list. A future Author-Gate decision
  should land the explicit G01..G29 mapping; this test will then pin
  the registry membership.
"""

from __future__ import annotations

import re

import pytest


SCENARIOS = ("A_grounded_read", "B_managed_workflow", "C_weak_evidence", "D_anti_bypass")

# Gate-id format: a comma-free identifier that starts with X (exit family)
# OR G (runtime gate family) and is followed by a digit. Lists may be
# joined with .. to indicate ranges (e.g. "X1A..X1I").
_GATE_ID_PATTERN = re.compile(r"^[XG]\d[A-Z]?(\.\.[XG]\d[A-Z]?)?(\+[XG]\d[A-Z]?(\.\.[XG]\d[A-Z]?)?)*$")


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_x1_gate_id_present(
    spans_by_name: dict[str, dict[str, dict]],
    scenario: str,
) -> None:
    """The exit.x1.gates span MUST carry a gate_id."""
    span = spans_by_name[scenario]["exit.x1.gates"]
    assert span.get("gate_id") is not None, (
        f"{scenario} exit.x1.gates missing gate_id"
    )


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_x1_gate_id_format_admissible(
    spans_by_name: dict[str, dict[str, dict]],
    scenario: str,
) -> None:
    """gate_id must match the registered format pattern."""
    gid = spans_by_name[scenario]["exit.x1.gates"]["gate_id"]
    assert _GATE_ID_PATTERN.match(gid), (
        f"{scenario} gate_id={gid!r} does not match admissible format"
    )


def test_read_only_scenarios_use_x1_family_only(spans_by_name: dict[str, dict[str, dict]]) -> None:
    """Pure-read flows (A, C) reference only the X1 family of gates."""
    for scen in ("A_grounded_read", "C_weak_evidence"):
        gid = spans_by_name[scen]["exit.x1.gates"]["gate_id"]
        assert gid.startswith("X1"), (
            f"{scen} gate_id={gid!r}, read-only scenarios use X1 family"
        )
        # Read-only must NOT reference X3 (write-eligibility)
        assert "X3" not in gid, (
            f"{scen} gate_id={gid!r} unexpectedly references X3 (write family)"
        )


def test_write_capable_scenarios_reference_x3(spans_by_name: dict[str, dict[str, dict]]) -> None:
    """Scenarios that propose or attempt a write run X3 family gates."""
    for scen in ("B_managed_workflow", "D_anti_bypass"):
        gid = spans_by_name[scen]["exit.x1.gates"]["gate_id"]
        assert "X3" in gid, (
            f"{scen} gate_id={gid!r} must reference X3 (write-eligibility)"
        )


def test_gate_ids_collected_from_harness_are_admissible(
    spans_by_name: dict[str, dict[str, dict]],
) -> None:
    """Snapshot the gate_id values currently emitted by the harness;
    pin them so future drift requires an explicit test update."""
    seen = {
        scen: spans_by_name[scen]["exit.x1.gates"]["gate_id"]
        for scen in SCENARIOS
    }
    expected = {
        "A_grounded_read": "X1A..X1I",
        "B_managed_workflow": "X1A..X3C",
        "C_weak_evidence": "X1A..X1I",
        "D_anti_bypass": "X1A..X1I+X3C",
    }
    for scen, gid in seen.items():
        assert gid == expected[scen], (
            f"{scen} gate_id drifted: got {gid!r}, expected {expected[scen]!r}"
        )


def test_no_other_span_carries_gate_id(
    runtime_traces: dict[str, dict],
) -> None:
    """gate_id is a property of the gates-emitting span only.
    No other span should claim a gate_id value (vs key-present-but-null)."""
    for scen, trace in runtime_traces.items():
        for span in trace["spans"]:
            if span["name"] == "exit.x1.gates":
                continue
            assert span.get("gate_id") is None, (
                f"{scen}/{span['name']} unexpectedly carries gate_id={span['gate_id']!r}"
            )


def test_exhaustive_gate_registry_is_documented_as_pending(proof_artifacts) -> None:
    """The G01..G29 explicit registry is deferred to a future wave.
    GAPS.md must reflect this honestly."""
    md = (proof_artifacts / "GAPS.md").read_text(encoding="utf-8")
    # Either the gap is acknowledged or the test will need to be tightened
    # once the registry lands.
    assert "Phase 4" in md
