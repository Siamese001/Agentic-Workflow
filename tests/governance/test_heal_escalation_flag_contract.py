"""
Governance contract: Heal escalation flag + observer safety enforcement.

Ensures:
1. Flag default-off is preserved (no escalation log without env var)
2. Observer seam cannot be set persistently (default is None, no module-level reassignment)

Phase 5 Wave 5.3 acceptance test.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

import agentic_core.utils.decorators_util as decorators_module
from agentic_core.L5_safety.types.heal_policy_types import (
    HealEscalationDecision,
    ReasoningTier,
)
from agentic_core.utils.decorators_compat_util import standard_heal

pytestmark = pytest.mark.governance


DECORATORS_MODULE_PATH = Path("agentic_core/utils/decorators_util.py")


class DummyHealer:
    """Minimal healer class for testing standard_heal decorator."""

    name: str = "DummyHealer"

    @standard_heal
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        _call_path: set[str] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Minimal heal_repository that returns a simple dict."""
        return {
            "violations_found": 2,
            "violations_fixed": 1,
            "status": "PASS",
        }


class TestFlagDefaultOff:
    """Enforce flag default-off behavior is preserved."""

    def test_no_escalation_log_without_env_var(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Without env var, no 'escalation_enabled=1' log appears."""
        monkeypatch.delenv("HEAL_POLICY_MODEL_ESCALATION", raising=False)

        mock_decision = HealEscalationDecision(
            tier=ReasoningTier.LOW,
            threshold_used="TEST",
            rationale="Test rationale",
        )

        captured_messages: list[str] = []

        def capture_debug(msg: str, *args: Any, **kwargs: Any) -> None:
            captured_messages.append(msg)

        with (
            patch(
                "agentic_core.utils.decorators_util.decide_reasoning_tier",
                return_value=mock_decision,
            ),
            patch(
                "agentic_core.utils.decorators_util.Logger.debug",
                side_effect=capture_debug,
            ),
        ):
            healer = DummyHealer()
            healer.heal_repository(dry_run=True)

        escalation_logs = [m for m in captured_messages if "escalation_enabled=1" in m]
        assert len(escalation_logs) == 0, (
            f"Expected no escalation log without env var, got: {escalation_logs}"
        )

    def test_observer_not_invoked_without_env_var(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Without env var, observer is not invoked."""
        monkeypatch.delenv("HEAL_POLICY_MODEL_ESCALATION", raising=False)

        mock_decision = HealEscalationDecision(
            tier=ReasoningTier.LOW,
            threshold_used="TEST",
            rationale="Test rationale",
        )

        observer_calls: list[ReasoningTier] = []

        def spy_observer(tier: ReasoningTier) -> None:
            observer_calls.append(tier)

        with (
            patch(
                "agentic_core.utils.decorators_util.decide_reasoning_tier",
                return_value=mock_decision,
            ),
            patch.object(decorators_module, "_HEAL_TIER_OBSERVER", spy_observer),
        ):
            healer = DummyHealer()
            healer.heal_repository(dry_run=True)

        assert len(observer_calls) == 0, (
            f"Expected observer not called without env var, got: {observer_calls}"
        )


class TestObserverSeamSafety:
    """Enforce observer seam cannot be set persistently."""

    def test_observer_default_is_none_at_import(self) -> None:
        """Observer seam must be None at import time."""
        import importlib

        import agentic_core.utils.decorators_util

        importlib.reload(agentic_core.utils.decorators_util)

        assert agentic_core.utils.decorators_util._HEAL_TIER_OBSERVER is None, (
            "Observer seam must default to None"
        )

    def test_observer_not_reassigned_at_module_scope(self) -> None:
        """Observer seam must not be reassigned anywhere at module scope (AST check)."""
        module_path = Path.cwd() / DECORATORS_MODULE_PATH
        assert module_path.exists(), f"Decorators module not found: {module_path}"

        source = module_path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(module_path))

        observer_assignments: list[tuple[int, str]] = []

        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "_HEAL_TIER_OBSERVER":
                        value_repr = ast.unparse(node.value) if hasattr(ast, "unparse") else "..."
                        observer_assignments.append((node.lineno, value_repr))

            elif isinstance(node, ast.AnnAssign):
                if isinstance(node.target, ast.Name) and node.target.id == "_HEAL_TIER_OBSERVER":
                    value_repr = ast.unparse(node.value) if node.value and hasattr(ast, "unparse") else "None"
                    observer_assignments.append((node.lineno, value_repr))

        assert len(observer_assignments) == 1, (
            f"Expected exactly one module-level assignment for _HEAL_TIER_OBSERVER, got {len(observer_assignments)}: {observer_assignments}"
        )

        line, value = observer_assignments[0]
        assert value == "None", (
            f"Observer seam must be assigned None at module scope (line {line}), got: {value}"
        )
