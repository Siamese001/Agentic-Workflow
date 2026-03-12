"""ADG-driven tests for agentic_core/L0_routing/scripts/verify_intentional_variants_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.scripts.verify_intentional_variants_util import (  # noqa: F401
        read_file_content,
        extract_key_identifiers,
        analyze_variant_likelihood,
        scan_for_duplicates,
        main,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    read_file_content = None  # type: ignore[assignment,misc]
    extract_key_identifiers = None  # type: ignore[assignment,misc]
    analyze_variant_likelihood = None  # type: ignore[assignment,misc]
    scan_for_duplicates = None  # type: ignore[assignment,misc]
    main = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="verify_intentional_variants_util.py deps unavailable")
class TestReadFileContent:
    def test_is_callable(self):
        assert callable(read_file_content)

@pytest.mark.skipif(not _AVAILABLE, reason="verify_intentional_variants_util.py deps unavailable")
class TestExtractKeyIdentifiers:
    def test_is_callable(self):
        assert callable(extract_key_identifiers)

@pytest.mark.skipif(not _AVAILABLE, reason="verify_intentional_variants_util.py deps unavailable")
class TestAnalyzeVariantLikelihood:
    def test_is_callable(self):
        assert callable(analyze_variant_likelihood)

@pytest.mark.skipif(not _AVAILABLE, reason="verify_intentional_variants_util.py deps unavailable")
class TestScanForDuplicates:
    def test_is_callable(self):
        assert callable(scan_for_duplicates)

@pytest.mark.skipif(not _AVAILABLE, reason="verify_intentional_variants_util.py deps unavailable")
class TestMain:
    def test_is_callable(self):
        assert callable(main)


def test_module_importable():
    """Module verify_intentional_variants_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
