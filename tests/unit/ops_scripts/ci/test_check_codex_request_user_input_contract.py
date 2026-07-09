"""Tests for the Codex request_user_input decision UI contract guard."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

_GATE_PATH = REPO_ROOT / "ops_scripts" / "ci" / "check_codex_request_user_input_contract.py"
_spec = importlib.util.spec_from_file_location("check_codex_request_user_input_contract", _GATE_PATH)
assert _spec and _spec.loader
gate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gate)


def test_current_repo_contract_passes() -> None:
    assert gate.check_contract(REPO_ROOT) == []


def test_scan_blocks_retired_question_tool(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    rel = Path("surface.md")
    (tmp_path / rel).write_text("Use " + "Ask" + "User" + "Question" + " here\n", encoding="utf-8")
    monkeypatch.setattr(gate, "CONTRACT_FILES", (str(rel),))

    findings = gate._scan_contract_files(tmp_path)

    assert [finding.code for finding in findings] == ["legacy_question_tool"]


def test_scan_blocks_legacy_product_token(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    rel = Path("surface.md")
    (tmp_path / rel).write_text("legacy " + "c" + "laude" + " wording\n", encoding="utf-8")
    monkeypatch.setattr(gate, "CONTRACT_FILES", (str(rel),))

    findings = gate._scan_contract_files(tmp_path)

    assert [finding.code for finding in findings] == ["legacy_product_token"]


def test_builder_schema_guard_requires_codex_question_id(monkeypatch: pytest.MonkeyPatch) -> None:
    import tools.decisions.enriched_choice_builder as builder

    real = builder.build_enriched_choice_question

    def broken(*args, **kwargs):
        payload = real(*args, **kwargs)
        del payload["tool_input"]["questions"][0]["id"]
        return payload

    monkeypatch.setattr(builder, "build_enriched_choice_question", broken)

    findings = gate._builder_schema_findings(REPO_ROOT)

    assert any(finding.code == "missing_question_id" for finding in findings)


def test_required_fallback_text_is_enforced(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    rel = Path("skill.md")
    (tmp_path / rel).write_text("request tool shape only\n", encoding="utf-8")
    monkeypatch.setattr(gate, "REQUIRED_SUBSTRINGS", {str(rel): ("plain-text clarifying question",)})

    findings = gate._required_text_findings(tmp_path)

    assert [finding.code for finding in findings] == ["missing_required_fallback_text"]
