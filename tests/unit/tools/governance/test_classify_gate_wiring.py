"""Tests for tools/governance/classify_gate_wiring.py.

The classifier is the W1.2 read-only audit that decides whether a CI gate is
REGISTRY / PRECOMMIT / WORKFLOW / TEST_ONLY / ORPHANED. Only ORPHANED gates
may be retired in consolidation W4 — misclassification would delete live gates.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.governance import classify_gate_wiring as mod
from tools.governance.classify_gate_wiring import _basenames, classify, main


def test_basenames_extracts_check_gate_filenames() -> None:
    text = "invoke check_foo_bar.py then check_baz.py"
    assert _basenames(text) == {"check_foo_bar.py", "check_baz.py"}


def test_basenames_ignores_non_check_prefixed_py_files() -> None:
    assert _basenames("run_contract_gates.py scan_modules.py") == set()


@pytest.mark.parametrize(
    ("refs", "expected"),
    [
        ({"registry": True, "precommit": True, "workflow": True, "tests": True}, "REGISTRY"),
        ({"registry": False, "precommit": True, "workflow": True, "tests": True}, "PRECOMMIT"),
        ({"registry": False, "precommit": False, "workflow": True, "tests": True}, "WORKFLOW"),
        ({"registry": False, "precommit": False, "workflow": False, "tests": True}, "TEST_ONLY"),
        ({"registry": False, "precommit": False, "workflow": False, "tests": False}, "ORPHANED"),
    ],
)
def test_classification_priority(
    refs: dict[str, bool], expected: str, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Registry wiring beats pre-commit, which beats workflow, then tests, else orphaned."""
    ci = tmp_path / "ci"
    ci.mkdir()
    gate = "check_priority_gate.py"
    (ci / gate).write_text("# gate\n", encoding="utf-8")

    monkeypatch.setattr(mod, "CI_DIR", ci)
    monkeypatch.setattr(mod, "_registry_refs", lambda: {gate} if refs["registry"] else set())
    monkeypatch.setattr(mod, "_workflow_refs", lambda: {gate} if refs["workflow"] else set())
    monkeypatch.setattr(mod, "_test_refs", lambda: {gate} if refs["tests"] else set())
    monkeypatch.setattr(
        mod,
        "_read",
        lambda path: gate if refs["precommit"] and path.name == ".pre-commit-config.yaml" else "",
    )

    row = classify()["gates"][gate]
    assert row["classification"] == expected


def test_classify_assigns_orphaned_when_unreferenced(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    ci = tmp_path / "ci"
    ci.mkdir()
    (ci / "check_orphan_gate.py").write_text("# orphan\n", encoding="utf-8")

    monkeypatch.setattr(mod, "CI_DIR", ci)
    monkeypatch.setattr(mod, "_registry_refs", lambda: set())
    monkeypatch.setattr(mod, "_workflow_refs", lambda: set())
    monkeypatch.setattr(mod, "_test_refs", lambda: set())
    monkeypatch.setattr(mod, "_read", lambda path: "")

    payload = classify()
    assert payload["total_gates"] == 1
    assert payload["counts"]["ORPHANED"] == 1
    assert payload["gates"]["check_orphan_gate.py"]["classification"] == "ORPHANED"


def test_classify_registry_wins_over_test_reference(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    ci = tmp_path / "ci"
    ci.mkdir()
    gate = "check_live_gate.py"
    (ci / gate).write_text("# live\n", encoding="utf-8")

    monkeypatch.setattr(mod, "CI_DIR", ci)
    monkeypatch.setattr(mod, "_registry_refs", lambda: {gate})
    monkeypatch.setattr(mod, "_workflow_refs", lambda: set())
    monkeypatch.setattr(mod, "_test_refs", lambda: {gate})
    monkeypatch.setattr(mod, "_read", lambda path: "")

    row = classify()["gates"][gate]
    assert row["classification"] == "REGISTRY"
    assert row["registry"] is True
    assert row["tests"] is True


def test_main_writes_json_report(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    ci = tmp_path / "ci"
    ci.mkdir()
    (ci / "check_only_in_tests.py").write_text("# t\n", encoding="utf-8")

    monkeypatch.setattr(mod, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(mod, "CI_DIR", ci)
    monkeypatch.setattr(mod, "_registry_refs", lambda: set())
    monkeypatch.setattr(mod, "_workflow_refs", lambda: set())
    monkeypatch.setattr(mod, "_test_refs", lambda: {"check_only_in_tests.py"})
    monkeypatch.setattr(mod, "_read", lambda path: "")

    out_rel = "reports/gate_wiring.json"
    assert main(["--out", out_rel]) == 0
    written = json.loads((tmp_path / out_rel).read_text(encoding="utf-8"))
    assert written["gates"]["check_only_in_tests.py"]["classification"] == "TEST_ONLY"
    assert "[classify_gate_wiring]" in capsys.readouterr().out
