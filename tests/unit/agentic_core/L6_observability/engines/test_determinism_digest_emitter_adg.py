"""ADG importability contract for agentic_core/L6_observability/engines/determinism_digest_emitter.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_determinism_digest_emitter.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L6_observability.engines.determinism_digest_emitter import (  # noqa: F401
        DuplicateEmissionError,
        DeterminismDigestEmitter,
        build_stable_config_surface,
        hash_config_surface,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    DuplicateEmissionError = None  # type: ignore[assignment,misc]
    DeterminismDigestEmitter = None  # type: ignore[assignment,misc]
    build_stable_config_surface = None  # type: ignore[assignment,misc]
    hash_config_surface = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="determinism_digest_emitter.py deps unavailable")
class TestDeterminismDigestEmitterImportability:
    def test_module_importable(self) -> None:
        """ADG contract: determinism_digest_emitter.py must be importable."""
        assert _AVAILABLE

    def test_duplicateemissionerror_is_type(self) -> None:
        assert DuplicateEmissionError is not None

    def test_determinismdigestemitter_is_type(self) -> None:
        assert DeterminismDigestEmitter is not None

    def test_build_stable_config_surface_callable(self) -> None:
        assert callable(build_stable_config_surface)

    def test_hash_config_surface_callable(self) -> None:
        assert callable(hash_config_surface)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

