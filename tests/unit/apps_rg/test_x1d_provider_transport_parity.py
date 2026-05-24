"""Provider transport parity — delegates to x1d_judge_transport_contract audits."""

from __future__ import annotations

from apps_rg.runtime.judges.x1d_judge_transport_contract import audit_x1d_judge_transport_parity
from apps_rg.runtime.sections.executive_summary_x1d_judge_contract import (
    build_brown_brown_six_sentence_packet,
)


def test_x1d_provider_transport_parity_zero_violations() -> None:
    packet = build_brown_brown_six_sentence_packet()
    violations = audit_x1d_judge_transport_parity(packet)
    codes = [v.code for v in violations]
    assert violations == [], codes
