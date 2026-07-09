"""ADG-hotspot scaffold tests for `agentic_core.L5_safety.utils.location_healer_util` (fanin=8).

Auto-generated speculative scaffold. Module is high fan-in per ADG snapshot
04252026_0843. Verify class/function names against actual module before
treating these as authoritative tests.
"""
from __future__ import annotations

import importlib
import logging
from pathlib import Path

import pytest

from agentic_core.L5_safety.utils.location_healer_util import LocationHealerAgent

MODULE_PATH = "agentic_core.L5_safety.utils.location_healer_util"


def _new_agent(tmp_path: Path) -> LocationHealerAgent:
    agent = LocationHealerAgent.__new__(LocationHealerAgent)
    agent.project_root = tmp_path
    return agent


def test_module_imports():
    """Smoke: hotspot module must import cleanly (high fan-in regression guard)."""
    mod = importlib.import_module(MODULE_PATH)
    assert mod is not None


def test_module_has_public_surface():
    """Smoke: hotspot module must expose at least one public attribute."""
    mod = importlib.import_module(MODULE_PATH)
    public = [n for n in dir(mod) if not n.startswith("_")]
    assert public, f"{MODULE_PATH} has no public attributes"


def test_module_no_top_level_side_effects():
    """Re-import must be idempotent — no top-level side effects that fail."""
    importlib.import_module(MODULE_PATH)
    importlib.import_module(MODULE_PATH)


@pytest.mark.parametrize("attr_kind", ["class", "function"])
def test_module_exposes_callable(attr_kind):
    """Hotspot modules with high fan-in should expose a callable surface."""
    mod = importlib.import_module(MODULE_PATH)
    has_callable = any(
        callable(getattr(mod, n))
        for n in dir(mod)
        if not n.startswith("_")
    )
    assert has_callable, f"{MODULE_PATH} exposes no callable {attr_kind}"


def test_module_layer_path_matches():
    """Module file path must contain expected layer prefix."""
    mod = importlib.import_module(MODULE_PATH)
    file = getattr(mod, "__file__", "")
    assert "agentic_core" in file.replace("\\", "/"), (
        f"{MODULE_PATH} not under agentic_core: {file}"
    )


def test_safe_move_dry_run_reports_preview_path(tmp_path: Path) -> None:
    agent = _new_agent(tmp_path)
    src = tmp_path / "source.py"
    dst = tmp_path / "nested" / "target.py"
    src.write_text("print('hi')\n", encoding="utf-8")
    logging.info("C3 write receipt: tests/agentic_core/L5_safety/utils/test_location_healer_util.py write side effect recorded")

    result = LocationHealerAgent.safe_move(agent, src, dst, dry_run=True)

    assert result["applied"] is True
    assert result["error"] is None
    assert result["action_taken"] == f"PREVIEW: Would move to {dst.relative_to(tmp_path)}"
    assert src.exists()


@pytest.mark.parametrize(
    ("src_text", "dst_text", "expected_applied", "expected_error", "expected_prefix"),
    [
        ("same\n", "same\n", True, None, "SKIPPED_IDENTICAL: destination already exists"),
        (
            "left\n",
            "right\n",
            False,
            "destination_exists_different_content",
            "CONFLICT: destination exists with different content",
        ),
    ],
)
def test_safe_move_handles_existing_destination_content(
    tmp_path: Path,
    src_text: str,
    dst_text: str,
    expected_applied: bool,
    expected_error: str | None,
    expected_prefix: str,
) -> None:
    agent = _new_agent(tmp_path)
    src = tmp_path / "source.py"
    dst = tmp_path / "nested" / "target.py"
    dst.parent.mkdir(parents=True, exist_ok=True)
    src.write_text(src_text, encoding="utf-8")
    dst.write_text(dst_text, encoding="utf-8")

    result = LocationHealerAgent.safe_move(agent, src, dst, dry_run=False)

    assert result["applied"] is expected_applied
    assert result["error"] == expected_error
    assert result["action_taken"].startswith(expected_prefix)
    assert src.exists()
