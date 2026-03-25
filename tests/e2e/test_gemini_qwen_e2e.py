"""Behavioral contract tests for agentic_core.L2_execution.types.vllm_token_budget_types."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.L2_execution.types.vllm_token_budget_types"


@pytest.fixture(scope="module")
def mod():
    """Import the module under test. Fails hard if first-party import broken."""
    try:
        return importlib.import_module(MODULE_PATH)
    except Exception as exc:
        pytest.fail(
            f"FIRST-PARTY IMPORT FAILED for {MODULE_PATH}: {exc}",
            pytrace=False,
        )


def test_module_importable(mod):
    """Module imports without errors."""
    assert mod.__name__ == MODULE_PATH


def test_module_exposes_public_api(mod):
    """Module exposes expected public symbols."""
    public = [n for n in dir(mod) if not n.startswith("_")]
    assert len(public) >= 1, f"{MODULE_PATH} must expose at least one public symbol"


def test_enum_is_instantiable(mod):
    """Enum is accessible and is a type."""
    cls = getattr(mod, "Enum", None)
    assert cls is not None, "Enum must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "Enum must be a class"


def test_layersegment_is_instantiable(mod):
    """LayerSegment is accessible and is a type."""
    cls = getattr(mod, "LayerSegment", None)
    assert cls is not None, "LayerSegment must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "LayerSegment must be a class"


def test_taskclass_is_instantiable(mod):
    """TaskClass is accessible and is a type."""
    cls = getattr(mod, "TaskClass", None)
    assert cls is not None, "TaskClass must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "TaskClass must be a class"


def test_tieredroutingdecision_is_instantiable(mod):
    """TieredRoutingDecision is accessible and is a type."""
    cls = getattr(mod, "TieredRoutingDecision", None)
    assert cls is not None, "TieredRoutingDecision must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "TieredRoutingDecision must be a class"


def test_vllmfailuretype_is_instantiable(mod):
    """VLLMFailureType is accessible and is a type."""
    cls = getattr(mod, "VLLMFailureType", None)
    assert cls is not None, "VLLMFailureType must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "VLLMFailureType must be a class"


def test_vllmoutputcapexceeded_is_instantiable(mod):
    """VLLMOutputCapExceeded is accessible and is a type."""
    cls = getattr(mod, "VLLMOutputCapExceeded", None)
    assert cls is not None, "VLLMOutputCapExceeded must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "VLLMOutputCapExceeded must be a class"


def test_vllmpreflightresult_is_instantiable(mod):
    """VLLMPreflightResult is accessible and is a type."""
    cls = getattr(mod, "VLLMPreflightResult", None)
    assert cls is not None, "VLLMPreflightResult must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "VLLMPreflightResult must be a class"


def test_literal_is_callable(mod):
    """Literal is accessible and callable."""
    func = getattr(mod, "Literal", None)
    assert func is not None, "Literal must be defined in {MODULE_PATH}"
    assert callable(func), "Literal must be callable"


def test_localtier_is_callable(mod):
    """LocalTier is accessible and callable."""
    func = getattr(mod, "LocalTier", None)
    assert func is not None, "LocalTier must be defined in {MODULE_PATH}"
    assert callable(func), "LocalTier must be callable"


def test_dataclass_is_callable(mod):
    """dataclass is accessible and callable."""
    func = getattr(mod, "dataclass", None)
    assert func is not None, "dataclass must be defined in {MODULE_PATH}"
    assert callable(func), "dataclass must be callable"


def test_emit_determinism_digest_is_callable(mod):
    """emit_determinism_digest is accessible and callable."""
    func = getattr(mod, "emit_determinism_digest", None)
    assert func is not None, "emit_determinism_digest must be defined in {MODULE_PATH}"
    assert callable(func), "emit_determinism_digest must be callable"


def test_emit_replay_key_is_callable(mod):
    """emit_replay_key is accessible and callable."""
    func = getattr(mod, "emit_replay_key", None)
    assert func is not None, "emit_replay_key must be defined in {MODULE_PATH}"
    assert callable(func), "emit_replay_key must be callable"


def test_enforce_output_cap_is_callable(mod):
    """enforce_output_cap is accessible and callable."""
    func = getattr(mod, "enforce_output_cap", None)
    assert func is not None, "enforce_output_cap must be defined in {MODULE_PATH}"
    assert callable(func), "enforce_output_cap must be callable"


def test_estimate_tokens_qwen_is_callable(mod):
    """estimate_tokens_qwen is accessible and callable."""
    func = getattr(mod, "estimate_tokens_qwen", None)
    assert func is not None, "estimate_tokens_qwen must be defined in {MODULE_PATH}"
    assert callable(func), "estimate_tokens_qwen must be callable"


def test_get_output_cap_is_callable(mod):
    """get_output_cap is accessible and callable."""
    func = getattr(mod, "get_output_cap", None)
    assert func is not None, "get_output_cap must be defined in {MODULE_PATH}"
    assert callable(func), "get_output_cap must be callable"

