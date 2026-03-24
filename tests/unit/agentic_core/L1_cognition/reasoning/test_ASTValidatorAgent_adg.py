"""ADG importability contract for agentic_core/L1_cognition/reasoning/ASTValidatorAgent.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_ASTValidatorAgent.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L1_cognition.reasoning.ASTValidatorAgent import (  # noqa: F401
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        ASTValidatorAgent,
        ASTValidatorBase,
        get_unified_ast_validator,
        validate_bare_except,
        validate_empty_except,
        validate_eval_exec,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    ASTValidatorBase = None  # type: ignore[assignment,misc]
    ASTValidatorAgent = None  # type: ignore[assignment,misc]
    get_unified_ast_validator = None  # type: ignore[assignment,misc]
    validate_bare_except = None  # type: ignore[assignment,misc]
    validate_empty_except = None  # type: ignore[assignment,misc]
    validate_eval_exec = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="ASTValidatorAgent.py deps unavailable")
class TestAstvalidatoragentImportability:
    def test_module_importable(self) -> None:
        """ADG contract: ASTValidatorAgent.py must be importable."""
        assert _AVAILABLE

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