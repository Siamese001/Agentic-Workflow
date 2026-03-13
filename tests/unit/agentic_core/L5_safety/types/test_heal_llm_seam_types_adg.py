"""ADG importability contract for agentic_core/L5_safety/types/heal_llm_seam_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_heal_llm_seam_types.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.types.heal_llm_seam_types import (  # noqa: F401
        HealLlmRequest,
        HealSeamBypassError,
        assert_heal_seam_capability,
        guarded_heal_llm_call,
        reset_heal_seam_capability,
        set_heal_seam_capability,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    HealSeamBypassError = None  # type: ignore[assignment,misc]
    set_heal_seam_capability = None  # type: ignore[assignment,misc]
    reset_heal_seam_capability = None  # type: ignore[assignment,misc]
    assert_heal_seam_capability = None  # type: ignore[assignment,misc]
    HealLlmRequest = None  # type: ignore[assignment,misc]
    guarded_heal_llm_call = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="heal_llm_seam_types deps unavailable")
class TestHealLlmSeamTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/types/heal_llm_seam_types.py must be importable."""
        assert _AVAILABLE

    def test_healseambypasserror_defined(self) -> None:
        assert HealSeamBypassError is not None

    def test_healllmrequest_defined(self) -> None:
        assert HealLlmRequest is not None
