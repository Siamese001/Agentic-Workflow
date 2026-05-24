"""Contract gate: X1D judge transport parity across apps_rg proof panel."""

from __future__ import annotations

from apps_rg.runtime.judges.x1d_judge_transport_contract import (
    audit_x1d_judge_transport_parity,
)
from apps_rg.runtime.sections.executive_summary_x1d_judge_contract import (
    audit_executive_summary_x1d_judge_coherence,
)


def test_x1d_transport_parity_contract_zero_violations() -> None:
    violations = audit_x1d_judge_transport_parity()
    assert violations == []


def test_executive_summary_judge_coherence_includes_transport() -> None:
    violations = audit_executive_summary_x1d_judge_coherence()
    assert violations == []
