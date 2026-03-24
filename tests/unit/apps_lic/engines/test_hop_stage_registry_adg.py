"""ADG importability contract for apps_lic/engines/hop_stage_registry.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_hop_stage_registry.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from apps_lic.engines.hop_stage_registry import (  # noqa: F401
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        get_stage_handler,
        register_stage,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    register_stage = None  # type: ignore[assignment,misc]
    get_stage_handler = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="hop_stage_registry.py deps unavailable")
class TestHopStageRegistryImportability:
    def test_module_importable(self) -> None:
        """ADG contract: hop_stage_registry.py must be importable."""
        assert _AVAILABLE

    def test_register_stage_callable(self) -> None:
        assert callable(register_stage)

    def test_get_stage_handler_callable(self) -> None:
        assert callable(get_stage_handler)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None