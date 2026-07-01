"""Tests for model_registry.py module.

This module contains SSOT constants for model identifiers and a tier-to-model
mapping function. Tests verify constant existence, types, and function behavior.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

from agentic_core.L0_routing.config.model_registry import (
    DETERMINISTIC_MODEL_SENTINEL,
    QWEN_LOCAL_MODEL_ID,
    VLLM_BASE_URL,
    QWEN_LOCAL_MAX_MODEL_LEN,
    GEMINI_FLASH_MODEL_ID,
    GEMINI_PRO_MODEL_ID,
    OPENAI_MODEL_ID,
    ANTHROPIC_MODEL_ID,
    CONSENSUS_JURORS,
    EMBEDDING_MODEL_ID,
    QWEN_DISALLOWED_FAILURE_TYPES,
    TIER_DETERMINISTIC,
    TIER_QWEN_LOCAL,
    TIER_GEMINI_FLASH,
    TIER_GEMINI_PRO,
    TIER_HITL,
    ALL_TIERS,
    get_model_for_tier,
)


class TestConstantsExistenceAndTypes:
    """Tests for constant existence and types."""

    def test_deterministic_model_sentinel(self):
        """Test DETERMINISTIC_MODEL_SENTINEL exists and is string."""
        assert isinstance(DETERMINISTIC_MODEL_SENTINEL, str)
        assert DETERMINISTIC_MODEL_SENTINEL == "local_deterministic"

    def test_qwen_local_model_id(self):
        """Test QWEN_LOCAL_MODEL_ID exists and is string."""
        assert isinstance(QWEN_LOCAL_MODEL_ID, str)
        assert QWEN_LOCAL_MODEL_ID

    def test_vllm_base_url(self):
        """Test VLLM_BASE_URL exists and is string."""
        assert isinstance(VLLM_BASE_URL, str)
        assert VLLM_BASE_URL

    def test_qwen_local_max_model_len(self):
        """Test QWEN_LOCAL_MAX_MODEL_LEN exists and is int."""
        assert isinstance(QWEN_LOCAL_MAX_MODEL_LEN, int)
        assert QWEN_LOCAL_MAX_MODEL_LEN > 0

    def test_gemini_flash_model_id(self):
        """Test GEMINI_FLASH_MODEL_ID exists and is string."""
        assert isinstance(GEMINI_FLASH_MODEL_ID, str)
        assert GEMINI_FLASH_MODEL_ID

    def test_gemini_pro_model_id(self):
        """Test GEMINI_PRO_MODEL_ID exists and is string."""
        assert isinstance(GEMINI_PRO_MODEL_ID, str)
        assert GEMINI_PRO_MODEL_ID

    def test_openai_model_id(self):
        """Test OPENAI_MODEL_ID exists and is string."""
        assert isinstance(OPENAI_MODEL_ID, str)
        assert OPENAI_MODEL_ID

    def test_anthropic_model_id(self):
        """Test ANTHROPIC_MODEL_ID exists and is string."""
        assert isinstance(ANTHROPIC_MODEL_ID, str)
        assert ANTHROPIC_MODEL_ID

    def test_embedding_model_id(self):
        """Test EMBEDDING_MODEL_ID exists and is string."""
        assert isinstance(EMBEDDING_MODEL_ID, str)
        assert EMBEDDING_MODEL_ID

    def test_qwen_disallowed_failure_types(self):
        """Test QWEN_DISALLOWED_FAILURE_TYPES exists and is frozenset."""
        assert isinstance(QWEN_DISALLOWED_FAILURE_TYPES, frozenset)
        assert len(QWEN_DISALLOWED_FAILURE_TYPES) > 0
        for failure_type in QWEN_DISALLOWED_FAILURE_TYPES:
            assert isinstance(failure_type, str)

    def test_tier_constants(self):
        """Test tier string constants exist."""
        assert isinstance(TIER_DETERMINISTIC, str)
        assert isinstance(TIER_QWEN_LOCAL, str)
        assert isinstance(TIER_GEMINI_FLASH, str)
        assert isinstance(TIER_GEMINI_PRO, str)
        assert isinstance(TIER_HITL, str)

    def test_all_tiers(self):
        """Test ALL_TIERS is a tuple of strings."""
        assert isinstance(ALL_TIERS, tuple)
        assert len(ALL_TIERS) > 0
        for tier in ALL_TIERS:
            assert isinstance(tier, str)


class TestConsensusJurors:
    """Tests for CONSENSUS_JURORS resolution."""

    def test_consensus_jurors_is_tuple(self):
        """Test CONSENSUS_JURORS is a tuple."""
        assert isinstance(CONSENSUS_JURORS, tuple)
        assert len(CONSENSUS_JURORS) >= 3  # At least default 3 jurors

    def test_consensus_jurors_are_strings(self):
        """Test all consensus jurors are strings."""
        for juror in CONSENSUS_JURORS:
            assert isinstance(juror, str)

    def test_consensus_jurors_default(self):
        """Test default consensus jurors without env override."""
        with patch.dict("os.environ", clear=True):
            # Re-import to trigger resolution without env vars
            from agentic_core.L0_routing.config import model_registry as mr_reload
            from importlib import reload
            reload(mr_reload)
            
            jurors = mr_reload.CONSENSUS_JURORS
            assert len(jurors) == 3
            assert mr_reload.OPENAI_MODEL_ID in jurors
            assert mr_reload.ANTHROPIC_MODEL_ID in jurors
            assert mr_reload.GEMINI_PRO_MODEL_ID in jurors

    def test_consensus_jurors_env_override(self):
        """Test CONSENSUS_JURORS env var override."""
        with patch.dict("os.environ", {"CONSENSUS_JURORS": "gpt-4o,claude-sonnet-5"}, clear=True):
            from agentic_core.L0_routing.config import model_registry as mr_reload
            from importlib import reload
            reload(mr_reload)
            
            jurors = mr_reload.CONSENSUS_JURORS
            assert len(jurors) == 2
            assert "gpt-4o" in jurors
            assert "claude-sonnet-5" in jurors

    def test_consensus_jurors_qwen_opt_in(self):
        """Test USE_QWEN_CONSENSUS_JUROR opt-in adds Qwen."""
        with patch.dict("os.environ", {"USE_QWEN_CONSENSUS_JUROR": "1"}, clear=True):
            from agentic_core.L0_routing.config import model_registry as mr_reload
            from importlib import reload
            reload(mr_reload)
            
            jurors = mr_reload.CONSENSUS_JURORS
            assert len(jurors) == 4
            assert mr_reload.QWEN_LOCAL_MODEL_ID in jurors


class TestGetModelForTier:
    """Tests for get_model_for_tier function."""

    def test_get_model_deterministic(self):
        """Test getting model for DETERMINISTIC tier."""
        model = get_model_for_tier(TIER_DETERMINISTIC)
        assert model == DETERMINISTIC_MODEL_SENTINEL

    def test_get_model_qwen_local(self):
        """Test getting model for QWEN_LOCAL tier."""
        model = get_model_for_tier(TIER_QWEN_LOCAL)
        assert model == QWEN_LOCAL_MODEL_ID

    def test_get_model_gemini_flash(self):
        """Test getting model for GEMINI_FLASH tier."""
        model = get_model_for_tier(TIER_GEMINI_FLASH)
        assert model == GEMINI_FLASH_MODEL_ID

    def test_get_model_gemini_pro(self):
        """Test getting model for GEMINI_PRO tier."""
        model = get_model_for_tier(TIER_GEMINI_PRO)
        assert model == GEMINI_PRO_MODEL_ID

    def test_get_model_hitl(self):
        """Test getting model for HITL tier."""
        model = get_model_for_tier(TIER_HITL)
        assert model == "human_review"

    def test_get_model_invalid_tier(self):
        """Test that invalid tier raises ValueError."""
        with pytest.raises(ValueError, match="Unknown tier"):
            get_model_for_tier("INVALID_TIER")
