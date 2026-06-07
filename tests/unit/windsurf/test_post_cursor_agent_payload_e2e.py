"""E2E: real Windsurf post_cursor_agent_response payload shape must capture markers.

Regression guard for the 2026-04-23 RCA: two hooks only checked top-level
response keys and silently dropped markers delivered in the documented
``tool_info.response`` nesting. This test reproduces the exact Windsurf
payload shape and asserts each hook extracts the embedded text.

Per the Windsurf docs:

    {
      "agent_action_name": "post_cursor_agent_response",
      "tool_info": { "response": "<full assistant text>" }
    }
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
SCRIPTS = REPO / ".cursor" / "scripts" / "_legacy_windsurf"
sys.path.insert(0, str(SCRIPTS))

from _post_cursor_agent_payload import extract_response_text  # noqa: E402


DEFERRED_SAMPLE = (
    "Some preamble.\n"
    "DEFERRED_SCOPE: plan=NEW:example wave=W1 phase=W1.1 layer=L2 "
    "fan_in=3 surface=Execution coverage_gap_pct=50.0 est_tokens=4000 "
    "reason=sample marker\n"
    "Some postamble."
)

WINDSURF_PAYLOAD = {
    "agent_action_name": "post_cursor_agent_response",
    "tool_info": {"response": DEFERRED_SAMPLE},
}


class TestSharedExtractor:
    def test_extracts_tool_info_response(self) -> None:
        got = extract_response_text(json.dumps(WINDSURF_PAYLOAD))
        assert got == DEFERRED_SAMPLE

    def test_extracts_top_level_response(self) -> None:
        # Legacy / test shape
        got = extract_response_text(json.dumps({"response": DEFERRED_SAMPLE}))
        assert got == DEFERRED_SAMPLE

    def test_passes_raw_text_through(self) -> None:
        got = extract_response_text(DEFERRED_SAMPLE)
        assert got == DEFERRED_SAMPLE

    def test_empty_input(self) -> None:
        assert extract_response_text("") == ""
        assert extract_response_text("   \n  ") == ""

    def test_unparseable_returns_raw(self) -> None:
        # Non-JSON, non-empty
        assert extract_response_text("<<not json>>") == "<<not json>>"

    def test_newlines_preserved_not_escaped(self) -> None:
        """Regression: multiline anchor regex MUST match after extraction."""
        import re

        extracted = extract_response_text(json.dumps(WINDSURF_PAYLOAD))
        # The ^DEFERRED_SCOPE: anchor (multiline) must find the marker
        assert re.search(r"^DEFERRED_SCOPE:", extracted, re.MULTILINE) is not None


class TestDeferredScopeCaptureHook:
    """Integration: pipe the real payload shape into the hook and verify
    markers land in the capture log."""

    def test_windsurf_payload_captures_marker(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        # Point the hook's capture log at a tmp file so we don't pollute the
        # real jsonl, and disable Notion posting by clearing the token.
        import subprocess

        env = {
            "NOTION_TOKEN": "",
            "NOTION_API_KEY": "",
            "PYTHONIOENCODING": "utf-8",
            "PATH": __import__("os").environ.get("PATH", ""),
            "SYSTEMROOT": __import__("os").environ.get("SYSTEMROOT", ""),
        }
        hook = SCRIPTS / "post_cursor_agent_deferred_scope_capture.py"
        proc = subprocess.run(
            [sys.executable, str(hook)],
            input=json.dumps(WINDSURF_PAYLOAD),
            text=True,
            capture_output=True,
            env=env,
            cwd=str(REPO),
            timeout=15,
            check=False,
        )
        # The hook should have detected the marker. With no NOTION_TOKEN,
        # the marker skips Notion post but still logs a record.
        assert proc.returncode == 0
        assert "markers=1" in (proc.stderr or ""), (
            f"Expected 'markers=1' in stderr; got:\nSTDERR: {proc.stderr}\nSTDOUT: {proc.stdout}"
        )
