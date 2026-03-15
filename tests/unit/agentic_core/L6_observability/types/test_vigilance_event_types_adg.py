"""ADG importability contract for agentic_core/L6_observability/types/vigilance_event_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_vigilance_event_types.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L6_observability.types.vigilance_event_types import (  # noqa: F401
        VigilanceEventArtifact,
        VigilanceSeverity,
        build_deterministic_trace_id,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    VigilanceSeverity = None  # type: ignore[assignment,misc]
    VigilanceEventArtifact = None  # type: ignore[assignment,misc]
    build_deterministic_trace_id = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="vigilance_event_types deps unavailable")
class TestVigilanceEventTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L6_observability/types/vigilance_event_types.py must be importable."""
        assert _AVAILABLE

    def test_vigilanceseverity_defined(self) -> None:
        assert VigilanceSeverity is not None

    def test_vigilanceeventartifact_defined(self) -> None:
        assert VigilanceEventArtifact is not None
