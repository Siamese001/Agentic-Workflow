"""H5 governance tests: LearningArtifactIntent frozen dataclass.

Validates:
- Immutability (frozen=True)
- Hash determinism (same inputs → same hash)
- Hash integrity (verify() passes on valid, fails on tampered)
- Construction via create() factory
- Hashability (usable as dict key / set member)
"""

import pytest

from agentic_core.L0_routing.seams.learning_seam import (
    LearningArtifactIntent,
)

pytestmark = pytest.mark.governance

SAMPLE_METRICS = (("accuracy", 0.95), ("latency_ms", 42.0))


class TestFrozenImmutability:
    """LearningArtifactIntent must be frozen — no field mutation."""

    def test_cannot_set_field_after_construction(self):
        intent = LearningArtifactIntent.create(
            agent_id="agent-1",
            execution_id="exec-1",
            outcome="success",
            metrics=SAMPLE_METRICS,
            context_hash="abc123",
        )
        with pytest.raises(AttributeError):
            intent.agent_id = "tampered"  # type: ignore[misc]

    def test_cannot_delete_field(self):
        intent = LearningArtifactIntent.create(
            agent_id="agent-1",
            execution_id="exec-1",
            outcome="success",
            metrics=SAMPLE_METRICS,
            context_hash="abc123",
        )
        with pytest.raises(AttributeError):
            del intent.agent_id  # type: ignore[misc]


class TestHashDeterminism:
    """Same inputs must produce identical intent_hash."""

    def test_same_inputs_same_hash(self):
        a = LearningArtifactIntent.create(
            agent_id="agent-1",
            execution_id="exec-1",
            outcome="success",
            metrics=SAMPLE_METRICS,
            context_hash="abc123",
        )
        b = LearningArtifactIntent.create(
            agent_id="agent-1",
            execution_id="exec-1",
            outcome="success",
            metrics=SAMPLE_METRICS,
            context_hash="abc123",
        )
        assert a.intent_hash == b.intent_hash

    def test_different_inputs_different_hash(self):
        a = LearningArtifactIntent.create(
            agent_id="agent-1",
            execution_id="exec-1",
            outcome="success",
            metrics=SAMPLE_METRICS,
            context_hash="abc123",
        )
        b = LearningArtifactIntent.create(
            agent_id="agent-2",
            execution_id="exec-1",
            outcome="success",
            metrics=SAMPLE_METRICS,
            context_hash="abc123",
        )
        assert a.intent_hash != b.intent_hash

    def test_hash_is_sha256_hex(self):
        intent = LearningArtifactIntent.create(
            agent_id="agent-1",
            execution_id="exec-1",
            outcome="success",
            metrics=SAMPLE_METRICS,
            context_hash="abc123",
        )
        assert len(intent.intent_hash) == 64
        assert all(c in "0123456789abcdef" for c in intent.intent_hash)


class TestHashIntegrity:
    """verify() must pass on valid intents, fail on tampered."""

    def test_verify_passes_on_valid_intent(self):
        intent = LearningArtifactIntent.create(
            agent_id="agent-1",
            execution_id="exec-1",
            outcome="success",
            metrics=SAMPLE_METRICS,
            context_hash="abc123",
        )
        assert intent.verify() is True

    def test_verify_fails_on_wrong_hash(self):
        intent = LearningArtifactIntent(
            agent_id="agent-1",
            execution_id="exec-1",
            outcome="success",
            metrics=SAMPLE_METRICS,
            context_hash="abc123",
            intent_hash="0" * 64,
        )
        assert intent.verify() is False


class TestHashability:
    """Frozen dataclass must be usable as dict key / set member."""

    def test_usable_as_set_member(self):
        intent = LearningArtifactIntent.create(
            agent_id="agent-1",
            execution_id="exec-1",
            outcome="success",
            metrics=SAMPLE_METRICS,
            context_hash="abc123",
        )
        s = {intent}
        assert intent in s

    def test_usable_as_dict_key(self):
        intent = LearningArtifactIntent.create(
            agent_id="agent-1",
            execution_id="exec-1",
            outcome="success",
            metrics=SAMPLE_METRICS,
            context_hash="abc123",
        )
        d = {intent: "value"}
        assert d[intent] == "value"
