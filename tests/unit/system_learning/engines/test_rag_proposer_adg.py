"""ADG-driven tests for system_learning/engines/rag_proposer.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from system_learning.engines.rag_proposer import (
    RAGChangePackage,
    _LOW_RECALL_THRESHOLD,
    _HIGH_NOISE_THRESHOLD,
    _TOP_K_MIN,
    _TOP_K_MAX,
    _SIMILARITY_CUTOFF_MIN,
    _SIMILARITY_CUTOFF_MAX,
)


class TestConstants:
    def test_low_recall_threshold(self):
        assert _LOW_RECALL_THRESHOLD == 0.60

    def test_high_noise_threshold(self):
        assert _HIGH_NOISE_THRESHOLD == 0.40

    def test_top_k_bounds(self):
        assert _TOP_K_MIN < _TOP_K_MAX

    def test_similarity_cutoff_bounds(self):
        assert _SIMILARITY_CUTOFF_MIN < _SIMILARITY_CUTOFF_MAX


class TestRAGChangePackage:
    def test_creates(self):
        pkg = RAGChangePackage(
            surface_name="rag_config",
            parameter="similarity_cutoff",
            old_value=0.5,
            new_value=0.55,
            justification="low recall",
            snapshot_id="snap-1",
        )
        assert pkg.surface_name == "rag_config"
        assert pkg.parameter == "similarity_cutoff"

    def test_is_frozen(self):
        pkg = RAGChangePackage(
            surface_name="s",
            parameter="p",
            old_value=0.5,
            new_value=0.6,
            justification="j",
            snapshot_id="snap-2",
        )
        with pytest.raises(Exception):
            pkg.old_value = 0.9

    def test_canonical_bytes_returns_bytes(self):
        pkg = RAGChangePackage(
            surface_name="s",
            parameter="p",
            old_value=0.5,
            new_value=0.6,
            justification="j",
            snapshot_id="snap-3",
        )
        result = pkg.canonical_bytes()
        assert isinstance(result, bytes)
