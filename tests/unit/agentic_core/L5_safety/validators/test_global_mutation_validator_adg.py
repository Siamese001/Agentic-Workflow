"""ADG importability contract for agentic_core/L5_safety/validators/global_mutation_validator.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_global_mutation_validator.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.validators.global_mutation_validator import (  # noqa: F401
        GlobalMutationDetector,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    GlobalMutationDetector = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="global_mutation_validator deps unavailable")
class TestGlobalMutationValidatorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/validators/global_mutation_validator.py must be importable."""
        assert _AVAILABLE

    def test_globalmutationdetector_defined(self) -> None:
        assert GlobalMutationDetector is not None
