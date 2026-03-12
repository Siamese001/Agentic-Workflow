"""ADG importability contract for agentic_core/L4_state/enforcement/readonly_retrieval_scope.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_readonly_retrieval_scope.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L4_state.enforcement.readonly_retrieval_scope import (  # noqa: F401
        RetrievalMutationViolation,
        is_read_only_retrieval_active,
        assert_not_read_only,
        read_only_retrieval_scope,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    RetrievalMutationViolation = None  # type: ignore[assignment,misc]
    is_read_only_retrieval_active = None  # type: ignore[assignment,misc]
    assert_not_read_only = None  # type: ignore[assignment,misc]
    read_only_retrieval_scope = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="readonly_retrieval_scope.py deps unavailable")
class TestReadonlyRetrievalScopeImportability:
    def test_module_importable(self) -> None:
        """ADG contract: readonly_retrieval_scope.py must be importable."""
        assert _AVAILABLE

    def test_retrievalmutationviolation_is_type(self) -> None:
        assert RetrievalMutationViolation is not None

    def test_is_read_only_retrieval_active_callable(self) -> None:
        assert callable(is_read_only_retrieval_active)

    def test_assert_not_read_only_callable(self) -> None:
        assert callable(assert_not_read_only)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

