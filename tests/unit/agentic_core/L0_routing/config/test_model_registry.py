"""Tests for L0 model registry SSOT.

Wave 1 P1.2 of `docs/archive/windsurf/legacy-tree/plans/routing-unification-qwen-abe735.md`.
"""

from __future__ import annotations

import importlib

import pytest

pytestmark = pytest.mark.unit

MODEL_REGISTRY_MODULE = "agentic_core.L0_routing.config.model_registry"


@pytest.fixture(scope="module")
def mr():
    return importlib.import_module(MODEL_REGISTRY_MODULE)


def test_all_tier_constants_exist(mr):
    assert mr.TIER_DETERMINISTIC == "DETERMINISTIC"
    assert mr.TIER_QWEN_LOCAL == "QWEN_LOCAL"
    assert mr.TIER_GEMINI_FLASH == "GEMINI_FLASH"
    assert mr.TIER_GEMINI_PRO == "GEMINI_PRO"
    assert mr.TIER_HITL == "HITL"
    assert mr.ALL_TIERS == (
        "DETERMINISTIC",
        "QWEN_LOCAL",
        "GEMINI_FLASH",
        "GEMINI_PRO",
        "HITL",
    )


def test_model_ids_are_non_empty_strings(mr):
    from tqdm import tqdm  # noqa: PLC0415 — §16 progress compliance

    names = (
        "QWEN_LOCAL_MODEL_ID",
        "GEMINI_FLASH_MODEL_ID",
        "GEMINI_PRO_MODEL_ID",
        "OPENAI_MODEL_ID",
        "ANTHROPIC_MODEL_ID",
        "EMBEDDING_MODEL_ID",
        "VLLM_BASE_URL",
        "DETERMINISTIC_MODEL_SENTINEL",
    )
    for name in tqdm(names, desc="Model IDs", unit="id", disable=True):
        value = getattr(mr, name)
        assert isinstance(value, str)
        assert value.strip(), f"{name} must be non-empty"


def test_qwen_disallowed_failure_types_includes_structural(mr):
    disallowed = mr.QWEN_DISALLOWED_FAILURE_TYPES
    assert "LAYER_VIOLATION" in disallowed
    assert "GATEWAY_BYPASS" in disallowed
    assert "KILL_SWITCH_BYPASS" in disallowed
    assert "SIGNATURE_VERIFY" in disallowed
    assert "UNSIGNED_INGRESS" in disallowed
    assert "IMPORT_BOUNDARY_VIOLATION" in disallowed
    assert "SCHEMA_REQUIRED_FIELDS_MISSING" in disallowed


def test_get_model_for_tier_maps_all_tiers(mr):
    assert mr.get_model_for_tier(mr.TIER_DETERMINISTIC) == mr.DETERMINISTIC_MODEL_SENTINEL
    assert mr.get_model_for_tier(mr.TIER_QWEN_LOCAL) == mr.QWEN_LOCAL_MODEL_ID
    assert mr.get_model_for_tier(mr.TIER_GEMINI_FLASH) == mr.GEMINI_FLASH_MODEL_ID
    assert mr.get_model_for_tier(mr.TIER_GEMINI_PRO) == mr.GEMINI_PRO_MODEL_ID
    assert mr.get_model_for_tier(mr.TIER_HITL) == "human_review"


def test_get_model_for_tier_rejects_unknown(mr):
    with pytest.raises(ValueError, match="Unknown tier"):
        mr.get_model_for_tier("NOT_A_REAL_TIER")


def test_registry_exports_are_complete(mr):
    exported = set(mr.__all__)
    expected = {
        "ALL_TIERS",
        "ANTHROPIC_MODEL_ID",
        "DETERMINISTIC_MODEL_SENTINEL",
        "EMBEDDING_MODEL_ID",
        "GEMINI_FLASH_MODEL_ID",
        "GEMINI_PRO_MODEL_ID",
        "OPENAI_MODEL_ID",
        "QWEN_DISALLOWED_FAILURE_TYPES",
        "QWEN_LOCAL_MODEL_ID",
        "TIER_DETERMINISTIC",
        "TIER_GEMINI_FLASH",
        "TIER_GEMINI_PRO",
        "TIER_HITL",
        "TIER_QWEN_LOCAL",
        "VLLM_BASE_URL",
        "get_model_for_tier",
    }
    missing = expected - exported
    assert not missing, f"Missing from __all__: {sorted(missing)}"
