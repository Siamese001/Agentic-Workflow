"""Smoke tests for DeferredLoader behavior after bounded-release hardening."""

from __future__ import annotations

import threading
import time

from tools.mcp.mcp_deferred_loader import DeferredLoader


def test_basic_get():
    loader = DeferredLoader("basic", lambda: 42, timeout=5)
    assert loader.get() == 42


def test_call_serialized_basic():
    loader = DeferredLoader("serial", lambda: 100, timeout=5)
    loader.get()
    assert loader.call_serialized(lambda r: r * 2, call_timeout=3, op_name="double") == 200


def test_call_serialized_fail_fast_when_resource_not_loaded():
    loader = DeferredLoader("slow", lambda: (time.sleep(10), 99)[1], timeout=15)
    started = time.monotonic()
    try:
        loader.call_serialized(lambda r: r, wait_timeout=0, call_timeout=3, op_name="fast-fail")
    except RuntimeError:
        elapsed = time.monotonic() - started
        assert elapsed < 1.0
    else:
        raise AssertionError("Expected RuntimeError when resource is not yet loaded")


def test_serialization_order_is_enforced():
    loader = DeferredLoader("concurrent", lambda: "model", timeout=5)
    loader.get()
    results: list[str] = []

    def serial_call(idx: int) -> None:
        result = loader.call_serialized(
            lambda model: (time.sleep(0.2), f"{model}-{idx}")[1],
            call_timeout=5,
            op_name=f"call-{idx}",
        )
        results.append(result)

    threads = [threading.Thread(target=serial_call, args=(i,)) for i in range(3)]
    start = time.monotonic()
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    elapsed = time.monotonic() - start

    assert len(results) == 3
    assert elapsed >= 0.6


def test_timeout_force_releases_lock():
    blocker = threading.Event()
    loader = DeferredLoader("timeout", lambda: "model", timeout=5)
    loader.get()

    def long_call():
        try:
            loader.call_serialized(
                lambda _model: blocker.wait(60),
                call_timeout=0.1,
                op_name="long-call",
            )
        except TimeoutError:
            return

    thread = threading.Thread(target=long_call)
    thread.start()
    thread.join()

    time.sleep(loader._QUARANTINE_RELEASE_TIMEOUT + 0.2)  # noqa: SLF001 - explicit behavioral probe
    result = loader.call_serialized(lambda model: f"{model}-ok", call_timeout=1, op_name="follow-up")
    assert result == "model-ok"
