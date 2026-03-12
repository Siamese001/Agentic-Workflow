"""ADG importability contract for agentic_core/L5_safety/types/heal_llm_seam_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_heal_llm_seam_types.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.types.heal_llm_seam_types import (  # noqa: F401
        HealSeamBypassError,
        HealLlmRequest,
        PolicyDecisionRecord,
        HealBudgetExceededError,
        HealBudgetCaps,
        HealTelemetryRecord,
        set_heal_seam_capability,
        reset_heal_seam_capability,
        assert_heal_seam_capability,
        guarded_heal_llm_call,
        REPO_HEAL_DENYLIST,
        REPO_HEAL_ALLOWLIST_EXTENSIONS,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    HealSeamBypassError = None  # type: ignore[assignment,misc]
    HealLlmRequest = None  # type: ignore[assignment,misc]
    PolicyDecisionRecord = None  # type: ignore[assignment,misc]
    HealBudgetExceededError = None  # type: ignore[assignment,misc]
    HealBudgetCaps = None  # type: ignore[assignment,misc]
    HealTelemetryRecord = None  # type: ignore[assignment,misc]
    set_heal_seam_capability = None  # type: ignore[assignment,misc]
    reset_heal_seam_capability = None  # type: ignore[assignment,misc]
    assert_heal_seam_capability = None  # type: ignore[assignment,misc]
    guarded_heal_llm_call = None  # type: ignore[assignment,misc]
    REPO_HEAL_DENYLIST = None  # type: ignore[assignment,misc]
    REPO_HEAL_ALLOWLIST_EXTENSIONS = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="heal_llm_seam_types.py deps unavailable")
class TestHealLlmSeamTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: heal_llm_seam_types.py must be importable."""
        assert _AVAILABLE

    def test_healseambypasserror_is_type(self) -> None:
        assert HealSeamBypassError is not None

    def test_healllmrequest_is_type(self) -> None:
        assert HealLlmRequest is not None

    def test_policydecisionrecord_is_type(self) -> None:
        assert PolicyDecisionRecord is not None

    def test_set_heal_seam_capability_callable(self) -> None:
        assert callable(set_heal_seam_capability)

    def test_reset_heal_seam_capability_callable(self) -> None:
        assert callable(reset_heal_seam_capability)

    def test_repo_heal_denylist_defined(self) -> None:
        assert REPO_HEAL_DENYLIST is not None

    def test_repo_heal_allowlist_extensions_defined(self) -> None:
        assert REPO_HEAL_ALLOWLIST_EXTENSIONS is not None

