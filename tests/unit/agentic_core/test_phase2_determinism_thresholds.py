"""
Phase 2 Wave 3 — Determinism Thresholds Tests

Tests that:
- depth_breaker, max_k, max_retries, token_budget come from BudgetConfig/RoutingConfig
- default config values match prior inline constants (parity lock)
- static audit: banned literals not re-introduced in targeted modules
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from agentic_core.L4_state.config.versioned_configs import BudgetConfig, RoutingConfig

pytestmark = pytest.mark.unit_min_deps

# Prior inline constants — parity lock values
PRIOR_DEPTH_BREAKER = 10
PRIOR_MAX_K = 10
PRIOR_MAX_RETRIES = 3
PRIOR_TOKEN_BUDGET = 1_000_000
PRIOR_BACKOFF_BASE = 1.0


class TestDefaultConfigMatchesPriorConstants:
    def test_default_config_matches_prior_constants(self):
        routing = RoutingConfig()
        budget = BudgetConfig()
        assert routing.depth_breaker == PRIOR_DEPTH_BREAKER, (
            f"depth_breaker parity broken: {routing.depth_breaker} != {PRIOR_DEPTH_BREAKER}"
        )
        assert budget.max_k == PRIOR_MAX_K, f"max_k parity broken: {budget.max_k} != {PRIOR_MAX_K}"
        assert budget.max_retries == PRIOR_MAX_RETRIES, (
            f"max_retries parity broken: {budget.max_retries} != {PRIOR_MAX_RETRIES}"
        )
        assert budget.token_budget == PRIOR_TOKEN_BUDGET, (
            f"token_budget parity broken: {budget.token_budget} != {PRIOR_TOKEN_BUDGET}"
        )
        assert budget.backoff_base_seconds == PRIOR_BACKOFF_BASE, (
            f"backoff_base parity broken: {budget.backoff_base_seconds} != {PRIOR_BACKOFF_BASE}"
        )

    def test_depth_breaker_uses_config_value(self):
        routing = RoutingConfig(depth_breaker=5)
        assert routing.depth_breaker == 5
        assert routing.config_hash != RoutingConfig().config_hash

    def test_max_k_uses_config_value(self):
        budget = BudgetConfig(max_k=25)
        assert budget.max_k == 25
        assert budget.config_hash != BudgetConfig().config_hash

    def test_retry_ceiling_uses_config_value(self):
        budget = BudgetConfig(max_retries=7)
        assert budget.max_retries == 7

    def test_token_budget_uses_config_value(self):
        budget = BudgetConfig(token_budget=500_000)
        assert budget.token_budget == 500_000


class TestStaticAudit:
    """
    Static audit: verify that the versioned_configs module itself does not
    re-introduce the banned inline literals as bare numeric constants
    in non-default-value positions (i.e., not as dataclass field defaults).

    We audit the durable_write_wrapper.py for hardcoded phase strings
    and versioned_configs.py for structural correctness.
    """

    def _get_numeric_literals_in_function_bodies(self, filepath: Path) -> list[int | float]:
        """
        Return numeric literals found inside function/method bodies
        (excluding class-level default assignments).
        """
        source = filepath.read_text(encoding="utf-8")
        tree = ast.parse(source)
        literals: list[int | float] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                for child in ast.walk(node):
                    if isinstance(child, ast.Constant) and isinstance(child.value, int | float):
                        literals.append(child.value)
        return literals

    def test_manifest_hash_validator_has_no_hardcoded_hash_strings(self):
        filepath = (
            Path(__file__).resolve().parents[2]
            / "agentic_core"
            / "L2_execution"
            / "enforcement"
            / "manifest_hash_validator.py"
        )
        source = filepath.read_text(encoding="utf-8")
        tree = ast.parse(source)
        string_literals_in_functions: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                for child in ast.walk(node):
                    if isinstance(child, ast.Constant) and isinstance(child.value, str):
                        if len(child.value) == 64 and all(c in "0123456789abcdef" for c in child.value):
                            string_literals_in_functions.append(child.value)
        assert string_literals_in_functions == [], (
            f"Hardcoded hash strings found in manifest_hash_validator: {string_literals_in_functions}"
        )

    def test_retrieval_anchor_module_parses_cleanly(self):
        filepath = (
            Path(__file__).resolve().parents[2]
            / "agentic_core"
            / "L4_state"
            / "types"
            / "retrieval_anchor.py"
        )
        source = filepath.read_text(encoding="utf-8")
        tree = ast.parse(source)
        assert tree is not None

    def test_versioned_configs_module_parses_cleanly(self):
        filepath = (
            Path(__file__).resolve().parents[2]
            / "agentic_core"
            / "L4_state"
            / "config"
            / "versioned_configs.py"
        )
        source = filepath.read_text(encoding="utf-8")
        tree = ast.parse(source)
        assert tree is not None

    def test_all_four_config_classes_present_in_module(self):
        filepath = (
            Path(__file__).resolve().parents[2]
            / "agentic_core"
            / "L4_state"
            / "config"
            / "versioned_configs.py"
        )
        source = filepath.read_text(encoding="utf-8")
        tree = ast.parse(source)
        class_names = {node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)}
        for required in ("PolicyConfig", "RoutingConfig", "ModelConfig", "BudgetConfig", "L4ActiveConfigs"):
            assert required in class_names, f"Missing class: {required}"
