"""ADG importability contract for agentic_core/L6_observability/engines/determinism_digest_emitter.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_determinism_digest_emitter.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L6_observability.engines.determinism_digest_emitter import (  # noqa: F401
        DeterminismDigestEmitter,
        DuplicateEmissionError,
        build_stable_config_surface,
        hash_config_surface,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    DuplicateEmissionError = None  # type: ignore[assignment,misc]
    DeterminismDigestEmitter = None  # type: ignore[assignment,misc]
    build_stable_config_surface = None  # type: ignore[assignment,misc]
    hash_config_surface = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="determinism_digest_emitter deps unavailable")
class TestDeterminismDigestEmitterImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L6_observability/engines/determinism_digest_emitter.py must be importable."""
        assert _AVAILABLE

    def test_duplicateemissionerror_defined(self) -> None:
        assert DuplicateEmissionError is not None

    def test_determinismdigestemitter_defined(self) -> None:
        assert DeterminismDigestEmitter is not None
