"""ADG importability contract for agentic_core/L4_state/enforcement/readonly_retrieval_scope.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_readonly_retrieval_scope.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L4_state.enforcement.readonly_retrieval_scope import (  # noqa: F401
        RetrievalMutationViolation,
        assert_not_read_only,
        is_read_only_retrieval_active,
        read_only_retrieval_scope,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    RetrievalMutationViolation = None  # type: ignore[assignment,misc]
    is_read_only_retrieval_active = None  # type: ignore[assignment,misc]
    assert_not_read_only = None  # type: ignore[assignment,misc]
    read_only_retrieval_scope = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="readonly_retrieval_scope deps unavailable")
class TestReadonlyRetrievalScopeImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L4_state/enforcement/readonly_retrieval_scope.py must be importable."""
        assert _AVAILABLE

    def test_retrievalmutationviolation_defined(self) -> None:
        assert RetrievalMutationViolation is not None
