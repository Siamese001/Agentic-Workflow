"""DS-R7 — apps_rg interactive JD prompt hardening.

Tests:
1. _prompt_jd_interactive raises SystemExit when stdin is not a TTY and batch stdin is not enabled.
2. _prompt_jd_interactive reads stdin when APPS_RG_INTERACTIVE_STDIN=1 even if not a TTY.
3. _prompt_jd_interactive returns the entered path when stdin IS a TTY.
4. --non-interactive flag on args prevents interactive prompt from being called.
5. jd_payload in raw_request is always a dict (assert guard); on-disk ``.json`` uses canonical JD shaping.
6. Raw JSON file path through _build_raw_request matches build_raw_request_for_r4 (certified digest).
7. Missing ``.json`` path stub returns empty jd_payload/body_text (explicit non-certified boundary).
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
from apps_rg.runtime.jd_resolution import build_canonical_jd_payload, canonical_jd_digest
from apps_rg.runtime.orchestration.canonical_dispatch import build_raw_request_for_r4


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


@pytest.fixture(autouse=True)
def _stub_generated_brief(monkeypatch, tmp_path):
    generated = tmp_path / "briefing.md"
    generated.write_text("Generated company brief for Acme.\n", encoding="utf-8")
    monkeypatch.setattr(
        "apps_rg.runtime.orchestration.canonical_dispatch._materialize_fallback_brief",
        lambda **_: str(generated),
    )
    return generated


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
    raw_obj = {"title": "SWE", "skills": ["Python"]}
    valid_jd.write_text(json.dumps(raw_obj), encoding="utf-8")
    args = _args(jd=str(valid_jd), non_interactive=True)
    result = _build_raw_request(args)
    assert isinstance(result["jd_payload"], dict)
    assert result["jd_payload"]["title"] == "SWE"
    expected = build_canonical_jd_payload(
        valid_jd.read_text(encoding="utf-8"),
        target_company="Acme",
        target_role="Engineer",
    )
    assert result["jd_payload"] == expected
    assert result["jd_hash"] == canonical_jd_digest(expected)


def test_build_raw_request_json_file_matches_canonical_dispatch(tmp_path):
    """Certified path: __main__._build_raw_request agrees with build_raw_request_for_r4."""
    jd_path = tmp_path / "role.json"
    jd_path.write_text(
        json.dumps(
            {"title": "Tech Lead", "description": "Run the platform team.", "company": "Globex"}
        ),
        encoding="utf-8",
    )
    args = _args(jd=str(jd_path), non_interactive=True)
    built = _build_raw_request(args)
    canonical = build_raw_request_for_r4(
        target_company="Acme",
        target_role="Engineer",
        target_level="",
        jd=str(jd_path),
        manual_brief="",
        resume_path="",
        generation_mode="strategic_tailor",
    )
    assert built["jd_payload"] == canonical["jd_payload"]
    assert built["jd_hash"] == canonical["jd_hash"]
    assert built["body_text"] == canonical["body_text"]


def test_missing_manual_brief_materializes_research_brief(tmp_path):
    jd_path = tmp_path / "role.json"
    jd_path.write_text(
        json.dumps(
            {"title": "Tech Lead", "description": "Run the platform team.", "company": "Globex"}
        ),
        encoding="utf-8",
    )
    args = _args(jd=str(jd_path), manual_brief="", non_interactive=True)
    result = _build_raw_request(args)
    assert result["manual_brief"].endswith("briefing.md")
    assert Path(result["manual_brief"]).read_text(encoding="utf-8").startswith(
        "Generated company brief for Acme."
    )


# ---------------------------------------------------------------------------
# 6–7. On-disk JSON parity vs missing-.json stub (DS-R7)
# ---------------------------------------------------------------------------

def test_jd_payload_forwarded_from_file(tmp_path):
    jd_data = {"title": "Principal Engineer", "company": "Acme"}
    jd_path = tmp_path / "jd.json"
    jd_path.write_text(json.dumps(jd_data), encoding="utf-8")
    args = _args(jd=str(jd_path), non_interactive=True)
    result = _build_raw_request(args)
    canonical = build_raw_request_for_r4(
        target_company="Acme",
        target_role="Engineer",
        target_level="",
        jd=str(jd_path),
        manual_brief="",
        resume_path="",
        generation_mode="strategic_tailor",
    )
    assert result["jd_payload"] == canonical["jd_payload"]
    assert result["body_text"] == canonical["body_text"]
    assert result["jd_hash"] == canonical["jd_hash"]


def test_missing_json_path_stub_returns_empty_payload_not_canonical_digest():
    """DS-R7: nonexistent ``.json`` path → minimal dict only (no digest parity with R4)."""
    args = _args(jd="nonexistent_file_xyz.json", non_interactive=True)
    result = _build_raw_request(args)
    assert "jd_payload" in result
    assert result["jd_payload"] == {}
    assert result["body_text"] == ""
