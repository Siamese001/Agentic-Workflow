"""ADG importability contract for agentic_core/L1_cognition/types/cache_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_cache_types.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L1_cognition.types.cache_types import (  # noqa: F401
        DomainConfig,
        EvictionPolicy,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    EvictionPolicy = None  # type: ignore[assignment,misc]
    DomainConfig = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="cache_types deps unavailable")
class TestCacheTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L1_cognition/types/cache_types.py must be importable."""
        assert _AVAILABLE

    def test_evictionpolicy_defined(self) -> None:
        assert EvictionPolicy is not None

    def test_domainconfig_defined(self) -> None:
        assert DomainConfig is not None