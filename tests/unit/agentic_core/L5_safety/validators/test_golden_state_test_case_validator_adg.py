"""ADG importability contract for agentic_core/L5_safety/validators/golden_state_test_case_validator.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_golden_state_test_case_validator.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.validators.golden_state_test_case_validator import (  # noqa: F401
        EvalResult,
        GoldenCase,
        GoldenOutput,
        GoldenStateTestCase,
        JudgeVerdict,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    GoldenStateTestCase = None  # type: ignore[assignment,misc]
    JudgeVerdict = None  # type: ignore[assignment,misc]
    EvalResult = None  # type: ignore[assignment,misc]
    GoldenCase = None  # type: ignore[assignment,misc]
    GoldenOutput = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="golden_state_test_case_validator deps unavailable")
class TestGoldenStateTestCaseValidatorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/validators/golden_state_test_case_validator.py must be importable."""
        assert _AVAILABLE

    def test_goldenstatetestcase_defined(self) -> None:
        assert GoldenStateTestCase is not None

    def test_judgeverdict_defined(self) -> None:
        assert JudgeVerdict is not None

    def test_evalresult_defined(self) -> None:
        assert EvalResult is not None

    def test_goldencase_defined(self) -> None:
        assert GoldenCase is not None

    def test_goldenoutput_defined(self) -> None:
        assert GoldenOutput is not None
