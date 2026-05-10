"""Unit tests for .windsurf/scripts/post_cascade_wave_lifecycle_capture.py.

Plan: notion-wave-lifecycle-autosync-f4a2b8 (W3.P3.1).

Network is fully mocked. NOTION_TOKEN is not required.
"""
from __future__ import annotations

import importlib
import io
import json
import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]
HOOK_PATH = REPO_ROOT / ".windsurf" / "scripts" / "post_cascade_wave_lifecycle_capture.py"


def _load_hook_module():
    """Load the hook as a module by file path so it can be exercised standalone."""
    sys.path.insert(0, str(REPO_ROOT / ".windsurf" / "scripts"))
    sys.path.insert(0, str(REPO_ROOT))
    spec = importlib.util.spec_from_file_location(
        "post_cascade_wave_lifecycle_capture", HOOK_PATH
    )
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules["post_cascade_wave_lifecycle_capture"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def hook_module():
    return _load_hook_module()


@pytest.fixture
def fake_stdin(monkeypatch):
    def _setter(text: str):
        monkeypatch.setattr(sys, "stdin", io.StringIO(text))

    return _setter


# ---------------------------------------------------------------------------
# _extract_response_text
# ---------------------------------------------------------------------------


class TestExtractResponseText:
    def test_string_payload_returned_as_is(self, hook_module):
        assert hook_module._extract_response_text("hello") == "hello"

    def test_dict_response_text_key(self, hook_module):
        out = hook_module._extract_response_text({"response_text": "abc"})
        assert out == "abc"

    def test_dict_text_fallback(self, hook_module):
        out = hook_module._extract_response_text({"text": "fallback"})
        assert out == "fallback"

    def test_dict_tool_info_response_text(self, hook_module):
        out = hook_module._extract_response_text({"tool_info": {"response_text": "nested"}})
        assert out == "nested"

    def test_unknown_payload_empty(self, hook_module):
        assert hook_module._extract_response_text(42) == ""
        assert hook_module._extract_response_text(None) == ""


# ---------------------------------------------------------------------------
# main() — bypass / no-stdin / empty-stdin paths
# ---------------------------------------------------------------------------


class TestMainBypass:
    def test_bypass_env_short_circuits(self, hook_module, monkeypatch):
        monkeypatch.setenv("WAVE_LIFECYCLE_CAPTURE_BYPASS", "1")
        # stdin would otherwise be consumed; ensure the hook returns 0 fast.
        with patch.object(hook_module.sys.stdin, "isatty", return_value=False):
            rc = hook_module.main()
        assert rc == 0

    def test_tty_stdin_returns_zero(self, hook_module, monkeypatch):
        monkeypatch.delenv("WAVE_LIFECYCLE_CAPTURE_BYPASS", raising=False)
        with patch.object(hook_module.sys.stdin, "isatty", return_value=True):
            rc = hook_module.main()
        assert rc == 0


# ---------------------------------------------------------------------------
# main() — happy path (stdin contains markers, writer applies them)
# ---------------------------------------------------------------------------


class TestMainMarkerProcessing:
    def test_markers_routed_to_writer(self, hook_module, monkeypatch, fake_stdin):
        monkeypatch.delenv("WAVE_LIFECYCLE_CAPTURE_BYPASS", raising=False)
        payload = json.dumps(
            {
                "response_text": (
                    "WAVE_COMPLETE: plan=demo-plan-abc123 wave=2\n"
                    "PLAN_COMPLETE: plan=demo-plan-abc123\n"
                )
            }
        )
        fake_stdin(payload)

        captured: dict = {}

        def fake_emit(text, *, dry_run=False):
            captured["text"] = text
            captured["dry_run"] = dry_run
            return [("demo-plan-abc123", True, "ok")]

        fake_writer = type("FakeWriter", (), {"emit_from_markers": staticmethod(fake_emit)})

        with patch.object(hook_module, "_load_writer", return_value=fake_writer), patch.object(
            hook_module.sys.stdin, "isatty", return_value=False
        ):
            rc = hook_module.main()

        assert rc == 0
        assert "WAVE_COMPLETE" in captured["text"]
        assert "PLAN_COMPLETE" in captured["text"]
        assert captured["dry_run"] is False

    def test_writer_failure_returns_zero(self, hook_module, monkeypatch, fake_stdin):
        monkeypatch.delenv("WAVE_LIFECYCLE_CAPTURE_BYPASS", raising=False)
        fake_stdin(json.dumps({"response_text": "WAVE_COMPLETE: plan=x-aaaaaa wave=1"}))

        def boom(text, *, dry_run=False):
            raise OSError("network down")

        fake_writer = type("FakeWriter", (), {"emit_from_markers": staticmethod(boom)})

        with patch.object(hook_module, "_load_writer", return_value=fake_writer), patch.object(
            hook_module.sys.stdin, "isatty", return_value=False
        ):
            rc = hook_module.main()

        assert rc == 0  # fail-soft

    def test_no_markers_returns_zero(self, hook_module, monkeypatch, fake_stdin):
        monkeypatch.delenv("WAVE_LIFECYCLE_CAPTURE_BYPASS", raising=False)
        fake_stdin(json.dumps({"response_text": "hello world, no markers here"}))

        def fake_emit(text, *, dry_run=False):
            return []

        fake_writer = type("FakeWriter", (), {"emit_from_markers": staticmethod(fake_emit)})

        with patch.object(hook_module, "_load_writer", return_value=fake_writer), patch.object(
            hook_module.sys.stdin, "isatty", return_value=False
        ):
            rc = hook_module.main()

        assert rc == 0

    def test_writer_import_failure_returns_zero(self, hook_module, monkeypatch, fake_stdin):
        monkeypatch.delenv("WAVE_LIFECYCLE_CAPTURE_BYPASS", raising=False)
        fake_stdin(json.dumps({"response_text": "WAVE_COMPLETE: plan=x-aaaaaa wave=1"}))

        with patch.object(hook_module, "_load_writer", return_value=None), patch.object(
            hook_module.sys.stdin, "isatty", return_value=False
        ):
            rc = hook_module.main()

        assert rc == 0


# ---------------------------------------------------------------------------
# Hook registration in hooks.json
# ---------------------------------------------------------------------------


class TestHooksJsonRegistration:
    def test_hook_registered_in_post_cascade_response(self):
        hooks_path = REPO_ROOT / ".windsurf" / "hooks.json"
        data = json.loads(hooks_path.read_text(encoding="utf-8"))
        commands = [
            entry["command"]
            for entry in data["hooks"]["post_cascade_response"]
        ]
        assert any(
            "post_cascade_wave_lifecycle_capture.py" in c for c in commands
        ), "hook not registered in .windsurf/hooks.json"

    def test_hook_entry_schema_pure(self):
        # Constitutional §27 — hooks.json entries may only contain
        # ``command`` / ``working_directory`` / ``show_output``.
        hooks_path = REPO_ROOT / ".windsurf" / "hooks.json"
        data = json.loads(hooks_path.read_text(encoding="utf-8"))
        allowed = {"command", "working_directory", "show_output"}
        for entry in data["hooks"]["post_cascade_response"]:
            if "post_cascade_wave_lifecycle_capture.py" in entry.get("command", ""):
                assert set(entry.keys()) <= allowed, (
                    f"non-schema keys present: {set(entry.keys()) - allowed}"
                )
                break
        else:
            pytest.fail("hook entry not found")
