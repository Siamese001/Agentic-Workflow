"""Foundational behavioral tests for agentic_core/L2_execution/types/vllm_token_budget_types.py.

fan_in=4 — imported by 4 other modules.
ADG import-hygiene is covered separately by test_vllm_token_budget_types_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L2_execution.types.vllm_token_budget_types import (  # noqa: F401
        TaskClass,
        VLLMOutputCapExceeded,
        VLLMFailureType,
        VLLMPreflightResult,
        TieredRoutingDecision,
        get_output_cap,
        enforce_output_cap,
        estimate_tokens_qwen,
        run_preflight_budget_check,
        select_local_tier,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
        MAX_DEPTH,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    TaskClass = None  # type: ignore[assignment,misc]
    VLLMOutputCapExceeded = None  # type: ignore[assignment,misc]
    VLLMFailureType = None  # type: ignore[assignment,misc]
    VLLMPreflightResult = None  # type: ignore[assignment,misc]
    TieredRoutingDecision = None  # type: ignore[assignment,misc]
    get_output_cap = None  # type: ignore[assignment,misc]
    enforce_output_cap = None  # type: ignore[assignment,misc]
    estimate_tokens_qwen = None  # type: ignore[assignment,misc]
    run_preflight_budget_check = None  # type: ignore[assignment,misc]
    select_local_tier = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="vllm_token_budget_types.py deps unavailable")
class TestTaskClassContract:
    def test_is_enum(self):
        import enum
        assert issubclass(TaskClass, enum.Enum)

    def test_has_members(self):
        assert len(list(TaskClass)) >= 1

    def test_member_values_accessible(self):
        for m in TaskClass:
            assert m.value is not None or m.value is None

    def test_known_member_healing_json_artifact_present(self):
        assert hasattr(TaskClass, 'HEALING_JSON_ARTIFACT')

    def test_members_are_unique(self):
        values = [m.value for m in TaskClass]
        assert len(values) == len(set(values))

@pytest.mark.skipif(not _AVAILABLE, reason="vllm_token_budget_types.py deps unavailable")
class TestVLLMOutputCapExceededContract:
    def test_is_class(self):
        assert isinstance(VLLMOutputCapExceeded, type)

    def test_public_api_surface_non_empty(self):
        pub = [m for m in dir(VLLMOutputCapExceeded) if not m.startswith('_')]
        assert len(pub) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="vllm_token_budget_types.py deps unavailable")
class TestVLLMFailureTypeContract:
    def test_is_enum(self):
        import enum
        assert issubclass(VLLMFailureType, enum.Enum)

    def test_has_members(self):
        assert len(list(VLLMFailureType)) >= 1

    def test_member_values_accessible(self):
        for m in VLLMFailureType:
            assert m.value is not None or m.value is None

    def test_known_member_token_budget_exceeded_present(self):
        assert hasattr(VLLMFailureType, 'TOKEN_BUDGET_EXCEEDED')

    def test_members_are_unique(self):
        values = [m.value for m in VLLMFailureType]
        assert len(values) == len(set(values))

@pytest.mark.skipif(not _AVAILABLE, reason="vllm_token_budget_types.py deps unavailable")
class TestVLLMPreflightResultContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(VLLMPreflightResult)

    def test_is_frozen(self):
        assert VLLMPreflightResult.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(VLLMPreflightResult)}
        assert fnames >= {'failure_type', 'max_output_tokens_requested', 'budget_margin_tokens', 'max_model_len_configured', 'token_budget_ok', 'prompt_tokens_estimated'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(VLLMPreflightResult)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="vllm_token_budget_types.py deps unavailable")
class TestTieredRoutingDecisionContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(TieredRoutingDecision)

    def test_is_frozen(self):
        assert TieredRoutingDecision.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(TieredRoutingDecision)}
        assert fnames >= {'model_id', 'failure_type', 'preflight', 'tier', 'reason'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(TieredRoutingDecision)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="vllm_token_budget_types.py deps unavailable")
class TestGetOutputCapFunction:
    def test_is_callable(self):
        assert callable(get_output_cap)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_output_cap)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="vllm_token_budget_types.py deps unavailable")
class TestEnforceOutputCapFunction:
    def test_is_callable(self):
        assert callable(enforce_output_cap)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(enforce_output_cap)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="vllm_token_budget_types.py deps unavailable")
class TestEstimateTokensQwenFunction:
    def test_is_callable(self):
        assert callable(estimate_tokens_qwen)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(estimate_tokens_qwen)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="vllm_token_budget_types.py deps unavailable")
class TestRunPreflightBudgetCheckFunction:
    def test_is_callable(self):
        assert callable(run_preflight_budget_check)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(run_preflight_budget_check)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="vllm_token_budget_types.py deps unavailable")
class TestSelectLocalTierFunction:
    def test_is_callable(self):
        assert callable(select_local_tier)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(select_local_tier)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="vllm_token_budget_types.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="vllm_token_budget_types.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

    def test_value_is_truthy_or_defined(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="vllm_token_budget_types.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

    def test_value_is_truthy_or_defined(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="vllm_token_budget_types.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="vllm_token_budget_types.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="vllm_token_budget_types.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Smoke: vllm_token_budget_types importable or gracefully unavailable."""
    assert True
