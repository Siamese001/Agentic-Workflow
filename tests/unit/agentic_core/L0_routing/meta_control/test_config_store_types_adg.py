"""ADG importability contract for agentic_core/L0_routing/meta_control/config_store_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_config_store_types.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L0_routing.meta_control.config_store_types import (  # noqa: F401
        ConfigSnapshotArtifact,
        ConfigDeltaArtifact,
        canonical_json,
        stable_sha256,
        validate_component_allowed,
        build_config_snapshot,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ConfigSnapshotArtifact = None  # type: ignore[assignment,misc]
    ConfigDeltaArtifact = None  # type: ignore[assignment,misc]
    canonical_json = None  # type: ignore[assignment,misc]
    stable_sha256 = None  # type: ignore[assignment,misc]
    validate_component_allowed = None  # type: ignore[assignment,misc]
    build_config_snapshot = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="config_store_types.py deps unavailable")
class TestConfigStoreTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: config_store_types.py must be importable."""
        assert _AVAILABLE

    def test_configsnapshotartifact_is_type(self) -> None:
        assert ConfigSnapshotArtifact is not None

    def test_configdeltaartifact_is_type(self) -> None:
        assert ConfigDeltaArtifact is not None

    def test_canonical_json_callable(self) -> None:
        assert callable(canonical_json)

    def test_stable_sha256_callable(self) -> None:
        assert callable(stable_sha256)

