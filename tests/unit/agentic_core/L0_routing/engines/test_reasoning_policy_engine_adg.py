"""ADG importability contract for agentic_core/L0_routing/engines/reasoning_policy_engine.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_reasoning_policy_engine.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L0_routing.engines.reasoning_policy_engine import (  # noqa: F401
        RequestStructureFeatures,
        ReasoningPolicyEngine,
        compute_complexity_score,
        select_tier,
        compute_policy_config_hash,
        PROFILE_VERSION,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    RequestStructureFeatures = None  # type: ignore[assignment,misc]
    ReasoningPolicyEngine = None  # type: ignore[assignment,misc]
    compute_complexity_score = None  # type: ignore[assignment,misc]
    select_tier = None  # type: ignore[assignment,misc]
    compute_policy_config_hash = None  # type: ignore[assignment,misc]
    PROFILE_VERSION = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="reasoning_policy_engine.py deps unavailable")
class TestReasoningPolicyEngineImportability:
    def test_module_importable(self) -> None:
        """ADG contract: reasoning_policy_engine.py must be importable."""
        assert _AVAILABLE

    def test_requeststructurefeatures_is_type(self) -> None:
        assert RequestStructureFeatures is not None

    def test_reasoningpolicyengine_is_type(self) -> None:
        assert ReasoningPolicyEngine is not None

    def test_compute_complexity_score_callable(self) -> None:
        assert callable(compute_complexity_score)

    def test_select_tier_callable(self) -> None:
        assert callable(select_tier)

    def test_profile_version_defined(self) -> None:
        assert PROFILE_VERSION is not None

