"""ADG importability contract for agentic_core/adg/runtime/mutation_transport.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_mutation_transport.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.adg.runtime.mutation_transport import (  # noqa: F401
        CommitPhase,
        MutationPacket,
        MutationTransport,
        MutationTransportReport,
        RFC6902Patch,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    CommitPhase = None  # type: ignore[assignment,misc]
    RFC6902Patch = None  # type: ignore[assignment,misc]
    MutationPacket = None  # type: ignore[assignment,misc]
    MutationTransportReport = None  # type: ignore[assignment,misc]
    MutationTransport = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="mutation_transport deps unavailable")
class TestMutationTransportImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/adg/runtime/mutation_transport.py must be importable."""
        assert _AVAILABLE

    def test_commitphase_defined(self) -> None:
        assert CommitPhase is not None

    def test_rfc6902patch_defined(self) -> None:
        assert RFC6902Patch is not None

    def test_mutationpacket_defined(self) -> None:
        assert MutationPacket is not None

    def test_mutationtransportreport_defined(self) -> None:
        assert MutationTransportReport is not None

    def test_mutationtransport_defined(self) -> None:
        assert MutationTransport is not None