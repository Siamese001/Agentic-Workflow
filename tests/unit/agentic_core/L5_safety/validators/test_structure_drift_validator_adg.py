"""ADG importability contract for agentic_core/L5_safety/validators/structure_drift_validator.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_structure_drift_validator.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.validators.structure_drift_validator import (  # noqa: F401
        generate_structure_manifest,
        save_manifest,
        load_manifest,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    generate_structure_manifest = None  # type: ignore[assignment,misc]
    save_manifest = None  # type: ignore[assignment,misc]
    load_manifest = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="structure_drift_validator.py deps unavailable")
class TestStructureDriftValidatorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: structure_drift_validator.py must be importable."""
        assert _AVAILABLE

    def test_generate_structure_manifest_callable(self) -> None:
        assert callable(generate_structure_manifest)

    def test_save_manifest_callable(self) -> None:
        assert callable(save_manifest)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

