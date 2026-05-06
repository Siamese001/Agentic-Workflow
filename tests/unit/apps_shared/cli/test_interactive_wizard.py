"""Unit tests for apps_shared.cli.interactive_wizard."""
from __future__ import annotations

import io
from unittest.mock import patch

import pytest

from apps_shared.cli.interactive_wizard import (
    WizardField,
    read_multiline_or_file,
    run_wizard,
)


class _FakeStdin(io.StringIO):
    def isatty(self) -> bool:  # noqa: D401
        return True


def test_run_wizard_requires_tty(monkeypatch):
    fake = io.StringIO("anything\n")
    fake.isatty = lambda: False  # type: ignore[method-assign]
    monkeypatch.setattr("sys.stdin", fake)
    with pytest.raises(RuntimeError, match="TTY"):
        run_wizard([WizardField("x", "X", kind="string")])


def test_run_wizard_string_field(monkeypatch):
    monkeypatch.setattr("sys.stdin", _FakeStdin())
    with patch("builtins.input", side_effect=["Brown & Brown"]):
        result = run_wizard([WizardField("company", "Company", kind="string")])
    assert result == {"company": "Brown & Brown"}


def test_run_wizard_string_required_reprompts(monkeypatch):
    monkeypatch.setattr("sys.stdin", _FakeStdin())
    with patch("builtins.input", side_effect=["", "  ", "Acme"]):
        result = run_wizard([WizardField("co", "Co", kind="string")])
    assert result == {"co": "Acme"}


def test_run_wizard_string_optional_allows_empty(monkeypatch):
    monkeypatch.setattr("sys.stdin", _FakeStdin())
    with patch("builtins.input", side_effect=[""]):
        result = run_wizard(
            [WizardField("note", "Note", kind="string", required=False)]
        )
    assert result == {"note": ""}


def test_read_multiline_or_file_paste_terminated_by_END(monkeypatch):
    monkeypatch.setattr("sys.stdin", _FakeStdin())
    with patch("builtins.input", side_effect=["line one", "line two", "END"]):
        text, source = read_multiline_or_file("desc")
    assert text == "line one\nline two"
    assert source is None


def test_read_multiline_or_file_at_path(tmp_path, monkeypatch):
    f = tmp_path / "jd.txt"
    f.write_text("file contents", encoding="utf-8")
    monkeypatch.setattr("sys.stdin", _FakeStdin())
    with patch("builtins.input", side_effect=[f"@{f}"]):
        text, source = read_multiline_or_file("desc")
    assert text == "file contents"
    assert source == str(f)


def test_read_multiline_or_file_empty_first_line(monkeypatch):
    monkeypatch.setattr("sys.stdin", _FakeStdin())
    with patch("builtins.input", side_effect=[""]):
        text, source = read_multiline_or_file("desc")
    assert text == ""
    assert source is None


def test_read_multiline_or_file_missing_path(monkeypatch):
    monkeypatch.setattr("sys.stdin", _FakeStdin())
    with patch("builtins.input", side_effect=["@/nonexistent/path/abc.txt"]):
        text, source = read_multiline_or_file("desc")
    assert text == ""
    assert source is None


def test_run_wizard_multiline_or_file_kind(monkeypatch):
    monkeypatch.setattr("sys.stdin", _FakeStdin())
    with patch("builtins.input", side_effect=["paragraph one", "paragraph two", "END"]):
        result = run_wizard(
            [WizardField("desc", "Description", kind="multiline_or_file")]
        )
    assert result["desc"] == {"text": "paragraph one\nparagraph two", "source": None}


def test_run_wizard_multiline_or_file_or_auto_auto(monkeypatch):
    monkeypatch.setattr("sys.stdin", _FakeStdin())
    with patch("builtins.input", side_effect=["auto"]):
        result = run_wizard(
            [WizardField("brief", "Brief", kind="multiline_or_file_or_auto")]
        )
    assert result["brief"] == {"mode": "auto", "text": "", "source": None}


def test_run_wizard_multiline_or_file_or_auto_paste(monkeypatch):
    monkeypatch.setattr("sys.stdin", _FakeStdin())
    with patch("builtins.input", side_effect=['{"company": "X"}', "END"]):
        result = run_wizard(
            [WizardField("brief", "Brief", kind="multiline_or_file_or_auto")]
        )
    assert result["brief"]["mode"] == "paste"
    assert '{"company": "X"}' in result["brief"]["text"]


def test_run_wizard_multiline_or_file_or_auto_file(tmp_path, monkeypatch):
    f = tmp_path / "brief.json"
    f.write_text("{}", encoding="utf-8")
    monkeypatch.setattr("sys.stdin", _FakeStdin())
    with patch("builtins.input", side_effect=[f"@{f}"]):
        result = run_wizard(
            [WizardField("brief", "Brief", kind="multiline_or_file_or_auto")]
        )
    assert result["brief"] == {"mode": "file", "text": "", "source": str(f)}


def test_run_wizard_multiline_or_file_or_auto_missing_falls_back_to_auto(monkeypatch):
    monkeypatch.setattr("sys.stdin", _FakeStdin())
    with patch("builtins.input", side_effect=["@/nonexistent/x.json"]):
        result = run_wizard(
            [WizardField("brief", "Brief", kind="multiline_or_file_or_auto")]
        )
    assert result["brief"]["mode"] == "auto"


def test_run_wizard_three_fields_apps_rg_shape(monkeypatch):
    monkeypatch.setattr("sys.stdin", _FakeStdin())
    inputs = [
        "Brown & Brown",
        "SVP IT Strategy",
        "Job desc line 1",
        "Job desc line 2",
        "END",
        "auto",
    ]
    with patch("builtins.input", side_effect=inputs):
        result = run_wizard(
            [
                WizardField("company", "Company", kind="string"),
                WizardField("role", "Role", kind="string"),
                WizardField("desc", "Desc", kind="multiline_or_file"),
                WizardField("brief", "Brief", kind="multiline_or_file_or_auto"),
            ]
        )
    assert result["company"] == "Brown & Brown"
    assert result["role"] == "SVP IT Strategy"
    assert result["desc"]["text"] == "Job desc line 1\nJob desc line 2"
    assert result["brief"]["mode"] == "auto"
