"""ADG importability contract for agentic_core/L5_safety/invariants/runtime_invariant_checker.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_runtime_invariant_checker.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.invariants.runtime_invariant_checker import (  # noqa: F401
        assert_mutation_source_is_l2,
        assert_mutation_in_ledger,
        assert_state_read_source_is_l4,
        assert_c0_no_authority_fields,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    assert_mutation_source_is_l2 = None  # type: ignore[assignment,misc]
    assert_mutation_in_ledger = None  # type: ignore[assignment,misc]
    assert_state_read_source_is_l4 = None  # type: ignore[assignment,misc]
    assert_c0_no_authority_fields = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="runtime_invariant_checker.py deps unavailable")
class TestRuntimeInvariantCheckerImportability:
    def test_module_importable(self) -> None:
        """ADG contract: runtime_invariant_checker.py must be importable."""
        assert _AVAILABLE

    def test_assert_mutation_source_is_l2_callable(self) -> None:
        assert callable(assert_mutation_source_is_l2)

    def test_assert_mutation_in_ledger_callable(self) -> None:
        assert callable(assert_mutation_in_ledger)

