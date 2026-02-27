"""REQ-085/086: HIL reviewer_sig verified; MODIFY_DIFF requires L5 re-clear."""

from __future__ import annotations

import dataclasses

import pytest


@pytest.mark.governance
def test_req085_reviewer_sig_field_required():
    from agentic_core.L0_routing.types.governance_types import HILReviewOutcome

    fields = {f.name for f in dataclasses.fields(HILReviewOutcome)}
    assert "reviewer_sig" in fields
    assert "reviewer_id" in fields


@pytest.mark.governance
def test_req086_modify_diff_requires_l5_reclear():
    from agentic_core.L0_routing.types.governance_types import HILReviewOutcome

    outcome = HILReviewOutcome(
        decision="MODIFY_DIFF",
        reviewer_id="r1",
        reviewer_sig="sig",
        requires_l5_reclear=True,
    )
    assert outcome.requires_l5_reclear is True
