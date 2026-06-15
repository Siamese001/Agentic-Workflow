"""Guardian workflow smoke coverage for the L1 cognition package boundary."""

from __future__ import annotations

import importlib
from pathlib import Path


def test_l1_cognition_package_imports_without_side_effect_errors() -> None:
    module = importlib.import_module("agentic_core.L1_cognition")

    assert module.__name__ == "agentic_core.L1_cognition"


def test_l1_cognition_package_marker_exists() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    assert (repo_root / "agentic_core" / "L1_cognition" / "__init__.py").is_file()
