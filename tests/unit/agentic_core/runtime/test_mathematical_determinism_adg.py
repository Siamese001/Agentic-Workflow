"""ADG-driven tests for runtime/mathematical_determinism.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.runtime.mathematical_determinism import (
    DeterministicArtifact,
    DeterminismProof,
    MathematicalDeterminismEngine,
)


class TestDeterministicArtifact:
    def test_creates(self):
        art = DeterministicArtifact(name="plan.json", hash_value="abc123", metadata={})
        assert art.name == "plan.json"
        assert art.hash_value == "abc123"

    def test_is_frozen(self):
        art = DeterministicArtifact(name="a", hash_value="b", metadata={})
        with pytest.raises(Exception):
            art.name = "modified"


class TestDeterminismProof:
    def test_creates(self):
        proof = DeterminismProof(
            core_digest="digest",
            run_id="run-1",
            creation_timestamp=1735689600.0,
            artifact_count=3,
            policy_hash="ph",
            hierarchy_hash="hh",
            authority_hash="ah",
        )
        assert proof.core_digest == "digest"
        assert proof.artifact_count == 3

    def test_is_frozen(self):
        proof = DeterminismProof(
            core_digest="d",
            run_id="r",
            creation_timestamp=1735689600.0,
            artifact_count=0,
            policy_hash="p",
            hierarchy_hash="h",
            authority_hash="a",
        )
        with pytest.raises(Exception):
            proof.core_digest = "modified"


class TestMathematicalDeterminismEngine:
    def test_importable(self):
        assert callable(MathematicalDeterminismEngine)

    def test_creates(self):
        engine = MathematicalDeterminismEngine(
            policy_hash="phash",
            hierarchy_hash="hhash",
            authority_hash="ahash",
        )
        assert engine is not None

    def test_has_seal(self):
        assert hasattr(MathematicalDeterminismEngine, "seal")
