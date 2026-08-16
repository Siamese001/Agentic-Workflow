"""Tests for the read-only default of the always-on instruction budget gate."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
GATE_PATH = REPO_ROOT / "ops_scripts" / "ci" / "check_always_on_token_budget.py"
sys.path.insert(0, str(GATE_PATH.parent))


def _load():
    spec = importlib.util.spec_from_file_location("always_on_budget_test", GATE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_default_check_does_not_write_inventory(monkeypatch, capsys) -> None:
    gate = _load()
    writes: list[str] = []
    monkeypatch.setattr(gate, "tier1_cursor_total", lambda: (0, []))
    monkeypatch.setattr(gate, "scan_windsurf_always_on_md", lambda: [])
    monkeypatch.setattr(gate, "claude_always_on_total", lambda: (0, []))
    monkeypatch.setattr(gate, "write_inventory", lambda **kwargs: writes.append(str(kwargs)) or Path("inventory.json"))

    assert gate.main([]) == 0
    assert writes == []
    assert "inventory not written" in capsys.readouterr().out


def test_write_inventory_requires_explicit_flag(monkeypatch) -> None:
    gate = _load()
    writes: list[dict[str, str]] = []
    monkeypatch.setattr(gate, "tier1_cursor_total", lambda: (0, []))
    monkeypatch.setattr(gate, "scan_windsurf_always_on_md", lambda: [])
    monkeypatch.setattr(gate, "claude_always_on_total", lambda: (0, []))
    monkeypatch.setattr(gate, "write_inventory", lambda **kwargs: writes.append(kwargs) or Path("inventory.json"))

    assert gate.main(["--write-inventory", "--inventory-wave", "W0-test"]) == 0
    assert writes == [{"wave": "W0-test"}]


def test_repo_real_always_on_surface_fits_enforced_ceiling() -> None:
    gate = _load()
    real_total, _ = gate.claude_always_on_total()

    assert real_total <= gate.REAL_SURFACE_THRESHOLD
