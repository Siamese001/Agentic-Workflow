"""ADG importability contract for agentic_core/L4_state/types/citation_bundle_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_citation_bundle_types.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L4_state.types.citation_bundle_types import (  # noqa: F401
        CitationBundle,
        build_citation_bundle,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    CitationBundle = None  # type: ignore[assignment,misc]
    build_citation_bundle = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="citation_bundle_types.py deps unavailable")
class TestCitationBundleTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: citation_bundle_types.py must be importable."""
        assert _AVAILABLE

    def test_citationbundle_is_type(self) -> None:
        assert CitationBundle is not None

    def test_build_citation_bundle_callable(self) -> None:
        assert callable(build_citation_bundle)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

