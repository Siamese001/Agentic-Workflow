"""
Phase 0.5 — Deterministic Providers Tests.

Validates:
  - FixedTimeProvider determinism from trace_id
  - DeterministicRandomSource reproducibility
  - DeterministicUUIDProvider monotonic sequence
  - patch_deterministic / unpatch_deterministic lifecycle
  - One-trace-per-process invariant (DeterministicPatchError)
  - Idempotent patching with same trace_id
"""

from __future__ import annotations

import random
import time
import uuid

import pytest

from agentic_core.L2_execution.deterministic_providers import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    DeterministicPatchError,
    DeterministicRandomSource,
    DeterministicUUIDProvider,
    FixedTimeProvider,
    is_patched,
    patch_deterministic,
    unpatch_deterministic,
)

# ---------------------------------------------------------------------------
# FixedTimeProvider
# ---------------------------------------------------------------------------


class TestFixedTimeProvider:
    @pytest.mark.unit_min_deps
    def test_deterministic_from_trace_id(self):
        """Same trace_id produces identical base time."""
        a = FixedTimeProvider("trace-abc")
        b = FixedTimeProvider("trace-abc")
        assert a.time() == b.time()

    @pytest.mark.unit_min_deps
    def test_different_trace_id_different_time(self):
        """Different trace_ids produce different base times."""
        a = FixedTimeProvider("trace-1")
        b = FixedTimeProvider("trace-2")
        assert a.time() != b.time()

    @pytest.mark.unit_min_deps
    def test_sleep_advances_clock(self):
        """sleep() advances virtual clock monotonically."""
        p = FixedTimeProvider("trace-sleep")
        t0 = p.time()
        p.sleep(DEFAULT_SLEEP)
        t1 = p.time()
        assert t1 == t0 + 1.5

    @pytest.mark.unit_min_deps
    def test_advance_advances_clock(self):
        """advance() advances virtual clock."""
        p = FixedTimeProvider("trace-advance")
        t0 = p.time()
        p.advance(3.0)
        assert p.time() == t0 + 3.0

    @pytest.mark.unit_min_deps
    def test_negative_sleep_raises(self):
        """Negative sleep duration raises ValueError."""
        p = FixedTimeProvider("trace-neg")
        with pytest.raises(ValueError):
            p.sleep(-1.0)

    @pytest.mark.unit_min_deps
    def test_negative_advance_raises(self):
        """Negative advance duration raises ValueError."""
        p = FixedTimeProvider("trace-neg")
        with pytest.raises(ValueError):
            p.advance(-1.0)

    @pytest.mark.unit_min_deps
    def test_current_offset_property(self):
        """current_offset reflects accumulated advances."""
        p = FixedTimeProvider("trace-offset")
        assert p.current_offset == 0.0
        p.sleep(DEFAULT_SLEEP)
        p.advance(1.0)
        assert p.current_offset == 3.0


# ---------------------------------------------------------------------------
# DeterministicRandomSource
# ---------------------------------------------------------------------------


class TestDeterministicRandomSource:
    @pytest.mark.unit_min_deps
    def test_reproducible_sequence(self):
        """Same trace_id produces identical random sequence."""
        a = DeterministicRandomSource("trace-rng")
        b = DeterministicRandomSource("trace-rng")
        seq_a = [a.random() for _ in range(10)]
        seq_b = [b.random() for _ in range(10)]
        assert seq_a == seq_b

    @pytest.mark.unit_min_deps
    def test_different_trace_different_sequence(self):
        """Different trace_ids produce different sequences."""
        a = DeterministicRandomSource("trace-x")
        b = DeterministicRandomSource("trace-y")
        seq_a = [a.random() for _ in range(10)]
        seq_b = [b.random() for _ in range(10)]
        assert seq_a != seq_b

    @pytest.mark.unit_min_deps
    def test_randint_range(self):
        """randint returns values within [a, b]."""
        src = DeterministicRandomSource("trace-randint")
        for _ in range(50):
            val = src.randint(1, 10)
            assert 1 <= val <= 10

    @pytest.mark.unit_min_deps
    def test_choice_from_sequence(self):
        """choice returns element from provided sequence."""
        src = DeterministicRandomSource("trace-choice")
        options = ["a", "b", "c"]
        for _ in range(20):
            assert src.choice(options) in options

    @pytest.mark.unit_min_deps
    def test_shuffle_deterministic(self):
        """shuffle produces identical result for same trace_id."""
        a = DeterministicRandomSource("trace-shuffle")
        b = DeterministicRandomSource("trace-shuffle")
        list_a = [1, 2, 3, 4, 5]
        list_b = [1, 2, 3, 4, 5]
        a.shuffle(list_a)
        b.shuffle(list_b)
        assert list_a == list_b


# ---------------------------------------------------------------------------
# DeterministicUUIDProvider
# ---------------------------------------------------------------------------


class TestDeterministicUUIDProvider:
    @pytest.mark.unit_min_deps
    def test_reproducible_uuid_sequence(self):
        """Same trace_id produces identical UUID sequence."""
        a = DeterministicUUIDProvider("trace-uuid")
        b = DeterministicUUIDProvider("trace-uuid")
        seq_a = [a.uuid4() for _ in range(5)]
        seq_b = [b.uuid4() for _ in range(5)]
        assert seq_a == seq_b

    @pytest.mark.unit_min_deps
    def test_monotonic_increment(self):
        """Sequential UUIDs are distinct."""
        p = DeterministicUUIDProvider("trace-mono")
        uuids = [p.uuid4() for _ in range(10)]
        assert len(set(uuids)) == 10

    @pytest.mark.unit_min_deps
    def test_uuid_version_4(self):
        """Generated UUIDs have version 4."""
        p = DeterministicUUIDProvider("trace-v4")
        u = p.uuid4()
        assert u.version == 4


# ---------------------------------------------------------------------------
# Patching lifecycle
# ---------------------------------------------------------------------------


class TestPatchLifecycle:
    @pytest.fixture(autouse=True)
    def _ensure_unpatched(self):
        """Ensure deterministic providers are unpatched before and after each test."""
        unpatch_deterministic()
        yield
        unpatch_deterministic()

    @pytest.mark.unit_min_deps
    def test_patch_installs_providers(self):
        """patch_deterministic replaces time/random/uuid modules."""
        original_time = time.time
        patch_deterministic("trace-patch")
        assert is_patched()
        assert time.time is not original_time

    @pytest.mark.unit_min_deps
    def test_unpatch_restores_originals(self):
        """unpatch_deterministic restores original modules."""
        original_time = time.time
        patch_deterministic("trace-unpatch")
        unpatch_deterministic()
        assert not is_patched()
        assert time.time is original_time

    @pytest.mark.unit_min_deps
    def test_idempotent_same_trace(self):
        """Patching with same trace_id is idempotent."""
        patch_deterministic("trace-idem")
        patch_deterministic("trace-idem")  # Should not raise
        assert is_patched()

    @pytest.mark.unit_min_deps
    def test_different_trace_raises(self):
        """Patching with different trace_id raises DeterministicPatchError."""
        patch_deterministic("trace-first")
        with pytest.raises(DeterministicPatchError):
            patch_deterministic("trace-second")

    @pytest.mark.unit_min_deps
    def test_unpatch_idempotent(self):
        """unpatch_deterministic is safe to call when not patched."""
        unpatch_deterministic()  # Should not raise
        assert not is_patched()

    @pytest.mark.unit_min_deps
    def test_patched_time_deterministic(self):
        """After patching, time.time() returns deterministic values."""
        patch_deterministic("trace-time-det")
        t1 = time.time()
        t2 = time.time()
        assert t1 == t2  # No real clock advancement

    @pytest.mark.unit_min_deps
    def test_patched_random_deterministic(self):
        """After patching, random.random() returns deterministic values."""
        patch_deterministic("trace-rand-det")
        r1 = random.random()
        unpatch_deterministic()
        patch_deterministic("trace-rand-det")
        r2 = random.random()
        assert r1 == r2

    @pytest.mark.unit_min_deps
    def test_patched_uuid_deterministic(self):
        """After patching, uuid.uuid4() returns deterministic values."""
        patch_deterministic("trace-uuid-det")
        u1 = uuid.uuid4()
        unpatch_deterministic()
        patch_deterministic("trace-uuid-det")
        u2 = uuid.uuid4()
        assert u1 == u2

    @pytest.mark.unit_min_deps
    def test_replay_determinism_proof(self):
        """Full replay determinism: same trace_id produces byte-identical outputs."""
        trace = "trace-replay-proof"

        # Run 1
        patch_deterministic(trace)
        run1_time = time.time()
        run1_rand = [random.random() for _ in range(5)]
        run1_uuid = uuid.uuid4()
        unpatch_deterministic()

        # Run 2
        patch_deterministic(trace)
        run2_time = time.time()
        run2_rand = [random.random() for _ in range(5)]
        run2_uuid = uuid.uuid4()
        unpatch_deterministic()

        assert run1_time == run2_time
        assert run1_rand == run2_rand
        assert run1_uuid == run2_uuid
