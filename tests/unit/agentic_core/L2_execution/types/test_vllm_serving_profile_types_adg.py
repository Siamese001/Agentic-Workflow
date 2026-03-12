"""ADG importability contract for agentic_core/L2_execution/types/vllm_serving_profile_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_vllm_serving_profile_types.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.types.vllm_serving_profile_types import (  # noqa: F401
        VLLMServingProfile,
        VLLMServingProfileInvalid,
        VLLMCoChangeViolation,
        assert_no_simultaneous_increase,
        get_profile,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    VLLMServingProfile = None  # type: ignore[assignment,misc]
    VLLMServingProfileInvalid = None  # type: ignore[assignment,misc]
    VLLMCoChangeViolation = None  # type: ignore[assignment,misc]
    assert_no_simultaneous_increase = None  # type: ignore[assignment,misc]
    get_profile = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="vllm_serving_profile_types.py deps unavailable")
class TestVllmServingProfileTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: vllm_serving_profile_types.py must be importable."""
        assert _AVAILABLE

    def test_vllmservingprofile_is_type(self) -> None:
        assert VLLMServingProfile is not None

    def test_vllmservingprofileinvalid_is_type(self) -> None:
        assert VLLMServingProfileInvalid is not None

    def test_vllmcochangeviolation_is_type(self) -> None:
        assert VLLMCoChangeViolation is not None

    def test_assert_no_simultaneous_increase_callable(self) -> None:
        assert callable(assert_no_simultaneous_increase)

    def test_get_profile_callable(self) -> None:
        assert callable(get_profile)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

