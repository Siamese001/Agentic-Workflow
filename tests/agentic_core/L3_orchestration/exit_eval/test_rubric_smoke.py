"""Smoke tests per gate — one test per rubric verifies the rubric loads.

Wiring-gate (``ops_scripts/ci/check_exit_eval_wiring.py``) requires that
each gate id appear in at least one test file as a string literal. This
file exists so every gate in ``config/exit_eval_rubrics/`` has a test
anchor, even the simple ones (X1A policy match, X1B schema) that don't
have dedicated behavior tests elsewhere.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_core.L3_orchestration.exit_eval.composition import CompositionMode
from agentic_core.L3_orchestration.exit_eval.rubric import load_rubric

REPO_ROOT = Path(__file__).resolve().parents[4]
RUBRIC_DIR = REPO_ROOT / "config" / "exit_eval_rubrics"


@pytest.mark.parametrize(
    "gate,expected_composition",
    [
        ("X1A", CompositionMode.BINARY),
        ("X1B", CompositionMode.HYBRID),
        ("X1C", CompositionMode.BINARY),
        ("X1D", CompositionMode.WEIGHTED),
        ("X1E", CompositionMode.HYBRID),
        ("X1F", CompositionMode.HYBRID),
    ],
)
def test_rubric_loads_and_has_expected_composition(gate: str, expected_composition: CompositionMode) -> None:
    """Each shipped rubric matches its gate's documented composition mode.

    This is load-and-shape only; semantic tests for each gate live in
    the module-specific test files (test_composition, test_adversarial,
    test_pipeline, etc.).
    """
    path = RUBRIC_DIR / f"{gate.lower()}_v1.yaml"
    rubric = load_rubric(path)
    assert rubric.gate == gate
    assert rubric.version.startswith(f"{gate}@")
    assert rubric.composition is expected_composition
    assert rubric.dimensions, f"{gate} rubric has no dimensions"


def test_x1b_has_schema_complete_hard_gate() -> None:
    """X1B 'schema_complete' must be a hard binary sub-gate."""
    rubric = load_rubric(RUBRIC_DIR / "x1b_v1.yaml")
    by_name = {d.name: d for d in rubric.dimensions}
    assert "schema_complete" in by_name
    assert by_name["schema_complete"].is_hard_gate
    assert by_name["schema_complete"].threshold == 1.0


def test_x1e_trajectory_has_hard_tool_selection() -> None:
    """X1E 'tool_selection_accuracy' must be a hard code-based sub-gate."""
    rubric = load_rubric(RUBRIC_DIR / "x1e_v1.yaml")
    by_name = {d.name: d for d in rubric.dimensions}
    assert "tool_selection_accuracy" in by_name
    assert by_name["tool_selection_accuracy"].is_hard_gate


def test_x1f_adversarial_has_three_hard_subgates() -> None:
    """X1F: injection + leak + jailbreak are all hard-gates."""
    rubric = load_rubric(RUBRIC_DIR / "x1f_v1.yaml")
    hard_names = {d.name for d in rubric.dimensions if d.is_hard_gate}
    assert {
        "prompt_injection_resistance",
        "system_prompt_leakage",
        "jailbreak_detection",
    }.issubset(hard_names)
