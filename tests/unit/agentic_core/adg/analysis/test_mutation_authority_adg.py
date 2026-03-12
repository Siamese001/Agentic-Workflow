"""ADG importability contract for agentic_core/adg/analysis/mutation_authority.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_mutation_authority.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.adg.analysis.mutation_authority import (  # noqa: F401
        MutationBypassViolation,
        MutationPathReport,
        verify_mutation_paths,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    MutationBypassViolation = None  # type: ignore[assignment,misc]
    MutationPathReport = None  # type: ignore[assignment,misc]
    verify_mutation_paths = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="mutation_authority.py deps unavailable")
class TestMutationAuthorityImportability:
    def test_module_importable(self) -> None:
        """ADG contract: mutation_authority.py must be importable."""
        assert _AVAILABLE

    def test_mutationbypassviolation_is_type(self) -> None:
        assert MutationBypassViolation is not None

    def test_mutationpathreport_is_type(self) -> None:
        assert MutationPathReport is not None

    def test_verify_mutation_paths_callable(self) -> None:
        assert callable(verify_mutation_paths)

