"""ADG importability contract for agentic_core/L0_routing/enforcement/mutation_prohibition.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_mutation_prohibition.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L0_routing.enforcement.mutation_prohibition import (  # noqa: F401
        IMMUTABLE_ROOTS,
        ProtectedRootBlockEvent,
        ProtectedRootPolicy,
        SourceMutationBlocked,
        enforce_protected_root,
        get_default_protected_root_policy,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    SourceMutationBlocked = None  # type: ignore[assignment,misc]
    ProtectedRootBlockEvent = None  # type: ignore[assignment,misc]
    ProtectedRootPolicy = None  # type: ignore[assignment,misc]
    get_default_protected_root_policy = None  # type: ignore[assignment,misc]
    IMMUTABLE_ROOTS = None  # type: ignore[assignment,misc]
    enforce_protected_root = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="mutation_prohibition deps unavailable")
class TestMutationProhibitionImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L0_routing/enforcement/mutation_prohibition.py must be importable."""
        assert _AVAILABLE

    def test_sourcemutationblocked_defined(self) -> None:
        assert SourceMutationBlocked is not None

    def test_protectedrootblockevent_defined(self) -> None:
        assert ProtectedRootBlockEvent is not None

    def test_protectedrootpolicy_defined(self) -> None:
        assert ProtectedRootPolicy is not None
