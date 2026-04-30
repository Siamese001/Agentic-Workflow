"""W6 contract tests: async substrate facade + cached AgenticRouter.

Locks in the W6 invariants:
1. ``GovernedAppRunner`` exposes ``run_governed_core_async`` as a coroutine.
2. ``run_governed_core_async`` returns the same record shape as the sync path.
3. ``GovernedAppRunner._get_router`` caches the ``AgenticRouter`` per instance
   (router constructed once, returned on subsequent calls — preserves bandit
   posterior state across calls).
4. The async helpers ``_l1_plan_async`` / ``_l0_route_async`` are coroutines.
5. ``asyncio.gather()`` of two ``run_governed_core_async`` calls on different
   runner instances completes cleanly (concurrent runs supported).

Plan ``apps-runtime-first-principles-e6ba58`` W6.1 + W6.2.
"""

from __future__ import annotations

import asyncio
import inspect
from typing import Any

import pytest

from apps_shared.integrations.governed_app_runner import (
    GovernedAppRunner,
    GovernedAppRunRecord,
)


# ---------------------------------------------------------------------------
# Helpers \u2014 minimal subclass for substrate testing
# ---------------------------------------------------------------------------


class _W6TestRunner(GovernedAppRunner):
    APP_NAME = "apps_w6_test"
    CAPABILITY_TOKEN = "apps_w6_test.governed_e2e.v1"
    ROUTING_TARGET = "w6_test_assembly"
    ROUTING_KEYWORDS = ["w6", "test"]


# ---------------------------------------------------------------------------
# Async public entrypoint contract
# ---------------------------------------------------------------------------


def test_run_governed_core_async_is_a_coroutine_function() -> None:
    """W6.1: ``run_governed_core_async`` is exposed as a coroutine function."""
    assert inspect.iscoroutinefunction(GovernedAppRunner.run_governed_core_async)


def test_run_governed_core_async_returns_governed_app_run_record() -> None:
    """W6.1: async facade returns the same record type as the sync path."""
    runner = _W6TestRunner(collection="w6_test_docs")
    rec = asyncio.run(runner.run_governed_core_async("w6 hello"))
    assert isinstance(rec, GovernedAppRunRecord)
    assert rec.app_name == "apps_w6_test"


def test_run_governed_core_async_matches_sync_shape() -> None:
    """W6.1: sync and async produce structurally equivalent records.

    Uses separate runner instances to avoid the recommended-pattern caveat
    (one runner per concurrent caller) and to keep accumulated L6 latency
    budgets isolated. The W6 contract is shape parity, not state sharing.
    """
    import dataclasses

    runner_sync = _W6TestRunner(collection="w6_test_docs")
    runner_async = _W6TestRunner(collection="w6_test_docs")
    sync_rec = runner_sync.run_governed_core("w6 sync probe")
    async_rec = asyncio.run(runner_async.run_governed_core_async("w6 async probe"))

    sync_fields = {f.name for f in dataclasses.fields(sync_rec)}
    async_fields = {f.name for f in dataclasses.fields(async_rec)}
    assert sync_fields == async_fields


# ---------------------------------------------------------------------------
# Cached AgenticRouter (W6.2)
# ---------------------------------------------------------------------------


def test_get_router_caches_router_across_calls() -> None:
    """W6.2: ``_get_router()`` returns the same instance on repeated calls."""
    runner = _W6TestRunner(collection="w6_test_docs")

    # Force a fresh cache slot.
    assert runner._cached_router is None

    first = runner._get_router()
    second = runner._get_router()

    # When AgenticRouter is importable, both calls return the same instance.
    # When AgenticRouter is unavailable, both return None \u2014 also acceptable
    # (the test environment did not satisfy the dependency).
    if first is not None:
        assert second is first, "router cache returned a different instance on second call"
    else:
        assert second is None


def test_get_router_does_not_reregister_target() -> None:
    """W6.2: target registration happens once \u2014 confirmed by checking the
    cache slot transitions from None to populated exactly once."""
    runner = _W6TestRunner(collection="w6_test_docs")

    assert runner._cached_router is None
    runner._get_router()
    cached_after_first = runner._cached_router
    runner._get_router()
    runner._get_router()
    assert runner._cached_router is cached_after_first


def test_separate_runner_instances_have_independent_routers() -> None:
    """W6.2: bandit posterior is per-runner \u2014 different instances do NOT
    share router state."""
    runner_a = _W6TestRunner(collection="w6_test_docs")
    runner_b = _W6TestRunner(collection="w6_test_docs")

    router_a = runner_a._get_router()
    router_b = runner_b._get_router()

    if router_a is not None and router_b is not None:
        assert router_a is not router_b


# ---------------------------------------------------------------------------
# Async-native helpers (W6.1 internal)
# ---------------------------------------------------------------------------


def test_l1_plan_async_is_a_coroutine_function() -> None:
    """W6.1: ``_l1_plan_async`` is async \u2014 callers can await it from inside an
    event loop without ``asyncio.run`` re-entry."""
    assert inspect.iscoroutinefunction(GovernedAppRunner._l1_plan_async)


def test_l0_route_async_is_a_coroutine_function() -> None:
    """W6.1: ``_l0_route_async`` is async \u2014 same rationale as L1."""
    assert inspect.iscoroutinefunction(GovernedAppRunner._l0_route_async)


def test_l0_route_async_uses_cached_router() -> None:
    """W6.1+W6.2: async L0 helper consumes the same cached router as sync."""
    import inspect as _inspect

    src = _inspect.getsource(GovernedAppRunner._l0_route_async)
    assert "_get_router" in src, "_l0_route_async must use _get_router cache"


# ---------------------------------------------------------------------------
# Concurrent run scenario \u2014 success criterion: \u22652 in flight
# ---------------------------------------------------------------------------


def test_two_concurrent_runs_complete_via_asyncio_gather() -> None:
    """W6.1 success criterion: \u22652 governed runs can be in flight concurrently."""

    async def _drive_two_runs() -> tuple[GovernedAppRunRecord, GovernedAppRunRecord]:
        runner_a = _W6TestRunner(collection="w6_test_docs")
        runner_b = _W6TestRunner(collection="w6_test_docs")
        return await asyncio.gather(
            runner_a.run_governed_core_async("concurrent run a"),
            runner_b.run_governed_core_async("concurrent run b"),
        )

    rec_a, rec_b = asyncio.run(_drive_two_runs())
    assert isinstance(rec_a, GovernedAppRunRecord)
    assert isinstance(rec_b, GovernedAppRunRecord)
    # Different runner instances must produce different correlation ids.
    assert rec_a.run_id != rec_b.run_id


# ---------------------------------------------------------------------------
# Sync regression: existing sync path still works
# ---------------------------------------------------------------------------


def test_sync_run_governed_core_still_works_after_w6() -> None:
    """W6 regression: legacy sync entrypoint MUST still succeed."""
    runner = _W6TestRunner(collection="w6_test_docs")
    rec = runner.run_governed_core("legacy sync")
    assert isinstance(rec, GovernedAppRunRecord)
    assert rec.app_name == "apps_w6_test"
