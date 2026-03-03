"""
Phase 1 — Qwen 14B + BMG Embedding Integration Tests.

Wave 1: HealingTierConfig 14B field validation
Wave 2: _calculate_semantic_similarity BMG/Jaccard routing
Wave 3: should_proceed_with_healing Qwen 14B routing for designated agents
"""

from __future__ import annotations

import os
import sys
from unittest.mock import MagicMock, patch

import pytest

pytestmark = pytest.mark.unit_min_deps

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

from agentic_core.L2_execution.healers.healing_tier_config import (
    BMG_EMBEDDING_AGENT_KEYS,
    BMG_EMBEDDING_MODEL_ID,
    QWEN_14B_AGENT_KEYS,
    QWEN_14B_MIN_COMPUTE,
    QWEN_14B_MIN_CUDA,
    QWEN_14B_MIN_VRAM_GB,
    QWEN_14B_MODEL_ID,
    HealingTierConfig,
    load_default_healing_tier_config,
)


def _make_config(**overrides) -> HealingTierConfig:
    base = {
        "heal_confidence_x": 0.75,
        "heal_confidence_y": 0.40,
        "max_heal_retries": 3,
        "model_qwen_vllm_id": "Qwen/Qwen2.5-7B-Instruct",
        "model_gemini_2_5_pro_id": "gemini-2.5-pro",
    }
    base.update(overrides)
    return HealingTierConfig(**base)


# ---------------------------------------------------------------------------
# Wave 1 — HealingTierConfig 14B field validation
# ---------------------------------------------------------------------------


class TestHealingTierConfig14B:
    def test_default_14b_model_id_present(self):
        cfg = _make_config()
        assert cfg.model_qwen_14b_vllm_id == QWEN_14B_MODEL_ID

    def test_explicit_14b_model_id(self):
        cfg = _make_config(model_qwen_14b_vllm_id="custom/model")
        assert cfg.model_qwen_14b_vllm_id == "custom/model"

    def test_empty_14b_model_id_raises(self):
        with pytest.raises(ValueError, match="model_qwen_14b_vllm_id"):
            _make_config(model_qwen_14b_vllm_id="")

    def test_bmg_embeddings_default_false(self):
        cfg = _make_config()
        assert cfg.enable_bmg_embeddings is False

    def test_bmg_embeddings_can_be_enabled(self):
        cfg = _make_config(enable_bmg_embeddings=True)
        assert cfg.enable_bmg_embeddings is True

    def test_config_frozen(self):
        cfg = _make_config()
        with pytest.raises((AttributeError, TypeError)):
            cfg.model_qwen_14b_vllm_id = "mutated"  # type: ignore[misc]

    def test_14b_constants_types(self):
        assert isinstance(QWEN_14B_MIN_VRAM_GB, float)
        assert isinstance(QWEN_14B_MIN_COMPUTE, float)
        assert isinstance(QWEN_14B_MIN_CUDA, str)
        assert QWEN_14B_MIN_VRAM_GB >= 16.0
        assert QWEN_14B_MIN_COMPUTE >= 8.0

    def test_qwen_14b_agent_keys_is_frozenset(self):
        assert isinstance(QWEN_14B_AGENT_KEYS, frozenset)
        assert "arch_governor" in QWEN_14B_AGENT_KEYS
        assert "file_classification" in QWEN_14B_AGENT_KEYS
        assert "cognitive_disposition" in QWEN_14B_AGENT_KEYS
        assert "observability_probe" in QWEN_14B_AGENT_KEYS

    def test_bmg_embedding_agent_keys_is_frozenset(self):
        assert isinstance(BMG_EMBEDDING_AGENT_KEYS, frozenset)
        assert "location" in BMG_EMBEDDING_AGENT_KEYS
        assert "root_hygiene" in BMG_EMBEDDING_AGENT_KEYS

    def test_bmg_embedding_model_id_is_bge_m3(self):
        assert "bge-m3" in BMG_EMBEDDING_MODEL_ID.lower() or "bge_m3" in BMG_EMBEDDING_MODEL_ID.lower()

    def test_load_default_config_bmg_disabled_by_default(self):
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("BMG_EMBEDDINGS_ENABLED", None)
            cfg = load_default_healing_tier_config()
        assert cfg.enable_bmg_embeddings is False

    def test_load_default_config_bmg_enabled_via_env(self):
        with patch.dict(os.environ, {"BMG_EMBEDDINGS_ENABLED": "true"}):
            cfg = load_default_healing_tier_config()
        assert cfg.enable_bmg_embeddings is True

    def test_load_default_config_has_14b_model(self):
        cfg = load_default_healing_tier_config()
        assert cfg.model_qwen_14b_vllm_id == QWEN_14B_MODEL_ID


# ---------------------------------------------------------------------------
# Wave 2 — _calculate_semantic_similarity BMG/Jaccard routing
# ---------------------------------------------------------------------------


def _make_engine(enable_llm: bool = False):
    """Import and instantiate AutonomousDecisionEngine without side effects."""
    from agentic_core.L0_routing.scripts.execute_ssot import AutonomousDecisionEngine

    return AutonomousDecisionEngine(enable_llm=enable_llm)


class TestSemanticSimilarityRouting:
    def test_jaccard_fallback_empty_list(self):
        engine = _make_engine()
        with patch.dict(os.environ, {"BMG_EMBEDDINGS_ENABLED": "false"}):
            result = engine._calculate_semantic_similarity("location_agent", [])
        assert result == 0.0

    def test_jaccard_fallback_when_bmg_disabled(self):
        engine = _make_engine()
        with patch.dict(os.environ, {"BMG_EMBEDDINGS_ENABLED": "false"}):
            result = engine._calculate_semantic_similarity("location agent", ["location agent"])
        assert result == 1.0

    def test_jaccard_partial_match(self):
        engine = _make_engine()
        with patch.dict(os.environ, {"BMG_EMBEDDINGS_ENABLED": "false"}):
            result = engine._calculate_semantic_similarity("location agent", ["location", "hygiene"])
        assert 0.0 < result < 1.0

    def test_bmg_path_called_when_enabled(self):
        engine = _make_engine()
        mock_similarity = MagicMock(return_value=0.92)
        fake_module = MagicMock()
        fake_module.bmg_cosine_similarity = mock_similarity

        with patch.dict(os.environ, {"BMG_EMBEDDINGS_ENABLED": "true"}):
            with patch.dict(
                sys.modules, {"agentic_core.L2_execution.healers.bmg_embedding_similarity": fake_module}
            ):
                result = engine._calculate_semantic_similarity("location agent", ["loc agent"])

        mock_similarity.assert_called_once_with("location agent", ["loc agent"])
        assert result == 0.92

    def test_bmg_exception_falls_back_to_jaccard(self):
        engine = _make_engine()
        fake_module = MagicMock()
        fake_module.bmg_cosine_similarity.side_effect = RuntimeError("GPU OOM")

        with patch.dict(os.environ, {"BMG_EMBEDDINGS_ENABLED": "true"}):
            with patch.dict(
                sys.modules, {"agentic_core.L2_execution.healers.bmg_embedding_similarity": fake_module}
            ):
                result = engine._calculate_semantic_similarity("location agent", ["location agent"])

        # Jaccard fallback should produce 1.0 for identical strings
        assert result == 1.0

    def test_bmg_import_error_falls_back_to_jaccard(self):
        engine = _make_engine()
        with patch.dict(os.environ, {"BMG_EMBEDDINGS_ENABLED": "true"}):
            # Ensure the module import fails
            modules = dict(sys.modules)
            modules.pop("agentic_core.L2_execution.healers.bmg_embedding_similarity", None)
            with patch.dict(
                sys.modules, {"agentic_core.L2_execution.healers.bmg_embedding_similarity": None}
            ):
                result = engine._calculate_semantic_similarity("location agent", ["location agent"])
        assert result == 1.0


# ---------------------------------------------------------------------------
# Wave 3 — should_proceed_with_healing Qwen 14B routing
# ---------------------------------------------------------------------------


def _make_confidence(value: float):
    from agentic_core.L0_routing.scripts.execute_ssot import ConfidenceScore

    return ConfidenceScore(value=value, reasoning="test")


class TestQwen14BRoutingInDecisionEngine:
    def test_high_confidence_always_sovereign_auto(self):
        engine = _make_engine(enable_llm=True)
        proceed, reason = engine.should_proceed_with_healing(_make_confidence(0.90), "arch_governor")
        assert proceed is True
        assert "SOVEREIGN-AUTO" in reason

    def test_medium_confidence_qwen14b_for_designated_agent(self):
        engine = _make_engine(enable_llm=True)
        with patch.dict(os.environ, {"QWEN_14B_MODEL": "Qwen/Qwen2.5-14B-Instruct-GPTQ-Int4"}):
            proceed, reason = engine.should_proceed_with_healing(_make_confidence(0.60), "arch_governor")
        assert proceed is True
        assert "QWEN14B" in reason

    def test_medium_confidence_gemini_flash_for_non_designated_agent(self):
        engine = _make_engine(enable_llm=True)
        with patch.dict(os.environ, {"GEMINI_MODEL": "gemini-3-flash-preview"}):
            proceed, reason = engine.should_proceed_with_healing(_make_confidence(0.60), "reconciler")
        assert proceed is True
        assert "FLASH" in reason

    def test_medium_confidence_all_qwen14b_agents_route_correctly(self):
        from agentic_core.L2_execution.healers.healing_tier_config import QWEN_14B_AGENT_KEYS

        engine = _make_engine(enable_llm=True)
        for agent_key in QWEN_14B_AGENT_KEYS:
            engine._call_path.clear()
            engine._healing_count = 0
            proceed, reason = engine.should_proceed_with_healing(_make_confidence(0.55), agent_key)
            assert proceed is True, f"{agent_key} should proceed"
            assert "QWEN14B" in reason, f"{agent_key} should route to Qwen14B, got: {reason}"

    def test_medium_confidence_model_recorded_in_decisions(self):
        engine = _make_engine(enable_llm=True)
        with patch.dict(os.environ, {"QWEN_14B_MODEL": "Qwen/Qwen2.5-14B-Instruct-GPTQ-Int4"}):
            engine.should_proceed_with_healing(_make_confidence(0.60), "cognitive_disposition")
        last = engine.decisions_made[-1]
        assert "model" in last
        assert "14B" in last["model"] or "Qwen2.5-14B" in last["model"]

    def test_low_confidence_stays_gemini_pro(self):
        engine = _make_engine(enable_llm=True)
        with patch.dict(os.environ, {"GEMINI_PRO_MODEL": "gemini-2.5-pro"}):
            proceed, reason = engine.should_proceed_with_healing(_make_confidence(0.30), "arch_governor")
        assert proceed is True
        assert "RECOVERY-PRO" in reason

    def test_medium_confidence_no_llm_triggers_hitl(self):
        engine = _make_engine(enable_llm=False)
        with patch.object(engine, "_hitl_gate", return_value=(False, "HITL-BLOCKED")) as mock_gate:
            proceed, reason = engine.should_proceed_with_healing(_make_confidence(0.60), "arch_governor")
        mock_gate.assert_called_once()
        assert proceed is False

    def test_decisions_made_records_correct_agent(self):
        engine = _make_engine(enable_llm=True)
        engine.should_proceed_with_healing(_make_confidence(0.60), "file_classification")
        assert engine.decisions_made[-1]["agent"] == "file_classification"


# ---------------------------------------------------------------------------
# Wave 1b — bmg_embedding_similarity module contract
# ---------------------------------------------------------------------------


class TestBmgEmbeddingSimilarityModule:
    def test_module_importable(self):
        from agentic_core.L2_execution.healers import bmg_embedding_similarity  # noqa: F401

    def test_public_api(self):
        from agentic_core.L2_execution.healers.bmg_embedding_similarity import (
            __all__,
        )

        assert "bmg_cosine_similarity" in __all__
        assert "clear_model_cache" in __all__

    def test_bmg_cosine_similarity_raises_on_empty_candidates(self):
        from agentic_core.L2_execution.healers.bmg_embedding_similarity import bmg_cosine_similarity

        with pytest.raises((ValueError, ImportError)):
            bmg_cosine_similarity("test", [])

    def test_clear_model_cache_callable(self):
        from agentic_core.L2_execution.healers.bmg_embedding_similarity import clear_model_cache

        clear_model_cache()  # Must not raise even if model was never loaded
