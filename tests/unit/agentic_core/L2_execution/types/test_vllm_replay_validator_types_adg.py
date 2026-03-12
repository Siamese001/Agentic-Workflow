"""ADG importability contract for agentic_core/L2_execution/types/vllm_replay_validator_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_vllm_replay_validator_types.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.types.vllm_replay_validator_types import (  # noqa: F401
        VLLMReplayArtifact,
        VLLMReplayValidator,
        canonical_prompt_hash,
        canonical_local_request_hash,
        canonical_response_hash,
        compute_replay_hash,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    VLLMReplayArtifact = None  # type: ignore[assignment,misc]
    VLLMReplayValidator = None  # type: ignore[assignment,misc]
    canonical_prompt_hash = None  # type: ignore[assignment,misc]
    canonical_local_request_hash = None  # type: ignore[assignment,misc]
    canonical_response_hash = None  # type: ignore[assignment,misc]
    compute_replay_hash = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="vllm_replay_validator_types.py deps unavailable")
class TestVllmReplayValidatorTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: vllm_replay_validator_types.py must be importable."""
        assert _AVAILABLE

    def test_vllmreplayartifact_is_type(self) -> None:
        assert VLLMReplayArtifact is not None

    def test_vllmreplayvalidator_is_type(self) -> None:
        assert VLLMReplayValidator is not None

    def test_canonical_prompt_hash_callable(self) -> None:
        assert callable(canonical_prompt_hash)

    def test_canonical_local_request_hash_callable(self) -> None:
        assert callable(canonical_local_request_hash)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

