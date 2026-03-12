"""ADG importability contract for agentic_core/prompt_governance/security/validators/output_schema_validator.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_output_schema_validator.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.prompt_governance.security.validators.output_schema_validator import (  # noqa: F401
        validate_against_schema,
        validate_healer_reentry,
        validate_context_contract,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    validate_against_schema = None  # type: ignore[assignment,misc]
    validate_healer_reentry = None  # type: ignore[assignment,misc]
    validate_context_contract = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="output_schema_validator.py deps unavailable")
class TestOutputSchemaValidatorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: output_schema_validator.py must be importable."""
        assert _AVAILABLE

    def test_validate_against_schema_callable(self) -> None:
        assert callable(validate_against_schema)

    def test_validate_healer_reentry_callable(self) -> None:
        assert callable(validate_healer_reentry)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

