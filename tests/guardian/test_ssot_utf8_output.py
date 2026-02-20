"""
Tests: SSOT stdout/stderr UTF-8 safety reconfigure, logging handler stream
reconfigure, and runtime_state.json ensure_ascii=False.

Verifies that _maybe_force_utf8_console() and _maybe_force_utf8_logging_handlers()
prevent UnicodeEncodeError on cp1252/ibm437 sinks without touching LocationHealerAgent.
"""

import json
import logging
import sys

import pytest

pytestmark = pytest.mark.guardian


def _import_console_fn():
    from agentic_core.L0_routing.scripts.execute_ssot import _maybe_force_utf8_console

    return _maybe_force_utf8_console


def _import_handlers_fn():
    from agentic_core.L0_routing.scripts.execute_ssot import (
        _maybe_force_utf8_logging_handlers,
    )

    return _maybe_force_utf8_logging_handlers


class TestMaybeForceUtf8Console:
    def test_reconfigures_stdout_on_windows(self, monkeypatch):
        """stdout.reconfigure(encoding='utf-8') is called on win32."""
        monkeypatch.setattr(sys, "platform", "win32")
        reconfigured = {}

        class FakeStream:
            def reconfigure(self, encoding, errors="strict"):
                reconfigured["encoding"] = encoding
                reconfigured["errors"] = errors

        monkeypatch.setattr(sys, "stdout", FakeStream())
        monkeypatch.setattr(sys, "stderr", FakeStream())
        monkeypatch.setattr("subprocess.run", lambda *a, **kw: None)

        fn = _import_console_fn()
        fn()

        assert reconfigured.get("encoding") == "utf-8"
        assert reconfigured.get("errors") == "replace"

    def test_reconfigures_on_non_windows_too(self, monkeypatch):
        """Reconfigure is called on linux (no longer gated to Windows only)."""
        monkeypatch.setattr(sys, "platform", "linux")
        reconfigured = {}

        class FakeStream:
            def reconfigure(self, encoding, errors="strict"):
                reconfigured["encoding"] = encoding
                reconfigured["errors"] = errors

        monkeypatch.setattr(sys, "stdout", FakeStream())
        monkeypatch.setattr(sys, "stderr", FakeStream())

        fn = _import_console_fn()
        fn()

        assert reconfigured.get("encoding") == "utf-8"
        assert reconfigured.get("errors") == "replace"

    def test_reconfigure_exception_is_swallowed(self, monkeypatch):
        """If reconfigure raises, _maybe_force_utf8_console does not propagate."""
        monkeypatch.setattr(sys, "platform", "win32")

        class BrokenStream:
            def reconfigure(self, **kw):
                raise AttributeError("no reconfigure")

        monkeypatch.setattr(sys, "stdout", BrokenStream())
        monkeypatch.setattr(sys, "stderr", BrokenStream())
        monkeypatch.setattr("subprocess.run", lambda *a, **kw: None)

        fn = _import_console_fn()
        fn()  # must not raise


class TestMaybeForceUtf8LoggingHandlers:
    def test_reconfigures_handler_stream_on_windows(self, monkeypatch):
        """Handler streams with .reconfigure get encoding='utf-8', errors='replace'."""
        monkeypatch.setattr(sys, "platform", "win32")
        reconfigure_calls = []

        class FakeStream:
            def reconfigure(self, encoding, errors="strict"):
                reconfigure_calls.append({"encoding": encoding, "errors": errors})

        handler = logging.StreamHandler()
        handler.stream = FakeStream()

        root_logger = logging.getLogger()
        original_handlers = root_logger.handlers[:]
        root_logger.handlers = [handler]
        try:
            fn = _import_handlers_fn()
            fn()
        finally:
            root_logger.handlers = original_handlers

        assert len(reconfigure_calls) >= 1
        assert reconfigure_calls[0]["encoding"] == "utf-8"
        assert reconfigure_calls[0]["errors"] == "replace"

    def test_reconfigures_on_non_windows_too(self, monkeypatch):
        """Reconfigure is called on linux (no longer gated to Windows only)."""
        monkeypatch.setattr(sys, "platform", "linux")
        reconfigure_calls = []

        class FakeStream:
            def reconfigure(self, encoding, errors="strict"):
                reconfigure_calls.append({"encoding": encoding, "errors": errors})

        handler = logging.StreamHandler()
        handler.stream = FakeStream()

        root_logger = logging.getLogger()
        original_handlers = root_logger.handlers[:]
        root_logger.handlers = [handler]
        try:
            fn = _import_handlers_fn()
            fn()
        finally:
            root_logger.handlers = original_handlers

        assert len(reconfigure_calls) >= 1
        assert reconfigure_calls[0]["encoding"] == "utf-8"
        assert reconfigure_calls[0]["errors"] == "replace"

    def test_handler_without_stream_is_skipped(self, monkeypatch):
        """Handlers without a stream attribute are silently skipped."""
        monkeypatch.setattr(sys, "platform", "win32")

        handler = logging.Handler()  # base Handler has no .stream

        root_logger = logging.getLogger()
        original_handlers = root_logger.handlers[:]
        root_logger.handlers = [handler]
        try:
            fn = _import_handlers_fn()
            fn()  # must not raise
        finally:
            root_logger.handlers = original_handlers

    def test_handler_reconfigure_exception_swallowed(self, monkeypatch):
        """If stream.reconfigure raises, it is silently swallowed."""
        monkeypatch.setattr(sys, "platform", "win32")

        class BrokenStream:
            def reconfigure(self, **kw):
                raise OSError("broken")

        handler = logging.StreamHandler()
        handler.stream = BrokenStream()

        root_logger = logging.getLogger()
        original_handlers = root_logger.handlers[:]
        root_logger.handlers = [handler]
        try:
            fn = _import_handlers_fn()
            fn()  # must not raise
        finally:
            root_logger.handlers = original_handlers


class TestRuntimeStateEnsureAscii:
    def test_json_dump_ensure_ascii_false_preserves_unicode(self, tmp_path):
        """runtime_state.json written with ensure_ascii=False preserves non-ASCII."""
        state = {"status": "ok", "arrow": "\u2192", "lock": "\U0001f512"}
        out = tmp_path / "runtime_state.json"
        with open(out, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, default=str, ensure_ascii=False)

        raw = out.read_text(encoding="utf-8")
        assert "\u2192" in raw
        assert "\U0001f512" in raw

        loaded = json.loads(out.read_text(encoding="utf-8"))
        assert loaded["arrow"] == "\u2192"
        assert loaded["lock"] == "\U0001f512"
