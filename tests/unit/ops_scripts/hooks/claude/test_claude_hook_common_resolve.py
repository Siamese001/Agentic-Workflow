"""Unit tests for the shared Stop-payload response resolver (claude_hook_common).

The live Claude ``Stop`` payload carries NO inline response — only ``transcript_path``.
``recover_response_from_transcript`` + ``resolve_response_text`` are the SSOT the three
Stop hooks share so they actually see the final assistant turn. claude_hook_common has no
intra-package relative imports, so we load it directly from its file path.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[5]
CHC_PATH = REPO_ROOT / ".claude" / "hooks" / "lib" / "claude_hook_common.py"


@pytest.fixture()
def chc():
    spec = importlib.util.spec_from_file_location("_claude_hook_common_test", CHC_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _write_transcript(tmp_path: Path, *assistant_texts: str, include_tool_use: bool = True) -> Path:
    lines = [json.dumps({"type": "user", "message": {"role": "user", "content": "go"}})]
    for text in assistant_texts:
        content = [{"type": "text", "text": text}]
        if include_tool_use:
            content.append({"type": "tool_use", "name": "Read", "input": {}})
        lines.append(json.dumps({"type": "assistant", "message": {"role": "assistant", "content": content}}))
    path = tmp_path / "transcript.jsonl"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


class TestRecoverFromTranscript:
    def test_returns_last_assistant_message(self, chc, tmp_path) -> None:
        tr = _write_transcript(tmp_path, "early", "middle", "the final turn")
        assert chc.recover_response_from_transcript(str(tr)) == "the final turn"

    def test_skips_malformed_lines(self, chc, tmp_path) -> None:
        path = tmp_path / "t.jsonl"
        path.write_text(
            "not json\n"
            + json.dumps({"type": "assistant", "message": {"role": "assistant", "content": [{"type": "text", "text": "good"}]}})
            + "\n{ broken json\n",
            encoding="utf-8",
        )
        assert chc.recover_response_from_transcript(str(path)) == "good"

    def test_missing_file_returns_empty(self, chc, tmp_path) -> None:
        assert chc.recover_response_from_transcript(str(tmp_path / "absent.jsonl")) == ""

    def test_empty_path_returns_empty(self, chc) -> None:
        assert chc.recover_response_from_transcript("") == ""

    def test_string_content_form(self, chc, tmp_path) -> None:
        path = tmp_path / "t.jsonl"
        path.write_text(
            json.dumps({"type": "assistant", "message": {"role": "assistant", "content": "plain body"}}) + "\n",
            encoding="utf-8",
        )
        assert chc.recover_response_from_transcript(str(path)) == "plain body"

    def test_tool_use_only_message_yields_empty(self, chc, tmp_path) -> None:
        # An assistant turn with only a tool_use block (no text) has no recoverable text.
        path = tmp_path / "t.jsonl"
        path.write_text(
            json.dumps({"type": "assistant", "message": {"role": "assistant", "content": [{"type": "tool_use", "name": "Read"}]}}) + "\n",
            encoding="utf-8",
        )
        assert chc.recover_response_from_transcript(str(path)) == ""


class TestResolveResponseText:
    def test_inline_response_wins(self, chc, tmp_path) -> None:
        tr = _write_transcript(tmp_path, "from transcript")
        assert chc.resolve_response_text({"response": "inline", "transcript_path": str(tr)}) == "inline"

    def test_tool_info_response_via_text_keys(self, chc) -> None:
        # Synthetic/legacy payloads carry tool_info.response — text_from_payload picks it up.
        assert chc.resolve_response_text({"tool_info": {"response": "legacy body"}}) == "legacy body"

    def test_transcript_fallback(self, chc, tmp_path) -> None:
        tr = _write_transcript(tmp_path, "recovered final")
        assert chc.resolve_response_text({"session_id": "s", "transcript_path": str(tr)}) == "recovered final"

    def test_empty_payload_returns_empty(self, chc) -> None:
        assert chc.resolve_response_text({}) == ""

    def test_missing_transcript_returns_empty(self, chc, tmp_path) -> None:
        assert chc.resolve_response_text({"transcript_path": str(tmp_path / "nope.jsonl")}) == ""
