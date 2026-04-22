"""Behavioral tests for ``agentic_core.L1_cognition.config.graphrag_config``.

Locks the dataclass defaults (10 fan-in consumers depend on these), and the
global singleton lifecycle of ``get_config`` / ``set_config``.
"""

from __future__ import annotations

import pytest

from agentic_core.L1_cognition.config import graphrag_config as mod
from agentic_core.L1_cognition.config.graphrag_config import (
    GraphRAGConfig,
    get_config,
    set_config,
)


@pytest.fixture(autouse=True)
def _reset_singleton():
    """Reset the module-level singleton before and after every test."""
    mod._global_config = None
    yield
    mod._global_config = None


# ---- Dataclass defaults ---------------------------------------------------


class TestGraphRAGConfigDefaults:
    def test_extraction_mode_default(self) -> None:
        assert GraphRAGConfig().extraction_mode == "fast"

    def test_min_entity_confidence_default(self) -> None:
        assert GraphRAGConfig().min_entity_confidence == 0.5

    def test_min_relationship_confidence_default(self) -> None:
        assert GraphRAGConfig().min_relationship_confidence == 0.3

    def test_community_detection_algorithm_default(self) -> None:
        assert GraphRAGConfig().community_detection_algorithm == "leiden"

    def test_search_fusion_method_default(self) -> None:
        assert GraphRAGConfig().search_fusion_method == "weighted_average"

    def test_max_context_items_default(self) -> None:
        assert GraphRAGConfig().max_context_items == 10

    def test_enable_guardrails_default(self) -> None:
        assert GraphRAGConfig().enable_guardrails is True

    def test_guardrail_strict_mode_default(self) -> None:
        assert GraphRAGConfig().guardrail_strict_mode is False

    def test_all_defaults_snapshot(self) -> None:
        """Single assertion locking the full default envelope.

        Adding a new field without updating this test is a signal that the
        10 downstream consumers need their expectations re-checked.
        """
        cfg = GraphRAGConfig()
        assert cfg.__dict__ == {
            "extraction_mode": "fast",
            "min_entity_confidence": 0.5,
            "min_relationship_confidence": 0.3,
            "community_detection_algorithm": "leiden",
            "search_fusion_method": "weighted_average",
            "max_context_items": 10,
            "enable_guardrails": True,
            "guardrail_strict_mode": False,
        }


# ---- Override behavior ----------------------------------------------------


class TestGraphRAGConfigOverrides:
    def test_custom_extraction_mode(self) -> None:
        cfg = GraphRAGConfig(extraction_mode="deep")
        assert cfg.extraction_mode == "deep"

    def test_strict_mode_enables(self) -> None:
        cfg = GraphRAGConfig(guardrail_strict_mode=True)
        assert cfg.guardrail_strict_mode is True

    def test_guardrails_can_be_disabled(self) -> None:
        cfg = GraphRAGConfig(enable_guardrails=False)
        assert cfg.enable_guardrails is False

    def test_confidence_thresholds_float_range(self) -> None:
        """Dataclass does not enforce range; exposes the contract."""
        cfg = GraphRAGConfig(min_entity_confidence=0.9, min_relationship_confidence=0.1)
        assert cfg.min_entity_confidence == 0.9
        assert cfg.min_relationship_confidence == 0.1

    def test_max_context_items_accepts_zero(self) -> None:
        """No validation at the dataclass level — documents the contract."""
        cfg = GraphRAGConfig(max_context_items=0)
        assert cfg.max_context_items == 0


# ---- Singleton get_config / set_config ------------------------------------


class TestGetConfig:
    def test_first_call_creates_default(self) -> None:
        cfg = get_config()
        assert isinstance(cfg, GraphRAGConfig)
        assert cfg.extraction_mode == "fast"

    def test_subsequent_calls_return_same_instance(self) -> None:
        first = get_config()
        second = get_config()
        assert first is second

    def test_returns_active_singleton_after_set(self) -> None:
        custom = GraphRAGConfig(extraction_mode="deep")
        set_config(custom)
        retrieved = get_config()
        assert retrieved is custom

    def test_reset_via_none_forces_new_default(self) -> None:
        # Prime the singleton
        original = get_config()
        # Reset (simulate test-fixture behavior)
        mod._global_config = None
        new = get_config()
        assert new is not original
        assert isinstance(new, GraphRAGConfig)


class TestSetConfig:
    def test_replaces_existing_singleton(self) -> None:
        first = get_config()
        custom = GraphRAGConfig(extraction_mode="deep")
        set_config(custom)
        assert get_config() is custom
        assert get_config() is not first

    def test_accepts_fresh_instance(self) -> None:
        fresh = GraphRAGConfig(max_context_items=99)
        set_config(fresh)
        assert get_config().max_context_items == 99

    def test_set_then_mutate_visible_via_get(self) -> None:
        """Singleton holds a reference, not a copy — mutations on the stored
        dataclass are visible through subsequent get_config() calls."""
        cfg = GraphRAGConfig()
        set_config(cfg)
        cfg.extraction_mode = "changed"
        assert get_config().extraction_mode == "changed"


# ---- Module surface ---------------------------------------------------------


class TestModuleSurface:
    def test_all_exports_exact(self) -> None:
        assert mod.__all__ == ["GraphRAGConfig", "get_config", "set_config"]

    def test_global_config_starts_uninitialized(self) -> None:
        """After fixture reset, singleton is None until first get_config()."""
        assert mod._global_config is None
