"""ADG-driven tests for agentic_core/L5_safety/validators/dependency_healing_integration_types.py — fan_in=2.

Contract tests: DependencyPruningStrategy constants, init, and can_heal.
"""
from __future__ import annotations

from pathlib import Path

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

_emit_records_execution_trace("p0", "evidence", "test_dependency_healing_integration_types_adg")
_emit_applies_guardrail("p0", "test_dependency_healing_integration_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_dependency_healing_integration_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_dependency_healing_integration_types_adg", "state_snapshot")
emit_replay_key("p0", "test_dependency_healing_integration_types_adg")
emit_determinism_digest("p0", "test_dependency_healing_integration_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.validators.dependency_healing_integration_types import (
    DependencyPruningStrategy,
    HealingStrategyProtocol,
)


class TestHealingStrategyProtocol:
    def test_protocol_importable(self):
        assert callable(HealingStrategyProtocol)


class TestDependencyPruningStrategyConstants:
    def test_supported_violations_nonempty(self):
        assert len(DependencyPruningStrategy.SUPPORTED_VIOLATIONS) > 0

    def test_is_frozenset(self):
        assert isinstance(DependencyPruningStrategy.SUPPORTED_VIOLATIONS, frozenset)

    def test_unused_dependency_supported(self):
        assert "unused_dependency" in DependencyPruningStrategy.SUPPORTED_VIOLATIONS


class TestDependencyPruningStrategyInit:
    def test_creates_without_args(self):
        s = DependencyPruningStrategy()
        assert s is not None

    def test_creates_with_path(self):
        s = DependencyPruningStrategy(project_root=Path("."))
        assert s.project_root == Path(".")

    def test_not_initialized_on_create(self):
        s = DependencyPruningStrategy()
        assert s._initialized is False

    def test_agent_none_on_create(self):
        s = DependencyPruningStrategy()
        assert s._agent is None

    def test_default_project_root_is_path(self):
        s = DependencyPruningStrategy()
        assert isinstance(s.project_root, Path)


class TestDependencyPruningStrategyCanHeal:
    def test_can_heal_supported_violation(self):
        s = DependencyPruningStrategy()
        assert s.can_heal({"type": "unused_dependency"}) is True

    def test_can_heal_unsupported_violation(self):
        s = DependencyPruningStrategy()
        assert s.can_heal({"type": "totally_unknown_violation_xyz"}) is False

    def test_can_heal_empty_dict(self):
        s = DependencyPruningStrategy()
        assert s.can_heal({}) is False

    def test_can_heal_dependency_bloat(self):
        s = DependencyPruningStrategy()
        assert s.can_heal({"type": "dependency_bloat"}) is True
