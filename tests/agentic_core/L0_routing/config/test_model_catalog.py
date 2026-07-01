"""Tests for the shared model catalog SSOT."""

from __future__ import annotations

import json

import pytest

from agentic_core.L0_routing.config import model_catalog


def test_openai_catalog_exports_non_empty_model_ids() -> None:
    assert model_catalog.OPENAI_DEFAULT_MODEL_ID == model_catalog.model_id("openai.default")
    assert model_catalog.OPENAI_CHAT_JUDGE_MODEL_ID == model_catalog.model_id("openai.chat_judge")
    assert model_catalog.OPENAI_DEFAULT_MODEL_ID
    assert model_catalog.OPENAI_CHAT_JUDGE_MODEL_ID
    assert model_catalog.OPENAI_DEFAULT_MODEL_ID in model_catalog.OPENAI_OMIT_TEMPERATURE_MODELS
    assert model_catalog.OPENAI_NON_CHAT_COMPLETIONS_MODELS


def test_catalog_json_is_the_loaded_source() -> None:
    data = json.loads(model_catalog.MODEL_CATALOG_PATH.read_text(encoding="utf-8"))
    assert data["openai"]["default"] == model_catalog.OPENAI_DEFAULT_MODEL_ID
    assert data["embedding"]["bge_m3_dimension"] == model_catalog.BGE_M3_EMBEDDING_DIMENSION
    assert model_catalog.model_int("embedding.bge_m3_dimension") == model_catalog.BGE_M3_EMBEDDING_DIMENSION


def test_missing_catalog_key_fails_closed() -> None:
    with pytest.raises(model_catalog.ModelCatalogError):
        model_catalog.model_id("openai.missing")
