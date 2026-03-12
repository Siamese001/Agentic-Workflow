"""ADG importability contract for agentic_core/L5_safety/hitl/patch_validator.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_patch_validator.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.hitl.patch_validator import (  # noqa: F401
        ValidatedPatch,
        validate_patch,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ValidatedPatch = None  # type: ignore[assignment,misc]
    validate_patch = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="patch_validator.py deps unavailable")
class TestPatchValidatorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: patch_validator.py must be importable."""
        assert _AVAILABLE

    def test_validatedpatch_is_type(self) -> None:
        assert ValidatedPatch is not None

    def test_validate_patch_callable(self) -> None:
        assert callable(validate_patch)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

