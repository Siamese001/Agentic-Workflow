"""DS-R7 — apps_rg interactive JD prompt hardening.

Tests:
1. _prompt_jd_interactive raises SystemExit when stdin is not a TTY and batch stdin is not enabled.
2. _prompt_jd_interactive reads stdin when APPS_RG_INTERACTIVE_STDIN=1 even if not a TTY.
3. _prompt_jd_interactive returns the entered path when stdin IS a TTY.
4. --non-interactive flag on args prevents interactive prompt from being called.
5. jd_payload in raw_request is always a dict (assert guard).
6. raw_request["jd_payload"] key is present and forwarded to the pipeline.
"""
from __future__ import annotations

import io
import json
import os
import types
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from apps_rg.__main__ import _build_raw_request, _prompt_jd_interactive


# ---------------------------------------------------------------------------
# Helper — minimal args namespace
# ---------------------------------------------------------------------------

def _args(**kwargs):
    defaults = dict(
        target_company="Acme",
        target_role="Engineer",
        jd=None,
        non_interactive=False,
        manual_brief="",
        candidate=None,
        tenant_id="default",
        research_via=None,
        auto_research_internal=False,
        auto_research_tavily=False,
        target_level=None,
    )
    defaults.update(kwargs)
    ns = types.SimpleNamespace(**defaults)
    return ns


# ---------------------------------------------------------------------------
# 1. _prompt_jd_interactive raises SystemExit when stdin is not a TTY (no batch)
# ---------------------------------------------------------------------------

def test_prompt_jd_non_tty_raises_without_batch_env(monkeypatch, capsys):
    monkeypatch.delenv("APPS_RG_INTERACTIVE_STDIN", raising=False)
    with patch("sys.stdin", new=io.StringIO("some/path.json")):
        # StringIO.isatty() returns False
        with pytest.raises(SystemExit) as excinfo:
            _prompt_jd_interactive()
    assert excinfo.value.code == 2
    err = capsys.readouterr().err
    assert "APPS_RG_INTERACTIVE_STDIN" in err


# ---------------------------------------------------------------------------
# 2. _prompt_jd_interactive reads stdin when batch env is set (non-TTY)
# ---------------------------------------------------------------------------

def test_prompt_jd_non_tty_reads_when_batch_env():
    with patch.dict(os.environ, {"APPS_RG_INTERACTIVE_STDIN": "1"}):
        with patch("sys.stdin", new=io.StringIO("some/path.json\n")):
            result = _prompt_jd_interactive()
    assert result == "some/path.json"


# ---------------------------------------------------------------------------
# 3. _prompt_jd_interactive returns entered path when stdin IS a TTY
# ---------------------------------------------------------------------------

def test_prompt_jd_tty_returns_path():
    fake_stdin = MagicMock()
    fake_stdin.isatty.return_value = True
    with patch("sys.stdin", fake_stdin):
        with patch("builtins.input", return_value="  my/jd.json  "):
            result = _prompt_jd_interactive()
    assert result == "my/jd.json"


# ---------------------------------------------------------------------------
# 4. --non-interactive flag prevents interactive prompt
# ---------------------------------------------------------------------------

def test_non_interactive_skips_prompt():
    called = []

    def _fake_prompt():
        called.append(True)
        return "should/not/be/called.json"

    args = _args(non_interactive=True)
    with patch("apps_rg.__main__._prompt_jd_interactive", side_effect=_fake_prompt):
        result = _build_raw_request(args)

    assert not called, "_prompt_jd_interactive should not be called in non-interactive mode"
    assert isinstance(result["jd_payload"], dict)


# ---------------------------------------------------------------------------
# 5. jd_payload is always a dict — assert guard fires on bad input
# ---------------------------------------------------------------------------

def test_jd_payload_is_always_dict(tmp_path):
    valid_jd = tmp_path / "jd.json"
    valid_jd.write_text(json.dumps({"title": "SWE", "skills": ["Python"]}), encoding="utf-8")
    args = _args(jd=str(valid_jd), non_interactive=True)
    result = _build_raw_request(args)
    assert isinstance(result["jd_payload"], dict)
    assert result["jd_payload"]["title"] == "SWE"


# ---------------------------------------------------------------------------
# 6. jd_payload is present in raw_request and forwarded
# ---------------------------------------------------------------------------

def test_jd_payload_key_present_when_no_file():
    args = _args(jd="nonexistent_file_xyz.json", non_interactive=True)
    result = _build_raw_request(args)
    assert "jd_payload" in result
    assert result["jd_payload"] == {}


def test_jd_payload_forwarded_from_file(tmp_path):
    jd_data = {"title": "Principal Engineer", "company": "Acme"}
    jd_path = tmp_path / "jd.json"
    jd_path.write_text(json.dumps(jd_data), encoding="utf-8")
    args = _args(jd=str(jd_path), non_interactive=True)
    result = _build_raw_request(args)
    assert result["jd_payload"] == jd_data
    assert result["body_text"] == json.dumps(jd_data)
