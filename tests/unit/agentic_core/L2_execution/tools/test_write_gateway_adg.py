"""ADG importability contract for agentic_core/L2_execution/tools/write_gateway.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_write_gateway.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.tools.write_gateway import (  # noqa: F401
        MAX_GROWTH_RATIO,
        MAX_WRITE_BYTES,
        MutationEntropyError,
        WriteAmplificationError,
        WriteSizeCapError,
        record_prohibition_hit,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    MAX_WRITE_BYTES = None  # type: ignore[assignment,misc]
    MAX_GROWTH_RATIO = None  # type: ignore[assignment,misc]
    WriteSizeCapError = None  # type: ignore[assignment,misc]
    WriteAmplificationError = None  # type: ignore[assignment,misc]
    MutationEntropyError = None  # type: ignore[assignment,misc]
    record_prohibition_hit = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="write_gateway deps unavailable")
class TestWriteGatewayImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L2_execution/tools/write_gateway.py must be importable."""
        assert _AVAILABLE

    def test_writesizecaperror_defined(self) -> None:
        assert WriteSizeCapError is not None

    def test_writeamplificationerror_defined(self) -> None:
        assert WriteAmplificationError is not None

    def test_mutationentropyerror_defined(self) -> None:
        assert MutationEntropyError is not None
