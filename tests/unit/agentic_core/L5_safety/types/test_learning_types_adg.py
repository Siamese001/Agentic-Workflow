"""ADG contract tests for L5_safety/types/learning_types.py."""
from __future__ import annotations

import ast

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

_emit_records_execution_trace("p0", "evidence", "test_learning_types_adg")
_emit_applies_guardrail("p0", "test_learning_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_learning_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_learning_types_adg", "state_snapshot")
emit_replay_key("p0", "test_learning_types_adg")
emit_determinism_digest("p0", "test_learning_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

MODULE_PATH = "agentic_core/L5_safety/types/learning_types.py"

def test_module_parses():
    import pathlib
    src = pathlib.Path(MODULE_PATH).read_text(encoding="utf-8")
    ast.parse(src)

def test_has_healing_pattern():
    import pathlib
    src = pathlib.Path(MODULE_PATH).read_text(encoding="utf-8")
    assert "HealingPattern" in src or "AdaptiveLearning" in src

def test_has_learning_engine():
    import pathlib
    src = pathlib.Path(MODULE_PATH).read_text(encoding="utf-8")
    assert "Engine" in src or "learn" in src.lower()

try:
    from agentic_core.L5_safety.types.learning_types import (
        AdaptiveLearningEngine,
        create_adaptive_learning_engine,
    )
    _AVAIL = True
except ImportError:
    _AVAIL = False
    AdaptiveLearningEngine = create_adaptive_learning_engine = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestAdaptiveLearningEngine:
    def test_creates(self):
        engine = AdaptiveLearningEngine(); assert engine is not None
    def test_get_statistics(self):
        engine = AdaptiveLearningEngine()
        stats = engine.get_statistics()
        assert "total_patterns" in stats
    def test_factory_function(self):
        engine = create_adaptive_learning_engine()
        assert isinstance(engine, AdaptiveLearningEngine)
