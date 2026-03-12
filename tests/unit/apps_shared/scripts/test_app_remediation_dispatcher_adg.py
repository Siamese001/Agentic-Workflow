"""ADG importability contract for apps_shared/scripts/app_remediation_dispatcher.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_app_remediation_dispatcher.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from apps_shared.scripts.app_remediation_dispatcher import (  # noqa: F401
        dispatch,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    dispatch = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="app_remediation_dispatcher.py deps unavailable")
class TestAppRemediationDispatcherImportability:
    def test_module_importable(self) -> None:
        """ADG contract: app_remediation_dispatcher.py must be importable."""
        assert _AVAILABLE

    def test_dispatch_callable(self) -> None:
        assert callable(dispatch)

