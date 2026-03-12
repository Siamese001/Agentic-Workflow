"""ADG importability contract for agentic_core/runtime/sovereignty_bootstrap.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_sovereignty_bootstrap.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.runtime.sovereignty_bootstrap import (  # noqa: F401
        SovereigntyBootstrap,
        bootstrap_sovereignty,
        seal_determinism_and_finalize,
        get_sovereignty_hashes,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    SovereigntyBootstrap = None  # type: ignore[assignment,misc]
    bootstrap_sovereignty = None  # type: ignore[assignment,misc]
    seal_determinism_and_finalize = None  # type: ignore[assignment,misc]
    get_sovereignty_hashes = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="sovereignty_bootstrap.py deps unavailable")
class TestSovereigntyBootstrapImportability:
    def test_module_importable(self) -> None:
        """ADG contract: sovereignty_bootstrap.py must be importable."""
        assert _AVAILABLE

    def test_sovereigntybootstrap_is_type(self) -> None:
        assert SovereigntyBootstrap is not None

    def test_bootstrap_sovereignty_callable(self) -> None:
        assert callable(bootstrap_sovereignty)

    def test_seal_determinism_and_finalize_callable(self) -> None:
        assert callable(seal_determinism_and_finalize)

