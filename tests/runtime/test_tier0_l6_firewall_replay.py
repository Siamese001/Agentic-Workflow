"""Tier 0 L6-firewall replay invariant validators.

Narrowly scoped tests for ``REQ-L6-FIREWALL-NO-CURRENT-RUN-MUTATION-001``.
L6 emits proposals only for future-run consumption and MUST NOT mutate
the current run, including via direct L4 writes.

These tests validate the static replay fixture pair only. They do not start
runtime services, do not execute live L6 evaluation, and do not invoke
proof harnesses, OTEL exporters, or full replay machinery.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

_REPLAY = Path("artifacts/runtime/requirements_proof/replay")


@pytest.mark.parametrize(
    "fname",
    [
        "replay_H_l6_firewall_no_current_run_mutation_run_1.json",
        "replay_H_l6_firewall_no_current_run_mutation_run_2.json",
    ],
)
def test_replay_H_no_current_run_mutation(fname: str) -> None:
    payload = json.loads((_REPLAY / fname).read_text(encoding="utf-8"))
    assert payload["step1_req_id"] == "REQ-L6-FIREWALL-NO-CURRENT-RUN-MUTATION-001"
    assert payload["expected_fail_reason"] == "L6_CURRENT_RUN_MUTATION_BLOCKED"
    assert payload["invariant_digest"].startswith("sha256:")
    assert payload["route_id"]
    assert payload["exit_disposition"]

    summary = payload["l6_firewall_summary"]
    assert summary["l6_attempted_current_run_mutations"] == 0
    assert summary["l6_attempted_l4_writes"] == 0
    assert summary["current_run_l4_writes_attributed_to_l6"] == 0
    # Future-run proposals are allowed.
    assert summary["l6_proposals_emitted_for_future_run"] >= 0


def test_replay_H_pair_digest_is_stable() -> None:
    p1 = json.loads(
        (_REPLAY / "replay_H_l6_firewall_no_current_run_mutation_run_1.json").read_text(encoding="utf-8")
    )
    p2 = json.loads(
        (_REPLAY / "replay_H_l6_firewall_no_current_run_mutation_run_2.json").read_text(encoding="utf-8")
    )
    assert p1["invariant_digest"] == p2["invariant_digest"]
    assert p1["route_id"] == p2["route_id"]
    assert p1["exit_disposition"] == p2["exit_disposition"]
    assert p1["l6_firewall_summary"] == p2["l6_firewall_summary"]
