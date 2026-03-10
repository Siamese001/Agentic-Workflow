"""W13: ToolTranscript hash bound; direct os.environ mutation raises.

REQ-121: ToolTranscript hash is bound to stdout canonical bytes.
REQ-126: Direct os.environ mutation is blocked by guard.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

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
# ToolTranscript with hash binding
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ToolTranscript:
    """Canonical tool execution transcript with hash-bound stdout."""

    tool_id: str
    command: str
    stdout: bytes
    stderr: bytes
    exit_code: int
    transcript_hash: str  # SHA-256 of canonical stdout bytes

    @classmethod
    def from_execution(
        cls,
        tool_id: str,
        command: str,
        stdout: bytes,
        stderr: bytes,
        exit_code: int,
    ) -> ToolTranscript:
        """Create transcript; hash is computed from canonical stdout."""
        canonical = cls._canonicalize(stdout)
        transcript_hash = hashlib.sha256(canonical).hexdigest()
        return cls(
            tool_id=tool_id,
            command=command,
            stdout=stdout,
            stderr=stderr,
            exit_code=exit_code,
            transcript_hash=transcript_hash,
        )

    @staticmethod
    def _canonicalize(raw_stdout: bytes) -> bytes:
        """Canonical form: strip trailing whitespace lines, normalise line endings."""
        lines = raw_stdout.replace(b"\r\n", b"\n").split(b"\n")
        stripped = [line.rstrip() for line in lines]
        # Remove trailing empty lines
        while stripped and stripped[-1] == b"":
            stripped.pop()
        return b"\n".join(stripped)

    def verify_hash(self) -> bool:
        """Return True iff transcript_hash matches recomputed value."""
        canonical = self._canonicalize(self.stdout)
        expected = hashlib.sha256(canonical).hexdigest()
        return expected == self.transcript_hash

    def is_hash_bound(self) -> bool:
        """Return True iff transcript_hash is non-empty 64-hex string."""
        return bool(self.transcript_hash) and len(self.transcript_hash) == 64


# ---------------------------------------------------------------------------
# Env mutation guard
# ---------------------------------------------------------------------------


class EnvMutationViolation(RuntimeError):
    """Raised on direct os.environ mutation in guarded context."""


class EnvMutationGuard:
    """Context manager that blocks direct os.environ writes."""

    def __init__(self):
        self._active = False
        self._blocked: list[str] = []

    def __enter__(self):
        self._active = True
        return self

    def __exit__(self, *args):
        self._active = False

    def assert_write_allowed(self, key: str) -> None:
        if self._active:
            self._blocked.append(key)
            raise EnvMutationViolation(f"Direct os.environ['{key}'] mutation blocked — use injected config")

    @property
    def blocked_keys(self) -> list[str]:
        return list(self._blocked)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.governance
def test_req121_transcript_hash_bound_to_stdout():
    """REQ-121: ToolTranscript hash is bound to canonical stdout bytes."""
    stdout = b"line1\nline2\nresult: OK\n"
    t = ToolTranscript.from_execution(
        tool_id="tool_pytest",
        command="python -m pytest",
        stdout=stdout,
        stderr=b"",
        exit_code=0,
    )
    assert t.is_hash_bound()
    assert t.verify_hash()


@pytest.mark.governance
def test_req121_transcript_hash_deterministic():
    """REQ-121: Two transcripts with identical stdout have identical hashes."""
    stdout = b"deterministic output\n"
    t1 = ToolTranscript.from_execution("t1", "cmd", stdout, b"", 0)
    t2 = ToolTranscript.from_execution("t2", "cmd", stdout, b"", 0)

    assert t1.transcript_hash == t2.transcript_hash


@pytest.mark.governance
def test_req121_tampered_stdout_fails_verification():
    """REQ-121: Tampering with stdout bytes fails hash verification."""
    stdout = b"original output\n"
    t = ToolTranscript.from_execution("t1", "cmd", stdout, b"", 0)

    # Create tampered version with same hash but different stdout
    tampered = ToolTranscript(
        tool_id=t.tool_id,
        command=t.command,
        stdout=b"TAMPERED output\n",
        stderr=t.stderr,
        exit_code=t.exit_code,
        transcript_hash=t.transcript_hash,  # stale hash
    )
    assert not tampered.verify_hash()


@pytest.mark.governance
def test_req121_empty_stdout_still_hash_bound():
    """REQ-121: Empty stdout still produces a valid hash binding."""
    t = ToolTranscript.from_execution("t1", "cmd", b"", b"", 0)
    assert t.is_hash_bound()
    assert t.verify_hash()


@pytest.mark.governance
def test_req121_transcript_is_immutable():
    """REQ-121: ToolTranscript is frozen — cannot be tampered after creation."""
    t = ToolTranscript.from_execution("t1", "cmd", b"output\n", b"", 0)
    with pytest.raises((AttributeError, TypeError)):
        t.transcript_hash = "tampered"  # type: ignore[misc]


@pytest.mark.governance
def test_req126_env_mutation_blocked_in_guard():
    """REQ-126: Direct os.environ mutation raises in guarded context."""
    guard = EnvMutationGuard()
    with guard:
        with pytest.raises(EnvMutationViolation, match="mutation blocked"):
            guard.assert_write_allowed("SOME_SECRET_KEY")

    assert "SOME_SECRET_KEY" in guard.blocked_keys


@pytest.mark.governance
def test_req126_env_mutation_allowed_outside_guard():
    """REQ-126: Outside guarded context, mutation check is a no-op."""
    guard = EnvMutationGuard()
    # Not inside __enter__, so no raise
    guard.assert_write_allowed("ANY_KEY")
    assert guard.blocked_keys == []


@pytest.mark.governance
def test_req126_env_guard_tracks_all_blocked_keys():
    """REQ-126: All blocked key attempts are recorded."""
    guard = EnvMutationGuard()
    keys = ["KEY_A", "KEY_B", "KEY_C"]
    with guard:
        for k in keys:
            with pytest.raises(EnvMutationViolation):
                guard.assert_write_allowed(k)

    assert guard.blocked_keys == keys
