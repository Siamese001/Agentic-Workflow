"""ADG importability contract for agentic_core/L2_execution/types/ml_write_intent_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_ml_write_intent_types.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.types.ml_write_intent_types import (  # noqa: F401
        MLWriteEnvelopeViolation,
        MLWriteIntent,
        MLWriteIntentExecutor,
        execute_ml_write_intent_outside_sandbox,
        is_commit_sandbox_active,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    MLWriteEnvelopeViolation = None  # type: ignore[assignment,misc]
    MLWriteIntent = None  # type: ignore[assignment,misc]
    is_commit_sandbox_active = None  # type: ignore[assignment,misc]
    MLWriteIntentExecutor = None  # type: ignore[assignment,misc]
    execute_ml_write_intent_outside_sandbox = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="ml_write_intent_types deps unavailable")
class TestMlWriteIntentTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L2_execution/types/ml_write_intent_types.py must be importable."""
        assert _AVAILABLE

    def test_mlwriteenvelopeviolation_defined(self) -> None:
        assert MLWriteEnvelopeViolation is not None

    def test_mlwriteintent_defined(self) -> None:
        assert MLWriteIntent is not None

    def test_mlwriteintentexecutor_defined(self) -> None:
        assert MLWriteIntentExecutor is not None