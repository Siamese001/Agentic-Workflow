"""Section-rigor SSOT: weak payloads must fail the named critical X2 gate."""

from __future__ import annotations

import pytest

from tests.unit.apps_rg.section_rigor.lane_registry import weak_fail_cases
from tests.unit.apps_rg.section_rigor.weak_payloads import _gate_pass


@pytest.mark.parametrize(
    "lane,gate_id,run_gates",
    [
        (case.lane, case.gate_id, case.run_gates)
        for case in weak_fail_cases()
    ],
    ids=[f"{c.lane}:{c.gate_id}" for c in weak_fail_cases()],
)
def test_weak_payload_fails_named_gate(lane: str, gate_id: str, run_gates) -> None:
    results = run_gates()
    assert not _gate_pass(results, gate_id), f"{lane} weak payload should fail {gate_id}"
