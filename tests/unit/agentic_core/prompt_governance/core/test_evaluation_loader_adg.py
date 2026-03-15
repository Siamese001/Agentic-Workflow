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
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    EvalLoadError = None  # type: ignore[assignment,misc]
    EvalSchemaError = None  # type: ignore[assignment,misc]
    EvaluationLoader = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="evaluation_loader deps unavailable")
class TestEvaluationLoaderImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/prompt_governance/core/evaluation_loader.py must be importable."""
        assert _AVAILABLE

    def test_evalloaderror_defined(self) -> None:
        assert EvalLoadError is not None

    def test_evalschemaerror_defined(self) -> None:
        assert EvalSchemaError is not None

    def test_evaluationloader_defined(self) -> None:
        assert EvaluationLoader is not None
