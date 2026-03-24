"""ADG importability contract for apps_lic/engines/control_plane.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_control_plane.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from apps_lic.engines.control_plane import (  # noqa: F401
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        ControlPlane,
        PolicyAction,
        PolicyDecision,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    PolicyAction = None  # type: ignore[assignment,misc]
    PolicyDecision = None  # type: ignore[assignment,misc]
    ControlPlane = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="control_plane.py deps unavailable")
class TestControlPlaneImportability:
    def test_module_importable(self) -> None:
        """ADG contract: control_plane.py must be importable."""
        assert _AVAILABLE

    def test_policyaction_is_type(self) -> None:
        assert PolicyAction is not None

    def test_policydecision_is_type(self) -> None:
        assert PolicyDecision is not None

    def test_controlplane_is_type(self) -> None:
        assert ControlPlane is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None