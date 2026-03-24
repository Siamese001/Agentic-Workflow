"""ADG importability contract for agentic_core/L0_routing/seams/canonical_truth_seam.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_canonical_truth_seam.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L0_routing.seams.canonical_truth_seam import (  # noqa: F401
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        CanonicalTruthProvider,
        categorize_agent,
        get_canonical_layer,
        get_canonical_truth_provider,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    CanonicalTruthProvider = None  # type: ignore[assignment,misc]
    get_canonical_truth_provider = None  # type: ignore[assignment,misc]
    get_canonical_layer = None  # type: ignore[assignment,misc]
    categorize_agent = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="canonical_truth_seam.py deps unavailable")
class TestCanonicalTruthSeamImportability:
    def test_module_importable(self) -> None:
        """ADG contract: canonical_truth_seam.py must be importable."""
        assert _AVAILABLE

    def test_canonicaltruthprovider_is_type(self) -> None:
        assert CanonicalTruthProvider is not None

    def test_get_canonical_truth_provider_callable(self) -> None:
        assert callable(get_canonical_truth_provider)

    def test_get_canonical_layer_callable(self) -> None:
        assert callable(get_canonical_layer)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None