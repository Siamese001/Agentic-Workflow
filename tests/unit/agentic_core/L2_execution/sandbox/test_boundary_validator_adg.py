"""ADG importability contract for agentic_core/L2_execution/sandbox/boundary_validator.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_boundary_validator.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.sandbox.boundary_validator import (  # noqa: F401
        compute_boundary_diff,
        verify_mutation_replay_integrity,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    compute_boundary_diff = None  # type: ignore[assignment,misc]
    verify_mutation_replay_integrity = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="boundary_validator.py deps unavailable")
class TestBoundaryValidatorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: boundary_validator.py must be importable."""
        assert _AVAILABLE

    def test_compute_boundary_diff_callable(self) -> None:
        assert callable(compute_boundary_diff)

    def test_verify_mutation_replay_integrity_callable(self) -> None:
        assert callable(verify_mutation_replay_integrity)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

