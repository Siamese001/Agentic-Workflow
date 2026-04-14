"""Smoke tests for package export surfaces and bundle metadata."""

from __future__ import annotations

from pathlib import Path

import agentic_core
import L1_cognition


def test_l1_cognition_namespace_has_expected_exports():
    assert set(L1_cognition.__all__) == {"config", "core", "enforcement", "reasoning", "types", "utils"}


def test_agentic_core_exposes_key_runtime_surfaces():
    expected = {
        "ActionRequest",
        "ASTValidatorAgentAdg",
        "BudgetEnforcerAdg",
        "BudgetWindow",
        "CacheScope",
        "ConsensusValidatorAdg",
        "ExecutionPhase",
        "ReactPolicyBoundary",
        "ThoughtEngineAgent",
    }
    assert expected.issubset(set(agentic_core.__all__))


def test_bundle_metadata_files_exist():
    root = Path(__file__).resolve().parents[1]
    assert (root / "README.md").exists()
    assert (root / "pyproject.toml").exists()
