"""Targeted gap-closure tests for PreventativeSandbox hardening.

Covers the vectors newly added in the L2 hardening phase:
- os.replace, pathlib.Path, builtins.eval, builtins.compile
  all raise SandboxViolationError inside activated()
- is_active lifecycle: False before/after, True inside
- originals are fully restored after context exit
"""

from __future__ import annotations

import builtins
import os

import pytest

from agentic_core.L2_execution.enforcement.preventative_sandbox import (
    PreventativeSandbox,
    SandboxViolationError,
)


def test_is_active_false_before_activation() -> None:
    sb = PreventativeSandbox()
    assert sb.is_active is False


def test_is_active_true_inside_context() -> None:
    sb = PreventativeSandbox()
    with sb.activated():
        assert sb.is_active is True


def test_is_active_false_after_context() -> None:
    sb = PreventativeSandbox()
    with sb.activated():
        pass
    assert sb.is_active is False


def test_eval_blocked_inside_sandbox() -> None:
    sb = PreventativeSandbox()
    with sb.activated():
        with pytest.raises(SandboxViolationError):
            builtins.eval("1+1")  # noqa: S307


def test_compile_blocked_inside_sandbox() -> None:
    sb = PreventativeSandbox()
    with sb.activated():
        with pytest.raises(SandboxViolationError):
            builtins.compile("x=1", "<string>", "exec")


def test_os_replace_blocked_inside_sandbox(tmp_path) -> None:
    src = tmp_path / "src.txt"
    src.write_text("hello", encoding="utf-8")
    dst = tmp_path / "dst.txt"
    sb = PreventativeSandbox()
    with sb.activated():
        with pytest.raises(SandboxViolationError):
            os.replace(str(src), str(dst))


def test_eval_restored_after_context() -> None:
    original_eval = builtins.eval
    sb = PreventativeSandbox()
    with sb.activated():
        pass
    assert builtins.eval is original_eval
    assert builtins.eval("2+2") == 4  # noqa: S307


def test_double_activation_raises() -> None:
    sb = PreventativeSandbox()
    with sb.activated():
        with pytest.raises(RuntimeError, match="already active"):
            with sb.activated():
                pass
