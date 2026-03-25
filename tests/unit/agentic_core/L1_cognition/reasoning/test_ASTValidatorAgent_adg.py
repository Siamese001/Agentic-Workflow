"""ADG importability contract for agentic_core/L1_cognition/reasoning/ASTValidatorAgent.py.

Auto-generated stub - covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_ASTValidatorAgent.py (no _adg suffix).
"""
from __future__ import annotations

from agentic_core.L1_cognition.reasoning.ASTValidatorAgent import (
    DEFAULT_SLEEP,
    MAX_RETRIES,
    ASTValidatorAgent,
    ASTValidatorBase,
    get_unified_ast_validator,
    validate_bare_except,
)  # noqa: F401


class TestAstvalidatoragentImportability:
    def test_module_importable(self) -> None:
        """ADG contract: ASTValidatorAgent.py must be importable."""

        pass  # Import verified at module level

    def test_astvalidatorbase_is_type(self) -> None:
        assert ASTValidatorBase is not None

    def test_astvalidatoragent_is_type(self) -> None:
        assert ASTValidatorAgent is not None

    def test_get_unified_ast_validator_callable(self) -> None:
        assert callable(get_unified_ast_validator)

    def test_validate_bare_except_callable(self) -> None:
        assert callable(validate_bare_except)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None
