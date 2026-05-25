"""Tests for ops_scripts/ci/check_l6_observer_law.py (plan W4)."""
from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

GATE = importlib.import_module("ops_scripts.ci.check_l6_observer_law")


def test_is_forbidden_writer_in_runtime_layer() -> None:
    assert GATE._is_forbidden("agentic_core.L4_state.uwg_writer") is not None
    assert GATE._is_forbidden("agentic_core.L0_routing.bandit_dispatcher") is not None
    assert GATE._is_forbidden("agentic_core.L3_orchestration.exit_executor") is not None


def test_is_forbidden_allows_types_and_contracts() -> None:
    assert GATE._is_forbidden("agentic_core.L4_state.contracts.app_domain") is None
    assert GATE._is_forbidden("agentic_core.L0_routing.types") is None
    assert GATE._is_forbidden("agentic_core.L3_orchestration.exit_eval.v6.pipeline") is None


def test_is_forbidden_ignores_l6_imports() -> None:
    # L6 importing from L6 (observability) is fine.
    assert GATE._is_forbidden("agentic_core.L6_observability.types") is None


def test_is_forbidden_ignores_non_layer_modules() -> None:
    assert GATE._is_forbidden("os") is None
    assert GATE._is_forbidden("agentic_core.L6_system_learning.engines.foo") is None


def test_scan_file_detects_writer_import(tmp_path: Path) -> None:
    src = tmp_path / "evil.py"
    src.write_text(
        "from agentic_core.L4_state.uwg_writer import write_uwg_state\n", encoding="utf-8"
    )
    # Patch REPO_ROOT to tmp_path so relative path computation works.
    original_root = GATE.REPO_ROOT
    GATE.REPO_ROOT = tmp_path
    try:
        findings = GATE._scan_file(src)
    finally:
        GATE.REPO_ROOT = original_root
    assert len(findings) == 1
    assert findings[0].module == "agentic_core.L4_state.uwg_writer"
    assert "writer-suffix" in findings[0].reason


def test_scan_file_clean_for_type_only_import(tmp_path: Path) -> None:
    src = tmp_path / "clean.py"
    src.write_text(
        "from agentic_core.L4_state.contracts.app_domain import AppDomain\n",
        encoding="utf-8",
    )
    original_root = GATE.REPO_ROOT
    GATE.REPO_ROOT = tmp_path
    try:
        findings = GATE._scan_file(src)
    finally:
        GATE.REPO_ROOT = original_root
    assert findings == []


def test_main_bypass_short_circuits(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("L6_OBSERVER_LAW_BYPASS", "1")
    assert GATE.main() == 0


def test_scan_file_ignores_type_checking_imports(tmp_path: Path) -> None:
    src = tmp_path / "tc.py"
    src.write_text(
        "from typing import TYPE_CHECKING\n"
        "if TYPE_CHECKING:\n"
        "    from agentic_core.L3_orchestration.healers.healing_tier_dispatcher import X\n",
        encoding="utf-8",
    )
    original_root = GATE.REPO_ROOT
    GATE.REPO_ROOT = tmp_path
    try:
        findings = GATE._scan_file(src)
    finally:
        GATE.REPO_ROOT = original_root
    assert findings == []


def test_main_advisory_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("L6_OBSERVER_LAW_BYPASS", raising=False)
    monkeypatch.delenv("L6_OBSERVER_LAW_FAIL_CLOSED", raising=False)
    # Either 0 (clean) or 0 (advisory mode swallows findings) — never raises.
    rc = GATE.main()
    assert rc == 0
