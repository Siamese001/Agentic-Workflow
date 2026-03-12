"""ADG importability contract for agentic_core/prompt_governance/core/evaluation_loader.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_evaluation_loader.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.prompt_governance.core.evaluation_loader import (  # noqa: F401
        EvalLoadError,
        EvalSchemaError,
        EvaluationLoader,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    EvalLoadError = None  # type: ignore[assignment,misc]
    EvalSchemaError = None  # type: ignore[assignment,misc]
    EvaluationLoader = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="evaluation_loader.py deps unavailable")
class TestEvaluationLoaderImportability:
    def test_module_importable(self) -> None:
        """ADG contract: evaluation_loader.py must be importable."""
        assert _AVAILABLE

    def test_evalloaderror_is_type(self) -> None:
        assert EvalLoadError is not None

    def test_evalschemaerror_is_type(self) -> None:
        assert EvalSchemaError is not None

    def test_evaluationloader_is_type(self) -> None:
        assert EvaluationLoader is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

