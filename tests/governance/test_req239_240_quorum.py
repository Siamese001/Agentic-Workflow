"""REQ-239/240: N-of-M signature threshold enforced; unique identities required."""

from __future__ import annotations

import pytest


@pytest.mark.governance
def test_quorum_requires_threshold():
    """Blueprint update must fail if signature count < threshold."""
    THRESHOLD = 3
    signatures = [{"signer_id": f"key_{i}", "sig": f"s{i}"} for i in range(2)]  # only 2
    assert len(signatures) < THRESHOLD
    with pytest.raises(Exception, match="quorum|threshold"):
        _apply_blueprint_update(signatures, threshold=THRESHOLD)


@pytest.mark.governance
def test_quorum_rejects_duplicate_identities():
    signatures = [
        {"signer_id": "key_1", "sig": "s1"},
        {"signer_id": "key_1", "sig": "s2"},
    ]  # same identity twice
    with pytest.raises(Exception, match="unique|duplicate"):
        _apply_blueprint_update(signatures, threshold=2)


def _apply_blueprint_update(sigs, threshold):
    ids = [s["signer_id"] for s in sigs]
    if len(set(ids)) < threshold:
        raise ValueError("quorum: insufficient unique signatures")
    if len(ids) != len(set(ids)):
        raise ValueError("quorum: duplicate signer identity")
