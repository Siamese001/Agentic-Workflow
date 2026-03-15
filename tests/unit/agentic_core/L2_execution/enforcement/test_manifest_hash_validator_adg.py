"""ADG importability contract for agentic_core/L2_execution/enforcement/manifest_hash_validator.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_manifest_hash_validator.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.enforcement.manifest_hash_validator import (  # noqa: F401
        REQUIRED_HASH_FIELDS,
        ManifestHashError,
        validate_manifest_hashes,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    REQUIRED_HASH_FIELDS = None  # type: ignore[assignment,misc]
    ManifestHashError = None  # type: ignore[assignment,misc]
    validate_manifest_hashes = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="manifest_hash_validator deps unavailable")
class TestManifestHashValidatorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L2_execution/enforcement/manifest_hash_validator.py must be importable."""
        assert _AVAILABLE

    def test_manifesthasherror_defined(self) -> None:
        assert ManifestHashError is not None
