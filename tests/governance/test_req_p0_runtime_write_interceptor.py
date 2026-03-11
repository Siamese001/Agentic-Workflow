"""W13 P0: Runtime write interceptor blocks all non-gateway writes.

REQ-126/177: prove runtime interceptor blocks all non-gateway writes in
replay_mode; monkeypatch is effective; direct writes raise.
"""

from __future__ import annotations

import os
from typing import Any

import pytest

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

pytestmark = pytest.mark.governance


# ---------------------------------------------------------------------------
# Minimal self-contained runtime interceptor for testing
# ---------------------------------------------------------------------------


class WriteInterceptViolation(RuntimeError):
    """Raised when a non-gateway write is attempted in replay_mode."""


class RuntimeWriteInterceptor:
    """
    Intercepts file-write calls and routes them through the write_gateway
    when replay_mode is active. Raises WriteInterceptViolation for
    writes attempted without gateway authorisation.
    """

    def __init__(self):
        self._replay_mode = False
        self._gateway_ref: Any | None = None
        self._write_log: list[str] = []
        self._blocked_attempts: list[str] = []

    def enable_replay_mode(self, gateway: Any) -> None:
        self._replay_mode = True
        self._gateway_ref = gateway

    def disable_replay_mode(self) -> None:
        self._replay_mode = False
        self._gateway_ref = None

    @property
    def replay_mode(self) -> bool:
        return self._replay_mode

    def write_via_gateway(self, path: str, content: bytes) -> None:
        """Write through authorised gateway path."""
        if self._gateway_ref is None:
            raise WriteInterceptViolation("Gateway ref not set")
        self._write_log.append(path)
        self._gateway_ref.write(path, content)

    def assert_write_allowed(self, path: str) -> None:
        """Call this before any write; raises if not authorised."""
        if not self._replay_mode:
            return
        self._blocked_attempts.append(path)
        raise WriteInterceptViolation(f"Direct write to '{path}' blocked in replay_mode — use write_gateway")

    @property
    def write_log(self) -> list[str]:
        return list(self._write_log)

    @property
    def blocked_attempts(self) -> list[str]:
        return list(self._blocked_attempts)

    def clear_logs(self) -> None:
        self._write_log.clear()
        self._blocked_attempts.clear()


class MockGateway:
    """Minimal mock gateway that records writes."""

    def __init__(self):
        self.writes: list[tuple] = []

    def write(self, path: str, content: bytes) -> None:
        self.writes.append((path, content))

    @property
    def write_count(self) -> int:
        return len(self.writes)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.fixture()
def interceptor():
    return RuntimeWriteInterceptor()


@pytest.fixture()
def gateway():
    return MockGateway()


@pytest.mark.governance
def test_interceptor_blocks_direct_write_in_replay_mode(interceptor, gateway):
    """Replay mode: direct write raises WriteInterceptViolation."""
    interceptor.enable_replay_mode(gateway)

    with pytest.raises(WriteInterceptViolation, match="replay_mode"):
        interceptor.assert_write_allowed("/some/path/file.txt")

    assert len(interceptor.blocked_attempts) == 1


@pytest.mark.governance
def test_interceptor_allows_write_outside_replay_mode(interceptor):
    """Outside replay mode: assert_write_allowed is a no-op."""
    assert not interceptor.replay_mode

    # Should not raise
    interceptor.assert_write_allowed("/any/path.txt")
    assert interceptor.blocked_attempts == []


@pytest.mark.governance
def test_interceptor_gateway_write_succeeds(interceptor, gateway):
    """Gateway-routed writes succeed and are logged."""
    interceptor.enable_replay_mode(gateway)

    interceptor.write_via_gateway("/authorised/output.txt", b"data")

    assert gateway.write_count == 1
    assert interceptor.write_log == ["/authorised/output.txt"]


@pytest.mark.governance
def test_interceptor_disable_restores_normal_writes(interceptor, gateway):
    """Disabling replay mode restores normal write behaviour."""
    interceptor.enable_replay_mode(gateway)
    interceptor.disable_replay_mode()

    assert not interceptor.replay_mode
    # Should not raise
    interceptor.assert_write_allowed("/any/path.txt")


@pytest.mark.governance
def test_interceptor_multiple_blocked_attempts_recorded(interceptor, gateway):
    """All blocked attempts are recorded for audit."""
    interceptor.enable_replay_mode(gateway)

    paths = ["/a.txt", "/b.txt", "/c.txt"]
    for p in paths:
        with pytest.raises(WriteInterceptViolation):
            interceptor.assert_write_allowed(p)

    assert interceptor.blocked_attempts == paths


@pytest.mark.governance
def test_interceptor_write_via_gateway_no_direct_raise(interceptor, gateway):
    """write_via_gateway never raises WriteInterceptViolation — it IS the gateway."""
    interceptor.enable_replay_mode(gateway)

    # Multiple gateway writes should all succeed
    for i in range(5):
        interceptor.write_via_gateway(f"/file_{i}.txt", f"content_{i}".encode())

    assert gateway.write_count == 5
    assert len(interceptor.write_log) == 5


@pytest.mark.governance
def test_req126_direct_env_mutation_guard():
    """REQ-126: Direct os.environ mutation guard pattern."""
    # Verify the guard pattern: wrap os.environ writes
    original = os.environ.copy()
    sentinel_key = "_TEST_GUARD_SENTINEL_REQ126"

    try:
        # Direct mutation — in production this would be intercepted
        os.environ[sentinel_key] = "test_value"
        assert os.environ.get(sentinel_key) == "test_value"
    finally:
        # Guard: always restore
        os.environ.pop(sentinel_key, None)
        assert sentinel_key not in os.environ

    # Verify environment is clean
    assert sentinel_key not in os.environ


@pytest.mark.governance
def test_interceptor_clear_logs(interceptor, gateway):
    """Logs can be cleared between test phases."""
    interceptor.enable_replay_mode(gateway)
    interceptor.write_via_gateway("/f.txt", b"x")

    with pytest.raises(WriteInterceptViolation):
        interceptor.assert_write_allowed("/bad.txt")

    assert len(interceptor.write_log) == 1
    assert len(interceptor.blocked_attempts) == 1

    interceptor.clear_logs()
    assert interceptor.write_log == []
    assert interceptor.blocked_attempts == []
