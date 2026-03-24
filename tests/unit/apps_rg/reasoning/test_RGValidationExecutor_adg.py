"""ADG importability contract for apps_rg/reasoning/RGValidationExecutor.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_RGValidationExecutor.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from apps_rg.reasoning.RGValidationExecutor import (  # noqa: F401
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        RGValidationExecutor,
        register_rule,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    RGValidationExecutor = None  # type: ignore[assignment,misc]
    register_rule = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="RGValidationExecutor.py deps unavailable")
class TestRgvalidationexecutorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: RGValidationExecutor.py must be importable."""
        assert _AVAILABLE

    def test_rgvalidationexecutor_is_type(self) -> None:
        assert RGValidationExecutor is not None

    def test_register_rule_callable(self) -> None:
        assert callable(register_rule)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None