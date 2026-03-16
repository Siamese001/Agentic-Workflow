"""ADG-driven tests for L2_execution/types/replay_envelope_types.py — fan_in=0."""
from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_replay_envelope_types_adg")
_emit_applies_guardrail("p0", "test_replay_envelope_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_replay_envelope_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_replay_envelope_types_adg", "state_snapshot")
emit_replay_key("p0", "test_replay_envelope_types_adg")
emit_determinism_digest("p0", "test_replay_envelope_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.types.replay_envelope_types import ReplayEnvelope

_ENV_KWARGS = dict(
    routing_hash="r", manifest_hash="m", model_id="gpt-4",
    model_version="v1", temperature=0.0,
    allowed_model_policy_version="v1", policy_version="v1",
    gateway_version="v1",
    embedder_provider="openai", embedder_model="text-embedding-3-small", embedder_dim=1536,
    normalization_policy="l2", chunking_policy="fixed_512",
    distance_metric="cosine", retrieval_top_k=5, retrieval_similarity_cutoff=0.75,
    agent_registry_hash="abc123", deterministic_engine_version="v1",
)


class TestReplayEnvelope:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ReplayEnvelope)

    def test_is_frozen(self):
        env = ReplayEnvelope(**_ENV_KWARGS)
        with pytest.raises((AttributeError, TypeError)):
            env.model_id = "other"

    def test_creates(self):
        env = ReplayEnvelope(**_ENV_KWARGS)
        assert env.model_id == "gpt-4"
        assert env.temperature == 0.0
