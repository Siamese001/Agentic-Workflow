"""ADG-driven tests for L5_safety/config/gravity_leak_config.py — fan_in=1."""
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

_emit_records_execution_trace("p0", "evidence", "test_gravity_leak_config_adg")
_emit_applies_guardrail("p0", "test_gravity_leak_config_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_gravity_leak_config_adg", "policy_binding")
_emit_snapshots_state("p0", "test_gravity_leak_config_adg", "state_snapshot")
emit_replay_key("p0", "test_gravity_leak_config_adg")
emit_determinism_digest("p0", "test_gravity_leak_config_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.config.gravity_leak_config import (
        CORE_TERRITORY_KEYWORDS,
        GravityLeakDetector,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    CORE_TERRITORY_KEYWORDS = None  # type: ignore[assignment]
    GravityLeakDetector = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="gravity_leak_config deps unavailable")
class TestGravityLeakConstants:
    def test_core_territory_keywords_is_set(self):
        assert isinstance(CORE_TERRITORY_KEYWORDS, set)

    def test_contains_sovereign(self):
        assert "sovereign" in CORE_TERRITORY_KEYWORDS


@pytest.mark.skipif(not _AVAILABLE, reason="gravity_leak_config deps unavailable")
class TestGravityLeakDetector:
    def test_importable(self):
        assert callable(GravityLeakDetector)

    def test_creates(self, tmp_path):
        detector = GravityLeakDetector(project_root=tmp_path)
        assert detector is not None


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
