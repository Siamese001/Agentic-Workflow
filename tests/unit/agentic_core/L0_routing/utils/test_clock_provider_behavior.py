"""Behavioral tests for ``agentic_core.L0_routing.utils.clock_provider.ClockProvider``.

Covers:
- Default behavior delegates to real ``datetime.now`` / ``time.time``.
- Timezone argument is forwarded to the injected ``_now_fn``.
- Monkey-patching ``_now_fn`` / ``_time_fn`` produces deterministic outputs.
- ``reset()`` restores real clock after test injection.
- Injection is class-scoped (singleton semantics).
"""

from __future__ import annotations

from collections.abc import Generator
from datetime import datetime, timezone

import pytest

from agentic_core.L0_routing.utils.clock_provider import ClockProvider


@pytest.fixture(autouse=True)
def _reset_clock() -> Generator[None, None, None]:
    """Ensure each test starts and ends with a real clock."""
    ClockProvider.reset()
    yield
    ClockProvider.reset()


class TestDefaultBehavior:
    def test_now_returns_datetime_instance(self) -> None:
        result = ClockProvider.now()
        assert isinstance(result, datetime)

    def test_time_returns_float(self) -> None:
        result = ClockProvider.time()
        assert isinstance(result, float)
        assert result > 0

    def test_now_naive_by_default(self) -> None:
        result = ClockProvider.now()
        # datetime.now() without tz returns a naive datetime
        assert result.tzinfo is None

    def test_now_with_utc_returns_aware(self) -> None:
        result = ClockProvider.now(timezone.utc)
        assert result.tzinfo is timezone.utc


class TestDeterministicInjection:
    def test_now_fn_injection(self) -> None:
        fixed = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        ClockProvider._now_fn = staticmethod(lambda *a, **kw: fixed)
        assert ClockProvider.now() == fixed
        assert ClockProvider.now(timezone.utc) == fixed

    def test_time_fn_injection(self) -> None:
        ClockProvider._time_fn = staticmethod(lambda: 1234567890.0)
        assert ClockProvider.time() == 1234567890.0

    def test_now_forwards_tz_to_injected_fn(self) -> None:
        captured: list[object] = []

        def fake_now(tz=None):  # noqa: ANN001
            captured.append(tz)
            return datetime(2026, 1, 1, tzinfo=tz) if tz else datetime(2026, 1, 1)

        ClockProvider._now_fn = staticmethod(fake_now)
        ClockProvider.now(timezone.utc)
        assert captured == [timezone.utc]

    def test_now_does_not_forward_tz_when_none(self) -> None:
        captured: list[tuple] = []

        def fake_now(*args, **kwargs):  # noqa: ANN002, ANN003
            captured.append((args, kwargs))
            return datetime(2026, 1, 1)

        ClockProvider._now_fn = staticmethod(fake_now)
        ClockProvider.now()
        # When tz is None, the provider must NOT forward it — it calls with no args
        assert captured == [((), {})]


class TestReset:
    def test_reset_restores_real_clock(self) -> None:
        ClockProvider._now_fn = staticmethod(lambda *a, **kw: datetime(1999, 1, 1))
        ClockProvider._time_fn = staticmethod(lambda: 0.0)
        assert ClockProvider.now() == datetime(1999, 1, 1)

        ClockProvider.reset()
        # After reset, wall-clock must be after epoch and not the frozen value
        assert ClockProvider.now() != datetime(1999, 1, 1)
        assert ClockProvider.time() > 1_000_000_000  # well past 2001

    def test_reset_is_idempotent(self) -> None:
        ClockProvider.reset()
        ClockProvider.reset()
        assert isinstance(ClockProvider.now(), datetime)


class TestSingletonSemantics:
    def test_injection_visible_across_callsites(self) -> None:
        """Class-level override is global — any caller sees the injected clock."""
        fixed = datetime(2026, 6, 15, 9, 30, tzinfo=timezone.utc)
        ClockProvider._now_fn = staticmethod(lambda *a, **kw: fixed)

        # Simulate two independent callsites
        t1 = ClockProvider.now(timezone.utc)
        t2 = ClockProvider.now(timezone.utc)
        assert t1 == t2 == fixed
