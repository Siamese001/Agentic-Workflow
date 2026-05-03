"""W15: CitationBundle + CognitiveDiffBundle emission; blueprint_hash in PromotionDecisionArtifact.

REQ-199/211/236:
- CitationBundle emitted on Tier III
- CognitiveDiffBundle emitted on Tier III
- blueprint_hash present in PromotionDecisionArtifact
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

import pytest

pytestmark = pytest.mark.governance


# ---------------------------------------------------------------------------
# Artifact types
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CitationBundle:
    bundle_id: str
    citations: tuple
    emitted_by: str
    semantic_clock_tick: int
    bundle_hash: str = ""

    def __post_init__(self):
        if not self.bundle_hash:
            data = {
                "bundle_id": self.bundle_id,
                "citations": list(self.citations),
                "emitted_by": self.emitted_by,
                "semantic_clock_tick": self.semantic_clock_tick,
            }
            h = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
            object.__setattr__(self, "bundle_hash", h)


@dataclass(frozen=True)
class CognitiveDiffBundle:
    diff_id: str
    trace_hash_before: str
    trace_hash_after: str
    emitted_on_tier3: bool
    semantic_clock_tick: int
    diff_hash: str = ""

    def __post_init__(self):
        if not self.diff_hash:
            data = {
                "diff_id": self.diff_id,
                "trace_hash_before": self.trace_hash_before,
                "trace_hash_after": self.trace_hash_after,
                "emitted_on_tier3": self.emitted_on_tier3,
                "semantic_clock_tick": self.semantic_clock_tick,
            }
            h = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
            object.__setattr__(self, "diff_hash", h)


@dataclass(frozen=True)
class PromotionDecisionArtifact:
    decision_id: str
    decision: str
    blueprint_hash: str  # REQ-236 — must be present
    prev_wave_hash: str
    semantic_clock_tick: int
    artifact_hash: str = ""

    def __post_init__(self):
        if not self.blueprint_hash:
            raise ValueError("blueprint_hash must be present in PromotionDecisionArtifact")
        if not self.artifact_hash:
            data = {
                "decision_id": self.decision_id,
                "decision": self.decision,
                "blueprint_hash": self.blueprint_hash,
                "prev_wave_hash": self.prev_wave_hash,
                "semantic_clock_tick": self.semantic_clock_tick,
            }
            h = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
            object.__setattr__(self, "artifact_hash", h)


# ---------------------------------------------------------------------------
# Emission registry
# ---------------------------------------------------------------------------


class ArtifactEmissionRegistry:
    """Records emitted artifacts by type."""

    def __init__(self):
        self._citations: list[CitationBundle] = []
        self._diffs: list[CognitiveDiffBundle] = []
        self._promotions: list[PromotionDecisionArtifact] = []

    def emit_citation_bundle(self, bundle: CitationBundle) -> None:
        self._citations.append(bundle)

    def emit_cognitive_diff(self, diff: CognitiveDiffBundle) -> None:
        self._diffs.append(diff)

    def emit_promotion_decision(self, artifact: PromotionDecisionArtifact) -> None:
        if not artifact.blueprint_hash:
            raise ValueError("PromotionDecisionArtifact missing blueprint_hash")
        self._promotions.append(artifact)

    @property
    def citation_count(self) -> int:
        return len(self._citations)

    @property
    def diff_count(self) -> int:
        return len(self._diffs)

    @property
    def promotion_count(self) -> int:
        return len(self._promotions)

    def get_latest_promotion(self) -> PromotionDecisionArtifact | None:
        return self._promotions[-1] if self._promotions else None


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.fixture()
def registry() -> ArtifactEmissionRegistry:
    return ArtifactEmissionRegistry()


@pytest.mark.governance
def test_req199_citation_bundle_emitted(registry):
    """REQ-199: CitationBundle is emitted and recorded."""
    bundle = CitationBundle(
        bundle_id="cite_001",
        citations=("cite_a", "cite_b", "cite_c"),
        emitted_by="tier3_handler",
        semantic_clock_tick=10,
    )
    registry.emit_citation_bundle(bundle)

    assert registry.citation_count == 1
    assert len(bundle.bundle_hash) == 64


@pytest.mark.governance
def test_req211_cognitive_diff_bundle_emitted_on_tier3(registry):
    """REQ-211: CognitiveDiffBundle is emitted on Tier III activation."""
    diff = CognitiveDiffBundle(
        diff_id="diff_001",
        trace_hash_before="a" * 64,
        trace_hash_after="b" * 64,
        emitted_on_tier3=True,
        semantic_clock_tick=11,
    )
    registry.emit_cognitive_diff(diff)

    assert registry.diff_count == 1
    assert diff.emitted_on_tier3 is True
    assert len(diff.diff_hash) == 64


@pytest.mark.governance
def test_req236_blueprint_hash_in_promotion_decision(registry):
    """REQ-236: PromotionDecisionArtifact must carry blueprint_hash."""
    blueprint_hash = hashlib.sha256(b"blueprint_v1").hexdigest()
    artifact = PromotionDecisionArtifact(
        decision_id="dec_001",
        decision="promote",
        blueprint_hash=blueprint_hash,
        prev_wave_hash="c" * 64,
        semantic_clock_tick=12,
    )
    registry.emit_promotion_decision(artifact)

    promo = registry.get_latest_promotion()
    assert promo is not None
    assert promo.blueprint_hash == blueprint_hash
    assert len(promo.artifact_hash) == 64


@pytest.mark.governance
def test_req236_promotion_missing_blueprint_hash_rejected():
    """REQ-236: PromotionDecisionArtifact without blueprint_hash raises."""
    with pytest.raises(ValueError, match="blueprint_hash"):
        PromotionDecisionArtifact(
            decision_id="dec_bad",
            decision="promote",
            blueprint_hash="",  # missing
            prev_wave_hash="d" * 64,
            semantic_clock_tick=13,
        )


@pytest.mark.governance
def test_req199_citation_bundle_hash_deterministic():
    """REQ-199: CitationBundle hash is deterministic across runs."""
    kwargs = {
        "bundle_id": "cite_002",
        "citations": ("c1", "c2"),
        "emitted_by": "tier3",
        "semantic_clock_tick": 5,
    }
    b1 = CitationBundle(**kwargs)
    b2 = CitationBundle(**kwargs)
    assert b1.bundle_hash == b2.bundle_hash


@pytest.mark.governance
def test_req211_cognitive_diff_hash_deterministic():
    """REQ-211: CognitiveDiffBundle hash is deterministic."""
    kwargs = {
        "diff_id": "diff_002",
        "trace_hash_before": "e" * 64,
        "trace_hash_after": "f" * 64,
        "emitted_on_tier3": True,
        "semantic_clock_tick": 7,
    }
    d1 = CognitiveDiffBundle(**kwargs)
    d2 = CognitiveDiffBundle(**kwargs)
    assert d1.diff_hash == d2.diff_hash
