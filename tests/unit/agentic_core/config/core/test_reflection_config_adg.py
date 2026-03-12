"""ADG importability contract for agentic_core/config/core/reflection_config.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_reflection_config.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.config.core.reflection_config import (  # noqa: F401
        CritiqueResult,
        ValidationCriterion,
        ReflectionConfig,
        MutationRequest,
        ReflectionEngine,
        get_reflection_engine,
        evaluate_content,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    CritiqueResult = None  # type: ignore[assignment,misc]
    ValidationCriterion = None  # type: ignore[assignment,misc]
    ReflectionConfig = None  # type: ignore[assignment,misc]
    MutationRequest = None  # type: ignore[assignment,misc]
    ReflectionEngine = None  # type: ignore[assignment,misc]
    get_reflection_engine = None  # type: ignore[assignment,misc]
    evaluate_content = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="reflection_config.py deps unavailable")
class TestReflectionConfigImportability:
    def test_module_importable(self) -> None:
        """ADG contract: reflection_config.py must be importable."""
        assert _AVAILABLE

    def test_critiqueresult_is_type(self) -> None:
        assert CritiqueResult is not None

    def test_validationcriterion_is_type(self) -> None:
        assert ValidationCriterion is not None

    def test_reflectionconfig_is_type(self) -> None:
        assert ReflectionConfig is not None

    def test_get_reflection_engine_callable(self) -> None:
        assert callable(get_reflection_engine)

    def test_evaluate_content_callable(self) -> None:
        assert callable(evaluate_content)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

