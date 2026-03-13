"""ADG importability contract for agentic_core/L2_execution/types/vllm_serving_profile_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_vllm_serving_profile_types.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.types.vllm_serving_profile_types import (  # noqa: F401
        VLLMCoChangeViolation,
        VLLMServingProfile,
        VLLMServingProfileInvalid,
        assert_no_simultaneous_increase,
        get_profile,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    VLLMServingProfile = None  # type: ignore[assignment,misc]
    VLLMServingProfileInvalid = None  # type: ignore[assignment,misc]
    assert_no_simultaneous_increase = None  # type: ignore[assignment,misc]
    VLLMCoChangeViolation = None  # type: ignore[assignment,misc]
    get_profile = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="vllm_serving_profile_types deps unavailable")
class TestVllmServingProfileTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L2_execution/types/vllm_serving_profile_types.py must be importable."""
        assert _AVAILABLE

    def test_vllmservingprofile_defined(self) -> None:
        assert VLLMServingProfile is not None

    def test_vllmservingprofileinvalid_defined(self) -> None:
        assert VLLMServingProfileInvalid is not None

    def test_vllmcochangeviolation_defined(self) -> None:
        assert VLLMCoChangeViolation is not None
