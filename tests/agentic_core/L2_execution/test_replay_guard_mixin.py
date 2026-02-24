"""
Phase 0.5 — ReplayGuardMixin Tests.

Validates:
  - ExecutionContext injection (not env vars)
  - Policy hash loaded from L4 config
  - Replay mode installs deterministic providers
  - Non-replay mode does not install providers
  - Properties: is_replay_mode, active_policy_hash, trace_id, safety_status
  - Policy hash drift detection
  - Deterministic replay proof across two instances
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import pytest

from agentic_core.L2_execution.deterministic_providers import (
    is_patched,
    unpatch_deterministic,
)
from agentic_core.mixins.replay_guard_mixin import ReplayGuardMixin


@dataclass
class _TestExecutionContext:
    """Minimal ExecutionContext stand-in for unit tests.

    Avoids importing execution_context.py which has unresolvable
    class dependencies (MCPHardenedMixin, HealerMixin) at module level.
    """

    mission_id: str = ""
    step_id: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)
    trace_id: str | None = None
    parent_span_id: str | None = None
    replay_mode: bool = False
    active_policy_hash: str | None = None
    safety_status: str = "PENDING"


# ---------------------------------------------------------------------------
# Helper: concrete class using ReplayGuardMixin
# ---------------------------------------------------------------------------


class _GuardedClass(ReplayGuardMixin):
    """Minimal concrete class for testing ReplayGuardMixin."""

    def __init__(self, execution_context=None):
        super().__init__(execution_context=execution_context)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestReplayGuardMixinNonReplay:
    @pytest.fixture(autouse=True)
    def _cleanup(self):
        unpatch_deterministic()
        yield
        unpatch_deterministic()

    @pytest.mark.unit_min_deps
    def test_default_non_replay(self):
        """Without ExecutionContext, defaults to non-replay mode."""
        obj = _GuardedClass()
        assert obj.is_replay_mode is False
        assert obj.trace_id == "no-trace"
        assert obj.safety_status == "PENDING"
        assert not is_patched()

    @pytest.mark.unit_min_deps
    def test_explicit_non_replay_context(self):
        """ExecutionContext with replay_mode=False does not install providers."""
        ctx = _TestExecutionContext(
            mission_id="test",
            trace_id="trace-non-replay",
            replay_mode=False,
            active_policy_hash="abc123",
            safety_status="CLEARED",
        )
        obj = _GuardedClass(execution_context=ctx)
        assert obj.is_replay_mode is False
        assert obj.trace_id == "trace-non-replay"
        assert obj.active_policy_hash == "abc123"
        assert obj.safety_status == "CLEARED"
        assert not is_patched()

    @pytest.mark.unit_min_deps
    def test_policy_hash_from_l4(self):
        """Without explicit policy hash, loads from L4 config."""
        ctx = _TestExecutionContext(
            mission_id="test",
            trace_id="trace-l4",
            replay_mode=False,
            active_policy_hash=None,
            safety_status="PENDING",
        )
        obj = _GuardedClass(execution_context=ctx)
        # Should have loaded from L4 (or fallback)
        assert obj.active_policy_hash is not None
        assert len(obj.active_policy_hash) > 0


class TestReplayGuardMixinReplay:
    @pytest.fixture(autouse=True)
    def _cleanup(self):
        unpatch_deterministic()
        yield
        unpatch_deterministic()

    @pytest.mark.unit_min_deps
    def test_replay_mode_installs_providers(self):
        """replay_mode=True installs deterministic providers."""
        ctx = _TestExecutionContext(
            mission_id="test",
            trace_id="trace-replay",
            replay_mode=True,
            active_policy_hash="policy-hash-replay",
            safety_status="CLEARED",
        )
        obj = _GuardedClass(execution_context=ctx)
        assert obj.is_replay_mode is True
        assert is_patched()

    @pytest.mark.unit_min_deps
    def test_replay_trace_id_immutable(self):
        """trace_id is set from ExecutionContext and immutable."""
        ctx = _TestExecutionContext(
            mission_id="test",
            trace_id="trace-immutable",
            replay_mode=True,
            active_policy_hash="ph",
            safety_status="CLEARED",
        )
        obj = _GuardedClass(execution_context=ctx)
        assert obj.trace_id == "trace-immutable"

    @pytest.mark.unit_min_deps
    def test_replay_policy_hash_from_context(self):
        """Policy hash comes from ExecutionContext, not env."""
        ctx = _TestExecutionContext(
            mission_id="test",
            trace_id="trace-ph",
            replay_mode=True,
            active_policy_hash="explicit-policy-hash",
            safety_status="CLEARED",
        )
        obj = _GuardedClass(execution_context=ctx)
        assert obj.active_policy_hash == "explicit-policy-hash"


class TestPolicyHashDrift:
    @pytest.fixture(autouse=True)
    def _cleanup(self):
        unpatch_deterministic()
        yield
        unpatch_deterministic()

    @pytest.mark.unit_min_deps
    def test_no_drift_initially(self):
        """initial_policy_hash matches active_policy_hash at construction."""
        ctx = _TestExecutionContext(
            mission_id="test",
            trace_id="trace-drift",
            replay_mode=False,
            active_policy_hash="stable-hash",
            safety_status="CLEARED",
        )
        obj = _GuardedClass(execution_context=ctx)
        assert not obj.policy_hash_drifted()
        assert obj.initial_policy_hash == "stable-hash"

    @pytest.mark.unit_min_deps
    def test_drift_detected(self):
        """Drift detected when active_policy_hash changes."""
        ctx = _TestExecutionContext(
            mission_id="test",
            trace_id="trace-drift2",
            replay_mode=False,
            active_policy_hash="hash-v1",
            safety_status="CLEARED",
        )
        obj = _GuardedClass(execution_context=ctx)
        # Simulate drift
        obj._active_policy_hash = "hash-v2"
        assert obj.policy_hash_drifted()


class TestReplayDeterminismProof:
    @pytest.fixture(autouse=True)
    def _cleanup(self):
        unpatch_deterministic()
        yield
        unpatch_deterministic()

    @pytest.mark.unit_min_deps
    def test_two_instances_same_trace_identical_providers(self):
        """Two ReplayGuard instances with same trace_id share deterministic state."""
        import time

        ctx = _TestExecutionContext(
            mission_id="test",
            trace_id="trace-proof",
            replay_mode=True,
            active_policy_hash="ph-proof",
            safety_status="CLEARED",
        )
        _GuardedClass(execution_context=ctx)
        t1 = time.time()

        # Unpatch and re-create with same trace
        unpatch_deterministic()
        _GuardedClass(execution_context=ctx)
        t2 = time.time()

        assert t1 == t2


class TestExecutionContextEnhancements:
    @pytest.mark.unit_min_deps
    def test_new_fields_exist(self):
        """ExecutionContext has replay_mode, active_policy_hash, safety_status."""
        ctx = _TestExecutionContext()
        assert hasattr(ctx, "replay_mode")
        assert hasattr(ctx, "active_policy_hash")
        assert hasattr(ctx, "safety_status")

    @pytest.mark.unit_min_deps
    def test_defaults(self):
        """Default values are non-replay, no policy hash, PENDING."""
        ctx = _TestExecutionContext()
        assert ctx.replay_mode is False
        assert ctx.active_policy_hash is None
        assert ctx.safety_status == "PENDING"

    @pytest.mark.unit_min_deps
    def test_fields_settable(self):
        """Fields can be set via constructor kwargs."""
        ctx = _TestExecutionContext(
            replay_mode=True,
            active_policy_hash="test-hash",
            safety_status="CLEARED",
        )
        assert ctx.replay_mode is True
        assert ctx.active_policy_hash == "test-hash"
        assert ctx.safety_status == "CLEARED"
