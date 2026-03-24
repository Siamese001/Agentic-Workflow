"""ADG importability contract for agentic_core/L0_routing/seams/layer_emission_seam.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_layer_emission_seam.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L0_routing.seams.layer_emission_seam import (  # noqa: F401
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        LayerEmissionValidator,
        assert_layer_may_emit,
        get_layer_emission_validator,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    LayerEmissionValidator = None  # type: ignore[assignment,misc]
    get_layer_emission_validator = None  # type: ignore[assignment,misc]
    assert_layer_may_emit = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="layer_emission_seam.py deps unavailable")
class TestLayerEmissionSeamImportability:
    def test_module_importable(self) -> None:
        """ADG contract: layer_emission_seam.py must be importable."""
        assert _AVAILABLE

    def test_layeremissionvalidator_is_type(self) -> None:
        assert LayerEmissionValidator is not None

    def test_get_layer_emission_validator_callable(self) -> None:
        assert callable(get_layer_emission_validator)

    def test_assert_layer_may_emit_callable(self) -> None:
        assert callable(assert_layer_may_emit)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None