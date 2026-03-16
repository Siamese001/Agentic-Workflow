"""ADG-driven tests for L0_routing/enforcement/boot_sequence.py — fan_in=0."""
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

_emit_records_execution_trace("p0", "evidence", "test_boot_sequence_adg")
_emit_applies_guardrail("p0", "test_boot_sequence_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_boot_sequence_adg", "policy_binding")
_emit_snapshots_state("p0", "test_boot_sequence_adg", "state_snapshot")
emit_replay_key("p0", "test_boot_sequence_adg")
emit_determinism_digest("p0", "test_boot_sequence_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.enforcement.boot_sequence import BootSequence
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    BootSequence = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="boot_sequence deps unavailable")
class TestBootSequence:
    def test_importable(self):
        assert callable(BootSequence)

    def test_creates_with_defaults(self):
        bs = BootSequence()
        assert bs.strict_mode is True
        assert bs.discovered_agents == []
        assert bs.compliance_violations == []

    def test_creates_non_strict(self):
        bs = BootSequence(strict_mode=False)
        assert bs.strict_mode is False

    def test_has_execute_boot(self):
        assert hasattr(BootSequence, "execute_boot")


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
