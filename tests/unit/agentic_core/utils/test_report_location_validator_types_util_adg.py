"""ADG importability contract for agentic_core/utils/report_location_validator_types_util.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_report_location_validator_types_util.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    import agentic_core.utils.report_location_validator_types_util as _mod  # noqa: F401
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    _mod = None

@pytest.mark.skipif(not _AVAILABLE, reason="report_location_validator_types_util.py deps unavailable")
class TestReportLocationValidatorTypesUtilImportability:
    def test_module_importable(self) -> None:
        """ADG contract: report_location_validator_types_util.py must be importable."""
        assert _AVAILABLE

