"""Unit tests for agentic_core.L4_state.uwg.durable_write_gateway.

W1 (plan adg-testing-hotspots-wave-plan-a7f3c1) — Core P1 state surface.
``durable_write_gateway`` (fan_in=27, L4_STATE) is the sole admission gateway for
durable L4 mutations (UWG). Behavioral coverage of the write-lock contention
manager, the direct-write rejection path (authority firewall), and the
process-default singleton.
"""

from __future__ import annotations

import threading
from contextlib import contextmanager
from typing import Iterator

import pytest

from agentic_core.L4_state.uwg.durable_write_gateway import (
    DurableWriteGateway,
    UWGAuthorityError,
    UWGContentionError,
    _WriteLockManager,
    get_default_gateway,
    reset_default_gateway,
)


class TestExceptions:
    def test_authority_error_is_runtimeerror(self) -> None:
        assert issubclass(UWGAuthorityError, RuntimeError)

    def test_contention_error_is_runtimeerror(self) -> None:
        assert issubclass(UWGContentionError, RuntimeError)


@contextmanager
def _held_in_other_thread(mgr: _WriteLockManager, surfaces: list[str], owner: str) -> Iterator[None]:
    """Hold ``surfaces`` locked in a separate thread for the block's duration.

    RLock is reentrant per-thread, so contention only manifests across threads.
    """
    acquired = threading.Event()
    release = threading.Event()

    def _holder() -> None:
        ok, _ = mgr.acquire(target_surfaces=surfaces, owner=owner)
        assert ok is True
        acquired.set()
        release.wait(timeout=5)
        mgr.release(target_surfaces=surfaces, owner=owner)

    t = threading.Thread(target=_holder, daemon=True)
    t.start()
    assert acquired.wait(timeout=5)
    try:
        yield
    finally:
        release.set()
        t.join(timeout=5)


class TestWriteLockManager:
    def test_acquire_free_surface(self) -> None:
        mgr = _WriteLockManager()
        acquired, contentions = mgr.acquire(target_surfaces=["s1"], owner="o1")
        assert acquired is True
        assert contentions == []

    def test_cross_thread_contention(self) -> None:
        mgr = _WriteLockManager()
        with _held_in_other_thread(mgr, ["s1"], "o1"):
            acquired, contentions = mgr.acquire(target_surfaces=["s1"], owner="o2")
        assert acquired is False
        assert contentions == ["s1"]

    def test_release_allows_reacquire(self) -> None:
        mgr = _WriteLockManager()
        with _held_in_other_thread(mgr, ["s1"], "o1"):
            pass  # released on exit
        acquired, contentions = mgr.acquire(target_surfaces=["s1"], owner="o2")
        assert acquired is True
        assert contentions == []

    def test_partial_contention_rolls_back(self) -> None:
        mgr = _WriteLockManager()
        with _held_in_other_thread(mgr, ["s2"], "o1"):
            # o2 wants s1 (free) + s2 (held by other thread) → must fail
            acquired, contentions = mgr.acquire(target_surfaces=["s1", "s2"], owner="o2")
            assert acquired is False
            assert contentions == ["s2"]
            # s1 must have been rolled back → a fresh owner can take it
            acquired2, _ = mgr.acquire(target_surfaces=["s1"], owner="o3")
            assert acquired2 is True


class TestRejectDirectWrite:
    def test_returns_blocked_receipt_with_authority_rule(self) -> None:
        gw = DurableWriteGateway()
        receipt = gw.reject_direct_write(
            attempting_surface="L2_executor",
            target_surface="L4_memory",
            reason="direct_write_forbidden",
        )
        assert "direct_write_forbidden" in receipt.blocked_reason_codes
        assert "non_uwg_surface_blocked" in receipt.blocked_reason_codes
        assert receipt.failed_rule_ids == ("UWG_AUTHORITY_REQUIRED",)
        assert receipt.state_surfaces_requested == ("L4_memory",)

    def test_blocked_receipt_is_retrievable(self) -> None:
        gw = DurableWriteGateway()
        receipt = gw.reject_direct_write(
            attempting_surface="L6_learning",
            target_surface="L4_policy",
            reason="learning_firewall",
        )
        rid = receipt.blocked_commit_receipt_id
        assert gw.get_blocked_receipt(rid) is receipt
        assert receipt in gw.list_direct_write_blocks()

    def test_unknown_receipt_id_returns_none(self) -> None:
        gw = DurableWriteGateway()
        assert gw.get_blocked_receipt("does-not-exist") is None
        assert gw.get_commit_receipt("does-not-exist") is None


class TestDefaultGateway:
    def test_singleton_identity(self) -> None:
        reset_default_gateway()
        a = get_default_gateway()
        b = get_default_gateway()
        assert a is b

    def test_reset_replaces_instance(self) -> None:
        a = get_default_gateway()
        reset_default_gateway()
        b = get_default_gateway()
        assert a is not b
