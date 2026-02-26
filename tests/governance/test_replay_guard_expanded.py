"""
Tests for expanded ReplayGuard kernel-level nondeterminism interception.

Phase 2.1: Mathematically-Sealed Sovereignty Hardening
"""

from __future__ import annotations

import os
import random
import socket
import subprocess
import threading

import pytest

pytestmark = pytest.mark.governance

from agentic_core.L2_execution.determinism.replay_guard import (
    ReplayGuard,
    ReplayViolation,
)


class TestReplayGuardSocket:
    def test_blocks_socket_creation(self) -> None:
        with ReplayGuard():
            with pytest.raises(ReplayViolation, match="socket"):
                socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def test_socket_restored_after_context(self) -> None:
        with ReplayGuard():
            pass
        # Should not raise outside context
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.close()


class TestReplayGuardSubprocess:
    def test_blocks_subprocess_run(self) -> None:
        with ReplayGuard():
            with pytest.raises(ReplayViolation, match="subprocess"):
                subprocess.run(["echo", "hello"])

    def test_blocks_os_system(self) -> None:
        with ReplayGuard():
            with pytest.raises(ReplayViolation, match="os.system"):
                os.system("echo hello")

    def test_subprocess_restored_after_context(self) -> None:
        with ReplayGuard():
            pass
        result = subprocess.run(["python", "-c", "print('ok')"], capture_output=True)
        assert result.returncode == 0


class TestReplayGuardFilesystem:
    def test_blocks_file_write(self, tmp_path) -> None:
        with ReplayGuard():
            with pytest.raises(ReplayViolation, match="write"):
                open(str(tmp_path / "test.txt"), "w")

    def test_blocks_file_append(self, tmp_path) -> None:
        with ReplayGuard():
            with pytest.raises(ReplayViolation, match="write"):
                open(str(tmp_path / "test.txt"), "a")

    def test_allows_file_read(self, tmp_path) -> None:
        test_file = tmp_path / "read.txt"
        test_file.write_text("content")
        with ReplayGuard():
            with open(str(test_file)) as f:
                assert f.read() == "content"

    def test_open_restored_after_context(self, tmp_path) -> None:
        with ReplayGuard():
            pass
        path = tmp_path / "after.txt"
        with open(str(path), "w") as f:
            f.write("ok")
        assert path.read_text() == "ok"


class TestReplayGuardThreading:
    def test_blocks_thread_start(self) -> None:
        results = []

        def worker():
            results.append(1)

        with ReplayGuard():
            t = threading.Thread(target=worker)
            with pytest.raises(ReplayViolation, match="threading"):
                t.start()

    def test_threading_restored_after_context(self) -> None:
        results = []

        def worker():
            results.append(1)

        with ReplayGuard():
            pass
        t = threading.Thread(target=worker)
        t.start()
        t.join()
        assert results == [1]


class TestReplayGuardRandom:
    def test_random_is_deterministic_with_seed(self) -> None:
        with ReplayGuard(deterministic_seed=42):
            v1 = random.random()
        with ReplayGuard(deterministic_seed=42):
            v2 = random.random()
        assert v1 == v2

    def test_different_seeds_give_different_values(self) -> None:
        with ReplayGuard(deterministic_seed=1):
            v1 = random.random()
        with ReplayGuard(deterministic_seed=2):
            v2 = random.random()
        assert v1 != v2

    def test_random_restored_after_context(self) -> None:
        # random should work normally after context exit
        with ReplayGuard():
            pass
        v = random.random()
        assert 0.0 <= v < 1.0


class TestReplayGuardContextManager:
    def test_exception_in_context_restores_patches(self, tmp_path) -> None:
        try:
            with ReplayGuard():
                raise ValueError("test error")
        except ValueError:
            pass
        # Patching should be fully restored
        path = tmp_path / "recovery.txt"
        with open(str(path), "w") as f:
            f.write("ok")
        assert path.read_text() == "ok"
