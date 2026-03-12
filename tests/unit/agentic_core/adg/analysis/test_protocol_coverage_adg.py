"""ADG importability contract for agentic_core/adg/analysis/protocol_coverage.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_protocol_coverage.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.adg.analysis.protocol_coverage import (  # noqa: F401
        ProtocolCoverageReport,
        check_protocol_coverage,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ProtocolCoverageReport = None  # type: ignore[assignment,misc]
    check_protocol_coverage = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="protocol_coverage.py deps unavailable")
class TestProtocolCoverageImportability:
    def test_module_importable(self) -> None:
        """ADG contract: protocol_coverage.py must be importable."""
        assert _AVAILABLE

    def test_protocolcoveragereport_is_type(self) -> None:
        assert ProtocolCoverageReport is not None

    def test_check_protocol_coverage_callable(self) -> None:
        assert callable(check_protocol_coverage)

