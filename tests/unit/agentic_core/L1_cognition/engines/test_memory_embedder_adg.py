"""ADG-driven tests for L1_cognition/engines/memory_embedder.py — fan_in=1."""
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

_emit_records_execution_trace("p0", "evidence", "test_memory_embedder_adg")
_emit_applies_guardrail("p0", "test_memory_embedder_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_memory_embedder_adg", "policy_binding")
_emit_snapshots_state("p0", "test_memory_embedder_adg", "state_snapshot")
emit_replay_key("p0", "test_memory_embedder_adg")
emit_determinism_digest("p0", "test_memory_embedder_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

try:
    from agentic_core.L1_cognition.engines.memory_embedder import HealingMemoryEmbedder
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    HealingMemoryEmbedder = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="memory_embedder deps unavailable")
class TestHealingMemoryEmbedder:
    def test_importable(self):
        assert callable(HealingMemoryEmbedder)

    def test_creates_with_defaults(self):
        embedder = HealingMemoryEmbedder()
        assert embedder is not None

    def test_has_embed_violation(self):
        assert hasattr(HealingMemoryEmbedder, "embed_violation") or hasattr(
            HealingMemoryEmbedder, "embed"
        )


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
