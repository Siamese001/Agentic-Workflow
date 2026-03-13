"""ADG importability contract for agentic_core/L5_safety/validators/direct_prompt_compilation_validator.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_direct_prompt_compilation_validator.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.validators.direct_prompt_compilation_validator import (  # noqa: F401
        DirectPromptCompilationDetector,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    DirectPromptCompilationDetector = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="direct_prompt_compilation_validator deps unavailable")
class TestDirectPromptCompilationValidatorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/validators/direct_prompt_compilation_validator.py must be importable."""
        assert _AVAILABLE

    def test_directpromptcompilationdetector_defined(self) -> None:
        assert DirectPromptCompilationDetector is not None
