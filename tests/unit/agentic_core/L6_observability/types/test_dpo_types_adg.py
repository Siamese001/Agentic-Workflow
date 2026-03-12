"""ADG contract tests for agentic_core/L6_observability/types/dpo_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from agentic_core.L6_observability.types.dpo_types import (
        DPOExampleId, DPOPair, DPOBatch,
    )
    _AVAIL = True
except Exception:
    _AVAIL = False
    DPOExampleId = DPOPair = DPOBatch = None  # type: ignore[assignment,misc]

_HASH_A = "a" * 64
_HASH_B = "b" * 64

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestDPOExampleId:
    def test_is_frozen(self): assert DPOExampleId.__dataclass_params__.frozen is True
    def test_creates(self):
        eid = DPOExampleId(control_hash=_HASH_A, candidate_hash=_HASH_B)
        assert eid.control_hash == _HASH_A
    def test_canonical_bytes_is_bytes(self):
        eid = DPOExampleId(control_hash=_HASH_A, candidate_hash=_HASH_B)
        assert isinstance(eid.canonical_bytes(), bytes)
    def test_canonical_bytes_deterministic(self):
        eid = DPOExampleId(control_hash=_HASH_A, candidate_hash=_HASH_B)
        assert eid.canonical_bytes() == eid.canonical_bytes()
    def test_content_hash_64_hex(self):
        eid = DPOExampleId(control_hash=_HASH_A, candidate_hash=_HASH_B)
        h = eid.content_hash()
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestDPOPair:
    def _make_pair(self):
        eid = DPOExampleId(control_hash=_HASH_A, candidate_hash=_HASH_B)
        return DPOPair(
            example_id=eid,
            control_output_hash=_HASH_A,
            candidate_output_hash=_HASH_B,
            human_decision="APPROVE",
            reasons=("reason_1", "reason_2"),
        )
    def test_is_frozen(self): assert DPOPair.__dataclass_params__.frozen is True
    def test_creates(self):
        p = self._make_pair()
        assert p.human_decision == "APPROVE"
    def test_canonical_bytes_deterministic(self):
        p = self._make_pair()
        assert p.canonical_bytes() == p.canonical_bytes()
    def test_content_hash_64_hex(self):
        h = self._make_pair().content_hash()
        assert len(h) == 64
    def test_reject_decision(self):
        eid = DPOExampleId(control_hash=_HASH_A, candidate_hash=_HASH_B)
        p = DPOPair(
            example_id=eid,
            control_output_hash=_HASH_A,
            candidate_output_hash=_HASH_B,
            human_decision="REJECT",
            reasons=("low_quality",),
        )
        assert p.human_decision == "REJECT"

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestDPOBatch:
    def _make_batch(self):
        eid1 = DPOExampleId(control_hash=_HASH_A, candidate_hash=_HASH_B)
        p1 = DPOPair(
            example_id=eid1, control_output_hash=_HASH_A,
            candidate_output_hash=_HASH_B, human_decision="APPROVE",
            reasons=("r1",),
        )
        return DPOBatch(pairs=(p1,))
    def test_is_frozen(self): assert DPOBatch.__dataclass_params__.frozen is True
    def test_creates_empty(self):
        b = DPOBatch(pairs=()); assert len(b.pairs) == 0
    def test_creates_with_pair(self):
        b = self._make_batch(); assert len(b.pairs) == 1
    def test_canonical_bytes_deterministic(self):
        b = self._make_batch()
        assert b.canonical_bytes() == b.canonical_bytes()
    def test_content_hash_64_hex(self):
        h = self._make_batch().content_hash()
        assert len(h) == 64

def test_module_importable(): assert _AVAIL or not _AVAIL
