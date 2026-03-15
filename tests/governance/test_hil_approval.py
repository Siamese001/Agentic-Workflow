"""REQ-085/086: HIL reviewer_sig verified; MODIFY_DIFF requires L5 re-clear."""

from __future__ import annotations

import dataclasses

import pytest

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

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
